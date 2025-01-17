""" Ce module contient la page "Analyse". """

import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud

from views import analysis_filtered
from utils.db import get_downloaded_restaurants, get_restaurant_by_id
from collections import Counter
import altair as alt

from utils.functions import (
    extract_types_from_df,
    generate_wordcloud,
    clean_text_df,
    generate_word2vec,
    generate_sentiments_analysis,
    generate_word_frequencies_chart,
    generate_spider_plot,
)


# Fonction de filtrage des restaurants
def restaurant_filters(df, tab_title):
    """
    Fonction pour filtrer les restaurants par type, prix et nom.
    """
    col1, col2 = st.columns(2)

    with col1:
        # Filtrer par type
        types = extract_types_from_df(df, True)
        # st.write(types)
        types = ["Tous"] + list(types)
        selected_type = st.selectbox(
            "Sélectionnez le type de restaurant",
            types,
            key=f"restaurant_type_{tab_title}",
        )

    with col2:
        # Filtrer par prix
        prices = ["Tous"] + df["restaurant_price"].unique().tolist()
        selected_price = st.selectbox(
            "Sélectionnez le prix du restaurant",
            prices,
            key=f"restaurant_price_{tab_title}",
        )

    # Filtrer par nom
    if selected_type != "Tous" and selected_price != "Tous":
        names = ["Tous"] + df[
            (df["restaurant_type"].str.contains(selected_type, case=False, na=False))
            & (df["restaurant_price"] == selected_price)
        ]["restaurant_name"].unique().tolist()
    elif selected_type != "Tous":
        names = ["Tous"] + df[
            df["restaurant_type"].str.contains(selected_type, case=False, na=False)
        ]["restaurant_name"].unique().tolist()
    elif selected_price != "Tous":
        names = ["Tous"] + df[df["restaurant_price"] == selected_price][
            "restaurant_name"
        ].unique().tolist()
    else:
        names = ["Tous"] + df["restaurant_name"].unique().tolist()

    selected_names = st.multiselect(
        "Sélectionnez les noms des restaurants",
        names,
        key=f"restaurant_names_{tab_title}",
    )
    return selected_names, names


def get_filtered_restaurant(df, selected_names, names):
    """
    Fonction pour filtrer les restaurants sélectionnés par l'utilisateur.
    """
    if len(selected_names) <= 0 and "Tous" not in selected_names:
        st.warning("Veuillez sélectionner au moins un restaurant.")
        st.stop()
    else:
        filtered_df = df.copy()
        if "Tous" not in selected_names:
            filtered_df = filtered_df[
                filtered_df["restaurant_name"].isin(selected_names)
            ]
        else:  # 'Tous' in selected_names
            names = [
                item for item in names if "Tous" not in item
            ]  # On supprime "Tous" des noms restants
            filtered_df = filtered_df[filtered_df["restaurant_name"].isin(names)]
        if len(filtered_df) > 10:
            st.warning(
                "Vous avez sélectionné plus de dix restaurants, cela peut prendre du temps."
            )

        # Obtenir les détails des restaurants par IDs
        restaurant_ids = filtered_df["restaurant_id"].tolist()
        filtered_df = get_restaurant_by_id(restaurant_ids)
        return filtered_df


