import pandas as pd
from pipeline.config import DATA_DIR, CCGT_HEAT_RATE, CCGT_EMISSION_FACTOR, VOM_COST, DEFAULT_GAS_PRICE, DEFAULT_CARBON_PRICE

def process_and_merge(ea_df, isp_df, eirgrid_df, entsoe_df):
    """Cleans and merges live data into standard DataFrames for the dashboard."""
    print("Processing and merging live data...")
    
    # Combine Ex-Ante (SMP) and Imbalance (ISP)
    smp_raw = pd.merge(ea_df, isp_df, on='Datetime', how='outer').sort_values('Datetime')
    
    # Forward fill missing values caused by different publication frequencies
    smp_raw['SMP'] = smp_raw['SMP'].ffill().bfill()
    smp_raw['ISP'] = smp_raw['ISP'].ffill().bfill()
    if 'IDA1_Price' in smp_raw.columns:
        smp_raw['IDA1_Price'] = smp_raw['IDA1_Price'].ffill().bfill()
    
    s_hourly = smp_raw.set_index('Datetime').resample('1h').mean().reset_index()
    if 'IDA1_Price' in s_hourly.columns:
        s_hourly['IDA1_Spread'] = s_hourly['IDA1_Price'] - s_hourly['SMP']
        
    e_hourly = eirgrid_df.set_index('Datetime').resample('1h').mean().reset_index()
    # EirGrid InterconnectorFlow: Imports are often positive. 
    imports = e_hourly['InterconnectorFlow'].clip(lower=0)
    exports = e_hourly['InterconnectorFlow'].clip(upper=0).abs()
    e_hourly['SNSP_Pct'] = ((e_hourly['WindGeneration'] + imports) / (e_hourly['SystemDemand'] + exports)) * 100
    
    smp_prices = s_hourly.copy()
    smp_prices.to_csv(DATA_DIR / "smp_prices.csv", index=False)
    
    eirgrid_grid = e_hourly.copy()
    eirgrid_grid.to_csv(DATA_DIR / "eirgrid_grid.csv", index=False)
    
    spark = pd.merge(s_hourly, e_hourly, on='Datetime', how='inner')
    
    spark['SRMC'] = (DEFAULT_GAS_PRICE * CCGT_HEAT_RATE) + (DEFAULT_CARBON_PRICE * CCGT_EMISSION_FACTOR) + VOM_COST
    spark['SparkSpread'] = spark['SMP'] - spark['SRMC']
    spark.to_csv(DATA_DIR / "spark_spread.csv", index=False)
    
    return smp_prices, eirgrid_grid, spark
