from services.db_service import get_connection
from services.model_service import predict_by_hybrid_model


def run_prediction_service(current_user, prediction_category, start_date, end_date, stock_code):
    result = predict_by_hybrid_model(
        prediction_category=prediction_category,
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date
    )

    # 这里先不强制保存到数据库
    # 你后面接模型后可以再把结果逐条写入 forecast_results
    #
    # 如果要保存，建议根据 stock_code 找 product_id，再写 created_by = current_user["user_id"]

    return result
def get_forecast_records(current_user):
    from services.db_service import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            can_view_all = current_user["permissions"]["can_view_all_records"]

            if can_view_all:
                sql = """
                    SELECT 
                        p.product_name AS product,
                        COALESCE(f.prediction_category, p.category_name, p.country, 'Unknown') AS type,
                        CONCAT(f.start_date, ' to ', f.end_date) AS range_text,
                        CONCAT(f.predicted_demand, ' ', f.prediction_unit) AS demand,
                        f.model_name AS model,
                        f.status AS status
                    FROM forecast_results f
                    JOIN products p ON f.product_id = p.product_id
                    ORDER BY f.created_at DESC
                    LIMIT 100
                """
                cursor.execute(sql)
            else:
                sql = """
                    SELECT 
                        p.product_name AS product,
                        COALESCE(f.prediction_category, p.category_name, p.country, 'Unknown') AS type,
                        CONCAT(f.start_date, ' to ', f.end_date) AS range_text,
                        CONCAT(f.predicted_demand, ' ', f.prediction_unit) AS demand,
                        f.model_name AS model,
                        f.status AS status
                    FROM forecast_results f
                    JOIN products p ON f.product_id = p.product_id
                    WHERE f.created_by = %s
                    ORDER BY f.created_at DESC
                    LIMIT 100
                """
                cursor.execute(sql, (current_user["user_id"],))

            return cursor.fetchall()
    finally:
        conn.close()
# def get_forecast_records(current_user):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             can_view_all = current_user["permissions"]["can_view_all_records"]

#             if can_view_all:
#                 sql = """
#                     SELECT 
#                         p.product_name AS product,
#                         COALESCE(p.category_name, p.country, 'Unknown') AS type,
#                         CONCAT(f.forecast_date, ' to ', f.forecast_date) AS range_text,
#                         CONCAT(f.predicted_demand, ' ', f.prediction_unit) AS demand,
#                         f.model_name AS model,
#                         'completed' AS status
#                     FROM forecast_results f
#                     JOIN products p ON f.product_id = p.product_id
#                     ORDER BY f.forecast_date DESC
#                     LIMIT 100
#                 """
#                 cursor.execute(sql)
#             else:
#                 sql = """
#                     SELECT 
#                         p.product_name AS product,
#                         COALESCE(p.category_name, p.country, 'Unknown') AS type,
#                         CONCAT(f.forecast_date, ' to ', f.forecast_date) AS range_text,
#                         CONCAT(f.predicted_demand, ' ', f.prediction_unit) AS demand,
#                         f.model_name AS model,
#                         'completed' AS status
#                     FROM forecast_results f
#                     JOIN products p ON f.product_id = p.product_id
#                     WHERE f.created_by = %s
#                     ORDER BY f.forecast_date DESC
#                     LIMIT 100
#                 """
#                 cursor.execute(sql, (current_user["user_id"],))

#             return cursor.fetchall()
#     finally:
#         conn.close()