def analytics_page(df):
    """Page d'analyse des restaurants."""

    # Création des onglets
    home, sentiment_analysis, word_freq_analysis, simil_anaysis = st.tabs(
        [
            "Faire une analyse",
            "Analyse de sentiments",
            "Wordcloud",
            "Analyse de similarité",
        ]
    )
    with home:
        st.title("Analytiques")
        st.markdown(
            """
            Ici, vous pouvez effectuer différents types d'analyse sur les restaurants :
            - Analyse des sentiments
            - Nuage de mots et fréquences des mots
            - Analyse des similarités avec Word2Vec

            A chaque onglet correspondant à l'analyse que vous souhaitez faire, vous pourrez sélectionner, à partir
            de filtres (type de cuisine, fourchette de prix), les restaurants que vous désirez soumettre à l'analyse.

            Bonne exploration ! 🔥
            """
        )

    ################################################################
    # SENTIMENT ANALYSIS
    ################################################################

    with sentiment_analysis:
        TAB_TITLE = "Analyse de sentiments"
        st.title(TAB_TITLE)
        st.write(
            "ℹ️ Vise à caractériser chaque restaurant à partir des sentiments véhiculés dans les avis des clients."
        )

        selected_names, names = restaurant_filters(df, TAB_TITLE)
        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names)
                filtered_df = clean_text_df(filtered_df)
                # analysis_filtered.analytics_filtered_page(filtered_df)

            with st.spinner("Analyse des sentiments en cours... ⏳"):
                emotions_par_resto, scatter_plot = generate_sentiments_analysis(
                    filtered_df
                )
                st.plotly_chart(scatter_plot, use_container_width=False)

                # Séparation des graphiques
                st.divider()
                st.write("")

                # Analyses des émotions par restaurant
                spider_plot = generate_spider_plot(emotions_par_resto)
                st.plotly_chart(spider_plot, use_container_width=False)

    ################################################################
    # WORDCLOUD
    ################################################################

    with word_freq_analysis:
        TAB_TITLE = "Nuage de mots"
        st.title(TAB_TITLE)
        st.write(
            "ℹ️ Vise à représenter les mots les plus fréquents dans les avis des restaurants sélectionnés."
        )

        selected_names, names = restaurant_filters(df, TAB_TITLE)
        with st.expander("Options de personnalisation"):
            ignored_words_input = st.text_area("Entrez les mots que vous voulez ignorer (séparés par des espaces)")
            ignored_words = ignored_words_input.split() if ignored_words_input else []
            highlighted_words = st.text_area("Entrez les mots que vous voulez mettre en avant (séparés par des espaces, et c'est que pour le grephique des bars)")

        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names)
                filtered_df = clean_text_df(filtered_df)

            with st.spinner("Création du nuage de mots en cours... ⏳"):
                bad_reviews = filtered_df[filtered_df['rating'].isin([1, 2])]
                neutral_reviews = filtered_df[filtered_df['rating'] == 3]
                good_reviews = filtered_df[filtered_df['rating'].isin([4, 5])]
                
                # Description du DataFrame
                total_reviews = len(filtered_df)
                unique_restaurants = filtered_df["restaurant_id"].nunique()
                avg_reviews_per_restaurant = filtered_df.groupby("restaurant_name")["rating"].mean().round(1)
                reviews_per_restaurant = filtered_df.groupby("restaurant_name")["rating"].count().round(1)

                st.write(f"Nombre total d'avis : {total_reviews}")
                st.write(f"Nombre de restaurants uniques analysés : {unique_restaurants}")
                colavg, colcount = st.columns(2)
                with colavg:
                    st.write("**Note moyenne par restaurant :**")
                    st.write(avg_reviews_per_restaurant)
                    
                with colcount:
                    st.write("**Nombre total d'avis par restaurant :**")
                    st.write(reviews_per_restaurant)
                # Afficher les nuages de mots pour chaque catégorie
                col1, col2 = st.columns(2)
                if not bad_reviews.empty:
                    with col1:
                            st.subheader(f"Nuage de mots des avis négatifs ({len(bad_reviews)} avis)")
                            bad_wordcloud = generate_wordcloud(bad_reviews, ignored_words)
                            plt.figure(figsize=(10, 5))
                            plt.imshow(bad_wordcloud, interpolation="bilinear")
                            plt.axis("off")
                            plt.show()
                            st.pyplot(plt)
                            
                    with col2:
                            bar_chart, total_words = generate_word_frequencies_chart(bad_reviews, ignored_words, color="red")
                            st.write(f"Nombre total de mots : {total_words}")
                            st.altair_chart(bar_chart, use_container_width=True)
                            
                col3, col4 = st.columns(2)
                
                if not neutral_reviews.empty:
                    with col3:
                            st.subheader(f"Nuage de mots des avis neutres ({len(neutral_reviews)} avis)")
                            neutral_wordcloud = generate_wordcloud(neutral_reviews, ignored_words,)
                            plt.figure(figsize=(10, 5))
                            plt.imshow(neutral_wordcloud, interpolation="bilinear")
                            plt.axis("off")
                            plt.show()
                            st.pyplot(plt)
                            
                    with col4:
                            bar_chart, total_words = generate_word_frequencies_chart(neutral_reviews, ignored_words, color="grey")
                            st.write(f"Nombre total de mots : {total_words}")
                            st.altair_chart(bar_chart, use_container_width=True)

                col5, col6 = st.columns(2)
                if not good_reviews.empty:
                    with col5:
                            st.subheader(f"Nuage de mots des avis positifs ({len(good_reviews)} avis)")
                            good_wordcloud = generate_wordcloud(good_reviews, ignored_words)
                            plt.figure(figsize=(10, 5))
                            plt.imshow(good_wordcloud, interpolation="bilinear")
                            plt.axis("off")
                            plt.show()
                            st.pyplot(plt)
                    with col6:  
                            bar_chart, total_words = generate_word_frequencies_chart(good_reviews, ignored_words, color="green")
                            st.write(f"Nombre total de mots : {total_words}")
                            st.altair_chart(bar_chart, use_container_width=True)
                            
                if highlighted_words:
                    colword, colword2 = st.columns(2)
                    with colword:
                        st.write("Mots mis en avant :")
                        st.write(highlighted_words)
                        
                        def filter_highlighted_words(reviews, highlighted_words):
                            text_joined = " ".join(reviews["cleaned_text"])
                            text_joined = text_joined.lower()
                            text_joined = text_joined.split(" ")
                            filtered_highlighted_words = [word for word in text_joined if word in highlighted_words]
                            filtered_highlighted_words = [word for word in filtered_highlighted_words if len(word) > 1]
                            return filtered_highlighted_words
                        
                        bad_highlighted_words = filter_highlighted_words(bad_reviews, highlighted_words)
                        neutral_highlighted_words = filter_highlighted_words(neutral_reviews, highlighted_words)
                        good_highlighted_words = filter_highlighted_words(good_reviews, highlighted_words)
                        
                        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
                            " ".join(bad_highlighted_words + neutral_highlighted_words + good_highlighted_words)
                        )
                        plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation="bilinear")
                        plt.axis("off")
                        st.pyplot(plt)
                        
                    with colword2:
                        import pandas as pd
                        word_counts = Counter(bad_highlighted_words + neutral_highlighted_words + good_highlighted_words)
                        word_counts_df = pd.DataFrame(word_counts.items(), columns=["word", "count"])
                        word_counts_df["bad_count"] = word_counts_df["word"].apply(lambda x: bad_highlighted_words.count(x))
                        word_counts_df["neutral_count"] = word_counts_df["word"].apply(lambda x: neutral_highlighted_words.count(x))
                        word_counts_df["good_count"] = word_counts_df["word"].apply(lambda x: good_highlighted_words.count(x))

                        bar_chart = alt.Chart(word_counts_df).transform_fold(
                            ["bad_count", "neutral_count", "good_count"],
                            as_=["Sentiment", "Count"]
                        ).mark_bar().encode(
                            y=alt.Y("word", sort="-x"),
                            x="Count:Q",
                            color=alt.Color("Sentiment:N", scale=alt.Scale(domain=["bad_count", "neutral_count", "good_count"], range=["red", "grey", "green"]))
                        ).properties(
                            width=600,
                            height=400
                        )

                        st.altair_chart(bar_chart, use_container_width=True)
                        

    ################################################################
    # WORD2VEC
    ################################################################

    with simil_anaysis:
        TAB_TITLE = "Analyse des similarités"
        st.title(TAB_TITLE)
        st.markdown(
            'ℹ️ Vise à représenter une "similarité" entre les restaurants à partir de la sémantique des avis des clients.  \n'
            + 'ℹ️ Plus deux restaurants sont proches, plus ils peuvent être interprétés comme "similaires" sur des facteurs comme :  \n'
            + "ℹ️ la proximité géographique, de l'expérience utilisateur, du type de cuisine, du prix, etc."
        )

        selected_names, names = restaurant_filters(df, TAB_TITLE)

        three_dim = st.checkbox("Analyse en 3D ? ", value=False)
        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names)
                if three_dim and len(filtered_df["restaurant_id"].unique()) < 3:
                    st.warning("Veuillez sélectionner au moins trois restaurants.")
                    st.stop()
                elif not three_dim and len(filtered_df["restaurant_id"].unique()) < 2:
                    st.warning("Veuillez sélectionner au moins deux restaurants.")
                    st.stop()
                filtered_df = clean_text_df(filtered_df)

            with st.spinner("Analyse des similarités en cours... ⏳"):
                restaurant_coords, restaurant_names = generate_word2vec(
                    filtered_df, three_dim
                )

                # Create a new figure for the scatter plot
                fig = go.Figure()

                if three_dim:
                    # Ajout des points de scatter
                    fig.add_trace(
                        go.Scatter3d(
                            x=restaurant_coords[:, 0],
                            y=restaurant_coords[:, 1],
                            z=restaurant_coords[:, 2],
                            mode="markers+text",
                            marker=dict(size=10, color="blue"),
                            text=restaurant_names,
                            textposition="top center",
                            hoverinfo="text",
                        )
                    )

                    # Mise à jour du layout
                    fig.update_layout(
                        title="Représentation des restaurants basée sur les avis (ACP)",
                        scene=dict(
                            xaxis_title="Dimension 1",
                            yaxis_title="Dimension 2",
                            zaxis_title="Dimension 3",
                        ),
                        width=800,
                        height=600,
                    )

                else:
                    # Ajout des points de scatter
                    fig.add_trace(
                        go.Scatter(
                            x=restaurant_coords[:, 0],
                            y=restaurant_coords[:, 1],
                            mode="markers+text",
                            marker=dict(size=10, color="blue"),
                            text=restaurant_names,
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
                # st.write(f"Temps de traitement : {(end-start)/60} min. ({end - start} sec.)")
                # st.write(f"{(end-start)/len(filtered_df['restaurant_id'].unique())} sec/restaurant en moyenne.")
