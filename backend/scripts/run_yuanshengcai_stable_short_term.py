import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, Input

import xgboost as xgb

# ==========================================
# 0. Basic config
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "vegetable_cleaned.csv")

TARGET_STOCK_CODE = "102900005115779"
TIME_STEPS = 7

np.random.seed(42)

# ==========================================
# 1. Read Dataset
# ==========================================
df = pd.read_csv(FILE_PATH)
df["Date"] = pd.to_datetime(df["Date"])
df["StockCode"] = df["StockCode"].astype(str).str.strip()

# ==========================================
# 2. Filter target stock code
# (single stock code, not item-name group)
# ==========================================
target_df = df[df["StockCode"] == TARGET_STOCK_CODE].copy()

if target_df.empty:
    raise ValueError(f"No data found for stock code {TARGET_STOCK_CODE}")

print("=" * 60)
print("Target stock code:", TARGET_STOCK_CODE)
print("Matched rows:", len(target_df))
print("Matched item names:")
print(target_df["ItemName"].dropna().unique())
print("=" * 60)

# ==========================================
# 3. Aggregate by date
# Follow your broccoli short-term stable logic:
# - group by Date
# - sum sales
# - mean price / wholesale / loss
# - DO NOT reindex
# - DO NOT create zero-demand rows
# ==========================================
target_daily = target_df.groupby("Date").agg({
    "QuantitySoldKilo": "sum",
    "UnitSellingPrice": "mean",
    "WholesalePrice": "mean",
    "LossRatePct": "mean"
}).reset_index()

target_daily = target_daily.rename(columns={
    "QuantitySoldKilo": "Sales",
    "UnitSellingPrice": "Price",
    "WholesalePrice": "Wholesale Price (RMB/kg)",
    "LossRatePct": "Loss Rate (%)"
})

target_daily["Discount"] = 0
target_daily = target_daily.sort_values("Date").reset_index(drop=True)

# ==========================================
# 4. Time Feature Engineering
# ==========================================
target_daily["weekday"] = target_daily["Date"].dt.weekday
target_daily["month"] = target_daily["Date"].dt.month
target_daily["is_weekend"] = target_daily["weekday"].isin([5, 6]).astype(int)

# ==========================================
# 5. Lag Features
# ==========================================
target_daily["lag_1"] = target_daily["Sales"].shift(1)
target_daily["lag_7"] = target_daily["Sales"].shift(7)
target_daily["lag_14"] = target_daily["Sales"].shift(14)
target_daily["rolling_mean_7"] = target_daily["Sales"].rolling(7).mean()

target_daily = target_daily.dropna().reset_index(drop=True)

print("Rows after feature engineering:", len(target_daily))

# ==========================================
# 6. Feature Selection
# Keep same feature structure as your broccoli code
# ==========================================
gru_features = [
    "Price",
    "Wholesale Price (RMB/kg)",
    "Discount",
    "Loss Rate (%)",
    "weekday",
    "month",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7"
]

xgb_features = [
    "weekday",
    "month",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7"
]

target = "Sales"

# ==========================================
# 7. Keep same time style as original broccoli code
# Broccoli short-term stable:
# 2021 train period and Jan 1–7 2022 future forecast style
# ==========================================
target_daily = target_daily[
    (target_daily["Date"] >= "2021-01-01") &
    (target_daily["Date"] <= "2021-12-31")
].copy()

train_df = target_daily[target_daily["Date"] <= "2021-12-24"].copy()
test_df = target_daily[target_daily["Date"] > "2021-12-01"].copy()

if len(train_df) <= TIME_STEPS or len(test_df) <= TIME_STEPS:
    raise ValueError("Not enough rows for this 2021 short-term stable split. You need more data or another split.")

train_dates = train_df["Date"].reset_index(drop=True)
test_dates = test_df["Date"].reset_index(drop=True)

# ==========================================
# 8. Scaling
# ==========================================
feature_scaler = MinMaxScaler()
target_scaler = MinMaxScaler()

train_features_scaled = feature_scaler.fit_transform(train_df[gru_features])
train_target_scaled = target_scaler.fit_transform(train_df[[target]])

test_features_scaled = feature_scaler.transform(test_df[gru_features])
test_target_scaled = target_scaler.transform(test_df[[target]])

