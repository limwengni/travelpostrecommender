import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin

# Load travel posts data from CSV
travel_posts = pd.read_csv("image_dataset.csv", encoding='latin1')

# Load feedback data from CSV
feedback_data = pd.read_csv("user_feedback.csv")

# Combine feedback data with existing dataset
combined_data = pd.concat([travel_posts, feedback_data])

class LocationHashtagEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoder = OneHotEncoder(handle_unknown='ignore')
        
    def fit(self, X, y=None):
        return self.encoder.fit(X[['location', 'hashtag']])
        
    def transform(self, X, y=None):
        return self.encoder.transform(X[['location', 'hashtag']])

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
    knn = joblib.load('knn_model.pkl')
    encoder = joblib.load('encoder.pkl')

    user_input_df = pd.DataFrame({
        'location': [location],
        'hashtag': [hashtag]
    })

    encoded_user_input = encoder.transform(user_input_df)

    distances, indices = knn.kneighbors(encoded_user_input)

    recommendations = combined_data.iloc[indices[0]].reset_index(drop=True)
    recommendations['score'] = 1 / (1 + distances[0])  # Adding score column
    return recommendations

def image_to_base64(image):
    buffered = BytesIO()
    image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    # Encode the bytes object to base64
    encoded_img = base64.b64encode(buffered.getvalue())
    # Convert the encoded bytes to a string
    return encoded_img.decode('utf-8')

st.title("Travel Recommendation App")

# Select recommendation algorithm
algorithm = st.selectbox("Select Recommendation Algorithm:", ["Hashtag-Based", "KNN-Based"])

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

# Call the recommendation function based on selected algorithm
if st.button("Recommend"):
    if algorithm == "Hashtag-Based":
        recommendations = recommend_posts_hashtag(location, hashtags)
    else:
        recommendations = recommend_posts_knn(location, hashtags[0])  # Using the first hashtag for KNN

    if not recommendations.empty:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed
        for i in range(num_rows):
            row_html = "<div style='display:flex;'>"
            for j in range(3):
                index = i * 3 + j
                if index < num_recommendations:
                    recommendation = recommendations.iloc[index]
                    # Display the image from GitHub repository using the provided URL
                    image_url = recommendation['image_url']
                    # Modify the URL to the correct format
                    full_image_url = f"https://github.com/limwengni/travelpostrecommender/raw/main/{image_url}"

                    try:
                        response = requests.get(full_image_url)
                        img = Image.open(BytesIO(response.content))
                        # Get image dimensions
                        width, height = img.size
                        # Calculate padding to make the image square
                        padding = abs(width - height) // 2
                        # Add padding to the shorter side
                        if width < height:
                            img = img.crop((0, padding, width, height - padding))
                        else:
                            img = img.crop((padding, 0, width - padding, height))
                        # Resize the image to 250x250
                        img = img.resize((250, 250))
                        # Convert the image to base64
                        img_base64 = image_to_base64(img)
                        # Create HTML for displaying image with image_title, location, hashtag, and similarity score
                        img_html = f"""
                        <div style="text-align:center; margin-right: 20px;">
                            <p style="font-weight:bold;">{recommendation['image_title']}</p>
                            <img src="data:image/jpeg;base64,{img_base64}" style="width:250px; height:250px; margin-bottom:10px;">
                            <p>Location: {recommendation['location']}</p>
                            <p>Hashtag: #{recommendation['hashtag']}</p>
                            <p>Similarity Score: {recommendation['score']}</p>
                        </div>
                        """
                        row_html += img_html
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
            row_html += "</div>"
            st.html(row_html)
    else:
        st.write("No recommendations found based on your input.")

# Collect feedback
feedback = st.radio("Was this recommendation helpful?", ("Yes", "No"))

# Store feedback along with the recommendations
if not recommendations.empty:
    if feedback == "Yes":
        recommendations["feedback"] = 1
    elif feedback == "No":
        recommendations["feedback"] = 0
    recommendations.to_csv("user_feedback.csv", mode="a", header=False)
    
st.stop()
