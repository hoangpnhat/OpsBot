import os
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers.string import StrOutputParser
from typing import List, Tuple, Dict
from dotenv import load_dotenv, find_dotenv
from typing import Callable
from langchain.chat_models.base import BaseChatModel
from pydantic import BaseModel, Field
from typing import List, Union, Dict
import pydantic
from langfuse.decorators import observe, langfuse_context

from app.chatbot.prompts.contextualization import contextualize_q_system_prompt
from app.chatbot.prompts.langfuse_prompt import get_prompt_str
from app.chatbot.query_router.router import Router
from app.common.config import logger


@observe()
def contextualize_query(llm_model: BaseChatModel, user_query: str, chat_history: List[BaseMessage]) -> str:
    """
    This function takes a user query and a chat history and returns a contextualized query.

    Args:
        llm_model (BaseChatModel): The language model to use for contextualization
        user_query (str): The user query to contextualize
        chat_history (List[BaseMessage]): The chat history to use for contextualization

    Returns:
        str: The contextualized query
    """
    # if len(chat_history) == 0:
    #     return user_query

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    chain = contextualize_q_prompt | llm_model #| StrOutputParser()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    ai_response = chain.invoke(
        {"chat_history": chat_history, "input": user_query},
        config={"callbacks": [langfuse_handler]}
    )
    #ai_response.response_metadata

    return ai_response.content


@observe()
def answer_from_chat(llm_model: BaseChatModel, 
                     user_query: str,
                     qa_system_prompt: str,
                     chat_history: List[BaseMessage]) -> str:
    """
    This function takes a user query, a QA system prompt, and a chat history and returns an answer.

    Args:
        llm_model (BaseChatModel): The LLM model to use for answering
        user_query (str): The user query to answer
        qa_system_prompt (str): The QA system prompt to use for answering
        chat_history (List[BaseMessage]): The chat history to use for answering

    Returns:
        str: The answer

    """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    chain = qa_prompt | llm_model #| StrOutputParser()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    ai_response = chain.invoke(
        {"chat_history": chat_history, "input": user_query},
        config={"callbacks": [langfuse_handler]}
    )
    return ai_response.content

@observe()
def pick_tool(llm_model: BaseChatModel,
              user_query: str,
              contextualized_query: str,
              chat_history: List[BaseMessage],
              system_prompt: str,
              tools: List[Callable]) -> List[Dict]:
    """
    This function takes a user query, a system prompt, a chat history, and a list of tools and returns the tool calls.

    Args:
        llm_model (BaseChatModel): The LLM model to use for answering
        user_query (str): The user query to answer
        contextualized_query (str): The contextualized query to use for answering
        chat_history (List[BaseMessage]): The chat history to use for answering
        system_prompt (str): The system prompt to use for answering
        tools (List[Callable]): The list of tools to use for answering

    Returns:
        List[Dict]: The tool calls for the given user query. 
                    For example: [{'name': 'multiply', 'args': {'a': 119, 'b': 8}, 'id': 'call_RofMKNQ2qbWAFaMs'}]
    """
    
    prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    chain = prompt_template | llm_model.bind_tools(tools)
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    response = chain.invoke(
                {
                    "input": user_query, 
                    "chat_history": chat_history,
                    "agent_scratchpad": []
                }, 
                config={"callbacks": [langfuse_handler]})
    return response.tool_calls
    

def choose_appropriate_tools(user_query: str, router: Router=Router()) -> List[str]:
    """
    This function takes a user query, a chat history, and a router and returns appropriate function names for the query.

    Args:
        user_query (str): The user query to classify
        router (Router): The router to use for classification

    Returns:
        List[str]: The function names
    """

    selected_routes = router.predict(user_query)
    tool_names = [route.name for route in selected_routes]
    if not tool_names or len(tool_names) == 0:
        logger.info("No appropriate function found for the query in the router. \
                    Using default functions unclear_issue and chitchat.")
        tool_names = ["unclear_issue", "chitchat"]
    return tool_names


