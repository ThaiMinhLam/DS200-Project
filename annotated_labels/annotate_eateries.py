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
        r"\b(giá|phí)\s*(ăn|món|đồ ăn|mì|bún|phở|nem|bánh|tráng miệng|chè|nước|trà|bia|ly|chai|menu|quán|dĩa|suất|combo|set|ốc)\b",
        r"\bchi phí\b", r"\bhóa đơn\b", r"\btính tiền\b", r"\bmức giá\b", r"\bgiá tiền\b", r"\bbill\b", r"\bprice\b",
        r"\b(tốn|cắt cổ|treo đầu dê bán thịt chó|bỏ ra|số tiền)\b",
        r"\b(giảm giá|ưu đãi|khuyến mãi|discount)\b",
        r"\b[0-9]+\.?[0-9]*\s*(k|ngàn|nghìn|đồng|vnđ|d|đ|triệu|tr)\b",
        r"\b(hơi |khá |rất |quá |cực )?(cao|đắt|mắc|rẻ|hạt dẻ|bèo|mềm|hời|chát|hợp lý)\b",
        r"\b(hợp lý|vừa túi tiền|hợp túi tiền|ưu đãi|chặt chém|phải chăng|bình dân|chát giá|trên trời)\b", 
        r"\b(xứng |đáng |xứng đáng )(đồng tiền|giá|giá tiền|số tiền|tiền bỏ ra)\b",
        r"\bgiá.{0,15}?(hời|bèo|đắt|mềm|chát|hợp lý|ổn|sinh viên|văn phòng|hợp túi tiền|vừa túi tiền|premium|cao cấp|bình thường|sốc)\b", 
        r"\bđắt\s*(xắt ra miếng|đỏ)\b",
        r"\b(mắc quá|rẻ quá|đắt ơi là đắt)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in price_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(giá|phí|suất|dĩa|hóa đơn|bill).{0,10}?(rẻ|bình dân|hợp lý|phải chăng|mềm|ổn|dân dã|bèo|hạt dẻ|hợp ví|hợp túi|sinh viên)\b",
            r"\b(xứng đáng|giá sinh viên|giá văn phòng|hạt dẻ|bèo|good value|worth it|đáng đồng tiền|rẻ mà ngon)\b",
            r"\b(giá|combo).{0,10}?(bình dân|dân dã|giá chợ|hạt dẻ|bèo|rẻ như cho|rẻ bất ngờ)\b",
            r"\b(suất ăn|phần ăn).{0,10}?(to|đầy đặn|nhiều).{0,5}\s*giá rẻ\b",
            r"\b(rẻ hơn|tốt hơn|hợp lý hơn).{0,10}?(mong đợi|dự kiến|so với|đa số|chỗ khác)\b",
            r"\b(đồ uống ngon mà giá cả hợp lý|chất lượng xứng giá|giá cả đi đôi với chất lượng)\b",
            r"\b(giá cả không thể tốt hơn|perfect price|great value for money)\b"
        ]
        negative_patterns = [
            r"\b(giá|phí|suất|dĩa|hóa đơn|bill).{0,10}?(cao|đắt|mắc|chát|sốc|đắt đỏ|cắt cổ|chặt chém|trên trời|khủng|hớ|không xứng|không đáng|trên trời)\b",
            r"\b(ăn vặt|đồ ăn|đồ uống).{0,10}?mà giá (cao|đắt|mắc|chát)\b",
            r"\b(không đáng tiền|không xứng|bị chém|bị hớ|mắc quá|đắt oặt)\b",
            r"\b(đắt hơn|cao hơn|mắc hơn).{0,10}?(mong đợi|dự kiến|so với|đa số|chỗ khác)\b",
            r"\b(suất ăn|phần ăn).{0,10}?(ít|nhỏ|thiếu).{0,5} giá cao\b",
            r"\b(đồ uống bình thường mà giá cao|chất lượng không xứng giá|giá cả quá đắt so với chất lượng|treo đầu dê bán thịt chó)\b",
            r"\b(giá|tính tiền).{0,10}?(theo kiểu|như) (khách du lịch|du lịch)\b"
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


# Gán nhãn FOOD#QUALITY
def extract_food_quality(text):
    food_quality_keywords = [
        r"\b(khó ăn|tuyệt vời|ấn tượng|đậm đà|chuẩn vị|thơm ngon|vừa miệng|hợp khẩu vị|tròn vị|tươi ngon|ngon miệng|gây nghiện|nhớ mãi hương vị)\b",
        r"\b(chất lượng|kém chất lượng|cao cấp|đồ đông lạnh|đồ cũ|món signature|best seller|authentic|đặc sản)\b",
        r"\b(đồ|món|thức) ăn\b", r"\bcơm\b", r"\blẩu\b", r"\bnướng\b", r"\bhải sản\b", 
        r"\bẩm thực\b", r"\bnêm nếm\b", r"\btẩm ướp (gia vị)?\b", r"\bgỏi\b", r"\bcanh\b", 
        r"\bphở\b", r"\bbún\b", r"\bthịt\b", r"\bmì\b", r"\bpizza\b", r"\bbeefsteak\b", 
        r"\bsalad\b", r"\bnguyên liệu\b", r"\bốc\b", r"\bburger\b", r"\bsúp\b", r"\brisotto\b",
        r"\bpasta\b", r"\bsteak\b", r"\bcurry\b", r"\bđặc sản\b", r"\bmón chính\b", r"\bmón khai vị\b",
        r"\btráng miệng\b", r"\bchế biến\b", r"\bnấu nướng\b", r"\bmón truyền thống\b", r"\bmón Âu\b",
        r"\bmón Á\b", r"\bgia vị\b", r"\bnước (sốt|chấm)\b", r"\bnước chấm\b", r"\bcháo\b", r"\bbánh (căn|xèo|ướt|cuốn|tráng)\b", r"\b(ngô|khoai lang)\b"
    ]

    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in food_quality_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(ngon|tuyệt vời|xuất sắc|ấn tượng|đậm đà|thơm ngon|vừa miệng|hợp khẩu vị|tròn vị|tươi ngon|ngon miệng|chuẩn vị|gây nghiện)\b",
            r"\b(chất lượng|tuyệt hảo|đỉnh cao|hoàn hảo|perfect|delicious|tasty|excellent|superb)\b",
            r"\b(giòn rụm|thơm nức|mềm ngon|tươi mới|nóng hổi|cân bằng|đậm đà hương vị|thấm gia vị|đúng điệu|chín tới)\b",
            r"\b(nguyên liệu tươi|hảo hạng|cao cấp|nhập khẩu|organic|hữu cơ|thượng hạng|prime|tươi sống)\b",
            r"\b(cách chế biến|kỹ thuật nấu|nấu nướng).{0,10}?(điêu luyện|chuyên nghiệp|tinh tế|khéo léo)\b",
            r"\b(ngon hơn|tốt hơn|chất lượng hơn).{0,10}?(mong đợi|dự kiến|so với|chỗ khác|nhà hàng khác)\b",
            r"\b(món).{0,10}?(đáng thử|recommend|gợi ý|nên order|best seller|đặc sản nhà hàng|signature dish)\b",
            r"\b(ăn là nghiền|nhớ mãi hương vị|muốn ăn lại|đúng gu|đậm chất truyền thống|authentic flavor)\b",
            r"\b(hương vị cân bằng hoàn hảo|kết hợp nguyên liệu tài tình|trình bày đẹp mắt)\b",
            r"\b(món ăn đạt chuẩn nhà hàng 5 sao|fine dining quality|đầu bếp tài năng)\b"
        ]
        negative_patterns = [
            r"\b(ngấy|dở|tệ|không ngon|nhạt|mặn|chua|đắng|khét|khó ăn|kinh khủng|thất vọng|tồi tệ|khó chịu)\b",
            r"\b(kém chất lượng|không tươi|đồ cũ|hết hạn|ôxy hóa|để lâu|tái sử dụng|hâm lại|không đáng tiền|phí tiền)\b",
            r"\b(khô cứng|nhão|dính răng|ngấy|quá ngọt|quá mặn|không tự nhiên|vị lạ|gia vị mất cân bằng|nêm nếm kém)\b",
            r"\b(nguyên liệu kém|đồ đông lạnh|không tươi|hết date|rẻ tiền|chất lượng thấp|hàng công nghiệp)\b",
            r"\b(chế biến sai cách|nấu quá tay|chín quá|sống quá|quá dai|quá cứng|quá mềm)\b",
            r"\b(món).{0,10}?(không đáng giá|phí tiền|không nên thử|avoid|thất vọng tràn trề)\b",
            r"\b(dở hơn|tệ hơn|kém hơn).{0,10}?(mong đợi|dự kiến|so với|chỗ khác|nhà hàng khác)\b",
            r"\b(đồ ăn).{0,10}?(tồi tệ nhất|dở nhất|đáng thất vọng nhất|tệ nhất từng ăn)\b",
            r"\b(tóc|móng tay|tàn thuốc|vật lạ|ruồi|gián|sạn|cát).{0,10}(trong món ăn|trong đồ ăn|trong thức ăn)\b",
            r"\b(món ăn không đảm bảo vệ sinh|ngửi thấy mùi lạ|có dấu hiệu ôi thiu)\b",
            r"\b(nấu ăn mà ngọt như chè|không hợp khẩu vị|ăn vào muốn trả lại|ăn vào phát sợ|không thể nuốt nổi|vứt đi|bỏ dở|gọi món khác thay thế|đổi món)\b",
            r"\b(đồ ăn như cám heo|chất lượng không xứng tầm nhà hàng|worst food experience ever)\b"
        ]
        
        for pat in negative_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "NEGATIVE"
        for pat in positive_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "POSITIVE"
        return "NEUTRAL"

    return None