# ==========================================
# 9. Sequence builder
# ==========================================
def create_sequences(X, y, time_steps=7):
    Xs, ys = [], []
    for i in range(time_steps, len(X)):
        Xs.append(X[i-time_steps:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

X_train_gru, y_train_gru = create_sequences(train_features_scaled, train_target_scaled, TIME_STEPS)
X_test_gru, y_test_gru = create_sequences(test_features_scaled, test_target_scaled, TIME_STEPS)

print("Train sequences:", X_train_gru.shape)
print("Test sequences:", X_test_gru.shape)

# ==========================================
# 10. GRU Model
# Match original structure more closely
# ==========================================
model = Sequential([
    Input(shape=(X_train_gru.shape[1], X_train_gru.shape[2])),
    GRU(64, return_sequences=True),
    Dropout(0.2),
    GRU(32),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")

model.fit(
    X_train_gru,
    y_train_gru,
    epochs=30,
    batch_size=32,
    validation_split=0.1,
    shuffle=False,
    verbose=0
)

# ==========================================
# 11. GRU Base Prediction
# ==========================================
y_pred_scaled = model.predict(X_test_gru, verbose=0)

y_pred_gru = target_scaler.inverse_transform(y_pred_scaled).flatten()
y_true = target_scaler.inverse_transform(y_test_gru).flatten()

# ==========================================
# 12. XGBoost residual learning
# ==========================================
X_xgb_train = train_df[xgb_features].iloc[TIME_STEPS:].values
X_xgb_test = test_df[xgb_features].iloc[TIME_STEPS:].values

scaler_xgb = StandardScaler()
X_xgb_train = scaler_xgb.fit_transform(X_xgb_train)
X_xgb_test = scaler_xgb.transform(X_xgb_test)

train_pred_scaled = model.predict(X_train_gru, verbose=0)
train_pred = target_scaler.inverse_transform(train_pred_scaled).flatten()
train_true = target_scaler.inverse_transform(y_train_gru).flatten()

train_residual = train_true - train_pred

gbm_model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

gbm_model.fit(X_xgb_train, train_residual)
residual_correction = gbm_model.predict(X_xgb_test)

# Keep original logic: no clipping before metrics
final_pred = y_pred_gru + residual_correction

# ==========================================
# 13. Metrics
# Use SAME sMAPE formula as your original broccoli code
# ==========================================
mae = mean_absolute_error(y_true, final_pred)
rmse = np.sqrt(mean_squared_error(y_true, final_pred))

def smape(y_true, y_pred):
    return np.mean(
        2 * np.abs(y_pred - y_true) /
        (np.abs(y_true) + np.abs(y_pred))
    ) * 100

smape_value = smape(y_true, final_pred)

print("\n" + "=" * 60)
print("Stable Short-Term Hybrid GRU-XGBoost Evaluation")
print(f"Stock Code: {TARGET_STOCK_CODE}")
print(f"MAE   : {mae:.4f}")
print(f"RMSE  : {rmse:.4f}")
print(f"sMAPE : {smape_value:.4f}%")
print("=" * 60)

# ==========================================
# 14. Data diagnosis
# This helps explain why sMAPE may be higher
# ==========================================
diag_df = pd.DataFrame({
    "Date": test_dates.iloc[TIME_STEPS:].reset_index(drop=True),
    "Actual": y_true,
    "Predicted": final_pred
})

print("\n--- Test Prediction Sample (first 15 rows) ---")
print(diag_df.head(15).to_string(index=False))

print("\n--- Actual Sales Distribution (Test) ---")
print(pd.Series(y_true).describe())

small_value_ratio = np.mean(y_true < 5) * 100
print(f"\nRatio of test actual values < 5 kg: {small_value_ratio:.2f}%")

# ==========================================
# 15. Future 7-Day Forecast
# Keep original broccoli code style:
# only recursively update lag_1
# ==========================================
future_dates = pd.date_range(start="2022-01-01", periods=7)

last_window = test_features_scaled[-TIME_STEPS:]
future_preds = []
current_window = last_window.copy()

for i in range(7):
    pred = model.predict(current_window.reshape(1, TIME_STEPS, -1), verbose=0)
    pred_real = target_scaler.inverse_transform(pred)[0][0]
    future_preds.append(pred_real)

    new_row = current_window[-1].copy()
    new_row[gru_features.index("lag_1")] = pred_real
    current_window = np.vstack([current_window[1:], new_row])

future_real = np.array(future_preds)

# ==========================================
# 16. Visualization
# EXACTLY match your original short-term stable broccoli style
# ==========================================
plt.figure(figsize=(16, 8))

y_train_real = train_df["Sales"].values
y_test_real = y_true
y_pred_real = final_pred

metrics_str = f"MAE: {mae:.2f}  |  RMSE: {rmse:.2f}  |  sMAPE: {smape_value:.2f}%"

plt.suptitle(
    metrics_str,
    fontsize=14,
    y=0.95,
    color="darkblue",
    fontweight="bold"
)

plt.plot(
    train_dates,
    y_train_real,
    label="Train Data",
    color="blue",
    alpha=0.3
)

plt.plot(
    test_dates.iloc[TIME_STEPS:],
    y_test_real,
    label="Actual Sales",
    color="orange",
    linewidth=2
)

plt.plot(
    test_dates.iloc[TIME_STEPS:],
    y_pred_real,
    label="Hybrid Prediction",
    color="black",
    linestyle="--"
)

plt.plot(
    future_dates,
    future_real,
    label="7-Day Future",
    color="green",
    marker="o"
)

plt.title(
    f"Stable Short-Term Hybrid Forecast ({TARGET_STOCK_CODE})",
    fontsize=12,
    pad=20
)

plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# ==========================================
# 17. Output
# Match your original style
# ==========================================
print("Train sequences:", X_train_gru.shape)
print("Test sequences:", X_test_gru.shape)
print(f"\nMAE: {mae:.2f} | RMSE: {rmse:.2f} | sMAPE: {smape_value:.2f}%")

print("\n--- 2022-01-01 To 2022-01-07 Forecast ---")
for d, v in zip(future_dates, future_real):
    print(f"{d.date()}: {v:.2f} Kilo")