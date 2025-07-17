from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse
import os
import re
import pytz
import json
import datetime
import requests
import sys

EDGE_DRIVER_PATH = "D:\BigData\msedgedriver.exe"
edge_options = Options()
edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0")
edge_options.add_argument(r'--profile-directory=Default')
edge_options.use_chromium = True

def get_parser():
    description = 'Crawling Data in Traveloka website'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--place', type=str, required=True, help='Place attraction tourist')
    parser.add_argument('--path_data', type=str, required=True, help='Path to dataset')
    parser.add_argument('--path_names', type=str, required=True, help='Path to list name')
    parser.add_argument('--folder_images', type=str, required=True, help='Path to save images')
    parser.add_argument('--path_changed_names', type=str, help='Path to list changed name')
    
    return parser

def setup(url: str):
    driver = webdriver.Edge(service=Service(executable_path=EDGE_DRIVER_PATH), options=edge_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    driver.get(url)
    return driver

def add_cookies(driver):
    cookies = read_file_json('traveloka_cookies.json')
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    return driver

def teardown(driver):
    driver.quit()
    
def get_url_hotels(place: str, num_rooms: int = 1, time_delta: int = 2, num_person: int = 2):
    tz_VN = pytz.timezone('Asia/Ho_Chi_Minh') # Set Time-zone in HCMC
    received_time = datetime.datetime(2025, 7, 2, tzinfo=tz_VN)
    giveback_time = received_time + datetime.timedelta(days=time_delta)
    url = f'https://www.traveloka.com/vi-vn/hotel/search?spec={received_time.strftime("%d-%m-%Y")}.{giveback_time.strftime("%d-%m-%Y")}.{time_delta}.{num_rooms}.HOTEL_GEO.{place}.{num_person}'
    return url

def write_file_json(data_json, path='hotel_DaLat.json'):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)
        
def read_file_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    return data_json

def preprocess_price(text):
    pattern = r'\d+(\.[0-9]{1,3})+'
    text_price = re.search(pattern, text).group()
    text_price = text_price.replace('.', '')
    return int(text_price)

def preprocess_highlight_locations(text):
    loc, distance = text.split('\n')
    distance = float(distance.split()[0]) / 1000 if 'm' == distance.split()[1] else float(distance.split()[0])
    return (loc, distance)

def preprocess_description(text):
    return text.split('\n')[3:]

def get_url_attraction(place):
    root = 'https://www.traveloka.com/vi-vn/activities/vietnam/product'
    return os.path.join(root, place)

