import re
import py_vncorenlp
from torch.utils.data import Dataset
import torch
import json
import pandas as pd
import ast
import os
from tqdm import tqdm
from torch.utils.data import random_split
from icecream import ic
from transformers import AutoTokenizer
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PhoBERTABSADataset(Dataset):
    def __init__(self, path_dataset, aspect_list, model_name):
        super().__init__()
        self.dfComments = pd.read_csv(path_dataset, index_col=0)
        
        self.origin_aspects = self.dfComments['aspects'].tolist()
        self.texts = self.dfComments['text'].tolist()
        self.aspect_list = aspect_list
        self.sentiment_map = {
            "POSITIVE": 1,
            "NEGATIVE": 2,
            "NEUTRAL": 3
        }
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.initialize_vncorenlp()

    def initialize_vncorenlp(self):
        """ VnCoreNLP tokenizer """
        self.rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=r"D:\MRC_2.0\VnCoreNLP")

    def word_segmentation(self, sentence: str):
        try:
            tokenized_sen = " ".join(self.rdrsegmenter.word_segment(sentence)[0]).strip()
        except:
            print(self.rdrsegmenter.word_segment(sentence))
            tokenized_sen = sentence
        return tokenized_sen

    def encode_sentence(self, text: str) -> torch.Tensor:
        tokenized_sen = self.word_segmentation(text)
        if not isinstance(tokenized_sen, str):
            print(f"[ERROR] tokenized_sen is not str: {tokenized_sen} - type: {type(tokenized_sen)}")
            raise
        encoded_sen = self.tokenizer(tokenized_sen, max_length=256, padding='max_length', truncation=True, return_tensors="pt").to(self.device)
        return encoded_sen

    def __len__(self):
        return len(self.dfComments)

    def __getitem__(self, idx):
        text = self.dfComments.loc[idx, 'text']
        
        # Parse string dictionary safely
        aspects_str = self.dfComments.loc[idx, 'aspects']
        aspects_dict = ast.literal_eval(aspects_str)
        
        labels = torch.full((len(self.aspect_list),), 0, dtype=torch.long)
        
        # Gán lại theo aspects_dict nếu tồn tại
        for aspect, sentiment in aspects_dict.items():
            if aspect in self.aspect_list and sentiment in self.sentiment_map:
                aspect_idx = self.aspect_list.index(aspect)
                labels[aspect_idx] = self.sentiment_map[sentiment]
                
        encoding = self.encode_sentence(text)
        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

def split_data(dataset):
    total_len = len(dataset)
    
    train_len = int(0.8 * total_len)
    dev_len = int(0.1 * total_len)
    test_len = total_len - train_len - dev_len
    
    train_dataset, dev_dataset, test_dataset = random_split(
        dataset,
        lengths=[train_len, dev_len, test_len],
        generator=torch.Generator().manual_seed(42)
    )
    
    return train_dataset, dev_dataset, test_dataset