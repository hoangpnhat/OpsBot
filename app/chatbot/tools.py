from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate
from app.chatbot.prompts.system import actor
from app.chatbot.prompts.info_customer import update_customer_info_prompt
from app.chatbot.prompts.material_warranty_staff import material_warranty_prompt
from app.chatbot.prompts.administrator import administrate_store_prompt, administrate_personnel_prompt
from app.chatbot.prompts.promotion import promotions_partnership_prompt, promotions_marketing_prompt
from app.chatbot.prompts.langfuse_prompt import get_prompt_str


@tool
def update_customer_info(query: str) -> ChatPromptTemplate:
    """Quy trình xử lý vấn đề "Cập nhật thông tin Khách hàng" 
    khi cần cập nhật thông tin khách hàng như số điện thoại, địa chỉ, email, ngày sinh, nghề nghiệp."""


    id_problem = "/vd101"
    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_update_customer_info_prompt = get_prompt_str(name="update_customer_info", 
                                                 label='latest')
    
    lf_actor = lf_actor or actor
    lf_update_customer_info_prompt = lf_update_customer_info_prompt or update_customer_info_prompt

    system_prompt = lf_actor + lf_update_customer_info_prompt
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

    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_promotions_partnership_prompt = get_prompt_str(name="promotions_partnership", 
                                                   label='latest')
    
    lf_actor = lf_actor or actor
    lf_promotions_partnership_prompt = lf_promotions_partnership_prompt or promotions_partnership_prompt
    
    id_problem = "/vd69"
    system_prompt= lf_actor + lf_promotions_partnership_prompt
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

    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_promotions_marketing_prompt = get_prompt_str(name="promotions_marketing", 
                                                 label='latest')
    
    lf_actor = lf_actor or actor
    lf_promotions_marketing_prompt = lf_promotions_marketing_prompt or promotions_marketing_prompt
    
    id_problem = "/vd47"
    system_prompt= lf_actor + lf_promotions_marketing_prompt
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

    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_material_warranty_prompt = get_prompt_str(name="material_warranty", label='latest')

    lf_actor = lf_actor or actor
    lf_material_warranty_prompt = lf_material_warranty_prompt or material_warranty_prompt

    id_problem = "/vd2"
    system_prompt= lf_actor + lf_material_warranty_prompt
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
    
    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_administrate_store_prompt = get_prompt_str(name="administrate_store", label='latest')

    lf_actor = lf_actor or actor
    lf_administrate_store_prompt = lf_administrate_store_prompt or administrate_store_prompt
    
    id_problem = "/vd14"
    system_prompt= lf_actor+ lf_administrate_store_prompt
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
    lf_actor = get_prompt_str(name="actor", label='latest')
    lf_administrate_personnel_prompt = get_prompt_str(name="administrate_personnel", 
                                                   label='latest')
    
    lf_actor = lf_actor or actor
    lf_administrate_personnel_prompt = lf_administrate_personnel_prompt or administrate_personnel_prompt
    
    system_prompt= lf_actor + lf_administrate_personnel_prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(query),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt,id_problem

@tool
def other(query: str) -> str:
    """
    Đây là "other" hàm này sẽ được chọn khi không phân loại được vấn đề hoặc vấn đề không thuộc phạm vi xử lý của bạn.

    Args:
        query (str): Câu hỏi của người dùng
    
    Returns:
        str: Câu trả lời từ của bạn
    
    """ 
    answer = """Vấn đề này vượt quá thẩm quyền hỗ trợ của em, vui lòng liên hệ nhân viên @Omni. CX. Trần Văn Nhớ để được hỗ trợ
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
    problem_id = "/vd0"
    return answer, problem_id
