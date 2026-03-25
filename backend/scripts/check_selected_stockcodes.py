import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def main():
    df = pd.read_csv(CSV_PATH)
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["ItemName"] = df["ItemName"].astype(str).str.strip()

    target_stock_codes = list(TARGET_PRODUCTS.keys())
    filtered = df[df["StockCode"].isin(target_stock_codes)].copy()

    print("=== Selected Product Summary ===")
    summary = filtered[["StockCode", "ItemName", "CategoryName"]].drop_duplicates()
    print(summary.to_string(index=False))

    print("\n=== Row Count by StockCode ===")
    count_summary = filtered.groupby(["StockCode", "ItemName"]).size().reset_index(name="row_count")
    print(count_summary.to_string(index=False))

    print("\n=== Missing Stock Codes Check ===")
    existing_codes = set(filtered["StockCode"].unique())
    for code in target_stock_codes:
        if code not in existing_codes:
            print(f"Missing: {code}")
        else:
            print(f"Found: {code}")

if __name__ == "__main__":
    main()