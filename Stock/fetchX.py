import requests
import pandas as pd
import os
from datetime import datetime
from setupLogger import setup_logger
import certifi
from configLoader import load_config

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

# Logging & Zertifikate setzen
logger = setup_logger(__name__, "logs/stockAnalyzer.log")

logger.info(certifi.where())
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

BEARER_TOKEN = load_config("X-Bearer")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def get_user_id(username: str) -> str:
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()['data']['id']

def fetch_tweets(username: str, csv_file: str, limit: int = 100):
    logger.info(f"Fetching tweets from {username}...")
    
    try:
        user_id = get_user_id(username)
    except Exception as e:
        logger.error(f"Could not resolve user '{username}': {e}")
        return

    existing_ids = set()
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        if "id" in df_existing.columns:
            existing_ids = set(df_existing['id'].astype(str))
        else:
            logger.warning("CSV has no 'id' column, ignoring duplicate check")
    else:
        df_existing = pd.DataFrame(columns=['date', 'time', 'content', 'url', 'id'])

    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": min(limit, 100),  # API limit: max 100
        "tweet.fields": "created_at"
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params)
        r.raise_for_status()
        tweets = r.json().get("data", [])
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return

    new_tweets = []
    for tweet in tweets:
        tweet_id = str(tweet['id'])
        if tweet_id in existing_ids:
            continue
        created_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
        new_tweets.append({
            "date": created_at.date().isoformat(),
            "time": created_at.time().isoformat(timespec='seconds'),
            "content": tweet["text"].replace('\n', ' '),
            "url": f"https://twitter.com/{username}/status/{tweet_id}",
            "id": tweet_id
        })

    if new_tweets:
        df_new = pd.DataFrame(new_tweets)
        df_all = pd.concat([df_new, df_existing], ignore_index=True)
        df_all.to_csv(csv_file, index=False)
        logger.info(f"{len(new_tweets)} neue Tweets gespeichert in '{csv_file}'.")
    else:
        logger.info("Keine neuen Tweets gefunden.")
