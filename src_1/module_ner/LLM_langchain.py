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

class VietnameseNormalizer:
    """
    Tham khảo: https://github.com/VinAIResearch/BARTpho/blob/main/VietnameseToneNormalization.md
    """
    VINAI_NORMALIZED_TONE = {
        'òa': 'oà', 'Òa': 'Oà', 'ÒA': 'OÀ', 
        'óa': 'oá', 'Óa': 'Oá', 'ÓA': 'OÁ', 
        'ỏa': 'oả', 'Ỏa': 'Oả', 'ỎA': 'OẢ',
        'õa': 'oã', 'Õa': 'Oã', 'ÕA': 'OÃ',
        'ọa': 'oạ', 'Ọa': 'Oạ', 'ỌA': 'OẠ',
        'òe': 'oè', 'Òe': 'Oè', 'ÒE': 'OÈ',
        'óe': 'oé', 'Óe': 'Oé', 'ÓE': 'OÉ',
        'ỏe': 'oẻ', 'Ỏe': 'Oẻ', 'ỎE': 'OẺ',
        'õe': 'oẽ', 'Õe': 'Oẽ', 'ÕE': 'OẼ',
        'ọe': 'oẹ', 'Ọe': 'Oẹ', 'ỌE': 'OẸ',
        'ùy': 'uỳ', 'Ùy': 'Uỳ', 'ÙY': 'UỲ',
        'úy': 'uý', 'Úy': 'Uý', 'ÚY': 'UÝ',
        'ủy': 'uỷ', 'Ủy': 'Uỷ', 'ỦY': 'UỶ',
        'ũy': 'uỹ', 'Ũy': 'Uỹ', 'ŨY': 'UỸ',
        'ụy': 'uỵ', 'Ụy': 'Uỵ', 'ỤY': 'UỴ',
    }
    
    @staticmethod
    def normalize_unicode(text):
        char1252 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
        charutf8 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
        char_map = dict(zip(char1252.split('|'), charutf8.split('|')))
        return re.sub(char1252, lambda x: char_map[x.group()], text.strip())

    @staticmethod
    def normalize_typing(text):
        for wrong_word, correct_word in VietnameseNormalizer.VINAI_NORMALIZED_TONE.items():
            text = text.replace(wrong_word, correct_word)
        return text.strip()

