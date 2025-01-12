""" This module contains the "Scraper" page. """

import time
import random
import streamlit as st
from utils.tripAdvisorScraper import TripAdvisorSpecificRestaurantScraper
from utils.db import save_reviews_to_db, get_not_downloaded_restaurants
from utils.functions import extract_types_from_df


# def scrape_all_restaurants(scraper, url):
#     """Scrape all restaurants and display progress in Streamlit."""
#     scraper.fetch_page(url)
#     restaurants = []
#     page = 1
#     tries = 0
#     while scraper.url is not None:
#         time.sleep(random.uniform(1, 3))
#         scraper.fetch_page(scraper.url)
#         restaurant_cards = scraper.get_restaurant_cards()
#         if not restaurant_cards:
#             tries += 1
#             if tries > 10:
#                 raise Exception("No restaurant cards found - Aborting")
#             else:
#                 continue
#         st.write(f"Scraping page {page}")
#         tries = 0
#         for card in restaurant_cards:
#             restaurant = scraper.parse_restaurant(card)
#             if restaurant:
#                 restaurants.append(restaurant)
#         scraper.url = scraper.get_next_url()
#         page += 1
#     return restaurants

def scrape_restaurant_reviews(scraper, url, total_reviews_expected):
    """Scrape all reviews for a specific restaurant and display progress in Streamlit."""
    scraper.fetch_page(url)
    reviews = []
    page = 1
    tries = 0
    total_pages = total_reviews_expected // 15 + 5
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while scraper.url:
        time.sleep(random.uniform(1, 3))
        review_cards = scraper.get_review_cards()
        if not review_cards:
            tries += 1
            if tries > 10:
                raise Exception("No restaurant cards found - Aborting")
            else:
                continue
        tries = 0
        for card in review_cards:
            reviews.append(scraper.parse_review(card))
        scraper.url = scraper.get_next_url()
        if scraper.url:
            scraper.fetch_page(scraper.url)
        page += 1
        progress_bar.progress(min(page / total_pages, 1.0))
        status_text.text(f"Scraping page {page} of {total_pages}")
    
    progress_bar.progress(1.0)  # Ensure the progress bar is complete at the end
    status_text.text("Scraping complete")
    return reviews

def download_restaurant_data(filtered_df):
    """
    Download data for each restaurant in the filtered DataFrame and save to the database.
    """
    progress_bar = st.progress(0)
    for i, (index, row) in enumerate(filtered_df.iterrows()):
        with st.spinner(f"Downloading data for {row['restaurant_name']}..."):
            time.sleep(random.uniform(1, 3))
            restaurant_url = row["restaurant_url"]
            restaurant_total_reviews = row["restaurant_total_reviews"]
            try:
                scraper = TripAdvisorSpecificRestaurantScraper()
                corpus = scrape_restaurant_reviews(scraper, restaurant_url, restaurant_total_reviews)
                save_reviews_to_db(row['restaurant_id'], corpus)
            except Exception as e:
                print(f"Error: {e}")
                continue
        time.sleep(random.uniform(1, 3))
        progress_bar.progress((i + 1) / len(filtered_df))


def scraper_page(df):
    """
    Streamlit page for scraping TripAdvisor restaurant data.
    """

    st.title("TripAdvisor Restaurant Data Scraper")
    try:
        rest_types = extract_types_from_df(df)
        download_option = st.radio("Télécharger par :", ("Nom", "Type"))

        if download_option == "Nom":
            restaurant_name = st.selectbox(
                "Restaurant:", df["restaurant_name"].to_list()
            )
            if st.button("Télécharger", key="button_name_selection"):
                st.write(f"Restaurant Sélectionné: {restaurant_name}")
                st.write(f"Téléchargement des données pour {restaurant_name}...")
                filtered_df = df[df["restaurant_name"] == restaurant_name]
                download_restaurant_data(filtered_df)

        elif download_option == "Type":
            restaurant_type = st.selectbox("Type:", rest_types)
            filtered_df = df[
                df["restaurant_type"].str.contains(restaurant_type, na=False)
            ]
            st.write("Restaurants du type sélectionné :")
            st.dataframe(
                filtered_df[
                    ["restaurant_name", "restaurant_type", "restaurant_total_reviews"]
                ]
            )
            if st.button("Télécharger"):
                download_restaurant_data(filtered_df)

    except FileNotFoundError:
        st.write(
            "Aucune donnée trouvée. Faites tourner le scraper avant de recommencer."
        )
