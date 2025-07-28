import os
# import google.generativeai as genai
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain_google_genai import ChatGoogleGenerativeAI
import json
import pandas as pd
import re
import random
from io import StringIO
import sys
from icecream import ic
from tqdm import tqdm
import time
import glob
import argparse
import ast
import random 
from sklearn.model_selection import train_test_split

# class Config:
#     RESULTS_LIMIT        = 3
#     GOOGLE_API_KEY       = "AIzaSyB8bMJU_EnP5iHKy7VtqfxyNCtaUkdSPYw"
#     LLM_NAME             = "gemini-1.5-flash-latest"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY

# class NERExtractor:
#     def __init__(self, llm):
#         self.prompt_template = PromptTemplate(
#             input_variables=["text"],
#             template="""
# Bạn là công cụ **viết lại review**, nhiệm vụ của bạn:

# # **Yêu cầu:**
# - Viết lại câu review **mạch lạc, tự nhiên, tròn ý** dựa trên **review gốc được cung cấp**.
# - Có thể lặp lại nội dung review gốc, nhưng **phải chèn tên quán đã cung cấp vào câu review mới**.
# - Giữ **giọng điệu gần gũi, dễ đọc, phù hợp đăng mạng xã hội**.
# - **Không thêm cảm nhận cá nhân mới hoặc nội dung không có trong review gốc**.
# - Không được bỏ sót các chi tiết cảm xúc hoặc đánh giá trong review gốc.
# - **Chỉ trả về câu review mới đã viết lại, không kèm bất kỳ nội dung nào khác.**

# ### Input:
# - Tên quán: {title}
# - Review gốc: {review}

# ### Output:
# - Một **câu review mới** đã viết lại, có chèn tên quán.
# - Không thêm bất kỳ ký hiệu, dấu gạch đầu dòng, tiêu đề hoặc lời giải thích nào.
# ```json
# {{
#     "new_review": "câu review mới",
# }}
# """
#         )
#         self.chain = LLMChain(llm=llm, prompt=self.prompt_template)

#     def extract(self, review: str, title: str, parse_json: bool = True):
#         """
#         text: câu tiếng Việt cần detect NER
#         parse_json: nếu True, tự parse JSON trả về, nếu lỗi trả raw string
#         """
#         result = self.chain.run(review=review, title=title)

#         cleaned_result = self.clean_result(result)
#         return cleaned_result
    
#     def clean_result(self, result):
#         result = result.strip()
#         if result.startswith("```"):
#             # Loại bỏ dòng đầu ```json hoặc ```
#             lines = result.split("\n")
#             if lines[0].startswith("```"):
#                 lines = lines[1:]
#             # Loại bỏ dòng cuối ```
#             if lines[-1].startswith("```"):
#                 lines = lines[:-1]
#             result = "\n".join(lines).strip()
#         return result
    

# def ner_extract(review, title):
#     llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
#     ner_extractor = NERExtractor(llm)
#     result = ner_extractor.extract(review, title)
#     template_result = json.loads(result)
#     if isinstance(template_result, list):
#         return template_result[0]
#     elif isinstance(template_result, dict):
#         return template_result
#     else:
#         raise ValueError('Error datatype of result')


def get_parser():
    description = 'Labeling NER Dataset'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--path_file', type=str, required=True, help='Path to dataset file')
    parser.add_argument('--output_file_ner', type=str, required=True, help='Path to output file')
    # parser.add_argument('--output_file_absa', type=str, required=True, help='Path to output file')
    # parser.add_argument('--train_file_ner', type=str, required=True, help='Path to train file')
    # parser.add_argument('--test_file_ner', type=str, required=True, help='Path to test file')
    parser.add_argument('--train_file_absa', type=str, required=True, help='Path to train file')
    parser.add_argument('--test_file_absa', type=str, required=True, help='Path to test file')
    
    return parser

BUG_NAME_PLACES = ['.', 'hai nguoi', '1']