def create_redirect_tools(tool_names: List[str], tool_info: Dict) -> List[BaseModel]:
    """
    This function creates tool schemas dynamically for the given class name.
    It actually creates a tool schema for the given function name.

    Args:
        tool_names (List[str]): The list of tool names
        tool_info (Dict): The object containing the function information
                        Ex: {
                            "update_customer_info": {
                                "name": "update_customer_info",
                                "id": "/vd101",
                                "type": "redirect"}
                            }
    Returns:
        List[BaseModel]: The list of tool schemas
    """
    tool_detail = []
    for name in tool_names:
        tool = tool_info.get(name, None)
        if tool and tool.get("type") == "redirect":
            tool_detail.append(tool_info.get(name))

    tool_schemas = []
    if not isinstance(tool_detail, List):
        logger.info("Invalid type of tool_info. It must be a List.")
    else:
        # Create tool schemas dynamically
        for tool in tool_detail:
            func_desc = tool.get("func_desc")
            base_attributes = {
                '__doc__': func_desc,
                'query': (str, Field(description="The query from user"))
            }
            
            tool_schema = pydantic.create_model(tool.get("name"), **base_attributes)
            tool_schemas.append(tool_schema)
    return tool_schemas


def load_external_tools(tool_names: List[str], tool_info: Dict) -> List[BaseModel]:
    """
    This function load defined tool schemas for the given class name.

    Args:
        tool_names (List[str]): The list of tool names. Ex ["update_customer_info", "promotion_partnership"]
        tool_info (Dict): The object containing the function information
                        Ex: {
                            "update_customer_info": {
                                "name": "update_customer_info",
                                "id": "/vd101",
                                "type": "external"}
                            }
        tool_schemas (Dict): The object containing the tool schemas
    Returns:
        List[BaseModel]: The list of tool schemas
    """

    tool_schemas = []
    # Load tool schemas from the tool_info
    for name in tool_names:
        tool_object = tool_info.get(name, None)
        if not tool_object:
            continue
        tool_schema = tool_object.get("schema", None)
        if not tool_schema:
            logger.error(f"Schema not found for the function {name}")
        else:
            tool_schemas.append(tool_schema)
    return tool_schemas

@observe()
def execute_redirect_tool(tool: Dict,
                          tool_info: Dict,
                          llm_model: BaseChatModel,
                          user_query: str,
                          contextualized_query: str,
                          chat_history: List[BaseMessage]) -> str:
    """
    This function takes a user query, a system prompt, a chat history, and a list of tools and returns the tool calls.

    Args:
        tool (Dict): The tool to execute. Ex {"name": "update_customer_info", "args": {"query": "....."}
        tool_info (Dict): The all tools information. 
                    Ex: {"update_customer_info": {"name": "update_customer_info", "id": "/vd101", "type": "redirect"}}
        llm_model (BaseChatModel): The LLM model to use for answering
        user_query (str): The user query to answer
        chat_history (List[BaseMessage]): The chat history to use for answering

    Returns:
        str: The tool response (answer from the llm model)
    """
    func_name = tool.get("name")
    func_args = tool.get("args")

    system_prompt = tool_info.get(func_name, {}).get("prompt", None)
    if not system_prompt:
        logger.error(f"No prompt found for the function {func_name}")
        system_prompt = "Hãy trả lời cho User như sau: `Em xin lỗi, em chưa được học về vấn đề này. Nhờ anh/chị liên hệ bộ phận CNTT để được hỗ trợ ạ.`"
    else:
        system_prompt += "\n\n### Luôn xưng hô là `Em` và `Anh/chị` đối với user. Hãy trả lời lịch sự, tự nhiên và ngắn gọn. \n \
        Đừng quên mời người phụ trách (người có thẩm quyền) vào xử lý vấn đề khi đã có đủ thông tin cần thiết. \
        Nếu có vấn dề khẩn cấp hoặc không thể giải quyết, hãy nhờ anh <@Omni. CX. Trần Văn Nhớ (id:158344261)> vào giúp đỡ. \n \
        Nếu có vấn đề kỹ thuật về sản phẩm Opsbot này (là chính bạn), hãy nhờ anh <@CNTT. Phạm Hoài Nguyên (id:1029514815)> vào giúp đỡ. "
    
    prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])
    chain = prompt_template | llm_model
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    result = chain.invoke(
        {
            "input": user_query,
            "chat_history": chat_history
        }, config={"callbacks": [langfuse_handler]})
    return result.content


