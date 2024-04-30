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
            recommendations = sorted_df[['location', 'hashtag', 'image_url', 'image_title']].head(10).to_dict('records')
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
        image_url = recommendation['image_url']
        # Modify the URL to the correct format (same logic as before)
        full_image_url = f"{base_github_url}/{image_url}".replace("/blob/", "/raw/")
        try:
            response = requests.get(full_image_url)
            img = Image.open(BytesIO(response.content))
            img_base64 = image_to_base64(img)
            # Use Streamlit components
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(img_base64, width=250, height=250)
            with col2:
                st.write(f"Title: {recommendation['image_title']}")
                st.write(f"Location: {recommendation['location']}")
            with col3:
                st.write(f"Hashtag: {recommendation['hashtag']}")
        except Exception as e:
            st.write(f"Error loading image from URL: {full_image_url}")
            st.write(e)
            row_html += "</div>"
            st.markdown(row_html, unsafe_allow_html=True)

def showDetails(title, location, hashtag, image_url):
    st.write(f"Title: {title}")
    st.write(f"Location: {location}")
    st.write(f"Hashtag: {hashtag}")
    st.image(image_url, use_column_width=True)