TEMPLATES = [
    "Tại {title}, {review}",
    "Mình ghé {title} và thấy {review}",
    "Trải nghiệm ở {title} là {review}",
    "Lần ghé {title} gần đây, mình thấy {review}",
    "Sau khi tới {title}, mình nhận ra {review}",
    "Ở {title}, mình đã trải nghiệm {review}",
    "Một lần đến {title}, mình cảm nhận {review}",
    "{title} mang lại cảm giác {review}",
    "Chuyến đi {title} khiến mình thấy {review}",
    "Sau khi ghé {title}, mình thấy {review}",
    "Trải nghiệm ở {title} khiến mình {review}",
    "{title} đã cho mình cảm giác {review}",
    "Khi ghé {title}, mình cảm nhận rõ {review}",
    "{title} thực sự là nơi {review}",
    "Mình từng ghé {title} và thấy {review}",
    "Từng trải nghiệm ở {title}, mình thấy {review}",
    "Cảm giác ở {title} là {review}",
    "Đi {title} một lần, mình thấy {review}",
    "Đến {title} rồi mới biết {review}",
    "{title} thật sự {review}",
    "Tới {title}, mình có cảm nhận {review}",
    "Lúc ở {title}, mình thấy {review}",
    "Khi đến {title}, mình thấy {review}",
    "Sau khi trải nghiệm ở {title}, mình thấy {review}",
    "Lần đầu đến {title}, mình cảm nhận {review}",
    "{title} đem lại trải nghiệm {review}",
    "Kỷ niệm ở {title} là {review}",
    "{title} là nơi mình thấy {review}",
    "Ghé {title} xong mình thấy {review}",
    "Đi {title} làm mình thấy {review}",
    "Đến {title} mình mới thấy {review}",
    "Khi ở {title}, mình thấy {review}",
    "Kỳ nghỉ ở {title} khiến mình {review}",
    "Đi {title} khiến mình {review}",
    "Sau khi trải nghiệm tại {title}, mình {review}",
    "Tại {title} mình đã {review}",
    "Sau khi đến {title}, mình {review}",
    "Khi trải nghiệm ở {title}, mình {review}",
    "{title} cho mình trải nghiệm {review}",
    "Trải nghiệm tại {title} làm mình thấy {review}",
    "Chuyến đi {title} vừa rồi {review}",
    "Một lần ở {title} {review}",
    "Ở {title} mình đã thấy {review}",
    "Trải qua thời gian ở {title}, mình thấy {review}",
    "{title} làm mình {review}",
    "Sau chuyến đi {title}, mình thấy {review}",
    "Ghé {title} mới thấy {review}",
    "Một lần ghé {title}, mình đã {review}",
    "Lần ghé {title} vừa rồi, mình thấy {review}",
    "Khi đến {title}, mình cảm thấy {review}",
    "Lần đầu trải nghiệm ở {title}, mình thấy {review}",
    "Sau khi nghỉ ở {title}, mình thấy {review}",
    "Khi ghé {title}, mình {review}",
    "Tới {title} một lần, mình thấy {review}",
    "Ở {title}, mình cảm thấy {review}",
    "Trải nghiệm ở {title} cho mình cảm giác {review}",
    "Từng ghé {title}, mình thấy {review}",
    "{title} là nơi {review}",
    "{title} khiến mình cảm nhận {review}",
    "{title} đã để lại cho mình cảm giác {review}",
    "Tại {title}, mình thấy {review}",
    "Ở {title} giúp mình thấy {review}",
    "Chuyến đi tới {title} cho mình cảm giác {review}",
    "Sau khi check-in tại {title}, mình {review}",
    "Khi nghỉ ở {title}, mình {review}",
    "Ở {title} một thời gian, mình thấy {review}",
    "Sau khi trải nghiệm {title}, mình cảm nhận {review}",
    "Tại {title}, trải nghiệm của mình là {review}",
    "Khi tới {title}, mình cảm nhận {review}",
    "Lần tới {title}, mình đã {review}",
    "Ghé thăm {title}, mình thấy {review}",
    "{title} để lại cảm giác {review}",
    "{title} mang đến trải nghiệm {review}",
    "{title} khiến mình cảm giác {review}",
    "Mình từng ở {title} và thấy {review}",
    "Lần đến {title}, mình thấy {review}",
    "Khi check-in {title}, mình {review}",
    "Ở {title}, mình trải nghiệm {review}",
    "Khi lưu trú tại {title}, mình thấy {review}",
    "Khi ghé qua {title}, mình {review}",
    "Từng trải qua tại {title}, mình thấy {review}",
    "Tới {title}, mình nhận thấy {review}",
    "{title} là nơi mình cảm nhận {review}",
    "Khi mình đến {title}, mình thấy {review}",
    "{title} thật sự khiến mình {review}",
    "Từng ghé qua {title}, mình {review}",
    "Đến {title}, mình trải nghiệm {review}",
    "Ghé qua {title}, mình thấy {review}",
    "{title} để lại cho mình trải nghiệm {review}",
    "{title} là nơi mình từng {review}",
    "Trải nghiệm tại {title} thật sự {review}",
    "{title} cho mình cảm giác {review}",
    "Một chuyến đi tới {title} khiến mình {review}",
    "{title} thực sự mang lại cảm giác {review}",
    "Một lần check-in {title}, mình thấy {review}",
    "{title} khiến mình nhận ra {review}",
    "Ghé chơi {title}, mình thấy {review}",
    "Ở {title}, mình cảm nhận rõ {review}",
    "{title} để lại cho mình cảm giác {review}",
    "Khi đến {title}, mình nhận ra {review}",
    "{title} đã cho mình trải nghiệm {review}",
    "Mình từng trải nghiệm ở {title} và thấy {review}",
    "Tới {title}, mình trải nghiệm {review}",
    "Tại {title}, tôi nhận thấy {review}",
    "Ghé {title}, trải nghiệm thực tế là {review}",
    "Theo quan sát tại {title}, {review}",
    "Sau khi thử {title}, ghi nhận {review}",
    "Trong lần ghé {title}, tôi thấy {review}",
    "Khi đến {title}, tình hình là {review}",
    "Quá trình sử dụng dịch vụ {title}, mình cảm thấy {review}",
    "Phải nói {title} khiến mình {review}",
    "Vừa đến {title} đã thấy {review}",
    "Không ngờ {title} lại {review}",
    "Một số nhận xét về {title}: {review}",
    "Điều đáng chú ý ở {title}: {review}",
    "Gần đây có ghé {title} thấy {review}",
    "Ở {title} thấy {review}",
    "Một số cảm nhận tại {title}: {review}",
    "Đến {title} thấy {review}",
    "Chia sẻ về {title}: {review}",
    "Một góc nhỏ tại {title} {review}",
    "Nghe chia sẻ về {title}: {review}",
    "Trải nghiệm tại {title}: {review}",
    "Tên địa điểm: {title}. Trải nghiệm: {review}",
    "Mới khám phá {title} hôm nay, {review}",
    "Có dịp trải nghiệm {title}, {review}",
    "Ghé {title}, mình thấy {review}",
    "Hôm mình ghé {title}, {review}",
    "Trong lần ghé {title}, mình cảm thấy {review}",
    "Vừa đặt chân đến {title}, mình thấy {review}",
    "Một hôm ghé {title}, mình thấy {review}",
    "Lúc ghé {title}, mình thấy {review}",
    "Ngày hôm đó tại {title}, mình cảm thấy {review}",
    "{review}. Đó là cảm nhận của mình khi ghé {title}.",
    "{review}. Trải nghiệm này mình có được tại {title}.",
    "{review}. Nơi đó chính là {title}.",
    "{review}. Chỗ mình ghé là {title}.",
    "{review}. Hôm mình ghé {title}.",
    "{review}. Đó là lúc mình có mặt tại {title}.",
    "{review}. Và địa điểm mình nhắc đến chính là {title}.",
    "{review}. Đó là những gì mình thấy ở {title}.",
    "{review}. Và nơi mình nhắc tới là {title}.",
    "{review}. Nơi mình trải nghiệm là {title}.",
    "{review}. Mình đã cảm nhận điều này tại {title}.",
    "{review}. Mình đã trải nghiệm khi ghé {title}.",
    "{review}. Đó là những gì mình thấy khi ở {title}.",
    "{review}. Đây là trải nghiệm của mình khi tới {title}.",
    "{review}. Đây là cảm nhận của mình khi ghé {title}.",
    "{review}. Một trải nghiệm khó quên tại {title}.",
    "{review}. Trên là đánh giá cá nhân về {title}.",
    "{review}. Một trải nghiệm tại {title}.",
    "{review}. Đó là ấn tượng của mình về {title}.",
    "{review}. Mình ghi nhận điều này tại {title}.",
    "{review}. Nơi mình đến chính là {title}.",
    "{review}. Mình có mặt ở đó là tại {title}.",
    "{review}. Địa điểm mình đề cập là {title}.",
    "{review}. Mình trải nghiệm điều này ở {title}.",
    "{review}. Nơi mình nói đến là {title}.",
    "{review}. Đây là điều mình thấy tại {title}.",
    "{review}. Và chỗ đó là {title}.",
    "{review}. Mình cảm nhận được tại {title}.",
    "{review}. Trong lần mình ghé {title}.",
    "{review}. Đó là kỷ niệm tại {title}.",
    "{review}. Khi mình có dịp đến {title}.",
    "{review}. Đó là tất cả cảm nhận của mình trong chuyến đi {title}.",
    "{review}. Trong chuyến thử {title}.",
    "{review}. Hôm đó mình dùng dịch vụ tại {title}.",
    "{review}. Đây là tất cả tại {title}.",
    "{review}. Và chỗ này là {title}.",
    "{review}. Địa điểm ấy chính là {title}.",
    "{review}. Mình đã cảm nhận điều này tại {title}.",
    "{review}. Và mình đã ghé {title} để có trải nghiệm đó.",
    "{review}. Địa điểm mình muốn nhắc đến là {title}.",
    "{review}. Đây chính là trải nghiệm của mình tại {title}.",
    "{review}. Mình đã trải nghiệm trong lần ghé {title}.",
    "{review}. Nơi mình đã ghé là {title}.",
    "{review}. Mình có dịp trải nghiệm tại {title}.",
    "{review}. Và nơi mình nói đến chính là {title}.",
    "{review}. Mình đã trải nghiệm khi ghé {title}.",
    "{review}. Và địa điểm mình ghé hôm đó là {title}.",
    "{review}. Mình đã từng cảm nhận điều đó tại {title}.",
    "{review}. Mình có cơ hội trải nghiệm tại {title}.",
    "{review}. Mình đã tới {title} hôm đó.",
    "{review}. Và địa điểm để lại ấn tượng là {title}.",
    "{review}. Và nơi mình tới trải nghiệm là {title}.",
    "{review}. Đó là những gì mình thấy khi ở {title}.",
    "Đã trải nghiệm tại {title}, và mình thấy {review}",
    "Về {title}, mình có vài điều muốn nói: {review}",
    "Khi đến {title}, cảm nhận của mình là {review}.",
    "Trải nghiệm của mình ở {title}: {review}.",
    "Sau khi ghé thăm {title}, mình thấy {review}.",
    "Đánh giá nhanh về {title}: {review}.",
    "Cảm nhận chung về {title} của mình là {review}.",
    "Với {title}, mình có thể nói rằng {review}.",
    "Để nói về {title}, mình thấy {review}.",
    "Tại {title}, điều mình nhận thấy là {review}.",
    "Có thể nói, {title} là nơi {review}.",
    "Với mình, {title} mang lại cảm giác {review}.",
    "Đôi lời chia sẻ về {title}: {review}.",
    "Và đây là trải nghiệm của mình tại {title}: {review}.",
    "Nếu hỏi mình về {title}, mình sẽ nói {review}.",
    "Mình đã thử {title} và thấy {review}.",
    "Chút chia sẻ về {title}: {review}.",
    "Mình đã khám phá {title} và thấy {review}.",
    "Sự thật về {title}: {review}.",
    "Sau khi trải nghiệm dịch vụ ở {title}, mình nhận thấy {review}.",
    "Về tổng thể, {title} mang lại cảm giác {review}.",
    "Nói ngắn gọn về {title}: {review}.",
    "Đến {title} và minh thấy {review}.",
    "Khám phá {title} và mình thấy {review}.",
    "Mình vừa có dịp ghé {title}, và đây là cảm nhận: {review}.",
    "Đây là một review chân thực về {title}: {review}.",
    "Với {title}, điều mình thấy là {review}.",
    "Về {title}, mình có nhận xét là {review}.",
    "Khi nói đến {title}, mình thấy {review}.",
    "Trải nghiệm của mình tại {title} là {review}.",
    "Để đánh giá {title}, mình nghĩ {review}.",
    "Tổng quan về {title}: {review}.",
    "Một vài nhận xét về {title}: {review}.",
    "Sau khi ghé {title}, mình có thể nói rằng {review}.",
    "Mình vừa thử {title} và thấy {review}.",
    "Cảm nhận cá nhân của mình về {title}: {review}.",
    "Cảm nhận của mình về {title} sau lần đầu ghé thăm là {review}.",
    "Tổng thể, {title} mang lại trải nghiệm {review}.",
    "Đôi lời về {title}: {review}.",
    "Thông tin thêm về {title}: {review}.",
    "Về cơ bản, {title} là {review}.",
    "Về tổng quan, {title} là nơi {review}.",
    "Với {title}, ý kiến của mình là {review}.",
    "Về {title}, mình có thể nói rằng {review}.",
    "Khi đề cập đến {title}, mình thấy {review}.",
    "Mình đã ghé {title} và đây là nhận định: {review}.",
    "Khi đánh giá {title}, mình thấy {review}.",
    "Đây là trải nghiệm cơ bản của mình tại {title}: {review}.",
    "Về {title}, mình chỉ muốn nói rằng {review}."
    "Khách quan mà nói, {title} là nơi {review}.",
    "Nếu bạn hỏi về {title}, mình sẽ nói {review}.",
    "Đây là trải nghiệm chân thật của mình ở {title}: {review}.",
    "Mình đã dành thời gian ở {title} và đây là những gì mình cảm nhận: {review}.",
    "Cá nhân mình, {title} mang lại cảm giác {review}.",
    "Với tất cả những gì {title} mang lại, mình thấy {review}.",
    "Cảm nhận riêng của mình về {title} là {review}.",
    "Nếu phải đánh giá {title}, mình sẽ nói {review}.",
    "Đây là câu chuyện trải nghiệm của mình tại {title}: {review}.",
    "Một trải nghiệm đáng giá tại {title}: {review}.",
    "Cảm nhận riêng của mình về {title} là {review}.",
    "Mình muốn chia sẻ về {title}: {review}.",
    "Về {title}, mình thấy {review}.",
    "Đây là cảm nhận của mình khi ghé {title}: {review}.",
    "Trải nghiệm ở {title} thì {review}.",
    "Sau khi ghé {title}, {review}.",
    "Sau khi trải nghiệm tại {title}, mình thấy {review}.",
    "Trong lần ghé {title}, mình thấy {review}.",
    "Ngày mình ghé {title}, mình thấy {review}.",
    "Sau chuyến đi {title}, mình thấy {review}.",
    "Khi mình tới {title}, mình thấy {review}.",
    "Trải nghiệm của mình tại {title} là {review}.",
    "Khi mình tới {title}, mình thấy {review}.",
    "Một lần ghé {title}, mình thấy {review}.",
    "Hôm ghé {title}, mình thấy {review}.",
    "Sau khi tới {title}, mình nhận thấy {review}.",
    "Một dịp ghé {title}, mình thấy {review}.",
    "Vừa ghé {title}, mình thấy {review}.",
    "Sau khi ghé qua {title}, mình thấy {review}.",
    "Trải nghiệm tại {title}, mình thấy {review}.",
    "{review}. Đây là chia sẻ về {title}.",
    "{review}. Nơi mình muốn chia sẻ là {title}.",
    "{review}. {title} là nơi mình muốn nhắc đến.",
    "{review}. Địa chỉ mình ghé là {title}.",
    "{review}. Đây là cảm nhận tại {title}.",
    "{review}. Và nơi mình muốn nhắc đến là {title}.",
    "{review}. Nơi này chính là {title}.",
    "{review}. Lúc đó mình ở {title}.",
    "{review}. Đó chính là {title}.",
    "{review}. Lần ghé đó là {title}.",
    "{review}. Và mình đã ở {title}.",
    "{review}. Nơi đó là {title}.",
    "{review}. Hôm ấy mình đến {title}.",
    "{review}. Hôm đó mình ghé {title}.",
    "{review}. Địa điểm này là {title}.",
    "Trong chuyến đi đến {title}, mình thấy {review}.",
    "Lúc mình ghé {title}, mình thấy {review}.",
    "Một dịp ghé thăm {title}, mình thấy {review}."
    "Hôm mình đến {title}, mình cảm nhận {review}.",
    "Lúc ghé {title}, mình thấy {review}.",
    "Đây là nhận xét của mình sau khi thăm {title}: {review}.",
    "Nhìn chung, trải nghiệm của mình tại {title} là {review}.",
    "Mình đã ghé {title} một lần và thấy {review}.",
    "Thật lòng mà nói, ghé {title} mình thấy {review}.",
    "Nói về {title} á hả, thì {review}.",
    "Đi {title} rồi, giờ mới hiểu sao {review}.",
    "Trải nghiệm của mình ở {title} nè: {review}.",
    "Với mình, {title} mang đến cảm giác {review}.",
    "Đôi lời về {title}: {review}.",
    "Nói chung, {title} cho mình cảm giác {review}.",
    "Một dịp ghé thăm {title}, mình thấy {review}.",
    "Trong buổi ghé qua {title}, mình thấy {review}.",
    "Trong chuyến tham quan {title}, mình cảm nhận {review}.",
    "Trong dịp ghé {title}, mình cảm nhận {review}.",
    "Lần ghé {title} vừa rồi, mình cảm nhận {review}.",
    "Ghé qua {title}, mình thấy {review}.",
    "Khi ghé {title}, mình thấy {review}.",
    "Lần ghé {title} vừa rồi, mình cảm nhận {review}.",
    "Khi có dịp tới {title}, mình thấy {review}.",
    "Tại {title}, mình thấy {review}.",
    "Hôm đến {title}, mình thấy {review}.",
    "Lần đầu ghé {title}, mình cảm nhận {review}.",
    "Khi có dịp ghé {title}, mình cảm nhận {review}.",
    "Lúc ghé qua {title}, mình thấy {review}.",
    "Ghé {title}, mình cảm nhận {review}.",
    "Tới {title}, mình nhận thấy {review}.",
    "Lần đầu tới {title}, mình nhận thấy {review}.",
    "Hôm mình ghé {title}, mình cảm nhận {review}.",
    "Khi ghé qua {title}, mình nhận ra {review}.",
    "Tại {title}, {review}.",
    "Tôi đã ghé {title} và {review}.",
    "Qua trải nghiệm ở {title}, tôi nhận thấy rằng {review}.",
    "Khi nhắc đến {title}, điều tôi muốn nói là {review}.",
    "Nếu bạn hỏi về {title}, thì {review}.",
    "Lần đầu đến {title}, tôi đã trải nghiệm {review}.",   
    "{review}. Tôi đã có trải nghiệm tương tự tại {title}.",
    "{review}. Đây là điều tôi mong đợi ở {title}.",
    "{review}. Và đó là trải nghiệm của tôi tại {title}.",
    "{review}. Đó là cảm nhận chung về {title}.",
    "{review}. Đó là tất cả những gì tôi muốn nói về {title}.",
    "{review}. Đó là cảm nhận của tôi sau khi đến {title}.",
    "Sau khi ghé thăm {title}, tôi nhận ra rằng {review}.",
    "Khi bạn đến {title}, bạn sẽ thấy rõ rằng {review}.",
    "Về {title}, tôi muốn nói rằng {review}.",
    "Xét về {title}, điều tôi nhận thấy là {review}.",
    "{review}. Đó là những gì tôi đã chứng kiến ở {title}.",
    "Ở {title}, bạn sẽ thấy rằng {review}.",
    "Mình được bạn bè giới thiệu {title}, và quả thật {review}."
    "Nghe nhiều người khen {title}, hôm nay thử thì thấy {review}.",
    "Nghe nhiều người chê {title}, hôm nay thử thì thấy {review}.",
    "{review}. Tôi muốn chia sẻ về {title}.",
    "Một vài chia sẻ về {title}. {review}.",
    "Tôi đã đến {title}, {review}.",
    "Lần gần đây tôi ghé {title}, {review}.",
    "Trong lần ghé {title}, {review}.",
    "Khi ghé qua {title}, tôi nhận thấy rằng {review}.",
    "{review}. Và tôi ghi nhận điều đó ở {title}.",
    "Đã đến {title}, ghi nhận rằng {review}.",
    "Có cơ hội đến {title}, tôi nhận thấy {review}.",
    "Ở {title}, một điều tôi quan sát được là {review}.",
    "Trải nghiệm của tôi tại {title} cho thấy {review}.",
    "Nếu bạn ghé {title}, bạn sẽ thấy {review}.",
    "{review}. Tôi đã có trải nghiệm này ở {title}.",
    "{review}. Tôi muốn chia sẻ về {title} trong các khía cạnh này.",
    "Lần đầu tiên tôi ghé {title}, tôi đã nhận thấy {review}.",
    "Khi đến trải nghiệm tại {title}, tôi cảm thấy {review}",
    "Tôi nghe nhiều người nhắc đến {title}, nên tôi đã đến thử. {review}.",
    "Tôi nghe nhiều người nhắc đến {title}, nên tôi đã trải nghiệm thử. {review}.",
    "Tôi nghe nhiều người nhắc đến {title}, nên tôi đến thử. {review}.",
    "Tìm thấy {title} trên bản đồ, tôi trải nghiệm thấy {review}.",
    "Qua một bài viết, tôi biết đến {title} và tôi thấy {review}.",
    "Trong chuyến đi Đà Lạt này, tôi đã ghé {title} và tôi thấy {review}.",
    "Cảm nhận của tôi về {title} là {review}.",
]


