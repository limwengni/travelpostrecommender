base_github_url = "https://github.com/limwengni/travelpostrecommender/blob/main"
if st.button("Recommend"):
    # Print recommendations if any
    recommendations = get_recommendations(location, hashtags_str)
    if recommendations:
        st.subheader("Recommendations:")
        col1, col2, col3 = st.beta_columns(3)  # Create three columns for images
        for i, recommendation in enumerate(recommendations):
            if i % 3 == 0:
                col1, col2, col3 = st.beta_columns(3)  # Reset columns for every three images
            with col1, col2, col3:
                st.write(f"- {recommendation['location']}: {recommendation['hashtag']}")
                # Display the image from GitHub repository using the provided URL
                image_url = recommendation['image_url']
                # Modify the URL to the correct format
                full_image_url = f"{base_github_url}/{image_url}"
                # Change the URL to view raw content
                full_image_url = full_image_url.replace("/blob/", "/raw/")
                try:
                    response = requests.get(full_image_url)
                    img = Image.open(BytesIO(response.content))
                    st.image(img, width=250)
                except Exception as e:
                    st.write(f"Error loading image from URL: {full_image_url}")
                    st.write(e)
    else:
        st.write("No recommendations found based on your input.")
st.stop()
