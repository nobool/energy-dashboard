import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar
from components.charts import MARKET_COLORS

st.set_page_config(page_title="Price Analysis", layout="wide",page_icon="⚡")
render_sidebar()
from components.header import render_header
render_header("Price Analysis")

smp_df, _, _ = load_data()

if smp_df.empty:
    st.warning("Data not available.")
else:
    smp_df['Time'] = smp_df['Datetime'].dt.strftime('%H:%M')
    smp_df['DayOfWeek'] = smp_df['Datetime'].dt.day_name()
    
    st.markdown("### Market Volumes")
    
    
    vol_cols = [c for c in ['DAM_Volume', 'IDA1_Volume', 'IDA2_Volume', 'IDA3_Volume'] if c in smp_df.columns]
    y_range = None
    if vol_cols:
        global_min = smp_df[vol_cols].min().min()
        global_max = smp_df[vol_cols].max().max()
        pad = (global_max - global_min) * 0.05
        y_range = [global_min - pad, global_max + pad]

    def plot_market_volume(market, metric, y_title, col):
        col_name = f'{market}_{metric}'
        if col_name in smp_df.columns:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(x=smp_df['Datetime'], y=smp_df[col_name], name=f'{market} {metric}', marker_color=MARKET_COLORS.get(market, 'blue')))
            
            layout_args = dict(title=f'{market} {metric}', xaxis_title="Date", yaxis_title=y_title)
            if y_range:
                layout_args['yaxis'] = dict(range=y_range)
                
            fig_comp.update_layout(**layout_args)
            col.plotly_chart(fig_comp, use_container_width=True)

    st.write("Market Volumes")
    comp_col1, comp_col2 = st.columns(2)
    comp_col3, comp_col4 = st.columns(2)
    
    markets = [("DAM", comp_col1), ("IDA1", comp_col2), ("IDA2", comp_col3), ("IDA3", comp_col4)]
    for market, col in markets:
        plot_market_volume(market, "Volume", "MW/MWh", col)

    st.markdown("### Market Price vs ISP Variance (Spread)")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    variance_color = 'blue'
    
    if 'DAM_Spread_to_ISP' in smp_df.columns:
        fig_dam = px.line(smp_df, x='Datetime', y='DAM_Spread_to_ISP', title='DAM Spread (DAM - ISP)')
        fig_dam.update_traces(line_color=variance_color)
        col1.plotly_chart(fig_dam, use_container_width=True)
    if 'IDA1_Spread_to_ISP' in smp_df.columns:
        fig_ida1 = px.line(smp_df, x='Datetime', y='IDA1_Spread_to_ISP', title='IDA 1 Spread (IDA1 - ISP)')
        fig_ida1.update_traces(line_color=variance_color)
        col2.plotly_chart(fig_ida1, use_container_width=True)
    if 'IDA2_Spread_to_ISP' in smp_df.columns:
        fig_ida2 = px.line(smp_df, x='Datetime', y='IDA2_Spread_to_ISP', title='IDA 2 Spread (IDA2 - ISP)')
        fig_ida2.update_traces(line_color=variance_color)
        col3.plotly_chart(fig_ida2, use_container_width=True)
    if 'IDA3_Spread_to_ISP' in smp_df.columns:
        fig_ida3 = px.line(smp_df, x='Datetime', y='IDA3_Spread_to_ISP', title='IDA 3 Spread (IDA3 - ISP)')
        fig_ida3.update_traces(line_color=variance_color)
        col4.plotly_chart(fig_ida3, use_container_width=True)

