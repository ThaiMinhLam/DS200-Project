import re
import json
import os
import pandas as pd
import numpy as np
import shutil
import glob
import matplotlib.pyplot as plt
import plotly.express as px
from transformers import AutoTokenizer, AutoModelForMaskedLM, AutoModel

def merge_data_apify(root):
    data_json = []
    for file in os.listdir(root):
        path_file = os.path.join(root, file)
        with open(path_file, 'r', encoding='utf-8') as f:
            data_json += json.load(f)
        
    with open('./Apify/filtered_reviews_final.json', 'w', encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)

def convert_csv(path_json):
    with open(path_json, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    
    df_full = pd.DataFrame(data_json)
    df_full_exploded = df_full.explode('reviews')
    df_full_exploded['reviews'] = df_full_exploded['reviews'].apply(lambda x: x[0])
    df_full_exploded = df_full_exploded.reset_index(drop=True)
    df_full_exploded['id'] = df_full_exploded.index
    
    cols = ['id'] + [col for col in df_full_exploded.columns if col == 'reviews']
    df_full_exploded = df_full_exploded[cols]
    
    df_full_exploded.iloc[:30].to_csv('./hotels/hotel_DaLat.csv', index=False)


def convert_categories(df_ggmaps):
    matching = {
        'cafe': ['cafe_rooftop_Da_Lat', 'cafe_san_vuon_Da_Lat', 'cafe_studio_Da_Lat', 'cafe_view_rung_Da_Lat', 'cafe_vintage_Da_Lat', 'quan_cafe_co_view_Da_Lat'],
        'attraction': ['danh_lam_thang_canh_Da_Lat', 'dia_diem_song_ao_Da_Lat', 'diem_tham_quan_Da_Lat', 'khu_du_lich_sinh_thai_Da_Lat', 'thac_Da_Lat', 'vuon_hoa_Da_Lat', 'nong_trai_Da_Lat', 'vuon_thu_Da_Lat', 'trang_trai_thu_Da_Lat', 'vuon_thu_trang_trai_dong_vat'],
        'hotel': ['homestay_Da_Lat', 'khach_san_Da_Lat', 'nha_nghi_Da_Lat', 'resort_Da_Lat', 'villa_Da_Lat'],
        'tour_renting': ['dich_vu_tour_&_thue_xe_may_Da_Lat'],
        'restaurant': ['nha_hang_chay_Da_Lat', 'nha_hang_hai_san_Da_Lat'],
        'eatery': ['quan_an_dem_Da_Lat', 'quan_an_sang_Da_Lat', 'quan_an_vat_Da_Lat'],
        'camping': ['trai_cam_trai_Da_Lat']
    }
    reversed_matching = {small_category: category for category, smalls in matching.items() for small_category in smalls}
    df_ggmaps['category'] = df_ggmaps['category'].map(reversed_matching)
    
    return df_ggmaps

def custom_mapping(record, matchingReviews_title, matchingReviews_urlId):
    if record['title'] in matchingReviews_title.keys():
        return matchingReviews_title[record['title']]
    elif record['urlId'] in matchingReviews_urlId:
        return matchingReviews_urlId[record['urlId']]
    return []

def normalize_unicode(text):
    char1252 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
    charutf8 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
    char_map = dict(zip(char1252.split('|'), charutf8.split('|')))
    return re.sub(char1252, lambda x: char_map[x.group()], text.strip())

def combine_df(folder_path: str):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    listDF = [pd.read_csv(file, index_col=0) for file in csv_files]
    finalDF = pd.concat(listDF, ignore_index=True)
    return finalDF

def contains_vietnamese_character(title: str):
    VN_CHARS = 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ'
    pattern = fr'[a-zA-Z0-9{VN_CHARS}]'
    return bool(re.search(pattern, title))

def visualize(df: pd.DataFrame):
    # df = df[['title', 'category']].drop_duplicates(subset=['title', 'category'])
    statistic_df = df['category'].value_counts().reset_index()
    
    plt.figure(figsize=(8, 6))
    plt.bar(statistic_df['category'], statistic_df['count'], color='skyblue')
    
    for index, value in enumerate(statistic_df['count']):
        plt.text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)
    
    plt.xlabel('Domain')
    plt.ylabel('Số lượng reviews')
    plt.title('Biểu đồ số lượng reviews theo từng domain')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()  # Giúp căn chỉnh không bị cắt chữ
    plt.show()
    
