import streamlit as st
import components

def show():
    st.markdown("<h3 style='font-weight: 700;'>課前預習</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.2])
    
    # 左側：設定 (修復為卡片形式)
    with c1:
        with components.interactive_card_container("課程設定", "🔍"):
            st.selectbox("選擇課程", ["計算機概論", "資料結構", "網頁設計", "線性代數"])
            st.text_input("輸入預習主題", placeholder="例如：指標 (Pointers) 與記憶體")
            st.write("") # 增加一點間距
            st.button("✨ AI 生成預習指南", use_container_width=True)
            st.markdown("<small style='color:#888'>* AI 將為您推薦 YouTube 影片與核心觀念</small>", unsafe_allow_html=True)
    
    # 右側：AI 結果
    with c2:
        components.html_card("AI 學習指南", "📚", """
            <div style="color:#888; text-align:center; padding:60px; background:#f9f9f9; border-radius:8px;">
                <h4>👋 準備好開始預習了嗎？</h4>
                <p>請在左側選擇課程並輸入主題，<br>我將為您整理最好的學習資源。</p>
            </div>
        """)