import streamlit as st
import components

def show():
    st.markdown("<h3 style='font-weight: 700;'>課前預習</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        with components.interactive_card_container("課程設定", "🔍"):
            st.selectbox("課程", ["計算機概論", "資料結構"])
            st.text_input("主題", placeholder="例如：指標")
            st.write("")
            st.button("✨ 生成指南", use_container_width=True)
    
    with c2:
        # 改用互動容器
        with components.interactive_card_container("AI 學習指南", "📚"):
            st.markdown("""
                <div style="text-align:center; color:#888; padding:50px;">
                    <p>請在左側設定課程<br>AI 將為您推薦影片與重點</p>
                </div>
            """, unsafe_allow_html=True)