from bs4 import BeautifulSoup
import time
import requests
import random
import string
from utils.functions import clean_text, extract_by_regex, filter_by_regex

class TripAdvisorScraper:
    """
    Base class for TripAdvisor scraping.
    All other classes inherit from this.
    """
    def __init__(self):
        self.url_base = "https://www.tripadvisor.fr"
        self.soup = None
        self.url = None
        self.full_url = None

    def fetch_page(self, url):
        """Fetch a page and set the soup."""
        self.url = url
        self.full_url = self.url_base + url
        random_request_id = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(180)
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "accept-language": "en-US,en;q=0.9,fr;q=0.8",
            "X-Requested-By": random_request_id,
            "Referer": "https://www.tripadvisor.fr/Hotels",
            "Origin": "https://www.tripadvisor.fr",
            "accept-encoding": "gzip, deflate, br",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "encoding": "utf-8",
        }

        response = requests.get(self.full_url, headers=headers)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "html.parser")

    def print_soup(self):
        """Print the soup for debugging purposes."""
        if self.soup:
            print(self.soup.prettify())
        else:
            print("Soup is not initialized. Fetch the page first.")

    def get_next_url(self):
        """Get the next page's URL."""
        next_button = self.soup.find(
            "a", 
            class_="BrOJk u j z _F wSSLS tIqAi unMkR",
            attrs={"aria-label": "Page suivante"},
        )
        return next_button["href"] if next_button else None

class TripAdvisorSpecificRestaurantScraper(TripAdvisorScraper):
    """Scraper for reviews of a specific restaurant."""
    def __init__(self):
        super().__init__()
        self.restaurant_data = []

    def get_review_cards(self):
        """Extract review cards."""
        if self.soup:
            return self.soup.find_all("div", class_="_c")
        print("Soup not initialized. Fetch the page first.")
        return []

    def parse_review(self, review_card):
        """Parse data from a single review card."""
        review_text_class = "biGQs _P pZUbB KxBGd"
        contributions_class = "b"
        date_class = "biGQs _P pZUbB ncFvv osNWb"
        user_name_class = "BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS"
        rating_class = "UctUV d H0"

        review_text = review_card.find("div", class_=review_text_class).get_text(strip=True) if review_card.find("div", class_=review_text_class) else None
        contributions = review_card.find("span", class_=contributions_class).get_text(strip=True) if review_card.find("span", class_=contributions_class) else None
        date = review_card.find("div", class_=date_class).get_text(strip=True) if review_card.find("div", class_=date_class) else None
        user_name = review_card.find("a", class_=user_name_class).get_text(strip=True) if review_card.find("a", class_=user_name_class) else None
        rating = review_card.find("svg", class_=rating_class).title.text if review_card.find("svg", class_=rating_class) else None

        date = filter_by_regex(date, r"Rédigé le") if date else None
        rating = extract_by_regex(rating, r"(\d\,\d)") if rating else None
        
        return {
            "review_text": clean_text(review_text) if review_text else None,
            "contributions": contributions,
            "date": date,
            "user_name": user_name,
            "rating": rating,
        }

    def get_all_reviews(self):
        """Get all reviews from the restaurant."""
        reviews = []
        page = 1
        tries = 0
        while self.url:
            time.sleep(random.uniform(1, 3))
            review_cards = self.get_review_cards()
            if not review_cards:
                tries += 1
                if tries > 10:
                    raise Exception("No restaurant cards found - Aborting")
                else:
                    continue
            print(f"Scraping page {page}")
            tries = 0
            for card in review_cards:
                reviews.append(self.parse_review(card))
            self.url = self.get_next_url()
            if self.url:
                self.fetch_page(self.url)
            page += 1   
        return reviews

class TripAdvisorRestaurantsScraper(TripAdvisorScraper):
    """Scraper for the list of restaurants."""
    def __init__(self):
        super().__init__()
        self.restaurant_data = []

    def get_restaurant_cards(self):
        """Extract restaurant cards."""
        if self.soup:
            cards = self.soup.find_all("div", class_="vIjFZ Gi o VOEhq")
            if not cards:
                print("No restaurant cards found. Check the structure.")
            return cards
        print("Soup not initialized. Fetch the page first.")
        return []

    def parse_restaurant(self, restaurant_card):
        """Parse data from a single restaurant card."""
        name_class = "BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS"
        url_class = "BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS"
        reviews_class = "IiChw"
        median_reviews_class = "Qqwyj"

        name = restaurant_card.find("a", class_=name_class).get_text(strip=True) if restaurant_card.find("a", class_=name_class) else None
        url = restaurant_card.find("a", class_=url_class)["href"] if restaurant_card.find("a", class_=url_class) else None
        reviews = restaurant_card.find("span", class_=reviews_class).get_text(strip=True) if restaurant_card.find("span", class_=reviews_class) else None
        median_reviews = restaurant_card.find("span", class_=median_reviews_class).get_text(strip=True) if restaurant_card.find("span", class_=median_reviews_class) else None
        
        ranking, name = name.split(".", 1) if name else (None, None)
        restaurant_name_csv_clean = ''.join(e for e in name if e.isalnum() or e == ' ')
        restaurant_name_clean = restaurant_name_csv_clean.replace(' ', '_')
        url = url
        reviews = filter_by_regex(reviews, r'\W+') if reviews else None
        avg_review = extract_by_regex(median_reviews, r"(\d\,\d)") if median_reviews else None
        
        
        return {
            "ranking": ranking,
            "name": name,
            "url": url,
            "avg_review": avg_review,
            "total_reviews": extract_by_regex(reviews, r"(\d+)?") if reviews else None,
            "filename": restaurant_name_clean,
        }

    def get_all_restaurants(self):
        """Get all restaurants."""
        restaurants = []
        page = 1
        tries = 0
        while self.url is not None:
            time.sleep(random.uniform(1, 3))
            self.fetch_page(self.url)
            restaurant_cards = self.get_restaurant_cards()
            if not restaurant_cards:
                tries += 1
                if tries > 10:
                    raise Exception("No restaurant cards found - Aborting")
                else:
                    continue
            print(f"Scraping page {page}")
            tries = 0
            for card in restaurant_cards:
                restaurant = self.parse_restaurant(card)
                if restaurant:
                    restaurants.append(restaurant)
            self.url = self.get_next_url()
            page += 1
        return restaurants
