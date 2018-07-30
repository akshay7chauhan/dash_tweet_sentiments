# imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, Event, State
import plotly.graph_objs as go
import numpy as np

#
import sqlite3
import pandas as pd
import time
#

from collections import deque

import plotly.plotly as py
from plotly.graph_objs import *
py.sign_in('akshay7chauhan',
           'c17dpSCUaTftQEtiuGQg')
map_box_key = 'pk.eyJ1Ijoic2FydGhha3F1aWx0IiwiYSI6ImNqazU0cDQ0ZjFnMGIzcG10bzV2N2FvNXoifQ.1KSgyiwemP39HHcCvocgbg'
# creating dash app
app = dash.Dash()

# data for scatter plot
# X = deque(maxlen=10)
# Y = deque(maxlen=10)
# starting values
# X.append(0)
# Y.append(0)


# data for Scattermapbox
# latitude = deque(maxlen=10)
# longitude = deque(maxlen=10)
# starting values
# latitude.append(23)
# longitude.append(78)


# creating app layout
app.layout = html.Div([
    # dashboard title
    html.Div([html.H1('Dashboard')],
             style={'color': '#CCCCCC', 'font-family': 'serif',
                    'font-size': '15px', 'text-align': 'center', 'font-style': 'initial'}
             ),
    # input map_box
    html.Div([html.H3('Enter the Word for Sentiment Analysis'),
              dcc.Input(id='sentiment_term',
                        value='',
                        placeholder='Enter Query',
                        type='text')],
             style={'color': '#CCCCCC',
                    'font-family': 'serif',
                    'font-size': '15px',
                    'text-align': 'center',
                    'font-style': 'normal'}
             ),
    # slider
    html.Div([
        html.H4('Smoothness Slider'),
        dcc.Slider(id='slider',
                   min=1,
                   max=50,
                   step=5,
                   value=20
                   )
    ],
        style={'color': '#CCCCCC',
               'margin-left': '5%', 'margin-right': '60%'}
    ),
    # graph component
    html.Div(
        [dcc.Graph(id='scatter_plot',
                   figure={
                       'data': [
                           go.Scatter(x=[1],
                                      y=[1],
                                      mode='markers+lines',
                                      marker=dict(symbol='diamond-open'),
                                      line=dict(
                               shape="spline",
                               smoothing=0.5,
                               width=1,
                               color='#56F0CC'
                           ))],
                       'layout':go.Layout(title='sentiment analysis',
                                          plot_bgcolor="#222226",
                                          font=dict(color='#CCCCCC',
                                                    family='serif',
                                                    size=12),
                                          paper_bgcolor="#020202",
                                          xaxis={'title': 'Random x value'},
                                          yaxis={'title': 'Random y value'},
                                          hovermode='closest')
                   })

         ]

    ),
    html.Div([
        html.Div([
            dcc.Graph(id='map_box',
                      figure={
                          'data': [go.Scattermapbox(
                              lat=[23],
                              lon=[78],
                              mode='markers',
                              marker=dict(
                                  size=6,
                                  color='#d37808',
                                  opacity=0.5
                              )
                          )],
                          'layout': go.Layout(title='Tweet pulse',
                                              paper_bgcolor="#020202",
                                              font=dict(color='#CCCCCC',
                                                        family='serif'),
                                              mapbox={'accesstoken': map_box_key,
                                                      'style': "dark",
                                                      'zoom': 1,
                                                      'center': dict(
                                                          lon=0,
                                                          lat=40
                                                      ),
                                                      })})
        ], style={'width': '75%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Graph(id='pie',
                      figure={
                          'data': [go.Pie(labels=['+ve', '-ve'],
                                          values=[1, 1],
                                          hoverinfo="percent+label",
                                          # textinfo="label+percent",
                                          marker=dict(
                              colors=['#92d8d8', '#fac1b7']))],
                          'layout':go.Layout(title='Sentiment Pie', paper_bgcolor="#020202", font=dict(color='#CCCCCC',
                                                                                                       family='serif'))
                      })
        ], style={'width': '25%', 'display': 'inline-block'}
        )

    ]
    ),

    dcc.Interval(id='graph-update', interval=1*1000,
                 n_intervals=0),
    dcc.Interval(id='map-update', interval=5*1000,
                 n_intervals=0)

], style={'background-color': "#020202"}
)

# callback decorator for scatter_plot


@app.callback(Output('scatter_plot', 'figure'),
              [Input('sentiment_term', 'value'),
               Input('slider', 'value')],
              events=[Event('graph-update', 'interval')])
def scatter_updater(sentiment_term, slider_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/slider_value)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = df.index[-100:]
        Y = df.sentiment_smoothed[-100:]
        data = go.Scatter(
            x=X,
            y=Y,
            mode='markers+lines',
            marker=dict(symbol='diamond-open'),
            text=df['tweet'],
            line=dict(
                shape="spline",
                smoothing=0.5,
                width=1,
                color='#56F0CC'
            ))

        figure = {'data': [data], 'layout': go.Layout(title='Term: {}'.format(sentiment_term),
                                                      plot_bgcolor="#222226",
                                                      font=dict(color='#CCCCCC',
                                                                family='serif', size=12),
                                                      paper_bgcolor="#020202",
                                                      xaxis={'title': 'timeline'},
                                                      yaxis={'title': 'sentiment', 'range': [-1, 1]})}

        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


# callback decorator for Scattermapbox
@app.callback(Output('map_box', 'figure'),
              [Input('sentiment_term', 'value')],
              events=[Event('map-update', 'interval')])
def mapbox_updater(sentiment_term):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        # df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/200)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = df.lat[-50:]
        Y = df.lng[-50:]

        data = go.Scattermapbox(
            lat=X,
            lon=Y,
            text=df['tweet'],
            mode='markers',
            marker=dict(
                size=6,
                color='#d37808',
                opacity=0.5
            ),
        )

        figure = {'data': [data],
                  'layout': go.Layout(title='Tweet pulse for ' + sentiment_term,
                                      paper_bgcolor="#020202",
                                      font=dict(color='#CCCCCC',
                                                family='serif', size=12),
                                      mapbox={'accesstoken': map_box_key,
                                              'style': "dark",
                                              'zoom': 1,
                                              'center': dict(
                                                  lon=0,
                                                  lat=40
                                              )
                                              })}

        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


# callback decorator for  pie chart
@app.callback(Output('pie', 'figure'),
              [Input('sentiment_term', 'value'),
               Input('slider', 'value')],
              events=[Event('graph-update', 'interval')])
def pie_updater(sentiment_term, slider_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/slider_value)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = 0
        Y = 0
        if df['sentiment_smoothed'] > 0:
            X = X + 1
        elif df['sentiment_smoothed'] < 0:
            Y = Y+1
        else:
            pass

        pair = [X, Y]
        figure = {
            'data': [go.Pie(labels=['Positive Sentiment', 'Negative Sentiment'],
                            values=pair,
                            hoverinfo="percent+label",
                            # textinfo="label+percent",
                            marker=dict(
                colors=['#92d8d8', '#fac1b7']))],
            'layout': go.Layout(title='Sentiment Pie', paper_bgcolor="#020202", font=dict(color='#CCCCCC',
                                                                                          family='serif'))
        }
        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')



# running dash server
if __name__ == '__main__':
    app.run_server(debug=True)
