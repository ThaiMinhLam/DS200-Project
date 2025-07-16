from kafka import KafkaConsumer, KafkaProducer
from apify_client import ApifyClient
import json
import time
from collections import defaultdict
import os

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.config import Config
from src.module_absa.LLM_langchain_absa import *
os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY2
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

def run_consumer_crawl_reviews_push_kafka(config):
    # Initialize Apify client
    client = ApifyClient(config.API_TOKEN)

    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        config.KAFKA_TOPIC_COMMENTS,
        bootstrap_servers=config.KAFKA_SERVERS,
        auto_offset_reset='earliest',
        group_id='gg_comments_crawler',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8')
    )

    print("[SYSTEM] Google Maps Reviews Crawler Consumer started, waiting for messages...")

    try:
        for message in consumer:
            data = message.value
            # print(data)
            place_name = data.get("place")
            domain = data.get("label")
            # print(place_name)
            # print(type)
            if not place_name:
                print("[WARN] No place name found, skipping...")
                continue

            print(f"[INFO] Crawling reviews for: {place_name}")

            # Prepare Apify actor input
            run_input = {
                "searchStringsArray": [place_name],
                "locationQuery": "Đà Lạt, Việt Nam", 
                "maxCrawledPlacesPerSearch": 1,  
                "language": "vi",
                "searchMatching": "all",
                "placeMinimumStars": "",
                "website": "allPlaces",
                "skipClosedPlaces": False,
                "scrapePlaceDetailPage": False,
                "scrapeTableReservationProvider": False,
                "includeWebResults": False,
                "scrapeDirectories": False,
                "maxQuestions": 0,
                "scrapeContacts": False,
                "maximumLeadsEnrichmentRecords": 0,
                "maxReviews": 10,
                "reviewsSort": "newest",
                "reviewsFilterString": "",
                "reviewsOrigin": "all",
                "scrapeReviewsPersonalData": False,
                "maxImages": 0,
                "scrapeImageAuthors": False,
                "allPlacesNoSearchAction": "",
            }

            try:
                # Run actor and wait for it to finish
                run = client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)
                aspect_counts = defaultdict(lambda: defaultdict(int))
                all_reviews = []
                url = next(client.dataset(run["defaultDatasetId"]).iterate_items())["url"]


                if url != []:
                    run_input = {
                        "startUrls": [{ "url": url }],
                        "maxReviews": 10,
                        "reviewsSort": "newest",
                        "language": "vi",
                        "reviewsOrigin": "all",
                        "personalData": False,
                    }

                    # Run the Actor and wait for it to finish
                    run2 = client.actor("Xb8osYTtOjlsgI6k9").call(run_input=run_input)
                    for item in client.dataset(run2["defaultDatasetId"]).iterate_items():
                        text = item.get("text", "")
                        if text == "":
                            continue

                        aspects_list = ASPECTS_DICT.get(domain, [])
                        if not aspects_list:
                            print(f"[WARN] No aspects configured for domain {domain}, skipping ABSA.")
                            continue

                        try:
                            prediction = absa_extract(
                                text=text,
                                domain=domain,
                                aspects_list=aspects_list
                            )
                        except Exception as e:
                            print(f"[ERROR] ABSA prediction failed for review: {e}")
                            prediction = []

                        print(f"[PREDICTED] {prediction}")

                        # Update statistics
                        if isinstance(prediction, list):
                            for item in prediction:
                                aspect = item.get("aspect")
                                sentiment = item.get("sentiment")
                                if aspect and sentiment:
                                    aspect_counts[aspect][sentiment] += 1

                        # Push predict + review to Kafka
                        payload = {
                            "place_name": place_name,
                            "domain": domain,
                            "review_text": text,
                            "absa_prediction": prediction
                        }
                        all_reviews.append(payload)
                        # producer.send(config.KAFKA_TOPIC_FB_COMMENTS_RAW, payload)
                        # print(f"[PUSHED] {payload}")

                with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\crawled_reviews.json", "w", encoding="utf-8") as f:
                    json.dump(all_reviews, f, ensure_ascii=False, indent=2)
                summary_output = {}
                for aspect, sentiments in aspect_counts.items():
                    summary_output[aspect] = dict(sentiments)
                with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\summary_statistics.json", "w", encoding="utf-8") as f:
                    json.dump(summary_output, f, ensure_ascii=False, indent=2)

                # Print summary statistics
                print(f"\n===== SUMMARY FOR {place_name} ({domain}) =====")
                for aspect, sentiments in aspect_counts.items():
                    sentiment_summary = " | ".join([f"{senti}: {count}" for senti, count in sentiments.items()])
                    print(f"{aspect}: {sentiment_summary}")
                print("=" * 60 + "\n")

                time.sleep(2)

            except Exception as e:
                print(f"[ERROR] Failed to crawl or predict for {place_name}: {e}")

    except KeyboardInterrupt:
        print("[SYSTEM] Stopped by user.")
    finally:
        consumer.close()
        producer.flush()
        producer.close()

            #         for review in reviews:
            #             # review_payload = {
            #             #     "place_name": place_title,
            #             #     "user_name": review.get("name", ""),
            #             #     "rating": review.get("rating", ""),
            #             #     "review_text": review.get("text", ""),
            #             #     "published_at": review.get("publishedAtDate", "")
            #             # }
            #             review_text = review.get("text", "")
            #             if not review_text.strip():
            #                 continue
            #             review_payload = {
            #                 "review_text": review.get("text", "")
            #             }

            #             # Push to Kafka
            #             producer.send(config.KAFKA_TOPIC_FB_COMMENTS_RAW, review_payload)
            #             print(f"[PUSHED] {review_payload}")

            #     time.sleep(2)  # tránh spam API

            # except Exception as e:
            #     print(f"[ERROR] Failed to crawl reviews for {place_name}: {e}")

    # except KeyboardInterrupt:
    #     print("Stopped by user.")
    # finally:
    #     consumer.close()
    #     producer.flush()
    #     producer.close()
if __name__ == "__main__":
    config = Config()
    run_consumer_crawl_reviews_push_kafka(config)