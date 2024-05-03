st.title("Travel Recommendation App")

# Select recommendation algorithm
algorithm = st.selectbox("Select Recommendation Algorithm:", ["Hashtag-Based", "KNN-Based"])

# Get user input for location and hashtags
location = st.selectbox("Select Location:", options=get_locations())
hashtags = st.multiselect("Select Hashtags:", options=get_hashtags())

# Display the recommendation button
if st.button("Recommend"):
    # Call the recommendation function based on the selected algorithm
    if algorithm == "Hashtag-Based":
        recommendations = recommend_posts_hashtag(location, hashtags)
    else:
        recommendations = recommend_posts_knn(location, hashtags[0])  # Using the first hashtag for KNN

    # Check if recommendations are available
    if not recommendations.empty:
        st.subheader("Recommendations:")
        num_recommendations = len(recommendations)
        num_columns = 3
        num_rows = (num_recommendations + num_columns - 1) // num_columns  # Calculate number of rows needed

        for i in range(num_rows):
            cols = st.columns(num_columns)
            for j in range(num_columns):
                index = i * num_columns + j
                if index < num_recommendations:
                    recommendation = recommendations.iloc[index]
                    # Display the image from GitHub repository using the provided URL
                    image_url = recommendation['image_url']
                    # Modify the URL to the correct format
                    full_image_url = f"https://github.com/limwengni/travelpostrecommender/raw/main/{image_url}"

                    try:
                        response = requests.get(full_image_url)
                        if response.status_code == 200:
                            # Display the image with title above
                            cols[j].markdown(f"<div style='text-align:center'><h2>{recommendation['image_title']}</h2></div>", unsafe_allow_html=True)
                            cols[j].image(full_image_url, caption=f"Similarity Score: {recommendation['score']}")

                            # Display location and hashtags in small boxes
                            cols[j].markdown(f"<div style='text-align:center; margin-top: 5px;'>"
                                        f"<div style='background-color: lightblue; padding: 5px; border-radius: 5px; margin-right: 10px; width: 150px; display:inline-block;'>{recommendation['location']}</div>"
                                        f"<div style='background-color: lightgreen; padding: 5px; border-radius: 5px; width: 150px; display:inline-block;'>{' '.join(['#' + tag for tag in recommendation['hashtag'].split(', ')])}</div>"
                                        f"</div>", unsafe_allow_html=True)

                    except Exception as e:
                        st.write(f"Error loading image from URL: {full_image_url}")
                        st.write(e)

    else:
        st.write("No recommendations found based on your input.")
