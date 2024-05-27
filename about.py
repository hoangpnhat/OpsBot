import streamlit as st

def about_chatbot247():
    with st.sidebar:
        col1, col2, = st.columns([1,2], gap="medium")
        with col1:
            st.image('Logo-Yody-Slogan-Yellow.webp', width=75)
        with col2:
            st.write(""" 
            Xin chào! Em là chatbot điều phối hỗ trợ cho nhân viên của YODY.
                    
            Anh/chị có thể hỏi em về các vấn đề mà anh/chị đang gặp phải.
            """)

        col1, col2, col3, col4, col5, col6 = st.columns([1.1,1,1,1,1,1.5], gap="medium")
def about_salebot():
    with st.sidebar:
        col1, col2, = st.columns([1,2], gap="medium")
        with col1:
            st.image('Logo-Yody-Slogan-Yellow.webp', width=75)
        with col2:
            st.write(""" 
            Xin chào! Em là chatbot hỗ trợ mua hàng của YODY.
                    
            Anh/chị có thể hỏi em về các mặt hàng mà anh/chị đang quan tâm.
            """)

        col1, col2, col3, col4, col5, col6 = st.columns([1.1,1,1,1,1,1.5], gap="medium")
  
     


