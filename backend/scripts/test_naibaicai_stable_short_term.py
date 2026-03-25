import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.db_service import get_connection

STOCK_CODE = "102900011008164"
MODEL_DIR = os.path.join(BASE_DIR, "models", "stable_short_term", "naibaicai")


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

    return pd.DataFrame(rows)


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

    naibaicai_df["weekday"] = naibaicai_df["Date"].dt.weekday
    naibaicai_df["month"] = naibaicai_df["Date"].dt.month
    naibaicai_df["is_weekend"] = naibaicai_df["weekday"].isin([5, 6]).astype(int)

    naibaicai_df["lag_1"] = naibaicai_df["Sales"].shift(1)
    naibaicai_df["lag_7"] = naibaicai_df["Sales"].shift(7)
    naibaicai_df["lag_14"] = naibaicai_df["Sales"].shift(14)
    naibaicai_df["rolling_mean_7"] = naibaicai_df["Sales"].rolling(7).mean()

    naibaicai_df = naibaicai_df.dropna().reset_index(drop=True)

    return naibaicai_df


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


def build_time_splits(df: pd.DataFrame):
    max_date = df["Date"].max()
    window_start = max_date - pd.Timedelta(days=364)
    window_end = max_date

    df = df[(df["Date"] >= window_start) & (df["Date"] <= window_end)].copy()

    forecast_start = window_end + pd.Timedelta(days=1)
    train_end = window_end - pd.Timedelta(days=7)
    test_start = train_end - pd.Timedelta(days=30)

    train_df = df[df["Date"] <= train_end].copy()
    test_df = df[df["Date"] > test_start].copy()

    return df, train_df, test_df, forecast_start


def create_sequences(X, y, time_steps=30):
    Xs, ys = [], []

    for i in range(time_steps, len(X)):
        Xs.append(X[i-time_steps:i])
        ys.append(y[i])

    return np.array(Xs), np.array(ys)


def smape_func(y_true, y_pred):
    return np.mean(
        2 * np.abs(y_pred - y_true) /
        (np.abs(y_true) + np.abs(y_pred))
    ) * 100


def main():
    with open(os.path.join(MODEL_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)

    time_steps = metadata["time_steps"]

    model = load_model(os.path.join(MODEL_DIR, "gru_model.keras"))
    gbm_model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
    feature_scaler = joblib.load(os.path.join(MODEL_DIR, "feature_scaler.pkl"))
    target_scaler = joblib.load(os.path.join(MODEL_DIR, "target_scaler.pkl"))
    scaler_xgb = joblib.load(os.path.join(MODEL_DIR, "xgb_scaler.pkl"))

    raw_df = load_data_from_db(STOCK_CODE)
    naibaicai_df = prepare_naibaicai_df(raw_df)
    naibaicai_df, train_df, test_df, forecast_start = build_time_splits(naibaicai_df)

    train_dates = train_df["Date"]
    test_dates = test_df["Date"]

    train_features_scaled = feature_scaler.transform(train_df[gru_features])
    train_target_scaled = target_scaler.transform(train_df[[target]])

    test_features_scaled = feature_scaler.transform(test_df[gru_features])
    test_target_scaled = target_scaler.transform(test_df[[target]])

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

    # GRU base prediction
    y_pred_scaled = model.predict(X_test_gru, verbose=0)
    y_pred_gru = target_scaler.inverse_transform(y_pred_scaled).flatten()
    y_true = target_scaler.inverse_transform(y_test_gru).flatten()

    # XGBoost residual correction
    X_xgb_train = train_df[xgb_features].iloc[time_steps:].values
    X_xgb_test = test_df[xgb_features].iloc[time_steps:].values

    X_xgb_train = scaler_xgb.transform(X_xgb_train)
    X_xgb_test = scaler_xgb.transform(X_xgb_test)

    train_pred_scaled = model.predict(X_train_gru, verbose=0)
    train_pred = target_scaler.inverse_transform(train_pred_scaled).flatten()
    train_true = target_scaler.inverse_transform(y_train_gru).flatten()

    train_residual = train_true - train_pred
    residual_correction = gbm_model.predict(X_xgb_test)

    # Final hybrid prediction
    final_pred = y_pred_gru + residual_correction

    # Metrics
    mae = mean_absolute_error(y_true, final_pred)
    rmse = np.sqrt(mean_squared_error(y_true, final_pred))
    smape = smape_func(y_true, final_pred)

    # Future 7-day forecast
    future_dates = pd.date_range(start=forecast_start, periods=7)

    last_window = test_features_scaled[-time_steps:]
    future_preds = []
    current_window = last_window.copy()

    for _ in range(7):
        pred = model.predict(current_window.reshape(1, time_steps, -1), verbose=0)
        pred_real = target_scaler.inverse_transform(pred)[0][0]
        future_preds.append(pred_real)

        new_row = current_window[-1].copy()
        new_row[gru_features.index("lag_1")] = pred_real
        current_window = np.vstack([current_window[1:], new_row])

    future_real = np.array(future_preds)

    # ========= 先打印，再画图 =========
    print("Train sequences:", X_train_gru.shape)
    print("Test sequences:", X_test_gru.shape)
    print(f"\nMAE: {mae:.2f} | RMSE: {rmse:.2f} | sMAPE: {smape:.2f}%")

    print(f"\n--- {future_dates[0].date()} To {future_dates[-1].date()} Forecast ---")
    for d, v in zip(future_dates, future_real):
        print(f"{d.date()}: {v:.2f} Kilo")

    # 保存预测结果 CSV
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "PredictedSalesKilo": future_real
    })
    forecast_csv_path = os.path.join(MODEL_DIR, "naibaicai_7day_forecast.csv")
    forecast_df.to_csv(forecast_csv_path, index=False, encoding="utf-8-sig")
    print(f"\nForecast CSV saved to: {forecast_csv_path}")

    # Visualization
    plt.figure(figsize=(16, 8))

    y_train_real = train_df["Sales"].values
    y_test_real = y_true
    y_pred_real = final_pred

    metrics_str = f"MAE: {mae:.2f}  |  RMSE: {rmse:.2f}  |  sMAPE: {smape:.2f}%"

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
        test_dates[time_steps:],
        y_test_real,
        label="Actual Sales",
        color="orange",
        linewidth=2
    )

    plt.plot(
        test_dates[time_steps:],
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
        "Strong Peak Detection: Hybrid GRU-XGBoost Naibaicai Sales Forecast",
        fontsize=12,
        pad=20
    )

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    main()
# import os
# import sys
# import json
# import joblib
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# from sklearn.metrics import mean_absolute_error, mean_squared_error
# from tensorflow.keras.models import load_model

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