# Gán nhãn FOOD#VARIETY
def extract_food_variety(text):
    context_keywords = [
        r"\b(menu|thực đơn|buffet|combo|line buffet|quầy line|topping|set menu).{0,10}(đơn điệu|lặp lại)?\b",
        r"\b(nhiều món|đa dạng|phong phú|ít món|lựa chọn)\b",
        r"\b(nhiều|đa dạng|đầy đủ|đủ thứ).{0,10}(lựa chọn|món)\b",
        r"\b(ít|thiếu).{0,10}(đổi món|món mới|lựa chọn|món)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in context_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(menu|thực đơn|quán)?.{0,10}?(nhiều lựa chọn|đầy đủ|phong phú|đa dạng|đủ cả|nhiều món)\b",
            r"\b(đa dạng|phong phú|đủ loại|đủ kiểu|đủ món|đủ thứ|rất nhiều|vô số|nhiều sự lựa chọn)\b",
            r"\bbuffet (nhiều món|đa dạng)\b",
            r"\b(set menu|combo).{0,10}(đa dạng|nhiều lựa chọn)\b",
            r"\b(quán chuyên).{0,10}?(nhiều loại|đa dạng kiểu|nhiều biến tấu|đủ cách chế biến)\b",
            r"\b(gì cũng có|đủ món trên đời|đủ các thể loại)\b",
            r"\b(tha hồ lựa chọn|chọn mãi không hết|mê mẩn vì nhiều món)\b",
        ]
        
        negative_patterns = [
            r"\b(hết không fill|giới hạn món|ít món|nghèo nàn|hạn chế|kém đa dạng|thiếu|không nhiều|không đủ|không đa dạng|hiếm|chỉ có vài|hạn hẹp|lèo tèo)\b",
            r"\b(menu|thực đơn|quán).{0,10}?(ít|ít ỏi|lặp lại|nghèo nàn|hạn chế|không đa dạng|thiếu lựa chọn)\b",
            r"\b(gì cũng không có|chỉ có|chỉ còn|chỉ toàn|quanh đi quẩn lại|vài ba món|độc nhất một món|chỉ có mỗi)\b",
            r"\b(thiếu muốn chết|chật vật chọn món|chọn mãi không ra|bó tay vì ít món)\b",
            r"\b(quán chuyên).{0,10}?(chỉ có vài món|ít lựa chọn|hạn chế)\b"
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


# Gán nhãn DRINK#QUALITY
def extract_drink_quality(text):
    drink_keywords = [
        r"\bnước ép\b", r"\b(nước|đồ|món) uống\b", r"\btrà\b", r"\bbia\b", r"\brượu\b", r"\bsinh tố\b",
        r"\bđồ uống\b", r"\bcocktail\b", r"\bmocktail\b", r"\bnước ngọt\b", r"\btrà sữa\b", r"\bcà phê\b", 
        r"\bmatcha\b", r"\bsoda\b", r"\blatte\b", r"\bespresso\b", r"\bsmoothie\b", r"\bmojito\b",
        r"\bmilkshake\b", r"\bjuice\b", r"\btea\b", r"\bcoffee\b", r"\bbeer\b", r"\bwine\b",
        r"\bchampagne\b", r"\bwhisky\b", r"\bvodka\b", r"\bliquor\b", r"\bbeverage\b", r"\bdrink\b",
        r"\bđá chanh\b", r"\btrà đá\b", r"\btrà đào\b", r"\bcốc\b", r"\bly\b", r"\bchai\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in drink_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(ngon|tuyệt vời|thơm ngon|vừa miệng|mát lạnh|ưng ý|sảng khoái|hoàn hảo|đậm đà|thượng hạng|hảo hạng|chất)\b",
            r"(đồ uống|nước uống|bia|trà|cà phê|rượu|cocktail).{0,15}?(ngon|thơm|chất lượng|đậm vị|tuyệt|hảo hạng|perfect|excellent)\b",
            r"\b(sảng khoái|dễ chịu|tỉnh táo|thư giãn|ấm bụng|mát lạnh).{0,10}?(khi uống|sau khi uống)\b",
            r"\b(ngon hơn|tốt hơn|chất lượng hơn).{0,10}?(mong đợi|dự kiến|so với)\b",
            r"\b(đáng giá|đáng tiền|nên thử|recommend|gọi thêm).{0,10}?(đồ uống|này)\b",
            r"\b(hương vị|mùi thơm|độ ngọt).{0,8}?(vừa phải|cân bằng|tuyệt vời)\b",
            r"\b(pha chế|phối trộn).{0,10}?(hoàn hảo|khéo léo|chuyên nghiệp)\b"
        ]
        negative_patterns = [
            r"\b(nhạt|lạt|nguội|đắng|chua|khó uống|dở|tanh|loãng|nhạt nhẽo|hôi|mùi lạ|kém|tệ|kinh khủng|thất vọng)\b",
            r"(đồ uống|nước uống|bia|trà|cà phê|rượu).{0,15}?(không ngon|tệ|khó uống|dở|nhạt|đắng|chua|hôi|loãng)\b",
            r"\b(quá ngọt|quá đắng|quá chua|quá nhạt|quá mạnh|quá yếu)\b",
            r"\b(vị).{0,5}?(lạ|khó chịu|không tự nhiên|hóa chất)\b",
            r"\b(mùi).{0,5}?(khó chịu|lạ|ôi|khét)\b",
            r"\b(không đáng giá|phí tiền|không nên thử|không recommend|không gọi lại).{0,5}?(đồ uống|này)\b",
            r"\b(để lâu|không tươi|ôxy hóa|hỏng|hết hạn|đổi vị)\b",
            r"\b(pha chế|phối trộn).{0,10}?(dở|tệ|không ổn|vụng về)\b",
            r"\b(tóc|móng tay|tàn thuốc|vật lạ).{0,10}(đồ uống|món( uống)?|thức uống|ly( nước)?)\b"
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


# Gán nhãn DRINK#VARIETY
def extract_drink_variety(text):
    context_keywords = [
        r"\b(menu nước|thực đơn nước|drink menu|beverage list|buffet nước|combo nước|set nước)\b", 
        r"\bđa dạng\b", r"\bphong phú\b", r"\blựa chọn\b", r"\bvariety\b", r"\bnghèo nàn\b",
        r"\b(ít|nhiều|đa dạng).{0,10}(loại|món|kiểu|dòng|hương vị|option)\b",
        r"\bphối trộn\b", r"\bpha chế\b", r"\bcombo\b", r"\bset\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in context_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(đa dạng|phong phú|nhiều loại|nhiều món|nhiều kiểu|nhiều dòng|nhiều hương vị|đầy đủ|đủ loại|rất nhiều)\b",
            r"\b(menu nước|thực đơn nước|drink menu|buffet nước|combo nước|set nước)?.{0,10}?(đa dạng|phong phú|nhiều lựa chọn|đầy đủ|complete|extensive|diverse|nhiều món)\b",
            r"\b(đủ các loại|từ A đến Z|tất cả các dòng|cập nhật mới nhất|đủ hãng|đủ vùng)\b",
            r"\b(đủ|đa dạng|nhiều).{0,10}(các loại|dòng )?(coffee|cà phê|trà|rượu|bia|cocktail)\b",
            r"\b(barista|bartender|quầy bar).{0,10}?(giới thiệu nhiều|nhiều option|đa dạng)\b",
            r"\b(đa dạng nhất|phong phú nhất|nhiều lựa chọn nhất|hơn hẳn|vượt trội|gì cũng có).{0,10}?(so với|mong đợi)?",
            r"(uống gì cũng có|đủ món để uống)"
        ]
        negative_patterns = [
            r"\b(hết không fill|ít loại|ít lựa chọn|ít|nghèo nàn|hạn chế|kém đa dạng|thiếu|không (có )?nhiều|không đủ|hiếm|chỉ có vài|hạn hẹp)\b",
            r"\b(menu nước|thực đơn nước|drink menu|buffet nước|combo nước|set nước).{0,15}?(ít|nghèo nàn|hạn chế|không đa dạng|thiếu lựa chọn|limited|poor)\b",
            r"\b(gì cũng không có|chỉ có|chỉ còn|chỉ toàn|quanh đi quẩn lại|mãi không đổi|không cập nhật|chỉ có vài món)\b",
            r"\b(không có|thiếu|missing).{0,10}?(đặc sản|craft beer|local brew|cocktail đặc biệt|signature drink)\b",
            r"\b(đơn điệu|nhàm chán|lặp lại|không đổi mới|không sáng tạo)\b",
            r"\b(ít hơn|nghèo nàn hơn|hạn chế hơn).{0,10}?(so với|mong đợi)",
            r"\b(variety).{0,10}?(poor|limited|lacking|disappointing)\b"
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


# Gán nhãn ENVIRONMENT#CLEANLINESS
def extract_environment_cleanliness(text):
    cleanliness_keywords = [
        r"\b(không gian|khuôn viên|chỗ ngồi)\b",
        r"\btinh tươm\b", r"\bbóng loáng\b", r"\bthơm tho\b",
        r"\bdơ\b", r"\bbẩn\b", r"\bẩm mốc\b", r"\bmùi hôi\b", r"\brác\b", r"\bkém vệ sinh\b", r"\bkhử mùi\b",
        r"\blấm lem\b", r"\bbụi bặm\b", r"\bcáu bẩn\b", r"\bhôi hám\b",
        r"\btràn\b", r"\bướt\b", r"\bẩm ướt\b", r"\bmất vệ sinh\b", r"\bthùng rác\b", r"\bđầy rác\b",
        r"\bđổ rác\b", r"\bbừa bộn\b", r"\blộn xộn\b", r"\bngổn ngang\b", r"\bđóng bụi\b", r"\bđầy bụi\b", r"\bđầy mạng nhện\b",
        r"\bvết ố\b", r"\bvết bẩn\b", r"\bvết dính\b", r"\bdầu mỡ\b", r"\bmảnh vụn\b", r"\bthức ăn rơi vãi\b", r"\bnước đổ\b",
        r"\bkhử trùng\b", r"\btẩy rửa\b", r"\blau chùi\b", r"\bdọn dẹp\b", r"\bquét dọn\b", r"\bvệ sinh kém\b",
        r"\b(sạch|sạch sẽ|ngăn nắp|gọn gàng|dọn vệ sinh|lau dọn|dọn dẹp|vệ sinh)\b",
        r"\b(bẩn|dơ|rất bẩn|khá bẩn|mùi lạ|hôi|mùi khó chịu)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in cleanliness_keywords)
    if existAspect:
        positive_patterns = [
            r"\b(sạch|sạch sẽ|sạch bóng|vệ sinh|gọn gàng|ngăn nắp|tinh tươm|bóng loáng|thơm tho|khử mùi tốt|sạch tinh tươm)\b",
            r"\b(quá sạch|rất sạch|siêu sạch|cực sạch|sạch hoàn hảo|sạch vượt trội|vệ sinh tuyệt đối)\b",
            r"(bàn|sàn|toilet|nhà vệ sinh|quầy|khu vực|phòng ăn|ghế|menu|dao kéo|bát đĩa|khăn trải bàn).{0,15}?(sạch|vệ sinh|gọn gàng|ngăn nắp|thơm|bóng|tinh tươm)",
            r"\b(được lau chùi|được dọn dẹp|giữ gìn|khử trùng|tẩy rửa).{0,10}?(sạch sẽ|thường xuyên|cẩn thận|kỹ lưỡng|kỹ càng)\b",
            r"\b(không gian|môi trường|quán|nhà hàng).{0,10}?(sạch|vệ sinh|gọn gàng|tinh tươm|ngăn nắp|đạt chuẩn)\b",
            r"\b(clean|hygienic)\b",
            r"\b(sạch hơn|vệ sinh hơn|gọn hơn).{0,10}?(mong đợi|dự kiến|so với|đa số)\b",
            r"\b(ấn tượng|hài lòng|thích thú).{0,10}?(vệ sinh|sạch sẽ)\b"
        ]
        negative_patterns = [
            r"\b(dơ|bẩn|ẩm mốc|mùi hôi|rác|kém vệ sinh|lấm lem|bụi bặm|cáu bẩn|hôi hám|bốc mùi|nhớt|dầu mỡ|mất vệ sinh|bừa bộn)\b",
            r"\b(quá bẩn|rất bẩn|siêu bẩn|cực bẩn|bẩn kinh khủng|bẩn hết chỗ nói|bẩn không tưởng|vệ sinh tệ hại)\b",
            r"(bàn|sàn|toilet|nhà vệ sinh|quầy|khu vực|phòng ăn|ghế|menu|dao kéo|bát đĩa|khăn trải bàn).{0,15}?(dơ|bẩn|hôi|ẩm mốc|rác|dính|nhớp|nhầy nhụa|bốc mùi|mốc meo)",
            r"\b(có rác|có mùi|có vết|bám bụi|tràn nước|đổ rác|ứ đọng|nấm mốc|bồn cầu bẩn|bồn rửa bẩn|thùng rác đầy|nước đọng)\b",
            r"\b(mùi).{0,5}?(hôi|khó chịu|nồng nặc|khai|urine|nước tiểu|ẩm mốc|mốc|thối|rác|thức ăn thối)\b",
            r"\b(gián|chuột|kiến|côn trùng|bọ|ruồi|muỗi).{0,10}?(xuất hiện|bò|trong nhà vệ sinh|dưới bàn|trên bàn|bay|bám)\b",
            r"\b(ẩm ướt|ướt át|nước đọng|vũng nước).{0,10}?(sàn|nhà vệ sinh|bếp|góc nhà)",
            r"\b(tóc|móng tay|tàn thuốc|vật lạ).{0,10}?(dưới bàn|trên bàn)\b",
            r"\b(không được lau|không dọn|bỏ mặc|không vệ sinh|vệ sinh kém|dọn dẹp qua loa|lơ là vệ sinh|bỏ bê vệ sinh)\b",
            r"không.{0,10}?(sạch|gọn|ngăn nắp|vệ sinh|lau)"
            r"\b(dirty|sticky)\b"
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


# Gán nhãn ENVIRONMENT#AMBIENCE
def extract_environment_ambience(text):
    ambience_keywords = [
        r"\bkhông gian\b", r"\bdecor\b", r"\btrang trí\b", r"\bánh sáng\b",
        r"\bban công\b", r"\bview\b", r"\bchill\b", r"\blãng mạn\b", r"\bbầu không khí\b",
        r"\bấm cúng\b", r"\bsang trọng\b", r"\bthoáng\b", r"\bmát mẻ\b", r"\bngột ngạt\b",
        r"\bsắp xếp\b", r"\b(nóng|bí)\b",
        r"\b(ấm cúng|thoáng đãng|ngột ngạt|chật chội|rộng rãi|khép kín)\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(keyword), text, re.IGNORECASE) for keyword in ambience_keywords)
    if existAspect:
        positive_patterns = [
            r"(không gian|bầu không khí|decor|trang trí|view|ban công)?.{0,10}(sạch sẽ|rộng rãi|đẹp|dễ chịu|tuyệt vời|lung linh|chill|thơ mộng|lý tưởng|lãng mạn|ấm cúng|ấn tượng|thoáng|sang trọng|mát mẻ|ấm cúng|gần gũi|thân thiện|huyền ảo|ma mị|bí ẩn|cổ kính)",
            r"(rất |khá |cực )?(thẩm mỹ|chill|ấm cúng|dễ chịu|lãng mạn|thư giãn|đáng yêu|thanh bình)",
            r"\b(thơ mộng|mộng mơ|ấn tượng|đẹp mê ly|view đẹp|đẹp ngất)",
            r"(gió|không khí).{0,5}(mát|lạnh|dễ chịu|trong lành|sảng khoái)",
            r"(ngồi ăn|chỗ ngồi).{0,10}(thoải mái|rộng|tự do|tận hưởng)",
            r"\b(ánh sáng.{0,10}(ấm áp|lãng mạn|đẹp|huyền ảo|lung linh))\b",
            r"\b(vibe|năng lượng).{0,10}(tích cực|tốt|tuyệt|mạnh|vui vẻ|ấm áp|nhộn nhịp)\b",
            r"\b(yên tĩnh|thanh bình|bình yên|tĩnh lặng|yên bình).{0,10}(dễ chịu|hoàn hảo)?\b",
            r"\b(nhộn nhịp|sôi động).{0,10}(vui vẻ|thú vị|hấp dẫn)\b",
            r"\b(hoài cổ|nostalgic|retro).{0,10}(đẹp|ấn tượng)\b",
        ]
        negative_patterns = [
            r"(không gian|decor|view|ánh sáng|bầu không khí)?.{0,10}(chê|hầm|nóng|bí|tệ|xấu|ngột ngạt|chói|rối mắt|ồn|ồn ào|nhức mắt|khó chịu|thiếu sáng|bí bách|chật chội|khó chịu|ngột ngạt|bức bối|tù túng|chán ngán|ức chế|buồn tẻ|nặng nề|đáng sợ|ngột ngạt|nóng nực|lạnh lẽo|ẩm ướt|hôi hám|hôi thối|khó thở|buồn tẻ|u ám|chật chội|hẹp|bừa bộn|bẩn thỉu|ngột ngạt|tối tăm|ảm đạm|cũ kỹ|đổ nát)",
            r"(quá ồn|quá sáng|quá tối|không được ấm cúng|khó chịu|cũ kỹ|phá.{0,5}không gian)",
            r"\b(chật chội|cramped|bụi|bẩn|dơ|ẩm ướt|trơn trượt|gió lùa|nhếch nhác|cũ nát|bẩn thỉu|tối tăm|ẩm thấp)\b",
            r"(mưa|nắng).{0,5}(vào|tạt|chiếu|ướt|chói)",
            r"\bánh sáng.{0,10}(tối|mờ|chói|loá mắt|khó chịu|không đủ)\b",
            r"\b(vibe|năng lượng).{0,10}(tiêu cực|xấu|kỳ lạ|nặng nề|ảm đạm)\b",
            r"\b(thiếu ánh sáng|tối om|mờ ảo|nhìn không rõ)\b",
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
        r"\b(nhân viên|staff|server|attendant|host|hostess|cashier|waiter|waitress|bartender|nhân sự|đội ngũ)\b",
        r"\b(ông|bà|anh|chị|bạn|cô|chú|bác)\s*(phụ trách|hướng dẫn|quản lý|chủ)?\b",
        r"\bchủ quán\b",
        r"\bquản lý\b",
        r"\b(bồi bàn|anh bồi|chị bồi)\b",
        r"\bphục vụ\b",
        r"\bngười\s+(phục vụ|order|thu ngân|chăm sóc)\b",
        r"\bnhân viên\s+(phục vụ|order|thu ngân|chăm sóc)\b"
    ]
    staff_activities = [
        r"\b(hòa đồng|cộc cằn|thái độ|phục vụ|nhiệt tình|thuyết minh|giới thiệu|hướng dẫn|tư vấn|giải đáp|đón tiếp|tiếp đón|quan tâm|dịch vụ)\b",
        r"\b(chăm sóc|hỗ trợ)( khách hàng| du khách)?\b",
        r"\bxử lý\s*(tình huống|vấn đề)\b"
    ]

    existAspect = any(re.search(normalize_unicode(entity), text, re.IGNORECASE) for entity in staff_entities) or any(re.search(activity, text, re.IGNORECASE) for activity in staff_activities)
    if existAspect:
        positive_patterns = [
            r"(?<!\bchưa\s)\b(tốt|tuyệt|ổn|đáng khen|hòa đồng|tươi cười|nhiệt tình|dễ thương|vui vẻ|hiếu khách|lịch sự|thân thiện|niềm nở|nhẹ nhàng|hết lòng|tận tâm|tận tình|chu đáo|quan tâm|tử tế|hỗ trợ tốt|chăm sóc|phục vụ|chuyên nghiệp|nhanh nhẹn|hiệu quả)\b",
            r"(?<!\bchưa\s)\b(ấn tượng|hài lòng|thích|tốt).{0,10}?(với|về)?.{0,10}?(nhân viên|phục vụ|quản lý)\b",
            r"(?<!\bchưa\s)\b(được hỗ trợ|được chăm sóc|được quan tâm).{0,10}?(tốt|chu đáo|tận tình)\b",
            r"\b(giới thiệu|recommend|gợi ý).{0,10}?(món|thực đơn).{0,10}?(hay|tốt|phù hợp)\b",
            r"\b(luôn mỉm cười|luôn tươi cười|nụ cười|thái độ tích cực)\b",
            r"(?<!\bchưa\s)\b(professional|friendly|attentive|helpful|courteous|kind|excellent service|great staff)\b"
        ]
        negative_patterns = [
            r"\b(cục súc|tệ|dở|kém|đáng chê|không ổn|không thân thiện|khó ưa|thái độ kém|phục vụ chậm|thái độ|liếc|nói chuyện đùa giỡn|khó chịu|cộc cằn|gắt|khó ưa|thờ ơ|lạnh nhạt|vô duyên|khinh khỉnh|kiêu kỳ|hỗn|mất dạy|bất lịch sự|vô lễ)\b",
            r"\b(thất vọng|không hài lòng|bực mình|ức chế|tức).{0,10}?(với|về)?.{0,10}?(nhân viên|phục vụ|quản lý)\b",
            r"\b(không|thiếu).{0,10}?(hỗ trợ|chú ý|tích cực|tươi cười|thân thiện|nhiệt tình|hợp tác|chăm sóc|quan tâm|hiểu biết|chuyên nghiệp|am hiểu)\b",
            r"\b(phớt lờ|lờ đi|bỏ mặc|không thèm nhìn|quay lưng|thái độ phân biệt)\b",
            r"\b(bad service|rude|unfriendly|slow service|ignored|poor attitude|incompetent|unprofessional)\b"
        ]
        
        for pat in negative_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "NEGATIVE"
        for pat in positive_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "POSITIVE"
        return "NEUTRAL"
    
    return None


# Gán nhãn SERVICE#ORDER
def extract_service_order(text):
    staff_entities = [
        r"\b(nhân viên|nv|staff|server|attendant|host|hostess|cashier|waiter|waitress|bartender|nhân sự|đội ngũ)\b",
        r"\b(ông|bà|anh|chị|bạn|cô)\s+chủ\b",
        r"\bchủ quán\b",
        r"\bquản lý\b",
        r"\b(bồi bàn|anh bồi|chị bồi)\b",
        r"\bphục vụ\b",
        r"\bngười\s+(phục vụ|order|thu ngân|chăm sóc)\b",
        r"\bnhân viên\s+(phục vụ|order|thu ngân|chăm sóc)\b"
    ]
    staff_orders = [
        r"\b(gọi|đặt|order)\s+món\b",
        r"\b(lên|mang|đem|ra|cấp)\s+món\b",
        r"\bphục vụ(\s+món)?\b",
        r"\btốc độ\s+(order|phục vụ)\b",
        r"\b(thời gian|waiting time|serving time)\s+(chờ|lên món|phục vụ)\b",
        r"\b(chờ|đợi|chờ đồ ăn)\b",
        r"\b(món\s+(lên|tới|ra))\b",
        r"\b(sai|thiếu)\s+món\b",
        r"\bthứ tự\s+món\b",
        r"\border\s+food\b"
    ]
    
    existAspect = any(re.search(normalize_unicode(entity), text, re.IGNORECASE) for entity in staff_entities) or any(re.search(normalize_unicode(order), text, re.IGNORECASE) for order in staff_orders)
    if existAspect:
        positive_patterns = [
            r"(phục vụ|mang món|lên món|gọi món|ra món|đem đồ ăn).{0,10}?(nhanh|rất nhanh|liền|kịp lúc|tốt|đúng giờ|ngay lập tức|tức thì|nhanh chóng)",
            r"\b(không phải chờ lâu|mang món đúng|phục vụ đúng hẹn|đúng giờ|đúng thời gian)\b",
            r"\b(thời gian chờ|waiting time|serving time).{0,10}?(ngắn|nhanh|hợp lý|tốt|đáng ngạc nhiên)\b",
            r"\b(món ra đều|món lên đúng thứ tự|đúng như order|đúng yêu cầu|không sai sót|chính xác tuyệt đối)\b",
            r"\b(đầy đủ|không thiếu|không sai|không nhầm lẫn)\b",
            r"\b(phục vụ nhanh hơn dự kiến|món lên nhanh bất ngờ|tốc độ đáng kinh ngạc|order chuẩn xác)\b"
        ]
        negative_patterns = [
            r"(lên món|gọi món|phục vụ|mang món|ra món|đem đồ ăn).{0,15}?(chậm|rất lâu|trễ|mãi không thấy|lâu quá|quá lâu|lâu kinh khủng)",
            r"(chờ|đợi).{0,10}?(lâu|rất lâu|quá lâu|mỏi|ngán|mệt|phát bực|quá giờ|((hơn|gần)\s*\d+\s*(tiếng|phút)))",
            r"\b(thời gian chờ|waiting time|serving time).{0,10}?(lâu|dài|quá lâu|kinh khủng|không chịu nổi)\b",
            r"\b(thiếu món|sai món|món không đúng|mang nhầm món|phục vụ không đều|mang món nhầm|order sai|gọi nhầm)\b",
            r"\b(quên món|không mang đủ|thiếu đồ uống|sai nước sốt|sai topping|sai yêu cầu)\b",
            r"\b(món).{0,10}?(không đúng|không giống|bị thiếu|bị sai|khác với order|khác menu|lên không đúng thứ tự|không theo trình tự|trước sau lộn xộn|không theo order)\b",
            r"\b(mang món tráng miệng trước|món chính lên trước món khai vị)\b",
            r"\bđợi lâu.{0,10}?nên\s*(đồ|món|thức)\s*ăn\s*(nguội( lạnh)?|mất ngon)\b"
        ]
        
        for pat in negative_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "NEGATIVE"
        for pat in positive_patterns:
            if re.search(normalize_unicode(pat), text, re.IGNORECASE):
                return "POSITIVE"
        return "NEUTRAL"
        
    return None

aspect_detection_functions = {
    "LOCATION": extract_location,
    "PRICE": extract_price,
    "FOOD#QUALITY": extract_food_quality,
    "FOOD#VARIETY": extract_food_variety,
    "DRINK#QUALITY": extract_drink_quality,
    "DRINK#VARIETY": extract_drink_variety,
    "ENVIRONMENT#CLEANLINESS": extract_environment_cleanliness,
    "ENVIRONMENT#AMBIENCE": extract_environment_ambience,
    "SERVICE#STAFF": extract_service_staff,
    "SERVICE#ORDER": extract_service_order
}

def append_aspects(df: pd.DataFrame, processor):
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

    df.loc[:, "aspects"] = listAspects
    return df

if __name__ == '__main__':
    processor = VietnameseTextProcessor()
    df = pd.read_csv("./DatasetGGMaps/final_review_googlemap_comments_eatery.csv", index_col=0)
    df = append_aspects(df, processor)
    df.to_csv('./annotated_labels/list_aspects_eateries.csv')