import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MARKET_COLORS = {
    'DAM': '#1f77b4',
    'IDA1': '#2ca02c',
    'IDA2': '#ff7f0e',
    'IDA3': '#9467bd',
    'ISP': '#d62728'
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
    if 'ISP' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['ISP'], name='Imbalance Settlement Price', mode='lines', line=dict(color=MARKET_COLORS['ISP'])))
    fig.update_traces(line={'width': 1})    
    fig.update_layout(title='Half Hourly Market Prices (DAM, IDA and ISP)', xaxis_title="Date", yaxis_title="Price (€/MWh)")
    return fig

def plot_system_demand_vs_renewables(df):
    fig = go.Figure()
    if 'WindGeneration' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['WindGeneration'], name='Wind Generation', stackgroup='one'))
    if 'SolarGeneration' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Datetime'], 
            y=df['SolarGeneration'], 
            name='Solar Generation', 
            stackgroup='one',
            fillcolor='rgba(255, 215, 0, 0.7)',
            line=dict(color='red')
        ))
    if 'SystemDemand' in df.columns:
        residual = df['SystemDemand'].copy()
        if 'WindGeneration' in df.columns:
            residual -= df['WindGeneration']
        if 'SolarGeneration' in df.columns:
            residual -= df['SolarGeneration']
        
        # Clip to 0 to prevent plotly stackgroup errors if generation ever exceeds demand
        residual = residual.clip(lower=0)
        
        fig.add_trace(go.Scatter(
            x=df['Datetime'],
            y=residual,
            name='Residual Demand',
            stackgroup='one',
            fillcolor='lightgrey',
            line=dict(color='rgba(0,0,0,0)')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Datetime'], 
            y=df['SystemDemand'],
            mode='lines',
            name='System Demand', 
            line=dict(color='black')
        ))
    
    max_y = df['SystemDemand'].max() if 'SystemDemand' in df.columns and not df.empty else 0
    y_range_max = max_y + 2000
    
    fig.update_layout(
        title='System Demand vs Solar and Wind Generation', 
        xaxis_title="Date", 
        yaxis_title="MW", 
        hovermode='x unified',
        yaxis=dict(range=[0, y_range_max])
    )
    return fig

def plot_day_ahead_prices(df):
    fig = go.Figure()
    
    if 'DAM_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['DAM_Price'], name='I-SEM DAM Price'))
    if 'GB_DA_Price' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['GB_DA_Price'], name='GB DA Price'))
        
    fig.update_layout(
        title="I-SEM vs GB (Nordpool N2EX) Day Ahead Prices",
        xaxis_title="Date",
        yaxis_title="Price (€/MWh)",
        hovermode="x unified"
    )
    return fig

def plot_interconnector_flows_price_variance(df, interconnector_df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Net Interconnector Flow (MW)", "Price Spread (I-SEM DAM - GB DA)"))
    
    if 'InterconnectorFlow' in interconnector_df.columns:
        # A positive flow generally means imports to I-SEM, negative exports
        fig.add_trace(go.Scatter(x=interconnector_df['Datetime'], y=interconnector_df['InterconnectorFlow'], name='Net Flow (MW)', fill='tozeroy', line=dict(color='teal')), row=1, col=1)
        
    if 'DAM_Price' in df.columns and 'GB_DA_Price' in df.columns:
        spread = df['DAM_Price'] - df['GB_DA_Price']
        fig.add_trace(go.Scatter(x=df['Datetime'], y=spread, name='Price Spread (€/MWh)', fill='tozeroy', line=dict(color='purple')), row=2, col=1)
        
    fig.update_layout(height=600, hovermode="x unified", title="Interconnector Flows vs Day-Ahead Price Spread")
    fig.update_yaxes(title_text="Net Flow (MW)", row=1, col=1)
    fig.update_yaxes(title_text="Spread (€/MWh)", row=2, col=1)
    return fig
