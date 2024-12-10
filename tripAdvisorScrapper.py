from bs4 import BeautifulSoup
import time
import requests
import random
import string

from utils.functions import clean_text, extract_by_regex


class TripAdvisorScraper:
    """
    Base class for TripAdvisor scraping.
    All the other classes will inherit from this one.
    """

    def __init__(self):
        self.url_base = "https://www.tripadvisor.com"
        self.soup = None
        self.url = None

    def fetch_page(self, url):
        """
        Fetch the page and set the soup.
        """
        self.url = self.url_base + url
        # Set headers
        random_request_id = "".join(
            random.choice(string.ascii_lowercase + string.digits) for i in range(180)
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "accept-language": "en-US,en;q=0.9,fr;q=0.8",
            "X-Requested-By": random_request_id,
            "Referer": "https://www.tripadvisor.com/Hotels",
            "Origin": "https://www.tripadvisor.com",
            "accept-encoding": "gzip, deflate, br",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "encoding": "utf-8",
        }

        # Send a GET request
        response = requests.get(self.url, headers=headers)
        try:
            # Check encoding

            if response.headers.get("Content-Encoding") == "gzip":
                content = response.content.decode("gzip")
            elif response.headers.get("Content-Encoding") == "deflate":
                content = response.content.decode("zlib")
            # elif response.headers.get('Content-Encoding') == 'br':
            #     content = brotli.decompress(response.content)
            else:
                content = response.text

        except Exception as e:
            print(f"Error: {e}")
            content = response.text
        finally:
            self.soup = BeautifulSoup(content, "html.parser")

    def print_soup(self):
        """
        print the soup
        """
        if self.soup:
            print(self.soup.prettify())
        else:
            print("Soup is not initialized. Please fetch the page first.")


class TripAdvisorSpecificRestaurantScrapper(TripAdvisorScraper):
    """
    Class to scrap the reviews of a specific restaurant.
    Inherits from the TripAdvisorScraper class.
    """

    def __init__(self):
        super().__init__()
        self.restaurant_data = []

    def get_review_cards(self):
        """
        Get the review cards from the soup.
        """
        if self.soup:
            review_cards = self.soup.find_all(
                "div", class_="_c", attrs={"data-automation": "reviewCard"}
            )
            return review_cards
        print("Soup is not initialized. Please fetch the page first.")
        return []

    def get_review_page(self, review_cards):
        """
        Extract the review data from the review cards.
        """
        corpus = []
        for card in review_cards:
            # Extract the review text
            review_text = "biGQs _P pZUbB KxBGd"
            contributions = "biGQs _P pZUbB osNWb"
            date = "biGQs _P pZUbB ncFvv osNWb"
            user_name = "biGQs _P fiohW fOtGX"
            rating = "UctUV d H0"

            scrap_review_text = (
                card.find("div", {"class": review_text}).text
                if card.find("div", {"class": review_text})
                else None
            )
            scrap_contributions = (
                card.find("div", {"class": contributions}).text
                if card.find("div", {"class": contributions})
                else None
            )
            scrap_date = (
                card.find("div", {"class": date}).text
                if card.find("div", {"class": date})
                else None
            )
            scrap_user_name = (
                card.find("span", {"class": user_name}).text
                if card.find("span", {"class": user_name})
                else None
            )
            scrap_rating = (
                card.find("svg", {"class": rating}).find("title").text
                if card.find("svg", {"class": rating})
                else None
            )

            doc = {
                "rating": (
                    extract_by_regex(scrap_rating, r"(\d\.\d) of 5 bubbles")
                    if scrap_rating is not None and scrap_rating != ""
                    else None
                ),
                "user_name": (
                    scrap_user_name
                    if scrap_user_name is not None and scrap_user_name != ""
                    else None
                ),
                "date": (
                    extract_by_regex(scrap_date, r"(\w+ \d+), (\d+)")
                    if scrap_date is not None and scrap_date != ""
                    else None
                ),
                "contributions": (
                    extract_by_regex(scrap_contributions, r"\d+")
                    if scrap_contributions is not None and scrap_contributions != ""
                    else None
                ),
                "review_text": (
                    clean_text(scrap_review_text)
                    if scrap_review_text is not None and scrap_review_text != ""
                    else None
                ),
            }
            corpus.append(doc)

        return corpus

    def get_all_pages(self):
        """
        Get all the reviews of the restaurant
        """
        page = 1
        corpus = []
        while self.url is not None:
            time.sleep(random.uniform(1, 3))
            new_cards = self.get_review_cards()
            if len(new_cards) == 0:
                break
            new_reg = self.get_review_page(new_cards)
            corpus.extend(new_reg)
            print(f"Page {page} done")
            page += 1
            url = self.get_next_url()
            if url is not None:
                self.fetch_page(url)
            else:
                break
        return corpus

    def get_next_url(self):
        """
        Get the next url to scrap
        """
        next_url = self.soup.find(
            "a",
            class_="BrOJk u j z _F wSSLS tIqAi unMkR",
            attrs={"aria-label": "Next page"},
        )
        if next_url is not None:
            return next_url.get("href")
        else:
            return None


