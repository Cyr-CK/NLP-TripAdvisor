"""
Ce script python a pour but de tester une implémentation de base SQLite.
On suppose que les données sur les restaurants sont des dataframes pandas.
"""

import sqlite3
import pandas as pd


# création bdd SQLite
conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()

# CREATION DES TABLES

# cursor.execute("DROP TABLE IF EXISTS restaurants;")
# cursor.execute("DROP TABLE IF EXISTS localisation;")
# cursor.execute("DROP TABLE IF EXISTS avis;")

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


# INSERTION DES DONNEES DANS LES TABLES APRES CREATION EN DF PANDAS
# A TERME, IL FAUDRAIT NE PAS CREER DE FICHIERS CSV INTERMEDIAIRES


def remplissage_bdd(nom_resto):
    """
    Fonction qui remplit la base de données avec les données d'un restaurant
    Se fait via les fichiers CSV, mais il faudrait ne plus passer par là à terme
    """

    # # Insertion des données dans la table restaurants

    df_restaurants = pd.read_csv("data/restaurants.csv")
    # mauvais format : id_resto==restaurant_class, nom_resto==restaurant_name,
    # cuisine (existe pas), prix (existe pas)
    df_restos = df_restaurants.rename(
        columns={"restaurant_class": "id_resto", "restaurant_name": "nom_resto"}
    )
    df_restos["cuisine"] = None  # pas d'info encore sur la cuisine
    df_restos["prix"] = None  # pas d'info encore sur le prix

    # supression colonnes en trop
    df_restos = df_restos.drop(columns=["restaurant_url", "restaurant_reviews"])

    # choisir la bonne ligne
    df_restos = df_restos[df_restos["nom_resto"] == nom_resto]

    # passage en base de données
    df_restos.to_sql("restaurants", conn, if_exists="append", index=False)

    # # Insertion des données dans la table avis

    # lecture du fichier CSV
    nom_resto_csv = nom_resto.replace(" ", "_").replace("'", "")
    df_avis = pd.read_csv(f"data/{nom_resto_csv}.csv")
    # mauvais format : id(existe pas), id_resto(existe pas dans table), user_name==user_name,
    # review_text==review_text, rating=rating, date==date, contributions==contributions,

    # On récupère l'id du restaurant
    id_resto = df_restos[df_restos["nom_resto"] == nom_resto]["id_resto"].values[0]
    df_avis["id_resto"] = id_resto

    # passage en base de données
    df_avis.to_sql("avis", conn, if_exists="append", index=False)

    # Insertion des données dans la table localisation
    # On ne peut pas car ces infos n'existent pas encore


# # TEST DE LA FONCTION
# remplissage_bdd("L'Argot")
# remplissage_bdd("Les Terrasses de Lyon")

# # LECTURE DES DONNEES
# print("Table restaurants")
# cursor.execute("SELECT * FROM restaurants;")
# print(cursor.fetchall())

# print("Table avis")
# cursor.execute("SELECT * FROM avis;")
# print(cursor.fetchall())

# Fermeture de la connexion
conn.close()
