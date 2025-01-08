import streamlit as st
import pandas as pd
import time
import random
import streamlit as st
import pandas as pd
import os
import psycopg2
import psycopg2.extras
from utils.tripAdvisorScraper import TripAdvisorSpecificRestaurantScraper
from utils.db import save_reviews_to_db, get_not_downloaded_restaurants


def download_restaurant_data(filtered_df):
    """
    Downloads the data for the selected restaurant.
    """
    progress_bar = st.progress(0)
    for i, (index, row) in enumerate(filtered_df.iterrows()):
        # filename = row['restaurant_name'].replace(' ', '_')
        # data_restaurant = os.path.join(data_folder, f"{filename}.csv")
        with st.spinner(f"Downloading data for {row['restaurant_name']}..."):
            time.sleep(random.uniform(1, 3))
            restaurant_url = row["restaurant_url"]
            try:
                scraper = TripAdvisorSpecificRestaurantScraper()
                scraper.fetch_page(restaurant_url)
                print(f"url: {scraper.full_url}")
                corpus = scraper.get_all_reviews()
                # df_restaurant = pd.DataFrame(corpus)
                # df_restaurant.to_csv(data_restaurant, index=False)
                save_reviews_to_db(row["restaurant_id"], corpus)
            except Exception as e:
                print(f"Error: {e}")
                continue
        time.sleep(random.uniform(1, 3))
        progress_bar.progress((i + 1) / len(filtered_df))


def extract_types_from_df(df):
    """
    Extracts the restaurant types from the dataframe.
    """
    rest_types = list()
    try:
        df["restaurant_type"] = df["restaurant_type"].apply(
            lambda x: None if "€" in str(x) else x
        )
        temp_rest_types = df["restaurant_type"].dropna().unique()
        for rest_type in temp_rest_types:
            types = rest_type.split(",")
            for type in types:
                rest_types.append(type.strip())
        rest_types = list(set(rest_types))
        rest_types.sort()
        return rest_types
    except KeyError:
        return rest_types
    except Exception as e:
        print(f"Error: {e}")
        return rest_types


def scraper_page():
    """
    Renders the scraper page.
    """
    # data_folder = './data'
    # data_restaurants = os.path.join(data_folder, 'restaurants.csv')
    # if not os.path.exists(data_folder):
    #     os.makedirs(data_folder)

    df = get_not_downloaded_restaurants()

    st.markdown("### 🧲 TripAdvisor Restaurant Data Scraper")
    try:
        # df = pd.DataFrame(data_restaurants)
        rest_types = extract_types_from_df(df)
        download_option = st.radio("Download by:", ("Name", "Type"))

        if download_option == "Name":
            restaurant_name = st.selectbox(
                "Restaurant:", df["restaurant_name"].to_list()
            )
            if st.button("Download", key="button_name_selection"):
                st.write(f"Selected restaurant: {restaurant_name}")
                st.write(f"Downloading data for {restaurant_name}...")
                filtered_df = df[df["restaurant_name"] == restaurant_name]
                download_restaurant_data(filtered_df)

        elif download_option == "Type":
            restaurant_type = st.selectbox("Type:", rest_types)
            filtered_df = df[
                df["restaurant_type"].str.contains(restaurant_type, na=False)
            ]
            st.write("Restaurants of selected type:")
            st.dataframe(
                filtered_df[
                    ["restaurant_name", "restaurant_type", "restaurant_total_reviews"]
                ]
            )
            if st.button("Download"):
                download_restaurant_data(filtered_df)

    except FileNotFoundError:
        st.write("No data found. Run the scraper first.")
