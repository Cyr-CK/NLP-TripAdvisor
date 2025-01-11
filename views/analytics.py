import streamlit as st
from streamlit_option_menu import option_menu
from views import analysis_filtered
from utils.db import get_downloaded_restaurants, get_restaurant_by_id
import pandas as pd


def analytics_page():
    st.title("Analytiques")

    # Load restaurant data
    df = get_downloaded_restaurants()

    # Filter by type
    types = ['Tous'] + df['restaurant_type'].unique().tolist()
    selected_type = st.selectbox('Sélectionnez le type de restaurant', types)

    if selected_type != 'Tous':
        df = df[df['restaurant_type'] == selected_type]

    # Filter by price
    prices = ['Tous'] + df['restaurant_price'].unique().tolist()
    selected_price = st.selectbox('Sélectionnez le prix du restaurant', prices)

    if selected_price != 'Tous':
        df = df[df['restaurant_price'] == selected_price]

    # Filter by name
    names = ['Tous'] + df['restaurant_name'].unique().tolist()
    selected_names = st.multiselect('Sélectionnez les noms des restaurants', names)

    # Update filters based on selections
    if selected_type != 'Tous':
        prices = ['Tous'] + df[df['restaurant_type'] == selected_type]['restaurant_price'].unique().tolist()
    if selected_price != 'Tous':
        names = ['Tous'] + df[df['restaurant_price'] == selected_price]['restaurant_name'].unique().tolist()
    if selected_type != 'Tous' and selected_price != 'Tous':
        names = ['Tous'] + df[(df['restaurant_type'] == selected_type) & (df['restaurant_price'] == selected_price)]['restaurant_name'].unique().tolist()

    # Display filtered selection
    if st.button('Afficher la sélection'):
        if len(selected_names) <= 0 and 'Tous' not in selected_names:
            st.warning('Veuillez sélectionner au moins un restaurant.')
        else:
            filtered_df = df.copy()
            if 'Tous' not in selected_names:
                filtered_df = filtered_df[filtered_df['restaurant_name'].isin(selected_names)]
            if selected_type != 'Tous':
                filtered_df = filtered_df[filtered_df['restaurant_type'] == selected_type]
            if selected_price != 'Tous':
                filtered_df = filtered_df[filtered_df['restaurant_price'] == selected_price]

            # Get restaurant details by IDs
            restaurant_ids = filtered_df['restaurant_id'].tolist()
            filtered_df = get_restaurant_by_id(restaurant_ids)
            
            analysis_filtered.analytics_filtered_page(filtered_df)