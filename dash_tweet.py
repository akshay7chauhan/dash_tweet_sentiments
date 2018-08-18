# imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, Event
import plotly.graph_objs as go

import sqlite3
import pandas as pd


import plotly.plotly as py
from plotly.graph_objs import *
py.sign_in('akshay7chauhan',
           'c17dpSCUaTftQEtiuGQg')
map_box_key = 'pk.eyJ1Ijoic2FydGhha3F1aWx0IiwiYSI6ImNqazU0cDQ0ZjFnMGIzcG10bzV2N2FvNXoifQ.1KSgyiwemP39HHcCvocgbg'
# creating dash app
app = dash.Dash()

server = app.server


# common sql connection (check_same_thread=False)
conn = sqlite3.connect('twitter.db', check_same_thread=False)
c = conn.cursor()


# creating app layout
app.layout = html.Div([
    # dashboard title
    html.Div(
        className="nav navbar",
        children=(
            html.Div(className="container",
                     children=(html.A(children=html.Img(src="https://quilt.ai/wp-content/uploads/2018/06/client-07_IKEA-2.jpg"),

                                      className=["navbar-brand"],
                                      ),
                               ),
                     ),
        ),
    ),
    # input map_box
    html.Div(
        className="jumbotron text-center",
        children=[(html.Div([html.H3('Look up Keyword'),
                             dcc.Input(id='sentiment_term',
                                       value='',
                                       placeholder='Type in your keyword',
                                       type='text'),
                             html.Div(dcc.Dropdown(id='tweet-number',
                                                   options=[
                                                       {'label': '10',
                                                        'value': 10},
                                                       {'label': '25',
                                                        'value': 25},
                                                       {'label': '50',
                                                        'value': 50},
                                                       {'label': '100',
                                                        'value': 100},
                                                       {'label': '200',
                                                        'value': 200}
                                                   ],

                                                   ),


                                      )]
                            ))]
    ),

    # graph component
    html.Div([html.Div(
        [dcc.Graph(id='scatter_plot',
                   figure={
                       'data': [
                           go.Scatter(x=[1],
                                      y=[1],
                                      mode='markers+lines',
                                      marker=dict(symbol='circle'),
                                      line=dict(
                               # shape="spline",
                               smoothing=1,
                               width=1,
                               color='rgb(168,203,212)'
                           ))],
                       'layout':go.Layout(title='Keyword',
                                          # plot_bgcolor="#222226",
                                          # font=dict(color='#CCCCCC',
                                          #           ),
                                          # paper_bgcolor="#020202",
                                          xaxis=dict(showgrid=False, showline=True),
                                          yaxis=dict(showgrid=False, showline=True),
                                          hovermode='closest')
                   })

         ]

    ),
        html.Div(className="row", children=[
            html.Div(className="col-8", children=[
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
                              'layout': go.Layout(autosize=False,
                                                  width=800,
                                                  height=600,
                                                  # paper_bgcolor="#020202",
                                                  # font=dict(color='#CCCCCC'),
                                                  mapbox={'accesstoken': map_box_key,
                                                          # 'style': "dark",
                                                          'zoom': 0.7,
                                                          'center': dict(
                                                              lon=10,
                                                              lat=30
                                                          ),
                                                          })})
            ],
            ),
            html.Div(className="col-4", children=[html.H3("Sentiments"), html.H6("real time updates"),
                                                  dcc.Graph(id='pie',
                                                            figure={
                                                                'data': [go.Pie(labels=['Positive', 'Negative', 'Neutral'],
                                                                                values=[1, 1, 1],
                                                                                hoverinfo="percent+label",
                                                                                textfont=dict(
                                                                                    size=20, color='white'),
                                                                                # textinfo="label+percent",
                                                                                marker=dict(
                                                                    colors=['#6dc993', '#ff6666', '#ffc46e']))],
                                                                'layout':go.Layout(showlegend=False, margin=go.layout.Margin(
                                                                    l=5,
                                                                    r=5,
                                                                    b=1,
                                                                    t=1,
                                                                    pad=2
                                                                ))
                                                            })
                                                  ],
                     style={'text-align': 'center'}
                     )

        ]
    ),
        # html.Div(id="recent-tweets-table"),

        dcc.Interval(id='graph-update', interval=2*1000,
                     n_intervals=0),
        dcc.Interval(id='map-update', interval=5*1000,
                     n_intervals=0),
        dcc.Interval(id='pie-update', interval=4*1000,
                     n_intervals=0)],
        className=['container']
    )

]
)

# callback decorator for scatter_plot


