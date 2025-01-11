import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
import altair as alt

if not nltk.data.find('tokenizers/punkt'):
    nltk.download('punkt')
elif not nltk.data.find('corpora/stopwords'):
    nltk.download('stopwords')


def clean_text(text: str) -> str:
    """
    Clean the input text by removing newlines, carriage returns, and tabs.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    txt = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    txt = txt.replace('  ', ' ')
    return txt.strip()


def extract_by_regex(text: str, regex: str) -> str:
    """
    Extract a substring from the input text using a regular expression.

    Args:
        text (str): The input text.
        regex (str): The regular expression pattern.

    Returns:
        str: The extracted substring or an empty string if no match is found.
    """
    pattern = re.compile(regex)
    match = pattern.search(text)
    if match:
        if match.groups():
            return match.group(1) + " " + match.group(2) if len(match.groups()) > 1 else match.group(1)
        else:
            return match.group(0)
    return ""


def filter_by_regex(text: str, pattern: str) -> str:
    """
    Filter the input text by removing substrings that match the regular expression pattern.

    Args:
        text (str): The input text.
        pattern (str): The regular expression pattern.

    Returns:
        str: The filtered text or None if no match is found.
    """
    match = re.sub(pattern, '', text)
    return match if match else None


def clean_text_df(df: pd.DataFrame, root_type: str = 'lemmatization') -> pd.DataFrame:
    """
    Clean the text in the dataframe by removing stop words and applying stemming or lemmatization.

    Args:
        df (pd.DataFrame): The input dataframe containing a 'review_text' column.
        root_type (str): The type of root processing to apply ('stemming' or 'lemmatization').

    Returns:
        pd.DataFrame: The dataframe with an additional 'cleaned_text' column.
    """
    stop_words = set(stopwords.words('french'))
    stemmer = SnowballStemmer('french')
    lemmatizer = nltk.WordNetLemmatizer()

    def process_text(text):
        tokens = nltk.word_tokenize(text, language='french')
        if root_type == 'stemming':
            tokens = [stemmer.stem(word) for word in tokens if word.lower() not in stop_words]
        else:
            tokens = [lemmatizer.lemmatize(word) for word in tokens if word.lower() not in stop_words]
        return ' '.join(tokens)

    df['cleaned_text'] = df['review_text'].apply(lambda x: process_text(x))

    return df


def generate_wordcloud(df: pd.DataFrame) -> WordCloud:
    """
    Generate a word cloud from the cleaned text in the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe containing 'restaurant_name' and 'cleaned_text' columns.

    Returns:
        WordCloud: The generated word cloud.
    """
    if not {'restaurant_name', 'cleaned_text'}.issubset(df.columns):
        raise ValueError("Dataframe must contain 'restaurant_name' and 'cleaned_text' columns.")

    text = " ".join(review for review in df['cleaned_text'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    return wordcloud


def generate_word_frequencies_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Generate a bar chart of the 20 most frequent words from the cleaned text in the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe containing 'cleaned_text' column.

    Returns:
        alt.Chart: The generated bar chart of word frequencies.
    """
    # Clean special characters and separations
    df['cleaned_text'] = df['cleaned_text'].str.replace(r'[^\w\s]', '', regex=True)

    # Generate word frequencies
    word_freq = Counter(" ".join(df['cleaned_text']).split())
    word_freq_df = pd.DataFrame(word_freq.items(), columns=['word', 'frequency'])

    # Get the 20 most frequent words
    word_freq_df = word_freq_df.nlargest(15, 'frequency')

    # Create bar chart
    bar_chart = alt.Chart(word_freq_df).mark_bar().encode(
        x='frequency:Q',
        y=alt.Y('word:N', sort='-x')
    ).properties(
        width=400,
        height=400
    )

    return bar_chart


def generate_word2vec(df: pd.DataFrame):
    """
    Generate a Word2Vec model from the cleaned text in the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe containing 'cleaned_text' column.

    Returns:
        Word2Vec: The generated Word2Vec model.
    """
    if len(df['restaurant_id'].unique()) < 2:
        return ("error" , "Veuillez sélectionner plus de restaurants.")
        # raise ValueError("Veuillez sélectionner plus de restaurants.")

    if not {'cleaned_text'}.issubset(df.columns):
        raise ValueError("Dataframe must contain 'cleaned_text' column.")

    ## CODE HERE##
    return ("OK" , "You'll see here your Word2Vec model")


