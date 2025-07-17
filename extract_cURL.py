import requests
import os
import json

cookies = {
    'TAUnique': '%1%enc%3A7EROaDtv%2FEHQC8fTV3Wlk%2Fg3cvG9K8Y1ydCaL7P9L4oKwSJCEYOPXb8y8ODKPG8gNox8JbUSTxk%3D',
    'TAUnique': '%1%enc%3A7EROaDtv%2FEHQC8fTV3Wlk%2Fg3cvG9K8Y1ydCaL7P9L4oKwSJCEYOPXb8y8ODKPG8gNox8JbUSTxk%3D',
    'TASameSite': '1',
    'TASSK': 'enc%3AAKtpdHq1uVnpbisIaOF3l8ZZ6xkZ3EtkuiRa33MZYf5gpGoTEZbxFDdfV8P2xbFbsgu6C0a0Uo1yu%2F4wOfjy8bIviEMYHgY2l5tyb%2FMcqhZkWstcXJL5Qh5H%2B1z7DxXRtQ%3D%3D',
    'TATrkConsent': 'eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9',
    '_gcl_au': '1.1.1275642037.1749577054',
    '_ga': 'GA1.1.1014861120.1749577054',
    '_lc2_fpi': '28c87295fd99--01jxdepe04ftyy43t780gdgh8r',
    '_lc2_fpi_meta': '%7B%22w%22%3A1749577054212%7D',
    'pbjs_sharedId': 'bdadfa96-398f-4788-9f21-f34373a8309a',
    'pbjs_sharedId_cst': 'zix7LPQsHA%3D%3D',
    '_lr_env_src_ats': 'false',
    'pbjs_unifiedID': '%7B%22TDID%22%3A%221bade59e-9768-4f5f-a7b0-70641d324187%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-05-10T17%3A37%3A33%22%7D',
    'pbjs_unifiedID_cst': 'zix7LPQsHA%3D%3D',
    'TATravelInfo': 'V2*A.2*MG.-1*HP.2*FL.3*RS.1',
    'TAUD': 'LA-1749650050664-1*RDD-1-2025_06_11',
    'VRMCID': '%1%V1*id.10568*llp.%2FRestaurant_Review-g293922-d24922389-Reviews-or30-Steak_Ngon-Da_Lat_Lam_Dong_Province%5C.html*e.1750257903465',
    'TART': '%1%enc%3ASTWzpfcz%2BY4BqbYJ4NiAagzKA6LEMogXWutspGpPdUJPOkU1BIDpcrNRJWzDV1UR4RNSWq8uk%2FA%3D',
    '_lr_sampling_rate': '100',
    'TADCID': 'ntxhHsnS5jtusRgNABQCJ4S5rDsRRMescG99HippfoZloHws7FtHFrUyT9gE-d7Ji1107AXNsnXL5bDdzzkFEwT0qQM0Augk9MA',
    'pbjs_li_nonid': '%7B%7D',
    'pbjs_li_nonid_cst': 'zix7LPQsHA%3D%3D',
    'TASID': 'E33518E6514109BFCB1478C41FF290AA',
    '_li_dcdm_c': '.tripadvisor.com.vn',
    'PAC': 'ACrLC25oqmzQHBFjSbynNHcA6WDT3zEqrr6VvMuYeX1FfKr0sc5ySNWWUL7eNgDfckkRc3a6mhSXafIxiXGfvr-dCA0T2KPnBQrx_7tPqfEH80a3lvlVWnIy2g0VCT3uftPiyainl3YrM522pgSVwoouTMcfSJ89zCv4xAzmQ4Zjiv_Fh77dR9y36PaQYN1QvyTj5C9rtIKTPBVC0RLNS2kToQK3CA4TQpX338hq1Mn7DDwxZdkhsXdFFOSUwf2I_g%3D%3D',
    '__gads': 'ID=9d88f277f4cc7883:T=1749577054:RT=1750511804:S=ALNI_MbIHv2KgeJrS3DMjylzFd9BjTSm3A',
    '__gpi': 'UID=000010267537bcb9:T=1749577054:RT=1750511804:S=ALNI_MZIZXe2VP0Cf1LynvcoIDaBmzLevw',
    '__eoi': 'ID=be7fccd3b83f4daa:T=1749577054:RT=1750511804:S=AA-AfjZ1vyoAApmCsi6G09ab_XH1',
    '_lr_retry_request': 'true',
    'SRT': 'TART_SYNC',
    '_gcl_aw': 'GCL.1750511913.null',
    'TASession': 'V2ID.E33518E6514109BFCB1478C41FF290AA*SQ.118*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true',
    '_ga_QX0Q50ZC9P': 'GS2.1.s1750508291$o12$g1$t1750511917$j36$l0$h0',
    'datadome': 's6KuJVYCSm4X4w_fHuj3~uROS2c7LqV5TVAj6neU8SIrdeKzMjIWAD_qdmv8b9OXs27y6d8LRXc~4Ddh9LrDhPlNLnYfMcwLpumjn7DJI9N6eq47NGq5oeXjO7TXEiSO',
    '__vt': '7P00JY7M2gGFuN3lABQCT24E-H_BQo6gx1APGQJPtzZFC9W-cF010_XKiws48eirfGhBYKwVIi4jBACoZZJWRyRKCdwf9C-6a1Yiv5nE0HAsjFs3a13TDzlh4jWnHgoeQDuzvSd6FmazBTlen-gz7IIYjQ',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.tripadvisor.com.vn',
    'priority': 'u=1, i',
    'referer': 'https://www.tripadvisor.com.vn/Restaurant_Review-g293922-d4100659-Reviews-Veronica_coffee-Da_Lat_Lam_Dong_Province.html',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="137.0.7151.119", "Chromium";v="137.0.7151.119", "Not/A)Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'same-origin',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    # 'cookie': 'TAUnique=%1%enc%3A7EROaDtv%2FEHQC8fTV3Wlk%2Fg3cvG9K8Y1ydCaL7P9L4oKwSJCEYOPXb8y8ODKPG8gNox8JbUSTxk%3D; TAUnique=%1%enc%3A7EROaDtv%2FEHQC8fTV3Wlk%2Fg3cvG9K8Y1ydCaL7P9L4oKwSJCEYOPXb8y8ODKPG8gNox8JbUSTxk%3D; TASameSite=1; TASSK=enc%3AAKtpdHq1uVnpbisIaOF3l8ZZ6xkZ3EtkuiRa33MZYf5gpGoTEZbxFDdfV8P2xbFbsgu6C0a0Uo1yu%2F4wOfjy8bIviEMYHgY2l5tyb%2FMcqhZkWstcXJL5Qh5H%2B1z7DxXRtQ%3D%3D; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; _gcl_au=1.1.1275642037.1749577054; _ga=GA1.1.1014861120.1749577054; _lc2_fpi=28c87295fd99--01jxdepe04ftyy43t780gdgh8r; _lc2_fpi_meta=%7B%22w%22%3A1749577054212%7D; pbjs_sharedId=bdadfa96-398f-4788-9f21-f34373a8309a; pbjs_sharedId_cst=zix7LPQsHA%3D%3D; _lr_env_src_ats=false; pbjs_unifiedID=%7B%22TDID%22%3A%221bade59e-9768-4f5f-a7b0-70641d324187%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222025-05-10T17%3A37%3A33%22%7D; pbjs_unifiedID_cst=zix7LPQsHA%3D%3D; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1; TAUD=LA-1749650050664-1*RDD-1-2025_06_11; VRMCID=%1%V1*id.10568*llp.%2FRestaurant_Review-g293922-d24922389-Reviews-or30-Steak_Ngon-Da_Lat_Lam_Dong_Province%5C.html*e.1750257903465; TART=%1%enc%3ASTWzpfcz%2BY4BqbYJ4NiAagzKA6LEMogXWutspGpPdUJPOkU1BIDpcrNRJWzDV1UR4RNSWq8uk%2FA%3D; _lr_sampling_rate=100; TADCID=ntxhHsnS5jtusRgNABQCJ4S5rDsRRMescG99HippfoZloHws7FtHFrUyT9gE-d7Ji1107AXNsnXL5bDdzzkFEwT0qQM0Augk9MA; pbjs_li_nonid=%7B%7D; pbjs_li_nonid_cst=zix7LPQsHA%3D%3D; TASID=E33518E6514109BFCB1478C41FF290AA; _li_dcdm_c=.tripadvisor.com.vn; PAC=ACrLC25oqmzQHBFjSbynNHcA6WDT3zEqrr6VvMuYeX1FfKr0sc5ySNWWUL7eNgDfckkRc3a6mhSXafIxiXGfvr-dCA0T2KPnBQrx_7tPqfEH80a3lvlVWnIy2g0VCT3uftPiyainl3YrM522pgSVwoouTMcfSJ89zCv4xAzmQ4Zjiv_Fh77dR9y36PaQYN1QvyTj5C9rtIKTPBVC0RLNS2kToQK3CA4TQpX338hq1Mn7DDwxZdkhsXdFFOSUwf2I_g%3D%3D; __gads=ID=9d88f277f4cc7883:T=1749577054:RT=1750511804:S=ALNI_MbIHv2KgeJrS3DMjylzFd9BjTSm3A; __gpi=UID=000010267537bcb9:T=1749577054:RT=1750511804:S=ALNI_MZIZXe2VP0Cf1LynvcoIDaBmzLevw; __eoi=ID=be7fccd3b83f4daa:T=1749577054:RT=1750511804:S=AA-AfjZ1vyoAApmCsi6G09ab_XH1; _lr_retry_request=true; SRT=TART_SYNC; _gcl_aw=GCL.1750511913.null; TASession=V2ID.E33518E6514109BFCB1478C41FF290AA*SQ.118*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true; _ga_QX0Q50ZC9P=GS2.1.s1750508291$o12$g1$t1750511917$j36$l0$h0; datadome=s6KuJVYCSm4X4w_fHuj3~uROS2c7LqV5TVAj6neU8SIrdeKzMjIWAD_qdmv8b9OXs27y6d8LRXc~4Ddh9LrDhPlNLnYfMcwLpumjn7DJI9N6eq47NGq5oeXjO7TXEiSO; __vt=7P00JY7M2gGFuN3lABQCT24E-H_BQo6gx1APGQJPtzZFC9W-cF010_XKiws48eirfGhBYKwVIi4jBACoZZJWRyRKCdwf9C-6a1Yiv5nE0HAsjFs3a13TDzlh4jWnHgoeQDuzvSd6FmazBTlen-gz7IIYjQ',
}

