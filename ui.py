import streamlit as st
import pandas as pd
import pickle
import requests
from PIL import Image
from io import BytesIO

# Assuming you have your get_recommendations function defined

st.title("Travel Recommendation App Test")

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location (Optional):")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

# Handle URL input (optional):
# if st.button("Submit URL"):
#    # Code to extract location and hashtags from URL (replace with your logic)
#    location = "..."  # Extracted location
#    hashtags_str = "..."  # Extracted hashtags

@st.cache(suppress_st_warning=True)
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
# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if not recommendations:
  st.write("No recommendations found based on your input.")
else:

  @st.cache(suppress_st_warning=True)
  def display_recommendation(recommendation, image_url):
    try:
      response = requests.get(image_url)
      img = Image.open(BytesIO(response.content))
      st.write(f"- {recommendation['location']}: {recommendation['hashtag']}")
      st.image(img, width=250)
    except Exception as e:
      st.write(f"Error loading image from URL: {image_url}")
      st.write(e)

  st.subheader("Recommendations:")
  num_recommendations = len(recommendations)
  num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed
  for i in range(num_rows):
    for j in range(3):
      index = i * 3 + j
      if index < num_recommendations:
        recommendation = recommendations[index]
        image_url = recommendation['image_url']
        # Call cached function
        display_recommendation(recommendation, image_url)
