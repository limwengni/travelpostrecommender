import streamlit as st
import pandas as pd
from Assignment import get_recommendations

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
recommendations = get_recommendations(location, hashtags_str)

# Print recommendations if any
if recommendations:
  st.subheader("Recommendations:")
  for recommendation in recommendations:
    st.write(f"- {recommendation['location']}: {recommendation['hashtag']}")
    if 'image_url' in recommendation:  # Check if image_url exists
      st.image(recommendation['image_url'], width=250)  # Display image with width adjustment
  else:
    st.write("No recommendations found based on your input.")

st.stop()
