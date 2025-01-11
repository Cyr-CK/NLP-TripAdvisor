import streamlit as st
from streamlit_option_menu import option_menu
from views.analytics import analytics_page
from views.home import home_page
from views.llm import llm_page
from views.scraper import scraper_page
from views.map import map_page

APP_TITLE = "TripAdvisor NLP"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="assets/img/Tripadvisor Icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
with st.sidebar:
    st.image("assets/img/Tripadvisor Icon_2.png")
    selected = option_menu(
        menu_icon='None',
        menu_title=APP_TITLE,
        options=["Accueil", "Scraper", "Analytiques", "LLM", "Carte"],
        icons=["house", "download", "bar-chart", "robot", "map"],
        default_index=0,
        # orientation="horizontal",
    )


if selected == "Accueil":
    home_page()
elif selected == "LLM":
    llm_page()
elif selected == "Analytiques":
    analytics_page()
elif selected == "Scraper":
    scraper_page()
elif selected == "Carte":
    map_page()
