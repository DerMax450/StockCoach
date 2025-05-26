import feedparser
import csv
import os
from datetime import datetime
from typing import List
from services.setupLogger import setup_logger
from services.configLoader import load_config

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

# Get all RSS feed links
feed_urls = load_config("feeds")

def fetch_and_store_rss_feeds(data, output_dir: str = ".", file_prefix: str = "rss_feed"):
    logger.info("Load some rss feeds...")
    os.makedirs(output_dir, exist_ok=True)

    for url in feed_urls:
        logger.debug("Fetch from URL: {url}")
        feed = feedparser.parse(url)
        feed_id = url.split("//")[-1].split("/")[0].replace(".", "_")
        csv_file = os.path.join(output_dir, f"{file_prefix}_{feed_id}.csv")

        existing_titles = set()
        if os.path.exists(csv_file):
            with open(csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_titles = {row['title'] for row in reader}

        new_entries = []
        for entry in feed.entries:
            if entry.title not in existing_titles:
                published = entry.get("published", datetime.utcnow().isoformat())
                try:
                    published_parsed = datetime(*entry.published_parsed[:6]).isoformat()
                except:
                    published_parsed = published
                new_entries.append({
                    "datetime": published_parsed,
                    "title": entry.title,
                    "link": entry.link
                })

        if new_entries:
            file_exists = os.path.exists(csv_file)
            with open(csv_file, mode='a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["datetime", "title", "link"])
                if not file_exists:
                    writer.writeheader()
                for entry in new_entries:
                    writer.writerow(entry)

            logger.info(f"{len(new_entries)} new entries added to {csv_file}")
        else:
            logger.info(f"No new entries for {url}")