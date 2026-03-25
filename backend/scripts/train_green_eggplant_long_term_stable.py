import os
import warnings
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import chinese_calendar

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.losses import Huber
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# =========================================================
# 0. Basic Config
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data", "green_eggplant_1_daily.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_NAME = "Green Eggplant (1) - Long-term Stable Hybrid GRU-XGBoost"
TIME_STEPS = 30
FUTURE_DAYS = 7
TEST_RATIO = 0.2
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# =========================================================
# 1. Metrics
# =========================================================
def smape_func(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    denominator = np.abs(y_true) + np.abs(y_pred)
    denominator = np.where(denominator == 0, 1e-8, denominator)
    return 100 * np.mean(2 * np.abs(y_pred - y_true) / denominator)

# =========================================================
# 2. Spring Festival Helper Functions
# =========================================================
def days_to_spring_festival(date_obj, max_search=60):
    for i in range(max_search + 1):
        future_date = date_obj + datetime.timedelta(days=i)
        _, holiday_name = chinese_calendar.get_holiday_detail(future_date)
        if holiday_name == "Spring Festival":
            return i
    return max_search + 1

def days_after_spring_festival(date_obj, max_search=30):
    for i in range(max_search + 1):
        past_date = date_obj - datetime.timedelta(days=i)
        _, holiday_name = chinese_calendar.get_holiday_detail(past_date)
        if holiday_name == "Spring Festival":
            return i
    return max_search + 1

def calculate_sf_weight(date_obj):
    _, holiday_name = chinese_calendar.get_holiday_detail(date_obj)

    if holiday_name == "Spring Festival":
        return 20

    for i in range(1, 16):
        future_date = date_obj + datetime.timedelta(days=i)
        _, future_name = chinese_calendar.get_holiday_detail(future_date)
        if future_name == "Spring Festival":
            return 16 - i

    for i in range(1, 8):
        past_date = date_obj - datetime.timedelta(days=i)
        _, past_name = chinese_calendar.get_holiday_detail(past_date)
        if past_name == "Spring Festival":
            return max(8 - i, 0)

    return 0

# =========================================================
# 3. Load Data
# =========================================================
df = pd.read_csv(FILE_PATH)
df["Date"] = pd.to_datetime(df["Date"])

# 这份文件理论上已经只有 Green Eggplant (1)
# 这里保留兜底过滤，防止文件里混入其他商品
if "ItemName" in df.columns:
    df["ItemName"] = df["ItemName"].astype(str).str.strip()
    if (df["ItemName"] == "Green Eggplant (1)").any():
        df = df[df["ItemName"] == "Green Eggplant (1)"].copy()

if df.empty:
    raise ValueError("No data found in green_eggplant_1_daily.csv")

# =========================================================
# 4. Aggregate Daily Sales
# =========================================================
# 保持和你 broccoli 长期代码一致：按天聚合，再补全日期
daily_sales = (
    df.groupby("Date")
      .agg({
          "QuantitySoldKilo": "sum",
          "UnitSellingPrice": "mean",
          "WholesalePrice": "mean",
          "LossRatePct": "mean"
      })
      .sort_index()
)

full_index = pd.date_range(daily_sales.index.min(), daily_sales.index.max(), freq="D")
daily_sales = daily_sales.reindex(full_index)
daily_sales.index.name = "Date"

daily_sales["QuantitySoldKilo"] = daily_sales["QuantitySoldKilo"].fillna(0)

for col in ["UnitSellingPrice", "WholesalePrice", "LossRatePct"]:
    daily_sales[col] = daily_sales[col].interpolate(method="time").ffill().bfill()

# 用于后面未来真实值查找
actual_lookup = daily_sales["QuantitySoldKilo"].copy()

# =========================================================
# 5. Advanced Feature Engineering
# =========================================================
def create_features(data):
    df_feat = data.copy()

    # Basic time features
    df_feat["DayOfWeek"] = df_feat.index.dayofweek
    df_feat["IsWeekend"] = (df_feat.index.dayofweek >= 5).astype(int)
    df_feat["Month"] = df_feat.index.month
    df_feat["DayOfYear"] = df_feat.index.dayofyear
    df_feat["WeekOfYear"] = df_feat.index.isocalendar().week.astype(int)

    # Holiday / Spring Festival features
    is_holiday = []
    sf_weight = []
    days_to_sf_list = []
    days_after_sf_list = []
    is_peak = []

    for d in df_feat.index:
        is_holiday.append(1 if chinese_calendar.is_holiday(d) else 0)

        w = calculate_sf_weight(d)
        sf_weight.append(w)

        d_to_sf = days_to_spring_festival(d)
        d_after_sf = days_after_spring_festival(d)

        days_to_sf_list.append(d_to_sf)
        days_after_sf_list.append(d_after_sf)

        is_peak.append(1 if (d_to_sf <= 12 or d_after_sf <= 3 or w >= 8) else 0)

    df_feat["IsHoliday"] = is_holiday
    df_feat["SF_Weight"] = sf_weight
    df_feat["Days_To_SF"] = days_to_sf_list
    df_feat["Days_After_SF"] = days_after_sf_list
    df_feat["Is_Peak"] = is_peak

    # Yearly alignment feature
    df_feat["Lag_364"] = df_feat["QuantitySoldKilo"].shift(364)
    df_feat["Lag_364"] = df_feat["Lag_364"].fillna(df_feat["QuantitySoldKilo"].shift(7))
    df_feat["Lag_364"] = df_feat["Lag_364"].fillna(df_feat["QuantitySoldKilo"].mean())

    # Rolling / lag features
    df_feat["Rolling_Mean_7"] = df_feat["QuantitySoldKilo"].rolling(window=7).mean()
    df_feat["Rolling_Std_7"] = df_feat["QuantitySoldKilo"].rolling(window=7).std()
    df_feat["Rolling_Max_7"] = df_feat["QuantitySoldKilo"].rolling(window=7).max()

    df_feat["Lag_1"] = df_feat["QuantitySoldKilo"].shift(1)
    df_feat["Lag_7"] = df_feat["QuantitySoldKilo"].shift(7)
    df_feat["Lag_14"] = df_feat["QuantitySoldKilo"].shift(14)

    df_feat["Peak_Ratio_7"] = df_feat["QuantitySoldKilo"].shift(1) / (df_feat["Rolling_Mean_7"] + 1e-6)

    # 价格特征也保留，便于贴合蔬菜数据结构
    df_feat["PriceSpread"] = df_feat["UnitSellingPrice"] - df_feat["WholesalePrice"]
    df_feat["ProfitRate"] = np.where(
        df_feat["WholesalePrice"] == 0,
        0,
        (df_feat["UnitSellingPrice"] - df_feat["WholesalePrice"]) / df_feat["WholesalePrice"]
    )

    df_feat = df_feat.dropna().copy()
    return df_feat

df_features = create_features(daily_sales)

# =========================================================
# 6. Feature Selection
# =========================================================
feature_cols = [
    "QuantitySoldKilo",
    "UnitSellingPrice",
    "WholesalePrice",
    "LossRatePct",
    "PriceSpread",
    "ProfitRate",
    "DayOfWeek",
    "IsWeekend",
    "Month",
    "DayOfYear",
    "WeekOfYear",
    "IsHoliday",
    "SF_Weight",
    "Days_To_SF",
    "Days_After_SF",
    "Is_Peak",
    "Rolling_Mean_7",
    "Rolling_Std_7",
    "Rolling_Max_7",
    "Lag_1",
    "Lag_7",
    "Lag_14",
    "Lag_364",
    "Peak_Ratio_7"
]

target_col = "QuantitySoldKilo"

# =========================================================
# 7. Train-Test Split
# =========================================================
split_raw = int(len(df_features) * (1 - TEST_RATIO))
train_df = df_features.iloc[:split_raw].copy()
test_df = df_features.iloc[split_raw:].copy()

# =========================================================
# 8. Scaling
# =========================================================
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

scaler_X.fit(train_df[feature_cols])
scaler_y.fit(train_df[[target_col]])

X_all_scaled = scaler_X.transform(df_features[feature_cols])
y_all_scaled = scaler_y.transform(df_features[[target_col]])

# =========================================================
# 9. Sequence Preparation
# =========================================================
def create_sequences(X, y, dates, window):
    X_seq, y_seq, d_seq = [], [], []
    for i in range(len(X) - window):
        X_seq.append(X[i:i + window])
        y_seq.append(y[i + window])
        d_seq.append(dates[i + window])
    return np.array(X_seq), np.array(y_seq), np.array(d_seq)

X_seq, y_seq, date_seq = create_sequences(
    X_all_scaled,
    y_all_scaled,
    df_features.index,
    TIME_STEPS
)

split_date = train_df.index[-1]

train_mask = date_seq <= np.datetime64(split_date)
test_mask = date_seq > np.datetime64(split_date)

X_train = X_seq[train_mask]
X_test = X_seq[test_mask]
y_train = y_seq[train_mask]
y_test = y_seq[test_mask]
train_dates = date_seq[train_mask]
test_dates = date_seq[test_mask]

print("Train sequences:", X_train.shape)
print("Test sequences:", X_test.shape)

# =========================================================
# 10. BiGRU Model
# =========================================================
gru_model = Sequential([
    Bidirectional(GRU(96, return_sequences=True), input_shape=(TIME_STEPS, len(feature_cols))),
    Dropout(0.2),
    GRU(48),
    Dense(24, activation="relu"),
    Dense(1)
])

gru_model.compile(optimizer="adam", loss=Huber())

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=12,
    restore_best_weights=True
)

