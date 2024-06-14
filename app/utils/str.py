import ast
from typing import List, Dict
def extract_dict_from_string(s)-> Dict | None:
    """
    This function extracts a dictionary from a string

    Args:
        s (str): The string containing the dictionary
    Returns:
        dict: The dictionary extracted from the string
    """
    # Find the start and end position of the dict in the string
    start = s.find('{')
    end = s.rfind('}') + 1

    # If the dict is not found in the string, return None
    if start == -1 or end == -1:
        return None

    # Extract the substring containing the dict
    dict_str = s[start:end]

    # Convert string dict to real dict
    try:
        dict_data = ast.literal_eval(dict_str)
    except (SyntaxError, ValueError) as e:
        # If transfer fails, return None
        print(f"Lỗi khi phân tích chuỗi: {e}")
        return None

    return dict_data
# str = """
#     Cảm ơn bạn đã cung cấp lý do. Tôi đã ghi nhận thông tin và yêu cầu của bạn. Bây giờ, tôi sẽ mời @Omni. CX. Trần Văn Nhớ vào để giúp cập nhật thông tin của bạn.
# {
#   "status": "clarified"
# }
#     """
# print(extract_dict_from_string(str)['status'])