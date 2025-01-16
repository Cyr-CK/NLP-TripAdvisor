import os
import platform
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv

if platform.system() == "Windows":
    # Specify the path to your .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    # Load the .env file
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Establish PostgreSQL connection
try:
    db = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=os.environ.get("POSTGRES_DBNAME"),
        port=os.environ.get("POSTGRES_PORT")
    )
except psycopg2.OperationalError as err:
    print(f"Operational error: {err}")
except psycopg2.Error as err:
    print(f"Database connection error: {err}")


def get_cursor():
    """
    Validate and obtain a cursor for database operations.

    Returns:
        cursor: A database cursor.
    """
    try:
        return db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.Error as err:
        print(f"Error obtaining cursor: {err}")
        return None


def get_all_reviews():
    """
    Fetch all reviews from the database.

    Returns:
        pd.DataFrame: DataFrame containing all reviews.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        cursor.execute("SELECT * FROM REVIEWS")
        reviews = cursor.fetchall()
        return pd.DataFrame([dict(review) for review in reviews])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()


def get_all_restaurants():
    """
    Fetch all restaurants from the database.

    Returns:
        pd.DataFrame: DataFrame containing all restaurants.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        cursor.execute("SELECT * FROM RESTAURANTS")
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()


def get_restaurant_by_type(restaurant_type):
    """
    Fetch restaurants by type from the database.

    Args:
        restaurant_type (str): The type of restaurant to fetch.

    Returns:
        pd.DataFrame: DataFrame containing restaurants of the specified type.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        cursor.execute(
            "SELECT * FROM RESTAURANTS WHERE restaurant_type = %s",
            (restaurant_type,)
        )
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()


def get_not_downloaded_restaurants():
    """
    Fetch restaurants that have not been downloaded yet.

    Returns:
        pd.DataFrame: DataFrame containing restaurants not downloaded.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
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
    finally:
        cursor.close()


def save_reviews_to_db(restaurant_id, reviews):
    """
    Save reviews to the database.

    Args:
        restaurant_id (int): The ID of the restaurant.
        reviews (list): List of reviews to save.
    """
    cursor = get_cursor()
    if cursor is None:
        return
    try:
        for review in reviews:
            cursor.execute(
                """
                INSERT INTO reviews (restaurant_id, user_name, review_text, date, contributions, rating)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    restaurant_id, review['user_name'], review['review_text'],
                    review['date'], review['contributions'], review['rating']
                )
            )
        db.commit()
    except psycopg2.Error as err:
        print(err)
    finally:
        cursor.close()


def get_downloaded_restaurants():
    """
    Fetch restaurants that have been downloaded.

    Returns:
        pd.DataFrame: DataFrame containing downloaded restaurants.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        cursor.execute("""
            SELECT r.restaurant_id,
                r.restaurant_name,
                r.restaurant_avg_review,
                r.restaurant_price,
                r.restaurant_type, 
                r.restaurant_total_reviews,
                r.restaurant_url,
                l.address,
                l.latitude, 
                l.longitude 
            FROM restaurants r
            JOIN locations l ON r.restaurant_id = l.restaurant_id
            WHERE r.restaurant_id IN (SELECT restaurant_id FROM REVIEWS)
        """)
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()


def get_restaurant_by_id(restaurant_ids):
    """
    Fetch restaurants by their IDs.

    Args:
        restaurant_ids (list): List of restaurant IDs to fetch.

    Returns:
        pd.DataFrame: DataFrame containing restaurants with the specified IDs.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        query = """
            SELECT 
                r.restaurant_id,
                r.restaurant_name,
                r.restaurant_avg_review,
                r.restaurant_type,
                l.latitude,
                l.longitude,
                r2.rating,
                r2.review_text,
                r2.contributions 
            FROM restaurants r
            JOIN locations l ON l.restaurant_id = r.restaurant_id
            JOIN reviews r2 ON r2.restaurant_id = r.restaurant_id 
            WHERE r.restaurant_id IN (%s)
        """ % ",".join(list(map(str, restaurant_ids)))
        cursor.execute(query)
        restaurants = cursor.fetchall()
        return pd.DataFrame([dict(restaurant) for restaurant in restaurants])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()


def get_reviews_one_restaurant(id):
    """
    Fetch reviews for a specific restaurant.

    Args:
        id (int): The ID of the restaurant.

    Returns:
        pd.DataFrame: DataFrame containing reviews for the specified restaurant.
    """
    cursor = get_cursor()
    if cursor is None:
        return pd.DataFrame()
    try:
        cursor.execute(
            "SELECT * FROM REVIEWS WHERE restaurant_id = %s",
            (int(id),)
        )
        reviews = cursor.fetchall()
        print(reviews)
        return pd.DataFrame([dict(review) for review in reviews])
    except psycopg2.Error as err:
        print(err)
        return pd.DataFrame()
    finally:
        cursor.close()