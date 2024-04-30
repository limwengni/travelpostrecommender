import streamlit as st
import pandas as pd
import pickle
import requests
from PIL import Image
from io import BytesIO

# Assuming you have your get_recommendations function defined

st.title("Travel Recommendation App")

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location (Optional):")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

# Handle URL input (optional):
# if st.button("Submit URL"):
#    # Code to extract location and hashtags from URL (replace with your logic)
#    location = "..."  # Extracted location
#    hashtags_str = "..."  # Extracted hashtags

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

# Function to convert image to base64 format
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return b64encode(buffered.getvalue()).decode('utf-8')

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
            row = st.empty()  # Create an empty placeholder to display the row
            for j in range(3):
                index = i * 3 + j
                if index < num_recommendations:
                    recommendation = recommendations[index]
                    # Display the image from URL
                    image_url = recommendation['image_url']
                    try:
                        response = requests.get(image_url)
                        img = Image.open(BytesIO(response.content))
                        # Resize image to desired size (e.g., 250x250)
                        img.thumbnail((250, 250))
                        # Convert image to base64 format for display
                        img_base64 = image_to_base64(img)
                        # Display image in DataFrame
                        st.image(img, caption=recommendation['location'], use_column_width=True)
                    except Exception as e:
                        st.write(f"Error loading image from URL: {image_url}")
                        st.write(e)
            st.write("<br>", unsafe_allow_html=True)  # Add some space between rows

    else:
        st.write("No recommendations found based on your input.")
