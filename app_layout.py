import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_table import DataTable

def generate_recos_list(recos):
    recos_list = []
    for index, row in recos.iterrows():
        link = 'https://www.google.com/search?q=' + row['title'].replace(' ', '+')
        item_header = dbc.ListGroupItemHeading(html.A(row['title'], href=link, target='_blank'), style={'margin': 0})
        item_text = dbc.ListGroupItemText(row['genres'], style={'margin': 0})
        recos_list.append(dbc.ListGroupItem([item_header, item_text], style={'padding-top': 0, 'padding-bottom': 0}))
    return dbc.ListGroup(recos_list)

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
                ), width=3
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
                    'Add rating',
                    id='add-rating',
                    color='primary'
                ), width='auto', style={'padding-right': 0}
            ),
            dbc.Col(
                dbc.Button(
                    'Save ratings',
                    id='save-ratings',
                    color='warning'
                ), width='auto'
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='select-genre',
                    options=[{'label': genre, 'value': genre} for genre in genres],
                    multi=True,
                    placeholder='Filter by genre'
                ), width=3
            ),
            dbc.Col(
                dbc.Button(
                    'Get recommendations',
                    id='run-model',
                    color='success'
                ), width='auto'
            )
        ]),

        html.Br(), html.Br(),

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
                            'width': '15%'
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
                ), style={'padding-right': 60}
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
            ], width=1, style={'padding-left': 45})
        ]),
    ], style={'padding': 30})
    return layout