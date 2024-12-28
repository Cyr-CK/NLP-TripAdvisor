import psycopg2
import json
import os
import psycopg2.extras
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Establish PostgreSQL connection

if os.environ.get("DOCKER_ENV") == "true":
    try:
        db = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            dbname=os.environ.get("POSTGRES_DBNAME"),
        )
        cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.Error as err:
        print(f"Database connection error: {err}")
else:
    try:
        db = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            dbname=os.environ.get("POSTGRES_DBNAME"),
            port=os.environ.get("POSTGRES_PORT")
        )
        cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.OperationalError as err:
        print(f"Operational error: {err}")
    except psycopg2.Error as err:
        print(f"Database connection error: {err}")
try:
    db = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=os.environ.get("POSTGRES_DBNAME"),
    )
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
except psycopg2.Error as err:
    print(f"Database connection error: {err}")

def get_all_reviews():
    try:
        cursor.execute("SELECT * FROM REVIEWS")
        reviews = cursor.fetchall()
        return pd.DataFrame([dict(review) for review in reviews])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    
def get_all_restaurants():
    try:
        cursor.execute("SELECT * FROM RESTAURANTS")
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    
def get_restaurant_by_type(restaurant_type):
    try:
        cursor.execute("SELECT * FROM RESTAURANTS WHERE restaurant_type = %s", (restaurant_type,))
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    
def get_not_downloaded_restaurants():
    try:
        cursor.execute("""
            SELECT * FROM RESTAURANTS 
            WHERE restaurant_id NOT IN (SELECT restaurant_id FROM REVIEWS)
        """)
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()

def save_reviews_to_db(restaurant_id, reviews):
    for review in reviews:
        cursor.execute(
            """
            INSERT INTO reviews (restaurant_id, user_name, review_text, date, contributions, rating)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (restaurant_id, review['user_name'], review['review_text'], review['date'], review['contributions'], review['rating'])
        )
    db.commit()
    