def execute_external_tool(tool: List[Dict],
                          tool_info: Dict,
                          llm_model: BaseChatModel,
                          user_query: str,
                          contextualized_query: str,
                          chat_history: List[BaseMessage]) -> str:
    """
    This function to execute selected external function.

    Args:
        tool (List[Dict]): The tool to execute
        tool_info (Dict): The all tools information
        llm_model (BaseChatModel): The LLM model to use for answering
        user_query (str): The user query to answer
        chat_history (List[BaseMessage]): The chat history to use for answering
    
    Returns:
        str: The response (answer from the llm model)
    """
    func_name = tool[0].get('name')
    func_args = tool[0].get('args')
    list_kargs = []
    for tool in tool:
        list_kargs.append(tool.get('args'))

    callable_func = tool_info.get(func_name).get("function", None)
    answer = callable_func(list_kargs, user_query, contextualized_query, chat_history, llm_model)
    return answer


@observe()
def check_user_satisfaction(user_query: str, chat_history: List[BaseMessage], llm_model: BaseChatModel) -> bool:
    """
    This function to use llm model to check user satisfaction

    Args:
        llm_model (BaseChatModel): The LLM model to use for answering
        user_query (str): The user query to answer
        chat_history (List[BaseMessage]): The chat history to use for answering

    Returns:
        bool: The user satisfaction. True if user is satisfied, False otherwise
    """

    system_prompt = """ Bạn là một trợ lý quan sát, dựa vào cuộc trò chuyện giữa bạn và user, 
    hãy đánh giá liệu user có hài lòng với câu trả lời của bạn không. 
    Trả lời `YES` nếu user hài lòng hoặc đang trong quá trình trao đổi thông tin với bạn.
    Trả lời `NO` với các trường hợp sau:
        - User KHÔNG hài lòng với câu trả lời của bạn
        - Bạn điều hướng user đến một tool hoặc người phụ trách KHÔNG phù hợp
        - User KHÔNG hài lòng với kết quả từ tool
    
    ### LƯU Ý: Câu trả lời của bạn chỉ là `YES` hoặc `NO`.
    """
    satisfaction_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )
    chain = satisfaction_prompt | llm_model | StrOutputParser()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    ai_response = chain.invoke(
        {"chat_history": chat_history, "input": user_query},
        config={"callbacks": [langfuse_handler]}
    )

    if ai_response.upper() == "NO" or ai_response.upper() == "KHÔNG" or "NO" in ai_response.upper():
        return False
    return True


def get_redirect_tools(selected_tools: List[Dict], tool_info: Dict) -> List[Dict]:
    """
    This function takes a list of selected tools and only the redirect tools.

    Args:
        selected_tools (List[Dict]): The list of selected tools

    Returns:
        List[Dict]: The list of external tools and the list of redirect tools
    """
    redirect_tools = []
    for tool in selected_tools:
        if not tool_info.get(tool['name']):
            continue
        if tool_info.get(tool['name']).get("type") == "redirect":
            redirect_tools.append(tool)
    return redirect_tools


def get_external_tools(selected_tools: List[Dict], tool_info: Dict) -> List[Dict]:
    """
    This function takes a list of selected tools and filter the external tool, 
    only use ONE tool, but it can called multiple times.

    Args:
        selected_tools (List[Dict]): The list of tools which are selected by the LLM

    Returns:
        List[Dict]: The tool to be called (it is a List because it can be called multiple times)
    """
    external_tools = []
    for tool in selected_tools:
        tool_name = tool.get("name")
        meta_tool = tool_info.get(tool_name, None)
        if not meta_tool:
            continue
        if meta_tool.get("function", None):
            external_tools.append(tool)


    if len(external_tools) == 0 or len(external_tools) == 1:
        return external_tools
    else:
        # only get the first external tool
        multiple_tool_calls = []
        first_tool = external_tools[0]
        multiple_tool_calls.append(first_tool)
        for tool in external_tools[1:]:
            if tool['name'] == first_tool['name']:
                multiple_tool_calls.append(tool)
        return multiple_tool_calls
    