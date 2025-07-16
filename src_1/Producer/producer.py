from apify_client import ApifyClient
from kafka import KafkaProducer
import json
import time
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.config import Config

def run_apify_facebook_crawl_push_kafka_topic(config, URL):
    """
    Apify crawl Facebook posts, push 3 records every 30 minutes to server.
    """

    client = ApifyClient(config.API_TOKEN)

    run_input = {
        "startUrls": [{"url": URL}],
        "resultsLimit": config.RESULTS_LIMIT,
        "captionText": False,
    }
    print("[SYSTEM] Running Apify crawl...")
    run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)
    data_list = []

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        fb_post = {
            "text": item.get("text"),
            "url": item.get("url")
        }
        data_list.append(fb_post)

    print(f"[SYSTEM] Crawl completed, {len(data_list)} records fetched.")

    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )

    index = 0
    try:
        while index < len(data_list):
            batch = data_list[index:index+3]

            for record in batch:
                producer.send(config.KAFKA_TOPIC_FB_POSTS, value=record)
                print(f"[SYSTEM] Pushed: {record['text'][:30]}... to {config.KAFKA_TOPIC_FB_POSTS}")

            producer.flush()
            index += 3

            if index >= len(data_list):
                print("[SYSTEM] All records have been pushed.")
                break

            print("[SYSTEM] Sleeping 30 minutes before pushing next 3 records...")
            time.sleep(30 * 60)

    except KeyboardInterrupt:
        print("[SYSTEM] Stopped by user.")
    finally:
        producer.flush()
        producer.close()
        print("[SYSTEM] Producer closed cleanly.")