json_data = [
    {
        'variables': {
            'request': [
                {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'location_id': 4100659,
                    'last_referrer': '',
                    'geo_id': 293922,
                    'servlet_name': 'Restaurant_Review',
                    'user_id': None,
                    'session_id': 'E33518E6514109BFCB1478C41FF290AA',
                    'unique_id': 'ad849602.6467.4e0a.bc3c.3d680cc02be6.1975A9F77D2',
                    'pageview_id': '53eec9c4-7f2c-433d-872f-48870676f359',
                    'impression_details': None,
                    'impression_type': 'eat_rr_page_view_impression',
                    'from_ad': False,
                },
            ],
        },
        'extensions': {
            'preRegisteredQueryId': 'a94842cce3364226',
        },
    },
    {
        'variables': {
            'page': 'Restaurant_Review',
            'platform': 'tablet',
        },
        'extensions': {
            'preRegisteredQueryId': 'b4613962d98df032',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
        },
        'extensions': {
            'preRegisteredQueryId': 'b6d4e00c5b27f98e',
        },
    },
    {
        'variables': {
            'restaurantId': 'ta-4100659',
        },
        'extensions': {
            'preRegisteredQueryId': 'ae35fe517e04ff38',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'offset': 0,
            'limit': 3,
        },
        'extensions': {
            'preRegisteredQueryId': 'a74001171c4cc850',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'albumId': 107,
            'photosLimit': 15,
            'dataStrategy': 'mr',
            'client': 'rr',
        },
        'extensions': {
            'preRegisteredQueryId': '5a248f7d0220cca5',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
        },
        'extensions': {
            'preRegisteredQueryId': '6ba0d709c01afcf1',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'keywordVariant': 'location_keywords_v2_llr_order_30_vi',
            'language': 'vi',
        },
        'extensions': {
            'preRegisteredQueryId': '35767cee55993f9f',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'filters': [
                {
                    'axis': 'LANGUAGE',
                    'selections': [
                        'vi',
                    ],
                },
            ],
            'limit': 15,
            'offset': 0,
            'sortType': None,
            'sortBy': 'SERVER_DETERMINED',
            'language': 'vi',
            'useAwsTips': True,
        },
        'extensions': {
            'preRegisteredQueryId': '51c593cb61092fe5',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'userId': None,
            'taUnique': 'ad849602.6467.4e0a.bc3c.3d680cc02be6.1975A9F77D2',
        },
        'extensions': {
            'preRegisteredQueryId': 'c38e0b1677c86df8',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'loggedInUserId': None,
            'loggedIn': False,
            'language': 'vi',
            'useAwsTips': True,
        },
        'extensions': {
            'preRegisteredQueryId': 'fbbe6ef94d557131',
        },
    },
    {
        'variables': {
            'ids': [
                6948253,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                3532773,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                26999504,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                20897403,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                10822892,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                4379473,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                11868281,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                12369071,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                2389473,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'ids': [
                17750310,
            ],
        },
        'extensions': {
            'preRegisteredQueryId': '496720f897546a4e',
        },
    },
    {
        'variables': {
            'rssId': 'ta-4100659',
            'locationId': 4100659,
            'geoId': 293922,
            'locale': 'vi-VN',
            'currency': 'VND',
            'distanceUnitHotelsAndRestaurants': 'KILOMETERS',
            'distanceUnitAttractions': 'KILOMETERS',
            'numTimeslots': 6,
        },
        'extensions': {
            'preRegisteredQueryId': 'e50473638bca81f5',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
            'request': {
                'locationId': 4100659,
                'servletName': 'Restaurant_Review',
                'trafficSource': 'ba',
                'deviceType': 'MOBILE',
            },
        },
        'extensions': {
            'preRegisteredQueryId': '26088b5a6a35f110',
        },
    },
    {
        'variables': {
            'page': 'Restaurant_Review',
            'locale': 'vi-VN',
            'platform': 'tablet',
            'id': '4100659',
            'urlRoute': None,
        },
        'extensions': {
            'preRegisteredQueryId': 'd194875f0fc023a6',
        },
    },
    {
        'variables': {
            'locationId': 4100659,
        },
        'extensions': {
            'preRegisteredQueryId': '5d0440dab8324fbd',
        },
    },
]

def processing_comments(comment):
    new_comment = comment.replace('\n', '. ')
    return new_comment.strip()

def write_file_json(data_json, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)
        
def read_file_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    return data_json

def extract_reviews(list_resp_json):
    data_reviews = []
    for resp_json in list_resp_json:
        if 'ReviewsProxy_getReviewListPageForLocation' not in resp_json['data']:
            continue
        
        reviews = resp_json['data']['ReviewsProxy_getReviewListPageForLocation'][0]['reviews']
        name_rest = reviews[0]['location']['name']
        for review in reviews:
            comment = processing_comments(review['text'])
            rating = review['rating']
            data_reviews.append((comment, rating))
    return name_rest, data_reviews

def get_reviews(list_resp_json):
    data_rest = read_file_json('./eateries/comments_coffee_DaLat.json') if os.path.exists('./eateries/comments_coffee_DaLat.json') else []
    crawl_name = [rest['name'] for rest in data_rest]
    name_rest, data_reviews = extract_reviews(list_resp_json)
    data = {
        'name': name_rest,
        'reviews': data_reviews
    }
    if data_rest:
        if data_rest[-1]['name'].strip() != name_rest.strip():
            if name_rest not in crawl_name:
                data_rest.append(data)
            else:
                print('Đã thu thập đánh giá của nhà hàng này')
        else:
            data_rest[-1]['reviews'].extend(data['reviews'])
    else:
        data_rest.append(data)
        
    print(f"{data_rest[-1]['name']} - Số lượng đánh giá thu được {len(data_rest[-1]['reviews'])}")
    write_file_json(data_rest, './eateries/comments_coffee_DaLat.json')

if __name__ == '__main__':
    response = requests.post('https://www.tripadvisor.com.vn/data/graphql/ids', cookies=cookies, headers=headers, json=json_data)
    list_resp_json = response.json()
    get_reviews(list_resp_json)
    