@app.callback(Output('scatter_plot', 'figure'),
              [Input('sentiment_term', 'value'),
               Input('tweet-number', 'value')],
              events=[Event('graph-update', 'interval')])
def scatter_updater(sentiment_term, tweet_number):
    try:

        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        # df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/slider_value)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = df.index[-tweet_number:]
        Y = df.sentiment[-tweet_number:]
        data = go.Scatter(
            x=X,
            y=Y,
            mode='markers+lines',
            marker=dict(symbol='circle', size=12,
                        color=Y, cmax=1, cmin=-1,
                        colorscale=[[0, '#ff6666'], [0.49, '#ff6666'], [0.49, '#ffc46e'], [
                            0.51, '#ffc46e'], [0.51, '#6dc993'], [1, '#6dc993']]
                        ),
            text=df['tweet'],
            line=dict(
                # shape="spline",
                smoothing=1,
                width=1,
                color='rgb(168,203,212)'
            )
        )

        figure = {'data': [data], 'layout': go.Layout(title='Keyword: {}'.format(sentiment_term),
                                                      # plot_bgcolor="#222226",
                                                      # font=dict(color='#CCCCCC'),
                                                      # paper_bgcolor="#020202",
                                                      xaxis=dict(showgrid=False,
                                                                 zeroline=True, showline=True, color='rgb(203,203,203)'),
                                                      yaxis={'range': [-1, 1], 'showgrid': False, 'zeroline': True, 'showline': True, 'color': 'rgb(203,203,203)'})}

        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


# callback decorator for Scattermapbox
@app.callback(Output('map_box', 'figure'),
              [Input('sentiment_term', 'value'),
               Input('tweet-number', 'value')],
              events=[Event('map-update', 'interval')])
def mapbox_updater(sentiment_term, tweet_number):
    try:

        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        # df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/200)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        XDF = df[-tweet_number:]
        X = XDF[XDF['sentiment'] > 0]['lat']
        Y = XDF[XDF['sentiment'] > 0]['lng']
        X1 = XDF[XDF['sentiment'] < 0]['lat']
        Y1 = XDF[XDF['sentiment'] < 0]['lng']
        X2 = XDF[XDF['sentiment'] == 0]['lat']
        Y2 = XDF[XDF['sentiment'] == 0]['lng']

        positive = go.Scattermapbox(
            lat=X,
            lon=Y,
            text=df['tweet'],
            name='Positive',
            mode='markers',
            marker=dict(
                size=12,
                color="#6dc993",
                opacity=0.8
            ),
        )

        negative = go.Scattermapbox(
            lat=X1,
            lon=Y1,
            text=df['tweet'],
            name='Negative',
            mode='markers',
            marker=dict(
                size=12,
                color="#ff6666",
                opacity=0.8
            ),
        )

        neutral = go.Scattermapbox(
            lat=X2,
            lon=Y2,
            text=df['tweet'],
            name='Neutral',
            mode='markers',
            marker=dict(
                size=12,
                color="#ffc46e",
                opacity=0.8
            ),
        )

        figure = {'data': [positive, negative, neutral],
                  'layout': go.Layout(legend=dict(orientation="h", x=.3, y=1.2, font=dict(size=18)),
                                      autosize=False,
                                      width=800,
                                      height=600,
                                      # paper_bgcolor="#020202",
                                      # font=dict(color='#CCCCCC'),
                                      mapbox={'accesstoken': map_box_key,
                                              # 'style': "dark",
                                              # 'pitch': 15,
                                              'zoom': 0.7,
                                              'center': dict(
                                                  lon=10,
                                                  lat=30
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
               Input('tweet-number', 'value')],
              events=[Event('pie-update', 'interval')])
def pie_updater(sentiment_term, tweet_number):
    try:

        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200",
                         conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        # df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/slider_value)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        X = 0
        Y = 0
        Z = 0
        for sent in df['sentiment'][-tweet_number:]:
            if sent > 0:
                X = X + 1
            elif sent < 0:
                Y = Y+1
            else:
                Z = Z+1

        triplet = [X, Y, Z]
        figure = {
            'data': [go.Pie(labels=['Positive', 'Negative', 'Neutral'],
                            values=triplet,
                            hoverinfo="percent+label",
                            textinfo='percent',
                            textfont=dict(size=20, color='white'),
                            domain=dict(x=[0, 1], y=[0, 1]),
                            marker=dict(
                colors=['#6dc993', '#ff6666', '#ffc46e']))],
            'layout': go.Layout(showlegend=False, margin=go.layout.Margin(
                l=5,
                r=5,
                b=1,
                t=1,
                pad=2
            ))
        }
        return figure

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})


# running dash server
if __name__ == '__main__':
    app.run_server(debug=True)
