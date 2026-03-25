from services.db_service import get_connection

def get_products():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT product_id, stock_code, product_name, category_name, unit, country
                FROM products
                ORDER BY product_name ASC
                LIMIT 200
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()