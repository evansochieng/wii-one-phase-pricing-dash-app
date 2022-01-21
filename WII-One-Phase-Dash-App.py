#load libraries

import dash
from dash import dcc
from dash import html
import pandas as pd
import os
import numpy as np
import random
from scipy import spatial
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import plotly.express as px

# Build the app
# Output the pixelname and other locational features of the farmer
# Plot the location of the farmer on the map
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#87CEEB',
    'text': '#7FDBFF',
    'subheadingsText': "red",
    'outputText': "blue",
    'submitText': 'green'
}

# Data preparation and cleaning
# load data
# os.chdir("C:/Users/HP/Desktop/Pricing Project")
data = pd.read_csv("Pixel524507.csv")

# drop column "Unnamed: 0"
data = data.drop(["Unnamed: 0"], axis=1)

# Assign 'NaN' to the -999 values(representing missing value)
data[data < 0] = float("NaN")

# app layout
app.layout = html.Div(children=[
    html.Div(children=[
        html.H1("PIXEL524507 FABA BEANS EMERGENCE PHASE DROUGHT COVER",
                style={'textAllign': 'center', 'color': colors['text']}
                )]),

    html.Div(children=[
        html.H2("CUSTOMER PERSONAL INFORMATION"),
        html.Div(children=[
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']},
                           children=["Customer Name"]),
                html.Div(dcc.Input(id='name', placeholder='Enter your name... ', type='text', value=''))
            ]),
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']},
                           children=["Serial Number"]),
                html.Div(dcc.Input(id='contact', placeholder='Enter your unique serial number... ', type='number', min=0, value=''))
            ], style={'padding-left': '50px'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'margin-bottom': '10px', 'textAlign': 'center',
                  'width': '50%',
                  'margin': 'auto'
                  })
    ]),

    html.Br(),

    html.Div(children=[
        html.H2("CONTRACT PARAMETERS"),
        html.Div(children=[
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']},
                           children=["Cover period"]),
                html.Div(dcc.RangeSlider(id='period', min=0, max=366, step=1, marks={i: i for i in range(0,367,20)},
                                         value=[246, 275]))
            ], style={'width': '50%'}),
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']},
                           children=["Area under cultivation"]),
                html.Div(dcc.Input(id='size', min=0, max=20, step=1, type='number', value=1))
            ], style={'width': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row'}),

        html.Br(),

        html.Div(children=[
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']},
                           children=["Phase trigger"]),
                html.Div(
                    dcc.Dropdown(id='trigger', options=[{"label": i, "value": i} for i in range(60, 91, 1)], value=80))
            ], style={'width': '50%'}),
            html.Div(children=[
                html.Br(),
                html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']}, children=["Phase exit"]),
                html.Div(
                    dcc.Dropdown(id='exit', options=[{"label": i, "value": i} for i in range(20, 41, 1)], value=20))
            ], style={'width': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ], style={'backgroundColor': colors['background'], 'padding': 10, 'flex': 1}),

    html.Br(),

    html.Div(children=[
        html.Button('Submit', id='submit-button', n_clicks=0,
                    style={'textAlign': 'center', 'backgroundColor': colors['submitText']})
    ], style={'margin-bottom': '10px',
              'textAlign': 'center',
              'width': '220px',
              'margin': 'auto'}),

    html.Br(),

    html.Div(children=[
        html.Label(style={"font-weight": "bold", 'textAlign': 'center', 'color': colors['subheadingsText']},
                   children=["HISTORICAL PAYOUT"]),
        dcc.Graph(id='historical-payout-graph', figure={})
    ], style={'border': 'solid 2px blue'}),

    html.Div(children=[
        html.Br(),
        html.Label(style={"font-weight": "bold", 'color': colors['subheadingsText']}, children=["Monthly Premium"]),
        html.Div(id='premium', style={"color": colors['outputText']})
    ], style={'width': '150px'})

])


@app.callback(Output('historical-payout-graph', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('period', 'value'),
               State('size', 'value'),
               State('trigger', 'value'),
               State('exit', 'value')])
def historical_payout_graph(n_clicks, input1, input2, input3, input4):
    # Cumulative rainfall
    cover_period = [v for v in input1]
    x = cover_period[0]
    y = cover_period[1]
    historical_rainfall = pd.DataFrame(data.iloc[x:y, :].sum(axis=0, skipna=True)).transpose()
    historical_rainfall.index = ["rain_sum"]  # define the row name

    # Historical payout
    minimum_payout = 300
    maximum_payout = 3000  # sum insured per unit acre - total sum insured will be equal to amount the farmers have invested
    maximum_payout = maximum_payout * input2

    # trigger and exit
    trigger = input3
    exit = input4

    # payout per mm of rainfall, tick
    # = (maximum_payout-minimum_payout)/(trigger-exit)
    tick = (maximum_payout - minimum_payout) / (trigger - exit)

    # dataframe of historical payouts
    payout = pd.DataFrame(index=["payouts"], columns=[data.columns])
    for i in range(len(data.columns)):
        if historical_rainfall.iloc[0, i] > exit and historical_rainfall.iloc[0, i] <= trigger:
            payout.iloc[0, i] = minimum_payout + (trigger - historical_rainfall.iloc[0, i]) * tick
        elif historical_rainfall.iloc[0, i] <= exit:
            payout.iloc[0, i] = minimum_payout + (trigger - exit) * tick  # this is just maximum_payout
        else:
            payout.iloc[0, i] = 0

    # use plotly express to plot the historical payouts
    x = payout.columns
    # convert x to a pure list:
    x = [item for t in x for item in t]
    y = list(payout.iloc[0, :])

    fig = px.bar(
        x=x, y=y,
        labels=dict(x='Years', y='Payouts'),
        title='Historical Payouts'
    )
    return fig


@app.callback(Output('premium', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('period', 'value'),
               State('size', 'value'),
               State('trigger', 'value'),
               State('exit', 'value')])
def premium_calculation(n_clicks, input1, input2, input3, input4):
    # Cumulative rainfall
    cover_period = [v for v in input1]
    x = cover_period[0]
    y = cover_period[1]
    historical_rainfall = pd.DataFrame(data.iloc[x:y, :].sum(axis=0, skipna=True)).transpose()
    historical_rainfall.index = ["rain_sum"]  # define the row name

    # Historical payout
    minimum_payout = 300
    maximum_payout = 3000  # sum insured per unit acre - total sum insured will be equal to amount the farmers have invested
    maximum_payout = maximum_payout * input2

    # trigger and exit
    trigger = input3
    exit = input4

    # payout per mm of rainfall, tick
    # = (maximum_payout-minimum_payout)/(trigger-exit)
    tick = (maximum_payout - minimum_payout) / (trigger - exit)

    # dataframe of historical payouts
    payout = pd.DataFrame(index=["payouts"], columns=[data.columns])
    for i in range(len(data.columns)):
        if historical_rainfall.iloc[0, i] > exit and historical_rainfall.iloc[0, i] <= trigger:
            payout.iloc[0, i] = minimum_payout + (trigger - historical_rainfall.iloc[0, i]) * tick
        elif historical_rainfall.iloc[0, i] <= exit:
            payout.iloc[0, i] = minimum_payout + (trigger - exit) * tick  # this is just maximum_payout
        else:
            payout.iloc[0, i] = 0

    # calculate premium
    pure_premium = int(payout.mean(axis=1))
    # use string formatting to round premium to 3 significant figures
    pure_premium = float('%.3g' % pure_premium)
    return pure_premium


if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
