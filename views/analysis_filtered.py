import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec

from nrclex import NRCLex  # Add this import
from utils.functions import (
    generate_wordcloud, 
    clean_text_df, 
    generate_word2vec, 
    generate_sentiments_analysis,
    generate_word_frequencies_chart
    )


def analytics_filtered_page(df):

    df = clean_text_df(df)
    
    
################################################################
# SENTIMENTS
################################################################
    
    ## CODE HERE YOUR FUNCTION MAKE ANYTHING YOU NEED WITH TO SHOW THE RESULT OF SENTIMENTS##
    result = generate_sentiments_analysis(df)
    # if result[0] == "error":
    #     st.warning(result[1])
    # else:
    st.markdown("#### Analyse de sentiments")
    st.success(result[1])
    df_reviews = df

    # Ajout d'une colonne "sentiment" avec la polarité des df_reviews
    df_reviews["sentiment"] = df_reviews["review_text"].apply(
        lambda x: TextBlob(x).sentiment.polarity
    )
    # La polarité est comprise entre -1 et 1
    # -1 étant très négatif, 1 très positif et 0 neutre

    # df_reviews par restaurant
    df_reviews_par_resto = df_reviews.groupby("restaurant_id")["sentiment"].mean()
    note_moyenne = df_reviews.groupby("restaurant_id")["rating"].mean()

    df_reviews_par_resto = pd.DataFrame(df_reviews_par_resto)
    note_moyenne = pd.DataFrame(note_moyenne)

    notes_moyennes = pd.merge(df_reviews_par_resto, note_moyenne, on="restaurant_id")
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
    emotion_data = df_reviews["review_text"].apply(extract_emotions)
    emotion_df = pd.DataFrame(emotion_data.tolist())

    # Reset index to be able to concatenate
    df_reviews.reset_index(drop=True, inplace=True)
    emotion_df.reset_index(drop=True, inplace=True)

    # Ajouter les scores d'émotions au DataFrame "df_reviews"
    df_reviews = pd.concat([df_reviews, emotion_df], axis=1)

    # Calculer les moyennes des émotions pour chaque restaurant
    emotions_par_resto = df_reviews.groupby("restaurant_id")[
        emotion_df.columns
    ].mean()
    st.write("Emotions moyennes par restaurant :")
    st.write(emotions_par_resto)

    st.write(
        "Les emotions sont présentées de manière moche pour l'instant mais cela va bouger"
    )
    st.pyplot(plt)
        
        
################################################################
# WORD2VEC
################################################################
    

    ## CODE HERE YOUR FUNCTION MAKE ANYTHING YOU NEED WITH TO SHOW THE RESULT##
    result = generate_word2vec(df)
    if result[0] == "error":
        st.warning(result[1])
    else:
        st.success(result[1])
    
    reviews = df
    reviews["tokens"] = reviews["cleaned_text"].apply(
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
    # Prétraitement des avis
    # Fonction pour obtenir le vecteur moyen d'un avis
    def get_avg_vector(tokens):
        vectors = [model.wv[word] for word in tokens if word in model.wv]
        if len(vectors) == 0:
            return np.zeros(100)
        return np.mean(vectors, axis=0)

    # Calculer les vecteurs moyens pour chaque restaurant
    reviews["avg_vector"] = reviews["tokens"].apply(get_avg_vector)

    # Agréger les vecteurs par restaurant
    restaurant_vectors = (
        reviews.groupby("restaurant_id")
        .agg({"avg_vector": lambda x: np.mean(list(x), axis=0), "restaurant_id": "first"})
        .reset_index(drop=True)
    )

    restaurant_vectors = restaurant_vectors.drop_duplicates(subset="restaurant_id")
    restaurant_vectors = restaurant_vectors.set_index("restaurant_id")
    restaurant_vectors["restaurant_name"] = df.drop_duplicates(subset="restaurant_id").set_index("restaurant_id")["restaurant_name"]
    restaurant_vectors.reset_index(inplace=True)

    # Réduction de dimensionnalité avec ACP
    from sklearn.decomposition import PCA

    pca = PCA(n_components=2, random_state=42)
    restaurant_coords = pca.fit_transform(
        np.array(restaurant_vectors["avg_vector"].tolist())
    )

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


################################################################
# WORDCLOUD
################################################################
    
    col1, col2 = st.columns(2)
    with col1:
        if len(df) == 1:
            st.warning("Vous avez besoin de plus d'un restaurant pour créer Word2Vec.")
        else:
            st.write("Le nuage de mots ci-dessus représente les mots les plus fréquents dans les df_reviews des restaurants sélectionnés.")
            wordcloud = generate_wordcloud(df)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()
            st.pyplot(plt)
            

    with col2:
        # Use the function to generate and display the chart
        bar_chart = generate_word_frequencies_chart(df)
        st.altair_chart(bar_chart, use_container_width=True)
        

