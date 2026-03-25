import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.db_service import get_connection

CSV_PATH = os.path.join(BASE_DIR, "data", "vegetable_cleaned.csv")

TARGET_PRODUCTS = {
    "102900011008164": {
        "product_name": "Naibaicai",
        "prediction_category": "stable_short_term",
    },
    "102900005115199": {
        "product_name": "Sichuan Red Cedar",
        "prediction_category": "high_volatility_short_term",
    },
    "102900005116509": {
        "product_name": "Green Eggplant (1)",
        "prediction_category": "stable_long_term",
    },
    "102900005122654": {
        "product_name": "Zhijiang Red Bolt",
        "prediction_category": "high_volatility_long_term",
    },
}

def normalize_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ["1", "true", "yes", "y"]

def load_and_filter_csv():
    print("Reading file:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    df["ItemName"] = df["ItemName"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["CategoryName"] = df["CategoryName"].astype(str).str.strip()

    target_stock_codes = list(TARGET_PRODUCTS.keys())
    filtered = df[df["StockCode"].isin(target_stock_codes)].copy()

    print("=== Filtered Product Summary ===")
    print(filtered[["StockCode", "ItemName", "CategoryName"]].drop_duplicates().to_string(index=False))
    print()

    print("=== Row Count By StockCode ===")
    print(filtered.groupby(["StockCode", "ItemName"]).size().reset_index(name="RowCount").to_string(index=False))
    print()

    print(f"Filtered total rows: {len(filtered)}")

    return filtered

def clear_old_data_for_targets(conn, target_stock_codes):
    with conn.cursor() as cursor:
        delete_sales_sql = """
            DELETE s
            FROM sales_records s
            JOIN products p ON s.product_id = p.product_id
            WHERE p.stock_code IN %s
        """
        cursor.execute(delete_sales_sql, (tuple(target_stock_codes),))

        delete_products_sql = """
            DELETE FROM products
            WHERE stock_code IN %s
        """
        cursor.execute(delete_products_sql, (tuple(target_stock_codes),))

def get_or_create_product(cursor, stock_code, product_name_from_csv, category_name):
    select_sql = """
        SELECT product_id
        FROM products
        WHERE stock_code = %s
        LIMIT 1
    """
    cursor.execute(select_sql, (stock_code,))
    existing = cursor.fetchone()

    if existing:
        return existing["product_id"], False

    product_name = TARGET_PRODUCTS[stock_code]["product_name"]
    prediction_category = TARGET_PRODUCTS[stock_code]["prediction_category"]

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
        "vegetable",
        stock_code,
        product_name,
        category_name,
        "kg",
        "China",
        prediction_category
    ))
    return cursor.lastrowid, True

def insert_products(conn, df):
    inserted_products = 0
    stockcode_to_productid = {}

    unique_products = df[["StockCode", "ItemName", "CategoryName"]].drop_duplicates()

    with conn.cursor() as cursor:
        for _, row in unique_products.iterrows():
            stock_code = str(row["StockCode"]).strip()
            item_name = str(row["ItemName"]).strip()
            category_name = str(row["CategoryName"]).strip()

            product_id, created = get_or_create_product(
                cursor,
                stock_code,
                item_name,
                category_name
            )

            stockcode_to_productid[stock_code] = product_id
            if created:
                inserted_products += 1

    return inserted_products, stockcode_to_productid

def insert_sales_records(conn, df, stockcode_to_productid):
    inserted_sales = 0

    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            stock_code = str(row["StockCode"]).strip()
            product_id = stockcode_to_productid[stock_code]
            sales_date = pd.to_datetime(row["Date"]).date()

            insert_sql = """
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
            cursor.execute(insert_sql, (
                product_id,
                None,
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

    return inserted_sales

def main():
    df = load_and_filter_csv()

    if df.empty:
        print("No target products found. Please check StockCode values.")
        return

    target_stock_codes = df["StockCode"].drop_duplicates().tolist()

    conn = get_connection()

    try:
        print("\n=== Step 1: Clear old imported data for these stock codes ===")
        clear_old_data_for_targets(conn, target_stock_codes)

        print("=== Step 2: Insert products ===")
        inserted_products, stockcode_to_productid = insert_products(conn, df)
        print(f"Inserted products: {inserted_products}")

        print("=== Step 3: Insert sales records ===")
        inserted_sales = insert_sales_records(conn, df, stockcode_to_productid)
        print(f"Inserted sales records: {inserted_sales}")

        conn.commit()
        print("\nImport completed successfully.")

        print("\n=== Imported StockCode Summary ===")
        summary = df.groupby("StockCode").size().reset_index(name="ImportedRows")
        print(summary.to_string(index=False))

    except Exception as e:
        conn.rollback()
        print("\nImport failed. Rolled back transaction.")
        print("Error:", str(e))

    finally:
        conn.close()

if __name__ == "__main__":
    main()