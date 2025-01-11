import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
from utils.functions import (
    generate_wordcloud, 
    clean_text_df, 
    generate_word2vec, 
    generate_sentiments_analysis,
    generate_word_frequencies_chart
    )


def analytics_filtered_page(df):

    col1, col2 = st.columns(2)

    with col1:
        if len(df) == 1:
            st.warning("Vous avez besoin de plus d'un restaurant pour créer Word2Vec.")
        else:
            df = clean_text_df(df)
            st.write("Le nuage de mots ci-dessus représente les mots les plus fréquents dans les avis des restaurants sélectionnés.")
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
        
    col3, col4 = st.columns(2)
    with col3:
        ## CODE HERE YOUR FUNCTION MAKE ANYTHING YOU NEED WITH TO SHOW THE RESULT OF SENTIMENTS##
        result = generate_sentiments_analysis(df)
        if result[0] == "error":
            st.warning(result[1])
        else:
         st.success(result[1])
    with col4:
        ## CODE HERE YOUR FUNCTION MAKE ANYTHING YOU NEED WITH TO SHOW THE RESULT##
        result = generate_word2vec(df)
        if result[0] == "error":
            st.warning(result[1])
        else:
            st.success(result[1])
            
    
    st.write(df)
    
    