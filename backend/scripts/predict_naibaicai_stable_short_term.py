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

MODEL_DIR = os.path.join(BASE_DIR, "models", "stable_short_term", "naibaicai")


# =========================
# Utility
# =========================
def smape_func(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    denominator = np.abs(y_true) + np.abs(y_pred)
    mask = denominator != 0
    if mask.sum() == 0:
        return np.nan
    return np.mean(
        2 * np.abs(y_pred[mask] - y_true[mask]) / denominator[mask]
    ) * 100


# =========================
# 1. Load history window from DB
# =========================
def load_history_from_db(stock_code: str, history_start: str, history_end: str) -> pd.DataFrame:
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
          AND s.sales_date >= %s
          AND s.sales_date <= %s
        ORDER BY s.sales_date ASC
    """

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (stock_code, history_start, history_end))
            rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        raise ValueError(
            f"No history data found for stock_code={stock_code}, "
            f"history window={history_start} to {history_end}"
        )

    return pd.DataFrame(rows)


# =========================
# 2. Load actual future values if they exist
# =========================
def load_actuals_from_db(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
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
          AND s.sales_date >= %s
          AND s.sales_date <= %s
        ORDER BY s.sales_date ASC
    """

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (stock_code, start_date, end_date))
            rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


# =========================
# 3. Prepare data exactly like training code
# =========================
def prepare_naibaicai_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    raw_df["sales_date"] = pd.to_datetime(raw_df["sales_date"], errors="coerce")

    numeric_cols = [
        "quantity_sold",
        "unit_selling_price",
        "wholesale_price",
        "loss_rate_pct"
    ]
    for col in numeric_cols:
        raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")

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

    naibaicai_df["Discount"] = 0.0
    naibaicai_df = naibaicai_df.sort_values("Date").reset_index(drop=True)

    float_cols = ["Sales", "Price", "Wholesale Price (RMB/kg)", "Loss Rate (%)", "Discount"]
    for col in float_cols:
        naibaicai_df[col] = pd.to_numeric(naibaicai_df[col], errors="coerce").astype(float)

    naibaicai_df["weekday"] = naibaicai_df["Date"].dt.weekday.astype(int)
    naibaicai_df["month"] = naibaicai_df["Date"].dt.month.astype(int)
    naibaicai_df["is_weekend"] = naibaicai_df["weekday"].isin([5, 6]).astype(int)

    naibaicai_df["lag_1"] = naibaicai_df["Sales"].shift(1)
    naibaicai_df["lag_7"] = naibaicai_df["Sales"].shift(7)
    naibaicai_df["lag_14"] = naibaicai_df["Sales"].shift(14)
    naibaicai_df["rolling_mean_7"] = naibaicai_df["Sales"].rolling(7).mean()

    naibaicai_df = naibaicai_df.dropna().reset_index(drop=True)

    numeric_feature_cols = [
        "Sales", "Price", "Wholesale Price (RMB/kg)", "Loss Rate (%)",
        "Discount", "weekday", "month", "is_weekend",
        "lag_1", "lag_7", "lag_14", "rolling_mean_7"
    ]
    for col in numeric_feature_cols:
        naibaicai_df[col] = pd.to_numeric(naibaicai_df[col], errors="coerce")

    return naibaicai_df


