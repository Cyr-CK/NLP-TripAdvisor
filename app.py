import streamlit as st
from tripAdvisorScraper import TripAdvisorRestaurantsScraper, TripAdvisorSpecificRestaurantScraper
import pandas as pd
import os

data_folder = './data'
data_restaurants = os.path.join(data_folder, 'restaurants.csv')
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    
st.title("TripAdvisor Restaurant Data Scraper")
    
    
df = pd.read_csv(data_restaurants)
st.write('Data file exists.')
st.write('Select a restaurant to download its data.')

restaurant_name = st.selectbox('Restaurant:', df['name'].to_list())

if st.button("Get Selection"):
    st.write(f"Selected restaurant: {restaurant_name}")
    st.write(f"Downloading data for {restaurant_name}...")
    scraper = TripAdvisorSpecificRestaurantScraper()
    
    restaurant_data = df[df['name'] == restaurant_name]
    restaurant_url = restaurant_data['url'].values[0]
    restaurant_filename = restaurant_data['filename'].values[0]
    restaurant_total_reviews = restaurant_data['total_reviews'].values[0]
    data_restaurant = os.path.join(data_folder, f'{restaurant_filename}.csv')
    
    st.write(f"Aprox pages: {int(restaurant_total_reviews) // 15}")
    
    scraper = TripAdvisorSpecificRestaurantScraper()
    scraper.fetch_page(restaurant_url)
    print(f'url: {scraper.full_url}')
    reviews = scraper.get_all_reviews()
    df_restaurant = pd.DataFrame(reviews)
    df_restaurant.to_csv(data_restaurant, index=False)
    print('Selection data generated!')
    
    st.write(f"Data downloaded for {restaurant_name}.")