from langchain.tools import tool
from prompts import material_warranty_prompt,update_customer_info_prompt,administrate_order_prompt,promotions_prompt,personnel_prompt
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate

@tool
def material_warranty(query: str) -> str:
    """Quy trình xử lý vấn đề "Bảo hành chất liệu" do chất liệu không đạt yêu cầu. """

    system_define = """Bạn là một người điều phối viên chuyên nghiệp của một công ty bán hàng thời trang YODY. 
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng \n"""
    system_prompt= system_define + material_warranty_prompt

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt

@tool
def update_customer_info(query: str) -> str:
    """Quy trình xử lý vấn đề "Cập nhật thông tin Khách hàng" 
    khi cần cập nhật thông tin khách hàng như số điện thoại, địa chỉ, email, ngày sinh, nghề nghiệp."""

    system_define = """Bạn là một người điều phối viên chuyên nghiệp của một công ty bán hàng thời trang YODY. 
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng \n"""
   
    fomart_output= """\n #Lưu ý: kết quả trả về phải có format như sau:
             {{"old_phone": 0123456789 /"old_address": "123 ABC" / "old_email":"testing@yody.vn"/ "old_job": "student",
            "new_phone": 0987654321 /"new_address": "234 XYZ" / "new_email":"testing_one@yody.vn"/ old_job": "teacher"}}
            "Đã đổi thông tin khách hàng thành công."
            """
    system_prompt= system_define + update_customer_info_prompt + fomart_output

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt
@tool
def administrate_order(query: str) -> str:
    """Quy trình xử lý vấn đề "#van_de: Hành chính cửa hàng (HD điện, chính quyền...) 
    khi gặp các vấn đề mất điện hoặc mất mạng tại cửa hàng, in hoá đơn bị mờ hoặc lỗi, hỗ trợ về giấy tờ, hợp đồng, phép kinh doanh."""
    
    system_define = """Bạn là một chuyên viên hành chính chuyên nghiệp của một công ty bán hàng thời trang YODY.
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng.
            Nếu không thể tự xử lý, hãy nhờ các đồng nghiệp có chuyên môn (được nêu trong quy trình) để hỗ trợ bạn \n"""
    system_prompt= system_define+ administrate_order_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt


@tool
def promotions(query: str) -> str:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    system_define = """Bạn là một chuyên viên chăm sóc khách hàng chuyên nghiệp của một công ty bán hàng thời trang YODY.
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng 
            Nếu không thể tự xử lý, hãy nhờ các đồng nghiệp có chuyên môn (được nêu trong quy trình) để hỗ trợ bạn\n"""
    system_prompt= system_define+ promotions_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt

@tool
def personnel(query: str) -> str:
    """Quy trình chuẩn để xử lý vấn đề "Hỗ trợ hành chính nhân sự", 
    Các yêu cầu thường gặp: Yêu cầu cấp lại mật khẩu, hỗ trợ đăng nhập vào các phần mềm của công ty (Unicorn, Office), hỗ trợ phân quyền để xem báo cáo hoặc tài liệu, hỗ trợ vấn đề liên quan đến đánh giá năng lực chuyên môn."""

    system_define = """Bạn là một chuyên viên quản lý nhân sự chuyên nghiệp của một công ty bán hàng thời trang YODY.
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng 
            Nếu không thể tự xử lý, hãy nhờ các đồng nghiệp có chuyên môn (được nêu trong quy trình) để hỗ trợ bạn\n"""
    system_prompt= system_define+ personnel_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt

@tool
def other(query: str) -> str:
    """Quy trình xử lý vấn đề những vấn đề khác, liên hệ với @Coordinators để được hỗ trợ.""" 
    return "Vấn đề này vượt quá thẩm quyền hỗ trợ của em, vui lòng liên hệ nhân viên @coordinate để được hỗ trợ"