if __name__ == '__main__':
    finalDF = combine_df("annotated_labels")
    finalDF = finalDF[finalDF['title'].apply(contains_vietnamese_character)].reset_index(drop=True)
    visualize(finalDF)

    # eraseCategories = ['studio', 'market', 'beauty_service', 'workshop']
    # final_reviews = pd.read_csv('./Apify/final_review_googlemap_comments.csv', sep=',', index_col=0)
    # categories_place = pd.read_csv('./Apify/final_category_of_places.csv', sep=',', index_col=0)
    # categories_place = categories_place[~categories_place['category'].isin(eraseCategories)]

    # patternIdplace = r'query_place_id=(.*)'
    # final_reviews['title'] = final_reviews['title'].map(lambda x: x.lower())
    # originalTitles = categories_place['title']
    # categories_place['title'] = categories_place['title'].map(lambda x: x.lower())
    # final_reviews['urlId'] = final_reviews['url'].map(lambda x: re.search(patternIdplace, x).group(1) if re.search(patternIdplace, x) else x)
    # categories_place['urlId'] = categories_place['url'].map(lambda x: re.search(patternIdplace, x).group(1) if re.search(patternIdplace, x) else x)
    
    # final_reviews_url_to_title = final_reviews.drop_duplicates(subset='urlId')[['urlId', 'title']].set_index('urlId')['title'].to_dict()
    # categories_place_url_to_title = categories_place.drop_duplicates(subset='urlId')[['urlId', 'title']].set_index('urlId')['title'].to_dict()
    # categories_place_url_to_category = categories_place.drop_duplicates(subset='urlId')[['urlId', 'category']].set_index('urlId')['category'].to_dict()
    # categories_place_title_to_category = categories_place.drop_duplicates(subset='title')[['title', 'category']].set_index('title')['category'].to_dict()
    
    # matchedPlaces = [(title, categories_place_url_to_category.get(urlId, 'unknown')) for urlId, title in final_reviews_url_to_title.items() if urlId in categories_place_url_to_title.keys()]
    # maybe_matchedPlaces = [title for urlId, title in final_reviews_url_to_title.items() if urlId not in categories_place_url_to_title.keys() and title not in [matched[0] for matched in matchedPlaces]]
    # matchedPlaces += [(title, categories_place_title_to_category.get(title, 'unknown')) for title in maybe_matchedPlaces if title in categories_place_url_to_title.values()]
    # notmatchedPlaces = [(title, 'unknown') for title in maybe_matchedPlaces if title not in [matched[0] for matched in matchedPlaces]]
    
    # matchedPlaces_dict = {place[0]: place[1] for place in matchedPlaces}
    # final_reviews['category'] = final_reviews['title'].map(matchedPlaces_dict)

    # final_reviews.drop(columns=['urlId'], inplace=True)
    # categories = list(final_reviews['category'].unique())
    # os.makedirs('DatasetGGMaps', exist_ok=True)
    # for category in categories:
    #     if category != np.Nan:
    #         pathCsv = f'./DatasetGGMaps/final_review_googlemap_comments_{category}.csv'
    #         dfReviews = final_reviews[final_reviews['category'] == category]
    #         dfReviews.reset_index(drop=True, inplace=True)
    #         dfReviews.to_csv(pathCsv)
    #         print(f'Tạo thành công file {pathCsv}')
    
    
    # with open('./attractions/matchings.json', 'r', encoding='utf-8') as f:
    #     matching_traveloka = json.load(f) 
    
    # with open('./attractions/attraction_DaLat.json', 'r', encoding='utf-8') as f:
    #     dataReviews = json.load(f) 

    # keep_matching_traveloka = {traveloka: ggmap for traveloka, ggmap in matching_traveloka.items() if ggmap.lower() in categories_place['title'].values}
    # print(f"Số lượng place từ traveloka tồn tại trong google maps: {len(keep_matching_traveloka)}")
    
    # matchingReviews = {}
    # for itemHotel in dataReviews:
    #     hotelName = itemHotel.get('name', 'unknown')
    #     hotelReviews = [review[0] for review in itemHotel.get('reviews', [])]
    #     if hotelName in keep_matching_traveloka.keys():
    #         if keep_matching_traveloka[hotelName] not in matchingReviews:
    #             matchingReviews[keep_matching_traveloka[hotelName]] = hotelReviews
    #         else:
    #             print(hotelName)
    #             matchingReviews[keep_matching_traveloka[hotelName]] += hotelReviews

    # hotelGGmaps = categories_place[(categories_place['category'] == 'attraction') & (categories_place['title'].isin(matchingReviews.keys()))]
    # matchingReviews = {title.lower(): listReviews for title, listReviews in matchingReviews.items()}
    # hotelGGmaps['reviewsTraveloka'] = hotelGGmaps['title'].map(matchingReviews)
    # matchingReviews_urlId = hotelGGmaps[['urlId', 'reviewsTraveloka']].set_index('urlId')['reviewsTraveloka'].to_dict()
  
    # reviewsTraveloka = final_reviews[(final_reviews['urlId'].isin(hotelGGmaps['urlId'].values)) | (final_reviews['title'].isin(hotelGGmaps['title'].values))]
    # reviewsTraveloka['text'] = reviewsTraveloka.apply(custom_mapping, axis=1, args=(matchingReviews, matchingReviews_urlId))
    # reviewsTraveloka = reviewsTraveloka.drop_duplicates(subset=['urlId'])
    # reviewsTraveloka = reviewsTraveloka.explode('text')
    # reviewsTraveloka.reset_index(drop=True, inplace=True)
    # reviewsTraveloka.drop(columns=['urlId'], inplace=True)
    # reviewsTraveloka.to_csv('./DatasetGGMaps/final_review_traveloka_comments_attraction.csv')
    
    
    # reviewsRentingTour = pd.read_csv('./DatasetGGMaps/final_review_googlemap_comments_tour_renting.csv', index_col=0)
    # pattern = 'thuê xe|motorbike|motobike|motor bike|motor|xe máy|xe dịch vụ|bike rent|xe'
    # rentPlaces = [normalize_unicode(place) for place in list(reviewsRentingTour['title'].unique()) if re.search(pattern, normalize_unicode(place), flags=re.IGNORECASE)]
    # tourPlaces = [normalize_unicode(place) for place in list(reviewsRentingTour['title'].unique()) if normalize_unicode(place) not in rentPlaces]
    
    # rentReviews = reviewsRentingTour[reviewsRentingTour['title'].isin(rentPlaces)]
    # tourReviews = reviewsRentingTour[reviewsRentingTour['title'].isin(tourPlaces)]
    # rentReviews.to_csv('./DatasetGGMaps/final_review_googlemap_comments_rent.csv')
    # tourReviews.to_csv('./DatasetGGMaps/final_review_googlemap_comments_tour.csv')
    
    # labels = json.load(open('./DatasetGGMaps/absa_cafe_service_labels_with_sentiment.json', 'r', encoding='utf-8'))
    # texts = pd.read_csv('./DatasetGGMaps/final_review_googlemap_comments_cafe.csv', index_col=0)
    
    # if len(labels) != len(texts):
    #     raise ValueError('Not same shape!!!')

    # full = []
    # for idx in range(len(labels)):
    #     rec_absa = {}
    #     rec_absa["text"] = texts["text"][idx]
    #     rec_absa["label"] = {}
    #     for aspect_dict in labels[str(idx)]:
    #         aspect = aspect_dict['aspect']
    #         sentiment = aspect_dict['sentiment']
    #         rec_absa["label"][aspect] = sentiment
    #     full.append({str(idx): rec_absa})
        
    # if len(full) != len(labels):
    #     raise ValueError('Not same shape!!!')
        
    # with open('./DatasetGGMaps/absa_cafe_service_labels_with_sentiment.json', 'w', encoding='utf-8') as f:
    #     json.dump(full, f, ensure_ascii=False, indent=4)