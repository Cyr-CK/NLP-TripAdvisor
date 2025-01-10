""" This module contains the "Analyse" page. """

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from gensim.models import Word2Vec
from textblob import TextBlob
from nrclex import NRCLex
from nltk.tokenize import word_tokenize
from utils.db import (
    get_downloaded_restaurants,
    get_reviews_one_restaurant,
    get_all_reviews,
)

# Télécharger les ressources NLTK nécessaires
# nltk.download('punkt')
# nltk.download('punkt_tab')


def analytics_page():
    """
    Affiche la page d'analyse
    """

    # Get the data from the database
    df = get_downloaded_restaurants()

    # Title of the page
    st.markdown("### 📊 Analyse de similarité")

    # Create tabs
    tab1, tab2 = st.tabs(["ACP", "Analyse de sentiment"])

    with tab1:
        st.markdown("#### Analyse en Composantes Principales (ACP)")

        # Choice of the restaurant from which we want to analyze the reviews.
        st.write("Choisissez les restaurants à analyser :")
        select_all = st.checkbox("Sélectionner Tous")
        if select_all:
            restaurant_name = df["restaurant_name"].to_list()
        else:
            restaurant_name = st.multiselect(
                "Restaurants choisis :",
                df["restaurant_name"].to_list(),
            )

        # Bouton pour lancer l'analyse
        if st.button("Analyse des similarités", key="analysis_button"):
            with st.spinner(
                "Apprentissage des représentations vectorielles des restaurants en cours..."
            ):
                restaurant_ids = df[df["restaurant_name"].isin(restaurant_name)][
                    "restaurant_id"
                ]
                reviews = pd.DataFrame()
                for id in restaurant_ids:
                    filtered_df = get_reviews_one_restaurant(id)
                    temp = filtered_df[["restaurant_id", "review_text"]]
                    if reviews.empty:
                        reviews = temp
                    else:
                        reviews = pd.concat([reviews, temp], axis=0)

                # Prétraitement des avis
                reviews["tokens"] = reviews["review_text"].apply(
                    lambda x: word_tokenize(x.lower())
                )

                # Entraîner le modèle Word2Vec
                model = Word2Vec(
                    sentences=reviews["tokens"],
                    vector_size=100,
                    window=5,
                    min_count=1,
                    workers=4,
                )

                # Fonction pour obtenir le vecteur moyen d'un avis
                def get_avg_vector(tokens):
                    vectors = [model.wv[word] for word in tokens if word in model.wv]
                    if len(vectors) == 0:
                        return np.zeros(100)
                    return np.mean(vectors, axis=0)

                # Calculer les vecteurs moyens pour chaque restaurant
                reviews["avg_vector"] = reviews["tokens"].apply(get_avg_vector)

                # Agréger les vecteurs par restaurant
                restaurant_vectors = reviews.groupby("restaurant_id")[
                    "avg_vector"
                ].apply(lambda x: np.mean(list(x), axis=0))
                # restaurant_vectors = restaurant_vectors.to_frame(name="avg_vector")
                # restaurant_vectors["restaurant_id"] = reviews.groupby('restaurant_id')['restaurant_id']
                restaurant_vectors = (
                    reviews.groupby("restaurant_id")
                    .agg({"avg_vector": "first", "restaurant_id": "first"})
                    .reset_index(drop=True)
                )

                restaurant_vectors["restaurant_name"] = df[
                    df["restaurant_id"] == restaurant_vectors["restaurant_id"]
                ]["restaurant_name"]

                # Réduction de dimensionnalité avec ACP
                from sklearn.decomposition import PCA

                pca = PCA(n_components=2, random_state=42)
                restaurant_coords = pca.fit_transform(
                    np.array(restaurant_vectors["avg_vector"].tolist())
                )

                # Visualisation
                # fig, ax = plt.subplots(figsize=(12, 8))

                # ax.scatter(restaurant_coords[:, 0], restaurant_coords[:, 1])

                # for i, restaurant in enumerate(restaurant_vectors.index):
                #     ax.annotate(restaurant, (restaurant_coords[i, 0], restaurant_coords[i, 1]))

                # ax.set_title("Représentation des restaurants basée sur les avis (ACP)")
                # ax.set_xlabel("Dimension 1")
                # ax.set_ylabel("Dimension 2")

                # st.pyplot(fig)

                fig = go.Figure()

                # Ajout des points de scatter
                fig.add_trace(
                    go.Scatter(
                        x=restaurant_coords[:, 0],
                        y=restaurant_coords[:, 1],
                        mode="markers+text",
                        marker=dict(size=10, color="blue"),
                        text=restaurant_vectors["restaurant_name"],
                        textposition="top center",
                        hoverinfo="text",
                    )
                )

                # Mise à jour du layout
                fig.update_layout(
                    title="Représentation des restaurants basée sur les avis (ACP)",
                    xaxis_title="Dimension 1",
                    yaxis_title="Dimension 2",
                    width=800,
                    height=600,
                )

                # Affichage du graphique dans Streamlit
                st.plotly_chart(fig)

    # Onglet analyse de sentiments
    with tab2:
        st.markdown("#### Analyse de sentiments")

        # Choice of the restaurant from which we want to analyze the reviews.
        st.write("Choisissez les restaurants à analyser :")
        select_all2 = st.checkbox("Selectionner Tous")
        if select_all2:
            restaurant_name2 = df["restaurant_name"].to_list()
        else:
            restaurant_name2 = st.multiselect(
                "Restaurants choisis:",
                df["restaurant_name"].to_list(),
            )

        # Button to launch the analysis
        if st.button("Analyse de sentiments", key="analysis_button2"):

            # Récupération des avis
            restaurant_ids = df[df["restaurant_name"].isin(restaurant_name2)][
                "restaurant_id"
            ]
            avis = pd.DataFrame()
            for id in restaurant_ids:
                filtered_df = get_reviews_one_restaurant(id)
                temp = filtered_df[["restaurant_id", "review_text", "rating"]]
                if avis.empty:
                    avis = temp
                else:
                    avis = pd.concat([avis, temp], axis=0)

            # Ajout d'une colonne "sentiment" avec la polarité des avis
            avis["sentiment"] = avis["review_text"].apply(
                lambda x: TextBlob(x).sentiment.polarity
            )
            # La polarité est comprise entre -1 et 1
            # -1 étant très négatif, 1 très positif et 0 neutre

            # avis par restaurant
            avis_par_resto = avis.groupby("restaurant_id")["sentiment"].mean()
            note_moyenne = avis.groupby("restaurant_id")["rating"].mean()

            avis_par_resto = pd.DataFrame(avis_par_resto)
            note_moyenne = pd.DataFrame(note_moyenne)

            notes_moyennes = pd.merge(avis_par_resto, note_moyenne, on="restaurant_id")
            notes_moyennes = notes_moyennes.rename(
                columns={"sentiment": "sentiment_moyen", "rating": "note_moyenne"}
            )

            # merge with restaurants
            data = pd.merge(df, notes_moyennes, on="restaurant_id")

            # Dispertion graph
            plt.figure(figsize=(10, 6))
            plt.scatter(data["note_moyenne"], data["sentiment_moyen"])
            for _, row in data.iterrows():
                plt.text(
                    row["note_moyenne"],
                    row["sentiment_moyen"],
                    row["restaurant_name"],
                    fontsize=9,
                )
            plt.xlabel("Note Moyenne")
            plt.ylabel("Sentiment Moyen")
            plt.title("Sentiment Moyen vs Note Moyenne par Restaurant")
            st.pyplot(plt)

            # Fonction pour extraire les scores d'émotions
            def extract_emotions(text):
                """
                Fonction qui extrait les scores d'émotions d'un texte.
                Pour chaque émotion, on calcule le score en fonction du nombre d'occurrences.
                """
                emotion_scores = NRCLex(text).raw_emotion_scores
                # Normaliser par le nombre total d'émotions détectées (optionnel)
                total = sum(emotion_scores.values())
                if total > 0:
                    return {
                        emotion: score / total
                        for emotion, score in emotion_scores.items()
                    }
                return emotion_scores

            # Appliquer la fonction sur la colonne "review_text" et créer un DataFrame d'émotions
            emotion_data = avis["review_text"].apply(extract_emotions)
            emotion_df = pd.DataFrame(emotion_data.tolist())

            # Reset index to be able to concatenate
            avis.reset_index(drop=True, inplace=True)
            emotion_df.reset_index(drop=True, inplace=True)

            # Ajouter les scores d'émotions au DataFrame "avis"
            avis = pd.concat([avis, emotion_df], axis=1)

            # Calculer les moyennes des émotions pour chaque restaurant
            emotions_par_resto = avis.groupby("restaurant_id")[
                emotion_df.columns
            ].mean()
            st.write("Emotions moyennes par restaurant :")
            st.write(emotions_par_resto)

            st.write(
                "Les emotions sont présentées de manière moche pour l'instant mais cela va bouger"
            )
