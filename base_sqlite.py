"""
Ce script python a pour but de tester une implémentation de base SQLite.
On suppose que les données sur les restaurants sont des dataframes pandas.
"""

import sqlite3
import pandas as pd


# création bdd SQLite
conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()

# Création de la table restaurants
cursor.execute(
    """
    CREATE TABLE restaurants (
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
    CREATE TABLE localisation (
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
    CREATE TABLE avis (
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

# On suppose que les dataframes pandas sont déjà créés

# Insertion des données dans la table restaurants
df_restaurants = pd.read_csv("restaurants.csv")
# mauvais format : id_resto==restaurant_class, nom_resto==restaurant_name,
# cuisine (existe pas), prix (existe pas)
df_restos = df_restaurants.rename(
    columns={"restaurant_class": "id_resto", "restaurant_name": "nom_resto"}
)
df_restos["cuisine"] = None  # pas d'info encore sur la cuisine
df_restos["prix"] = None  # pas d'info encore sur le prix

df_restos.to_sql("restaurants", conn, if_exists="append", index=False)


# Insertion des données dans la table avis
COMPTEUR = 1
for nom_resto in df_restos["nom_resto"]:
    df_avis = pd.read_csv(f"{nom_resto}.csv")
    # mauvais format : id(existe pas), id_resto(existe pas dans table), user_name==user_name,
    # review_text==review_text, rating=rating, date==date, contributions==contributions,

    # On récupère l'id du restaurant
    id_resto = df_restos[df_restos["nom_resto"] == nom_resto]["id_resto"].values[0]
    df_avis["id_resto"] = id_resto

    # id inexistant dans le csv, on le crée
    df_avis["id"] = COMPTEUR
    COMPTEUR += 1

    df_avis.to_sql("avis", conn, if_exists="append", index=False)


# Insertion des données dans la table localisation
# On ne peut pas car ces infos n'existent pas encore


# Fermeture de la connexion
conn.close()
