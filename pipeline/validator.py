import pandas as pd
from pipeline.config import DATA_DIR

def validate_market_data(smp_df, eirgrid_df, entsoe_df):
    """Sanity checks SEMO prices against ENTSO-E and validates market logic."""
    print("Running data validation checks...")
    results = []
    
    # Resample to common hourly frequency
    s_h = smp_df.set_index('Datetime').resample('1h').mean()
    e_h = eirgrid_df.set_index('Datetime').resample('1h').mean()
    ent_h = entsoe_df.set_index('Datetime').resample('1h').mean()
    
    merged = pd.concat([s_h, e_h, ent_h], axis=1)
    # Only drop rows missing the specific columns we use for validation
    required_cols = ['DAM_Price', 'DA_Price', 'SystemDemand', 'ActualLoad', 'WindGeneration']
    # But only require columns that actually exist in the merged dataframe to avoid KeyError if an API failed completely
    available_cols = [c for c in required_cols if c in merged.columns]
    merged = merged.dropna(subset=available_cols)
    
    if len(merged) == 0:
        raise ValueError("Merged validation dataset is empty! Time indices likely do not align across SEMOpx, EirGrid, and ENTSO-E sources. Cannot proceed with cross-validation.")
        
    # Layer 1: Source Cross-Validation
    # 1. SEMOpx DAM Price vs ENTSO-E DA Price
    dam_mean = merged['DAM_Price'].mean()
    da_mean = merged['DA_Price'].mean()
    diff_pct_dam = abs(dam_mean - da_mean) / da_mean if da_mean != 0 else 0
    results.append({
        'Check': 'Source CV: SEMOpx DAM Price vs ENTSO-E DA',
        'Value1': round(dam_mean, 2),
        'Value2': round(da_mean, 2),
        'Variance': f"{diff_pct_dam*100:.1f}%",
        'Status': 'PASS' if diff_pct_dam < 0.15 else 'FAIL'
    })
    
    # 2. EirGrid Demand vs ENTSO-E Actual Load
    eg_demand = merged['SystemDemand'].mean()
    ent_load = merged['ActualLoad'].mean()
    diff_pct_demand = abs(eg_demand - ent_load) / ent_load if ent_load != 0 else 0
    results.append({
        'Check': 'Source CV: EirGrid Demand vs ENTSO-E Load',
        'Value1': round(eg_demand, 2),
        'Value2': round(ent_load, 2),
        'Variance': f"{diff_pct_demand*100:.1f}%",
        'Status': 'PASS' if diff_pct_demand < 0.15 else 'FAIL'
    })
    
    df_results = pd.DataFrame(results, columns=['Check', 'Value1', 'Value2', 'Variance', 'Status'])
    df_results.to_csv(DATA_DIR / "validation_report.csv", index=False)
    print("Validation report saved.")
    return df_results
