""" Ce module contient la page "Analyse". """

import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from views import analysis_filtered
from utils.db import get_downloaded_restaurants, get_restaurant_by_id

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


def get_filtered_restaurant(df, selected_names, names, relevance):
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
        if relevance:
            avg = filtered_df["contributions"].median()
            filtered_df = filtered_df[filtered_df["contributions"] >= avg]
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

        relevance = st.checkbox("Analyse des avis les plus pertinents ?", value=False,
                                help="Seuls les avis émis par des internautes ayant un volume de contribution supérieur à la médiane seront pris en compte lors de l'analyse.",
                                key=f"relevant_only_{TAB_TITLE}")

        st.divider()
        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names, relevance)
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

        relevance = st.checkbox("Analyse des avis les plus pertinents ?", value=False,
                                help="Seuls les avis émis par des internautes ayant un volume de contribution supérieur à la médiane seront pris en compte lors de l'analyse.",
                                key=f"relevant_only_{TAB_TITLE}")

        st.divider()
        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names, relevance)
                filtered_df = clean_text_df(filtered_df)

            with st.spinner("Création du nuage de mots en cours... ⏳"):
                col1, col2 = st.columns(2)
                with col1:
                    wordcloud = generate_wordcloud(filtered_df)
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation="bilinear")
                    plt.axis("off")
                    plt.show()
                    st.pyplot(plt)

                with col2:
                    # Use the function to generate and display the chart
                    bar_chart = generate_word_frequencies_chart(filtered_df)
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

        # col1, col2, col3 = st.columns(3)
        col1, col2 = st.columns(2)
        with col1:
            relevance = st.checkbox("Analyse des avis les plus pertinents ?", value=False,
                                    help="Seuls les avis émis par des internautes ayant un volume de contribution supérieur à la médiane seront pris en compte lors de l'analyse.",
                                    key=f"relevant_only_{TAB_TITLE}")
        with col2:
            three_dim = st.checkbox("Analyse en 3D ? ", value=False)
        # with col3:
        #     analysis_type = st.selectbox("Où mettre l'accent pour l'analyse ?", options=["Type de cuisine", "Fourchette de prix"])
            
        st.divider()
        # Afficher la sélection filtrée
        if st.button("Démarrer l'analyse", key=f"start_analysis_{TAB_TITLE}"):
            with st.spinner(
                "Acquisition et pré-traitement des données sélectionnées... ⏳"
            ):
                filtered_df = get_filtered_restaurant(df, selected_names, names, relevance)
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
                # if analysis_type == "Type de cuisine":
                #     classes = restaurant_info_supp["restaurant_type"]
                # else: # analysis_type == "Fourchette de prix"
                #     classes = restaurant_info_supp["restaurant_price"]
                
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
                            marker=dict(
                                size=10, 
                                color="blue"
                                ),
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
                            marker=dict(
                                size=10, 
                                color="blue"
                                ),
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
