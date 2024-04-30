import streamlit as st
import pandas as pd

# Assuming you have your get_recommendations function defined

st.title("Travel Recommendation App")

# Get user input for location and hashtags (combined string)
location = st.text_input("Enter Location (Optional):")
hashtags_str = st.text_input("Enter Hashtags (e.g., cultural tours):")

travel = pd.read_csv("image_dataset.csv") 

# Remove commas from hashtags
travel['hashtag'] = travel['hashtag'].str.replace(',', '')

# Example: Access hashtags without commas for all entries (using a loop)
for index, row in travel.iterrows():
    clean_hashtag = row['hashtag']
    print(f"Index: {index}, Clean hashtag: {clean_hashtag}")

# Alternative: Access all hashtags as a list (optional)
all_clean_hashtags = travel['hashtag'].tolist()

def get_recommendations(location, hashtags_str):

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
  return []  # Return empty list if no recommendations found

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
