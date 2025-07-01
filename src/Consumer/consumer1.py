from kafka import KafkaConsumer
from kafka import KafkaProducer

import os
import google.generativeai as genai
import json
import pandas as pd
import re
import requests
from io import StringIO
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.config import Config
os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from module_ner.LLM_langchain import *

# consumer = KafkaConsumer(
#     'fb_posts',
#     bootstrap_servers='localhost:9092',
#     auto_offset_reset='earliest',
#     group_id='fb_posts_viewer',
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )

# for message in consumer:
#     print(message.value)

def run_consumer_extract_push_kafka(config: Config):
    # Khởi tạo consumer nhận từ topic fb_posts
    consumer = KafkaConsumer(
        config.KAFKA_TOPIC_FB_POSTS, 
        bootstrap_servers=config.KAFKA_SERVERS, 
        auto_offset_reset='earliest',
        group_id='fb_posts_viewer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # Khởi tạo producer để push lên topic mới
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )


    print("[SYSTEM] Consumer started, waiting for messages...")

    try:
        for message in consumer:
            data = message.value
            print(f"Received: {data}")

            # Gọi extract NER
            extracted_result = ner_extract(data["text"])
            full_result = {}
            full_result["text"] = data["text"]
            full_result["label"] = {}
            for place_dict in extracted_result:
                place = place_dict['text']
                label = place_dict['label']

                result_payload = {
                    "place": place,
                    "label": label
                }
                full_result["label"][place] = label
                # Push lên topic mới
                producer.send(config.KAFKA_TOPIC_COMMENTS, result_payload)
                # print(f"[SYSTEM] Pushed NER result to {config.KAFKA_TOPIC_COMMENTS}: {result_payload}")

            with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\ner_results.json", "w", encoding="utf-8") as f:
                    json.dump(full_result, f, ensure_ascii=False)

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        consumer.close()
        producer.flush()
        producer.close()