TEMPLATES_HOTELS = [
    "Khi lưu trú tại {title}, tôi nhận thấy rằng {review}.",
    "Lần gần nhất tôi lưu trú tại {title}. {review}.",
    "Chuyến đi vừa rồi tôi chọn nghỉ tại {title}. {review}.",
    "{title} là nơi tôi đã ở trong chuyến đi gần đây. {review}.",
    "Khi đến thành phố, tôi chọn {title} để nghỉ lại. {review}.",
    "Trong thời gian lưu trú tại {title}, tôi cảm thấy {review}.",
    "Trong hành trình nghỉ dưỡng Đà Lạt, tôi ở {title}, {review}.",
    "Tôi sử dụng dịch vụ lưu trú của {title}. {review}.",
    "Khoảng thời gian ở {title}, tôi cảm thấy {review}.",
    "Suốt kỳ nghỉ tại {title}, tôi cảm thấy {review}.",
    "Trong thời gian ở tại {title}, tôi nhận thấy rằng {review}.",
    "Khi nghỉ lại ở {title}, tôi thấy rằng {review}.",
    "Khi ở tại {title}, tôi có ghi nhận rằng {review}.",
    "Trong lúc lưu trú tại {title}, tôi đã quan sát thấy {review}.",
    "Khi tôi lưu trú ở {title}, tôi thấy {review}.",
    "Trong kỳ nghỉ tại {title}, tôi nhận thấy {review}.",
    "Trong quá trình ở {title}, tôi thấy rằng {review}.",
    "Trong thời gian lưu lại {title}, tôi có cảm nhận rằng {review}.",
    "Trong thời gian ở lại {title}, tôi nhận thấy {review}.",
    "Khi tôi chọn nghỉ lại tại {title}, tôi thấy {review}.",
    "Để có chỗ nghỉ ngơi ở Đà Lạt, tôi đã chọn {title}. {review}.",
    "Địa điểm tôi chọn để nghỉ chân là {title}. {review}.",
    "Nếu bạn đang tìm một nơi ở, {title} là nơi tôi đã trải nghiệm và thấy {review}.",
    "Khi tôi cần một nơi để nghỉ, tôi đã tìm đến {title} và nhận thấy {review}.",
    "Cảm nhận của tôi khi ở {title} là {review}."
]


