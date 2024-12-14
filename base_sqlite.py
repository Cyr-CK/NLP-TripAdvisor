"""
Ce script python a pour but de tester une implémentation de base SQLite.
On suppose que les données sur les restaurants sont des dataframes pandas.
"""

import os
import sqlite3
import pandas as pd
from tripAdvisorScraper import (
    TripAdvisorRestaurantsScraper,
    TripAdvisorSpecificRestaurantScraper,
)

conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()


# création bdd SQLite
def create_bdd():
    """
    Fonction qui crée la base de données SQLite restaurants.db
    Tables : restaurants, localisation, avis
    """
    cursor.execute("DROP TABLE IF EXISTS restaurants;")
    cursor.execute("DROP TABLE IF EXISTS localisation;")
    cursor.execute("DROP TABLE IF EXISTS avis;")

    # Création de la table restaurants
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS restaurants (
            id_resto INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_resto TEXT NOT NULL,
            cuisine TEXT,
            prix TEXT 
        );
    """
    )
    # Prix sous la forme de "€", "€€", "€€€", "€€€€"
    # éventuellement sous la forme "€€-€€€" selon ce que renvoie TripAdvisor

    # Création de la table localisation
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS localisation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_resto INTEGER NOT NULL,
            addresse TEXT,
            ville,
            code_postal TEXT,
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (id_resto) REFERENCES restaurants(id_resto)
        );
    """
    )

    # Création de la table avis
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS avis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_resto INTEGER NOT NULL,
            user_name TEXT,
            review_text TEXT,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            date DATE,
            contributions INTEGER,
            FOREIGN KEY (id_resto) REFERENCES restaurants(id_resto)
        );
    """
    )


# # WEB SCRAPPING DES DONNEES


def all_restaurants():
    """
    Fonction qui renvoie la liste des restaurants dans un dataframe pandas

    La liste des restaurants est demandée plusieurs fois
    Pour ne pas survharger TripAdvisor, on stocke également les données dans un fichier csv.

    Cette fonction ne doit donc être appellée qu'une seule fois !
    """
    print("Generating the list of all restaurants...")

    # On récupère les données des restaurants
    restaurants_url = "/FindRestaurants?geo=187265&offset=0&establishmentTypes=10591&minimumTravelerRating=TRAVELER_RATING_LOW&broadened=false"
    restaurants_scraper = TripAdvisorRestaurantsScraper()
    restaurants_scraper.fetch_page(restaurants_url)
    corpus = restaurants_scraper.get_all_pages()
    df_all_restos = pd.DataFrame(corpus)

    # Stockage des données dans un fichier csv
    df_all_restos.to_csv("data/restaurants.csv", index=False)

    print("Restaurants list downloaded!")
    return df_all_restos


def specific_restaurant(restaurant_name):
    """
    Fonction qui renvoie les données d'un restaurant spécifique
    """
    print(f"Generating data for {restaurant_name}...")

    # On récupère les données du restaurant
    if not os.path.exists("data/restaurants.csv"):
        df_all_restos = all_restaurants()
    else:
        df_all_restos = pd.read_csv("data/restaurants.csv")

    restaurant_data = df_all_restos[df_all_restos["restaurant_name"] == restaurant_name]
    restaurant_url = restaurant_data["restaurant_url"].values[0]

    # On récupère les avis du restaurant
    scraper = TripAdvisorSpecificRestaurantScraper()
    scraper.fetch_page(restaurant_url)
    corpus = scraper.get_all_pages()
    df_1_resto = pd.DataFrame(corpus)

    print(f"{restaurant_name} data downloaded!")
    return df_1_resto


# INSERTION DES DONNEES DANS LES TABLES APRES CREATION EN DF PANDAS


def remplissage_bdd(nom_resto):
    """
    Fonction qui remplit la base de données avec les données d'un restaurant
    Se fait via df pandas, mais il faudrait ne plus passer par là à terme
    """

    # # Insertion des données dans la table restaurants

    if not os.path.exists("data/restaurants.csv"):
        df_restaurants = all_restaurants()
    else:
        df_restaurants = pd.read_csv("data/restaurants.csv")
    # mauvais format : id_resto==restaurant_class, nom_resto==restaurant_name,
    # cuisine (existe pas), prix (existe pas)
    df_restos = df_restaurants.rename(
        columns={"restaurant_class": "id_resto", "restaurant_name": "nom_resto"}
    )
    df_restos["cuisine"] = None  # pas d'info encore sur la cuisine
    df_restos["prix"] = None  # pas d'info encore sur le prix

    print(df_restos.columns)

    # supression colonnes en trop
    df_restos = df_restos.drop(columns=["restaurant_url", "restaurant_reviews"])

    # choisir la bonne ligne
    df_restos = df_restos[df_restos["nom_resto"] == nom_resto]

    # passage en base de données
    df_restos.to_sql("restaurants", conn, if_exists="append", index=False)

    # # Insertion des données dans la table avis

    # lecture des données
    df_avis = specific_restaurant(nom_resto)
    # mauvais format : id(existe pas), id_resto(existe pas dans table), user_name==user_name,
    # review_text==review_text, rating=rating, date==date, contributions==contributions,

    # On récupère l'id du restaurant
    id_resto = df_restos[df_restos["nom_resto"] == nom_resto]["id_resto"].values[0]
    df_avis["id_resto"] = id_resto

    # passage en base de données
    df_avis.to_sql("avis", conn, if_exists="append", index=False)

    # Insertion des données dans la table localisation
    # On ne peut pas car ces infos n'existent pas encore


# TEST DE LA FONCTION
create_bdd()

remplissage_bdd("L'Argot")
remplissage_bdd("Les Terrasses de Lyon")

# LECTURE DES DONNEES
print("Table restaurants")
cursor.execute("SELECT * FROM restaurants;")
print(cursor.fetchall())

print("Table avis")
cursor.execute("SELECT * FROM avis;")
print(cursor.fetchall())

# Fermeture de la connexion
conn.close()
