import streamlit as st
import pandas as pd
import requests
from PIL import Image
import io

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
            return sorted_df[['location', 'hashtag', 'image_url', 'image_title']].to_dict('records')
    return []

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        # Define the number of images to display per row
        images_per_row = 3
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + images_per_row - 1) // images_per_row
        for i in range(num_rows):
            row_images = recommendations[i * images_per_row: (i + 1) * images_per_row]
            cols = st.columns(images_per_row)
            for j, col in enumerate(cols):
                if j < len(row_images):
                    recommendation = row_images[j]
                    try:
                        # Display the image from GitHub repository using the provided URL
                        image_url = recommendation['image_url']
                        # Modify the URL to the correct format
                        base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"
                        full_image_url = f"{base_github_url}/{image_url}"
                        response = requests.get(full_image_url)
                        if response.status_code == 200:
                            # Load the image directly from the response content
                            img = Image.open(io.BytesIO(response.content))
                            # Display image with pop-up effect on click
                            if col.image(img, caption=recommendation['image_title'], use_column_width=True, clamp=True):
                                # Display additional details when image is clicked
                                st.write(f"Location: {recommendation['location']}")
                                st.write(f"Hashtag: {recommendation['hashtag']}")
                        else:
                            st.write(f"Failed to fetch image from URL: {full_image_url}")
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
    else:
        st.write("No recommendations found based on your input.")
