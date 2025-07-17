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
    direct_keywords = [
        r"\b(giá cả|giá thuê|chi phí|tốn|cắt cổ|cọc xe|treo đầu dê bán thịt chó)\b",
        r"\b(thuê xe|cho thuê xe|mướn xe|đặt xe)\b",
        r"\bgiá.{0,10}(theo giờ|theo ngày|theo tuần|theo tháng)\b"
        r"\btiền.{0,5}(cọc|đặt cọc|thế chân)\b",
        r"\bphí.{0,5}(giao xe|nhận xe|trả xe|trễ giờ|muộn giờ|bảo hiểm|phạt)\b",
        r"\b(hơi |khá |rất |quá |cực )?(cao|đắt|mắc|rẻ|hạt dẻ|bèo|mềm)\b",
        r"\b[0-9]+\.?[0-9]*\s*(k|ngàn|nghìn|đồng|vnđ|d|đ|triệu|tr)\b",
        r"\b(gói|ưu đãi|khuyến mãi|giảm giá)\b",
        r"\b(hợp lý|vừa túi tiền|hợp túi tiền|ưu đãi|chặt chém|phải chăng|bình dân|chát giá|trên trời)\b",
        r"\b(xứng |đáng |xứng đáng )(đồng tiền|giá|giá tiền|số tiền|tiền bỏ ra)\b",
        r"\bgiá.{0,10}?(hời|bèo|đắt|mềm|chát|hợp lý|ổn|sinh viên|văn phòng|hợp túi tiền|vừa túi tiền|premium|cao cấp|bình thường|sốc)\b", 
        r"\bđắt (xắt ra miếng|đỏ)\b",
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in direct_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(giá|phí|thuê).{0,10}(rẻ|bèo|hạt dẻ|mềm|hợp lý|ổn|phải chăng|tốt|tiết kiệm|bình dân|tiết kiệm|acceptable|reasonable|affordable)\b",
            r"\bgiá thuê.{0,10}(bình dân|sinh viên|học sinh|tốt)\b",
            r"\b(ưu đãi|giảm giá|khuyến mãi|combo|gói).{0,10}?(tốt|đáng giá|hời|worth it|tiết kiệm)\b",
            r"\b(giảm giá|discount).{0,10}?(nhiều|đáng kể|hấp dẫn)\b",
            r"\b(rẻ hơn|tốt hơn|hợp lý hơn).{0,10}?(chỗ khác|đối thủ|dự kiến|mong đợi)\b",
            r"\bgiá cả không thể tốt hơn\b",
            r"\b(cọc).{0,10}?(thấp|nhẹ nhàng|hợp lý|dễ chịu|không đáng kể)\b",
            r"\bhoàn cọc.{0,5}?(đầy đủ|nhanh chóng|dễ dàng)\b",
            r"\bkhông.{0,5}?(phát sinh|mất).{0,5}?phí\b",
            r"\bphù hợp.{0,5}?(với|cho).{0,5}?túi tiền.{0,5}?(sinh viên|du khách|khách)\b"
        ]
        negative_patterns = [
            r"\b(giá|phí|thuê).{0,10}?(cao|đắt|mắc|cắt cổ|chát|sốc|khủng|trên trời|vô lý|ảo|expensive|overprice)\b",
            r"\bgiá thuê.{0,10}?(đắt đỏ|cắt cổ|quá đáng|quá tay)\b",
            r"\b(không hợp lý|không đáng|không xứng|không tương xứng|bị chặt chém|bị hố|bị chém)\b",
            r"\b(quá đắt|quá mắc).{0,10}?(so với|đối với|với)\b",
            r"\b(phí|tiền).{0,10}?(ẩn|phát sinh|vô lý|bất hợp lý|cao|đắt|cắt cổ)\b",
            r"\bcọc.{0,10}?(cao|đắt|nặng|khủng|mất|cướp|giữ lại|không trả|trả không đủ|hoàn không đủ)\b",
            r"\b(phí trả muộn|phí trễ giờ).{0,10}?(cao|vô lý|cắt cổ)\b",
            r"\b(đắt hơn|cao hơn|mắc hơn).{0,10}?(nơi khác|chỗ khác|giá thị trường|đối thủ)\b",
            r"\b(giá chênh lệch|chênh giá).{0,10}?(nhiều|lớn)\b",
            r"\b(lừa đảo|lừa gạt|bịp|scam|hét giá|ép giá|nâng giá)\b",
            r"\bthuê xe.{0,10}?(đắt hơn|cao hơn).{0,10}?(nơi khác)\b"
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
        r"\b(nhân viên|staff|nv|chủ quán|chủ xe|người cho thuê|anh chủ|chị chủ|cô chú)\b",
        r"\b(cô chú|ông bà|anh|chị|bác|cô|chú|ông|bà).{0,10}?(phụ trách|hướng dẫn|quản lý|chủ).{0,10}?xe\b"
        r"\bngười.{0,5}(giao xe|nhận xe|đón xe|trả xe|hỗ trợ|hướng dẫn|tư vấn)\b",
        r"\b(anh|chị|bác|cô|chú|em).{0,5}(bán hàng|phụ trách|cho thuê|tư vấn)\b",
        r"\b(hòa đồng|thái độ|phục vụ|nhiệt tình|niềm nở|thân thiện|vui vẻ|chậm trễ|trễ giờ|quên|thất hứa|lừa đảo|dịch vụ)\b"
    ]

    existAspect = any(re.search(normalize_unicode(entity), text, re.IGNORECASE) for entity in staff_entities)
    if existAspect:
        positive_patterns = [
            r"(?<!\bchưa\s)\b(nhanh nhẹn|tận tình|hòa đồng|dễ mến|hết lòng|rất ok|tốt bụng|tuyệt vời|tốt|chuyên nghiệp|xuất sắc|đáng khen|hoàn hảo|vui tính|nhiệt tình|dễ thương|vui vẻ|hiếu khách|lịch sự|thân thiện|niềm nở|nhẹ nhàng|tận tâm|chu đáo|quan tâm|tử tế|dễ tính)\b",
            r"\b(bằng mọi cách|bằng mọi giá)\b"
            r"\bcọc.{0,10}(nhanh|đầy đủ|ngay lập tức|không khó khăn)\b",
            r"\b(hỗ trợ.{0,10}(24/7|kịp thời|tận tình))|(giúp đỡ.{0,10}(nhiệt tình|khi gặp sự cố))\b",
            r"\b(thay xe.{0,10}(ngay lập tức|miễn phí))|(sửa xe.{0,10}(nhanh|tại chỗ))\b",
            r"\b(hỗ trợ|giúp đỡ|tư vấn|hướng dẫn|chỉ đường|chăm sóc|quan tâm).{0,10}?(kỹ|tốt|tận tình|rất tốt|chu đáo|từng bước)\b",
            r"\b(ấn tượng|hài lòng|thích).{0,10}?(với|về).{0,10}?(chủ|nhân viên)\b",
            r"\b(sẽ quay lại|giới thiệu bạn bè|recommend).{0,10}?(vì|do).{0,10}?(chủ|nhân viên)\b",
        ]
        negative_patterns = [
            r"\b(cục súc|vô duyên|tiêu cực|không tốt|kém|đáng chê|tồi|chậm chạp|thái độ|thô lỗ|tệ|khó chịu|cộc cằn|gắt gỏng|thờ ơ|bỏ mặc|phớt lờ|lạnh nhạt|khó tính|hỗn|vô lễ|bất lịch sự|khinh thường|mất dạy|láo|thờ ơ|không trả lời|lơ|phớt lờ|không quan tâm|quát|mắng|chửi|đe dọa)\b",
            r"\bcọc.{0,10}(chậm|thiếu|không đủ|giữ lại|tìm cớ giữ|không trả|mất|bị cướp)\b",
            r"\b(đòi.{0,5}(tiền tip|phụ phí vô lý))|vòi vĩnh|chèn ép|hét giá|ép giá\b",
            r"\b(kiểm tra xe|soát xe).{0,10}(kỹ quá|bắt bẻ|khắt khe|vạch lá tìm sâu)b",
            r"(thiếu|không)\s*(hướng dẫn|thèm nhìn|chuyên nghiệp|chú ý|ổn|thân thiện|nhiệt tình|hợp tác|chăm sóc|quan tâm|hiểu biết|hỗ trợ|giúp đỡ|am hiểu|chỉ đường)",
            r"\b(thất vọng|không hài lòng|bực mình|ức chế).{0,10}?(với|về).{0,10}?(dịch vụ|nhân viên)",
            r"\b(tránh xa|không nên|đừng).{0,10}?(thuê|đến|sử dụng).{0,10}?(vì|do).{0,10}?(chủ|nhân viên)",
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


# Gán nhãn SERVICE#RENTING
def extract_service_renting(text):
    renting_keywords = [
        r"\b(quy trình|thủ tục|đặt xe|book xe|thuê xe   )\b",
        r"\b(giấy tờ|chứng minh nhân dân|căn cước công dân|hộ chiếu|passport|bằng lái|giấy phép lái xe)\b",
        r"\b(hợp đồng|contract|ký kết|văn bản|điều khoản)\b",
        r"\b(giao xe|nhận xe|đưa xe|trả xe|hoàn xe|trao xe|nhận lại xe)\b",
        r"\b(kiểm tra xe|soát xe|bàn giao|nghiệm thu|đánh giá tình trạng)\b",
        r"\b(đặt cọc|thế chân|deposit|tiền cọc|hoàn cọc|trả cọc)\b",
        r"\b(thanh toán|payment|tiền|phí|giá|chuyển khoản|tiền mặt)\b",
        r"\b(nhanh|chậm|đúng giờ|trễ|đơn giản|phức tạp|dễ dàng|khó khăn|rườm rà|nhanh gọn)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in renting_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(nhanh|đơn giản|dễ dàng|nhanh chóng|tiện lợi|không rườm rà|minimal paperwork)\b",
            r"\b(thủ tục|quy trình|quá trình)?.{0,10}?(đơn giản|nhanh|gọn lẹ|dễ|chỉ mất \d+ phút)\b",
            r"\b(đặt online|book app|website).{0,10}?(dễ dàng|tiện lợi|nhanh chóng|trực quan)\b",
            r"\bgiấy tờ.{0,10}?(đơn giản|chỉ cần chứng minh nhân dân|không cần bằng lái|không yêu cầu nhiều)\b",
            r"\b(chỉ cần chụp chứng minh nhân dân|photo chứng minh nhân dân|không cần bản gốc)\b",
            r"\b(nhận xe|giao xe|lấy xe)?.{0,10}?(thuận tiện|linh hoạt|dễ dàng|đúng giờ|tận nơi|nhanh|đúng giờ|sớm hơn|chỉ trong \d+ phút)\b",
            r"\b(trả xe|hoàn xe)?.{0,10}?(nhanh chóng|đơn giản|không mất thời gian)\b",
            r"\b(kiểm tra xe|soát xe)?.{0,10}?(nhanh|đơn giản|không bắt bẻ|công bằng)\b",
            r"\b(bàn giao)?.{0,10}?(chuyên nghiệp|rõ ràng|minh bạch|có biên bản)\b",
            r"\b(thanh toán)?.{0,10}?(linh hoạt|đa dạng|online|chuyển khoản|tiện)\b",
            r"\b(cọc|đặt cọc).{0,10}?(thấp|nhẹ|hợp lý|dễ chịu|chỉ \d+)\b",
            r"\b(hoàn cọc)?.{0,10}?(ngay|nhanh|đầy đủ|dễ dàng)\b",
            r"\b(quy trình)?.{0,10}?(chuyên nghiệp|hoàn hảo|tốt|đáng khen)\b",
            r"\btrải nghiệm.{0,10}?(mượt mà|suôn sẻ|tuyệt vời|không trục trặc)\b"
        ]
        negative_patterns = [
            r"\b(phức tạp|rườm rà|chậm chạp|mất thời gian|nhiều bước|bất tiện|complicated)\b",
            r"\b(thủ tục|quy trình|quá trình).{0,10}?(lằng nhằng|phiền phức|quá nhiều giấy tờ|cầu kỳ)\b",
            r"\b(đặt online|book app|website).{0,10}?(khó|lỗi|không hoạt động|khó hiểu)\b",
            r"\b(phải gọi nhiều lần|không ai nghe máy|trả lời chậm)\b",
            r"\bgiấy tờ.{0,10}?(phức tạp|quá nhiều|yêu cầu bằng lái|bản gốc)\b",
            r"\b(giao xe|nhận xe|trả xe|hoàn xe)?.{0,10}?(chậm|mất thời gian|bị giữ lại|làm khó|trễ|muộn|chậm|không đúng giờ|quá \d+ tiếng|khó khăn|phiền phức|phức tạp|bị làm khó)\b",
            r"\b(kiểm tra xe|soát xe)?.{0,10}?(kỹ quá|bắt bẻ|vạch lá tìm sâu|khắt khe)\b",
            r"\b(kiểm tra)?.{0,10}?(lâu|mất thời gian|quá chi tiết)\b",
            r"\b(hợp đồng)?.{0,10}?(dài|phức tạp|điều khoản bất lợi|ẩn điều khoản)\b",
            r"\b(thanh toán)?.{0,10}?(khó khăn|chỉ tiền mặt|không chuyển khoản|thêm phí)\b",
            r"\b(cọc)?.{0,10}?(cao|đắt|nặng|không hợp lý|quá \d+)\b",
            r"\b(hoàn cọc)?.{0,10}?(chậm|thiếu|không trả|giữ lại|khó khăn|tìm cớ giữ)\b",
            r"\b(quy trình)?.{0,10}?(kém|tệ|thiếu chuyên nghiệp|cần cải thiện)\b",
            r"\b(trải nghiệm)?.{0,10}?(tồi tệ|ức chế|khó chịu|đáng thất vọng)\b"
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


# Gán nhãn VEHICLE#QUALITY
def extract_vehicle_quality(text):
    vehicle_keywords = [
        r"\bxe\s*(máy|số|tay ga|côn|phổ thông|đời mới|hơi|\d chỗ)?\b",
        r"\b(tình trạng|chất lượng|độ bền|độ mới|năm sản xuất|đời xe|model)\b",
        r"\b(motor|động cơ|máy móc|bộ phận|linh kiện|phụ tùng)\b",
        r"\b(bảo dưỡng|bảo trì|kiểm định|an toàn|độ tin cậy)\b",
        r"\b(thắng|phanh|lốp|vỏ|bánh|đèn|xi nhan|còi|yên|ghế|tay lái|xăng)\b",
        r"\b(chạy|vận hành|khởi động|tăng tốc|leo dốc|đổ đèo|tiêu hao nhiên liệu)\b",
        r"\b(ồn|rung|giật|khói|mùi|dầu nhớt|bảo hành)\b",
        r"\b(mới|cũ|like new)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in vehicle_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(mới|như mới|like new|99%|đời mới|model mới)\b",
            r"\b(êm ru|chất lượng tốt|cao cấp|bền bỉ|ổn định|độ tin cậy cao|xịn xò|khỏe|đẹp|tốt|mượt|bốc|êm|khỏe|bền|hoạt động tốt|ngon)\b",
            r"\bkhởi động.{0,10}?(ngon|dễ|một lần|nhanh)\b",
            r"\b(tiết kiệm nhiên liệu|ít hao xăng|ăn ít xăng|bình xăng đầy|đầy xăng)\b",
            r"\b(thắng|phanh).{0,10}?(nhạy|gắt|tốt|an toàn)\b",
            r"\b(lốp|vỏ).{0,10}?(mới|tốt|đủ gai|không mòn)\b",
            r"\b(đèn|còi|xi nhan).{0,10}?(sáng|rõ|to|hoạt động tốt)\b",
            r"\b(yên|ghế).{0,10}?(êm|rộng|thoải mái)\b",
            r"\b(bảo dưỡng|bảo trì).{0,10}?(tốt|đầy đủ|định kỳ)\b",
            r"\bxe.{0,10}?(sạch sẽ|thơm tho|không mùi|không ồn|không rung)\b",
            r"\b(xe đẹp|xế xịn|xe ngon|xe chất)\b",
            r"\b(hài lòng|ưng ý|thích|tốt).{0,10}?(với|về).{0,10}?(chất lượng xe|xe)\b",
            r"\b(đáng đồng tiền|xứng đáng|không thất vọng)\b"
        ]
        negative_patterns = [
            r"\b(cũ|đời cũ|hao mòn|second hand|đã sử dụng lâu năm)\b",
            r"\bxe.{0,10}?(cùi|kém chất lượng|dỏm|giả|nhái|fake|hết xăng|không còn xăng|bẩn|hôi mùi|ồn ào|rung lắc)\b",
            r"\b(chất lượng kém|tồi|dở|không đảm bảo|đáng lo ngại)\b",
            r"\b(máy móc|động cơ).{0,10}?(yếu|ì|ồn|rung|giật|khói|đen|hư hỏng|trục trặc)\b",
            r"\b(chạy|vận hành).{0,10}?(ì ạch|yếu|không nổi|khó khăn|không ổn định)\b",
            r"\bkhởi động.{0,10}?(khó|không nổ|phải đạp nhiều lần|chết máy)\b",
            r"\b(tiêu hao nhiên liệu|hao xăng|ăn xăng|ngốn xăng|bình xăng rỗng)\b",
            r"\b(trục trặc|hư hỏng|chết máy|đứng máy).{0,10}?(giữa đường|khi đang chạy)\b",
            r"\b(thắng|phanh).{0,10}?(mòn|trơ|không ăn|mất phanh|kém)\b",
            r"\b(lốp|vỏ).{0,10}?(mòn|trơ|non hơi|rách|bị vá|hết gai)\b",
            r"\b(đèn|còi|xi nhan).{0,10}?(mờ|tối|hư|không sáng|không hoạt động)\b",
            r"\b(yên|ghế).{0,10}?(cứng|gãy|hư|đau lưng|khó chịu)\b",
            r"\btay lái.{0,10}?(lệch|nặng|rơ|khó điều khiển)\b",
            r"\b(không bảo dưỡng|bảo trì kém|dầu nhớt cũ|không thay nhớt)\b",
            r"\b(mất an toàn|nguy hiểm|rủi ro|đáng sợ)\b",
            r"\b(sự cố|tai nạn|nguy cơ).{0,10}?(do|vì).{0,10}?(xe|chất lượng)\b",
            r"\b(thất vọng|không hài lòng|nguy hiểm).{0,10}?(với|về).{0,10}?(chất lượng xe|xe)\b",
            r"\b(khuyên không nên|đừng|tránh xa).{0,10}?(vì|do).{0,10}?(xe kém chất lượng)\b"
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
    "SERVICE#STAFF": extract_service_staff,
    "SERVICE#RENTING": extract_service_renting,
    "VEHICLE#QUALITY": extract_vehicle_quality
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
    df = pd.read_csv("./DatasetGGMaps/final_review_googlemap_comments_rent.csv", index_col=0)
    df = append_aspects(df, processor)
    df.to_csv('./annotated_labels/list_aspects_rents.csv')