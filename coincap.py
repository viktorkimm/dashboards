#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import requests
import json 
import pandas as pd
from datetime import datetime, timedelta
from datetime import date


assets_url = "http://api.coincap.io/v2/assets"
assets_response = requests.get(assets_url)
assets_data = json.loads(assets_response.text.encode('utf8'))
assets_raw = assets_data['data']
assets = pd.DataFrame(assets_raw, columns=['id', 'symbol'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,compress=False)
app.layout = html.Div(children=[  
    
    html.Div([

        #правый блок
        html.Div([
            #пустая часть
            html.Div([ 
                html.Br(),                
            ], style={'height': '20vh'}),
            #селектор валюты
            html.Div([
                html.Label('Select an asset'),
                dcc.Dropdown(
                    id='asset_selector',
                    clearable=False,
                    value=assets['symbol'].unique()[0],
                    options=[{'label': x, 'value': x} for x in assets['symbol'].unique()], 
                    className = 'twelve columns', 
                    style={'textAlign': 'center'})
            ], className = 'twelve columns', style={'height': '15vh', 'padding-left' : '5%', 'padding-right' : '5%'}),
            #селекторы даты
            html.Div([ 
                #селектор даты начала
                html.Div([ 
                    html.Label('Date from'),
                    dcc.DatePickerSingle(
                        id='date_from_selector',
                        date = date.today() - timedelta(days=7),
                        display_format='DD.MM.YYYY')               
                ], className = 'six columns'),
                #селектор даты конца
                html.Div([ 
                    html.Label('Date to'),
                    dcc.DatePickerSingle(
                        id='date_to_selector',
                        date = date.today(),
                        display_format='DD.MM.YYYY')               
                ], className = 'six columns'),
            ], className = 'row', style = {'padding-left' : '5%', 'padding-right' : '5%'}),
        ], className = 'four columns', style={'height': '100vh', 'backgroundColor':'#d4d3d3'}),
        #левый блок
        html.Div([
            #пустая часть
            html.Div([ 
                html.Br(),                
            ], style={'height': '10vh'}),
            #график
            dcc.Graph(
            id = 'assets_scatter', style={'height': '50vh', 'width': '90%', 
            'margin-left': 'auto', 'margin-right': 'auto', }
           ),
        ], className = 'eight columns', style={'margin-left': '0%'}),

    ], className = 'row'),         
 
])

@app.callback(
    [Output('assets_scatter', 'figure'),
    ],
    [Input('asset_selector', 'value'),
     Input('date_from_selector', 'date'),
     Input('date_to_selector', 'date'),
    ])

def history(value, date_from, date_to):
    asset_id = assets[assets['symbol'] == value].iloc[0]['id']
    date_from = datetime.strptime(date_from, '%Y-%m-%d')
    date_to = datetime.strptime(date_to, '%Y-%m-%d')
    unixtime_from = int(pd.Timestamp(date_from).value/1000000)
    unixtime_to = int((pd.Timestamp(date_to) + pd.offsets.Day(1)).value/1000000)
    rates_url = f"http://api.coincap.io/v2/assets/{asset_id}/history?interval=d1&start={unixtime_from}&end={unixtime_to}" 
    rates_response = requests.get(rates_url)
    rates_data = json.loads(rates_response.text.encode('utf8'))
    rates_raw = rates_data['data']
    rates = pd.DataFrame(rates_raw, columns=['priceUsd', 'date'])
    rates['priceUsd'] = pd.to_numeric(rates['priceUsd'],errors='coerce')
    rates['date'] = pd.to_datetime(rates['date'], format="%Y-%m-%d").dt.tz_localize(None)

    data = [go.Bar(x = rates['date'],
               y = rates['priceUsd'],
               textposition = 'auto',               
               name = 'rates')]
    return ({'data': data,
             'layout': go.Layout(xaxis = {'title': 'TIME'},
                                 yaxis = {'title': 'PRICE'},
                                 paper_bgcolor = '#eae6e6', plot_bgcolor = '#eae6e6')
    },)

if __name__ == '__main__':
    app.run_server(debug=True) 