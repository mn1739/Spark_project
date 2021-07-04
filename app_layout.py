import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_table import DataTable

def generate_recos_list(recos):
    cards = []
    for index, row in recos.iterrows():
        link = 'https://www.google.com/search?q=' + row['title'].replace(' ', '+')
        header = html.A(row['title'], href=link, target='_blank', style={'text-decoration': 'none', 'font-size': 15})
        body = html.Div(row['genres'], style={'font-size': 13})
        cards.append([dbc.CardHeader(header, style={'padding': 10, 'padding-top': 7, 'padding-bottom': 7}),
                      dbc.CardBody(body, style={'padding': 10})])
    rows = []
    l = len(cards)
    for i in range(0, l, 2):
        if i == l - 1:
            rows.append(dbc.Row(
                dbc.Col(dbc.Card(cards[i], color='primary', outline=True), width=6, style={'padding': 8}),
            ))
        else:
            rows.append(dbc.Row([
                dbc.Col(dbc.Card(cards[i], color='primary', outline=True), width=6, style={'padding': 8}),
                dbc.Col(dbc.Card(cards[i+1], color='primary', outline=True), width=6, style={'padding': 8})
            ]))
    return rows

def get_layout(movies_dict, genres, user_ratings_file, user_ratings_df):
    layout = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='select-movie',
                    options=[{'label': movies_dict[key], 'value': key} for key in movies_dict],
                    value=1,
                    placeholder='Select a Movie',
                    clearable=False
                ), width=3, style={'padding-right': 0}
            ),
            dbc.Col(
                dcc.Slider(
                    id='rating',
                    min=0.5, max=5, step=0.5,
                    marks={i: str(i) for i in range(1, 6)},
                    value=0.5
                ), width=2, style={'padding': 0}
            ),
            dbc.Col(
                dbc.Button(
                    '➕',
                    id='add-rating',
                    color='primary'
                ), width='auto', style={'padding': 0}
            ),
            dbc.Col(
                dbc.Button(
                    'Save ratings',
                    id='save-ratings',
                    color='warning'
                ), width='auto', style={'padding-left': 15, 'padding-right': 5}
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='select-genre',
                    options=[{'label': genre, 'value': genre} for genre in genres],
                    multi=True,
                    placeholder='Filter by genre'
                )
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='exclude-genre',
                    options=[{'label': genre, 'value': genre} for genre in genres],
                    multi=True,
                    placeholder='Exclude genres'
                ), style={'padding-left': 0}
            ),
            dbc.Col(
                dbc.Button(
                    '▶',
                    id='run-model',
                    color='success'
                ), width='auto', style={'padding-left': 0}
            )
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col(
                DataTable(
                    id='user-ratings',
                    columns=[{'id': 'MOVIE', 'name': 'MOVIE'}, {'id': 'RATING', 'name': 'RATING'}],
                    data=user_ratings_df,
                    editable=True,
                    row_deletable=True,
                    style_as_list_view=True,
                    style_table={'height': '500px', 'overflowY': 'auto'},
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'padding': 10,
                        'height': 'auto',
                        'font-size': 15
                    },
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'MOVIE'},
                            'textAlign': 'left'
                        },
                        {
                            'if': {'column_id': 'RATING'},
                            'width': '12%'
                        }
                    ],
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'even'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    }
                ), style={'padding-right': 40, 'padding-top': 8}, width=5
            ),
            dbc.Col(
                dbc.Spinner(
                    html.Div(id='recos-list')
                )
            ),
            dbc.Col([
                dbc.Toast(
                    f'Output filename: {user_ratings_file}',   # Notification for download
                    id="toast",
                    header="Ratings Saved!",
                    icon="success",
                    dismissable=True,
                    is_open=False,
                    duration=3000,
                    style={"position": "fixed", "top": 10, "right": 10, "width": 200}
                ),
                dcc.RangeSlider(
                    id='time-period',
                    min=1995, max=2020, step=1,
                    marks={i: str(i) for i in range(1995, 2021, 5)},
                    value=[1995, 2020],
                    allowCross=False,
                    vertical=True
                )
            ], width='auto', style={'padding-left': 35, 'padding-right': 20})
        ]),
    ], style={'padding': 20})
    return layout