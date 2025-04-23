import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine

# Connect to MySQL database
def get_connection():
    user = '2jJrpvjwrA9Wt2x.root'
    password = '0ZT6EVmzzpAYMnUB'
    host = 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
    port = '4000'
    database = 'Guvi_imdb_project'
    engine = create_engine("mysql+mysqlconnector://2jJrpvjwrA9Wt2x.root:0ZT6EVmzzpAYMnUB@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/Guvi_imdb_project")
    return engine

def load_data():
    try:
        engine = get_connection()
        query = "SELECT * FROM table_movies"  # Adjust to your actual table/fields
        df = pd.read_sql(query, engine)
        df['Duration_hours'] = df['Duration'] / 60
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails
    
df= load_data()

st.set_page_config(layout="wide")
st.title("🎬 IMDb 2024 Movie Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Filter Movies")

# Genre filter
genres = df["Genre"].dropna().unique().tolist()
selected_genres = st.sidebar.multiselect("Select Genres", genres, default=genres)

# Rating filter
min_rating = float(df["Rating"].min())
max_rating = float(df["Rating"].max())
rating_range = st.sidebar.slider("IMDb Rating", min_rating, max_rating, (min_rating, max_rating), step=0.1)

# Votes filter
min_votes = int(df["Votes"].min())
max_votes = int(df["Votes"].max())
votes_range = st.sidebar.slider("Vote Count", min_votes, max_votes, (min_votes, max_votes), step=100)

# Duration filter
min_duration = int(df["Duration"].min())
max_duration = int(df["Duration"].max())
duration_range = st.sidebar.slider("Duration (minutes)", min_duration, max_duration, (min_duration, max_duration), step=10)

# Apply all filters
filtered_df = df[
    (df["Genre"].isin(selected_genres)) &
    (df["Rating"] >= rating_range[0]) & (df["Rating"] <= rating_range[1]) &
    (df["Votes"] >= votes_range[0]) & (df["Votes"] <= votes_range[1]) &
    (df["Duration"] >= duration_range[0]) & (df["Duration"] <= duration_range[1])
]

# --- Top 10 Movies by Rating and Votes ---
st.subheader("⭐ Top 10 Movies by Rating & Voting Count")
top_movies = filtered_df.sort_values(by=["Rating", "Votes"], ascending=False).head(10)
st.dataframe(top_movies[["Title", "Genre", "Rating", "Votes", "Duration"]])

# --- Genre Distribution (Bar Chart) ---
st.subheader("📊 Genre Distribution")
genre_counts = filtered_df["Genre"].value_counts()
st.bar_chart(genre_counts)

# --- Average Duration by Genre ---
st.subheader("⏱️ Average Duration by Genre")
avg_duration = filtered_df.groupby("Genre")["Duration"].mean().sort_values()
fig1, ax1 = plt.subplots()
sns.barplot(x=avg_duration.values, y=avg_duration.index, ax=ax1, palette="coolwarm")
ax1.set_xlabel("Average Duration (min)")
ax1.set_ylabel("Genre")
st.pyplot(fig1)

# --- Average Voting by Genre ---
st.subheader("📈 Voting Trends by Genre")
avg_votes = filtered_df.groupby("Genre")["Votes"].mean().sort_values()
fig2, ax2 = plt.subplots()
sns.barplot(x=avg_votes.values, y=avg_votes.index, ax=ax2, palette="viridis")
ax2.set_xlabel("Average Votes")
ax2.set_ylabel("Genre")
st.pyplot(fig2)

# --- Rating Distribution (Histogram) ---
st.subheader("🔸 Rating Distribution")
fig3, ax3 = plt.subplots()
sns.histplot(filtered_df["Rating"], bins=20, kde=True, ax=ax3, color="orange")
ax3.set_xlabel("Rating")
st.pyplot(fig3)

# --- Genre-Based Rating Leaders ---
st.subheader("🏆 Top-Rated Movie per Genre")
top_rated_by_genre = filtered_df.loc[filtered_df.groupby("Genre")["Rating"].idxmax()]
st.dataframe(top_rated_by_genre[["Genre", "Title", "Rating", "Votes"]])

# --- Most Popular Genres by Voting (Pie Chart) ---
st.subheader("🥧 Most Popular Genres by Total Votes")
votes_by_genre = filtered_df.groupby("Genre")["Votes"].sum().sort_values(ascending=False)
fig4, ax4 = plt.subplots()
ax4.pie(votes_by_genre, labels=votes_by_genre.index, autopct='%1.1f%%', startangle=90)
ax4.axis("equal")
st.pyplot(fig4)

# --- Duration Extremes ---
st.subheader("⏱️ Duration Extremes")
shortest = filtered_df.loc[filtered_df["Duration"].idxmin()]
longest = filtered_df.loc[filtered_df["Duration"].idxmax()]
col1, col2 = st.columns(2)
with col1:
    st.metric(label="🎬 Shortest Movie", value=shortest["Title"], delta=f"{shortest['Duration']} min")
with col2:
    st.metric(label="🎬 Longest Movie", value=longest["Title"], delta=f"{longest['Duration']} min")

# --- Ratings by Genre (Heatmap) ---
st.subheader("🌡️ Average Ratings by Genre (Heatmap)")
heatmap_df = filtered_df.groupby("Genre")[["Rating"]].mean().sort_values("Rating", ascending=False)
fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_df, annot=True, cmap="YlGnBu", ax=ax5)
st.pyplot(fig5)

# --- Correlation Analysis: Votes vs Rating ---
st.subheader("📉 Correlation: Ratings vs Voting Count")
fig6, ax6 = plt.subplots()
sns.scatterplot(data=filtered_df, x="Votes", y="Rating", hue="Genre", alpha=0.7, ax=ax6)
ax6.set_xscale("log")
st.pyplot(fig6)