gru_model.fit(
    X_train,
    y_train,
    epochs=120,
    batch_size=32,
    validation_split=0.1,
    callbacks=[early_stop],
    shuffle=False,
    verbose=0
)

# =========================================================
# 11. Hybrid XGBoost Refinement
# =========================================================
gru_train_pred = gru_model.predict(X_train, verbose=0)
gru_test_pred = gru_model.predict(X_test, verbose=0)

X_train_xgb = np.column_stack([gru_train_pred.flatten(), X_train[:, -1, 1:]])
X_test_xgb = np.column_stack([gru_test_pred.flatten(), X_test[:, -1, 1:]])

xgb_model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=8,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_alpha=0.3,
    reg_lambda=1.5,
    objective="reg:squarederror",
    random_state=42
)

xgb_model.fit(X_train_xgb, y_train.flatten())

# =========================================================
# 12. Metrics Calculation
# =========================================================
y_test_pred_scaled = xgb_model.predict(X_test_xgb)

y_test_real = scaler_y.inverse_transform(y_test).flatten()
y_pred_real = scaler_y.inverse_transform(y_test_pred_scaled.reshape(-1, 1)).flatten()

# 按你 broccoli 长期代码保留 peak-aware post adjustment
peak_flags_test = []
for d in test_dates:
    if calculate_sf_weight(pd.Timestamp(d)) >= 8 or days_to_spring_festival(pd.Timestamp(d)) <= 7:
        peak_flags_test.append(1)
    else:
        peak_flags_test.append(0)

