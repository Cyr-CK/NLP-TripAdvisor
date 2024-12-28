"""
This Python script aims to test an implementation of an SQLite database.
We assume that the data on the restaurants are pandas dataframes.
"""

import os
import sqlite3

conn = sqlite3.connect("tripadvisor.db")
cursor = conn.cursor()


def execute_sql_file(cursor, filepath):
    with open(filepath, 'r') as file:
        sql_script = file.read()
    cursor.executescript(sql_script)


# Create SQLite database
def create_db():
    """
    Function that creates the SQLite database tripadvisor.db
    Tables: restaurants, location, reviews
    """
    script_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(script_dir, 'sql', 'init.sql')
    execute_sql_file(cursor, sql_file_path)

def set_restaurants():
    """
    Function that inserts data into the restaurants table
    """
    script_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(script_dir, 'sql', 'set_restaurants.sql')
    execute_sql_file(cursor, sql_file_path)

def set_reviews():
    """
    Function that inserts data into the reviews table
    """
    script_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(script_dir, 'sql', 'set_reviews.sql')
    execute_sql_file(cursor, sql_file_path)

def set_locations():
    """
    Function that inserts data into the location table
    """
    script_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(script_dir, 'sql', 'set_locations.sql')
    execute_sql_file(cursor, sql_file_path)


if __name__ == "__main__":
    create_db()
    set_restaurants()
    set_reviews()
    set_locations()

    # READ DATA
    print("Table restaurants")
    cursor.execute("SELECT * FROM restaurants;")
    print(cursor.fetchall())

    print("Table reviews")
    cursor.execute("SELECT * FROM reviews ORDER BY RANDOM() LIMIT 100;")
    print(cursor.fetchall())

    # Close the connection
    conn.close()
