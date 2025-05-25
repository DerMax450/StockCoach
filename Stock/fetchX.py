import snscrape.modules.twitter as sntwitter
import pandas as pd
import os
from datetime import datetime
from setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

def fetch_new_tweets(username: str, csv_file: str, limit: int = 100):
    existing_dates = set()
    
    # load csv file if there
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        existing_dates = set(df_existing['url'])
    else:
        df_existing = pd.DataFrame(columns=['date', 'time', 'content', 'url'])

    new_tweets = []

    for tweet in sntwitter.TwitterUserScraper(username).get_items():
        if tweet.url in existing_dates:
            break  # Tweets come in descending order
        new_tweets.append({
            'date': tweet.date.date().isoformat(),
            'time': tweet.date.time().isoformat(timespec='seconds'),
            'content': tweet.content.replace('\n', ' '),
            'url': tweet.url
        })
        if len(new_tweets) >= limit:
            break

    if new_tweets:
        df_new = pd.DataFrame(new_tweets)
        df_all = pd.concat([df_new, df_existing], ignore_index=True)
        df_all.to_csv(csv_file, index=False)
        print(f"{len(new_tweets)} neue Tweets gespeichert.")
    else:
        print("Keine neuen Tweets gefunden.")
