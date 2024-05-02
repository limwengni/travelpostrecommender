import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Load travel posts data from CSV
travel_posts = pd.read_csv("image_dataset.csv", encoding='latin1')

def get_locations():
    return travel_posts["location"].unique()

def get_hashtags():
    hashtags = set()
    for tags in travel_posts["hashtag"]:
        hashtags.update(tags.split(", "))
    return sorted(list(hashtags))

def recommend_posts_hashtag(location, hashtags):
    # Handle empty hashtags
    if not hashtags:
        return pd.DataFrame()

    recommended_posts = []
    for _, post in travel_posts.iterrows():
        if location == post["location"]:
            common_hashtags = set(post["hashtag"].split(", ")) & set(hashtags)
            score = len(common_hashtags)
            if score > 0:
                post['score'] = score  # Add the score to the recommendation
                recommended_posts.append(post)

    return pd.DataFrame(recommended_posts)

def recommend_posts_knn(location, hashtag):
    # Replace this function with your KNN recommendation logic
    pass

st.title("Travel Recommendation App")

# Select recommendation algorithm
algorithm = st.selectbox("Select Recommendation Algorithm:", ["Hashtag-Based", "KNN-Based"])

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

# Display the recommendation button
if st.button("Recommend"):
    # Call the recommendation function based on selected algorithm
    if algorithm == "Hashtag-Based":
        recommendations = recommend_posts_hashtag(location, hashtags)
    else:
        recommendations = recommend_posts_knn(location, hashtags[0])  # Using the first hashtag for KNN

    # Check if recommendations are available
    if not recommendations.empty:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        
        # Calculate the number of rows and columns needed
        num_cols = 3
        num_rows = (num_recommendations + num_cols - 1) // num_cols

        # Create columns to display images
        cols = st.beta_columns(num_cols)
        for i in range(num_recommendations):
            col_index = i % num_cols
            col = cols[col_index]

            recommendation = recommendations.iloc[i]
            image_url = recommendation['image_url']
            full_image_url = f"https://github.com/limwengni/travelpostrecommender/raw/main/{image_url}"

            try:
                response = requests.get(full_image_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    col.image(img, caption=f"Location: {recommendation['location']}\nHashtag: #{recommendation['hashtag']}\nSimilarity Score: {recommendation['score']}", use_column_width=True)
            except Exception as e:
                st.write(f"Error loading image from URL: {full_image_url}")
                st.write(e)
    else:
        st.write("No recommendations found based on your input.")
