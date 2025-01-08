"""
This module contains the LLM page.
"""

import streamlit as st
from utils.MistralAPI import MistralAPI
from utils.db import get_all_restaurants, get_reviews_one_restaurant


def reviews_treatment(reviews, restaurant_name, restaurant_info):
    """
    The goal is to treat the reviews so they can be used by the models.
    We want to transform the column of reviews into a string.
    We have to get rid of the apostrophes (\")
    Before the list of reviews, we want to insert the query to the LLM.
    """
    reviews = reviews.replace('"', "")
    reviews = reviews.to_string(index=False)

    query = f"Le restaurant est appellé : {restaurant_name}. \
        Voici des infos à propos du restaurant : {restaurant_info}: \
        Résume ces commentaires du restaurant. Le but est de décrire ses qualités et défauts."
    query_and_reviews = query + reviews

    return query_and_reviews


def llm_page():
    """
    Renders the LLM page.
    """
    # Get the data from the database
    df = get_all_restaurants()

    # Title of the page
    st.title("🤖 Analyses utilisant un Large Language Model (IA)")

    # Choice of the restaurant from which we want to analyze the reviews.
    restaurant_name = st.selectbox("Restaurant :", df["restaurant_name"].to_list())
    restaurant_id = df[df["restaurant_name"] == restaurant_name][
        "restaurant_id"
    ].values[0]

    if st.button("Get Reviews", key="button_name_selection"):
        # Get the reviews of the selected restaurant
        filtered_df = get_reviews_one_restaurant(restaurant_id)
        reviews = filtered_df["review_text"]
        restaurant_info = df[df["restaurant_name"] == restaurant_name]

        # Call the API to analyse the reviews of the restaurant
        ministral8b = MistralAPI(model="ministral-8b-latest")
        reviews_cleaned = reviews_treatment(reviews, restaurant_name, restaurant_info)
        st.write(ministral8b.query(reviews_cleaned))

        # Get the reviews of the restaurant
        st.write("\n\n\n")
        st.write("Commentaires du restaurant:")
        st.write(get_reviews_one_restaurant(restaurant_id))
        st.write(restaurant_info)
