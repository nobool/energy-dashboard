import pandas as pd
from pipeline.config import DATA_DIR, CCGT_HEAT_RATE, CCGT_CARBON_INTENSITY, VOM_COST, DEFAULT_GAS_PRICE, DEFAULT_CARBON_PRICE

def process_and_merge(ea_df, isp_df, eirgrid_df, gb_df):
    """Cleans and merges live data into standard DataFrames for the dashboard."""
    print("Processing and merging live data...")
    
    # Combine Ex-Ante (DAM, IDA1, IDA2, IDA3) and Imbalance (ISP, NIV)
    smp_raw = pd.merge(ea_df, isp_df, on='Datetime', how='outer').sort_values('Datetime')
    
    # Forward fill missing values caused by different publication frequencies
    # Keep 30 min granularity
    s_half_hourly = smp_raw.set_index('Datetime').resample('30min').mean().reset_index()
    for col in ['DAM_Price', 'ISP', 'NIV']:
        if col in s_half_hourly.columns:
            s_half_hourly[col] = s_half_hourly[col].ffill().bfill()
            
    for col in ['IDA1_Price', 'IDA2_Price', 'IDA3_Price']:
        if col in s_half_hourly.columns:
            s_half_hourly[col] = s_half_hourly[col].ffill().bfill()
            
    # Compute Spreads
    for col in ['DAM', 'IDA1', 'IDA2', 'IDA3']:
        if f'{col}_Price' in s_half_hourly.columns:
            s_half_hourly[f'{col}_Spread_to_ISP'] = s_half_hourly[f'{col}_Price'] - s_half_hourly['ISP']
        
    # Eirgrid is saved natively in 15 mins
    eirgrid_grid = eirgrid_df.copy()
    eirgrid_grid.to_csv(DATA_DIR / "eirgrid_grid.csv", index=False)
    
    e_half_hourly = eirgrid_df.set_index('Datetime').resample('30min').mean().reset_index()
    # EirGrid InterconnectorFlow: Imports are often positive. 
    if 'InterconnectorFlow' in e_half_hourly.columns:
        imports = e_half_hourly['InterconnectorFlow'].clip(lower=0)
        exports = e_half_hourly['InterconnectorFlow'].clip(upper=0).abs()
        e_half_hourly['SNSP_Pct'] = ((e_half_hourly['WindGeneration'] + imports) / (e_half_hourly['SystemDemand'] + exports)) * 100
    
    # Process GB DA Data (Forward fill hourly to half hourly)
    if not gb_df.empty:
        gb_half_hourly = gb_df.set_index('Datetime').resample('30min').ffill().reset_index()
        s_half_hourly = pd.merge(s_half_hourly, gb_half_hourly, on='Datetime', how='left')
        s_half_hourly['GB_DA_Price'] = s_half_hourly['GB_DA_Price'].ffill().bfill()
    
    s_half_hourly.to_csv(DATA_DIR / "smp_prices.csv", index=False)
    
    spark = pd.merge(s_half_hourly, e_half_hourly, on='Datetime', how='inner')
    
    spark['SRMC'] = (DEFAULT_GAS_PRICE * CCGT_HEAT_RATE) + (DEFAULT_CARBON_PRICE * CCGT_CARBON_INTENSITY) + VOM_COST
    if 'DAM_Price' in spark.columns:
        spark['SparkSpread'] = spark['DAM_Price'] - spark['SRMC']
    spark.to_csv(DATA_DIR / "spark_spread.csv", index=False)
    
    return s_half_hourly, eirgrid_grid, spark
