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
from collections import Counter
import string
import regex as re
# from cache import cache
# from config import stop_words
import pickle
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

# common sql connection (check_same_thread=False)
conn = sqlite3.connect('twitter.db', check_same_thread=False)
c = conn.cursor()


# generating table for recent tweets
def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color': app_colors['text']}
                              )
                          ),
                          html.Tbody(
                              [

                                  html.Tr(
                                      children=[
                                          html.Td(data) for data in d
                                      ], style={'color': app_colors['text'],
                                                'background-color':quick_color(d[2])}
                                  )
                                  for d in df.values.tolist()])
                      ]
                      )


# creating app layout
app.layout = html.Div([
    # dashboard title
    html.Div([html.H1('Dashboard')],
             style={'color': '#CCCCCC', 'text-align': 'center'}
             ),
    # input map_box
    html.Div([html.H3('Enter the Word for Sentiment Analysis'),
              dcc.Input(id='sentiment_term',
                        value='',
                        placeholder='Enter Query',
                        type='text')],
             style={'color': '#CCCCCC',
                    'text-align': 'center'}
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
                                                    ),
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
                                              font=dict(color='#CCCCCC'),
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
                          'layout':go.Layout(title='Sentiment Pie', paper_bgcolor="#020202", font=dict(color='#CCCCCC'))
                      })
        ], style={'width': '25%', 'display': 'inline-block'}
        )

    ]
    ),
    html.Div(id="recent-tweets-table", children='Recent tweets box'),

    dcc.Interval(id='graph-update', interval=1*1000,
                 n_intervals=0),
    dcc.Interval(id='map-update', interval=5*1000,
                 n_intervals=0),
    dcc.Interval(id='pie-update', interval=10*1000,
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
                                                      font=dict(color='#CCCCCC'),
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
                                      font=dict(color='#CCCCCC'),
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
              events=[Event('pie-update', 'interval')])
def pie_updater(sentiment_term, slider_value):
    try:

        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/slider_value)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = 0
        Y = 0
        for sent in df['sentiment_smoothed']:
            if sent > 0:
                X = X + 1
            elif sent < 0:
                Y = Y+1
            else:
                pass

        pair = [X, Y]
        figure = {
            'data': [go.Pie(labels=['+ve', '-ve'],
                            values=pair,
                            hoverinfo="percent+label",
                            # textinfo="label+percent",
                            marker=dict(
                colors=['#92d8d8', '#fac1b7']))],
            'layout': go.Layout(title='Sentiment Pie', paper_bgcolor="#020202", font=dict(color='#1242e2'))
        }
        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


# callback decorator for recent tweets
@app.callback(Output('recent-tweets-table', 'children'),
              [Input('sentiment_term', 'value')],
              events=[Event('graph-update', 'interval')])
def update_recent_tweets(sentiment_term):
    if sentiment_term:
        df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 10",
                         conn, params=(sentiment_term+'*',))
    else:
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 10", conn)

    df['date'] = pd.to_datetime(df['unix'], unit='ms')

    df = df.drop(['unix', 'id'], axis=1)
    df = df[['date', 'tweet', 'sentiment']]

    return generate_table(df, max_rows=10)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})


# running dash server
if __name__ == '__main__':
    app.run_server(debug=True)
