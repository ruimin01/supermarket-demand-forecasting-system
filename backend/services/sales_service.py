from services.db_service import get_connection

def get_sales_history(stock_code=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if stock_code:
                sql = """
                    SELECT s.sales_date AS date, s.quantity_sold AS sales
                    FROM sales_records s
                    JOIN products p ON s.product_id = p.product_id
                    WHERE p.stock_code = %s
                    ORDER BY s.sales_date ASC
                    LIMIT 100
                """
                cursor.execute(sql, (stock_code,))
            else:
                sql = """
                    SELECT s.sales_date AS date, s.quantity_sold AS sales
                    FROM sales_records s
                    ORDER BY s.sales_date ASC
                    LIMIT 100
                """
                cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()