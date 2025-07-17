import pandas as pd
import re
import sys
import os
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from preprocessor_text import VietnameseTextProcessor

def normalize_unicode(text):
    char1252 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
    charutf8 = r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'
    char_map = dict(zip(char1252.split('|'), charutf8.split('|')))
    return re.sub(char1252, lambda x: char_map[x.group()], text.strip())

# Gán nhãn HOTEL#LOCATION
def extract_hotel_location(text):
    location_keywords = [
        r"\bgần\b", r"\btrung tâm\b", r"\bvị trí.{0,10}?(đẹp|thuận tiện|dễ tìm|lý tưởng|hợp lý)?\b",
        r"cách .* [0-9]+ ?(m|km|phút|p)", r"di chuyển (dễ|thuận tiện|khó|bất tiện)", r"đi lại",
        r"tọa lạc", r"nằm (ở|trong|gần)", r"(đường|lối|hướng) (đi|vào|vô)", r"(gần|sát) bên",
        r"(dễ|khó) (tìm|kiếm)", 
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in location_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(gần kề|gần|ngay|sát) trung tâm\b", r"\bnằm gần\b", r"ngay gần", r"ngay cạnh", r"\b(rất|siêu) gần\b",
            r"(vị trí)?.{0,10}(tiện|tốt|rất đẹp|tuyệt vời|đẹp|thuận tiện|dễ tìm( thấy)?|lý tưởng|hợp lý|dễ thấy|thuận lợi|)",
            r"(đường|lối).{0,5}(đi|vào|vô).{0,10}(dễ|thuận tiện)",
            r"(ngay|nằm|ở).{0,5}trung tâm",
            r"\b(tìm|kiếm).{0,5}địa chỉ\b"
        ]    
        negative_patterns = [
            r"khó tìm", r"xa trung tâm", r"hẻo lánh", r"\b(bị lạc|không thấy đường|lạc đường|đi nhầm|vòng vèo|quanh co)\b"
            r"(đường|lối).{0,10}(khó|xấu|xa|vòng vèo|nhỏ|hẹp|gập ghềnh|chật|tối|khó thấy)", r"quá xa", r"ở tận", r"ở đâu không biết",
            r"vị trí.{0,10}(khó|xa|không.*thuận tiện|bất tiện|tệ|kém)", r"nằm( hơi|rất) xa",
            r"không.{0,10}(gần|thuận tiện|dễ tìm|dễ đi)", r"di chuyển.{0,10}(khó khăn|mất thời gian|bất tiện|khổ sở)",
            r"đi bộ.{0,10}(lâu|xa|mệt|đường dài)", r"\b(không|chưa|chẳng|đâu có).{0,3}(gần|thuận tiện|dễ tìm)\b",
            r"\b(khuất|góc khuất|ngõ cụt)\b", r"\bmất( nhiều|hơn) thời gian\b",
            r"\bxa (tít|tắp|mù)\b", r"\b(khó|trở ngại) (di chuyển|đi lại)\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None


# Gán nhãn HOTEL#FACILITIES
def extract_hotel_facilities(text):
    hotel_facilities_keywords = [
        r"\bkhông gian (chung|sinh hoạt)\b",
        r"\b(bãi |chỗ |nơi |chỗ để )?(đậu xe|đỗ xe|xe|parking)\b",
        r"\b(thang máy|(swimming )?pool|jacuzzi|phòng xông hơi)\b", r"\b(hồ|bể) (bơi|sục)\b",
        r"\b(bbq|khu nướng|tiệc nướng|vườn rau|vườn dâu)\b",
        r"\b(?!(quán\s))(?:(quầy|mini)\s)?bar\b",
        r"\b(khu|khu vực) (vui chơi|ăn uống|sinh hoạt|vườn|nấu ăn|tập gym|thể dục|yoga|đọc sách|chơi game|lửa trần|sảnh)\b",
        r"\b(phòng gym|phòng tập|phòng sinh hoạt|fitness)\b",
        r"\b(sân vườn|vườn hoa|vườn rau|vườn cây|sân thượng|terrace)\b",
        r"\b(sảnh chờ|lobby|sảnh khách)\b",
        r"\bbếp chung\b",
        r"\b(nhà hàng|restaurant|dining area)\b",
        r"\b(dịch vụ|service|gói) (ăn sáng|buffet|thuê xe|đưa đón|tour|massage|giặt ủi|spa|cho thuê xe máy|bicycle)\b",
        r"\b(xe đưa đón|đưa rước sân bay)\b",
        r"\b(thuê xe|xe.{0,10}cho thuê)\b"
        r"\b(máy bán nước|máy bán hàng tự động)\b",
        r"\b(tiện nghi|lò sưởi|)\b",
        r"\b(bàn (billiards|bida|bi-a))\b",
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in hotel_facilities_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(bể bơi|hồ bơi|pool).{0,8}(tốt|đẹp|xịn|sạch|rộng|ấn tượng|lý tưởng)\b",
            r"\b(bếp|khu nấu ăn).{0,8}(đầy đủ|tiện nghi|hiện đại|rộng rãi|sạch sẽ|thoáng mát)\b",
            r"\b(ăn sáng|buffet|nhà hàng).{0,8}(tốt|ngon|đa dạng|phong phú|đậm đà|hấp dẫn|tuyệt vời|đáng giá)\b",
            r"\b(lò sưởi|sưởi ấm).{0,5}(ấm áp|dễ chịu|tiện nghi|tuyệt vời)\b",
            r"\b(phòng gym|phòng tập).{0,8}(đầy đủ|hiện đại|rộng rãi|view đẹp)\b",
            r"\b(khu vườn|sân vườn).{0,8}(đẹp|thơ mộng|nhiều hoa|view đẹp|tranquil|yên bình)\b",
            r"\b(xe đưa đón|shuttle).{0,8}(đúng giờ|tiện lợi|nhanh chóng|miễn phí)\b",
            r"\b(tiện ích|tiện nghi|facilities|dịch vụ).{0,10}(xịn|tốt|đầy đủ|hiện đại|cao cấp|tuyệt vời|ấn tượng|vượt mong đợi)\b",
            r"có\s*(nhiều|đầy đủ)\s*(tiện nghi|dịch vụ)", 
            r"\b(bãi |chỗ |nơi |chỗ để )?(đậu xe|đỗ xe|xe|parking).{0,8}(rộng|thoải mái)\b"
        ]
        negative_patterns = [
            r"\b(bể bơi|hồ bơi|pool).{0,8}(bẩn|dơ|hôi|nhỏ|đông|không sử dụng|tạm đóng|đóng cửa)\b",
            r"\b(thang máy).{0,8}(chậm|hỏng|đông|không hoạt động|không có|nhỏ|cũ kỹ|lâu)\b",
            r"\b(bãi |chỗ |nơi |chỗ để )?(đậu xe|đỗ xe|xe|parking).{0,8}(nhỏ|khó|ít|chật|xa|khó tìm|không an toàn|trả phí|đắt|không có)\b",
            r"\b(ăn sáng|buffet|nhà hàng).{0,8}(dở|ít món|đơn điệu|không ngon|không đa dạng|giới hạn)\b",
            r"\b(bếp|khu nấu ăn).{0,8}(thiếu đồ|không đầy đủ|bẩn|chật|không vệ sinh)\b",
            r"\b(không có|thiếu).{0,8}(thang máy|bể bơi|hồ bơi|pool|bbq|((bãi |chỗ |nơi |chỗ để )?(đậu xe|đỗ xe|xe|parking))|buffet|nhà hàng|tiện nghi)",
            r"\b(lò sưởi|sưởi ấm).{0,5}(không hoạt động|hỏng|không đủ ấm)\b",
            r"\b(phòng gym|phòng tập).{0,8}(thiếu thiết bị|cũ|hỏng|không có|bỏ)\b",
            r"\b(khu vườn|sân vườn).{0,8}(bẩn|không chăm sóc|hoang tàn|không sử dụng)\b",
            r"\b(xe đưa đón|shuttle).{0,8}(không có|trễ|chậm|bỏ quên|thất hẹn)\b",
            r"\b(tiện nghi|facilities).{0,10}(thiếu|cũ|hỏng|không đạt|không như mô tả|tệ|kém)\b",
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None
            

# Gán nhãn HOTEL#STYLE
def extract_hotel_style(text):
    hotel_style_keywords = [
        r"(khách sạn|homestay|homstay|villa|resort|hotel|home).{0,10}(ấn tượng|độc đáo|đặc biệt|đẹp|thẩm mỹ|thiết kế|phong cách|vibe|decor|bày trí|trang trí|style|kiến trúc|xinh|nội thất|ngoại thất)",
        r"(kiểu dáng|mẫu mã|bố cục|màu sắc|tông màu|chất liệu|thẩm mỹ|thiết kế|phong cách|vibe|decor|bày trí|trang trí|style|kiến trúc|nội thất|ngoại thất|đẹp|ấn tượng|độc đáo|đặc biệt).{0,10}(khách sạn|homestay|homstay|villa|resort|hotel|home)"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in hotel_style_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(thiết kế|decor|bày trí|trang trí|kiến trúc).{0,10}(đặc biệt|đặc sắc|đặc trưng|độc nhất|hiếm có|xinh|đẹp|lãng mạn|đậm chất|đúng chất|hài hòa|hoàn hảo|tuyệt vời|ấm cúng|sang trọng|đẹp|ấn tượng|xịn|dễ thương|đáng yêu|độc đáo|hiện đại|tinh tế|xịn xò|lung linh)\b",
            r"\b(vibe|style).{0,10}(xịn|chill|ấm áp|thư giãn|dễ chịu|lãng mạn|sang trọng|độc đáo|đặc biệt|cá tính|retro|hoài cổ)\b",
            r"\b(kiến trúc|phong cách).{0,10}(đặc biệt|đặc sắc|đặc trưng|độc nhất|hiếm có|Pháp|châu Âu|vintage|hoài cổ|mộc mạc|gỗ|đá|tối giản|Scandinavian|boutique)\b",
            r"\b(nội thất|ngoại thất).{0,10}(cao cấp|chất lượng|đẹp|ấn tượng|tinh tế|phối màu hài hòa|ấm áp)\b",
            r"\b(đèn lồng|đèn trang trí|lò sưởi|ốp gỗ|ốp đá).{0,10}(đẹp|ấn tượng|ấm áp|lãng mạn|đậm chất Đà Lạt)\b",
            r"\b(tông màu|màu sắc).{0,10}(ấm áp|dễ chịu|hài hòa|phù hợp|ấn tượng)\b"
        ]
        negative_patterns = [
            r"\b(thiết kế|kiến trúc|phong cách|decor|trang trí|bày trí).{0,10}(sơ sài|xấu|cũ|kỳ dị|lỗi thời|không đẹp|rối mắt|khó hiểu|kém|đơn điệu|nhàm chán|tẻ nhạt|sơ sài|lộn xộn|không đồng bộ|không phối hợp|không ấn tượng)\b",
            r"\b(vibe|style).{0,10}(buồn|ảm đạm|kỳ lạ|không hợp|không thoải mái|khó chịu|nặng nề|tiêu cực|rối mắt)\b",
            r"\b(kiến trúc|phong cách).{0,10}(không rõ ràng|lẫn lộn|không nhất quán|lai căng|không phù hợp)\b",
            r"\b(nội thất|ngoại thất).{0,10}(cũ|hỏng|bẩn|bong tróc|không đồng bộ|lỗi thời|rẻ tiền|kém chất lượng)\b",
            r"\b(màu sắc|tông màu).{0,10}(chói mắt|không hài hòa|u ám|lạnh lẽo|ảm đạm)\b",
            r"\b(kiến trúc|thiết kế).{0,10}(giống nhà kho|như ký túc xá|như bệnh viện|thiếu đầu tư)\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


#Gán nhãn HOTEL#QUALITY
def extract_hotel_quality(text):
    hotel_quality_keywords = [
        r"\b(khách sạn|homestay|villa|resort|hotel|bungalow|nhà nghỉ|biệt thự|căn hộ|dorm|hostel|stay|nhà).{0,10}?(ok|tốt|tệ|ổn|ngon|đỉnh|dở|không ra gì|đáng tiền|đáng giá|xứng đáng|không đáng với giá|quá đáng thất vọng|đẹp|xinh|xịn|sang|mới|cũ|xuống cấp|((không )?như (hình|mong đợi))|khác hình|vượt mong đợi|tốt hơn mình nghĩ|đáng đồng tiền|chất)\b",
        r"\b(chất lượng|đẳng cấp|level|standard|tổng quan|tổng thể|chung|overall|đánh giá|trải nghiệm|tổng kết).{0,10}?(khách sạn|homestay|villa|resort|hotel|bungalow|nhà nghỉ|biệt thự|căn hộ|dorm|hostel|stay|nhà)\b",
        r"\b(khách sạn|homestay|villa|resort|hotel|bungalow|nhà nghỉ|biệt thự|căn hộ|dorm|hostel|stay|nhà).{0,10}?(không như|khác xa|không giống|không đúng|trái ngược|khác biệt|không phản ánh đúng|không khớp).{0,10}?(hình( ảnh)?|ảnh|quảng cáo|mong đợi|kỳ vọng|trên mạng|bài đăng|bài viết)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in hotel_quality_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(khách sạn|homestay|villa|resort|hotel|bungalow|nhà nghỉ|biệt thự|căn hộ|dorm|hostel|stay|nhà).{0,15}?(đẹp|tốt|xịn|sang|mới|vượt mong đợi|tốt hơn mình nghĩ|đáng tiền|xứng đáng|ok|đỉnh|chất|lý tưởng|hoàn hảo|tuyệt vời)\b",
            r"\b(chất lượng|đẳng cấp|tổng quan|tổng thể).{0,10}?(tốt|xịn|ok|đáng giá|xứng đáng|cao|ấn tượng|vượt trội|tuyệt|hoàn hảo)\b",
            r"\b(giống y hình|như hình|phản ánh đúng thực tế|tốt hơn mình nghĩ|đẹp hơn trong hình)\b",
            r"\b(đồng tiền xứng đáng|tiền nào của nấy|chất lượng tương xứng giá|giá trị xứng đáng|đáng đồng tiền bát gạo)\b",
            r"\b(so với giá tiền|so với chi phí).{0,10}?(xứng đáng|đáng giá|rất tốt|hơn mong đợi)\b",
            r"\b(tổng kết|kết luận|sau cùng).{0,10}?(hài lòng|tốt|đáng tiền|nên trải nghiệm|sẽ quay lại)\b"
        ]
        negative_patterns = [
            r"\b(khách sạn|homestay|villa|resort|hotel|bungalow|nhà nghỉ|biệt thự|căn hộ|dorm|hostel|stay|nhà).{0,10}(tệ|dở|cũ|xuống cấp|không ra gì|không đáng tiền|quá đáng thất vọng|không như hình|khác hình|khác xa|không giống|không đúng|không phản ánh đúng|không khớp|kém chất lượng|tồi tàn|nhếch nhác)\b",
            r"\b(chất lượng|đẳng cấp|tổng quan|tổng thể).{0,10}?(kém|tệ|thất vọng|không tốt|quá tệ|không hài lòng|dưới trung bình|tệ hại|thấp|kém cỏi)\b",
            r"\b(hình ảnh|ảnh trên mạng|quảng cáo).{0,10}?(không đúng|khác|lừa tình|lừa đảo|không giống thực tế|ảo)\b",
            r"\b((không (như mong đợi|xứng đáng|giống trên mạng))|thất vọng tràn trề|không tương xứng giá|đắt mà không xứng)\b",
            r"\b(so với giá tiền|so với chi phí).{0,10}?(không xứng|quá đắt|không đáng|thất vọng|kém)\b",
            r"\b(tổng kết|kết luận|sau cùng).{0,10}?(không hài lòng|thất vọng|không nên|không quay lại|không đáng tiền)\b",
            r"\b(lừa đảo|scam|hớ|chém|bị hố|tiền mất tật mang)\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn WIFI
def extract_wifi(text):
    wifi_keywords = [
        r"\b(wifi|wi-fi|internet|mạng|kết nối mạng|truy cập mạng|sóng)\b",
        r"\b(tín hiệu|tốc độ mạng|mạng internet|free wifi|wifi miễn phí|wifi free)\b",
        r"\b(kết nối|connect|online|mạng yếu|mạng chậm)\b",
        r"\b(mạng|wifi|wi-fi|internet).{0,10}?(yếu|chậm|mạnh|rớt|không ổn|kém|tốt|ổn định|kết nối|rất ok|xài được)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in wifi_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(wifi|mạng|internet|wi-fi|kết nối|tín hiệu|sóng).{0,10}(mạnh|đầy đủ|không có vấn đề|full|phủ khắp nơi|khắp khuôn viên|mọi góc|từ phòng đến sân vườn|mạnh|nhanh|tốt|ổn định|rất ok|kết nối tốt|full vạch|đầy đủ|khỏe|tuyệt vời|rất ổn|mượt)\b",
            r"\btruy cập.{0,10}(dễ dàng|nhanh chóng|ổn định|mượt mà|tốt)\b",
            r"\btốc độ.{0,10}(cao|nhanh|ổn định|đủ xem phim|đủ làm việc|tải nhanh)\b",
            r"\bkhông (gặp vấn đề|trục trặc|gặp lỗi|gián đoạn).{0,10}(wifi|mạng|internet)\b"
        ]
        negative_patterns = [
            r"\b(wifi|mạng|internet|wi-fi|kết nối|tín hiệu|sóng).{0,10}(chỉ ở sảnh|chỉ một số khu vực|không phủ rộng|không vào được phòng|yếu|chậm|rớt|lỗi|không ổn|kém|tệ|rất tệ|lúc được lúc không|gián đoạn|có vấn đề|(không (xài|sử dụng|kết nối|mượt)( được)?)|)\b",
            r"\btruy cập.{0,10}(khó khăn|thất bại|gián đoạn|không được|chậm)\b",
            r"\btốc độ.{0,10}(chậm|rùa bò|như rùa|không chấp nhận được|không đủ dùng)\b",
            r"\b(không thể|không).{0,5}(xem phim|làm việc online|gọi video|tải file).{0,10}(wifi|mạng)\b",
            r"\b(bực mình|khó chịu|ức chế).{0,10} vì (wifi|mạng|internet)\b",
            r"\b(mất sóng|mất kết nối).{0,10}thường xuyên\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn PRICE
def extract_price(text):
    price_keywords = [
        r"\b(giá|phí|chi phí).{0,10}(cả|phòng|thuê|dịch vụ|tiền|đêm|qua đêm|booking|đặt phòng|((dịp )?(lễ|tết))|mùa cao điểm|mùa thấp điểm|khuyến mãi|ưu đãi|công bố|niêm yết|cuối tuần|ngày thường|phòng)",
        r"\b(giá|phí|chi phí).{0,10}(bình thường|mềm|cao|đắt|mắc|rẻ|bèo|hạt dẻ|hợp lý|phải chăng|sốc|chát|hời|bình dân|chợ|dân dã|ổn|sinh viên)\b",
        r"\b(không )?(đáng|xứng) (với )?(đồng|giá )?tiền\b",
        r"\b(tiền nào của nấy|tiền nào phòng nấy|cắt cổ|trên trời|đắt đỏ|giá du lịch|giá khách du lịch|mức giá|hợp túi tiền|vừa túi tiền)\b",
        r"\b((đắt (xắt ra miếng|đỏ))|treo đầu dê bán thịt chó|bị chém|bị hớ|hớ giá)\b",
        r"\b(so sánh|so với).{0,10}?(chỗ khác|đối thủ|khu vực|giá trị nhận được)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in price_keywords)
    if existAspect:
        positive_patterns = [
            r"(giá|chi phí|phí).{0,10}?(rẻ|bình dân|dân dã|hạt dẻ|bèo|hợp lý|phải chăng|tốt|ổn|mềm|hời|hợp túi tiền|vừa túi tiền|sinh viên|ưu đãi)",
            r"\bgiá.{0,5}?(mềm|rẻ|hạt dẻ|bình dân).{0,10}?(so với|cho).{0,10}?(chất lượng|dịch vụ|địa điểm)\b",
            r"\b(đáng (đồng )?tiền|xứng đáng|đáng giá|giá hợp lý|giá ok|giá tốt|giá hời)\b",
            r"\b(tiền nào của nấy|giá cả đi đôi với chất lượng|chất lượng xứng giá)\b",
            r"\bgiá.{0,10}?(mùa thấp điểm|ngày thường|ưu đãi|khuyến mãi|giảm giá|promotion).{0,10}?(tốt|hấp dẫn|đáng giá|hợp lý|rẻ)\b",
            r"\b((rẻ|tốt|hợp lý|phải chăng) hơn )?so với.{0,10}?(chỗ khác|đối thủ|khu vực).{0,10}?((rẻ|tốt|hợp lý|phải chăng) hơn)?\b",
        ]
        negative_patterns = [
            r"(giá|phí|chi phí).{0,10}?(cao|đắt|mắc|chát|sốc|không hợp lý|không đáng|không xứng|trên trời|cắt cổ|đắt đỏ|quá đáng|khủng|hớ)",
            r"\b(giá).{0,5}?(đắt|cao|sốc).{0,10}?(so với|cho).{0,10}?(chất lượng|dịch vụ|địa điểm)\b",
            r"(giá).{0,10}?(quá cao|trên trời|cắt cổ|chém gió|chém du lịch|bóc lột)",
            r"\b(treo đầu dê bán thịt chó|bị chém|bị hớ|giá hớ|hớ giá|giật mình vì giá|không đáng|không xứng)\b",
            r"\b(giá).{0,10}?(dịp lễ|tết|mùa cao điểm).{0,10}?(đắt|cắt cổ|sốc|quá đáng)\b",
            r"\b(đắt hơn |cao hơn |không hợp lý )?(so với).{0,10}?(chỗ khác|đối thủ|khu vực).{0,10}?(đắt hơn|cao hơn|không hợp lý)?\b",
        ]

        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None


# Gán nhãn ROOM#STYLE
def extract_room_style(text):
    room_style_keywords = [
        r"\b(phòng|căn phòng|phòng ngủ|room|suite|studio|dorm|bungalow|căn hộ|phòng ốc).{0,10}(ấn tượng|độc đáo|đặc biệt|đẹp|thẩm mỹ|thiết kế|phong cách|vibe|decor|bày trí|trang trí|style|kiến trúc|xinh)\b",
        r"\b(ấn tượng|độc đáo|đặc biệt|đẹp|thẩm mỹ|thiết kế|phong cách|vibe|decor|bày trí|trang trí|style|kiến trúc|xinh).{0,10}(phòng|căn phòng|phòng ngủ|room|suite|studio|dorm|bungalow|villa|căn hộ|phòng ốc)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in room_style_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(ấm áp|hài hòa|lãng mạn|mới|đẹp|xinh|ấn tượng|độc đáo|tuyệt vời|hoàn hảo|lãng mạn|ấm cúng|dễ thương|đáng yêu|chill|sang trọng)\b",
            r"\b(thiết kế|phong cách|decor).{0,10}?(đẹp|tinh tế|ấn tượng|độc đáo|hài hòa|sang trọng|hiện đại|ấm cúng|dễ thương|đậm chất|đúng chất|hợp lý)\b",
            r"\b(vibe|style).{0,10}?(chill|ấm áp|thư giãn|dễ chịu|lãng mạn|sang trọng|độc đáo|đặc biệt|cá tính|retro|hoài cổ|Đà Lạt|Tây Nguyên)\b",
            r"\b(kiến trúc|phong cách).{0,10}(đặc biệt|đặc sắc|đặc trưng|độc nhất|hiếm có|Pháp|châu Âu|vintage|hoài cổ|mộc mạc|gỗ|đá|tối giản|Scandinavian|boutique)\b",
            r"\b(sống ảo|sống ảo đẹp|chụp hình đẹp|instagrammable|đẹp|ấn tượng|thiết kế độc đáo|hiện đại)\b",
        ]
        negative_patterns = [
            r"(xấu|cũ|kỳ dị|lỗi thời|không đẹp|rối mắt|khó chịu|đơn điệu|nhàm chán|tẻ nhạt|sơ sài|lộn xộn|chật chội|ảm đạm|u ám)",
            r"\b(thiết kế|phong cách|decor).{0,10}?(xấu|cũ|kém|không đẹp|rối rắm|lộn xộn|không đồng bộ|không phối hợp|lỗi thời|nhàm chán|sơ sài)\b",
            r"\b(vibe|style).{0,10}?(buồn|ảm đạm|kỳ lạ|không hợp|không thoải mái|khó chịu|nặng nề|tiêu cực|lạnh lẽo|rối mắt)\b",
            r"\b(kiến trúc|phong cách).{0,10}(không rõ ràng|lẫn lộn|không nhất quán|lai căng|không phù hợp)\b",
            r"\b(như nhà kho|như ký túc xá|như bệnh viện|thiếu đầu tư|không được decor|tối|không ấm áp|không phù hợp|chói mắt|không hài hòa)\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


#Gán nhãn ROOM#QUALITY
def extract_room_quality(text):
    room_quality_keywords = [
        r"\b(phòng|căn phòng|room|suite|studio|dorm|bungalow|căn hộ|chỗ nghỉ).{0,10}(ok|tốt|tệ|ổn|ngon|đỉnh|dở|không ra gì|đáng tiền|đáng giá|xứng đáng|không đáng với giá|quá đáng thất vọng|đẹp|xinh|xịn|sang|mới|cũ|xuống cấp|như hình|không như hình|khác hình|không như mong đợi|vượt mong đợi|tốt hơn mình nghĩ|đáng đồng tiền|chất)\b",
        r"\b(chất lượng|đẳng cấp|level|standard|tổng quan|tổng thể|chung|overall|đánh giá|trải nghiệm|tổng kết).{0,10}(phòng|căn phòng|room|suite|studio|dorm|bungalow|căn hộ|chỗ nghỉ)\b",
        r"\b(phòng|căn phòng|room|suite|studio|dorm|bungalow|căn hộ|chỗ nghỉ).{0,10}(so với|so sánh|so với hình|so với ảnh|so với quảng cáo|so với mong đợi|so với kỳ vọng|không như|khác xa|không giống|không đúng|trái ngược|khác biệt|không phản ánh đúng|không khớp).{0,10}(hình( ảnh)?|ảnh|quảng cáo|mong đợi|kỳ vọng|trên mạng|bài đăng|bài viết)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in room_quality_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(phòng|căn phòng|room|suite|studio|dorm|bungalow|căn hộ|chỗ nghỉ).{0,10}?(đẹp|xinh|tốt|xịn|sang|mới|vượt mong đợi|tốt hơn mình nghĩ|đáng tiền|xứng đáng|ok|đỉnh|chất|lý tưởng|hoàn hảo|tuyệt vời)\b",
            r"\b(chất lượng|đẳng cấp|tổng quan|tổng thể|trải nghiệm).{0,10}?(tốt|xịn|ok|đáng giá|xứng đáng|cao|ấn tượng|vượt trội|tuyệt|hoàn hảo)\b",
            r"\b(giống y hình|như hình|phản ánh đúng thực tế|tốt hơn mình nghĩ|đẹp hơn trong hình)\b"
        ]
        negative_patterns = [
            r"\b(phòng|căn phòng|room|suite|studio|dorm|bungalow|căn hộ|chỗ nghỉ).{0,10}(tệ|dở|cũ|xuống cấp|không ra gì|không đáng tiền|quá đáng thất vọng|không như hình|khác hình|khác xa|không giống|không đúng|không phản ánh đúng|không khớp|kém chất lượng|tồi tàn|nhếch nhác)\b",
            r"\b(chất lượng|đẳng cấp|tổng quan|tổng thể|trải nghiệm).{0,10}(kém|tệ|thất vọng|không tốt|quá tệ|không hài lòng|dưới trung bình|không như kỳ vọng|tệ hại|thấp|kém cỏi)\b",
            r"\b(hình ảnh|ảnh trên mạng|quảng cáo).{0,10}?(không đúng|khác|lừa tình|lừa đảo|không giống thực tế|ảo)\b",
            r"\b((không (như mong đợi|xứng đáng|giống trên mạng))|thất vọng tràn trề|không tương xứng giá|đắt mà không xứng)\b",
            r"\bphòng.{0,10}?(lạnh|gió lùa|ẩm thấp|nồm).{0,10}?(đã bật|sử dụng).{0,10}?(máy sưởi|lò sưởi)\b",
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn ROOM#FACILITES
def extract_room_facilities(text):
    facilities_keywords = [
        r"\b(máy lạnh|máy điều hòa|máy sưởi|tủ lạnh|bàn|ghế|giường|tivi|tv|máy sấy|máy sấy tóc|máy nước nóng|nước nóng|ấm đun|ấm siêu tốc|két sắt|quạt|bếp điện|đèn ngủ|nội thất|trang thiết bị|tiện nghi|đầy đủ tiện nghi)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in facilities_keywords)
    if existAspect:
        positive_patterns = [
            r"(tiện nghi|trang thiết bị|nội thất|máy lạnh|máy điều hòa|máy nước nóng|đầy đủ).{0,10}(tốt|đầy đủ|xịn|mới|hoạt động tốt|ok|rất ổn|xài ngon|ổn định)",
            r"(máy lạnh|tivi|tv|máy sưởi|nội thất).{0,10}(mạnh|mới|xịn|thích)",
            r"(tiện nghi|thiết bị).{0,10}(hiện đại|sạch|ok)"
        ]
        negative_patterns = [
            r"(thiết bị|máy lạnh|tivi|tv|máy sưởi|máy nước nóng|nội thất).{0,10}(cũ|kém|hỏng|không hoạt động|không chạy|không dùng được|rỉ sét|lỗi)",
            r"(không có|thiếu|thiếu hụt|không đầy đủ).{0,10}(tiện nghi|nội thất|trang thiết bị)",
            r"(thiết bị|nội thất|máy lạnh|máy sưởi).{0,10}(rất tệ|tệ|kém chất lượng)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn ROOM#SOUND
def extract_room_sound(text):
    room_sound_keywords = [
        r"\bcách âm\b",
        r"\b(yên tĩnh|yên lặng|im ắng|ồn kinh khủng|quá ồn|ồn ào|ồn|nhiều tiếng)\b",
        r"(phòng|căn phòng).*?(yên tĩnh|yên lặng|im ắng|ồn|ồn ào|nhiều tiếng)",
        r"(yên tĩnh|yên lặng|im ắng|ồn|ồn ào|nhiều tiếng).*?(phòng|căn phòng)",
        r"(không|chưa).*cách âm",
        r"cách âm.*?(tốt|kém|không tốt|rất tốt|tệ|kỹ|kỹ càng|ổn|kỹ lưỡng)"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in room_sound_keywords)
    if existAspect:
        positive_patterns = [
            r"(phòng|căn phòng).{0,10}?(yên tĩnh|yên lặng|im ắng)",
            r"(cách âm).{0,10}?(tốt|ổn|rất tốt|kỹ|kỹ lưỡng)",
            r"không nghe thấy.*(tiếng|ồn)",
            r"khá yên tĩnh|rất yên tĩnh|không bị ồn"
        ]
        negative_patterns = [
            r"(phòng|căn phòng).{0,10}?(ồn|ồn ào|nhiều tiếng|ồn kinh khủng|rất ồn)",
            r"(cách âm).{0,10}?(tệ|kém|không tốt|không ổn|không kỹ|quá tệ)",
            r"(không|chưa).{0,5}?cách âm",
            r"nghe rõ tiếng.*(bên cạnh|phòng bên|hành lang)",
            r"khó ngủ vì.*(ồn|tiếng)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"

    return None


# Gán nhãn ROOM#VIEW
def extract_room_view(text):
    hard_keywords = [
        r"phòng (có view|nhìn ra)",
        r"(cảnh nhìn|cảnh đẹp|view) từ phòng",
        r"(cửa sổ|ban công) nhìn ra",
        r"ban công có view",
    ]

    soft_keywords = [
        r"\bphòng.{0,15}?(view|nhìn ra|cửa sổ|ban công|hướng ra)",
        r"(view|nhìn ra|ban công|cửa sổ|hướng ra).{0,15}?phòng",
        r"\bban công.{0,10}?(view|nhìn ra)",
        r"\bcửa sổ.{0,10}?(view|nhìn ra)",
        r"view\s+(biển|núi|thung lũng|rừng|đồi|vườn|toàn cảnh)"
    ]

    # Tránh nhầm lẫn: view của homestay/villa chứ không phải phòng
    if re.search(normalize_unicode(r"\b(homestay|villa|khách sạn|resort|home).{0,10}?(view|rừng|núi|biển)"), text):
        if not re.search(normalize_unicode(r"\b(phòng|ban công|cửa sổ)\b"), text):
            return None

    existAspect = any(normalize_unicode(hard_keyword) in text for hard_keyword in hard_keywords) or any(re.search(normalize_unicode(soft_keyword), text, re.IGNORECASE) for soft_keyword in soft_keywords)
    if existAspect:
        positive_patterns = [
            r"(view|cảnh).{0,10}?(đẹp|chill|xịn|rất đẹp|ấn tượng|thơ mộng|đỉnh|mê|hấp dẫn|lung linh|tuyệt vời)",
            r"(view|nhìn ra).{0,10}?(biển|núi|thung lũng|rừng|đồi|vườn|toàn cảnh)",
            r"(ban công|cửa sổ).{0,10}?(view|nhìn ra).{0,10}?(biển|núi|thung lũng|rừng|vườn|đồi)",
            r"view (ngắm)?.*(mặt trời mọc|triệu đô)"
        ]
        negative_patterns = [
            r"(view|cảnh).{0,10}?(xấu|không đẹp|không như hình|bị chắn|tệ|không tốt)",
            r"(view).{0,10}?(bị che|không thấy gì)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"

    return None


# Gán nhãn ROOM#ATMOSPHERE
def extract_room_atmosphere(text):
    atmosphere_keywords = [
        r"(không khí|ánh sáng|cảm giác|không gian|ko gian|ấm cúng|thoải mái|rộng rãi|ngột ngạt|bí bách|dễ chịu|như ở nhà|ấm áp|gần gũi|mùi hương)",
        r"\bphòng thơm\b", r"\bánh sáng tự nhiên\b", r"\bmùi dễ chịu\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in atmosphere_keywords)
    if existAspect:
        positive_patterns = [
            r"(không khí|ánh sáng|mùi hương|mùi|cảm giác|phòng|không gian).{0,10}?(tốt|dễ chịu|thơm|thoải mái|ấm cúng|ấm áp|gần gũi|rộng rãi|lung linh|tự nhiên)",
            r"(ánh sáng tự nhiên|mùi dễ chịu|phòng thơm)",
            r"(cảm giác|trải nghiệm).{0,10}?(như ở nhà|dễ chịu)"
        ]
        negative_patterns = [
            r"(không khí|phòng|căn phòng).{0,10}?(bí bách|bí|ngột ngạt|khó chịu|khó thở|thiếu ánh sáng)",
            r"ánh sáng.{0,10}?(tối|kém|thiếu)",
            r"(mùi|mùi hương).{0,10}?(khó chịu|lạ|hôi)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None


# Gán nhãn ROOM#CLEANLINESS
def extract_room_cleanliness(text):
    cleanliness_keywords = [
        r"\b(sạch|sạch sẽ|ngăn nắp|dọn vệ sinh|lau dọn|dọn dẹp|vệ sinh)\b",
        r"\b(bẩn|dơ|rất bẩn|khá bẩn|mùi lạ|hôi|mùi khó chịu)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in cleanliness_keywords)
    if existAspect:
        positive_patterns = [
            r"(rất|khá)?\s?(sạch|sạch sẽ|ngăn nắp|sạch bong|sạch tinh tươm)",
            r"dọn (dẹp|vệ sinh|lau dọn) (kỹ|kĩ|rất tốt|gọn gàng)",
            r"phòng được lau dọn (kỹ|kĩ|gọn gàng|rất sạch)"
        ]
        negative_patterns = [
            r"(rất|khá)?\s?(bẩn|dơ|mùi lạ|hôi|khó chịu)",
            r"không (sạch|gọn|ngăn nắp|vệ sinh)",
            r"phòng còn (bẩn|mùi|rác)",
            r"dọn vệ sinh (sơ sài|không kỹ|qua loa)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None


# Gán nhãn SERVICE#STAFF
def extract_service_staff(text):
    staff_entities = [
        r"\b(nhân viên|staff|hướng dẫn( viên)?|chăm sóc khách hàng|người phụ trách|chủ vườn|lễ tân)\b",
        r"\b(cô chú|ông bà|anh|chị|bác|cô|chú|ông|bà).{0,10}(phụ trách|hướng dẫn|quản lý|chủ)?\b"
    ]
    staff_activities = [
        r"\b(tích cực|hòa đồng|thái độ|nhiệt tình|thuyết minh|giới thiệu|dịch vụ|chu đáo|hiếu khách|lịch sự|thân thiện|tốt)\b",
        r"\b(thân thiện|niềm nở|nhẹ nhàng|hết lòng|tận tâm|tận tình|chu đáo|quan tâm|tử tế)\b",
        r"\b(service|chăm sóc|hỗ trợ|phục vụ|hướng dẫn|tư vấn|giải đáp|đón tiếp|tiếp đón|quan tâm|giúp đỡ)\b",
        r"\bxử lý\s*(tình huống|vấn đề)\b",
        r"\b(dở|vô duyên|tiêu cực|kém|đáng chê|tồi|chậm chạp|thô lỗ|tệ|khó chịu|cộc cằn|gắt gỏng|thờ ơ|bỏ mặc|phớt lờ|lạnh nhạt|khó tính)\b",
        r"\b(hỗn|vô lễ|bất lịch sự|khinh thường|mất dạy|láo|lơ|phớt lờ|quát|mắng|chửi|đe dọa)\b",
        r"\b(phân biệt đối xử|đòi tiền tip|vòi vĩnh|chèn ép|quay lưng)\b",
    ]
    
    existAspect = any(re.search(normalize_unicode(entity), text, re.IGNORECASE) for entity in staff_entities) or any(re.search(normalize_unicode(activity), text, re.IGNORECASE) for activity in staff_activities)
    if existAspect:
        positive_patterns = [
            r"(?<!\bchưa\s)\b(nhanh nhẹn|tận tình|hòa đồng|mến khách|rất ok|tuyệt vời|tốt|chuyên nghiệp|đáng khen|xuất sắc|hoàn hảo|bằng mọi cách|bằng mọi giá|tốt nhất|nhiệt tình|dễ thương|vui tính|vui vẻ|hiếu khách|lịch sự|thân thiện|niềm nở|nhẹ nhàng|hết lòng|tận tâm|tận tình|chu đáo|quan tâm|tử tế)\b",
            r"\b(nhân viên|đội ngũ).{0,10}?(thuyết minh|giới thiệu).{0,10}?(rất hay|hấp dẫn|sinh động)\b",
            r"(?<!\bchưa\s)\b(hướng dẫn|tư vấn|giúp đỡ|chăm sóc|hỗ trợ|quan tâm|chăm sóc|phục vụ|service).{0,10}?(hiệu quả|tốt|tận tình|rất tốt|chu đáo|từng bước|kỹ)\b",
            r"\b(ấn tượng|hài lòng|thích).{0,10}?(với|về).{0,10}?(nhân viên|đội ngũ)\b",
            r"\b(luôn mỉm cười|luôn tươi cười|nụ cười|thái độ tích cực)\b",
        ]
        negative_patterns = [
            r"\b(cục súc|vô duyên|tiêu cực|không tốt|kém|đáng chê|tồi|chậm chạp|thái độ|thô lỗ|tệ|khó chịu|cộc cằn|gắt gỏng|thờ ơ|bỏ mặc|phớt lờ|lạnh nhạt|khó tính|hỗn|vô lễ|bất lịch sự|khinh thường|mất dạy|láo|không trả lời|lơ|phớt lờ|không quan tâm|quát|mắng|chửi|đe dọa)\b",
            r"\b(phân biệt đối xử|đòi tiền tip|vòi vĩnh|chèn ép|phục vụ chậm|lờ đi|quay lưng)\b",
            r"\b(thất vọng|không hài lòng|bực mình|ức chế|tức).{0,10}(với|về)?.{0,10}(nhân viên|phục vụ)?\b",
            r"\b(nhân viên|phục vụ|dịch vụ).{0,10}?(quá|rất|cực)?.{0,5}?(tệ|dở|kém|đáng chê|không ổn)\b",
            r"(thiếu|không)\s*(tươi cười|tích cực|hướng dẫn|thèm nhìn|chuyên nghiệp|chú ý|ổn|thân thiện|nhiệt tình|hợp tác|chăm sóc|quan tâm|hiểu biết|hỗ trợ|giúp đỡ|am hiểu|chỉ đường)",
            r"\b(bad service|rude|unfriendly|slow service|ignored|poor attitude|incompetent|unprofessional)\b"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn SERVICE#CHECKIN
def extract_service_checkin(text):
    checkin_keywords = [
        "checkin", "check-in", "nhận phòng", 
        "thủ tục nhận phòng", "làm thủ tục", 
        "quá trình checkin", "quy trình nhận phòng", 
        "đợi nhận phòng", "chờ checkin", "thời gian checkin", "giao phòng", "được nhận phòng"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in checkin_keywords)
    if existAspect:
        positive_patterns = [
            r"(checkin|check-in|nhận phòng|giao phòng|thủ tục).{0,10}?(nhanh|dễ dàng|thuận tiện|trơn tru|đúng giờ|không phải đợi)",
            r"(nhanh|dễ|thuận tiện|dễ dàng|mau).{0,10}?(checkin|check-in|nhận phòng|làm thủ tục|giao phòng)",
            r"(được nhận phòng sớm|checkin sớm|trả phòng muộn miễn phí|nhận phòng đúng giờ)",
        ]
        negative_patterns = [
            r"(checkin|check-in|nhận phòng|làm thủ tục|giao phòng).{0,10}?(lâu|chậm|mất thời gian|rườm rà|khó khăn|không rõ ràng|phức tạp|bất tiện|trì hoãn|trễ)",
            r"(phải|bị)?\s?(đợi|chờ|delay|lùi giờ|hủy).{0,10}?(nhận phòng|checkin|check-in|phòng)",
            r"giao phòng.{0,5}?(muộn|trễ|không đúng giờ)"
        ]
        
        compiled_neg = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in negative_patterns]
        compiled_pos = [re.compile(normalize_unicode(pat), re.IGNORECASE) for pat in positive_patterns]
        
        for neg in compiled_neg:
            if neg.search(text):
                return "NEGATIVE"
        for pos in compiled_pos:
            if pos.search(text):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None


aspect_detection_functions = {
    "HOTEL#LOCATION": extract_hotel_location,
    "HOTEL#FACILITIES": extract_hotel_facilities,
    "HOTEL#QUALITY": extract_hotel_quality,
    "HOTEL#STYLE": extract_hotel_style,
    "WIFI": extract_wifi,
    "PRICE": extract_price,
    "ROOM#QUALITY": extract_room_quality,
    "ROOM#STYLE": extract_room_style,
    "ROOM#FACILITIES": extract_room_facilities,
    "ROOM#SOUND": extract_room_sound,
    "ROOM#VIEW": extract_room_view,
    "ROOM#ATMOSPHERE": extract_room_atmosphere,
    "ROOM#CLEANLINESS": extract_room_cleanliness,
    "SERVICE#STAFF": extract_service_staff,
    "SERVICE#CHECKIN": extract_service_checkin,
}

def append_aspects(df, processor):
    listAspects = []
    priority = {"NEGATIVE": 3, "POSITIVE": 2, "NEUTRAL": 1}
    df['text'] = df['text'].apply(lambda x: processor.process_text(x))
    df = df[df['text'].notna() & (df['text'] != "")]
    df.reset_index(drop=True, inplace=True)
    
    for idx, row in tqdm(df.iterrows(), desc='Annotating Sample'):
        review_text = str(row['text']).lower()
        sentences = re.split(r'[.!?•\n]', review_text)
        detected_aspects = {}

        for sentence in sentences:
            if not sentence:
                continue
            
            for aspect, extract_function in aspect_detection_functions.items():
                extracted_aspect = extract_function(sentence)
                if extracted_aspect is not None:
                    if aspect not in detected_aspects:
                        detected_aspects[aspect] = extracted_aspect
                    else:
                        # Ưu tiên NEGATIVE > POSITIVE > NEUTRAL
                        if priority[extracted_aspect] > priority[detected_aspects[aspect]]:
                            detected_aspects[aspect] = extracted_aspect  
        
        listAspects.append(detected_aspects)

    if len(listAspects) != len(df):
        raise ValueError('Bug in length of dataframe')
    df.loc[:, "aspects"] = listAspects
    return df

if __name__ == '__main__':
    listAspects = []
    processor = VietnameseTextProcessor()
    df = pd.read_csv("./DatasetGGMaps/final_review_googlemap_comments_hotel.csv", index_col=0)
    df1 = pd.read_csv("./DatasetGGMaps/final_review_traveloka_comments_hotel.csv", index_col=0)
    
    df = append_aspects(df, processor)
    df1 = append_aspects(df1, processor)
    
    df_new = pd.concat([df, df1], ignore_index=True)
    df_new.to_csv('./annotated_labels/list_aspects_hotels.csv')