def generate_sentiments_analysis(df: pd.DataFrame):
    """
    Analyze the sentiment of the reviews in the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe containing 'cleaned_text' column.

    Returns:
        pd.DataFrame: The dataframe with an additional 'sentiment' column.
    """
    # def get_selected_restaurants(df):
    #     st.markdown("#### Analyse de sentiments")

    #     # Choice of the restaurant from which we want to analyze the reviews.
    #     st.write("Choisissez les restaurants à analyser :")
    #     select_all2 = st.checkbox("Selectionner Tous")
    #     if select_all2:
    #         restaurant_name2 = df["restaurant_name"].to_list()
    #     else:
    #         restaurant_name2 = st.multiselect(
    #             "Restaurants choisis:",
    #             df["restaurant_name"].to_list(),
    #         )
    #     return restaurant_name2


    # def get_reviews(restaurant_ids):
    #     avis = pd.DataFrame()
    #     for id in restaurant_ids:
    #         filtered_df = get_reviews_one_restaurant(id)
    #         temp = filtered_df[["restaurant_id", "review_text", "rating"]]
    #         if avis.empty:
    #             avis = temp
    #         else:
    #             avis = pd.concat([avis, temp], axis=0)
    #     return avis


    # def calculate_sentiment(avis):
    #     avis["sentiment"] = avis["review_text"].apply(
    #         lambda x: TextBlob(x).sentiment.polarity
    #     )
    #     return avis


    # def plot_sentiment_vs_rating(data):
    #     plt.figure(figsize=(10, 6))
    #     plt.scatter(data["note_moyenne"], data["sentiment_moyen"])
    #     for _, row in data.iterrows():
    #         plt.text(
    #             row["note_moyenne"],
    #             row["sentiment_moyen"],
    #             row["restaurant_name"],
    #             fontsize=9,
    #         )
    #     plt.xlabel("Note Moyenne")
    #     plt.ylabel("Sentiment Moyen")
    #     plt.title("Sentiment Moyen vs Note Moyenne par Restaurant")
    #     st.pyplot(plt)


    # def extract_emotions(text):
    #     """
    #     Fonction qui extrait les scores d'émotions d'un texte.
    #     Pour chaque émotion, on calcule le score en fonction du nombre d'occurrences.
    #     """
    #     emotion_scores = NRCLex(text).raw_emotion_scores
    #     # Normaliser par le nombre total d'émotions détectées (optionnel)
    #     total = sum(emotion_scores.values())
    #     if total > 0:
    #         return {
    #             emotion: score / total
    #             for emotion, score in emotion_scores.items()
    #         }
    #     return emotion_scores


    # def analyze_sentiments(df):
    #     restaurant_name2 = get_selected_restaurants(df)

    #     # Button to launch the analysis
    #     if st.button("Analyse de sentiments", key="analysis_button2"):

    #         # Récupération des avis
    #         restaurant_ids = df[df["restaurant_name"].isin(restaurant_name2)][
    #             "restaurant_id"
    #         ]
    #         avis = get_reviews(restaurant_ids)

    #         # Ajout d'une colonne "sentiment" avec la polarité des avis
    #         avis = calculate_sentiment(avis)

    #         # avis par restaurant
    #         avis_par_resto = avis.groupby("restaurant_id")["sentiment"].mean()
    #         note_moyenne = avis.groupby("restaurant_id")["rating"].mean()

    #         avis_par_resto = pd.DataFrame(avis_par_resto)
    #         note_moyenne = pd.DataFrame(note_moyenne)

    #         notes_moyennes = pd.merge(avis_par_resto, note_moyenne, on="restaurant_id")
    #         notes_moyennes = notes_moyennes.rename(
    #             columns={"sentiment": "sentiment_moyen", "rating": "note_moyenne"}
    #         )

    #         # merge with restaurants
    #         data = pd.merge(df, notes_moyennes, on="restaurant_id")

    #         # Dispertion graph
    #         plot_sentiment_vs_rating(data)

    #         # Appliquer la fonction sur la colonne "review_text" et créer un DataFrame d'émotions
    #         emotion_data = avis["review_text"].apply(extract_emotions)
    #         emotion_df = pd.DataFrame(emotion_data.tolist())

    #         # Reset index to be able to concatenate
    #         avis.reset_index(drop=True, inplace=True)
    #         emotion_df.reset_index(drop=True, inplace=True)

    #         # Ajouter les scores d'émotions au DataFrame "avis"
    #         avis = pd.concat([avis, emotion_df], axis=1)

    #         # Calculer les moyennes des émotions pour chaque restaurant
    #         emotions_par_resto = avis.groupby("restaurant_id")[
    #             emotion_df.columns
    #         ].mean()
    #         st.write("Emotions moyennes par restaurant :")
    #         st.write(emotions_par_resto)

    #         st.write(
    #             "Les emotions sont présentées de manière moche pour l'instant mais cela va bouger"
    #         )

    return ("OK", "You'll see here your sentiment analysis result")


    # Replace the placeholder with the function call
    # analyze_sentiments(df)