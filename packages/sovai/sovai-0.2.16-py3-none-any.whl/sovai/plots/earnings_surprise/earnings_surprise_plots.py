import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sovai import data
import random

# Global dictionary to keep track of apps and their ports
app_ports = {}


def get_unique_port(app_name):
    global app_ports
    min_port = 8050  # define the range of ports you want to use
    max_port = 8099

    if app_name in app_ports:
        # Return the previously assigned port for this app
        return app_ports[app_name]
    else:
        # Generate a unique port for the new app
        while True:
            port = random.randint(min_port, max_port)
            if (
                port not in app_ports.values()
            ):  # check if the port is not already in use
                app_ports[app_name] = port
                return port


def create_earnings_surprise_plot():
    df_earn = data("earnings/surprise")


    def calculate_slope(data):
        x = np.arange(len(data))
        slope, _ = np.polyfit(x, data, 1)
        return slope

    def create_figure(df_company, df_price, ticker):
        df_company['rolling_slope'] = df_company['surprise_probability'].rolling(window=13).apply(calculate_slope)
        min_slope = df_company['rolling_slope'].min()
        max_slope = df_company['rolling_slope'].max()
        df_company['scaled_slope'] = np.interp(df_company['rolling_slope'], (min_slope, max_slope), (-0.5, 0.5))

        fig = go.Figure()

        # Earnings data
        fig.add_trace(go.Scatter(x=df_company.index, y=df_company['surprise_probability'], name='Predicted Surprise Probability', line=dict(color='#00FFFF', width=2)))
        fig.add_trace(go.Scatter(x=df_company.index, y=df_company['eps_surprise'], name='Real EPS Surprise', line=dict(color='#FF69B4', width=2)))
        fig.add_trace(go.Scatter(x=df_company.index, y=df_company['scaled_slope'], name='Surprise Probability Rolling Slope (13-period, Scaled)', line=dict(color='#d62728', width=1)))

        # Stock price data
        fig.add_trace(go.Scatter(x=df_price['date'], y=df_price['closeadj'], name='Stock Price', yaxis='y2', line=dict(color='#90EE90', width=2)))

        earnings_range = max(
            abs(df_company['surprise_probability'].min()),
            abs(df_company['surprise_probability'].max()),
            abs(df_company['eps_surprise'].min()),
            abs(df_company['eps_surprise'].max())
        )

        fig.update_layout(
            title=dict(text=f'{ticker}: Earnings Surprise and Stock Price', font=dict(size=20, color='white')),
            xaxis=dict(
                title='Date', 
                gridcolor='#2c2c2c', 
                showgrid=True, 
                linecolor='white', 
                tickfont=dict(color='white'),
                range=[df_company.index.min(), df_company.index.max()]  # Set x-axis range based on earnings data
            ),
            yaxis=dict(
                title='Earnings Metrics',
                range=[-earnings_range, earnings_range],
                gridcolor='#2c2c2c',
                showgrid=True,
                linecolor='white',
                tickfont=dict(color='white')
            ),
            yaxis2=dict(
                title='Stock Price',
                overlaying='y',
                side='right',
                gridcolor='#2c2c2c',
                showgrid=False,
                linecolor='white',
                tickfont=dict(color='white')
            ),
            plot_bgcolor='#1c1c1c',
            paper_bgcolor='#1c1c1c',
            legend=dict(
                x=0.5,
                y=-0.2,
                orientation='h',
                xanchor='center',
                font=dict(color='white'),
                bgcolor='#1c1c1c',
                bordercolor='white',
                borderwidth=1
            ),
            hovermode='x unified',
            hoverlabel=dict(font=dict(color='white'), bgcolor='#1c1c1c')
        )

        return fig
    
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[{'label': ticker, 'value': ticker} for ticker in df_earn.index.get_level_values('ticker').unique()],
            value='ADBE',  # Default value
            style={'width': '50%', 'margin': '10px auto'}
        ),
        dcc.Graph(id='stock-graph')
    ])

    @app.callback(
        Output('stock-graph', 'figure'),
        Input('ticker-dropdown', 'value')
    )
    def update_graph(selected_ticker):
        df_company = df_earn.reset_index().set_index("date").query("ticker == @selected_ticker")
        price_df = data("market/prices", tickers=[selected_ticker]).reset_index()
        return create_figure(df_company, price_df, selected_ticker)


    app_name = "earning_surprise_plot"
    return app.run_server(
        debug=False, port=get_unique_port(app_name)
    )  # Apply exponential moving average to smooth the data
