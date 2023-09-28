# -*- coding: utf-8 -*-
"""IMDb Games Recommender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TaV389ocipGZN-V2b80ZdBfcOVGZ9ppZ

# Data Understanding
"""

# install kaggle
import requests
URL = "https://raw.githubusercontent.com/rezaafaisal/source/main/kaggle.json"
response = requests.get(URL)
open("kaggle.json", "wb").write(response.content)

!ls -lha kaggle.json
!pip install -q kaggle
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# unduh dataset
!kaggle datasets download -d lorentzyeung/imdb-video-games-dataset

# import library yang digunakan
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import  OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

# extrak dataset
shutil.unpack_archive('/content/imdb-video-games-dataset.zip', 'dataset')

# load dataset
games_df = pd.read_csv('/content/dataset/imdb_video_games.csv')

# jumlah data
row_len, col_len = games_df.shape
print(f"Jumlah baris : {row_len}\nJumlah Kolom : {col_len}")

games_df.head()

"""# Exploratory Data Analysis"""

games_df.info()

games_df.describe()

# cek fitur genre
print(f"Jumlah genre kombinasi unik : {games_df['Genre'].nunique()}")

genres = games_df['Genre'].str.split(',').explode()

print('Jumlah genre game: ', len(genres.unique()))

plt.figure(figsize=(6,3))
genres.value_counts(ascending=True)[-10:].plot(kind='barh')
plt.show()

# mengecek 10 genre paling banyak dan paling sedikit
genre_count = games_df['Genre'].value_counts(ascending=True)[-10:]
percent = 100*games_df['Genre'].value_counts(normalize=True)

print(tabulate(
    pd.DataFrame({
        'count' : genre_count[:10],
        'percent': percent[:10]
    }),
    headers=['Genre', 'Count', 'Percent']))

plt.figure(figsize=(6,3))
genre_count.plot(kind='barh', title='Genre of Games')
plt.show()

# mengecek fitur Certificate

certificate_count = games_df['Certificate'].value_counts(ascending=True)[-10:]

certificate_count.plot(kind='barh')
plt.show()

sns.lineplot(data=games_df, x='Year', y='User Rating')
plt.title('Game Rate by Year')
plt.show()

"""# Data Preprocessing"""

def slugify(text):
  return text.replace(' ', '_').lower()

# mengambil fitur yang akan digunakan
features = ['Title', 'Genre', 'User Rating', 'Number of Votes', 'Year']

new_df = pd.DataFrame()

for feature in features:
  new_df[slugify(feature)] = games_df[feature]

new_df.head()

new_df.info()

# cek missing value
new_df.isna().sum()

# cek duplicate
new_df.duplicated().sum()

# menghapus missing value
game_clean_df = new_df.dropna()

# menghapus data duplicate
game_clean_df = game_clean_df.drop_duplicates()

# cek mising value dan duplikat
print(f"Jumlah missing value : \n{game_clean_df.isna().sum()}")
print(f"Jumlah duplikat : {game_clean_df.duplicated().sum()}")

# ubah tipe data number_of_votes ke integer
game_clean_df['number_of_votes'] = game_clean_df['number_of_votes'].str.replace(',', '').astype(int)

game_clean_df['number_of_votes'].sample(5)

# cek dataframe
game_clean_df.head()

"""# Data Preparation"""

# mengecek jumlah game
print(f"Jumlah game dengan nama unik : {game_clean_df.title.nunique()}")

# mengecek jumlah genre yang memiliki kombinasi unik
print(f"Jumlah genre dengan kombinasi unik : {game_clean_df.genre.nunique()}")

# menambahkan kolom sesuai nama genre
game_clean_df['genre'] = game_clean_df['genre'].str.split(',')

for index, data in game_clean_df.iterrows():
  for genre in data['genre']:
    game_clean_df.at[index, genre.lower()] = 1

game_clean_df = game_clean_df.fillna(0)

game_clean_df.head()

# mengambil matriks genre
genre_matrix = game_clean_df.loc[:, 'action':]
genre_matrix.sample(5)

"""# Model Development"""

data = game_clean_df

# hitung cosine similarity pada matrix genre
cosine_sim = cosine_similarity(genre_matrix)
print(cosine_sim)

# membuat dataframe dari varible cosine similarity dengan baris dan kolom berupa nama game
cosine_sim_df = pd.DataFrame(cosine_sim, index=data['title'], columns=data['title'])

print(cosine_sim_df.shape)

# melihat similarity matrik
cosine_sim_df.sample(5, axis=1).sample(10, axis=0)

# fungsi mencetak rekomendasi
def display_recommendation(by, data, k):
  data = data.loc[:, :'year']
  columns = data.columns
  closest = data.sort_values(by=by, ascending=False).head(k)
  print(f"Reccomendation by {by}")
  print(tabulate(closest.set_index('title'), headers=columns))
  print("\n")


# membuat fungsi mendapatkan rekomendasi
def game_recommendations(name, similarity_data=cosine_sim_df, items=data, k=5):
  # Mengambil data dengan menggunakan argpartition untuk melakukan partisi secara tidak langsung sepanjang sumbu yang diberikan
  # Dataframe diubah menjadi numpy
  # Range(start, stop, step)
  index = similarity_data.loc[:, name].to_numpy().argpartition(range(-1, -k, -1))

  # Mengambil 50 data dengan similarity terbesar dari index yang ada
  closest = similarity_data.iloc[index[-1:-(50):-1]][name]

  # Drop nama_resto agar nama resto yang dicari tidak muncul dalam daftar rekomendasi
  closest = closest.drop(name, errors='ignore')

  # buat df baru untuk mengurutkan berdasrkan (genre, rating), (genre, tahun terbaru), (genre, jumlah pemain / jumlah vote)
  closest_df = pd.DataFrame(closest).merge(data, on='title').rename({name: 'cosine_similarity'}, axis=1)

  display_recommendation('user_rating', closest_df, k)
  display_recommendation('number_of_votes', closest_df, k)
  display_recommendation('year', closest_df, k)

# list nama game untuk meminta rekomendasi
game_clean_df[['title', 'genre']].sample(10)

# mendapatkan rekomendasi game
game_recommendations('Chiller') # genre : actian, horror