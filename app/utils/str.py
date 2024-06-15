import json
import re
def extract_and_remove_dict_from_string(s):
    # Xử lý trường hợp dict được bọc trong ```json và ```
    pattern_json = r'```json\s*({.*?})\s*```'
    match_json = re.search(pattern_json, s, re.DOTALL)
    
    if match_json:
        dict_str = match_json.group(1)
        modified_str = s[:match_json.start()] + s[match_json.end():]
    else:
        # Tìm dict có thể có trong chuỗi (cả JSON và non-JSON)
        pattern_dict = r'{.*}'
        match_dict = re.search(pattern_dict, s, re.DOTALL)
        
        if match_dict:
            dict_str = match_dict.group(0)
            modified_str = s[:match_dict.start()] + s[match_dict.end():]
        else:
            return s, None

    # Chuyển chuỗi dict thành dict thực
    try:
        dict_data = json.loads(dict_str.replace("'", "\""))
    except json.JSONDecodeError as e:
        print(f"Lỗi khi phân tích chuỗi: {e}")
        return s, None

    return modified_str.strip(), dict_data
# str = """
#     Cảm ơn bạn đã cung cấp lý do. Tôi đã ghi nhận thông tin và yêu cầu của bạn. Bây giờ, tôi sẽ mời @Omni. CX. Trần Văn Nhớ vào để giúp cập nhật thông tin của bạn.
# {
#   "status": "clarified"
# }
#     """
# print(extract_dict_from_string(str)['status'])