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
            recommendations = sorted_df[['location', 'hashtag', 'image_url', 'image_title']].head(10).to_dict('records')
            return recommendations
    return []

base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"

# Call the recommendation function
if st.button("Recommend"):
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        for recommendation in recommendations:
            try:
                # Display the image from GitHub repository using the provided URL
                image_url = recommendation['image_url']
                # Modify the URL to the correct format
                full_image_url = f"{base_github_url}/{image_url}"
                # Change the URL to view raw content
                full_image_url = full_image_url.replace("/blob/", "/raw/")
                response = requests.get(full_image_url)
                img = Image.open(BytesIO(response.content))
                # Convert image to base64
                img_base64 = Image.open(BytesIO(response.content)).convert("RGBA")
                img_pil = Image.new("RGBA", img_base64.size)
                img_pil.paste(img_base64, (0, 0), img_base64)
                img_byte_arr = BytesIO()
                img_pil.save(img_byte_arr, format="PNG")
                img_base64_encoded = base64.b64encode(img_byte_arr.getvalue()).decode()

                # Create HTML to display image with details in a pop-up on click
                # Create HTML to display image with details in a pop-up on click
html_code = f"""
<div onclick="showDetails('{recommendation['image_title']}', '{recommendation['location']}', '{recommendation['hashtag']}', '{img_base64_encoded}')" style="cursor: pointer;">
    <img src="data:image/png;base64,{img_base64_encoded}" style="width:250px; height:250px; margin-right:10px; margin-bottom: 10px">
</div>
<script>
    function showDetails(title, location, hashtag, image) {{
        var modal = document.createElement('div');
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '9999';
        modal.innerHTML = `
            <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 80%; max-height: 80%;">
                <h3>Title: ${title}</h3>
                <p>Location: ${location}</p>
                <p>Hashtag: ${hashtag}</p>
                <img src="data:image/png;base64,${image}" style="max-width: 100%; max-height: 300px;">
                <button onclick="closeModal()">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        function closeModal() {{
            document.body.removeChild(modal);
        }}
    }}
</script>
"""

                st.write(html_code, unsafe_allow_html=True)
            except Exception as e:
                st.write(f"Error loading image from URL: {full_image_url}")
                st.write(e)
    else:
        st.write("No recommendations found based on your input.")

st.stop()
