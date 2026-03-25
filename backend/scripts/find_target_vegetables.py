import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "vegetable_cleaned.csv")

TARGET_KEYWORDS = [
    "Naibaicai",
    "Lotus (Ea)",
    "Green Eggplant",
    "Zhijiang Red Bolt",
]

def main():
    print("Reading file:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    print("=== Unique ItemName Count ===")
    print(df["ItemName"].nunique())
    print()

    print("=== Exact Match Check ===")
    for keyword in TARGET_KEYWORDS:
        matched = df[df["ItemName"].astype(str).str.strip() == keyword]
        print(f"\nTarget: {keyword}")
        print(f"Matched rows: {len(matched)}")

        if len(matched) > 0:
            summary = matched[["ItemName", "StockCode", "CategoryName"]].drop_duplicates()
            print(summary.to_string(index=False))
        else:
            print("No exact match found.")

    print("\n=== Fuzzy Contains Check ===")
    for keyword in TARGET_KEYWORDS:
        matched = df[df["ItemName"].astype(str).str.contains(keyword, case=False, na=False, regex=False)]
        print(f"\nKeyword contains: {keyword}")
        print(f"Matched rows: {len(matched)}")

        if len(matched) > 0:
            summary = matched[["ItemName", "StockCode", "CategoryName"]].drop_duplicates()
            print(summary.to_string(index=False))
        else:
            print("No fuzzy match found.")

if __name__ == "__main__":
    main()