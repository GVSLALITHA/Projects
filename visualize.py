import streamlit as st
import pandas as pd
import numpy as np
import re
import psycopg2
import plotly.express as px
import plotly.graph_objects as go



connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="movies",
    user="postgres",
    password="kamakshi@5"
)
# Function to convert "1h 42m" -> Minutes (eg : 102)
def convert_duration(duration_str):
    if pd.isna(duration_str) or duration_str == "None":
        return np.nan
    match = re.match(r'(\d+)h\s*(\d*)m?', duration_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return hours * 60 + minutes
    return np.nan

# Function to convert "5.5K" -> 5500
def convert_voting(vote_str):
    if pd.isna(vote_str) or vote_str in ["None", "", "nan", None]:
        return np.nan
    try:
        if "K" in vote_str:
            return float(vote_str.replace("K", "")) * 1000
        return float(vote_str)
    except ValueError:
        return np.nan

# Fetching data from TiDB Cloud
@st.cache_data
def fetch_data():
    query = "SELECT title, genre, duration, rating, voting FROM movies;"
    df = pd.read_sql(query, connection)

    # Apply transformations with correct column names
    df["duration"] = df["duration"].astype(str).apply(convert_duration).fillna(0)
    df["voting"] = df["voting"].astype(str).apply(convert_voting).fillna(0)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

    return df
movies_df = fetch_data()


# Sidebar Navigation
st.sidebar.title("MovieZone")
page = st.sidebar.radio("Go to", ["Movie Trends & Analysis - 2024", "Find Your Movie"])

if page == "Movie Trends & Analysis - 2024":
    st.title("🎬 IMDb 2024 Movies Analysis - Overall")
    
    # Top 10 Movies by Rating & Votes
    st.subheader("Top 10 Movies by Rating & Votes")
    top_movies = movies_df.sort_values(["rating", "voting"], ascending=[False, False]).head(10)
    st.dataframe(top_movies.reset_index(drop=True))
    
    # Genre Distribution
    st.subheader("Genre Distribution")
    genre_counts = movies_df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    st.plotly_chart(px.bar(genre_counts, x="genre", y="count", title="Number of Movies per Genre"))

    # Average Duration by Genre
    st.subheader("Average Duration by Genre")
    avg_duration = movies_df.groupby("genre")["duration"].mean().reset_index()
    st.plotly_chart(px.bar(avg_duration, x="duration", y="genre", orientation="h", title="Average Duration per Genre"))

    # Voting Trends by Genre
    st.subheader("Voting Trends by Genre")
    avg_voting = movies_df.groupby("genre")["voting"].mean().reset_index()
    st.plotly_chart(px.bar(avg_voting, x="genre", y="voting", title="Average Voting Counts per Genre"))

    # Rating Distribution
    st.subheader("Rating Distribution")
    st.plotly_chart(px.histogram(movies_df, x="rating", nbins=20, title="Rating Distribution of Movies"))

    # Top Rated Movie per Genre
    st.subheader("Top Rated Movie in Each Genre")
    top_per_genre = movies_df.loc[movies_df.groupby("genre")["rating"].idxmax()]
    st.dataframe(top_per_genre[["genre", "title", "rating"]].reset_index(drop=True))

    # Most Popular Genres by Voting
    st.subheader("Most Popular Genres by Voting")
    total_votes_by_genre = movies_df.groupby("genre")["voting"].sum().reset_index()
    st.plotly_chart(px.pie(total_votes_by_genre, names="genre", values="voting", title="Most Popular Genres by Voting"))


    # Filter out movies with valid durations (> 0)
    valid_movies = movies_df[movies_df["duration"] > 0]

    # Get the shortest and longest movies from valid entries
    shortest_movie = valid_movies.loc[valid_movies["duration"].idxmin()]
    longest_movie = valid_movies.loc[valid_movies["duration"].idxmax()]

    st.subheader("🎥 Shortest & Longest Movies")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Shortest Movie")
        st.markdown(f"**Title:** {shortest_movie['title']}")
        st.markdown(f"**Duration:** {shortest_movie['duration']} mins")
        st.markdown(f"**Rating:** {shortest_movie['rating']}")
        st.markdown(f"**Genre:** {shortest_movie['genre']}")
        st.markdown("---")

    with col2:
        st.markdown("###  Longest Movie")
        st.markdown(f"**Title:** {longest_movie['title']}")
        st.markdown(f"**Duration:** {longest_movie['duration']} mins")
        st.markdown(f"**Rating:**  {longest_movie['rating']}")
        st.markdown(f"**Genre:** {longest_movie['genre']}")
        st.markdown("---")


    
    # Ratings by Genre (Heatmap)
    st.subheader(" Ratings by Genre ")
    heatmap_data = movies_df.pivot_table(index="genre", values="rating", aggfunc="mean").reset_index()
    st.plotly_chart(px.imshow([heatmap_data["rating"]], labels=dict(x="Genre", y="Average Rating"), x=heatmap_data["genre"]))

    # Correlation Analysis
    st.subheader(" Correlation: Ratings vs Voting")
    st.plotly_chart(px.scatter(movies_df, x="voting", y="rating", title="Correlation Between Ratings & Voting Counts"))

elif page == "Find Your Movie":
    st.title(" Find Your Favorite Movies, Discover the Best! ")
    
    st.sidebar.header("Filters")
    selected_genre = st.sidebar.multiselect("Select Genre", movies_df["genre"].unique())
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0, 0.1)
    max_rating = st.sidebar.slider("Maximum Rating", 0.0, 10.0, 10.0, 0.1)
    min_votes = st.sidebar.slider("Minimum Votes", 0, int(movies_df["voting"].max()), 1000, 100)
    movie_search = st.sidebar.text_input("Search Movie Name")
    duration_filter = st.sidebar.radio("Select Duration:", ["All", "< 2 hrs", "2-3 hrs", "> 3 hrs"])
    filtered_df = movies_df[
        (movies_df["rating"] >= min_rating) &
        (movies_df["rating"] <= max_rating) &
        (movies_df["voting"] >= min_votes)
    ]
    if duration_filter == "< 2 hrs":
        filtered_df = filtered_df[filtered_df["duration"] < 120]
    elif duration_filter == "2-3 hrs":
        filtered_df = filtered_df[(filtered_df["duration"] >= 120) & (filtered_df["duration"] <= 180)]
    elif duration_filter == "> 3 hrs":
        filtered_df = filtered_df[filtered_df["duration"] > 180]
    if selected_genre:
        filtered_df = filtered_df[filtered_df["genre"].isin(selected_genre)]
    if movie_search:
        filtered_df = filtered_df[filtered_df["title"].str.contains(movie_search, case=False, na=False)]

        st.dataframe(filtered_df.reset_index(drop=True))

    if not filtered_df.empty:
        # Top 10 Movies by Rating & Votes
        st.subheader("Top 10 Movies by Rating & Votes")
        top_movies = filtered_df.sort_values(["rating", "voting"], ascending=[False, False]).head(10)
        st.dataframe(top_movies)

        # Genre Distribution
        st.subheader(" Genre Distribution ")
        genre_counts = filtered_df["genre"].value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]
        st.plotly_chart(px.bar(genre_counts, x="Genre", y="Count", title="Number of Movies per Genre "))

        # Average Duration by Genre
        st.subheader(" Average Duration by Genre ")
        avg_duration = filtered_df.groupby("genre")["duration"].mean().reset_index()
        st.plotly_chart(px.bar(avg_duration, x="duration", y="genre", orientation="h", title="Average Duration per Genre "))

        # Voting Trends by Genre
        st.subheader("Voting Trends ")
        avg_voting = filtered_df.groupby("genre")["voting"].mean().reset_index()
        st.plotly_chart(px.bar(avg_voting, x="genre", y="voting", title="Average Voting Counts per Genre "))

        # Rating Distribution
        st.subheader("Rating Distribution ")
        st.plotly_chart(px.histogram(filtered_df, x="rating", nbins=20, title="Rating Distribution of Movies"))

        # Top Rated Movie per Genre
        st.subheader("Top Rated Movie in Each Genre")
        top_per_genre = filtered_df.loc[filtered_df.groupby("genre")["rating"].idxmax()]
        st.dataframe(top_per_genre[["genre", "title", "rating"]])

        # Most Popular Genres by Voting
        st.subheader("Most Popular Genres by Voting ")
        total_votes_by_genre = filtered_df.groupby("genre")["voting"].sum().reset_index()
        st.plotly_chart(px.pie(total_votes_by_genre, names="genre", values="voting", title="Most Popular Genres by Voting "))

        # Shortest & Longest Movies
        valid_movies = filtered_df[filtered_df["duration"] > 0]
        if not valid_movies.empty:
            shortest_movie = valid_movies.loc[valid_movies["duration"].idxmin()]
            longest_movie = valid_movies.loc[valid_movies["duration"].idxmax()]

            st.subheader("Shortest & Longest Movies")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Shortest Movie")
                st.markdown(f"**Title:** {shortest_movie['title']}")
                st.markdown(f"**Duration:** {shortest_movie['duration']} mins")
                st.markdown(f"**Rating:** {shortest_movie['rating']}")
                st.markdown(f"**Genre:** {shortest_movie['genre']}")
                st.markdown("---")

            with col2:
                st.markdown("### Longest Movie")
                st.markdown(f"**Title:** {longest_movie['title']}")
                st.markdown(f"**Duration:**  {longest_movie['duration']} mins")
                st.markdown(f"**Rating:**  {longest_movie['rating']}")
                st.markdown(f"**Genre:** {longest_movie['genre']}")
                st.markdown("---")

        # Ratings by Genre (Heatmap)
        st.subheader(" Ratings by Genre ")
        heatmap_data = filtered_df.pivot_table(index="genre", values="rating", aggfunc="mean").reset_index()
        st.plotly_chart(px.imshow([heatmap_data["rating"]], labels=dict(x="Genre", y="Average Rating"), x=heatmap_data["genre"]))

        # Correlation Analysis
        st.subheader("Correlation: Ratings vs Voting ")
        st.plotly_chart(px.scatter(filtered_df, x="voting", y="rating", title="Correlation Between Ratings & Voting Counts "))
    else:
        st.warning("No movies match your filters. Try adjusting the filters.")