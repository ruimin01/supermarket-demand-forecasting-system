import numpy as np
import pandas as pd

from scripts.predict_naibaicai_stable_short_term import predict_range


def convert_nan_to_none(value):
    if pd.isna(value):
        return None
    if isinstance(value, (np.floating, np.integer)):
        return float(value)
    return value


def run_prediction_service(prediction_category: str, stock_code: str, start_date: str, end_date: str):
    
    if prediction_category == "stable_short_term" and stock_code == "102900011008164":
        history_df, result_df, evaluation = predict_range(stock_code, start_date, end_date)
    else:
        raise ValueError("Current backend only supports Naibaicai stable_short_term for now.")

    history_list = []
    for _, row in history_df.iterrows():
        history_list.append({
            "date": str(pd.to_datetime(row["Date"]).date()),
            "sales": round(float(row["Sales"]), 2)
        })

    forecast_list = []
    for _, row in result_df.iterrows():
        forecast_list.append({
            "date": str(pd.to_datetime(row["Date"]).date()),
            "predictedSalesKilo": round(float(row["PredictedSalesKilo"]), 2)
        })

    total_predicted = round(float(result_df["PredictedSalesKilo"].sum()), 2)

    return {
        "summary": {
            "stockCode": stock_code,
            "predictionCategory": prediction_category,
            "startDate": start_date,
            "endDate": end_date,
            "totalPredictedSalesKilo": total_predicted,
            "evaluation": evaluation
        },
        "history": history_list,
        "list": forecast_list
    }
# import numpy as np
# import pandas as pd

# from scripts.predict_naibaicai_stable_short_term import predict_range


# def convert_nan_to_none(value):
#     if pd.isna(value):
#         return None
#     if isinstance(value, (np.floating, np.integer)):
#         return float(value)
#     return value


# def run_prediction_service(prediction_category: str, stock_code: str, start_date: str, end_date: str):
#     # 目前先只支持 Naibaicai 的 stable_short_term
#     if prediction_category == "stable_short_term" and stock_code == "102900011008164":
#         history_df, result_df, evaluation = predict_range(stock_code, start_date, end_date)
#     else:
#         raise ValueError("Current backend only supports Naibaicai stable_short_term for now.")

#     result_list = []
#     for _, row in result_df.iterrows():
#         actual_value = row.get("ActualSalesKilo", np.nan)

#         result_list.append({
#             "date": str(pd.to_datetime(row["Date"]).date()),
#             "predictedSalesKilo": round(float(row["PredictedSalesKilo"]), 2),
#             "actualSalesKilo": None if pd.isna(actual_value) else round(float(actual_value), 2)
#         })

#     total_predicted = round(float(result_df["PredictedSalesKilo"].sum()), 2)

#     return {
#         "summary": {
#             "stockCode": stock_code,
#             "predictionCategory": prediction_category,
#             "startDate": start_date,
#             "endDate": end_date,
#             "totalPredictedSalesKilo": total_predicted,
#             "evaluation": evaluation
#         },
#         "list": result_list
#     }