import os
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from prompts import system_prompt
from langchain_openai import ChatOpenAI
from typing import List, Union
import sys
from dotenv import load_dotenv, find_dotenv
import logging

load_dotenv(find_dotenv(), override=True)

sys.path.append(os.getcwd())
from app.common.config import cfg
from app.chatbot.tools import material_warranty, update_customer_info,administrate_order, \
                                promotions,promotions,personnel,other


class Chatbot:
    def __init__(self, model=os.environ.get("OPENAI_MODEL"), temperature=0, api_key=None):
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.tools = [
            material_warranty, update_customer_info, administrate_order, 
            promotions, personnel, other
        ]
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature, api_key=self.api_key)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.prompt_template = self.setup_prompt_template()
        self.chain_for_tool = self.prompt_template | self.llm_with_tools

    @staticmethod
    def call_function_by_name(function_name, args):
        func = globals().get(function_name)
        if func:
            return func(args)
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

    def chat(self, chat_history: List[Union[HumanMessage, AIMessage]], user_input: str):
        logging.debug(f"User input: {user_input}")
        logging.debug(f"Chat history: {chat_history}")
        selected_tool =  self.chain_for_tool.invoke({
            "input": user_input, 
            "chat_history": chat_history, 
            "agent_scratchpad": []
        })
        logging.debug(f"Selected tool: {selected_tool}")
        try:
            get_prompt_problems = self.call_function_by_name(selected_tool.tool_calls[0]['name'], 
                                                         selected_tool.tool_calls[0]['args']['query'])
            chain = get_prompt_problems | self.llm
            response = chain.invoke({"chat_history": chat_history, "agent_scratchpad": []})
            logging.debug(f"Response from LLM after identifying the problem: {response}")
        except Exception as e:
            response = selected_tool
        return response.content