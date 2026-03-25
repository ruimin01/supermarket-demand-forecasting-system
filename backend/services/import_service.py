import pandas as pd
from services.db_service import get_connection

def normalize_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    value_str = str(value).strip().lower()
    return value_str in ["1", "true", "yes", "y"]

def get_or_create_product(
    cursor,
    stock_code,
    product_name,
    category_name,
    dataset_type,
    unit,
    country,
    prediction_category=None
):
    # 先按 stock_code 查
    select_sql = """
        SELECT product_id
        FROM products
        WHERE stock_code = %s
        LIMIT 1
    """
    cursor.execute(select_sql, (stock_code,))
    existing = cursor.fetchone()

    if existing:
        return existing["product_id"]

    insert_sql = """
        INSERT INTO products (
            dataset_type,
            stock_code,
            product_name,
            category_name,
            unit,
            country,
            prediction_category
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (
        dataset_type,
        stock_code,
        product_name,
        category_name,
        unit,
        country,
        prediction_category
    ))
    return cursor.lastrowid

def import_necessity_csv(df, file_id, prediction_category=None, max_rows=None):
    if max_rows:
        df = df.head(max_rows).copy()

    conn = get_connection()
    inserted_products = 0
    inserted_sales = 0

    try:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                stock_code = str(row["StockCode"]).strip()
                product_name = str(row["Description"]).strip()
                country = str(row["Country"]).strip()
                sales_date = pd.to_datetime(row["Date"]).date()

                # 先查是否已有 product
                cursor.execute("SELECT product_id FROM products WHERE stock_code = %s LIMIT 1", (stock_code,))
                existing = cursor.fetchone()

                if existing:
                    product_id = existing["product_id"]
                else:
                    product_id = get_or_create_product(
                        cursor=cursor,
                        stock_code=stock_code,
                        product_name=product_name,
                        category_name=None,
                        dataset_type="necessity",
                        unit="piece",
                        country=country,
                        prediction_category=prediction_category
                    )
                    inserted_products += 1

                insert_sales_sql = """
                    INSERT INTO sales_records (
                        product_id,
                        file_id,
                        sales_date,
                        year,
                        month,
                        day,
                        day_of_week,
                        is_weekend,
                        quantity_sold,
                        quantity_unit,
                        avg_unit_price
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sales_sql, (
                    product_id,
                    file_id,
                    sales_date,
                    int(row["Year"]),
                    int(row["Month"]),
                    int(pd.to_datetime(row["Date"]).day),
                    int(row["DayOfWeek"]),
                    normalize_bool(row["IsWeekend"]),
                    float(row["QuantitySold"]),
                    "piece",
                    float(row["AvgUnitPrice"]) if not pd.isna(row["AvgUnitPrice"]) else None
                ))
                inserted_sales += 1

        return {
            "inserted_products": inserted_products,
            "inserted_sales_records": inserted_sales
        }
    finally:
        conn.close()

def import_vegetable_csv(df, file_id, prediction_category=None, max_rows=None):
    if max_rows:
        df = df.head(max_rows).copy()

    conn = get_connection()
    inserted_products = 0
    inserted_sales = 0

    try:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                stock_code = str(row["StockCode"]).strip()
                product_name = str(row["ItemName"]).strip()
                category_name = str(row["CategoryName"]).strip()
                sales_date = pd.to_datetime(row["Date"]).date()

                cursor.execute("SELECT product_id FROM products WHERE stock_code = %s LIMIT 1", (stock_code,))
                existing = cursor.fetchone()

                if existing:
                    product_id = existing["product_id"]
                else:
                    product_id = get_or_create_product(
                        cursor=cursor,
                        stock_code=stock_code,
                        product_name=product_name,
                        category_name=category_name,
                        dataset_type="vegetable",
                        unit="kg",
                        country="China",
                        prediction_category=prediction_category
                    )
                    inserted_products += 1

                insert_sales_sql = """
                    INSERT INTO sales_records (
                        product_id,
                        file_id,
                        sales_date,
                        year,
                        month,
                        day,
                        day_of_week,
                        is_weekend,
                        quantity_sold,
                        quantity_unit,
                        unit_selling_price,
                        wholesale_price,
                        loss_rate_pct
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sales_sql, (
                    product_id,
                    file_id,
                    sales_date,
                    int(row["Year"]),
                    int(row["Month"]),
                    int(row["Day"]),
                    int(row["DayOfWeek"]),
                    normalize_bool(row["IsWeekend"]),
                    float(row["QuantitySoldKilo"]),
                    "kg",
                    float(row["UnitSellingPrice"]) if not pd.isna(row["UnitSellingPrice"]) else None,
                    float(row["WholesalePrice"]) if not pd.isna(row["WholesalePrice"]) else None,
                    float(row["LossRatePct"]) if not pd.isna(row["LossRatePct"]) else None
                ))
                inserted_sales += 1

        return {
            "inserted_products": inserted_products,
            "inserted_sales_records": inserted_sales
        }
    finally:
        conn.close()