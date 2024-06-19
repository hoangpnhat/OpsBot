from langchain.tools import tool

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate

import sys
import os
sys.path.append(os.getcwd())
from app.chatbot.prompts.system import actor
from app.chatbot.prompts.info_customer import update_customer_info_prompt
from app.chatbot.prompts.material_warranty_staff import material_warranty_prompt
from app.chatbot.prompts.administrator import administrate_store_prompt, administrate_personnel_prompt
from app.chatbot.prompts.promotion import promotions_partnership_prompt, promotions_marketing_prompt

@tool
def update_customer_info(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "Cập nhật thông tin Khách hàng" 
    khi cần cập nhật thông tin khách hàng như số điện thoại, địa chỉ, email, ngày sinh, nghề nghiệp."""

    id_problem = "/vd101"
    system_prompt = actor + update_customer_info_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

# @tool
# def promotions_vip(query: str) -> ChatPromptTemplate:
#     """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi cho khách hàng VIP và sinh nhật", 
#     khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
#     Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

#     id_problem = "/vd51"
                
#     system_prompt= actor + promotions_vip_prompt
#     prompt = ChatPromptTemplate.from_messages([
#         SystemMessagePromptTemplate.from_template(system_prompt),
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template(query),
#         MessagesPlaceholder(variable_name="agent_scratchpad")
#     ])
#     return prompt,id_problem

@tool
def promotions_partnership(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi cho Partnership", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    id_problem = "/vd69"
    system_prompt= actor + promotions_partnership_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def promotions_marketing(query: str) -> ChatPromptTemplate:
    """Quy trình chuẩn để xử lý vấn đề "Chương trình khuyến mãi của YODY", 
    khi gặp các vấn đề Khách hàng không áp được mã giảm giá hoặc không nhận được tin nhắn hoặc mã khuyến mãi,
    Khách hàng không hài lòng với quy trình áp dụng mã khuyến mãi, Vấn đề về việc xác nhận và sử dụng mã khuyến mãi."""

    id_problem = "/vd47"
    system_prompt= actor + promotions_marketing_prompt
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
    system_prompt= actor + material_warranty_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def administrate_store(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "#van_de: Vận hành cửa hàng 
    khi gặp các vấn đề mất điện hoặc mất mạng tại cửa hàng, in hoá đơn bị mờ hoặc lỗi,báo lỗi camera, hỗ trợ về giấy tờ, hợp đồng, phép kinh doanh."""
    
    id_problem = "/vd14"
    system_prompt= actor+ administrate_store_prompt
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

    system_prompt= actor+ administrate_personnel_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def other(query: str) -> str:
    """Quy trình xử lý khi không phân loại được vấn đề hoặc vấn đề không thuộc phạm vi xử lý.""" 
    return """Vấn đề này vượt quá thẩm quyền hỗ trợ của em, vui lòng liên hệ nhân viên @Omni. CX. Trần Văn Nhớ để được hỗ trợ
            ```json
            {
            "status": "clarified",
            "mention": [{
                "pic_gapo_name": "@Omni. CX. Trần Văn Nhớ",
                "pic_gapo_id": 158344261
                }]
            }
            ```
"""
