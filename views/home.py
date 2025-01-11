""" This module contains the "Home" page. """

import streamlit as st


def home_page():
    """
    Renders the Home page.
    """
    st.markdown("### 🏠 Accueil")

    st.markdown(
        """
        Cette application a pour objectif d'analyser les avis des restaurants de TripAdvisor en utilisant des techniques de traitement du langage naturel (NLP).
        Voici les principales fonctionnalités de l'application :

        - **Scraper** : Récupérez les données des restaurants directement depuis TripAdvisor.
        - **Analyse** : Comparez les restaurants en fonction de leurs avis, notes et types de cuisine.
        - **LLM** : Utilisez un modèle de langage large (LLM) pour résumer les avis des restaurants.
        - **Carte** : Visualisez les restaurants sur une carte interactive.

        L'application est construite avec Streamlit et utilise diverses bibliothèques Python pour le scraping, l'analyse des données et la visualisation.

        **Technologies utilisées :**
        - Scraping : BeautifulSoup
        - Base de données : PostgreSQL
        - Modèles NLP : Word2Vec, TextBlob, NRCLex
        - LLM : Mistral API (ministral-8b-latest)
        - Interface utilisateur : Streamlit

        Ce projet a été réalisé par Juan Diego Alfonso, Cyril Kocab et Maxence Liogier dans le cadre du cours de NLP du Master 2 SISE.

        Nous espérons que cette application vous sera utile pour explorer et analyser les avis des restaurants de manière efficace et intuitive.
        """
    )