# from services.db_service import get_connection

# STOCK_CODE = "102900011008164"
# MODEL_DIR = os.path.join(BASE_DIR, "models", "stable_short_term", "naibaicai")


# def smape(y_true, y_pred):
#     y_true = np.array(y_true)
#     y_pred = np.array(y_pred)
#     denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
#     diff = np.abs(y_true - y_pred)
#     mask = denominator != 0
#     return np.mean(diff[mask] / denominator[mask]) * 100


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
#     return df


# def prepare_daily_features(df: pd.DataFrame) -> pd.DataFrame:
#     df["sales_date"] = pd.to_datetime(df["sales_date"].astype(str), errors="coerce")

#     bad_rows = df[df["sales_date"].isna()]
#     if not bad_rows.empty:
#         print("\n=== Bad sales_date rows detected ===")
#         print(bad_rows.head(20))
#         raise ValueError("Found invalid sales_date values in database query result.")

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

#     return daily_df


# def create_sequences(X, y, time_steps=7):
#     Xs, ys = [], []
#     for i in range(time_steps, len(X)):
#         Xs.append(X[i - time_steps : i])
#         ys.append(y[i])
#     return np.array(Xs), np.array(ys)


# def build_next_day_row(history_df: pd.DataFrame, next_date: pd.Timestamp) -> pd.Series:
#     row = {}

#     row["Date"] = next_date
#     row["weekday"] = next_date.weekday()
#     row["month"] = next_date.month
#     row["is_weekend"] = 1 if next_date.weekday() in [5, 6] else 0

#     # 价格类先用最近7天均值近似
#     row["Price"] = history_df["Price"].tail(7).mean()
#     row["WholesalePrice"] = history_df["WholesalePrice"].tail(7).mean()
#     row["LossRate"] = history_df["LossRate"].tail(7).mean()
#     row["Discount"] = 0.0

#     row["lag_1"] = history_df["Sales"].iloc[-1]
#     row["lag_7"] = history_df["Sales"].iloc[-7]
#     row["lag_14"] = history_df["Sales"].iloc[-14]
#     row["rolling_mean_7"] = history_df["Sales"].tail(7).mean()

#     row["Sales"] = np.nan
#     return pd.Series(row)


# def main():
#     # 1. 加载 metadata 和模型文件
#     with open(os.path.join(MODEL_DIR, "metadata.json"), "r", encoding="utf-8") as f:
#         metadata = json.load(f)

#     gru_features = metadata["gru_features"]
#     xgb_features = metadata["xgb_features"]
#     time_steps = metadata["time_steps"]
#     future_days = metadata["future_days"]

#     gru_model = load_model(os.path.join(MODEL_DIR, "gru_model.keras"))
#     xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
#     feature_scaler = joblib.load(os.path.join(MODEL_DIR, "feature_scaler.pkl"))
#     target_scaler = joblib.load(os.path.join(MODEL_DIR, "target_scaler.pkl"))
#     xgb_scaler = joblib.load(os.path.join(MODEL_DIR, "xgb_scaler.pkl"))

#     # 2. 取数据库数据并构造特征
#     raw_df = load_data_from_db(STOCK_CODE)
#     daily_df = prepare_daily_features(raw_df)

