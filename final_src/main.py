import json
import numpy as np
import pandas as pd
import os
from transformers import AutoModelForTokenClassification, AutoTokenizer
import pickle
import torch

from pathlib import Path
import sys
sys.path.append(r'F:\Studies\Third_year\Big_data\Final_Code')
from final_src.config import Config

drinkplaces_aspects = ['DRINK#QUALITY',
 'DRINK#VARIETY',
 'ENVIRONMENT#CLEANLINESS',
 'ENVIRONMENT#AMBIENCE',
 'FOOD#QUALITY',
 'LOCATION',
 'PRICE',
 'SERVICE#ORDER',
 'SERVICE#STAFF']

hotels_aspects = ['HOTEL#LOCATION',
 'HOTEL#QUALITY',
 'HOTEL#FACILITIES',
 'HOTEL#STYLE',
 'WIFI',
 'PRICE',
 'ROOM#QUALITY',
 'ROOM#STYLE',
 'ROOM#FACILITIES',
 'ROOM#SOUND',
 'ROOM#VIEW',
 'ROOM#ATMOSPHERE',
 'ROOM#CLEANLINESS',
 'SERVICE#STAFF',
 'SERVICE#CHECKIN']

restaurants_aspects = ['LOCATION',
 'PRICE',
 'FOOD#QUALITY',
 'FOOD#VARIETY',
 'FOOD#PRESENTATION',
 'FOOD#FRESHNESS',
 'DRINK#QUALITY',
 'ENVIRONMENT#CLEANLINESS',
 'ENVIRONMENT#AMBIENCE',
 'SERVICE#STAFF',
 'SERVICE#ORDER']

eateries_aspects = ['LOCATION',
 'PRICE',
 'FOOD#QUALITY',
 'FOOD#VARIETY',
 'DRINK#QUALITY',
 'DRINK#VARIETY',
 'ENVIRONMENT#CLEANLINESS',
 'ENVIRONMENT#AMBIENCE',
 'SERVICE#STAFF',
 'SERVICE#ORDER']

attractions_aspects = ['LOCATION',
 'PRICE',
 'SERVICE#STAFF',
 'ENVIRONMENT#SCENERY',
 'ENVIRONMENT#ATMOSPHERE',
 'EXPERIENCE#ACTIVITY']

rents_aspects = ['LOCATION', 'PRICE', 'SERVICE#RENTING', 'SERVICE#STAFF', 'VEHICLE#QUALITY']

tours_aspects = ['LOCATION',
 'PRICE',
 'SERVICE#STAFF',
 'EXPERIENCE#ACTIVITY',
 'ENVIRONMENT#SCENERY',
 'ENVIRONMENT#ATMOSPHERE']

campings_aspects = ['LOCATION#DISTANCE',
 'LOCATION#ACCESSIBILITY',
 'SERVICE#STAFF',
 'ENVIRONMENT#SCENERY',
 'ENVIRONMENT#WEATHER',
 'ENVIRONMENT#ATMOSPHERE']

sentiment_map = {
    1: 'NEGATIVE',
    2: 'NEUTRAL',
    3: 'POSITIVE'
}

label_list = ['B-TOUR', 'B-RENT', 'B-RESTAURANT', 'I-RESTAURANT', 'B-ATTRACTION', 'I-TOUR', 'I-EATERY', 'O', 'B-HOTEL', 'I-HOTEL', 'I-ATTRACTION', 'I-CAMPING', 'B-EATERY', 'B-DRINKPLACE', 'I-RENT', 'B-CAMPING', 'I-DRINKPLACE']
label_map = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for i, label in enumerate(label_list)}



# Queue dùng để giao tiếp giữa thread consumer và giao diện
def main():
    config = Config()
producer_thread = threading.Thread(
                    target=push_text_and_run_consumer,
                    args=(config, text),
                    daemon=True
                )
                consumer_thread = threading.Thread(
                    target=run_consumer_extract_push_kafka,
                    args=(config,),
                    daemon=True
                )

                producer_thread.start()
                consumer_thread.start()
 