# =========================
# 4. Predict date range without leakage
# =========================
def predict_range(stock_code: str, start_date: str, end_date: str):
    with open(os.path.join(MODEL_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)

    time_steps = metadata["time_steps"]
    gru_features = metadata["gru_features"]
    xgb_features = metadata["xgb_features"]

    model = load_model(os.path.join(MODEL_DIR, "gru_model.keras"))
    gbm_model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
    feature_scaler = joblib.load(os.path.join(MODEL_DIR, "feature_scaler.pkl"))
    target_scaler = joblib.load(os.path.join(MODEL_DIR, "target_scaler.pkl"))
    scaler_xgb = joblib.load(os.path.join(MODEL_DIR, "xgb_scaler.pkl"))

    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    if end_dt < start_dt:
        raise ValueError("end_date must be later than or equal to start_date")

    forecast_days = (end_dt - start_dt).days + 1

    # 历史窗口：严格只取 start_date 前 365 天
    history_start_dt = start_dt - pd.Timedelta(days=365)
    history_end_dt = start_dt - pd.Timedelta(days=1)

    history_start = history_start_dt.strftime("%Y-%m-%d")
    history_end = history_end_dt.strftime("%Y-%m-%d")

    print("=== Prediction Request ===")
    print("stock_code:", stock_code)
    print("forecast_start:", start_date)
    print("forecast_end:", end_date)
    print("history_start:", history_start)
    print("history_end:", history_end)
    print("forecast_days:", forecast_days)

    raw_history_df = load_history_from_db(stock_code, history_start, history_end)
    history_df = prepare_naibaicai_df(raw_history_df)

    if len(history_df) < max(30, time_steps + 1):
        raise ValueError(
            f"Not enough history rows after feature engineering: {len(history_df)}"
        )

    for col in gru_features + xgb_features + ["Sales"]:
        if col in history_df.columns:
            history_df[col] = pd.to_numeric(history_df[col], errors="coerce")

    last_window_features = feature_scaler.transform(history_df[gru_features].tail(time_steps))
    current_window = last_window_features.copy()
    current_history = history_df.copy()

    future_dates = pd.date_range(start=start_dt, end=end_dt, freq="D")
    future_preds = []

    for current_date in future_dates:
        # 1) GRU 预测
        pred_scaled = model.predict(
            current_window.reshape(1, time_steps, -1),
            verbose=0
        )
        pred_real = float(target_scaler.inverse_transform(pred_scaled)[0][0])

        # 2) XGB 残差修正
        row = {}
        row["weekday"] = int(current_date.weekday())
        row["month"] = int(current_date.month)
        row["is_weekend"] = 1 if current_date.weekday() in [5, 6] else 0

        row["lag_1"] = float(current_history["Sales"].iloc[-1])
        row["lag_7"] = float(current_history["Sales"].iloc[-7])
        row["lag_14"] = float(current_history["Sales"].iloc[-14])
        row["rolling_mean_7"] = float(current_history["Sales"].tail(7).astype(float).mean())

        xgb_input = pd.DataFrame([row])[xgb_features].astype(float).values
        xgb_input_scaled = scaler_xgb.transform(xgb_input)
        residual_correction = float(gbm_model.predict(xgb_input_scaled)[0])

        # 非负裁剪
        final_pred = max(float(pred_real + residual_correction), 0.0)
        future_preds.append(final_pred)

        # 3) 更新递推历史
        new_row = current_history.iloc[-1].copy()
        new_row["Date"] = current_date
        new_row["Sales"] = float(final_pred)
        new_row["weekday"] = int(current_date.weekday())
        new_row["month"] = int(current_date.month)
        new_row["is_weekend"] = 1 if current_date.weekday() in [5, 6] else 0
        new_row["lag_1"] = float(current_history["Sales"].iloc[-1])
        new_row["lag_7"] = float(current_history["Sales"].iloc[-7])
        new_row["lag_14"] = float(current_history["Sales"].iloc[-14])
        new_row["rolling_mean_7"] = float(current_history["Sales"].tail(7).astype(float).mean())

        new_row["Price"] = float(current_history["Price"].iloc[-1])
        new_row["Wholesale Price (RMB/kg)"] = float(current_history["Wholesale Price (RMB/kg)"].iloc[-1])
        new_row["Loss Rate (%)"] = float(current_history["Loss Rate (%)"].iloc[-1])
        new_row["Discount"] = float(current_history["Discount"].iloc[-1])

        current_history = pd.concat(
            [current_history, pd.DataFrame([new_row])],
            ignore_index=True
        )

        for col in gru_features:
            current_history[col] = pd.to_numeric(current_history[col], errors="coerce")

        next_window_features = feature_scaler.transform(
            current_history[gru_features].tail(time_steps)
        )
        current_window = next_window_features.copy()

    future_real = np.array(future_preds, dtype=float)

    # 读取真实值（仅用于回测评估，不参与预测）
    actual_df = load_actuals_from_db(stock_code, start_date, end_date)

    result_df = pd.DataFrame({
        "Date": future_dates,
        "PredictedSalesKilo": future_real
    })

    evaluation = None

    if not actual_df.empty:
        actual_df["sales_date"] = pd.to_datetime(actual_df["sales_date"], errors="coerce")
        actual_df["quantity_sold"] = pd.to_numeric(actual_df["quantity_sold"], errors="coerce")

        actual_daily = actual_df.groupby("sales_date").agg({
            "quantity_sold": "sum"
        }).reset_index()

        actual_daily = actual_daily.rename(columns={
            "sales_date": "Date",
            "quantity_sold": "ActualSalesKilo"
        })

        result_df = result_df.merge(actual_daily, on="Date", how="left")

        # 只对有真实值的日期做评估
        valid_eval_df = result_df.dropna(subset=["ActualSalesKilo"]).copy()

        if not valid_eval_df.empty:
            y_true = valid_eval_df["ActualSalesKilo"].astype(float).values
            y_pred = valid_eval_df["PredictedSalesKilo"].astype(float).values

            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            smape = smape_func(y_true, y_pred)

            evaluation = {
                "MAE": float(mae),
                "RMSE": float(rmse),
                "sMAPE": float(smape),
                "valid_actual_days": int(len(valid_eval_df))
            }

    return history_df, result_df, evaluation


# =========================
# 5. Visualization
# =========================
def plot_result(history_df: pd.DataFrame, result_df: pd.DataFrame, evaluation, stock_code: str):
    plt.figure(figsize=(16, 8))

    metrics_str = "Future Forecast (No Actual Available)"
    if evaluation is not None:
        metrics_str = (
            f"MAE: {evaluation['MAE']:.2f}  |  "
            f"RMSE: {evaluation['RMSE']:.2f}  |  "
            f"sMAPE: {evaluation['sMAPE']:.2f}%  |  "
            f"Valid Days: {evaluation['valid_actual_days']}"
        )

    plt.suptitle(
        metrics_str,
        fontsize=14,
        y=0.95,
        color="darkblue",
        fontweight="bold"
    )

    # 历史一年真实值：橙色
    plt.plot(
        history_df["Date"],
        history_df["Sales"],
        label="Historical Actual Sales",
        color="orange",
        linewidth=2
    )

    # 预测区间：只有绿色
    plt.plot(
        result_df["Date"],
        result_df["PredictedSalesKilo"],
        label="7-Day Future",
        color="green",
        marker="o"
    )

    plt.title(
        f"Strong Peak Detection: Hybrid GRU-XGBoost {stock_code} Sales Forecast",
        fontsize=12,
        pad=20
    )

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


# =========================
# 6. Main
# =========================
def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("python scripts/predict_naibaicai_stable_short_term.py <stock_code> <start_date> <end_date>")
        print("Example:")
        print("python scripts/predict_naibaicai_stable_short_term.py 102900011008164 2023-01-01 2023-01-07")
        return

    stock_code = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    history_df, result_df, evaluation = predict_range(stock_code, start_date, end_date)

    print("\n=== Prediction Result ===")
    if evaluation is not None:
        print(
            f"MAE: {evaluation['MAE']:.2f} | "
            f"RMSE: {evaluation['RMSE']:.2f} | "
            f"sMAPE: {evaluation['sMAPE']:.2f}% | "
            f"Valid Actual Days: {evaluation['valid_actual_days']}"
        )
    else:
        print("No actual values available for evaluation in the selected forecast range.")

    print(f"\n--- {start_date} To {end_date} Forecast ---")
    for _, row in result_df.iterrows():
        actual_value = row.get("ActualSalesKilo", np.nan)
        if not pd.isna(actual_value):
            print(
                f"{row['Date'].date()}: "
                f"Pred={row['PredictedSalesKilo']:.2f} Kilo | "
                f"Actual={actual_value:.2f} Kilo"
            )
        else:
            print(
                f"{row['Date'].date()}: "
                f"Pred={row['PredictedSalesKilo']:.2f} Kilo"
            )

    output_path = os.path.join(
        MODEL_DIR,
        f"forecast_{stock_code}_{start_date}_{end_date}.csv".replace(":", "-")
    )
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nForecast CSV saved to: {output_path}")

    plot_result(history_df, result_df, evaluation, stock_code)


if __name__ == "__main__":
    main()