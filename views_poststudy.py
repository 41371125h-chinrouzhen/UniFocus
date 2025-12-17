import streamlit as st
import components

def show():
    st.markdown("<h3 style='font-weight: 700;'>課後總整</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        with st.container():
            components.card_header("筆記整理", "📝")
            with st.container():
                st.markdown('<div style="padding:15px;">', unsafe_allow_html=True)
                st.text_area("輸入原始筆記", height=200)
                st.button("整理重點", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        with st.container():
            components.card_header("思維導圖", "🧠")
            with st.container():
                st.markdown('<div style="padding:15px; text-align:center; height:200px; display:flex; align-items:center; justify-content:center; background:#f9f9f9;">圖表預覽區</div>', unsafe_allow_html=True)
                st.button("生成導圖", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        components.html_card("AI 助教", "🤖", """
            <p>有問題嗎？隨時問我！</p>
            <div style="background:#eee; padding:10px; border-radius:8px; margin-bottom:10px;">
                同學，這週的作業重點在於...
            </div>
        """)