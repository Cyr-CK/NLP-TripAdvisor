import streamlit as st
from streamlit_option_menu import option_menu
from views.analytics import analytics_page
from views.home import home_page
from views.llm import llm_page
from views.scraper import scraper_page


selected = option_menu(
    menu_title="TripAdvisor NLP",
    options=["Accueil",  "Scraper", "Analyse", "LLM", "Carte"],
    icons=["house", "download", "bar-chart", "robot", "map"],
    default_index=0,
    orientation="horizontal",
)



if selected == "Accueil":
    home_page()
elif selected == "LLM":
    llm_page()
elif selected == "Analyse":
    analytics_page()
elif selected == "Scraper":
    scraper_page()
elif selected == "Carte":
    st.write("Carte")
