import plotly.express as px
import plotly.graph_objects as go

def plot_smp_timeseries(df):
    fig = px.line(df, x='Datetime', y='SMP', title='System Marginal Price (SMP) Time Series')
    fig.update_layout(xaxis_title="Date", yaxis_title="Price (€/MWh)")
    return fig

def plot_demand_wind_area(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SystemDemand'], fill='tozeroy', name='System Demand'))
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['WindGeneration'], fill='tozeroy', name='Wind Generation'))
    fig.update_layout(title='System Demand vs Wind Generation', xaxis_title="Date", yaxis_title="MW")
    return fig
