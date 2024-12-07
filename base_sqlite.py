# Ce script python a pour but de tester une implémentation de base SQLite.
# On suppose que les données sur les restaurants sont des dataframes pandas.

import pandas as pd
import sqlite3

# création bdd SQLite
connection = sqlite3.connect('restaurants.db')

data = {
    "review_text": [
        "Lovey simple meal at a bouchon. Good size portions and great taste.",
        "I had a lunch/dinner here ordering off one of their special menus. Food was excellent!",
        "We made the reservation with 'the Fork' and was pleasantly surprised by the service."
    ],
    "rating": [4.0, 4.0, 5.0],
    "user_name": ["AngryofTollcross", "graceinbeijing", "Laura M"],
    "date": ["October 18 2024", "March 1 2020", "October 27 2020"],
    "contributions": [10, 71, 1]
}
df = pd.DataFrame(data)

# création table
df.to_sql('reviews', connection, if_exists='replace', index=False)

# lecture table
df = pd.read_sql('SELECT * FROM reviews', connection)
print(df)
