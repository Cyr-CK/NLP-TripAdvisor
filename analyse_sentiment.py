"""
Ce script python a pour but de tester une analyse de sentiment sur les avis des restaurants.
"""

import pandas as pd
import sqlite3
from textblob import TextBlob
from nrclex import NRCLex

# Connexion à la base de données
conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()

# Récupération des avis
cursor.execute("SELECT * FROM avis")
avis = cursor.fetchall()
avis = pd.DataFrame(avis, columns=[x[0] for x in cursor.description])

# Ajout d'une colonne "sentiment" avec la polarité des avis
avis["sentiment"] = avis["review_text"].apply(lambda x: TextBlob(x).sentiment.polarity)
# La polarité est comprise entre -1 et 1
# -1 étant très négatif, 1 très positif et 0 neutre

# avis par restaurant
avis_par_resto = avis.groupby("id_resto")["sentiment"].mean()
note_moyenne = avis.groupby("id_resto")["rating"].mean()

avis_par_resto = pd.DataFrame(avis_par_resto)
note_moyenne = pd.DataFrame(note_moyenne)

notes_moyennes = pd.merge(avis_par_resto, note_moyenne, on="id_resto")
notes_moyennes = notes_moyennes.rename(
    columns={"sentiment": "sentiment_moyen", "rating": "note_moyenne"}
)
print(notes_moyennes)

# merge avec restaurants
cursor.execute("SELECT * FROM restaurants")
restaurants = cursor.fetchall()
restaurants = pd.DataFrame(restaurants, columns=[x[0] for x in cursor.description])
data = pd.merge(restaurants, notes_moyennes, on="id_resto")

# ordonner les restaurants par note moyenne
data = data.sort_values(by="note_moyenne", ascending=False)

# Afficher les premières lignes du DataFrame avec la nouvelle colonne
print(data)


# Fonction pour extraire les scores d'émotions
def extract_emotions(text):
    """
    Fonction qui extrait les scores d'émotions d'un texte.
    Pour chaque émotion, on calcule le score en fonction du nombre d'occurrences.
    """
    emotion_scores = NRCLex(text).raw_emotion_scores
    # Normaliser par le nombre total d'émotions détectées (optionnel)
    total = sum(emotion_scores.values())
    if total > 0:
        return {emotion: score / total for emotion, score in emotion_scores.items()}
    return emotion_scores


# Appliquer la fonction sur la colonne "review_text" et créer un DataFrame d'émotions
emotion_data = avis["review_text"].apply(extract_emotions)
emotion_df = pd.DataFrame(emotion_data.tolist())

# Ajouter les scores d'émotions au DataFrame "avis"
avis = pd.concat([avis, emotion_df], axis=1)

# Calculer les moyennes des émotions pour chaque restaurant
emotions_par_resto = avis.groupby("id_resto")[emotion_df.columns].mean()
print(emotions_par_resto)

# Fermeture de la connexion
conn.close()