TEMPLATES_RESTAURANTS = [
    "Trong chuyến đi, tôi ghé qua {title}. {review}.",
    "Tôi có dịp ăn ở {title}, tôi cảm thấy {review}.",
    "Sau khi ăn tại {title}, tôi nhận thấy rằng {review}.",
    "Tôi được bạn giới thiệu {title} và đã thử. {review}.",
    "Tôi chọn {title} trong số các nhà hàng gần đó. {review}.",
    "Trong lúc dùng bữa tại {title}, tôi ghi nhận rằng {review}.",
    "{title} là một trong những nhà hàng tôi đã thử. {review}.",
    "Trong lúc chờ món ở {title}, tôi nhận thấy {review}.",
    "Khi dùng bữa tại {title}, tôi nhận thấy rằng {review}.",
    "Bước vào {title}, điều đầu tiên tôi nhận ra là {review}.",
    "{review}, tôi đã trải nghiệm điều này khi dùng bữa ở {title}.",
    "Lần gần nhất tôi ăn tại {title}, tôi cảm thấy {review}.",
    "Tôi từng ghé ăn ở {title}, tôi cảm thấy {review}.",
    "Tôi dừng lại ăn ở {title}, tôi cảm thấy {review}.",
    "Tôi chọn {title} khi đang tìm chỗ ăn, tôi cảm thấy {review}.",
    "Tôi được người quen giới thiệu {title}, tôi thấy rằng {review}.",
    "Khi ghé {title}, tôi thấy rằng {review}.",
    "Lần đầu tiên tôi ghé {title}, tôi đã nhận thấy {review}.",
    "Bạn bè tôi gợi ý {title}, và khi thử, tôi thấy {review}.",
    "Tôi quyết định dùng thử món tại {title} và nhận ra {review}.",
    "Tôi đã dành thời gian ăn ở {title} và điều tôi thấy là {review}.",
    "Khi đói bụng ở Đà Lạt, tôi tìm đến {title}. {review}.",
    "Tôi đã ghé {title} để ăn một bữa thịnh soạn. {review}.",
    "Để thưởng thức ẩm thực, tôi đã ghé {title} và thấy {review}.",
    "Tôi tìm một nhà hàng và đã ghé {title}, tôi cảm nhận {review}.",
    "Lúc thưởng thức món ăn ở {title}, tôi cảm nhận được {review}.",
]


