import streamlit as st
import os
from tools import material_warranty,update_customer_info,administrate_order,promotions,promotions,personnel,other
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts.chat import SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage
from prompts import system_prompt
from langchain_openai import ChatOpenAI
import json
from about import about_chatbot247
if not os.path.exists('history_conversation'):
    os.makedirs('history_conversation')

def call_function_by_name(function_name, args):
    # Retrieve the function object from globals based on the function name
    func = globals()[function_name]
    # Call the function with unpacked arguments
    return func(args)
tools =[material_warranty,update_customer_info,administrate_order,promotions,personnel,other]
# Function to save session to a file
def save_session(session_id, chat_history):
    # Convert HumanMessage objects to dictionaries for serialization
    serializable_chat_history = [
        {"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) else {"type": "system", "content": msg}
        for msg in chat_history
    ]
    with open(f"history_conversation/session_{session_id}.json", 'w', encoding='utf-8') as f:
        json.dump(serializable_chat_history, f, ensure_ascii=False, indent=4)

# Function to load session from a file
def load_session(session_id):
    file_path = f"history_conversation/session_{session_id}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_chat_history = json.load(f)
            # Convert dictionaries back to HumanMessage objects where appropriate
            return [
                HumanMessage(content=msg['content']) if msg['type'] == "human" else msg['content']
                for msg in loaded_chat_history
            ]
    return []

# Function to delete session file
def delete_session(session_id):
    file_path = f"history_conversation/session_{session_id}.json"
    if os.path.exists(file_path):
        os.remove(file_path)

prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = ChatOpenAI(model="gpt-3.5-turbo-0125",temperature=0,api_key=st.secrets["OPENAI_API_KEY"])
llm_with_tools = llm.bind_tools(tools)
chain_for_tool = prompt_template | llm_with_tools

st.set_page_config(
    page_title="DEMO CHATBOT247",
    layout="wide",
)
st.title("DEMO CHATBOT247")
with st.sidebar:
    about_chatbot247()
    st.write('  ') 
    st.markdown("""---""")
# Initialize session state for chat history and sessions
if 'sessions' not in st.session_state:
    st.session_state['sessions'] = {}
if 'current_session' not in st.session_state:
    st.session_state['current_session'] = None

existing_sessions = [int(f.split('_')[1].split('.')[0]) for f in os.listdir('history_conversation') if f.startswith('session_') and f.endswith('.json')]
for session_id in existing_sessions:
    if session_id not in st.session_state['sessions']:
        st.session_state['sessions'][session_id] = load_session(session_id)

# Automatically create a new session if there is no active session
if st.session_state['current_session'] is None:
    session_id = max(st.session_state['sessions'].keys(), default=0) + 1
    st.session_state['sessions'][session_id] = []
    st.session_state['current_session'] = session_id
# Sidebar for managing sessions
st.sidebar.title("Chat Sessions")
new_session_button = st.sidebar.button("New Session")

# Create a new session
if new_session_button:
    session_id = max(st.session_state['sessions'].keys(), default=0) + 1
    st.session_state['sessions'][session_id] = []
    st.session_state['current_session'] = session_id

# Display existing sessions in the sidebar
for session_id in list(st.session_state['sessions'].keys()):
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if st.button(f"Session {session_id}", key=f"select_{session_id}"):
            st.session_state['current_session'] = session_id
    with col2:
        if st.button("❌", key=f"delete_{session_id}"):
            # Delete the session
            del st.session_state['sessions'][session_id]
            delete_session(session_id)
            # If the deleted session was the current session, reset current session
            if st.session_state['current_session'] == session_id:
                st.session_state['current_session'] = None
                st.rerun()

# if selected_session:
#     st.session_state['current_session'] = selected_session

# Get the current chat history
current_session_id = st.session_state['current_session']
if current_session_id:
    chat_history = st.session_state['sessions'][current_session_id]
else:
    chat_history = []
st.header("Lịch sử chat")

# Display chat history
for message in chat_history:
    if isinstance(message, HumanMessage):
        col1, col2 = st.columns([1, 3])  # User messages right aligned
        with col2:
            st.info(f"{message.content}")
            # st.chat_message("user").write(message.content)
            
            
    else:  # Bot's messages left aligned
        col1, col2 = st.columns([3, 1])
        with col1:
            # st.success(message)
            st.chat_message("assistant").write(message)

# Define the UI elements for user input
if user_input := st.chat_input("Hỗ trợ đổi số điện thoại khách hàng"):

    # Gửi truy vấn đến agent và nhận phản hồi
    # import pdb; pdb.set_trace()
    selected_tool = chain_for_tool.invoke({"input": user_input,
            "chat_history":chat_history,
            "agent_scratchpad":[]})
    try:
        prompt_problems = call_function_by_name(selected_tool.tool_calls[0]['name'], selected_tool.tool_calls[0]['args']['query'])
        chain = prompt_problems | llm
        response = chain.invoke({"chat_history": chat_history,"agent_scratchpad":[]})
    except:
        response = selected_tool
    # Save the question and response to the chat history
    chat_history.extend([
        HumanMessage(content=user_input),
        response.content
    ])

    st.session_state['sessions'][current_session_id] = chat_history
    save_session(current_session_id, chat_history)
    
    st.rerun()
    
