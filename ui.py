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
            recommendations = sorted_df[['image_title', 'location', 'hashtag', 'image_url']].head(10).to_dict('records')
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

# Custom JavaScript function to enlarge images when clicked
def enlarge_image_on_click():
    return """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelectorAll(".enlarge-img").forEach(item => {
            item.addEventListener("click", event => {
                const imgSrc = event.target.getAttribute("src");
                const imgTitle = event.target.getAttribute("alt");
                const modalContent = `
                    <div style='text-align: center;'>
                        <img src='${imgSrc}' style='max-width: 80%; max-height: 80%;'>
                        <p>${imgTitle}</p>
                    </div>
                `;
                const modal = document.createElement("div");
                modal.innerHTML = modalContent;
                modal.style.cssText = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center;";
                modal.addEventListener("click", () => {
                    modal.remove();
                });
                document.body.appendChild(modal);
            });
        });
    });
    </script>
    """

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed
        for i in range(num_rows):
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
                        response = requests.get(full_image_url)
                        img = Image.open(BytesIO(response.content))
                        # Resize the image to 250x250
                        img = img.resize((250, 250))
                        # Convert the image to base64
                        img_base64 = image_to_base64(img)
                        # Create HTML for displaying image with image_title, location, and hashtag
                        img_html = f"""
                        <img class="enlarge-img" src="data:image/jpeg;base64,{img_base64}" alt="{recommendation['image_title']}" style="width:250px; height:250px; margin-right:10px; margin-bottom:10px; cursor:pointer;">
                        """
                        st.write(img_html, unsafe_allow_html=True)
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
        # Add JavaScript to the page to enable image enlargement on click
        st.write(enlarge_image_on_click(), unsafe_allow_html=True)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
