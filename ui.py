import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64

# Assuming you have your get_recommendations function defined

st.title("Travel Recommendation App")

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location:")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

# Call the recommendation function
def get_recommendations(location, hashtags_str):
    travel = pd.read_csv("image_dataset.csv")

    # Handle empty hashtags string
    if not hashtags_str:
        return []

    # Split the provided hashtags string into a list
    hashtags = hashtags_str.strip().split()

    # Filter the dataframe based on location (if provided)
    if location:
        filtered_df = travel[travel['location'] == location].copy()  # Make a copy of the filtered DataFrame
        if not filtered_df.empty:
            # Calculate hashtag similarity scores for filtered entries
            filtered_df['hashtag_sim_score'] = filtered_df['hashtag'].apply(
                lambda x: len(set(x.split()) & set(hashtags))
            )
            # Sort entries based on hashtag similarity score
            sorted_df = filtered_df.sort_values(by='hashtag_sim_score', ascending=False)
            # Get top 10 recommendations
            if 'image_title' in sorted_df.columns:  # Check if 'title' column exists
                recommendations = sorted_df[['location', 'hashtag', 'image_url', 'image_title']].head(10).to_dict('records')
            else:
                recommendations = sorted_df[['location', 'hashtag', 'image_url']].head(10).to_dict('records')
            return recommendations
    return []

base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_columns = 2
        num_rows = -(-num_recommendations // num_columns)  # Ceiling division to calculate number of rows needed
        for i in range(num_rows):
            st.write("<div style='display:flex;'>", unsafe_allow_html=True)
            for j in range(num_columns):
                index = i * num_columns + j
                if index < num_recommendations:
                    recommendation = recommendations[index]
                    try:
                        # Display the image from GitHub repository using the provided URL
                        image_url = recommendation['image_url']
                        # Modify the URL to the correct format
                        full_image_url = f"{base_github_url}/{image_url}"
                        # Change the URL to view raw content
                        full_image_url = full_image_url.replace("/blob/", "/raw/")
                        response = requests.get(full_image_url)
                        img = Image.open(BytesIO(response.content))
                        # Display image with expander for pop-up effect
                        st.write(f"<div style='margin-right:10px; margin-bottom: 10px;'><img src='data:image/jpeg;base64,{base64.b64encode(response.content).decode()}' style='width:250px; height:250px;'/><div>Location: {recommendation['location']}</div><div>Hashtag: {recommendation['hashtag']}</div></div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
            st.write("</div>", unsafe_allow_html=True)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
