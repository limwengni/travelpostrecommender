import streamlit as st
import pandas as pd
import pickle
import requests
from PIL import Image
from io import BytesIO

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location (Optional):")
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

# Function to convert image to base64 format
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue())
    return encoded_img.decode('utf-8')

# Function to display the recommendations
def display_recommendations(recommendations):
    base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"
    for recommendation in recommendations:
        st.write(f"- {recommendation['location']}: {recommendation['hashtag']}")
        image_url = recommendation['image_url']
        full_image_url = f"{base_github_url}/{image_url}"
        full_image_url = full_image_url.replace("/blob/", "/raw/")
        try:
            response = requests.get(full_image_url)
            img = Image.open(BytesIO(response.content))
            # Convert image to base64
            img_base64 = image_to_base64(img)
            # Display the image with a link to the original image
            img_html = f'<a href="{full_image_url}" target="_blank"><img src="data:image/jpeg;base64,{img_base64}" style="width:250px; height:250px; margin-right:10px; margin-bottom: 10px"></a>'
            st.write(img_html, unsafe_allow_html=True)
        except Exception as e:
            st.write(f"Error loading image from URL: {full_image_url}")
            st.write(e)

# Streamlit app
st.title("Travel Recommendation App")
location = st.text_input("Enter Location:")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        display_recommendations(recommendations)
    else:
        st.write("No recommendations found based on your input.")
st.stop()