TEMPLATES_EATERIES = [
    "Trong chuyến đi, tôi ghé qua {title}. {review}.",
    "Tôi có dịp ăn ở {title}, tôi cảm thấy {review}.",
    "Sau khi ăn tại {title}, tôi nhận thấy rằng {review}.",
    "Tôi được bạn giới thiệu {title} và đã thử. {review}.",
    "Tôi chọn {title} trong số các quán ăn gần đó. {review}.",
    "Trong lúc dùng bữa tại {title}, tôi ghi nhận rằng {review}.",
    "{title} là một trong những quán ăn tôi đã thử. {review}.",
    "Trong lúc chờ món ở {title}, tôi nhận thấy {review}.",
    "Khi dùng bữa tại {title}, tôi nhận thấy rằng {review}.",
    "Bước vào {title}, điều đầu tiên tôi nhận ra là {review}.",
    "{review}, tôi đã trải nghiệm điều này khi dùng bữa ở {title}.",
    "Lần gần nhất tôi ăn tại {title}, tôi cảm thấy {review}.",
    "Tôi từng ghé ăn ở {title}, tôi cảm thấy {review}.",
    "Tôi dừng lại ăn ở {title}, tôi cảm thấy {review}.",
    "Tôi chọn {title} khi đang tìm chỗ ăn, tôi cảm thấy {review}.",
    "Tôi được người quen giới thiệu {title}, tôi thấy rằng {review}.",
    "Khi ghé {title}, tôi thấy rằng {review}.",
    "Khi đói bụng ở Đà Lạt, tôi tìm đến {title}. {review}.",
    "Tôi đã ghé {title} để ăn một bữa. {review}.",
    "Ăn ở {title}, tôi thấy rằng {review}.",
    "Lần đầu tiên tôi ghé {title}, tôi đã nhận thấy {review}.",
    "Tôi tìm một quán ăn và đã ghé {title}, tôi cảm nhận {review}.",
    "Bạn bè tôi gợi ý {title}, và khi thử, tôi thấy {review}.",
    "Trên đường đi dạo phố, tôi dừng lại ở {title} và nhận thấy {review}.",
    "Tôi quyết định dùng thử món tại {title} và nhận ra {review}.",
    "Tôi tìm thấy {title} khi lang thang tìm đồ ăn, tôi trải nghiệm thấy {review}.",
    "Tôi đã dành thời gian ăn ở {title} và điều tôi thấy là {review}.",
]


