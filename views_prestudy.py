import streamlit as st
import components

def show():
    c1, c2 = st.columns([1, 1])
    
    # 左側：設定
    with c1:
        with st.container():
            components.card_header("課程設定", "🔍")
            with st.container():
                st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
                st.selectbox("選擇課程", ["計算機概論", "資料結構", "網頁設計"])
                st.text_input("輸入主題", placeholder="例如：指標與陣列")
                st.write("")
                st.button("✨ 生成預習指南", type="primary", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    # 右側：AI 結果
    with c2:
        components.html_card("AI 學習指南", "📚", """
            <div style="color:#888; text-align:center; padding:50px;">
                👈 請先在左側設定課程<br>AI 將為您推薦影片與重點
            </div>
        """)