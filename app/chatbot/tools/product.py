import requests
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from langchain.chat_models.base import BaseChatModel
import json
from typing import List, Dict

def search_product(list_kargs: List[Dict], 
                   user_query: str,
                   contextualized_query: str,
                   chat_history: List[BaseMessage], 
                   llm: BaseChatModel) -> str:
    """
    This function is used to search for product information based on the product code and return the response to the user.

    Args:
        list_kargs (List[Dict]): List of dictionaries containing the key-words arguments for the function.
                                The function can be called multiple time with each dictionary in the list.
        user_query (str): The user's query
        chat_history (List[BaseMessage]): The chat history
        llm (BaseChatModel): The language model used to generate the response
    
    Returns:
        str: Your response
    
    """

    kargs = list_kargs[0]
    product_code = kargs.get("product_code", "").strip()
    # Response is a xml format
    url = f"https://unicorn-dev.yody.io/admin/v3/product/public/products/vdm-request.json?page=1&limit=2&search={product_code}"
    headers = {
        "Content-Type": "text/html",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Xin lỗi em không thể tìm thấy thông tin sản phẩm này, vui lòng kiểm tra lại mã sản phẩm ạ!"
    
    xml_content = response.text
    json_content = json.loads(xml_content)


    product_str = ""
    for product in json_content['data']:
        product_info = f"""
        Mã sản phẩm: {product.get("code", "Không có mã sản phẩm")}
        Tên sản phẩm: {product.get("title", "Không có tên sản phẩm")}
        Tồn kho: {str(product.get("inventory_quantity", 0))}
        SKU: {product.get("sku", "Không có SKU")}
        Màu sắc: {product.get("color", "")}
        Size: {product.get("size", "")}
        """

        product_str += product_info + "\n\n\n"

    system_prompt= """
    Dưới đây là thông tin sản phẩm được truy xuất từ hệ thống của công ty YODY.:
    Hãy viết lại câu trả lời của bạn dựa trên thông tin sản phẩm này một cách ngắn gọn.
    """

    if product_str == "":
        system_prompt = f"Hãy phản hồi lại cho User là không tìm thấy sản phẩm với mã {product_code}."
        product_str = f"Không tìm thấy sản phẩm {product_code}, hãy kiểm tra lại mã sản phẩm."
    

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(product_str)
    ])
    
    chain = prompt | llm

    response = chain.invoke({
        "chat_history": chat_history
    })

    return response.content

