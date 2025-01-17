"""
This module contains the "LLM" page.
"""

import streamlit as st
from utils.MistralAPI import MistralAPI
from utils.db import get_reviews_one_restaurant


def reviews_treatment(reviews, restaurant_name, restaurant_info):
    """
    The goal is to treat the reviews so they can be used by the models.
    We want to transform the column of reviews into a string.
    We have to get rid of the apostrophes (\")
    Before the list of reviews, we want to insert the query to the LLM.
    """
    reviews = reviews.replace('"', "")
    reviews = reviews.to_string(index=False)

    query = (
        "Vous êtes un critique culinaire professionnel. "
        f"Votre tâche consiste à analyser et résumer les avis sur le restaurant '{restaurant_name}', en tenant compte des informations suivantes : {restaurant_info}. "
        "Commencez par une introduction présentant le nom du restaurant, son type de cuisine, et sa localisation. "
        "Décrivez ensuite les points forts et faibles du restaurant en deux paragraphes distincts, avec des listes claires pour chaque catégorie. "
        "Mentionnez, si possible, les allergènes présents dans les plats ainsi que l'existence d'options végétariennes, halal ou autres régimes spécifiques. "
        "Ajoutez une recommandation générale basée sur l'analyse des avis en conclusion. "
        "Si des avis sont contradictoires, indiquez-le explicitement. "
        "Rédigez votre réponse de manière claire, professionnelle et engageante."
    )
    query_and_reviews = query + reviews

    return query_and_reviews


def llm_page(df):
    """
    Renders the LLM page.
    """
    # Title of the page
    st.markdown("### 🤖 Analyses utilisant un Large Language Model (IA)")

    # Choice of the restaurant from which we want to analyze the reviews.
    restaurant_name = st.selectbox("Restaurant :", df["restaurant_name"].to_list())
    restaurant_id = df[df["restaurant_name"] == restaurant_name][
        "restaurant_id"
    ].values[0]

    if st.button("Résumer les avis", key="button_name_selection"):
        try:
            st.write("\n\n\n")
            filtered_df = get_reviews_one_restaurant(restaurant_id)
            reviews = filtered_df["review_text"]
            restaurant_info = df[df["restaurant_name"] == restaurant_name]

            # Call the API to analyse the reviews of the restaurant
            ministral = MistralAPI(model="ministral-3b-latest")
            prompt = reviews_treatment(reviews, restaurant_name, restaurant_info)
            st.write(ministral.query(prompt))

        except Exception as e:
            st.warning("Please set up the MISTRAL_API_KEY in the Streamlit secrets.")
            print(f"Error: {e}")
            return
