import os
import requests
import pandas as pd
from textblob import TextBlob
import mysql.connector
from dotenv import load_dotenv

print("data_processor.py: Script loaded, loading environment variables...")
load_dotenv() # Load environment variables from .env file

NEWSAPI_API_KEY = os.getenv('NEWSAPI_API_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

print(f"data_processor.py: DB_HOST={DB_HOST}, DB_USER={DB_USER}, DB_NAME={DB_NAME}")

def get_financial_news(query="economy", api_key=NEWSAPI_API_KEY):
    print(f"data_processor.py: Fetching news for query: '{query}'")
    if not api_key:
        print("data_processor.py: NEWSAPI_API_KEY is not set. Cannot fetch news.")
        return None

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=relevancy&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        print(f"data_processor.py: Fetched {len(data.get('articles', []))} articles.")
        return data.get('articles')
    except requests.exceptions.RequestException as e:
        print(f"data_processor.py: Error fetching news: {e}")
        return None
    except ValueError as e: # Catch JSON decoding errors
        print(f"data_processor.py: Error decoding JSON response: {e}")
        return None

def analyze_sentiment(text):
    if not text:
        return 0.0
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def process_news_data(articles):
    print("data_processor.py: Processing news data...")
    if not articles:
        return []

    processed_data = []
    for article in articles:
        title = article.get('title')
        description = article.get('description')
        published_at = article.get('publishedAt')
        
        sentiment_score = analyze_sentiment(description) if description else analyze_sentiment(title)

        processed_data.append({
            'title': title,
            'description': description,
            'published_at': published_at,
            'sentiment_score': sentiment_score
        })
    
    # Optionally convert to DataFrame for more complex processing
    df = pd.DataFrame(processed_data)
    print("data_processor.py: News data processed into DataFrame.")
    
    # Store processed data in DB (optional, can be done periodically or on demand)
    # For now, we'll just return it. You can add a function to save to DB here.
    return df.to_dict(orient='records') # Return as list of dictionaries for Flask template

def init_db():
    print("data_processor.py: init_db() called, attempting database connection...")
    conn = None # Initialize conn to None
    cursor = None # Initialize cursor to None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        print("data_processor.py: Connected to database.")

        # Create news table if it doesn't exist
        # Using TEXT for description to allow longer content
        # Using VARCHAR(255) for title
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description TEXT,
                published_at DATETIME,
                sentiment_score FLOAT
            )
        """)
        conn.commit()
        print("data_processor.py: News table checked/created.")

    except mysql.connector.Error as err:
        print(f"data_processor.py: Database error during init_db: {err}")
        # IMPORTANT: If init_db fails, the app will likely crash later.
        # For a dev setup, printing is fine. For production, you might want more robust error handling.
    except Exception as e:
        print(f"data_processor.py: An unexpected error occurred during init_db: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("data_processor.py: Database connection closed after init_db.")

# Example usage (for testing purposes, not part of the Flask app flow)
if __name__ == '__main__':
    print("data_processor.py: Running example usage directly.")
    # Example: Test get_financial_news
    # news_articles = get_financial_news("tech stocks")
    # if news_articles:
    #     processed = process_news_data(news_articles)
    #     print(f"Processed {len(processed)} articles.")
    # else:
    #     print("No articles fetched.")
    
    # Test init_db
    init_db()
    print("data_processor.py: init_db() test complete.")