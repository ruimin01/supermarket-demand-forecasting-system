import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout

import xgboost as xgb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.db_service import get_connection

# ==========================================
# Config
# ==========================================
STOCK_CODE = "102900011008164"
MODEL_DIR = os.path.join(BASE_DIR, "models", "stable_short_term", "naibaicai")
os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================
# 1️⃣ Read Dataset From Database
# ==========================================
def load_data_from_db(stock_code: str) -> pd.DataFrame:
    sql = """
        SELECT
            p.stock_code,
            p.product_name,
            s.sales_date,
            s.quantity_sold,
            s.unit_selling_price,
            s.wholesale_price,
            s.loss_rate_pct
        FROM sales_records s
        JOIN products p ON s.product_id = p.product_id
        WHERE p.stock_code = %s
        ORDER BY s.sales_date ASC
    """

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (stock_code,))
            rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        raise ValueError(f"No data found for stock_code={stock_code}")

    df = pd.DataFrame(rows)
    return df


# ==========================================
# 2️⃣ Aggregate exactly like original stable short-time code
# ==========================================
def prepare_naibaicai_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    raw_df["sales_date"] = pd.to_datetime(raw_df["sales_date"], errors="coerce")

    naibaicai_df = raw_df.groupby("sales_date").agg({
        "quantity_sold": "sum",
        "unit_selling_price": "mean",
        "wholesale_price": "mean",
        "loss_rate_pct": "mean"
    }).reset_index()

    naibaicai_df = naibaicai_df.rename(columns={
        "sales_date": "Date",
        "quantity_sold": "Sales",
        "unit_selling_price": "Price",
        "wholesale_price": "Wholesale Price (RMB/kg)",
        "loss_rate_pct": "Loss Rate (%)"
    })

    naibaicai_df["Discount"] = 0
    naibaicai_df = naibaicai_df.sort_values("Date").reset_index(drop=True)

    # ==========================================
    # 3️⃣ Time Feature Engineering
    # ==========================================
    naibaicai_df["weekday"] = naibaicai_df["Date"].dt.weekday
    naibaicai_df["month"] = naibaicai_df["Date"].dt.month
    naibaicai_df["is_weekend"] = naibaicai_df["weekday"].isin([5, 6]).astype(int)

    # ==========================================
    # 4️⃣ Lag Features
    # ==========================================
    naibaicai_df["lag_1"] = naibaicai_df["Sales"].shift(1)
    naibaicai_df["lag_7"] = naibaicai_df["Sales"].shift(7)
    naibaicai_df["lag_14"] = naibaicai_df["Sales"].shift(14)

    naibaicai_df["rolling_mean_7"] = naibaicai_df["Sales"].rolling(7).mean()

    naibaicai_df = naibaicai_df.dropna().reset_index(drop=True)

    return naibaicai_df


# ==========================================
# 5️⃣ Feature Selection
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
# 6️⃣ Train Test Split (mimic original style)
# ==========================================
def build_time_splits(df: pd.DataFrame):
    max_date = df["Date"].max()
    window_start = max_date - pd.Timedelta(days=364)
    window_end = max_date

    df = df[(df["Date"] >= window_start) & (df["Date"] <= window_end)].copy()

    # 原代码风格：train 到最后7天前，test 提前30天开始以保证窗口
    forecast_start = window_end + pd.Timedelta(days=1)
    train_end = window_end - pd.Timedelta(days=7)
    test_start = train_end - pd.Timedelta(days=30)

    train_df = df[df["Date"] <= train_end].copy()
    test_df = df[df["Date"] > test_start].copy()

    return df, train_df, test_df, forecast_start


# ==========================================
# 7️⃣ Create GRU Sequences
# ==========================================
def create_sequences(X, y, time_steps=30):
    Xs, ys = [], []

    for i in range(time_steps, len(X)):
        Xs.append(X[i-time_steps:i])
        ys.append(y[i])

    return np.array(Xs), np.array(ys)


# ==========================================
# 8️⃣ sMAPE exactly like original stable short-time code
# ==========================================
def smape_func(y_true, y_pred):
    return np.mean(
        2 * np.abs(y_pred - y_true) /
        (np.abs(y_true) + np.abs(y_pred))
    ) * 100


