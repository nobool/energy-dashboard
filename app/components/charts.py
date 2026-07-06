import plotly.express as px
import plotly.graph_objects as go

MARKET_COLORS = {
    'DAM': '#1f77b4',
    'IDA1': '#2ca02c',
    'IDA2': '#ff7f0e',
    'IDA3': '#9467bd',
    'ISP': '#d62728',
    'NIV': '#d62728'
}

def plot_market_prices(df):
    fig = go.Figure()
    if 'DAM_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['DAM_Price'], name='DAM Price', mode='lines', line=dict(color=MARKET_COLORS['DAM'])))
    if 'IDA1_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['IDA1_Price'], name='IDA 1 Price', mode='lines', line=dict(color=MARKET_COLORS['IDA1'])))
    if 'IDA2_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['IDA2_Price'], name='IDA 2 Price', mode='lines', line=dict(color=MARKET_COLORS['IDA2'])))
    if 'IDA3_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['IDA3_Price'], name='IDA 3 Price', mode='lines', line=dict(color=MARKET_COLORS['IDA3'])))
        
    fig.update_layout(title='Half Hourly Market Prices (DAM & IDA)', xaxis_title="Date", yaxis_title="Price (€/MWh)")
    return fig

def plot_system_demand_vs_renewables(df):
    fig = go.Figure()
    if 'SystemDemand' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SystemDemand'], fill='tozeroy', name='System Demand'))
    if 'WindGeneration' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['WindGeneration'], fill='tozeroy', name='Wind Generation'))
    if 'SolarGeneration' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SolarGeneration'], fill='tozeroy', name='Solar Generation'))
        
    fig.update_layout(title='System Demand vs Solar and Wind Generation', xaxis_title="Date", yaxis_title="MW")
    return fig

def plot_residual_demand(df):
    fig = go.Figure()
    if 'SystemDemand' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SystemDemand'], name='Total System Demand', mode='lines'))
        wind = df['WindGeneration'] if 'WindGeneration' in df.columns else 0
        solar = df['SolarGeneration'] if 'SolarGeneration' in df.columns else 0
        residual = df['SystemDemand'] - (wind + solar)
        fig.add_trace(go.Scatter(x=df['Datetime'], y=residual, fill='tozeroy', name='Residual Demand', line=dict(color='gray')))
        
    fig.update_layout(title='Total System Demand vs Residual Demand', xaxis_title="Date", yaxis_title="MW")
    return fig

