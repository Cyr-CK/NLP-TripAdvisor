import psycopg2
import os
import psycopg2.extras
import pandas as pd
import platform

if platform.system() == "Windows":
    from dotenv import load_dotenv
    import os

    # Specify the path to your .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

    # Load the .env file
    load_dotenv(dotenv_path)
else:
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
            port=os.environ.get("POSTGRES_PORT"),
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
    """
    Get all reviews from the database.
    """
    try:
        cursor.execute("SELECT * FROM REVIEWS")
        reviews = cursor.fetchall()
        return pd.DataFrame([dict(review) for review in reviews])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()


def get_reviews_one_restaurant(restaurant_id):
    """
    Get all reviews of a restaurant from the database.
    """
    try:
        cursor.execute(f"SELECT * FROM REVIEWS WHERE restaurant_id = {restaurant_id}")
        reviews = cursor.fetchall()
        return pd.DataFrame([dict(review) for review in reviews])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()


def get_all_restaurants():
    """
    Get all restaurants from the database.
    """
    try:
        cursor.execute("SELECT * FROM RESTAURANTS")
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()


def get_restaurant_by_type(restaurant_type):
    """
    Get all restaurants of a specific type from the database.
    """
    try:
        cursor.execute(
            "SELECT * FROM RESTAURANTS WHERE restaurant_type = %s", (restaurant_type,)
        )
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()


def get_not_downloaded_restaurants():
    """
    Get all restaurants that have not been downloaded yet.
    """
    try:
        cursor.execute(
            """
            SELECT * FROM RESTAURANTS 
            WHERE restaurant_id NOT IN (SELECT restaurant_id FROM REVIEWS)
        """
        )
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()


def save_reviews_to_db(restaurant_id, reviews):
    """
    Save the reviews of a restaurant to the database.
    """
    for review in reviews:
        cursor.execute(
            """
            INSERT INTO reviews (restaurant_id, user_name, review_text, date, contributions, rating)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                restaurant_id,
                review["user_name"],
                review["review_text"],
                review["date"],
                review["contributions"],
                review["rating"],
            ),
        )
    db.commit()
