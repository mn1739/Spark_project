from pyspark import SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import *
from pyspark.ml.recommendation import ALS
import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import webbrowser
import os
from pathlib import Path
os.chdir(Path(__file__).parent.absolute())
from app_layout import get_layout, generate_recos_list


# User ratings file
user_ratings_file = 'User Ratings.csv'
if os.path.isfile(user_ratings_file): user_ratings_df = pd.read_csv(user_ratings_file).to_dict('records')
else: user_ratings_df = [{'MOVIE': '', 'RATING': ''}]
if len(user_ratings_df) == 0: user_ratings_df = [{'MOVIE': '', 'RATING': ''}]


# Spark session
config = SparkConf()
config.setMaster('local[8]').setAppName('Movie Recommender')
spark = SparkSession.builder.config(conf=config).getOrCreate()

movies = spark.read.csv('ml-latest-small/movies.csv', header=True, inferSchema=True)
ratings = spark.read.csv('ml-latest-small/ratings.csv', header=True, inferSchema=True)

movies_dict = {}
movies_dict_reverse = {}
temp = movies.collect()
for row in temp: movies_dict[row['movieId']] = row['title']
for row in temp: movies_dict_reverse[row['title']] = row['movieId']

genres = []
for row in temp: genres += row['genres'].split('|')
genres = sorted(set(genres))
if '(no genres listed)' in genres: genres.remove('(no genres listed)')

movies = movies.withColumn('genres', expr("REPLACE(genres, '|', ', ') AS genres")) \
               .withColumn('year', expr("CAST(LEFT(RIGHT(title, 5), 4) AS INT)"))

ratings_count = ratings.groupby('movieId').count()
ratings = ratings.join(ratings_count, on='movieId').filter('count >= 25').drop('count', 'timestamp')


# ALS model
als = ALS(userCol='userId', itemCol='movieId', ratingCol='rating', nonnegative=True, coldStartStrategy='drop')

users = spark.createDataFrame([Row(userId=0)])
unique_movies = ratings.select('movieId').distinct().count()

def train_model(ratings, user_ratings, genres_selected, genres_excluded, years):
    model = als.fit(ratings)
    recos = model.recommendForUserSubset(users, unique_movies).withColumn("rec_exp", explode("recommendations")) \
                 .select(col("rec_exp.movieId"), col("rec_exp.rating")).join(movies, on='movieId').toPandas()
    watched = [x.movieId for x in user_ratings.select('movieId').distinct().collect()]
    recos = recos[~recos['movieId'].isin(watched)]
    if type(years) != str: recos = recos[(recos['year'] >= years[0]) & (recos['year'] <= years[-1])]
    if type(genres_selected) != str:
        genres_selected = set(genres_selected)
        for i, row in recos.iterrows():
            genres_list = row['genres'].split(', ')
            genre_set = genres_selected.intersection(set(genres_list))
            recos.loc[i, 'filter_1'] = len(genre_set) > 0
    if type(genres_excluded) != str:
        genres_excluded = set(genres_excluded)
        for i, row in recos.iterrows():
            genres_list = row['genres'].split(', ')
            genre_set = genres_excluded.intersection(set(genres_list))
            recos.loc[i, 'filter_2'] = len(genre_set) == 0
    return recos[(recos['filter_1']) & (recos['filter_2'])][['title', 'genres']].head(20)


# Dash app
app = Dash(title='Movie Recommender', update_title='Updating Recos...', prevent_initial_callbacks=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = get_layout(movies_dict, genres, user_ratings_file, user_ratings_df)

@app.callback(Output('user-ratings', 'data'),
              [Input('add-rating', 'n_clicks'),
               State('user-ratings', 'data'),
               State('select-movie', 'value'),
               State('rating', 'value')])
def update_user_ratings(n, rows, movie, rating):
    if type(n) == int:
        for row in rows:
            if row['MOVIE'] == '' and row['RATING'] == '': rows.remove(row)
            elif row['MOVIE'] == movies_dict[movie]: rows.remove(row)
        rows.append({'MOVIE': movies_dict[movie], 'RATING': rating})
    return rows

@app.callback(Output('toast', 'is_open'),
              [Input('save-ratings', 'n_clicks'),
               State('user-ratings', 'data')])
def save_user_ratings(n, rows):
    if type(n) == int:
        user_ratings_df = pd.DataFrame(rows).set_index('MOVIE')
        user_ratings_df.to_csv('User Ratings.csv')
    return True if type(n) == int else False

@app.callback(Output('recos-list', 'children'),
              [Input('run-model', 'n_clicks'),
               State('user-ratings', 'data'),
               State('select-genre', 'value'),
               State('exclude-genre', 'value'),
               State('time-period', 'value')])
def run_model(n, user_ratings, genres_selected, genres_excluded, years):
    if type(n) == int:
        user_ratings = pd.DataFrame(user_ratings).rename(columns={'MOVIE': 'movieId', 'RATING': 'rating'})
        user_ratings['userId'] = 0
        user_ratings['movieId'] = user_ratings['movieId'].map(movies_dict_reverse)
        user_ratings = spark.createDataFrame(user_ratings[['movieId', 'userId', 'rating']])
        ratings_mod = user_ratings.unionAll(ratings)
        if not genres_selected or len(genres_selected) == 0: genres_selected = ''
        if not genres_excluded or len(genres_excluded) == 0: genres_excluded = ''
        if not years or len(years) == 0: years = ''
        recos = train_model(ratings_mod, user_ratings, genres_selected, genres_excluded, years)
        return generate_recos_list(recos)

webbrowser.open('http://127.0.0.1:8050/')
app.run_server()