def crawl_data_hotel(args):
    url = get_url_hotels(args.place)
    driver = setup(url)
    
    data_hotel = read_file_json(args.path_data) if os.path.exists(args.path_data) else []
    crawled_name = read_file_json(args.path_names) if os.path.exists(args.path_names) else []
    scrolled = 0

    def get_hotels():
        return driver.find_elements(By.XPATH, "//div[@class='css-1dbjc4n'][@data-testid='tvat-searchListItem']")

    def get_img_path(hotel_name, img_folder):
        os.makedirs(img_folder, exist_ok=True)
        img_path = f"{img_folder}/{hotel_name}.jpg"
        return img_path
    
    def download_img(img_link, img_path):
        response = requests.get(img_link)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(response.content)
            print("✅ Ảnh Hotel đã được tải về.")
        else:
            print(f"❌ Lỗi khi tải ảnh Hotel: {response.status_code}")
    
    def click_random():
        window_width = driver.execute_script("return window.innerWidth")
        window_height = driver.execute_script("return window.innerHeight")
        x = window_width // 2 + window_width // 4
        y = window_height // 2

        driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")
    
    def close_login():
        try:
            close_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='auth-modal-close-button']"))
            )
            close_button.click()
            print("✅ Đã đóng popup đăng nhập")
        except:
            print("⚠️ Không tìm thấy popup đăng nhập")
            
    def change_type_price():
        try:
            type_price = driver.find_elements(By.XPATH, "//div[@class='css-1dbjc4n r-1awozwy r-1ta3fxp r-18u37iz r-1wtj0ep']")[-1]
            button_price = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((type_price))
            )
            button_price.click()
            
            option_night = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='option-night']"))
            )
            option_night.click()
            print("✅ Đã thay đổi giá mỗi phòng (bao gồm thuế và phí)")
        except:
            print("⚠️ Chưa thay đổi giá mỗi phòng (chưa bao gồm thuế và phí)")
            
    def close_overlays():
        """Đóng tất cả popup/dropdown có thể che phủ"""
        try:
            # Đóng dropdown nếu đang mở
            dropdown = driver.find_element(By.CSS_SELECTOR, "[data-testid='selected-dropdown-item']")
            if dropdown.is_displayed():
                driver.execute_script("arguments[0].style.display = 'none';", dropdown)
            print("✅ Đã đóng popup/dropdown che phủ thông tin khách sạn")
        except:
            print("⚠️ Chưa đóng popup/dropdown")
            
    def ban_advertise():
        try:
            ad_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'r-1ta3fxp')]"))
            )
            driver.execute_script("arguments[0].style.display='none';", ad_div)
            print("✅ Đã ẩn quảng cáo")
        except:
            print("⚠️ Không tìm thấy quảng cáo")
            
    def trick(num_steps):
        for _ in range(num_steps):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)
    
    # Nhấn ngẫu nhiên để tắt lưu chỉ mục
    click_random()
    
    # Close Login
    close_login()
    
    # Change price
    change_type_price()
    
    # Closs popup
    close_overlays()
    
    # Trick
    # trick(5)
    # time.sleep(5)
    
    while True:
        previous_scroll_position = driver.execute_script("return window.scrollY")
        curr_hotels = get_hotels()
            
        if scrolled == 0:
            print(f"Chưa scroll: Tìm thấy {len(curr_hotels)} khách sạn")
        else:
            print(f"Lần scroll {scrolled+1}: Tìm thấy {len(curr_hotels)} khách sạn")
            milestone = (len(curr_hotels) // 2 ) - 1
            curr_hotels = curr_hotels[milestone:]
        scrolled += 1
        
        for idx in range(len(curr_hotels)):
            try:
                time.sleep(5)
                element = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((curr_hotels[idx]))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                
                hotel_name = WebDriverWait(curr_hotels[idx], 15).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        ".//h3[@data-testid='tvat-hotelName']"
                    ))
                ).text
                
                if hotel_name in crawled_name:
                    print(f"⏩ Đã xử lý rồi: {hotel_name}")
                    continue
                
                hotel_price = WebDriverWait(curr_hotels[idx], 15).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        ".//div[@data-testid='tvat-hotelPrice']"
                    ))
                ).text
                
                element.click()
                print("✅ Đã click vào khách sạn")

                # Chuyển qua tab mới
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(7)

                try:
                    data = {}
                    
                    if data.get('name') != hotel_name:
                        data['name'] = hotel_name
                    
                except Exception as name_err:
                    print(f"⚠️ Lỗi load tên khách sạn: {str(name_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                try:
                    hotel_img = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((
                            By.XPATH,
                            "//img[@data-testid='hotel_detail_imgBigThumbnail']"
                        ))
                    )
                    hotel_img_src = hotel_img.get_attribute("src")
                    img_path = get_img_path(hotel_name, args.folder_images)
                    
                    if data.get('img') != img_path:
                        data['img'] = img_path
                    
                except Exception as img_err:
                    print(f"⚠️ Lỗi tải ảnh: {str(img_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                    
                try:
                    if data.get('price') != preprocess_price(hotel_price):
                        data['price'] = preprocess_price(hotel_price)
                    
                except Exception as price_err:
                    print(f"⚠️ Lỗi tải giá: {str(price_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                    
                try:
                    hotel_address = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((
                            By.XPATH,
                            "//div[@class='css-901oao css-cens5h r-13awgt0 r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-fdjqy7']"
                        ))
                    )
                    if data.get('address') != hotel_address.text:
                        data['address'] = hotel_address.text
                    
                except Exception as address_err:
                    print(f"⚠️ Lỗi tải địa chỉ: {str(address_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                
                try:
                    header_star = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@data-testid='header_star_rating']" \
                            "/div[1]"
                        ))
                    )
                    star = header_star.find_elements(By.TAG_NAME, "svg")
                    num_star = len(star)
                    if num_star > 0:
                        if 'half' in star[-1].get_attribute('data-id').lower():
                            num_star -= 0.5
                            
                    if data.get('num_star') != num_star:
                        data['num_star'] = num_star
                    
                except Exception as num_star_err:
                    print(f"⚠️ Không có sao: {str(num_star_err)}")
                    data['num_star'] = 0
                    
                try:
                    highlight_locations = WebDriverWait(driver, 20).until(
                        EC.visibility_of_all_elements_located((
                            By.XPATH,
                            "//div[@class='css-1dbjc4n r-1awozwy r-18u37iz r-1cmwbt1 r-13qz1uu']"
                        ))
                    )
                    highlight_locations_text = []
                    for element in highlight_locations:
                        if element.text not in highlight_locations_text:
                            highlight_locations_text.append(element.text)

                    highlight_locations_text = [preprocess_highlight_locations(text) for text in highlight_locations_text]
                    if len(data.get('highlight_locations', [])) < len(highlight_locations_text):
                        data['highlight_locations'] = highlight_locations_text
                    time.sleep(2)
                    
                except Exception as highligh_locations_err:
                    print(f"⚠️ Lỗi tải các địa điểm nổi bật xung quanh khách sạn: {str(highligh_locations_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                
                try:
                    button_more = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 
                            "div[class='css-18t94o4 css-1dbjc4n r-kdyh1x r-1loqt21 r-10paoce r-5njf8e r-1otgn73 r-lrvibr r-7xmw5f'][role='button']"
                        ))
                    )
                    button_more.click()
                    
                    container = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@class='css-1dbjc4n r-f4gmv6 r-nsbfu8']" \
                            "/div[1]"
                        ))
                    )
                    hotel_description = preprocess_description(container.text)
                    if len(data.get('description', [])) < len(hotel_description):
                        data['description'] = hotel_description
                    time.sleep(2)
                    
                    button_exist = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 
                            "svg[data-id='IcSystemCrossClose']"
                        ))
                    )
                    button_exist.click()
                    
                    # Chờ overlay/modal biến mất
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((
                            By.CSS_SELECTOR, 
                            "div.r-f4gmv6.r-nsbfu8"
                        ))
                    )
                    time.sleep(5)
                    
                except Exception as description_err:
                    print(f"⚠️ Lỗi tải thông tin mô tả về khách sạn: {str(description_err)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                
                try:
                    block_language = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@class='css-1dbjc4n r-18u37iz r-bztko3']" \
                            "/div[last()]"
                        ))
                    )
                    button_language = WebDriverWait(block_language, 20).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 
                            "svg[data-id='IcSystemChevronDown16']"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_language)
                    button_language.click()
                    
                    scrollable_div = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@class='css-1dbjc4n r-150rngu r-eqz5dr r-16y2uox r-1wbh5a2 r-11yh6sk r-1rnoaur r-1sncvnh']"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2;", scrollable_div)
                    
                    selector_language = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@class='css-1dbjc4n r-cn9azx']" \
                            "/div[last()-1]"
                        ))
                    )
                    button_vietnamese = WebDriverWait(selector_language, 20).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "./div[last()]" \
                            "/div" \
                            "/div[6]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_vietnamese)
                    button_vietnamese.click()
                    time.sleep(2)
                    
                    button_apply = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//div[@class='css-1dbjc4n r-1awozwy r-t7z1y5 r-5kkj8d r-tcvcnk r-13awgt0 r-1777fci r-10gryf7 r-1yzf0co']" \
                            "/div[1]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_apply)
                    button_apply.click()
                    time.sleep(2)
                    
                    hotel_reviews = []
                    container = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@class='css-1dbjc4n'][@data-testid='review-list-container']"
                        ))
                    )
                    
                    while True:
                        reviews = container.find_elements(By.XPATH, "//div[@class='css-1dbjc4n r-1habvwh r-13awgt0 r-1ssbvtb']")
                        for review in reviews:
                            rating = review.find_element(By.XPATH, ".//div[@data-testid='tvat-ratingScore']")
                            comment = review.find_element(By.XPATH, ".//div[@class='css-901oao css-cens5h r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-fdjqy7']")
                            hotel_reviews.append((comment.text, float(rating.text.replace(',', '.'))))

                        enable_click_bottons = driver.find_elements(By.XPATH, "//div[@class='css-901oao r-1awozwy r-1i6uqv8 r-6koalj r-61z16t']")
                        if len(enable_click_bottons) == 4:
                            next_page_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((enable_click_bottons[1]))
                            )
                        elif len(enable_click_bottons) == 2:
                            if len(hotel_reviews) > 20:
                                break
                            next_page_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((enable_click_bottons[0]))
                            )
                        else:
                            print("Không thể qua trang vì <= 20 comment")
                            break
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
                        next_page_button.click()
                        print("✅ Đã click qua trang để lấy phản hồi khách hàng")
                        time.sleep(2)
                    
                    print(f'Số lượng comment đã thu {len(hotel_reviews)}')
                    if len(data.get('reviews', [])) < len(hotel_reviews):
                        data['reviews'] = hotel_reviews
                    
                except Exception as reviews_err:
                    if len(hotel_reviews) > 0:
                        print(f'Số lượng comment đã thu {len(hotel_reviews)}')
                        data['reviews'] = hotel_reviews
                    else:
                        print(f"⚠️ Lỗi tải đánh giá của khách hàng: {str(reviews_err)}")
                        if len(driver.window_handles) > 1:
                            driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                if data.get("name") and data.get("reviews"):
                    data_hotel.append(data)
                    crawled_name.append(data['name'])
                    download_img(hotel_img_src, data['img'])
                    write_file_json(data_hotel, args.path_data)
                    write_file_json(crawled_name, args.path_names)
                    print(f"✅ Cập nhật dữ liệu thành công - Hiện có {len(data_hotel)}")
                else:
                    print(f"⚠️ Không cập nhật dữ liệu mới")
                
                time.sleep(10)
                if len(driver.window_handles) > 1:
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as hotel_err:
                print(f"⚠️ Không thể click vào khách sạn: {str(hotel_err)}")
                continue
            
        time.sleep(10)
        new_scroll_position = driver.execute_script("return window.scrollY")
        if new_scroll_position <= previous_scroll_position:
            break
        
    teardown(driver)
        
        