# ==========================================
# 9️⃣ Training Pipeline
# ==========================================
def train_and_save():
    print("Step 1: Load data from database...")
    raw_df = load_data_from_db(STOCK_CODE)
    print(f"Loaded rows: {len(raw_df)}")

    print("Step 2: Prepare stable short-time features...")
    naibaicai_df = prepare_naibaicai_df(raw_df)
    print(f"Rows after feature engineering: {len(naibaicai_df)}")

    naibaicai_df, train_df, test_df, forecast_start = build_time_splits(naibaicai_df)

    train_dates = train_df["Date"]
    test_dates = test_df["Date"]

    print(f"Filtered yearly rows: {len(naibaicai_df)}")
    print(f"Train rows: {len(train_df)}")
    print(f"Test rows: {len(test_df)}")
    print(f"Forecast start: {forecast_start.date()}")

    # ==========================================
    # 7️⃣ Scaling
    # ==========================================
    feature_scaler = MinMaxScaler()
    target_scaler = MinMaxScaler()

    train_features_scaled = feature_scaler.fit_transform(train_df[gru_features])
    train_target_scaled = target_scaler.fit_transform(train_df[[target]])

    test_features_scaled = feature_scaler.transform(test_df[gru_features])
    test_target_scaled = target_scaler.transform(test_df[[target]])

    # ==========================================
    # 8️⃣ Create Sequences
    # ==========================================
    time_steps = 7

    X_train_gru, y_train_gru = create_sequences(
        train_features_scaled,
        train_target_scaled,
        time_steps
    )

    X_test_gru, y_test_gru = create_sequences(
        test_features_scaled,
        test_target_scaled,
        time_steps
    )

    print("Train sequences:", X_train_gru.shape)
    print("Test sequences:", X_test_gru.shape)

    # ==========================================
    # 9️⃣ GRU Model
    # ==========================================
    model = Sequential([
        GRU(64, return_sequences=True,
            input_shape=(X_train_gru.shape[1], X_train_gru.shape[2])),
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
    # 🔟 GRU Base Prediction
    # ==========================================
    y_pred_scaled = model.predict(X_test_gru, verbose=0)

    y_pred_gru = target_scaler.inverse_transform(y_pred_scaled).flatten()
    y_true = target_scaler.inverse_transform(y_test_gru).flatten()

    # ==========================================
    # 11️⃣ Residual
    # ==========================================
    residual = y_true - y_pred_gru

    # ==========================================
    # 12️⃣ XGBoost Residual Learning
    # ==========================================
    X_xgb_train = train_df[xgb_features].iloc[time_steps:].values
    X_xgb_test = test_df[xgb_features].iloc[time_steps:].values

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

    # ==========================================
    # 13️⃣ Final Hybrid Prediction
    # ==========================================
    final_pred = y_pred_gru + residual_correction

    # ==========================================
    # 14️⃣ Evaluation Metrics
    # ==========================================
    mae = mean_absolute_error(y_true, final_pred)
    rmse = np.sqrt(mean_squared_error(y_true, final_pred))
    smape = smape_func(y_true, final_pred)

    print(f"\nMAE: {mae:.2f} | RMSE: {rmse:.2f} | sMAPE: {smape:.2f}%")

    # ==========================================
    # 15️⃣ Save model artifacts
    # ==========================================
    model.save(os.path.join(MODEL_DIR, "gru_model.keras"))
    joblib.dump(gbm_model, os.path.join(MODEL_DIR, "xgb_model.pkl"))
    joblib.dump(feature_scaler, os.path.join(MODEL_DIR, "feature_scaler.pkl"))
    joblib.dump(target_scaler, os.path.join(MODEL_DIR, "target_scaler.pkl"))
    joblib.dump(scaler_xgb, os.path.join(MODEL_DIR, "xgb_scaler.pkl"))

    metadata = {
        "stock_code": STOCK_CODE,
        "model_type": "stable_short_term",
        "time_steps": 7,
        "future_days": 7,
        "gru_features": gru_features,
        "xgb_features": xgb_features,
        "target": target,
        "window_start": str(naibaicai_df["Date"].min().date()),
        "window_end": str(naibaicai_df["Date"].max().date()),
        "train_end": str(train_df["Date"].max().date()),
        "forecast_start": str(forecast_start.date()),
        "mae": float(mae),
        "rmse": float(rmse),
        "smape": float(smape)
    }

    with open(os.path.join(MODEL_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("Saved to:", MODEL_DIR)
    print("Training completed successfully.")


if __name__ == "__main__":
    train_and_save()
# import os
# import sys
# import json
# import joblib
# import numpy as np
# import pandas as pd

# from sklearn.preprocessing import MinMaxScaler, StandardScaler
# from sklearn.metrics import mean_absolute_error, mean_squared_error
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import GRU, Dense, Dropout
# from tensorflow.keras.callbacks import EarlyStopping
# import xgboost as xgb

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from services.db_service import get_connection

# # =========================
# # Config
# # =========================
# STOCK_CODE = "102900011008164"
# MODEL_DIR = os.path.join(BASE_DIR, "models", "stable_short_term", "naibaicai")
# os.makedirs(MODEL_DIR, exist_ok=True)

# TIME_STEPS = 7
# FUTURE_DAYS = 7

# GRU_FEATURES = [
#     "Price",
#     "WholesalePrice",
#     "Discount",
#     "LossRate",
#     "weekday",
#     "month",
#     "is_weekend",
#     "lag_1",
#     "lag_7",
#     "lag_14",
#     "rolling_mean_7",
# ]

# XGB_FEATURES = [
#     "weekday",
#     "month",
#     "is_weekend",
#     "lag_1",
#     "lag_7",
#     "lag_14",
#     "rolling_mean_7",
# ]

# TARGET_COL = "Sales"


# def load_data_from_db(stock_code: str) -> pd.DataFrame:
#     sql = """
#         SELECT
#             p.stock_code,
#             p.product_name,
#             s.sales_date,
#             s.quantity_sold,
#             s.unit_selling_price,
#             s.wholesale_price,
#             s.loss_rate_pct,
#             s.year,
#             s.month,
#             s.day,
#             s.day_of_week,
#             s.is_weekend
#         FROM sales_records s
#         JOIN products p ON s.product_id = p.product_id
#         WHERE p.stock_code = %s
#         ORDER BY s.sales_date ASC
#     """

#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(sql, (stock_code,))
#             rows = cursor.fetchall()
#     finally:
#         conn.close()

#     if not rows:
#         raise ValueError(f"No data found for stock_code={stock_code}")

#     df = pd.DataFrame(rows)

#     print("=== Raw Data Sample ===")
#     print(df.head())
#     print("\n=== Data Types Before Cleaning ===")
#     print(df.dtypes)

#     return df


# def prepare_daily_features(df: pd.DataFrame) -> pd.DataFrame:
#     # 先强制转字符串再转日期，出错的变成 NaT
#     df["sales_date"] = pd.to_datetime(df["sales_date"].astype(str), errors="coerce")

#     # 看看有没有坏值
#     bad_rows = df[df["sales_date"].isna()]
#     if not bad_rows.empty:
#         print("\n=== Bad sales_date rows detected ===")
#         print(bad_rows.head(20))
#         raise ValueError("Found invalid sales_date values in database query result.")

#     # 数值列转成数值
#     numeric_cols = [
#         "quantity_sold",
#         "unit_selling_price",
#         "wholesale_price",
#         "loss_rate_pct",
#     ]
#     for col in numeric_cols:
#         df[col] = pd.to_numeric(df[col], errors="coerce")

#     daily_df = (
#         df.groupby("sales_date")
#         .agg(
#             {
#                 "quantity_sold": "sum",
#                 "unit_selling_price": "mean",
#                 "wholesale_price": "mean",
#                 "loss_rate_pct": "mean",
#             }
#         )
#         .reset_index()
#     )

#     daily_df = daily_df.rename(
#         columns={
#             "sales_date": "Date",
#             "quantity_sold": "Sales",
#             "unit_selling_price": "Price",
#             "wholesale_price": "WholesalePrice",
#             "loss_rate_pct": "LossRate",
#         }
#     )

#     daily_df["Discount"] = 0.0
#     daily_df = daily_df.sort_values("Date").reset_index(drop=True)

#     # 时间特征
#     daily_df["weekday"] = daily_df["Date"].dt.weekday
#     daily_df["month"] = daily_df["Date"].dt.month
#     daily_df["is_weekend"] = daily_df["weekday"].isin([5, 6]).astype(int)

#     # 滞后特征
#     daily_df["lag_1"] = daily_df["Sales"].shift(1)
#     daily_df["lag_7"] = daily_df["Sales"].shift(7)
#     daily_df["lag_14"] = daily_df["Sales"].shift(14)
#     daily_df["rolling_mean_7"] = daily_df["Sales"].rolling(7).mean()

#     daily_df = daily_df.dropna().reset_index(drop=True)

#     if len(daily_df) < 60:
#         raise ValueError(
#             f"Data too short after feature engineering: only {len(daily_df)} rows."
#         )

#     print("\n=== Daily Feature Sample ===")
#     print(daily_df.head())
#     print(f"\nRows after feature engineering: {len(daily_df)}")

#     return daily_df


# def create_sequences(X, y, time_steps=7):
#     Xs, ys = [], []
#     for i in range(time_steps, len(X)):
#         Xs.append(X[i - time_steps : i])
#         ys.append(y[i])
#     return np.array(Xs), np.array(ys)


# def train_and_save():
#     print("Step 1: Load data from database...")
#     raw_df = load_data_from_db(STOCK_CODE)
#     print(f"Loaded rows: {len(raw_df)}")

#     print("Step 2: Prepare daily features...")
#     daily_df = prepare_daily_features(raw_df)
#     print(f"Rows after feature engineering: {len(daily_df)}")

#     # 按时间切分，最后 20% 作为测试集
#     split_idx = int(len(daily_df) * 0.8)
#     train_df = daily_df.iloc[:split_idx].copy()
#     test_df = daily_df.iloc[split_idx - TIME_STEPS :].copy()

#     print(f"Train rows: {len(train_df)}")
#     print(f"Test rows (with lookback): {len(test_df)}")

#     # scaler
#     feature_scaler = MinMaxScaler()
#     target_scaler = MinMaxScaler()

#     train_features_scaled = feature_scaler.fit_transform(train_df[GRU_FEATURES])
#     train_target_scaled = target_scaler.fit_transform(train_df[[TARGET_COL]])

#     test_features_scaled = feature_scaler.transform(test_df[GRU_FEATURES])
#     test_target_scaled = target_scaler.transform(test_df[[TARGET_COL]])

#     # sequence
#     X_train_gru, y_train_gru = create_sequences(
#         train_features_scaled, train_target_scaled, TIME_STEPS
#     )
#     X_test_gru, y_test_gru = create_sequences(
#         test_features_scaled, test_target_scaled, TIME_STEPS
#     )

#     print("Step 3: Train GRU...")
#     model = Sequential(
#         [
#             GRU(
#                 64,
#                 return_sequences=True,
#                 input_shape=(X_train_gru.shape[1], X_train_gru.shape[2]),
#             ),
#             Dropout(0.2),
#             GRU(32),
#             Dense(1),
#         ]
#     )
#     model.compile(optimizer="adam", loss="mse")

#     early_stop = EarlyStopping(
#         monitor="val_loss", patience=5, restore_best_weights=True
#     )

#     model.fit(
#         X_train_gru,
#         y_train_gru,
#         epochs=30,
#         batch_size=16,
#         validation_split=0.1,
#         shuffle=False,
#         verbose=1,
#         callbacks=[early_stop],
#     )

#     print("Step 4: GRU prediction on test set...")
#     y_pred_scaled = model.predict(X_test_gru, verbose=0)
#     y_pred_gru = target_scaler.inverse_transform(y_pred_scaled).flatten()
#     y_true = target_scaler.inverse_transform(y_test_gru).flatten()

#     # XGBoost residual learning
#     print("Step 5: Train XGBoost on residuals...")
#     X_xgb_train = train_df[XGB_FEATURES].iloc[TIME_STEPS:].values
#     X_xgb_test = test_df[XGB_FEATURES].iloc[TIME_STEPS:].values

#     scaler_xgb = StandardScaler()
#     X_xgb_train_scaled = scaler_xgb.fit_transform(X_xgb_train)
#     X_xgb_test_scaled = scaler_xgb.transform(X_xgb_test)

#     train_pred_scaled = model.predict(X_train_gru, verbose=0)
#     train_pred = target_scaler.inverse_transform(train_pred_scaled).flatten()
#     train_true = target_scaler.inverse_transform(y_train_gru).flatten()
#     train_residual = train_true - train_pred

#     xgb_model = xgb.XGBRegressor(
#         n_estimators=200,
#         max_depth=4,
#         learning_rate=0.05,
#         subsample=0.9,
#         colsample_bytree=0.9,
#         random_state=42,
#     )

#     xgb_model.fit(X_xgb_train_scaled, train_residual)

#     xgb_residual_test = xgb_model.predict(X_xgb_test_scaled)
#     y_pred_final = y_pred_gru + xgb_residual_test

#     mae = mean_absolute_error(y_true, y_pred_final)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred_final))

#     print("\n=== Evaluation ===")
#     print(f"MAE:  {mae:.4f}")
#     print(f"RMSE: {rmse:.4f}")

#     print("Step 6: Save model artifacts...")
#     model.save(os.path.join(MODEL_DIR, "gru_model.keras"))
#     joblib.dump(xgb_model, os.path.join(MODEL_DIR, "xgb_model.pkl"))
#     joblib.dump(feature_scaler, os.path.join(MODEL_DIR, "feature_scaler.pkl"))
#     joblib.dump(target_scaler, os.path.join(MODEL_DIR, "target_scaler.pkl"))
#     joblib.dump(scaler_xgb, os.path.join(MODEL_DIR, "xgb_scaler.pkl"))

#     metadata = {
#         "stock_code": STOCK_CODE,
#         "model_type": "stable_short_term",
#         "time_steps": TIME_STEPS,
#         "future_days": FUTURE_DAYS,
#         "gru_features": GRU_FEATURES,
#         "xgb_features": XGB_FEATURES,
#         "target_col": TARGET_COL,
#         "train_rows": int(len(train_df)),
#         "test_rows": int(len(test_df)),
#         "mae": float(mae),
#         "rmse": float(rmse),
#     }

#     with open(os.path.join(MODEL_DIR, "metadata.json"), "w", encoding="utf-8") as f:
#         json.dump(metadata, f, ensure_ascii=False, indent=2)

#     print("Saved to:", MODEL_DIR)
#     print("Training completed successfully.")


# if __name__ == "__main__":
#     train_and_save()