peak_flags_test = np.array(peak_flags_test)
y_pred_real = np.where(peak_flags_test == 1, y_pred_real * 1.12, y_pred_real)
y_pred_real = np.maximum(y_pred_real, 0)

mae = mean_absolute_error(y_test_real, y_pred_real)
rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))
smape = smape_func(y_test_real, y_pred_real)

# =========================================================
# 13. Future 7-Day Dynamic Recursive Prediction
# =========================================================
def predict_future(n_days=7):
    predictions = []

    current_window = X_all_scaled[-TIME_STEPS:].copy()
    current_sales_history = df_features["QuantitySoldKilo"].tolist()
    base_last_date = df_features.index[-1]

    for i in range(n_days):
        gru_p = gru_model.predict(
            current_window.reshape(1, TIME_STEPS, len(feature_cols)),
            verbose=0
        )

        xgb_input = np.column_stack([gru_p.flatten(), current_window[-1, 1:].reshape(1, -1)])
        xgb_p = xgb_model.predict(xgb_input)

        pred_val_scaled = xgb_p[0]
        pred_val_real = scaler_y.inverse_transform([[pred_val_scaled]])[0, 0]
        pred_val_real = max(0, pred_val_real)

        next_date = base_last_date + datetime.timedelta(days=i + 1)

        if calculate_sf_weight(next_date) >= 8 or days_to_spring_festival(next_date) <= 7:
            pred_val_real *= 1.12

        pred_val_real = max(0, pred_val_real)
        predictions.append(pred_val_real)

        current_sales_history.append(pred_val_real)

        try:
            lag_364_val = daily_sales.loc[next_date - datetime.timedelta(days=364), "QuantitySoldKilo"]
        except Exception:
            lag_364_val = np.mean(current_sales_history[-7:])

        rolling_mean_7 = np.mean(current_sales_history[-7:])
        rolling_std_7 = np.std(current_sales_history[-7:], ddof=0)
        rolling_max_7 = np.max(current_sales_history[-7:])
        lag_1 = current_sales_history[-2]
        lag_7 = current_sales_history[-8]
        lag_14 = current_sales_history[-15] if len(current_sales_history) >= 15 else np.mean(current_sales_history[-7:])
        peak_ratio_7 = lag_1 / (rolling_mean_7 + 1e-6)

        # 未来价格未知，用最近7天均值近似
        unit_price = daily_sales["UnitSellingPrice"].tail(7).mean()
        wholesale_price = daily_sales["WholesalePrice"].tail(7).mean()
        loss_rate = daily_sales["LossRatePct"].tail(7).mean()
        price_spread = unit_price - wholesale_price
        profit_rate = 0 if wholesale_price == 0 else price_spread / wholesale_price

        new_row = [
            pred_val_real,
            unit_price,
            wholesale_price,
            loss_rate,
            price_spread,
            profit_rate,
            next_date.weekday(),
            1 if next_date.weekday() >= 5 else 0,
            next_date.month,
            next_date.timetuple().tm_yday,
            int(next_date.isocalendar().week),
            1 if chinese_calendar.is_holiday(next_date) else 0,
            calculate_sf_weight(next_date),
            days_to_spring_festival(next_date),
            days_after_spring_festival(next_date),
            1 if (days_to_spring_festival(next_date) <= 12 or days_after_spring_festival(next_date) <= 3 or calculate_sf_weight(next_date) >= 8) else 0,
            rolling_mean_7,
            rolling_std_7,
            rolling_max_7,
            lag_1,
            lag_7,
            lag_14,
            lag_364_val,
            peak_ratio_7
        ]

        new_row_scaled = scaler_X.transform(pd.DataFrame([new_row], columns=feature_cols))
        current_window = np.vstack([current_window[1:], new_row_scaled])

    return predictions

