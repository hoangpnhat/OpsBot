import os
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from typing import List, Union, Dict, Tuple
import sys
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langfuse.decorators import langfuse_context, observe

load_dotenv(find_dotenv(), override=True)

from app.common.config import logger
from app.chatbot.tools import material_warranty, update_customer_info,administrate_store, \
                                promotions_partnership,promotions_marketing,personnel,other
from app.chatbot.prompts.system import system_prompt


class Chatbot:
    def __init__(self, model=os.environ.get("OPENAI_MODEL"), temperature=0, api_key=None):
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.tools = [
            material_warranty, update_customer_info, administrate_store, 
            promotions_partnership,promotions_marketing, personnel, other
        ]
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature, api_key=self.api_key)
        # self.llm = ChatGroq(temperature=0, groq_api_key="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", model_name="llama3-70b-8192")
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.prompt_template = self.setup_prompt_template()
        self.chain_for_tool = self.prompt_template | self.llm_with_tools


    @staticmethod
    @observe(capture_output=None)
    def call_function_by_name(function_name, args) -> Tuple[str, str]:
        """
        Call a function by its name and arguments

        Args:
            function_name (str): The name of the function
            args (dict): The arguments for the function
        
        Returns:
            Tuple[str, str]: The prompt of the problem and the id of the problem
        """
        func = globals().get(function_name)
        if func:
            result = func(args)
            return result
        else:
            raise ValueError(f"Function {function_name} not found")

    @staticmethod
    def setup_prompt_template():
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    @observe()
    def select_tool(self, user_input, chat_history) -> List[Union[HumanMessage, AIMessage]]:
        """
        This function selects the tool based on the user input

        Args:
            user_input (str): The user input
            chat_history (List[Union[HumanMessage, AIMessage]]): The chat history
        
        Returns:
            AIMessage: The selected tool
        """
        selected_tool = self.chain_for_tool.invoke(
                {
                    "input": user_input, 
                    "chat_history": chat_history,
                    "agent_scratchpad": []
                },
                config={"callbacks": [langfuse_context.get_current_langchain_handler()]}
        )
        logger.debug(f"Selected tool: {selected_tool}")
        return selected_tool

    
    @observe(capture_input=None)
    def handle_problem(self, problem_prompt, chat_history) -> str:
        """
        This function handles the problem by calling the LLM

        Args:
            problem_prompt (str): The prompt of a specific problem
            chat_history (List[Union[HumanMessage, AIMessage]]): The chat history

        Returns:
            str: The response from the LLM
        """
        chain = problem_prompt | self.llm
        response = chain.invoke(
            {
                "chat_history": chat_history, 
                "agent_scratchpad": []
                },
                config={"callbacks": [langfuse_context.get_current_langchain_handler()]}
            )
        return response.content


    @observe()
    def chat(self, 
             chat_history: List[Union[HumanMessage, AIMessage]], 
             user_input: str, 
             user_id: str = None, 
             session_id: str = None,
             metadata: Dict = None
             ) -> str:
        """
        This function is the main function to chat with the bot
        
        Args:
            chat_history (List[Union[HumanMessage, AIMessage]]): The chat history
            user_input (str): The user input to chat with the bot
            user_id (str): The user_id to log in langfuse
            session_id (str): The session id to log in langfuse
            metadata (Dict): The metadata to log in langfuse
        
        """
        logger.debug(f"User input: {user_input}")
        try:
            selected_tool = self.select_tool(user_input, chat_history)
            logger.debug(f"Selected tool: {selected_tool}")

            try:
                function_name = selected_tool.tool_calls[0]['name']
                function_args = selected_tool.tool_calls[0]['args']['query']
                if function_name =="other":
                    response, id_problem = self.call_function_by_name(function_name=function_name, args=function_args)
                else:
                    prompt_problem, id_problem = self.call_function_by_name(selected_tool.tool_calls[0]['name'], 
                                                                selected_tool.tool_calls[0]['args']['query'])
                    response = self.handle_problem(prompt_problem, chat_history)
                logger.debug(f"Response from LLM after identifying the problem: {response}")

                langfuse_context.update_current_trace(
                    tags=[id_problem]
                )

            except Exception as e:
                response = selected_tool.content
            return response
        except Exception as e:
            logger.error(f"Cannot get the answer from api. Error: {e}")
            return "Xin lỗi em chưa hiểu câu hỏi của anh/chị, anh/chị có thể giải thích thêm (hoặc liên hệ với bộ phần CX) giúp em được không ạ?"