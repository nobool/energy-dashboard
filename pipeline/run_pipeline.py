import argparse
import os
from datetime import datetime, timedelta
from pipeline.fetcher import fetch_semopx_ea001, fetch_semo_imbalance, fetch_eirgrid_data, fetch_nordpool_gb_da
from pipeline.processor import process_and_merge


def main():
    parser = argparse.ArgumentParser(description="I-SEM Market Dashboard Data Pipeline")
    parser.add_argument("--full-backfill", action="store_true", help="Fetch full history")
    args = parser.parse_args()

    # Default to 7 days trailing window if environment variables are not set
    default_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    default_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    start_date = os.environ.get("DATE_FROM", default_start)
    end_date = os.environ.get("DATE_TO", default_end)

    print(f"Starting LIVE data pipeline (start: {start_date}, end: {end_date})")

    ea_df = fetch_semopx_ea001(start_date, end_date)
    isp_df = fetch_semo_imbalance(start_date, end_date)
    eirgrid_df = fetch_eirgrid_data(start_date, end_date)
    gb_df = fetch_nordpool_gb_da(start_date, end_date)

    process_and_merge(ea_df, isp_df, eirgrid_df, gb_df)
    
    print("Pipeline execution completed successfully. Data saved to data/ directory.")

if __name__ == "__main__":
    main()
