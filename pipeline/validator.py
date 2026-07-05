import pandas as pd
from pipeline.config import DATA_DIR

def validate_market_data(smp_df, eirgrid_df, entsoe_df):
    """Sanity checks SEMO prices against ENTSO-E and validates wind correlation."""
    print("Running data validation checks...")
    results = []
    
    s_h = smp_df.set_index('Datetime').resample('1h').mean()
    e_h = eirgrid_df.set_index('Datetime').resample('1h').mean()
    ent_h = entsoe_df.set_index('Datetime')
    
    merged = pd.concat([s_h, e_h, ent_h], axis=1).dropna()
    
    if len(merged) > 0:
        smp_mean = merged['SMP'].mean()
        da_mean = merged['DA_Price'].mean()
        diff_pct = abs(smp_mean - da_mean) / da_mean if da_mean != 0 else 0
        results.append({
            'Check': 'SMP vs ENTSO-E DA Price',
            'Value1': smp_mean,
            'Value2': da_mean,
            'Variance': diff_pct,
            'Status': 'PASS' if diff_pct < 0.15 else 'FAIL'
        })
        
        corr = merged['WindGeneration'].corr(merged['SMP'])
        results.append({
            'Check': 'Wind vs SMP Correlation',
            'Value1': corr,
            'Value2': 0, 
            'Variance': 0,
            'Status': 'PASS' if corr < 0 else 'FAIL'
        })
        
    df_results = pd.DataFrame(results)
    df_results.to_csv(DATA_DIR / "validation_report.csv", index=False)
    print("Validation report saved.")
    return df_results
