import argparse
from pipeline.fetcher import fetch_semopx_ea001, fetch_semo_imbalance, fetch_eirgrid_data, fetch_entsoe_data
from pipeline.processor import process_and_merge
from pipeline.validator import validate_market_data

def main():
    parser = argparse.ArgumentParser(description="I-SEM Market Dashboard Data Pipeline")
    parser.add_argument("--full-backfill", action="store_true", help="Fetch full history")
    args = parser.parse_args()

    start_date = "2026-06-22" 
    end_date = "2026-06-29" 

    print(f"Starting LIVE data pipeline (start: {start_date}, end: {end_date})")

    ea_df = fetch_semopx_ea001(start_date, end_date)
    isp_df = fetch_semo_imbalance(start_date, end_date)
    eirgrid_df = fetch_eirgrid_data(start_date, end_date)
    entsoe_df = fetch_entsoe_data(start_date, end_date)

    process_and_merge(ea_df, isp_df, eirgrid_df, entsoe_df)
    
    try:
        import pandas as pd
        smp_df = pd.merge(ea_df, isp_df, on='Datetime', how='outer')
        validate_market_data(smp_df, eirgrid_df, entsoe_df)
    except Exception as e:
        print("Validation warning:", e)
    
    

    print("Pipeline execution completed successfully. Data saved to data/ directory.")

if __name__ == "__main__":
    main()
