import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64

# Load travel posts data from CSV
travel_posts = pd.read_csv("image_dataset.csv")

def get_locations():
    return travel_posts["location"].unique()

def get_hashtags():
    hashtags = set()
    for tags in travel_posts["hashtag"]:
        hashtags.update(tags.split(", "))
    return sorted(list(hashtags))

def recommend_posts(location, hashtags):
    recommended_posts = []
    for _, post in travel_posts.iterrows():
        if location == post["location"] and set(hashtags).intersection(post["hashtag"].split(", ")):
            recommended_posts.append(post)
    return recommended_posts

st.title("Travel Recommendation App")

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"

def image_to_base64(image):
    buffered = BytesIO()
    image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    # Encode the bytes object to base64
    encoded_img = base64.b64encode(buffered.getvalue())
    # Convert the encoded bytes to a string
    return encoded_img.decode('utf-8')

# Call the recommendation function
if st.button("Recommend"):
    recommendations = recommend_posts(location, hashtags)
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
                    full_image_url = f"{base_github_url}/{image_url}"
                    # Change the URL to view raw content
                    full_image_url = full_image_url.replace("/blob/", "/raw/")

                    try:
                        response = requests.get(recommendation['full_image_url'])
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
                        # Convert the image to base64
                        img_base64 = image_to_base64(img)
                        # Create HTML for displaying image with image_title, location, and hashtag
                        img_html = f"""
                        <div style="text-align:center; margin-right: 20px;">
                            <p style="font-weight:bold;">{recommendation['image_title']}</p>
                            <img src="data:image/jpeg;base64,{img_base64}" style="width:250px; height:250px; margin-bottom:10px;">
                            <p>Location: {recommendation['location']}</p>
                            <p>Hashtag: #{recommendation['hashtag']}</p>
                        </div>
                        """
                        row_html += img_html
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
            row_html += "</div>"
            st.html(row_html)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
