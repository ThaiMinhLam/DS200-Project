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

# Gán nhãn LOCATION
def extract_location(text):
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


# Gán nhãn PRICE
def extract_price(text):
    price_keywords = [
        r"\b(giá|phí)\s*?(vé|vào cổng|tour|gói|tiền)\b",
        r"\b(chi phí|tốn|cắt cổ|treo đầu dê bán thịt chó|bỏ ra|số tiền|tiền vé|phí tham gia|phí tham quan)",
        r"\b(giảm giá|ưu đãi|khuyến mãi|discount)\b",
        r"\b[0-9]+\.?[0-9]*\s*(k|ngàn|nghìn|đồng|vnđ|d|đ|triệu|tr)\b",
        r"\b(hơi |khá |rất |quá |cực )?(cao|đắt|mắc|rẻ|hạt dẻ|bèo|mềm|hời|chát|hợp lý)\b",
        r"\b(hợp lý|vừa túi tiền|hợp túi tiền|ưu đãi|chặt chém|phải chăng|bình dân|chát giá|trên trời)\b", 
        r"\b(xứng |đáng |xứng đáng )(đồng tiền|giá|giá tiền|số tiền|tiền bỏ ra)\b",
        r"\bgiá.{0,10}?(hời|bèo|đắt|mềm|chát|hợp lý|ổn|sinh viên|văn phòng|hợp túi tiền|vừa túi tiền|premium|cao cấp|bình thường|sốc)\b", 
        r"\bđắt (xắt ra miếng|đỏ)\b",
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in price_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(giá|vé|phí).{0,10}?(tốt|rẻ|hạt dẻ|bình dân|hợp lý|ổn áp|tiết kiệm|hời|bèo|sinh viên|phải chăng|tốt|mềm|acceptable|reasonable|affordable)\b",
            r"\b(đáng đồng tiền|đáng giá|rất đáng|giảm giá|ưu đãi)\b",
            r"\b(happy hour|khuyến mãi|giảm giá|promotion).{0,10}?(đáng giá|tốt|hời|worth it)\b",
            r"\b(rẻ hơn|tốt hơn|hợp lý hơn).{0,10}?(mong đợi|dự kiến|so với|đa số|chỗ khác)\b",
            r"\b(giá cả không thể tốt hơn|perfect price|great value for money)\b"
        ]
        negative_patterns = [
            r"\b(giá|phí|vé).{0,10}(khủng khiếp|cao|đắt|mắc|cắt cổ|không hợp lý|không đáng|không xứng|chát|sốc|expensive|overprice|trên trời|vô lý|ảo)\b",
            r"\b(tốn tiền|không đáng tiền|không xứng với giá|too expensive|not worth it|bị chặt chém|bị hố)\b",
            r"\b(đắt hơn|cao hơn|mắc hơn).{0,10}(đáng|mong đợi|dự kiến|so với|đa số|chỗ khác)\b",
            r"\b(mất tiền).{0,5}(mà không).{0,5}(xứng đáng)\b"
            r"\b(happy hour|khuyến mãi|giảm giá).{0,10}?(vẫn đắt|không đáng|not worth)\b"
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
        r"\b(nhân viên|staff|hướng dẫn( viên)?|tour guide|guide|chăm sóc khách hàng|người phụ trách|chủ vườn)\b",
        r"\b(cô chú|ông bà|anh|chị|bác|cô|chú|ông|bà).{0,10}(phụ trách|hướng dẫn|quản lý|chủ)?\b"
    ]
    staff_activities = [
        r"\b(hòa đồng|thái độ|nhiệt tình|thuyết minh|giới thiệu|dịch vụ|chu đáo|hiếu khách|lịch sự)\b",
        r"\b(thân thiện|niềm nở|nhẹ nhàng|hết lòng|tận tâm|tận tình|chu đáo|quan tâm|tử tế)\b"
        r"\b(chăm sóc|hỗ trợ|phục vụ|hướng dẫn|tư vấn|giải đáp|đón tiếp|tiếp đón|quan tâm|giúp đỡ)\b",
        r"\bxử lý\s*(tình huống|vấn đề)\b",
        r"\bkiểm tra (vé|giấy tờ)\b",
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
            r"\b(thất vọng|không hài lòng|bực mình|ức chế|tức).{0,10}?(với|về)?.{0,10}?(nhân viên|phục vụ)\b",
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


# Gán nhãn ENVIRONMENT#SCENERY
def extract_environment_scenery(text):
    scenery_keywords = [
        r"\b(cảnh|phong cảnh|view|quang cảnh|khung cảnh|scenery|landscape|panorama)\b",
        r"\b(núi non|sông nước|biển cả|bờ biển|đồi núi|thác nước|rừng cây|hoàng hôn|bình minh|bầu trời)\b",
        r"\b(vẻ đẹp|đẹp mắt|đẹp tự nhiên|thiên nhiên|khung cảnh thiên nhiên|vùng quê|nông thôn|đồng quê)\b",
        r"\b(trời nước|mây trời|núi đồi|hang động|đảo|vịnh|(?<!chủ\s)vườn|hoa cỏ|cây xanh|thảm thực vật)\b",
        r"\b(tầm nhìn|góc nhìn|background)\b",
        r"\b(panoramic|vista|seascape|mountainside|riverside|lakeside|coastal)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in scenery_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(đẹp|tuyệt đẹp|tuyệt vời||đỉnh cao|hoàn hảo|tuyệt hảo|đẹp mê hồn|ngoạn mục|hùng vĩ|nên thơ|thơ mộng|lãng mạn|tráng lệ|choáng ngợp|ấn tượng)\b",
            r"\b(cảnh|phong cảnh|khung cảnh).{0,10}?(đẹp|mãn nhãn|say đắm|quyến rũ|nên thơ|hữu tình)\b",
            r"\b(đẹp nhất|đỉnh nhất|đẹp vô đối|đẹp không tưởng|đẹp ngỡ ngàng|đẹp mê ly)\b",
            r"\b(xứng đáng|đáng giá|đáng đồng tiền).{0,10}?(với|vì).{0,10}?(cảnh|view)\b",
            r"\b(thích|mê|say|ấn tượng|ngẩn ngơ|ngây ngất).{0,10}?(với|vì|bởi).{0,10}?(cảnh|view|phong cảnh|khung cảnh)\b",
            r"\b(quên lối về|quên thời gian|đắm chìm|mãn nhãn|thư giãn|bình yên|tận hưởng)\b",
            r"\b(trong lành|tươi mát|mát mẻ|thanh bình|yên tĩnh|thoáng đãng|rộng lớn|bát ngát|mênh mông)\b",
            r"\b(thiên nhiên hoang sơ|nguyên sơ|tự nhiên|chưa bị tác động|bảo tồn tốt)\b",
            r"\b(sống ảo|cắm trại|dã ngoại|picnic|ngắm cảnh|thưởng ngoạn|ngồi ngắm).{0,10}?(tuyệt|đã|thích)\b"
        ]
        negative_patterns = [
            r"\b(xấu|tẻ nhạt|nhàm chán|đơn điệu|nghèo nàn|thất vọng|tầm thường|không đẹp|không ấn tượng)\b",
            r"\b(view|tầm nhìn|góc nhìn).{0,10}?(xấu|kém|tệ|hạn chế|bị che khuất|không rõ|không đẹp)\b",
            r"\b(ô nhiễm|bụi bặm|rác thải|khói bụi|mùi hôi|tanh|hôi thối|nước đục|bẩn)\b",
            r"\b(hoang tàn|đổ nát|xói mòn|sạt lở|khô cằn|trơ trọi|trọc|thiếu cây xanh)\b",
            r"\b(xây dựng lộn xộn|công trình xấu|kiến trúc lạc lõng|dây điện chằng chịt|quảng cáo loè loẹt)\b",
            r"\b(đông đúc|chật chội|ồn ào|bị che khuất|khuất tầm nhìn|mất tự nhiên|bê tông hoá)\b",
            r"\b(không như hình|khác xa quảng cáo|thua kém|không bằng|đáng thất vọng)\b",
            r"\b(chán|thất vọng|ức chế|bực mình|không thích|tiếc công).{0,10}?(vì|do|bởi).{0,10}?(cảnh|view)\b",
            r"\b(không đẹp|chẳng có gì|không đáng|không xứng|phí tiền).{0,10}?(vì|cho).{0,10}?(cảnh)\b"
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


# Gán nhãn ENVIRONMENT#ATMOSPHERE
def extract_environment_atmosphere(text):
    atmosphere_keywords = [
        r"\b(không khí|bầu không khí)\b",
        r"\b(không gian|khuôn viên)\b",
        r"\b(yên tĩnh|thanh bình|bình yên|yên bình|tĩnh lặng|im ắng|ồn ào|náo nhiệt|đông đúc|vắng vẻ)\b",
        r"\b(cảm giác|cảm nhận|năng lượng)\b",
        r"\b(ấm cúng|thoáng đãng|ngột ngạt|chật chội|rộng rãi|khép kín)\b",
        r"\b(nhộn nhịp|sôi động|tấp nập|huyền ảo|ma quái)\b",
        r"\b(ánh sáng|đèn đuốc|đèn lồng|đèn dầu|đèn điện|đèn màu|đèn neon|trang trí)\b",
        r"\b(âm nhạc|nhạc nền|tiếng động|âm thanh|im lặng)\b",
        r"\b(tĩnh mịch|huyền bí|hoài cổ|cổ kính|hiện đại)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in atmosphere_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(dễ chịu|thoải mái|thư thái|tuyệt vời|ấn tượng|tuyệt hảo|hoàn hảo|tuyệt trần|thoáng đãng)\b",
            r"\b(không khí.{0,10}(thoáng đãng|trong lành|dễ chịu|mát mẻ|ấm áp|ấm cúng|sôi động|vui vẻ|nhộn nhịp|tưng bừng|rộn ràng))\b",
            r"\b(cảm giác.{0,10}(thoải mái|dễ chịu|thư giãn|thích thú|hạnh phúc|phấn khích|tích cực))\b",
            r"\b(không gian.{0,10}(rộng rãi|thoáng đãng|sạch sẽ|gọn gàng|ngăn nắp|ấm cúng|đẹp|lãng mạn|độc đáo))\b",
            r"\b(âm nhạc.{0,10}(hay|du dương|nhẹ nhàng|phù hợp))\b",
            r"\b(ánh sáng.{0,10}(ấm áp|lãng mạn|đẹp|huyền ảo|lung linh))\b",
            r"\b(vibe|năng lượng).{0,10}(tích cực|tốt|tuyệt|mạnh|ổn)\b",
            r"\b(yên tĩnh|thanh bình|bình yên|tĩnh lặng|yên bình).{0,10}(dễ chịu|hoàn hảo)?\b",
            r"\b(nhộn nhịp|sôi động).{0,10}(vui vẻ|thú vị|hấp dẫn)\b",
            r"\b(ấm cúng|gần gũi|thân thiện)\b",
            r"\b(huyền ảo|ma mị|bí ẩn|cổ kính).{0,10}(thích|ấn tượng|đặc biệt)\b",
            r"\b(hoài cổ|nostalgic|retro).{0,10}(đẹp|ấn tượng)\b",
            r"\bquên.{0,5}(hết|đi).{0,10}(mệt mỏi|ưu phiền)\b",
            r"\b(thoát khỏi|xa rời).{0,5}(ồn ào|chốn thị thành)\b"
        ]
        negative_patterns = [
            r"\b(khó chịu|ngột ngạt|bức bối|tù túng|chán ngán|ức chế|buồn tẻ|nặng nề|đáng sợ|rùng rợn|ma quái)\b",
            r"\b(không khí.{0,10}(ngột ngạt|nóng nực|lạnh lẽo|ẩm ướt|hôi hám|hôi thối|khó thở|buồn tẻ|u ám|ảm đạm))\b",
            r"\b(cảm giác.{0,10}(khó chịu|bất an|sợ hãi|lo lắng|chán nản|mệt mỏi|ức chế|bồn chồn|bực bội))\b",
            r"\b(không gian.{0,10}(chật chội|hẹp|bừa bộn|bẩn thỉu|ngột ngạt|tối tăm|ảm đạm|cũ kỹ|đổ nát))\b",
            r"\b(âm nhạc.{0,10}(ồn ào|chói tai|khó chịu|to quá|nhức đầu|không phù hợp))\b",
            r"\b(ánh sáng.{0,10}(tối|mờ|chói|loá mắt|khó chịu|không đủ))\b",
            r"\b(vibe|năng lượng).{0,10}(tiêu cực|xấu|kỳ lạ|nặng nề|ảm đạm)\b",
            r"\b(ồn ào|náo nhiệt|đông đúc).{0,10}(quá mức|mệt mỏi|khó chịu|ức chế)\b",
            r"\b(yên tĩnh|vắng vẻ).{0,10}(quá|đáng sợ|rùng rợn|ma quái)\b",
            r"\b(quá|rất|siêu).{0,5}(ồn|đông|chật|nóng|lạnh)\b",
            r"\b(không có|thiếu).{0,5}(không khí vui vẻ|sự sống|năng lượng)\b",
            r"\b(cảm thấy|thấy).{0,5}(lạc lõng|không an toàn|bồn chồn)\b"
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


# Gán nhãn EXPERIENCE#ACTIVITY
def extract_experience_activity(text):
    experience_activities_keywords = [
        r"\b(hoạt động|trải nghiệm|tour|hành trình|tham quan|khám phá)\b",
        r"\b(trò chơi|game|đùa nghịch|giải trí|vui chơi|chơi)\b",
        r"\b(thử thách|challenge|mạo hiểm|adventure)\b",
        r"\b(workshop|dạy|dạy làm|tự tay làm)\b",
        r"\b(trải nghiệm văn hoá|văn nghệ|biểu diễn|show|ca nhạc|kịch|múa rối|ẩm thực|nếm thử|ăn thử)\b",
        r"\b(câu cá|đi xe đạp|leo núi|chèo thuyền|bơi lội|cắm trại|dã ngoại|picnic)\b",
        r"\b(thăm quan|ngắm cảnh|check-in|góc chụp|sống ảo|chụp.{0,15}hình|chụp.{0,15}ảnh|sống ảo|khám phá|tìm hiểu|lội suối|đi bộ đường dài)\b",
        r"\b(tương tác|hands-on|thực hành|tương tác với động vật|cho ăn động vật|cưỡi ngựa)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in experience_activities_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(bao vui|nhiều niềm vui|tuyệt vời|hấp dẫn|thú vị|đỉnh cao|đáng giá|đáng trải nghiệm|ấn tượng|khó quên|tuyệt hảo)\b",
            r"\b(hoạt động|trải nghiệm|trò chơi).{0,10}?(hay|hấp dẫn|thú vị|bổ ích|sáng tạo|độc đáo|chuyên nghiệp)\b",
            r"\b(thích|mê|say|phấn khích|hào hứng|thỏa mãn|hài lòng).{0,10}?(với|vì).{0,10}?(hoạt động|trải nghiệm)\b",
            r"\b(đáng đồng tiền|giá trị|không uổng công|không thất vọng|vượt mong đợi|không chán)\b",
            r"\b(đa dạng|phong phú|nhiều lựa chọn|phù hợp (cho|với) mọi lứa tuổi|cho cả gia đình)\b",
            r"\b(an toàn|lành mạnh|vui nhộn|sôi động|hấp dẫn|kích thích|tăng trải nghiệm)\b",
            r"\b(quên hết mệt mỏi|quên thời gian|muốn quay lại|sẽ quay lại|giới thiệu cho bạn bè)\b",
            r"\b(trải nghiệm.{0,10}(đáng nhớ|khó quên|mới lạ|độc nhất vô nhị))\b"
        ]
        negative_patterns = [
            r"\b(nhàm chán|tẻ nhạt|đơn điệu|kém chất lượng|thất vọng|không đáng giá|phí tiền|phí thời gian|lừa đảo)\b",
            r"\b(hoạt động|trải nghiệm|trò chơi).{0,10}?(ít|nghèo nàn|đơn giản|sơ sài|kém|dở|tệ|chán|không hấp dẫn)\b",
            r"\b((tổ chức.{0,10}(kém|lộn xộn|thiếu chuyên nghiệp))|(thời gian.{0,10}(quá ngắn|quá dài|không hợp lý)))\b",
            r"\b((phải chờ đợi.{0,10}(lâu|nhiều))|đông đúc|chật chội|chen lấn|(xếp hàng.{0,10}(dài|mệt)))\b",
            r"\b(cũ kỹ|hư hỏng|không an toàn|nguy hiểm|thiếu bảo trì|bẩn|không vệ sinh)\b",
            r"\b(giới thiệu quá mức|khác xa mô tả|không như quảng cáo|ảo|không đúng như hình)\b",
            r"\b((không phù hợp.{0,10}(với trẻ em|cho người già))|quá khó|quá dễ|nhàm chán)\b",
            r"\b(chán|thất vọng|ức chế|mệt mỏi|buồn ngủ|không thích).{0,10}?(vì|do|bởi).{0,10}?(hoạt động|trải nghiệm)\b",
            r"\b(mất công|mất tiền|uổng phí|không đáng|không nên thử|khuyên không nên)\b",
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
    "LOCATION": extract_location,
    "PRICE": extract_price,
    "ENVIRONMENT#SCENERY ": extract_environment_scenery,
    "ENVIRONMENT#ATMOSPHERE ": extract_environment_atmosphere,
    "SERVICE#STAFF": extract_service_staff,
    "EXPERIENCE#ACTIVITY": extract_experience_activity
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
    processor = VietnameseTextProcessor()
    df = pd.read_csv("./DatasetGGMaps/final_review_googlemap_comments_attraction.csv", index_col=0)
    df1 = pd.read_csv("./DatasetGGMaps/final_review_traveloka_comments_attraction.csv", index_col=0)
    
    df = append_aspects(df, processor)
    df1 = append_aspects(df1, processor)
    
    df_new = pd.concat([df, df1], ignore_index=True)
    df_new.to_csv('./annotated_labels/list_aspects_attractions.csv')