TEMPLATES_DRINKPLACES = [
    "Lần gần đây tôi ngồi ở {title}, tôi cảm thấy {review}.",
    "Tôi gọi đồ uống tại {title}, tôi cảm thấy {review}.",
    "Tôi được bạn bè giới thiệu đến {title}, tôi trải nghiệm thấy {review}.",
    "Tôi biết đến {title} qua mạng xã hội, tôi cảm thấy {review}.",
    "Trong thời gian ngồi tại {title}, tôi nhận thấy {review}.",
    "Lúc ngồi ở {title}, tôi thấy rằng {review}.",
    "Uống nước ở {title}, tôi thấy rằng {review}.",
    "Khi thưởng thức đồ uống tại {title}, tôi nhận thấy {review}.",
    "Tôi chọn {title} làm điểm đến, và tôi thấy rằng {review}.",
    "Ngồi hướng thức đồ uống tại {title}, tôi nhận thấy {review}.",
    "Khi ghé {title}, tôi thấy rằng {review}.",
    "Khi bước vào {title}, tôi cảm thấy {review}.",
    "Tôi được gợi ý đến {title}, và tôi thấy {review}.",
    "Được gợi ý thử {title} ở Đà Lạt, tôi thấy {review}.",
    "Đi ngang qua {title} và tò mò ghé vào, tôi nhận thấy {review}.",
    "Khi khám phá Đà Lạt, tôi dừng chân tại {title} và tôi cảm nhận {review}.",
    "Chiều mưa ở Đà Lạt, tôi ghé {title} và tôi thấy {review}.",
    "Buổi tối ở {title} tại Đà Lạt, tôi cảm nhận {review}.",
    "Buổi sáng ở {title}, tôi cảm nhận {review}.",
    "Đến {title} và tôi cảm nhận được {review}.",
    "Ngồi nhâm nhi đồ uống tại {title}, tôi nhận thấy {review}.",
]


TEMPLATES_ATTRACTIONS = [
    "Trong hành trình vừa rồi, tôi có mặt tại {title}. {review}.",
    "Tôi có dịp tham quan {title}, tôi cảm thấy {review}.",
    "Trong chuyến du lịch, tôi dừng chân tại {title}. {review}.",
    "Trong chuyến du lịch, tôi ghé qua {title}. {review}.",
    "Tôi dành thời gian tham quan {title}. {review}.",
    "Tôi đi tham quan {title}, tôi cảm thấy {review}.",
    "Tôi quyết định ghé qua {title} khi đi ngang. {review}.",
    "Trên đường tham quan thành phố, tôi ghé {title}. {review}.",
    "Khi tham quan {title}, tôi quan sát thấy {review}.",
    "Tôi có mặt ở {title} trong hành trình khám phá. {review}.",
    "Tôi vào tham quan {title}, tôi thấy {review}.",
    "Trong chuyến tham quan thành phố, tôi đến {title}. {review}.",
    "Tôi có dịp đi qua {title}. {review}.",
    "Khám phá {title}, tôi nhận ra rằng {review}.",
    "Dừng chân tại {title} trong chuyến đi, tôi cảm nhận được {review}.",
    "Khi ghé thăm {title}, tôi thấy {review}.",
    "Chuyến đi đến {title} đã cho tôi thấy {review}.",
    "Tham quan {title} là một phần trong kế hoạch của tôi. {review}.",
    "Tôi đã có mặt ở {title} để trải nghiệm. {review}.",
    "Trong số các điểm đến, tôi chọn {title}. {review}.",
    "Trong chuyến tham quan {title}, tôi thấy {review}.",
    "Khi khám phá {title}, tôi cảm thấy {review}.",
    "Lúc ở {title}, tôi nhận thấy {review}.",
    "Trên con đường khám phá Đà Lạt, {title} là một điểm dừng chân. {review}.",
    "Tôi dành một khoảng thời gian ở {title}. {review}.",
    "Tham quan {title} và điều tôi cảm nhận được là {review}.",
    "Tôi đã dành thời gian khám phá {title}. {review}.",
    "Trong chuyến du lịch Đà Lạt, tôi quyết định ghé {title}. {review}.",
    "Dừng lại ở {title} trong chuyến đi của mình. {review}.",
    "Đây là điều tôi thấy ở {title}. {review}.",
    "Khi tham quan {title}, tôi đã nhận ra {review}.",
    "Tôi có dịp thăm {title} và điều tôi cảm nhận là {review}.",
    "Trong chuyến đi đến Đà Lạt, tôi đã ghé {title}. {review}."
]


