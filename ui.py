import streamlit as st
import pandas as pd
import pickle
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
            recommendations = sorted_df[['location', 'hashtag', 'image_url']].head(10).to_dict('records')
            return recommendations
    return []

base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    # Encode the bytes object to base64
    encoded_img = base64.b64encode(buffered.getvalue())
    # Convert the encoded bytes to a string
    return encoded_img.decode('utf-8')

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        for recommendation in recommendations:
            # Display the image from GitHub repository using the provided URL
            image_url = recommendation['image_url']
            # Modify the URL to the correct format
            full_image_url = f"{base_github_url}/{image_url}"
            # Change the URL to view raw content
            full_image_url = full_image_url.replace("/blob/", "/raw/")
            try:
                response = requests.get(full_image_url)
                img = Image.open(BytesIO(response.content))
                # Display the image thumbnail
                st.image(img, caption=f"{recommendation['location']}: {recommendation['hashtag']}", width=250, use_column_width=False)
                # Check if image is clicked
                if st.image_clicked(img):
                    # Display the original size image
                    st.image(img, caption=f"{recommendation['location']}: {recommendation['hashtag']}")
            except Exception as e:
                st.write(f"Error loading image from URL: {full_image_url}")
                st.write(e)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
