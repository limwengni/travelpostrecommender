import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import base64
import os
import tempfile

# Load travel posts data from CSV
travel_posts = pd.read_csv("image_dataset.csv", encoding='latin1')

def get_locations():
    return travel_posts["location"].unique()

def get_hashtags():
    hashtags = set()
    for tags in travel_posts["hashtag"]:
        hashtags.update(tags.split(", "))
    return sorted(list(hashtags))

def recommend_posts_hashtag(location, hashtags):
    # Handle empty hashtags
    if not hashtags:
        return pd.DataFrame()

    recommended_posts = []
    for _, post in travel_posts.iterrows():
        if location == post["location"]:
            common_hashtags = set(post["hashtag"].split(", ")) & set(hashtags)
            score = len(common_hashtags)
            if score > 0:
                post['score'] = score  # Add the score to the recommendation
                recommended_posts.append(post)

    return pd.DataFrame(recommended_posts)

def recommend_posts_knn(location, hashtag):
    encoder = OneHotEncoder(handle_unknown='ignore')
    encoded_features = encoder.fit_transform(travel_posts[['location', 'hashtag']])
    knn = NearestNeighbors(n_neighbors=10, algorithm='auto').fit(encoded_features)

    user_input_df = pd.DataFrame({
        'location': [location],
        'hashtag': [hashtag]
    })

    encoded_user_input = encoder.transform(user_input_df)

    distances, indices = knn.kneighbors(encoded_user_input)

    recommendations = travel_posts.iloc[indices[0]].reset_index(drop=True)
    recommendations['score'] = 1 / (1 + distances[0])  # Adding score column
    return recommendations

def image_to_base64(image):
    buffered = BytesIO()
    image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    # Encode the bytes object to base64
    encoded_img = base64.b64encode(buffered.getvalue())
    # Convert the encoded bytes to a string
    return encoded_img.decode('utf-8')

def crop_image(image, crop_box):
    width, height = image.size
    left, top, right, bottom = crop_box

    # Convert percentage to pixels
    left = int(left * width)
    top = int(top * height)
    right = int(right * width)
    bottom = int(bottom * height)

    # Crop image
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image

def display_cropped_image(image, crop_box):
    cropped_image = crop_image(image, crop_box)
    st.image(cropped_image, caption="Cropped Image", use_column_width=True)

def get_cropped_image(image_url, crop_box):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        cropped_image = crop_image(image, crop_box)
        return cropped_image
    else:
        return None

def save_cropped_image(image_url, crop_box):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        cropped_image = crop_image(image, crop_box)

        # Save cropped image
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "cropped_image.jpg")
        cropped_image.save(temp_file_path)
        return temp_file_path
    else:
        return None

st.title("Travel Recommendation App")

# Select recommendation algorithm
algorithm = st.selectbox("Select Recommendation Algorithm:", ["Hashtag-Based", "KNN-Based"])

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

# Display the recommendation button
if st.button("Recommend"):
    # Call the recommendation function based on selected algorithm
    if algorithm == "Hashtag-Based":
        recommendations = recommend_posts_hashtag(location, hashtags)
    else:
        recommendations = recommend_posts_knn(location, hashtags[0])  # Using the first hashtag for KNN

    # Check if recommendations are available
    if not recommendations.empty:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)

        for index, recommendation in recommendations.iterrows():
            st.markdown(f"## {recommendation['image_title']}")
            st.write(f"Location: {recommendation['location']}")
            st.write(f"Hashtags: {recommendation['hashtag']}")

            # Display the image from GitHub repository using the provided URL
            image_url = f"https://github.com/limwengni/travelpostrecommender/raw/main/{recommendation['image_url']}"
            response = requests.get(image_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="Original Image", use_column_width=True)

                # Cropper.js for interactive image cropping
                st.write("<h3>Crop Image</h3>", unsafe_allow_html=True)
                st.write(
                    f'<img id="cropped-image" src="{image_url}" alt="Original Image">'
                    '<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.js"></script>'
                    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.css">'
                    '<script>'
                    'window.addEventListener("DOMContentLoaded", () => {'
                    'const image = document.getElementById("cropped-image");'
                    'const cropper = new Cropper(image, {'
                    'aspectRatio: 1 / 1,'
                    'crop(event) {'
                    'const cropData = cropper.getData();'
                    'const cropBoxData = cropper.getCropBoxData();'
                    'const message = `Crop area: ${cropData.width}px × ${cropData.height}px`;'
                    'const cropBoxMessage = `Crop box size: ${cropBoxData.width}px × ${cropBoxData.height}px`;'
                    'console.log(message);'
                    'console.log(cropBoxMessage);'
                    'window.parent.postMessage(cropData, "*");'
                    'window.parent.postMessage(cropBoxData, "*");'
                    '},'
                    '});'
                    '});'
                    '</script>',
                    unsafe_allow_html=True
                )

                crop_box_data = st.experimental_get_query_params()["cropData"]
                crop_box = (crop_box_data["left"], crop_box_data["top"], crop_box_data["width"], crop_box_data["height"])

                # Display the cropped image
                cropped_image = get_cropped_image(image_url, crop_box)
                if cropped_image:
                    st.image(cropped_image, caption="Cropped Image", use_column_width=True)
                    # Save the cropped image
                    save_button = st.button("Save Cropped Image")
                    if save_button:
                        temp_file_path = save_cropped_image(image_url, crop_box)
                        st.success(f"Saved cropped image to: {temp_file_path}")
                else:
                    st.warning("Failed to crop the image.")
            else:
                st.warning(f"Failed to load the image from URL: {image_url}")

    else:
        st.write("No recommendations found based on your input.")
