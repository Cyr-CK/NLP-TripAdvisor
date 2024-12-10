"""
Ce script python a pour but de tester une implémentation de base SQLite.
On suppose que les données sur les restaurants sont des dataframes pandas.
"""

import sqlite3

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
        restaurant_id INTEGER NOT NULL,
        user_name TEXT,
        review_text TEXT,
        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
        date DATE,
        contributions INTEGER,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
    );
"""
)


## RESTE A FAIRE : INSERTION DES DONNEES DANS LES TABLES ##
