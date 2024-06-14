from langchain.tools import tool

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate

import sys
import os
sys.path.append(os.getcwd())
from app.chatbot.prompts.system import system_action
from app.chatbot.prompts.info_customer import update_customer_info_prompt
from app.chatbot.prompts.material_warranty_staff import material_warranty_prompt
from app.chatbot.prompts.administrator import administrate_store_prompt, administrate_personnel_prompt
from app.chatbot.prompts.promotion import promotions_vip_prompt, promotions_partnership_prompt, promotions_marketing_prompt

@tool
def update_customer_info(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "Cập nhật thông tin Khách hàng" 
    khi cần cập nhật thông tin khách hàng như số điện thoại, địa chỉ, email, ngày sinh, nghề nghiệp."""

    id_problem = "/vd101"
    system_prompt = system_action + update_customer_info_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def promotions_vip(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi cho khách hàng VIP và sinh nhật", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    id_problem = "/vd51"
                
    system_prompt= system_action + promotions_vip_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def promotions_partnership(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi cho Partnership", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    id_problem = "/vd69"
    system_prompt= system_action + promotions_partnership_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def promotions_marketing(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi hàng tháng", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    id_problem = "/vd47"
    system_prompt= system_action + promotions_marketing_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def material_warranty(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "Bảo hành chất liệu" do chất liệu không đạt yêu cầu. """

    id_problem = "/vd2"
    system_prompt= system_action + material_warranty_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def administrate_store(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "#van_de: Vận hành cửa hàng (HD điện, chính quyền...) 
    khi gặp các vấn đề mất điện hoặc mất mạng tại cửa hàng, in hoá đơn bị mờ hoặc lỗi, hỗ trợ về giấy tờ, hợp đồng, phép kinh doanh."""
    
    id_problem = "/vd14"
    system_prompt= system_action+ administrate_store_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem


@tool
def personnel(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Hỗ trợ hành chính nhân sự", 
    Các yêu cầu thường gặp: Yêu cầu cấp lại mật khẩu, hỗ trợ đăng nhập vào các phần mềm của công ty (Unicorn, Office), hỗ trợ phân quyền để xem báo cáo hoặc tài liệu, hỗ trợ vấn đề liên quan đến đánh giá năng lực chuyên môn."""

    id_problem = "/vd12"
    system_define = """Bạn là một chuyên viên quản lý nhân sự chuyên nghiệp của một công ty bán hàng thời trang YODY.
            Dựa vào quy trình dưới đây, hãy xử lý vấn đề của người dùng 
            Nếu không thể tự xử lý, hãy nhờ các đồng nghiệp có chuyên môn (được nêu trong quy trình) để hỗ trợ bạn\n"""
    format_output= """\n #Lưu ý: kết quả trả về phải có format JSON gồm có trường status. 
    Ở trường "status" lựa chọn giữa: 
        -"out of scope" cho trường hợp không thể hỗ trợ
        -"clarifying" cho trường hợp đang làm rõ vấn đề
        -"clarified" cho trường hợp đã làm rõ vấn đề.
    Fomart:
    *YOUR ANSWER HERE* \n {{'status': "out of scope"/ "clarifying"/ "clarified"}}
    ví dụ:
    - Đã nhận thông tin, nhờ @... hỗ trợ em vấn đề này với ạ \n {{'status': "clarified"}}
    - Không thể hỗ trợ vấn đề này, vui lòng liên hệ @coordination để được hỗ trợ \n {{'status': "out of scope"}}       
    - Nhờ anh/chị cũng cấp thêm thông tin về vấn đề này với ạ \n {{'status': 'clarifying'}}"""
    system_prompt= system_define+ administrate_personnel_prompt + format_output
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def other(query: str) -> str:
    """Quy trình xử lý vấn đề những vấn đề khác, liên hệ với @Coordinators để được hỗ trợ.""" 
    return "Vấn đề này vượt quá thẩm quyền hỗ trợ của em, vui lòng liên hệ nhân viên @coordinate để được hỗ trợ"
