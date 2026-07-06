import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.metrics import load_data
from components.sidebar import render_sidebar
from components.charts import MARKET_COLORS

st.set_page_config(page_title="Price Analysis", layout="wide")
render_sidebar()
st.title("Price Analysis")

smp_df, _, _ = load_data()

if smp_df.empty:
    st.warning("Data not available.")
else:
    smp_df['Time'] = smp_df['Datetime'].dt.strftime('%H:%M')
    smp_df['DayOfWeek'] = smp_df['Datetime'].dt.day_name()
    
    st.markdown("### Market vs Imbalance Comparison")
    metric_choice = st.radio("Select Metric:", ("Price", "Volume"), horizontal=True, index=1)
    
    if metric_choice == "Price":
        st.write("Comparing Market Price vs Imbalance Settlement Price (ISP)")
        comp_col1, comp_col2 = st.columns(2)
        comp_col3, comp_col4 = st.columns(2)
        
        markets = [("DAM", comp_col1), ("IDA1", comp_col2), ("IDA2", comp_col3), ("IDA3", comp_col4)]
        for market, col in markets:
            if f'{market}_Price' in smp_df.columns:
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df[f'{market}_Price'], name=f'{market} Price', line=dict(color=MARKET_COLORS.get(market, 'blue'))))
                fig_comp.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df['ISP'], name='ISP', line=dict(color=MARKET_COLORS['ISP'])))
                fig_comp.update_layout(title=f'{market} Price vs ISP', xaxis_title="Date", yaxis_title="€/MWh")
                col.plotly_chart(fig_comp, use_container_width=True)
                
    else:
        st.write("Comparing Market Volume vs Net Imbalance Volume (NIV)")
        comp_col1, comp_col2 = st.columns(2)
        comp_col3, comp_col4 = st.columns(2)
        
        markets = [("DAM", comp_col1), ("IDA1", comp_col2), ("IDA2", comp_col3), ("IDA3", comp_col4)]
        for market, col in markets:
            if f'{market}_Volume' in smp_df.columns:
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df[f'{market}_Volume'], name=f'{market} Volume', line=dict(color=MARKET_COLORS.get(market, 'blue'))))
                fig_comp.add_trace(go.Scatter(x=smp_df['Datetime'], y=smp_df['NIV'], name='NIV', line=dict(color=MARKET_COLORS['NIV'])))
                fig_comp.update_layout(title=f'{market} Volume vs NIV', xaxis_title="Date", yaxis_title="MW/MWh")
                col.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("### Market Price vs ISP Variance (Spread)")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    variance_color = 'gray'
    
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