TEMPLATES_CAMPINGS = [
    "Tôi đã có dịp cắm trại tại {title}, tôi cảm thấy {review}.",
    "Tôi đã có dịp cắm trại tại {title}, tôi có trải nghiệm {review}.",
    "Tôi có dịp cắm trại tại {title}, tôi cảm thấy {review}.",
    "Tôi từng chọn {title} làm điểm cắm trại, tôi cảm thấy {review}.",
    "Tôi từng chọn {title} làm điểm cắm trại. {review}.",
    "Chuyến cắm trại gần đây tôi thực hiện ở {title}. {review}.",
    "Chuyến cắm trại gần đây tôi thực hiện ở {title}, tôi cảm thấy {review}.",
    "Tôi cắm trại ở {title} trong dịp đến Đà Lạt. {review}.",
    "Tôi cắm trại ở {title} trong dịp đến Đà Lạt, tôi cảm thấy {review}.",
    "Tôi cắm trại ở {title} trong chuyến du lịch gần đây. {review}.",
    "Tôi cắm trại ở {title} trong chuyến du lịch gần đây, tôi cảm thấy {review}.",
    "Tôi cắm trại ở {title} khi đến Đà Lạt. {review}.",
    "Tôi cắm trại ở {title} khi đến Đà Lạt, tôi cảm thấy {review}.",
    "Tôi ngủ lại qua đêm ở {title}, tôi nhận thấy {review}.",
    "Trong chuyến đi cắm trại, tôi chọn {title}. {review}.",
    "Trong chuyến đi cắm trại, tôi trải nghiệm tại {title}. {review}.",
    "Tôi cắm trại tại {title} và ngủ qua đêm. {review}.",
    "Khi đến {title} để cắm trại, tôi nhận ra rằng {review}.",
    "Gói ghém đồ đạc đến {title}, tôi cảm nhận được {review}.",
    "Chúng tôi đã chọn {title} làm điểm hạ trại, và tôi thấy rằng {review}.",
    "Dừng chân tại {title} để cắm trại, tôi cảm nhận được {review}.",
    "Tìm kiếm một địa điểm cắm trại ở Đà Lạt, tôi đã đến {title} và trải nghiệm thấy {review}.",
    "Tôi đã có dịp cắm trại tại {title} và điều tôi cảm nhận là {review}.",
]


TEMPLATES_TOURS = [
    "Tôi đã tham gia {title}. {review}.",
    "Tôi đã trải nghiệm {title}. {review}.",
    "Tôi có dịp tham gia {title} trong chuyến đi. {review}.",
    "Chuyến đi vừa rồi tôi chọn {title}. {review}.",
    "Chuyến đi vừa rồi tôi thử trải nghiệm {title}. {review}.",
    "Tôi được giới thiệu {title} nên đã thử. {review}.",
    "Tôi biết đến {title} qua mạng xã hội nên đã thử. {review}.",
    "Tôi chọn {title} để khám phá trong ngày. {review}.",
    "Tôi chọn {title} để khám phá Đà Lạt trong ngày. {review}.",
    "Lịch trình của tôi có bao gồm {title}. {review}.",
    "Tôi chọn tour {title} vì thấy phù hợp thời gian. {review}.",
    "Tôi được gợi ý tham gia {title} và đã thử. {review}.",
    "Tôi được người quen giới thiệu tour {title}. {review}.",
    "Tôi trải nghiệm {title} theo kế hoạch đã định. {review}.",
    "Tôi chọn tour {title} vì thấy lịch trình phù hợp. {review}.",
]


TEMPLATES_RENTS = [
    "Tôi đã sử dụng dịch vụ tại {title}. {review}.",
    "Tôi có mặt tại {title} để thuê xe. {review}.",
    "Tôi đã thuê xe tại {title}. {review}.",
    "Tôi ghé {title} để lấy xe đã đặt trước. {review}.",
    "Tôi được giới thiệu thuê xe tại {title}. {review}.",
    "Tôi có dịp thuê phương tiện từ {title}. {review}.",
    "Tôi thuê xe tại {title} để di chuyển trong thành phố. {review}.",
    "Tôi ghé {title} để thuê xe đi tham quan. {review}.",
    "Tôi chọn {title} làm nơi thuê phương tiện di chuyển. {review}.",
    "Sau khi đến Đà Lạt, tôi thuê xe từ {title}. {review}.",
    "Tôi dùng xe thuê từ {title} để đi quanh thành phố. {review}.",
    "Tôi sử dụng dịch vụ thuê xe tại {title}. {review}.",
    "Địa điểm tôi thuê xe là {title}. {review}.",
    "Hành trình khám phá Đà Lạt của tôi được thực hiện nhờ xe từ {title}. {review}.",
    "Khi tìm dịch vụ thuê xe tại Đà Lạt, {title} là lựa chọn của tôi. {review}.",
    "Tình cờ, tôi đã thuê xe tại {title}. {review}.",
    "Sau khi tìm kiếm, tôi đã liên hệ {title} để thuê xe. {review}."
]


