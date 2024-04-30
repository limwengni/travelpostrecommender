import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

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

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        for recommendation in recommendations:
            try:
                # Display the image from GitHub repository using the provided URL
                image_url = recommendation['image_url']
                # Construct the full URL by appending the relative image path to the base URL
                base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"
                full_image_url = f"{base_github_url}/{image_url}"
                print("Full image URL:", full_image_url)
                response = requests.get(full_image_url)
                print("Response status code:", response.status_code)
                print("Response content type:", response.headers['Content-Type'])
                print("Response content:", response.content)
                img = Image.open(BytesIO(response.content))
                # Display image with pop-up effect on click
                if st.image(img, caption=recommendation['image_title'], use_column_width=True, clamp=True):
                    # Display additional details when image is clicked
                    st.write(f"Location: {recommendation['location']}")
                    st.write(f"Hashtag: {recommendation['hashtag']}")
            except Exception as e:
                st.write(f"Error loading image from URL: {full_image_url}")
                st.write(e)
    else:
        st.write("No recommendations found based on your input.")
