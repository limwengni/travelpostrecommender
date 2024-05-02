import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64

# Load travel posts data from CSV
travel_posts = pd.read_csv("image_dataset.csv")

def get_locations():
    return travel_posts["location"].unique()

def get_hashtags():
    hashtags = set()
    for tags in travel_posts["hashtag"]:
        hashtags.update(tags.split(", "))
    return sorted(list(hashtags))

def recommend_posts(location, hashtags):
    recommended_posts = []
    for _, post in travel_posts.iterrows():
        if location == post["location"] and set(hashtags).intersection(post["hashtag"].split(", ")):
            recommended_posts.append(post)
    return recommended_posts

st.title("Travel Recommendation App")

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

# Call the recommendation function
if st.button("Recommend"):
    recommendations = recommend_posts(location, hashtags)
    if recommendations:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed
        for i in range(num_rows):
            row_html = "<div style='display:flex;'>"
            for j in range(3):
                index = i * 3 + j
                if index < num_recommendations:
                    recommendation = recommendations[index]
                    # Display the image from URL
                    try:
                        response = requests.get(recommendation['image_url'])
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
                        img_base64 = base64.b64encode(BytesIO(response.content).read()).decode()
                        # Create HTML for displaying image with image_title, location, and hashtag
                        img_html = f"""
                        <div style="text-align:center; margin-right: 20px;">
                            <p style="font-weight:bold;">{recommendation['image_title']}</p>
                            <img src="data:image/jpeg;base64,{img_base64}" style="width:250px; height:250px; margin-bottom:10px;">
                            <p>Location: {recommendation['location']}</p>
                            <p>Hashtag: {recommendation['hashtag']}</p>
                        </div>
                        """
                        row_html += img_html
                    except Exception as e:
                        st.write(f"Error loading image from URL: {recommendation['image_url']}")
                        st.write(e)
            row_html += "</div>"
            st.markdown(row_html, unsafe_allow_html=True)
    else:
        st.write("No recommendations found based on your input.")
