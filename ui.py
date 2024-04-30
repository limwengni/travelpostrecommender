import streamlit as st
import pandas as pd
import pickle
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
            recommendations = sorted_df[['location', 'hashtag', 'image_url']].head(10).to_dict('records')
            return recommendations
    return []

base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"


def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue())
    return encoded_img.decode('utf-8')


# Function to create a modal for a recommendation
def create_modal(recommendation):
    """
    Creates an HTML structure for a modal displaying recommendation details.

    Args:
        recommendation (dict): A dictionary containing recommendation details.

    Returns:
        str: The HTML string for the modal.
    """
    location = recommendation['location']
    hashtag = recommendation['hashtag']
    image_url = recommendation['image_url']

    # Modify the URL to the correct format
    full_image_url = f"{base_github_url}/{image_url}"
    full_image_url = full_image_url.replace("/blob/", "/raw/")

    try:
        response = requests.get(full_image_url)
        img = Image.open(BytesIO(response.content))
        img_base64 = image_to_base64(img)
    except Exception as e:
        st.write(f"Error loading image from URL: {full_image_url}")
        st.write(e)
        return ""

    modal_html = f"""
    <div class="modal fade" id="{location}-{hashtag}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">{location}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <img src="data:image/jpeg;base64,{img_base64}" class="img-fluid" alt="{location}">
            <p class="mt-3"><b>Hashtags:</b> {hashtag}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    """
    return modal_html


# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_rows = (num_recommendations + 2) // 3  # Calculate number of rows needed

        # Include Bootstrap CSS for modal styling
        st.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css" integrity="sha384-0evSXbVzTVFTJwgasCwqfyfCzuklaqHdQvCOuRL habOgQ6Lkvelz2Lvq8EVy19hN" crossorigin="anonymous">')

        for i in range(num_rows):
            row_html = "<div style='display:flex;'>"
            for j in range(3):
                index = i * 3 + j
                if index < num_recommendations:
                    recommendation = recommendations[index]

                    # Display image with a data-bs-toggle attribute for modal
                    image_url = recommendation['image_url']
                    # Modify the URL to the correct format
                    full_image_url = f"{base_github_url}/{image_url}"
                    full_image_url = full_image_url.replace("/blob/", "/raw/")
                    try:
                        response = requests.get(full_image_url)
                        img = Image.open(BytesIO(response.content))
                        width, height = img.size
                        padding = abs(width - height) // 2
                        if width < height:
                            img = img.crop((0, padding, width, height - padding))
                        else:
                            img = img.crop((padding, 0, width - padding, height))
                        img = img.resize((250, 250))
                        img_base64 = image_to_base64(img)
                        img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="width:250px; height:250px; margin-right:10px; margin-bottom: 10px;" data-bs-toggle="modal" data-bs-target="#{recommendation["location"]}-{recommendation["hashtag"]}">''
                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)
                        img_html = ""

                    row_html += img_html

                    # Create the modal content using the create_modal function
                    modal_content = create_modal(recommendation)

                    # Write both the image and modal content to the Streamlit app
                    row_html += modal_content

            row_html += "</div>"
            st.write(row_html, unsafe_allow_html=True)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
