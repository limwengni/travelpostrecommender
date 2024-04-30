import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Sample get_recommendations function
def get_recommendations(location, hashtags_str):
    # Your recommendation logic here
    pass

st.title("Travel Recommendation App")

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location (Optional):")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed
        for i in range(num_rows):
            col1, col2, col3 = st.beta_columns(3)  # Create three columns for images
            for j in range(3):
                index = i * 3 + j
                if index < num_recommendations:
                    recommendation = recommendations[index]
                    with col1, col2, col3:
                        st.write(f"- {recommendation['location']}: {recommendation['hashtag']}")
                        # Display the image from GitHub repository using the provided URL
                        image_url = recommendation['image_url']
                        # Modify the URL to the correct format
                        full_image_url = f"{base_github_url}/{image_url}"
                        # Change the URL to view raw content
                        full_image_url = full_image_url.replace("/blob/", "/raw/")
                        try:
                            response = requests.get(full_image_url)
                            img = Image.open(BytesIO(response.content))
                            st.image(img, width=250)
                        except Exception as e:
                            st.write(f"Error loading image from URL: {full_image_url}")
                            st.write(e)
    else:
        st.write("No recommendations found based on your input.")
