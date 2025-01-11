import streamlit as st
from utils.db import get_downloaded_restaurants
import folium
from streamlit_folium import folium_static

def map_page():
    df = get_downloaded_restaurants()
    st.title("Carte des restaurants")
    # Create a map centered around the average location
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12, tiles='cartodb positron')

    # Define a function to get color based on average review
    def get_color(avg_review):
        if (avg_review >= 4):
            return 'green'
        elif (avg_review >= 3):
            return 'orange'
        else:
            return 'red'

    # Add markers to the map
    for _, row in df.iterrows():
        popup_content = f"""
        <div>
            <h4>{row['restaurant_name']}</h4>
            <p><strong>Address:</strong> {row['address']}</p>
            <p><strong>Average Review:</strong> {row['restaurant_avg_review']}</p>
            <p><strong>Number of Reviews:</strong> {row['restaurant_total_reviews']}</p>
            <p><strong>Price:</strong> {row['restaurant_price']}</p>
            <p><a href="https://www.tripadvisor.fr/{row['restaurant_url']}" target="_blank">Visit on TripAdvisor</a></p>
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=get_color(row['restaurant_avg_review']))
        ).add_to(m)

    # Display the map
    folium_static(m)
    # Display restaurant information in a grid format
    cols = st.columns(3)
    for idx, row in df.iterrows():
        col = cols[idx % 3]
        with col:
            col.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 10px 0;">
                <h4>{row['restaurant_name']}</h4>
                <div style="display: flex; justify-content: space-between;">
                    <div style="background-color: {get_color(row['restaurant_avg_review'])}; color: white; padding: 5px; border-radius: 5px; text-align: center; flex: 1; margin-right: 5px;">
                        {row['restaurant_avg_review']}
                    </div>
                    <div style="background-color: grey; color: white; padding: 5px; border-radius: 5px; text-align: center; flex: 1; margin-right: 5px;">
                        {row['restaurant_total_reviews']}
                    </div>
                    <div style="background-color: grey; color: white; padding: 5px; border-radius: 5px; text-align: center; flex: 1;">
                        {row['restaurant_price']}
                    </div>
                </div>
                <p><strong>Address:</strong> {row['address']}</p>
                <p><a href="https://www.tripadvisor.fr/{row['restaurant_url']}" target="_blank">Visit on TripAdvisor</a></p>
            </div>
            """, unsafe_allow_html=True)
