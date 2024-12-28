import streamlit as st
from streamlit_option_menu import option_menu
from views.analytics import analytics_page
from views.home import home_page
from views.predictions import prediction_page
from views.scraper import scraper_page


selected = option_menu(
    menu_title="TripAdvisor NLP",
    options=["Accueil", "Analytiques", "Prediction", "Scraper"],
    icons=["house", "bar-chart", "robot", "download"],
    default_index=0,
    orientation="horizontal",
)



if selected == "Accueil":
    home_page()
elif selected == "Prediction":
    prediction_page()
elif selected == "Analytiques":
    analytics_page()
elif selected == "Scraper":
    scraper_page()