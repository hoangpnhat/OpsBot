import requests
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from typing import List, Dict
import os
from app.common.config import logger
from app.database.graphdb import GraphDatabaseConnection
from app.chatbot.prompts.rewrite_query import rewrite_query_prompt
from app.chatbot.prompts.langfuse_prompt import get_prompt_str

graph_database_promtion = GraphDatabaseConnection()

def retrieve_promotion(query: str) -> str:
    """
    This function is to retrivel the promotion information from the graph database
    Args:
        data (dict): The query to retrivel the promotion information
    Returns:
        Response: The response of the promotion information
    """

    llm = ChatOpenAI(model=os.environ.get("LLM_GRAPH"), temperature=0,
                     api_key=os.environ.get("OPENAI_API_KEY"))
    retrival_engine = graph_database_promtion.get_retrieval_engine()

    lf_rewrite_query = get_prompt_str(name="rewrite_query", label='latest')
    lf_system_prompt = lf_rewrite_query or rewrite_query_prompt

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(lf_system_prompt),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])
    chain = prompt | llm
    query_graph = chain.invoke(
        {
            "input": query,
        },
    )
    logger.debug(f"Query graph: {query_graph.content}")
    result = retrival_engine.retrieve(query_graph.content)
    response = "\n".join([node.text for node in result]
                         ) if result else "No promotion found"
    return response


def query_promotion(list_kargs: List[Dict], 
                   user_query: str,
                   contextualized_query: str,
                   chat_history: List[BaseMessage], 
                   llm: BaseChatModel) -> str:
    
    """Hàm này trả về thông tin chương trình khuyến mãi khi người dùng hỏi về thông tin chương trình khuyến mãi
    
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
    query = kargs.get("query", "")

    response_retrieval = retrieve_promotion(contextualized_query)
    logger.debug(f"Response of retrieval: {response_retrieval}")

    lf_actor = "Bạn là một chuyên viên hỗ trợ vấn đề của một công ty bán hàng thời trang YODY.\n"

    infomation_promotion = f"""Sau khi truy vấn trên Graph database, bạn tìm thấy thông tin sau: \n
    {response_retrieval}
    \n
    NOTE: 
    -   Thông tin truy vấn có cấu trúc: <LABEL_ENTITY>: <VALUE_ENTITY> -> <RELATIONSHIP> -> <LABEL_ENTITY>: <VALUE__ENTITY>
    -   Mỗi <VALUE_ENTITY> là 1 thực thể riêng, dựa vào query bạn chỉ trả lời đúng thực thể cần tìm.
    Hãy kiểm tra xem thông tin trên có đúng không và giải quyết vấn đề của người dùng
    Nếu có, hãy cung cấp thông tin cho người dùng, 
    Nếu không, hãy xin lỗi và báo là không tìm thấy thông tin cần thiết
    """

    lf_actor = lf_actor
    system_prompt = lf_actor + infomation_promotion

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(user_query)
    ])
    
    chain = prompt | llm

    response = chain.invoke({
        "chat_history": chat_history
    })

    return response.content