def generate_new_review(record, origin_template, sup_template):
    template = random.choice(origin_template+sup_template)
    filled_template = template.format(title=record['title'].strip(), review=record['text'].strip())
    return filled_template

def tokenize(text):
    """Simple whitespace tokenizer with punctuation split."""
    return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

def BIO_tagging(record, reversed_matching_titles):
    tokens = tokenize(record['text'])
    tags = ["O"] * len(tokens) 

    entity_tokens = tokenize(record['title'])
        
    for i in range(len(tokens) - len(entity_tokens) + 1):
        window = tokens[i:i+len(entity_tokens)]
        if window == entity_tokens:
            tags[i] = f"B-{reversed_matching_titles[record['title']]}"
            for j in range(1, len(entity_tokens)):
                tags[i+j] = f"I-{reversed_matching_titles[record['title']]}"
    
    return list(zip(tokens, tags))

def NER_labelling(record, reversed_matching_titles):
    title = record['title']
    label = reversed_matching_titles[record['title']]
    return (title, label)


def regex_ner_span(record, reversed_matching_titles):
    pattern = fr"{record['title']}"
    matches = re.finditer(pattern, record['text'], flags=re.UNICODE | re.IGNORECASE)
    spans = []
    for match in matches:
        start, end = match.span()
        spans.append({
            'start': start,
            'end': end,
            'label': reversed_matching_titles[record['title']]
        })
    return spans


def write_file_json(path: str, data_json):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)


def write_file_conll(review_series, reversed_matching_titles, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for text_review in review_series.dropna():
            tokens_tags = BIO_tagging(text_review, reversed_matching_titles)
            for token, tag in tokens_tags:
                f.write(f"{token}\t{tag}\n")
            f.write("\n") 
        

def get_match_category_titles(path_file: str):
    matching = {}
    dataframe = pd.read_csv(path_file, index_col=0)
    if 'hotels' in os.path.basename(path_file):
        matching['HOTEL'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_HOTELS
    elif 'restaurants' in os.path.basename(path_file):
        matching['RESTAURANT'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_RESTAURANTS
    elif 'eateries' in os.path.basename(path_file):
        matching['EATERY'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_EATERIES
    elif 'drinkplaces' in os.path.basename(path_file):
        matching['DRINKPLACE'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_DRINKPLACES
    elif 'attractions' in os.path.basename(path_file):
        matching['ATTRACTION'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_ATTRACTIONS
    elif 'campings' in os.path.basename(path_file):
        matching['CAMPING'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_CAMPINGS
    elif 'tours' in os.path.basename(path_file):
        matching['TOUR'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_TOURS
    elif 'rents' in os.path.basename(path_file):
        matching['RENT'] = dataframe['title'].unique().tolist()
        sup_template = TEMPLATES_RENTS
    else:
        raise ValueError('Cannot get list titles')
        
    return matching, dataframe, sup_template
    
    
def contains_vietnamese_character(title: str):
    VN_CHARS = 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ'
    pattern = fr'[a-zA-Z0-9{VN_CHARS}]'
    return bool(re.search(pattern, title))

def create_data_for_NER1(df, reversed_matching_titles):
    if len(df) <= 20000:
        df['ner_BIO'] = df.apply(lambda row: BIO_tagging(row, reversed_matching_titles), axis=1)
    else:
        df = df.sample(n=20000, random_state=42).reset_index(drop=True)
        df['ner_BIO'] = df.apply(lambda row: BIO_tagging(row, reversed_matching_titles), axis=1)

    conll_lines = []

    for sentence in df['ner_BIO']:
        for word, tag in sentence:
            conll_lines.append(f"{word}\t{tag}")
        conll_lines.append("")  
    return conll_lines

def create_data_for_NER2(df, reversed_matching_titles):
    df['ner_BIO'] = df.apply(lambda row: BIO_tagging(row, reversed_matching_titles), axis=1)

    conll_lines = []

    for sentence in df['ner_BIO']:
        for word, tag in sentence:
            conll_lines.append(f"{word}\t{tag}")
        conll_lines.append("")  
    return conll_lines


def split_dataframe(df, test_size=0.2, random_state=42):
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)
    
    
if __name__ == "__main__":
    args = get_parser().parse_args(sys.argv[1:])
    
    matching_titles, dataframe, sup_template = get_match_category_titles(args.path_file)
    ic(dataframe.shape, len(sup_template))
    # Loại bỏ các tên quán tên không chứa tiếng Anh & tiếng Việt
    dataframe = dataframe[dataframe['title'].apply(contains_vietnamese_character)].reset_index(drop=True)
    ic(dataframe.shape)
    reversed_matching_titles = {title: category for category, listTitles in matching_titles.items() for title in listTitles}

    dataframe['text'] = dataframe.apply(func=generate_new_review, axis=1, args=(TEMPLATES, sup_template))
    train_df, test_df = split_dataframe(dataframe)
    dataframe['ner_BIO'] = dataframe.apply(lambda row: BIO_tagging(row, reversed_matching_titles), axis=1)
    # dataframe['ner_SPAN'] = dataframe.apply(lambda row: regex_ner_span(row, reversed_matching_titles), axis=1)
    dataframe['ner'] = dataframe.apply(lambda row: NER_labelling(row, reversed_matching_titles), axis=1)
    conll_lines = create_data_for_NER1(dataframe, reversed_matching_titles)
    with open(args.output_file_ner, "w", encoding="utf-8") as f:
        f.write("\n".join(conll_lines))
    ic(dataframe.iloc[0])
    # dataframe.to_csv(args.output_file_absa)
    
    
    train_df.to_csv(args.train_file_absa)
    test_df.to_csv(args.test_file_absa)
    
    # train_conll_lines = create_data_for_NER1(train_df, reversed_matching_titles)
    # test_conll_lines = create_data_for_NER1(test_df, reversed_matching_titles)
    # with open(args.train_file_ner, "w", encoding="utf-8") as f:
    #     f.write("\n".join(train_conll_lines))
    # with open(args.test_file_ner, "w", encoding="utf-8") as f:
    #     f.write("\n".join(test_conll_lines))
    