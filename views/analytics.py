import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sklearn
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk
from utils.db import get_downloaded_restaurants, get_reviews_one_restaurant

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
    
    # Choice of the restaurant from which we want to analyze the reviews.
    restaurant_name = st.multiselect("Restaurants :", df["restaurant_name"].to_list())

    # Bouton pour lancer l'analyse
    if st.button("Analyse des similarités", key="analysis_button"):
        with st.spinner("Apprentissage des représentations vectorielles des restaurants en cours..."):
            restaurant_ids = df[df["restaurant_name"].isin(restaurant_name)]["restaurant_id"]
            reviews = pd.DataFrame()
            for id in restaurant_ids:
                filtered_df = get_reviews_one_restaurant(id)
                temp = filtered_df[["restaurant_id","review_text"]]
                if reviews.empty:
                    reviews = temp
                else:
                    reviews = pd.concat([reviews, temp], axis=0)
            
            # Prétraitement des avis
            reviews['tokens'] = reviews['review_text'].apply(lambda x: word_tokenize(x.lower()))

            # Entraîner le modèle Word2Vec
            model = Word2Vec(sentences=reviews['tokens'], vector_size=100, window=5, min_count=1, workers=4)

            # Fonction pour obtenir le vecteur moyen d'un avis
            def get_avg_vector(tokens):
                vectors = [model.wv[word] for word in tokens if word in model.wv]
                if len(vectors) == 0:
                    return np.zeros(100)
                return np.mean(vectors, axis=0)

            # Calculer les vecteurs moyens pour chaque restaurant
            reviews['avg_vector'] = reviews['tokens'].apply(get_avg_vector)

            # Agréger les vecteurs par restaurant
            restaurant_vectors = reviews.groupby('restaurant_id')['avg_vector'].apply(lambda x: np.mean(list(x), axis=0))
            # restaurant_vectors = restaurant_vectors.to_frame(name="avg_vector")
            # restaurant_vectors["restaurant_id"] = reviews.groupby('restaurant_id')['restaurant_id']
            restaurant_vectors = reviews.groupby('restaurant_id').agg({
                'avg_vector': 'first',
                'restaurant_id': 'first'
            }).reset_index(drop=True)

            restaurant_vectors["restaurant_name"] = df[df["restaurant_id"] == restaurant_vectors["restaurant_id"]]["restaurant_name"]

            # Réduction de dimensionnalité avec ACP
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2, random_state=42)
            restaurant_coords = pca.fit_transform(np.array(restaurant_vectors["avg_vector"].tolist()))

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
            fig.add_trace(go.Scatter(
                x=restaurant_coords[:, 0],
                y=restaurant_coords[:, 1],
                mode='markers+text',
                marker=dict(size=10, color='blue'),
                text=restaurant_vectors["restaurant_name"],
                textposition="top center",
                hoverinfo='text'
            ))

            # Mise à jour du layout
            fig.update_layout(
                title="Représentation des restaurants basée sur les avis (ACP)",
                xaxis_title="Dimension 1",
                yaxis_title="Dimension 2",
                width=800,
                height=600
            )

            # Affichage du graphique dans Streamlit
            st.plotly_chart(fig)