#     # 3. 按与训练相同方式切分
#     split_idx = int(len(daily_df) * 0.8)
#     train_df = daily_df.iloc[:split_idx].copy()
#     test_df = daily_df.iloc[split_idx - time_steps :].copy()

#     # 4. 缩放
#     train_features_scaled = feature_scaler.transform(train_df[gru_features])
#     train_target_scaled = target_scaler.transform(train_df[["Sales"]])

#     test_features_scaled = feature_scaler.transform(test_df[gru_features])
#     test_target_scaled = target_scaler.transform(test_df[["Sales"]])

#     X_train_gru, y_train_gru = create_sequences(train_features_scaled, train_target_scaled, time_steps)
#     X_test_gru, y_test_gru = create_sequences(test_features_scaled, test_target_scaled, time_steps)

#     # 5. 测试集预测
#     y_pred_scaled = gru_model.predict(X_test_gru, verbose=0)
#     y_pred_gru = target_scaler.inverse_transform(y_pred_scaled).flatten()
#     y_test_real = target_scaler.inverse_transform(y_test_gru).flatten()

#     X_xgb_test = test_df[xgb_features].iloc[time_steps:].values
#     X_xgb_test_scaled = xgb_scaler.transform(X_xgb_test)
#     residual_pred = xgb_model.predict(X_xgb_test_scaled)

#     y_pred_real = y_pred_gru + residual_pred

#     mae = mean_absolute_error(y_test_real, y_pred_real)
#     rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))
#     smape_value = smape(y_test_real, y_pred_real)

#     # 6. 未来7天递推预测
#     current_history = daily_df.copy()
#     future_preds = []

#     for _ in range(future_days):
#         next_date = current_history["Date"].iloc[-1] + pd.Timedelta(days=1)
#         next_row = build_next_day_row(current_history, next_date)

#         temp_df = pd.concat([current_history, pd.DataFrame([next_row])], ignore_index=True)

#         last_seq_df = temp_df.tail(time_steps)[gru_features]
#         last_seq_scaled = feature_scaler.transform(last_seq_df)
#         X_seq = np.expand_dims(last_seq_scaled, axis=0)

#         gru_pred_scaled = gru_model.predict(X_seq, verbose=0)
#         gru_pred_real = target_scaler.inverse_transform(gru_pred_scaled).flatten()[0]

#         xgb_input = pd.DataFrame([next_row])[xgb_features].values
#         xgb_input_scaled = xgb_scaler.transform(xgb_input)
#         residual_future = xgb_model.predict(xgb_input_scaled)[0]

#         final_pred = max(gru_pred_real + residual_future, 0.0)

#         next_row["Sales"] = final_pred
#         current_history = pd.concat([current_history, pd.DataFrame([next_row])], ignore_index=True)

#         future_preds.append(final_pred)

#     future_real = np.array(future_preds)
#     future_dates = pd.date_range(
#         start=daily_df["Date"].iloc[-1] + pd.Timedelta(days=1),
#         periods=future_days
#     )

#     # 7. 准备画图数据
#     y_train_real = train_df["Sales"].values
#     train_dates = train_df["Date"].values
#     test_dates = test_df["Date"].values

#     # 你原文件里的风格：test_dates[time_steps:] 对齐真实测试值和预测值
#     test_plot_dates = test_dates[time_steps:]

#     # 8. 打印未来7天
#     print("\n=== 7-Day Forecast ===")
#     for d, v in zip(future_dates, future_real):
#         print(f"{d.date()}: {v:.2f} Kilo")

#     print(f"\nMAE: {mae:.2f} | RMSE: {rmse:.2f} | sMAPE: {smape_value:.2f}%")

#     # 9. 本地可视化（严格按你文件里的风格）
#     plt.figure(figsize=(16, 8))

#     metrics_str = f"MAE: {mae:.2f}  |  RMSE: {rmse:.2f}  |  sMAPE: {smape_value:.2f}%"
#     plt.suptitle(
#         metrics_str,
#         fontsize=14,
#         y=0.95,
#         color="darkblue",
#         fontweight="bold"
#     )

#     plt.plot(
#         train_dates,
#         y_train_real,
#         label="Train Data",
#         color="blue",
#         alpha=0.3
#     )

#     plt.plot(
#         test_plot_dates,
#         y_test_real,
#         label="Actual Sales",
#         color="orange",
#         linewidth=2
#     )

#     plt.plot(
#         test_plot_dates,
#         y_pred_real,
#         label="Hybrid Prediction",
#         color="black",
#         linestyle="--"
#     )

#     plt.plot(
#         future_dates,
#         future_real,
#         label="7-Day Future",
#         color="green",
#         marker="o"
#     )

#     plt.title(
#         "Peak-Aware Optimized GRU-XGBoost Naibaicai Sales Forecast",
#         fontsize=14
#     )
#     plt.xlabel("Date")
#     plt.ylabel("Quantity (Kilo)")
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.show()


# if __name__ == "__main__":
#     main()
