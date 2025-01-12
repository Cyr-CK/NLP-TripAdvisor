""" This module contains the "Analyse" page. """

import streamlit as st
from streamlit_option_menu import option_menu
from views import analysis_filtered
from utils.db import get_downloaded_restaurants, get_restaurant_by_id
from utils.functions import extract_types_from_df
import pandas as pd


def analytics_page(df):
    st.title("Analytiques")


    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by type
        types = extract_types_from_df(df, True)
        # st.write(types)
        types = ['Tous'] + list(types)
        selected_type = st.selectbox('Sélectionnez le type de restaurant', types)

    with col2:
        # Filter by price
        prices = ['Tous'] + df['restaurant_price'].unique().tolist()
        selected_price = st.selectbox('Sélectionnez le prix du restaurant', prices)

    # Filter by name
    if selected_type != 'Tous' and selected_price != 'Tous':
        names = ['Tous'] + df[(df['restaurant_type'].str.contains(selected_type, case=False, na=False)) & (df['restaurant_price'] == selected_price)]['restaurant_name'].unique().tolist()
    elif selected_type != 'Tous':
        names = ['Tous'] + df[df['restaurant_type'].str.contains(selected_type, case=False, na=False)]['restaurant_name'].unique().tolist()
    elif selected_price != 'Tous':
        names = ['Tous'] + df[df['restaurant_price'] == selected_price]['restaurant_name'].unique().tolist()
    else:
        names = ['Tous'] + df['restaurant_name'].unique().tolist()

    selected_names = st.multiselect('Sélectionnez les noms des restaurants', names)
    
    # Display filtered selection
    if st.button('Afficher la sélection'):
        if len(selected_names) <= 0 and 'Tous' not in selected_names:
            st.warning('Veuillez sélectionner au moins un restaurant.')
        else:
            filtered_df = df.copy()
            if 'Tous' not in selected_names:
                filtered_df = filtered_df[filtered_df['restaurant_name'].isin(selected_names)]
            else:
                filtered_df = df.copy()
                st.warning('You have selected all restaurants it can take time.')

            # Get restaurant details by IDs
            restaurant_ids = filtered_df['restaurant_id'].tolist()
            filtered_df = get_restaurant_by_id(restaurant_ids)
            
            analysis_filtered.analytics_filtered_page(filtered_df)