future_pred = predict_future(FUTURE_DAYS)
future_dates = pd.date_range(
    start=df_features.index[-1] + pd.Timedelta(days=1),
    periods=FUTURE_DAYS
)

# 如果未来真实值存在，就取出来；没有就记为 NaN
future_actual = []
for d in future_dates:
    if d in actual_lookup.index:
        future_actual.append(float(actual_lookup.loc[d]))
    else:
        future_actual.append(np.nan)

future_actual = np.array(future_actual, dtype=float)

# =========================================================
# 14. Output Tables
# =========================================================
test_result_df = pd.DataFrame({
    "Date": pd.to_datetime(test_dates),
    "Actual": y_test_real,
    "Predicted": y_pred_real
})

future_result_df = pd.DataFrame({
    "Date": future_dates,
    "Predicted": future_pred,
    "Actual_if_available": future_actual
})

test_csv_path = os.path.join(OUTPUT_DIR, "green_eggplant_test_predictions.csv")
future_csv_path = os.path.join(OUTPUT_DIR, "green_eggplant_future_7days.csv")

test_result_df.to_csv(test_csv_path, index=False, encoding="utf-8-sig")
future_result_df.to_csv(future_csv_path, index=False, encoding="utf-8-sig")

# =========================================================
# 15. Visualization
# =========================================================
fig, ax = plt.subplots(figsize=(18, 9))

# 训练集真实值
y_train_real = scaler_y.inverse_transform(y_train).flatten()
ax.plot(train_dates, y_train_real, label="Train Actual", color="steelblue", alpha=0.25)

# 测试集真实值（橙色）
ax.plot(test_dates, y_test_real, label="Test Actual", color="orange", linewidth=2)

# 测试集预测值（绿色）
ax.plot(test_dates, y_pred_real, label="Test Predicted", color="green", linewidth=2)

# 未来 7 天预测（绿色虚线）
ax.plot(
    future_dates,
    future_pred,
    label="Future 7-Day Forecast",
    color="green",
    linestyle="--",
    marker="o",
    linewidth=2
)

# 如果未来真实值存在，就一起画出来（橙色）
if np.isfinite(future_actual).any():
    ax.plot(
        future_dates,
        future_actual,
        label="Future Actual (if available)",
        color="orange",
        linestyle=":",
        marker="s",
        linewidth=2
    )

ax.set_title(f"{MODEL_NAME}", fontsize=15, pad=20)
ax.set_xlabel("Date")
ax.set_ylabel("Quantity (Kilo)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")

# 顶部平铺指标框
metric_box_style = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#999999", alpha=0.95)

fig.text(0.20, 0.96, f"MAE\n{mae:.2f}", ha="center", va="top", fontsize=13, fontweight="bold", bbox=metric_box_style)
fig.text(0.50, 0.96, f"RMSE\n{rmse:.2f}", ha="center", va="top", fontsize=13, fontweight="bold", bbox=metric_box_style)
fig.text(0.80, 0.96, f"sMAPE\n{smape:.2f}%", ha="center", va="top", fontsize=13, fontweight="bold", bbox=metric_box_style)

plt.tight_layout(rect=[0, 0, 1, 0.90])

plot_path = os.path.join(OUTPUT_DIR, "green_eggplant_long_term_stable.png")
plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.show()

# =========================================================
# 16. Console Output
# =========================================================
print("=" * 70)
print(MODEL_NAME)
print("=" * 70)
print("Train sequences:", X_train.shape)
print("Test sequences:", X_test.shape)
print(f"MAE   : {mae:.2f}")
print(f"RMSE  : {rmse:.2f}")
print(f"sMAPE : {smape:.2f}%")
print("-" * 70)

print("\n[Test Set Predictions vs Actual]")
print(test_result_df.tail(20).to_string(index=False))

print("\n[Future 7-Day Forecast]")
for d, pred, actual in zip(future_dates, future_pred, future_actual):
    actual_str = f"{actual:.2f}" if np.isfinite(actual) else "N/A"
    print(f"{d.date()} | Predicted: {pred:.2f} | Actual: {actual_str}")

print("\nSaved files:")
print("Plot:", plot_path)
print("Test CSV:", test_csv_path)
print("Future CSV:", future_csv_path)