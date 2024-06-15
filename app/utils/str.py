import ast
from typing import List, Dict
def extract_and_remove_dict_from_string(s):
    # Tìm vị trí bắt đầu và kết thúc của dict trong chuỗi
    start = s.find('{')
    end = s.rfind('}') + 1

    # Nếu không tìm thấy dict trong chuỗi, trả về chuỗi gốc và None
    if start == -1 or end == -1:
        return s, None

    # Trích xuất chuỗi con chứa dict
    dict_str = s[start:end]

    # Chuyển chuỗi dict thành dict thực
    try:
        dict_data = ast.literal_eval(dict_str)
    except (SyntaxError, ValueError) as e:
        # Nếu không chuyển được, trả về chuỗi gốc và None
        print(f"Lỗi khi phân tích chuỗi: {e}")
        return s, None

    # Xóa dict ra khỏi chuỗi gốc
    modified_str = s[:start] + s[end:]

    return modified_str.strip(), dict_data
# str = """
#     Cảm ơn bạn đã cung cấp lý do. Tôi đã ghi nhận thông tin và yêu cầu của bạn. Bây giờ, tôi sẽ mời @Omni. CX. Trần Văn Nhớ vào để giúp cập nhật thông tin của bạn.
# {
#   "status": "clarified"
# }
#     """
# print(extract_dict_from_string(str)['status'])