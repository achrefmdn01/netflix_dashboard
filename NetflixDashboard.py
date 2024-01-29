
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dateutil import parser

# Constants
DATA_PATH = r"C:\Users\achre\Desktop\DSpy\NetflixOriginals.csv"

# Load data
netflix_data = pd.read_csv(DATA_PATH, encoding='latin-1')

# Data cleaning and preparation
netflix_data.dropna(inplace=True)

# Convert 'Premiere' column to datetime with a specific format
netflix_data['Premiere'] = netflix_data['Premiere'].apply(lambda x: parser.parse(x).strftime('%d-%m-%Y'))

# Extract year and convert to integer
netflix_data['Premiere'] = pd.to_datetime(netflix_data['Premiere'], format='%d-%m-%Y', errors='coerce')
netflix_data['Year'] = netflix_data['Premiere'].dt.year.astype('Int64')
# Use 'Int64' type to handle NaNs

# Get unique years without NaN values
unique_years = netflix_data['Year'].dropna().unique()

def count_language(dataframe):
    # Initialize language counts
    language_counts = {}

    # Iterate through rows in the DataFrame
    for index, row in dataframe.iterrows():
        languages = row.get('Language', '').split('/')

        for language in languages:
            language = language.strip()  # Remove trailing spaces
            language_counts[language] = language_counts.get(language, 0) + 1

    return language_counts
def count_genre(dataframe):
    # Initialize genre counts
    genre_counts = {}

    # Iterate through rows in the DataFrame
    for index, row in dataframe.iterrows():
        genres = row.get('Genre', '').split('/')

        for genre in genres:
            genre = genre.strip()  # Remove leading/trailing spaces
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return genre_counts

# Error handling
def get_genre_stats(dataframe, genre, language):
    try:
        genre_data = dataframe[dataframe['Genre'] == genre]
        language_films = genre_data[genre_data['Language'].str.contains(language, case=False)]
        language_films_count = language_films.shape[0]
        avg_imdb_score = language_films['IMDB Score'].mean()
        return language_films_count , avg_imdb_score
    except KeyError:
        return None, None
def get_genre_top_films(dataframe, genre, language):
    try:
        genre_data = dataframe[(dataframe['Genre'] == genre) & (dataframe['Language'].str.contains(language, case=False))]
        top_films = genre_data[(genre_data['IMDB Score'] >= 1) & (genre_data['IMDB Score'] <= 10)]
        top_films_sorted = top_films.nlargest(10, 'IMDB Score')  # Get top 10 films by IMDB Score
        return top_films_sorted
    except KeyError:
        return None
st.markdown('<h1><span style="color:red">Netflix</span> <span style="color:black">Dashboard</span></h1>', unsafe_allow_html=True)
tabs = st.tabs(["Films Overview", "Language Distribution"])

#st.checkbox('Show  Data'):
   #st.write(netflix_data)
with tabs[0]:
    # Obtenir les genres distincts
    distinct_genres = list(count_genre(netflix_data).keys())
    distinct_languages = list(count_language(netflix_data).keys())

    # Sidebar
    selected_genre = st.selectbox("Choose Genre", distinct_genres, key='genre_selector')
    selected_language = st.selectbox("Choose Language", distinct_languages, key='language_selector')

    # Count of films and average IMDb score for Tab 1
    if not get_genre_stats(netflix_data, selected_genre, selected_language) is None:
        films_count, avg_score = get_genre_stats(netflix_data, selected_genre, selected_language)

        # st.write(f"There are {films_count} films in the '{selected_genre}' genre in '{selected_language}'.")
        # st.write(f"The average IMDb score of films in '{selected_genre}' genre and '{selected_language}' language is: {avg_score:.2f}")

  
    language_counts_tab1 = count_language(netflix_data)

    # Fetch top 10 films if 'Documentary' genre is selected
    if selected_genre == 'Documentary':
        top_films_documentary = get_genre_top_films(netflix_data, selected_genre, selected_language)

        # Bar chart for top 10 films
        fig, ax = plt.subplots(figsize=(16, 14))
        bars = ax.bar(top_films_documentary['Title'], top_films_documentary['IMDB Score'], color='Red', edgecolor='black')
        ax.set_xlabel('Film Title')
        ax.set_ylabel('IMDb Score')
        ax.set_title(f'Top 10 IMDb Scores of Films in {selected_genre} Genre and {selected_language} Language')
        plt.xticks(rotation=90)
        plt.legend([f'Top 10 {selected_genre} Genre - {selected_language} Language'])
        plt.tight_layout()
        st.pyplot(fig)
    else:
        fig, ax = plt.subplots(figsize=(16, 14))
        genre_data = netflix_data[netflix_data['Genre'] == selected_genre]
        language_films = genre_data[genre_data['Language'].str.contains(selected_language, case=False)]
        bars = ax.bar(language_films['Title'], language_films['IMDB Score'], color='Red', edgecolor='black')
        ax.set_xlabel('Film Title')
        ax.set_ylabel('IMDb Score')
        ax.set_title(f'IMDb Scores of Films in {selected_genre} Genre and {selected_language} Language')
        plt.xticks(rotation=90)
        plt.legend([f'{selected_genre} Genre - {selected_language} Language'])
        plt.tight_layout()
        st.pyplot(fig)


with tabs[1]:
    # Function to get unique years from 'Premiere' column
    unique_years = pd.to_datetime(netflix_data['Premiere']).dt.year.unique()
    selected_year = st.selectbox("Choose Year for Premiere", options=unique_years)

    # Filter data based on selected year
    language_data = netflix_data[pd.to_datetime(netflix_data['Premiere']).dt.year == selected_year]

    if not language_data.empty:
        # Calculate language counts for the selected year
        language_counts_tab2 = count_language(language_data)

        # Create a pie chart to display language distribution
        fig_pie, ax_pie = plt.subplots(figsize=(16, 16))
        ax_pie.pie(language_counts_tab2.values(), labels=language_counts_tab2.keys(), autopct='%1.1f%%')
        ax_pie.set_title(f'Language Distribution in {selected_year}')
        st.pyplot(fig_pie)
    else:
        st.write("No data available for the selected criter.")


st.sidebar.markdown('''
Created by Ashref Mednini.
''')