def crawl_data_attraction(args):
    url = get_url_attraction(args.place)
    driver = setup(url)
    
    data_attraction = read_file_json(args.path_data) if os.path.exists(args.path_data) else []
    crawled_name = read_file_json(args.path_names) if os.path.exists(args.path_names) else []
    data = {}
    curr_pos = len(data_attraction)
    
    def close_webToApp():
        try:
            button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "div[data-testid='button_webToAppCloseButton']"
                ))
            )
            button.click()
            print("✅ Đã đóng App đăng nhập")
        except:
            print("⚠️ Không tìm thấy App đăng nhập")
            
    def get_img_path(place_name, img_folder):
        os.makedirs(img_folder, exist_ok=True)
        img_path = f"{img_folder}/{place_name}.jpg"
        return img_path
    
    def download_img(img_link, img_path):
        response = requests.get(img_link)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(response.content)
            print("✅ Ảnh địa điểm đã được tải về.")
        else:
            print(f"❌ Lỗi khi tải ảnh: {response.status_code}")   
    
    # Đóng popup tải app
    close_webToApp()
    time.sleep(2)
    
    try:
        place_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//h1[@data-testid='lblProductTitle']"
            ))
        )
        
        if place_name.text in crawled_name:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

            for idx in range(len(data_attraction)):
                if data_attraction[idx]['name'] == place_name.text:
                    data = data_attraction[idx]
                    curr_pos = idx
                    break
                
        if data.get('name') != place_name.text:
            data['name'] = place_name.text
        
    except Exception as name_err:
        print(f"⚠️ Lỗi load tên: {str(name_err)}")
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])

    
    try:
        block_img = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[@class='css-1dbjc4n r-6koalj r-18u37iz r-tzz3ar r-1777fci r-q90dru']" \
                "/div[2]" \
                "/div[1]"
            ))
        )
        place_img = block_img.find_element(By.TAG_NAME, 'img')
        place_img_src = place_img.get_attribute("src")
        img_path = get_img_path(place_name.text, args.folder_images)
        if data.get('img') != img_path:
            data['img'] = img_path
        
    except Exception as img_err:
        print(f"⚠️ Lỗi tải ảnh: {str(img_err)}")
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
        
    try:
        place_address = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[@data-testid='lblProductLocation']"
            ))
        )
        if data.get('address') != place_address.text:
            data['address'] = place_address.text
        
    except Exception as address_err:
        print(f"⚠️ Lỗi load địa chỉ: {str(address_err)}")
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
      
        
    try:
        place_price = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[@data-testid='lblProductPrice']"
            ))
        )
        if data.get('price') != preprocess_price(place_price.text):
            data['price'] = preprocess_price(place_price.text)
        
    except Exception as price_err:
        print(f"⚠️ Lỗi load giá: {str(price_err)}")
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
     
     
    try:
        place_reviews = data.get('reviews', [])
        block_language = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH, 
                "//div[@class='css-1dbjc4n r-18u37iz r-bztko3']" \
                "/div[last()]"
            ))
        )
        button_language = WebDriverWait(block_language, 20).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                "svg[data-id='IcSystemChevronDown16']"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_language)
        button_language.click()
        
        scrollable_div = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH, 
                "//div[@class='css-1dbjc4n r-150rngu r-eqz5dr r-16y2uox r-1wbh5a2 r-11yh6sk r-1rnoaur r-1sncvnh']"
            ))
        )
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
        
        selector_language = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH, 
                "//div[@class='css-1dbjc4n r-cn9azx']" \
                "/div[last()]"
            ))
        )
        button_vietnamese = WebDriverWait(selector_language, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "./div[last()]" \
                "/div" \
                "/div[6]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_vietnamese)
        button_vietnamese.click()
        time.sleep(2)
        
        button_apply = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@class='css-1dbjc4n r-1awozwy r-t7z1y5 r-5kkj8d r-tcvcnk r-13awgt0 r-1777fci r-10gryf7 r-1yzf0co']" \
                "/div[1]"
            ))
        )
        button_apply.click()
        time.sleep(2)
        
        container = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='css-1dbjc4n'][@data-testid='review-list-container']"))
        )
        milestone = 0
        
        while True:
            reviews = container.find_elements(By.XPATH, "//div[@class='css-1dbjc4n r-1habvwh r-13awgt0 r-1ssbvtb']")
            milestone += len(reviews)
            if milestone > len(place_reviews):
                for review in reviews:
                    rating = review.find_element(By.XPATH, ".//div[@data-testid='tvat-ratingScore']")
                    comment = review.find_element(By.XPATH, ".//div[@class='css-901oao css-cens5h r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-fdjqy7']")
                    place_reviews.append((comment.text, float(rating.text.replace(',', '.'))))

            enable_click_bottons = driver.find_elements(By.XPATH, "//div[@class='css-901oao r-1awozwy r-1i6uqv8 r-6koalj r-61z16t']")
            if len(enable_click_bottons) == 4:
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((enable_click_bottons[1]))
                )
            elif len(enable_click_bottons) == 2:
                if len(place_reviews) > 20 and milestone > 20:
                    break
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((enable_click_bottons[0]))
                )
            else:
                print("Không thể qua trang vì <= 20 comment")
                break
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
            next_page_button.click()
            print("✅ Đã click qua trang để lấy phản hồi khách hàng")
            time.sleep(2)
        
        print(f'Số lượng comment đã thu {len(place_reviews)}')
        if len(data['reviews']) < len(place_reviews):
            data['reviews'] = place_reviews
        
    except Exception as reviews_err:
        if len(place_reviews) > 0:
            print(f'Số lượng comment đã thu {len(place_reviews)}')
            data['reviews'] = place_reviews
        else:
            print(f"⚠️ Lỗi tải đánh giá: {str(reviews_err)}")
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
    if data:
        if curr_pos != len(data_attraction):
            data_attraction[curr_pos] = data
        else:
            data_attraction.insert(curr_pos, data)
            crawled_name.append(place_name.text)
            
        download_img(place_img_src, img_path)
        write_file_json(data_attraction, args.path_data)
        write_file_json(crawled_name, args.path_names)
        print(f"✅ Cập nhật dữ liệu mới thành công - Hiện có {len(data_attraction)} với {len(data_attraction[-1]['reviews'])} comments")
    else:
        print(f"⚠️ Không cập nhật dữ liệu mới")
        
    teardown(driver)
    
    
if __name__ == '__main__':
    args = get_parser().parse_args(sys.argv[1:])
    # crawl_data_hotel(args)
    crawl_data_attraction(args)