class TripAdvisorRestaurantsScrapper(TripAdvisorScraper):
    """
    Class to scrap the list of restaurants.
    """

    def __init__(self):
        super().__init__()
        self.restaurant_data = []

    def get_restaurants_cards(self):
        """
        Get the restaurant cards from the soup.
        """
        if self.soup:
            restaurant_cards = self.soup.find_all("div", class_="qeraN")
            return restaurant_cards
        else:
            print("Soup is not initialized. Please fetch the page first.")
            return []

    def get_next_url(self):
        """
        Get the next url to scrap
        """
        next_url = self.soup.find(
            "a",
            class_="BrOJk u j z _F wSSLS tIqAi unMkR",
            attrs={"aria-label": "Next page"},
        )
        if next_url is not None:
            return next_url.get("href")
        else:
            return None

    def extract_restaurant_data(self, restaurant_cards):
        """
        Extract the restaurant data from the restaurant cards.
        """
        corpus = []
        # restaurant_name = "biGQs _P fiohW alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU mtnKn ngXxk"
        # # non utilisé donc commenté

        restaurant_url = "BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS"
        restaurant_reviews = "jVDab W f u w JqMhy"
        for restaurant_card in restaurant_cards:
            scrap_restaurant_name = (
                restaurant_card.find("a", {"class": restaurant_url}).text
                if restaurant_card.find("a", {"class": restaurant_url})
                else None
            )
            scrap_restaurant_url = (
                restaurant_card.find("a", {"class": restaurant_url}).get("href")
                if restaurant_card.find("a", {"class": restaurant_url})
                else None
            )
            scrap_restaurant_reviews = (
                restaurant_card.find("div", {"class": restaurant_reviews}).get(
                    "aria-label"
                )
                if restaurant_card.find("div", {"class": restaurant_reviews})
                else None
            )

            doc = {
                "restaurant_class": (
                    scrap_restaurant_name.split(".")[0].strip()
                    if scrap_restaurant_name is not None
                    else None
                ),
                "restaurant_name": (
                    scrap_restaurant_name.split(".")[1].strip()
                    if scrap_restaurant_name is not None
                    else None
                ),
                "restaurant_url": (
                    scrap_restaurant_url
                    if scrap_restaurant_url is not None and scrap_restaurant_url != ""
                    else None
                ),
                "restaurant_reviews": (
                    scrap_restaurant_reviews
                    if scrap_restaurant_reviews is not None
                    else None
                ),
            }
            corpus.append(doc)
        return corpus

    def get_all_pages(self):
        """
        Get all the restaurants
        """
        page = 1
        corpus = []
        while self.url is not None:
            time.sleep(random.uniform(1, 3))
            new_cards = self.get_restaurants_cards()
            new_reg = self.extract_restaurant_data(new_cards)
            corpus.extend(new_reg)
            print(f"Page {page} done")
            page += 1
            url = self.get_next_url()
            if url is not None:
                self.fetch_page(url)
            else:
                break
        return corpus
