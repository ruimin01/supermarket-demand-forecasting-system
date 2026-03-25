import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.db_service import get_connection

TARGET_STOCK_CODE = "102900005116509"
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "green_eggplant_1_daily.csv")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = get_connection()

    try:
        sql = """
            SELECT
                s.sales_date AS Date,
                p.stock_code AS StockCode,
                s.quantity_sold AS QuantitySoldKilo,
                s.unit_selling_price AS UnitSellingPrice,
                s.wholesale_price AS WholesalePrice,
                s.loss_rate_pct AS LossRatePct,
                p.product_name AS ItemName,
                p.category_name AS CategoryName,
                s.year AS Year,
                s.month AS Month,
                s.day AS Day,
                s.day_of_week AS DayOfWeek,
                s.is_weekend AS IsWeekend
            FROM sales_records s
            JOIN products p ON s.product_id = p.product_id
            WHERE p.stock_code = %s
            ORDER BY s.sales_date ASC
        """

        df = pd.read_sql(sql, conn, params=[TARGET_STOCK_CODE])

        if df.empty:
            print("No data found for stock code:", TARGET_STOCK_CODE)
            return

        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

        print("Export completed.")
        print("Output file:", OUTPUT_FILE)
        print("Rows:", len(df))
        print("Columns:", list(df.columns))

    finally:
        conn.close()

if __name__ == "__main__":
    main()