from kafka import KafkaConsumer, KafkaProducer
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

def merge_subwords(tokens, labels):
    merged_tokens = []
    merged_labels = []

    current_token = ""
    current_label = None

    for token, label in zip(tokens, labels):
        if token.endswith('@@'):  # Subword token
            current_token += token[:-2]  # Bỏ @@ và nối vào
            if current_label is None:
                current_label = label  # Lấy label đầu tiên (B- hoặc I-)
        else:
            current_token += token  # Token đầy đủ, nối vào
            if current_label is None:
                current_label = label
            merged_tokens.append(current_token)
            merged_labels.append(current_label)
            current_token = ""
            current_label = None

    # Nếu còn token cuối
    if current_token:
        merged_tokens.append(current_token)
        merged_labels.append(current_label)

    return merged_tokens, merged_labels


def predict_ner(text, model, tokenizer, id2label):
    # Tokenize
    # text = text.lower()
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        is_split_into_words=False
    )

    # Predict
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)

    # Decode tokens và labels
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    labels = [id2label[label_id.item()] for label_id in predictions[0]]
    # print(labels)
    new_tokens, new_lables = merge_subwords(tokens[1:-1], labels[1:-1])
    # Hiển thị sạch
    # for token, label in zip(new_tokens, new_lables):
    #     # token_clean = token.replace("▁", "") if "▁" in token else token
    #     # print(f"{token_clean}\t{label}")
    #     print(f"{token}\t{label}")
    return new_tokens, new_lables

def extract_location_and_domain(tokens, labels):
    target_labels = ['B-TOUR', 'B-RENT', 'B-RESTAURANT', 
                     'B-ATTRACTION', 'B-HOTEL', 'B-EATERY',
                     'B-DRINKPLACE', 'B-CAMPING']
    
    extracted_tokens = []
    domain = None
    extracting = False

    for token, label in zip(tokens, labels):
        if not extracting:
            if label in target_labels:
                extracted_tokens.append(token)
                domain = label.replace('B-', '')  # Lấy domain
                extracting = True
        else:
            if label.startswith('I-'):
                extracted_tokens.append(token)
            else:
                break  # Gặp O hoặc B- khác thì dừng

    if extracted_tokens:
        text = ' '.join(extracted_tokens)
        return {"text": text, "domain": domain}
    else:
        return {"text": None, "domain": None}
    
def decode_prediction(pred_array, aspects, sentiment_map):
    pred_array = np.array(pred_array).flatten() 

    result = {}
    for aspect, sentiment_id in zip(aspects, pred_array):
        if sentiment_id != 0: 
            result[aspect] = sentiment_map[sentiment_id]

    return result

# decode_prediction(ypred_single, aspects, sentiment_map)
def save_to_csv(output_csv_path, text, place_extracted, domain_extracted, aspect_result):

    record_result = {
        'text': text,
        'place_extracted': place_extracted,
        'domain_extracted': domain_extracted,
        'aspect_result': json.dumps(aspect_result, ensure_ascii=False)
    }

    df_new = pd.DataFrame([record_result])

    if not os.path.exists(output_csv_path):
        df_new.to_csv(output_csv_path, index=False)
    else:
        df_new.to_csv(output_csv_path, mode='a', header=False, index=False)
    

def ner_absa_consumer_processor(config, ner_model, ner_tokenizer,
                                attractions_model, attractions_vectorizer,
                                eateries_model, eateries_vectorizer,
                                rents_model, rents_vectorizer,
                                drinkplaces_model, drinkplaces_vectorizer,
                                campings_model, campings_vectorizer, 
                                tours_model, tours_vectorizer,
                                restaurants_model, restaurants_vectorizer,
                                hotels_model, hotels_vectorizer):
    consumer = KafkaConsumer(
        config.KAFKA_TOPIC_COMMENTS,
        bootstrap_servers=config.KAFKA_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='comments_viewer',
        auto_offset_reset='earliest',
    )

    # producer = KafkaProducer(
    #     bootstrap_servers=config.KAFKA_SERVERS,
    #     value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    # )

    for message in consumer:
        print(message.value)
        record = message.value
        text = record.get('text', '')

        predict_tokens, predict_labels = predict_ner(text, ner_model, ner_tokenizer, id2label)
        ner_result = extract_location_and_domain(predict_tokens, predict_labels)
        place_extracted = ner_result['text']
        domain_extracted = ner_result['domain']
        
        if domain_extracted == 'TOUR':
            text_tfidf = tours_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = tours_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, tours_aspects, sentiment_map)
        elif domain_extracted == 'RENT':
            text_tfidf = rents_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = rents_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, rents_aspects, sentiment_map)
        elif domain_extracted == 'RESTAURANT':
            text_tfidf = restaurants_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = restaurants_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, restaurants_aspects, sentiment_map)
        elif domain_extracted == 'ATTRACTION':
            attractions_model, attractions_vectorizer
            text_tfidf = attractions_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = attractions_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, attractions_aspects, sentiment_map)
        elif domain_extracted == 'HOTEL':
            text_tfidf = hotels_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = hotels_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, hotels_aspects, sentiment_map)
        elif domain_extracted == 'EATERY':
            text_tfidf = eateries_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = eateries_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, eateries_aspects, sentiment_map)
        elif domain_extracted == 'DRINKPLACE':
            text_tfidf = drinkplaces_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = drinkplaces_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, drinkplaces_aspects, sentiment_map)
        elif domain_extracted == 'CAMPING':
            text_tfidf = campings_vectorizer.transform([text])  # dùng [text] để thành shape (1, n_features)
            ypred_single = campings_model.predict(text_tfidf)
            aspect_result = decode_prediction(ypred_single, campings_aspects, sentiment_map)
            
        save_to_csv(r'F:\Studies\Third_year\Big_data\Final_Code\Result\result.csv', text, place_extracted, domain_extracted, aspect_result)
            
            
        # absa_result = absa_model.predict(text)


        # record['ner_result'] = ner_result
        # record['absa_result'] = absa_result

        # producer.send(config.KAFKA_TOPIC_PREDICTED, value=record)
        # producer.flush()

        # print(f"[PROCESSOR] Processed and pushed record: {text[:30]}...")

