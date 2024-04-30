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

# Function to display details in popout when image is clicked
def show_details(recommendation):
    st.write(f"Location: {recommendation['location']}")
    st.write(f"Hashtag: {recommendation['hashtag']}")
    st.write(f"Title: {recommendation['image_title']}")

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
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
                    # Display the image from GitHub repository using the provided URL
                    image_url = recommendation['image_url']
                    # Modify the URL to the correct format
                    base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"
                    full_image_url = f"{base_github_url}/{image_url}"
                    # Change the URL to view raw content
                    full_image_url = full_image_url.replace("/blob/", "/raw/")
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
                        # Display image with a click event to show popout details
                        if st.image(img, caption=recommendation['image_title'], use_column_width=True, clamp=True, 
                                     on_click=show_details, args=(recommendation,)):
                            pass
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
            row_html += "</div>"
            st.write(row_html, unsafe_allow_html=True)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
