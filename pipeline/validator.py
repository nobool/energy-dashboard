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
    required_cols = ['SMP', 'DA_Price', 'SystemDemand', 'ActualLoad', 'WindGeneration']
    # But only require columns that actually exist in the merged dataframe to avoid KeyError if an API failed completely
    available_cols = [c for c in required_cols if c in merged.columns]
    merged = merged.dropna(subset=available_cols)
    
    if len(merged) == 0:
        raise ValueError("Merged validation dataset is empty! Time indices likely do not align across SEMOpx, EirGrid, and ENTSO-E sources. Cannot proceed with cross-validation.")
        
    # Layer 1: Source Cross-Validation
    # 1. SEMOpx SMP vs ENTSO-E DA Price
    smp_mean = merged['SMP'].mean()
    da_mean = merged['DA_Price'].mean()
    diff_pct_smp = abs(smp_mean - da_mean) / da_mean if da_mean != 0 else 0
    results.append({
        'Check': 'Source CV: SEMOpx SMP vs ENTSO-E DA',
        'Value1': round(smp_mean, 2),
        'Value2': round(da_mean, 2),
        'Variance': f"{diff_pct_smp*100:.1f}%",
        'Status': 'PASS' if diff_pct_smp < 0.15 else 'FAIL'
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
    
    # Layer 2: Market Logic Sanity Checks
    # 1. Wind vs SMP Correlation
    corr = merged['WindGeneration'].corr(merged['SMP'])
    results.append({
        'Check': 'Logic: Wind vs SMP Negative Correlation',
        'Value1': round(corr, 2),
        'Value2': '< 0', 
        'Variance': 'N/A',
        'Status': 'PASS' if corr < 0 else 'FAIL'
    })
    
    # 2. Winter vs Summer SMP
    merged['Month'] = merged.index.month
    winter_smp = merged[merged['Month'].isin([11, 12, 1, 2])]['SMP'].mean()
    summer_smp = merged[merged['Month'].isin([5, 6, 7, 8])]['SMP'].mean()
    if pd.notna(winter_smp) and pd.notna(summer_smp):
        results.append({
            'Check': 'Logic: Winter SMP > Summer SMP',
            'Value1': round(winter_smp, 2),
            'Value2': round(summer_smp, 2),
            'Variance': 'N/A',
            'Status': 'PASS' if winter_smp > summer_smp else 'FAIL'
        })
    
    # 3. Negative SMP occurrences < 0.5%
    neg_smp_count = (merged['SMP'] < 0).sum()
    total_periods = len(merged)
    neg_pct = neg_smp_count / total_periods
    results.append({
        'Check': 'Logic: Negative SMP < 0.5%',
        'Value1': f"{neg_pct*100:.2f}%",
        'Value2': '0.50%',
        'Variance': 'N/A',
        'Status': 'PASS' if neg_pct < 0.005 else 'FAIL'
    })
    
    # 4. Price Spikes cluster
    spike_threshold = merged['SMP'].mean() * 2
    spikes = merged[merged['SMP'] > spike_threshold]
    if len(spikes) > 0:
        avg_spike_wind = spikes['WindGeneration'].mean()
        avg_all_wind = merged['WindGeneration'].mean()
        avg_spike_demand = spikes['SystemDemand'].mean()
        avg_all_demand = merged['SystemDemand'].mean()
        spikes_logic = (avg_spike_wind < avg_all_wind) or (avg_spike_demand > avg_all_demand)
        results.append({
            'Check': 'Logic: Spikes align with Low Wind / High Demand',
            'Value1': f"W:{round(avg_spike_wind,0)}, D:{round(avg_spike_demand,0)}",
            'Value2': f"W:{round(avg_all_wind,0)}, D:{round(avg_all_demand,0)}",
            'Variance': 'N/A',
            'Status': 'PASS' if spikes_logic else 'FAIL'
        })
        
    # Layer 3: Benchmarks
    results.append({
        'Check': 'Benchmark: Average SMP vs CRU (Q2 2023 ~€115)',
        'Value1': round(smp_mean, 2),
        'Value2': '115',
        'Variance': 'N/A',
        'Status': 'INFO'
    })

    df_results = pd.DataFrame(results, columns=['Check', 'Value1', 'Value2', 'Variance', 'Status'])
    df_results.to_csv(DATA_DIR / "validation_report.csv", index=False)
    print("Validation report saved.")
    return df_results