class VietnameseCleaner:
    def remove_emoji(text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002700-\U000027BF"
            u"\U000024C2-\U0001F251"            
                            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    def remove_punctuation_emoji(text):
        # Xóa các emoji: :))), :(((, =)))), =(((, ...
        text = re.sub(r'[:;=xX8@₫&]+-?[)(DPpOo3v]+', '', text)
        text = re.sub(r'[)(DPpOo3v]+-?[:;=xX8@₫&]+', '', text)
        text = re.sub(r'[:;=xX8@₫&]+[)(DPpOo3v]+', '', text)
        
        # Xóa các emoji @@, @.@, =.=, ...
        text = re.sub(r'[@=^~*]([.o_-])?[@=^~*]', '', text)
        
        # Xóa ngoặc thừa
        text = re.sub(r'\(\)', '', text)
        return text.strip()

    def remove_uncharacter_Vietnamese(text):
        ALLOWED_PUNCTUATION = r'\.,!?–:;'
        VN_CHARS = 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ'
        text = re.sub(fr'[^\sa-zA-Z0-9{VN_CHARS}{ALLOWED_PUNCTUATION}]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    @staticmethod
    def clean_social_text(text):
        text = VietnameseCleaner.remove_emoji(text)
        text = VietnameseCleaner.remove_punctuation_emoji(text)
        
        # remove html
        text = re.sub(r'<[^>]*>', '', text)
        
        # remove hashtag
        text = re.sub(r'#\w+', '', text)
        
        # remove url
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # remove hotline
        text = re.sub(r'\b[(]?(\+84|0)[)]?\d{3}[-\s\.]?\d{3}[-\s\.]?\d{3,6}\b', '', text)
        
        # remove email
        text = re.sub(r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+', '', text)
        
        # remove repeated characters (giảm bớt cường độ của từ)
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)

        # remove uncharacter + extra whitespace
        text = VietnameseCleaner.remove_uncharacter_Vietnamese(text)
        return text


class VietnameseTextProcessor:
    def __init__(self, max_correction_length=512):
        self.max_correction_length = max_correction_length
        self._build_teencodes()
    
    def _build_teencodes(self):
        self.teencodes = {
            'ok': ['okie', 'okey', 'ôkê', 'oki', 'oke', 'okay', 'okê'], 
            'không': ['kg', 'not', 'k', 'kh', 'kô', 'hok', 'ko', 'khong'], 'không phải': ['kp'], 
            'cảm ơn': ['tks', 'thks', 'thanks', 'ths', 'thank'], 'hồi đó': ['hùi đó'], 'muốn': ['mún'],
            
            'rất tốt': ['perfect', '❤️', '😍'], 'dễ thương': ['cute'], 'yêu': ['iu'], 'thích': ['thik'], 
            'tốt': [
                'gud', 'good', 'gút', 'tot', 'nice',
                'hehe', 'hihi', 'haha', 'hjhj', 'thick', '^_^', ':)', '=)'
                '👍', '🎉', '😀', '😂', '🤗', '😙', '🙂'
            ], 
            'bình thường': ['bt', 'bthg'], 'hàg': ['hàng'], 
            'không tốt':  ['lol', 'cc', 'huhu', ':(', '😔', '😓'],
            'tệ': ['sad', 'por', 'poor', 'bad'], 'giả mạo': ['fake'], 
            
            'quá': ['wa', 'wá', 'qá'], 'được': ['đx', 'dk', 'dc', 'đk', 'đc'], 
            'với': ['vs'], 'gì': ['j'], 'rồi': ['r'], 'mình': ['m', 'mik'], 
            'thời gian': ['time'], 'giờ': ['h'], 
        }
                
        self.teencodes = {word: key for key, values in self.teencodes.items() for word in values}
        teencode_url = 'https://gist.githubusercontent.com/behitek/7d9441c10b3c2739499fc5a4d9ea06fb/raw/df939245b3e841b62af115be4dcb3516dadc9fc5/teencode.txt'
        response = requests.get(teencode_url)
        
        if response.status_code == 200:
            text_data = StringIO(response.text)
            for pair in text_data:
                teencode, true_text = pair.split('\t')
                self.teencodes[teencode.strip()] = true_text.strip()
            self.teencodes = {k: self.teencodes[k] for k in sorted(self.teencodes)}
        else: print('Failed to fetch teencode.txt from', teencode_url)
        
    def correct_vietnamese_errors(self, texts):
        # https://huggingface.co/bmd1905/vietnamese-correction
        predictions = self.corrector(texts, max_length=self.max_correction_length, truncation=True)
        return [prediction['generated_text'] for prediction in predictions]
    
    def normalize_teencodes(self, text):
        words = []
        for word in text.split():
            words.append(self.teencodes.get(word, word))
        return ' '.join(words)
    
    def process_text(self, text, normalize_tone=True):
        # text = text.lower()
        if normalize_tone:
            text = VietnameseNormalizer.normalize_unicode(text)
            text = VietnameseNormalizer.normalize_typing(text)
        text = VietnameseCleaner.clean_social_text(text)
        text = self.normalize_teencodes(text)
        return text
    
class NERExtractor:
    def __init__(self, llm):
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
Bạn là công cụ NER, nhiệm vụ của bạn là **trích xuất các cụm danh từ tiếng Việt liên quan đến địa điểm và dịch vụ du lịch ở Thành phố Đà Lạt, Việt Nam** trong đoạn văn dưới đây. Chỉ trích xuất **cụm từ đầy đủ**, không bỏ sót từ mô tả đi kèm, không trích rời lẻ.
Đoạn văn:
{text}

### Định nghĩa các nhóm:
- **HOTELS**: Khách sạn, homestay, villa, resort, nhà nghỉ, nơi lưu trú.
- **RESTAURANTS**: Quán ăn, nhà hàng, tiệm cơm, quán nhậu.
- **DRINKPLACES**: Quán cà phê, quán trà, quán nước, quán bar, quán pub.
- **STREETFOODRESTAURANT**: Xe đẩy, gánh hàng rong, tiệm bánh căn, quán vỉa hè.
- **ATTRACTIONS**: Địa điểm tham quan, điểm check-in, công viên, đồi, thác, hồ, khu du lịch.
- **RENTALSERVICES**: Dịch vụ cho thuê xe máy, xe đạp, ô tô, lều trại.
- **TOURS**: Tour du lịch, tour trekking, tour trải nghiệm, tour tham quan.
- **CAMPINGS**: Địa điểm cắm trại.

### Quy định output:
- Chỉ trả kết quả **dạng JSON array**, mỗi phần tử gồm:
```json
{{
    "text": "cụm từ được trích",
    "label": "tên nhóm"
}}
- Nếu không có phần tử thì trả về rỗng
                """
            )
        self.chain = LLMChain(llm=llm, prompt=self.prompt_template)

    def extract(self, text: str, parse_json: bool = True):
        """
        text: câu tiếng Việt cần detect NER
        parse_json: nếu True, tự parse JSON trả về, nếu lỗi trả raw string
        """
        result = self.chain.run(text=text)
        cleaned_result = clean_result(result)
        # print(cleaned_result)
        return cleaned_result
    
@staticmethod
def clean_result(result):
    result = result.strip()
    if result.startswith("```"):
        # Loại bỏ dòng đầu ```json hoặc ```
        lines = result.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Loại bỏ dòng cuối ```
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        result = "\n".join(lines).strip()
    return result

def ner_extract(text):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    ner_extractor = NERExtractor(llm)
    result = ner_extractor.extract(text)
    return(json.loads(result))
    
if __name__ == "__main__":
    ner_extract()
