from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json
import requests
from bs4 import BeautifulSoup
import os
import re
import undetected_chromedriver as uc
from seleniumwire import webdriver as wire_webdriver
from pathlib import Path

def get_driver(url):
    unchrome_options = uc.ChromeOptions()
    unchrome_options.add_argument("--start-maximized")
    unchrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    
    class PatchedUC(uc.Chrome, wire_webdriver.Chrome):
        def __init__(self, *args, **kwargs):
            wire_webdriver.Chrome.__init__(self, *args, **kwargs)
            
    driver = PatchedUC(options=unchrome_options, seleniumwire_options={})
    driver.get(url)

    return driver

def teardown(driver):
    driver.quit()
    
def get_cURL(driver):
    graphQL = []
    for request in driver.requests:
        if request.response and '/graphql/ids' in request.url and request.method == 'POST':
            if 'application/json' in request.headers.get('Content-Type', ''):
                size = len(request.body or b'')
                graphQL.append((size, request))
    largest_graphQL = max(graphQL, key=lambda x: x[0])[1]
    print("🎯 Chọn request lớn nhất:", largest_graphQL.url)
    
    def build_cURL_from_request(request):
        curl = f"curl '{request.url}' \\\n"
        for header_name, header_value in request.headers.items():
            curl += f"  -H '{header_name}: {header_value}' \\\n"
        if request.body:
            curl += f"  --data-raw '{request.body.decode('utf-8')}' \\\n"
        return curl
    
    curl_cmd = build_cURL_from_request(largest_graphQL)
    with open("graphql_request.sh", "w", encoding="utf-8") as f:
        f.write(curl_cmd)
    print("✅ Đã ghi cURL vào file `graphql_request.sh`")
    return curl_cmd.body
    
def get_response(url):
    driver = get_driver(url)
    cookies = driver.get_cookies()

    cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
    }

    resp = requests.get(url, headers=headers)
    teardown(driver)
    return resp

def write_file_json(data_json, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)
        
def read_file_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    return data_json

def format_url(match, number):
    return f'{match.group(1)}-or{number}-{match.group(2)}'

def generate_url_comments(root_url, number):
    new_url = re.sub(r'(Reviews)\-(.*)', lambda match: format_url(match, number), root_url)
    return new_url

def crawl_infor_restaurant(urls_restaurant):
    for idx in range(len(urls_restaurant)):
        print(urls_restaurant[idx])
        resp = get_response(urls_restaurant[idx])
        if resp.status_code == 200:
            print(f"✅ Truy cập thành công")
            doc = BeautifulSoup(resp.content, 'html.parser')

            detail_infor = doc.find('div', {
                'class': '_T XXmCa',
                'data-test-target': 'restaurant-detail-info'
            })
            name_rest = detail_infor.find('h1').get_text(strip=True)
            print(f"Nhà hàng: {name_rest}")

            detail_infor = doc.find('div', {
                'class': 'FXihi f e'
            })
            address_rest = detail_infor.find('span', {'data-automation': 'restaurantsMapLinkOnName'}).get_text(strip=True)
            print(f"Địa chỉ: {address_rest}")

        else:
            print(f"❌ Lỗi truy cập trang web")
            time.sleep(5)
            continue

if __name__ == '__main__':
    urls_restaurant = read_file_json('./eateries/urls_coffee.json')
    crawl_infor_restaurant(urls_restaurant)