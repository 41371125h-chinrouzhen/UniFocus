import streamlit as st
import components
import pandas as pd
import styles

def show():
    # 上方功能列
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.markdown("<h3 style='font-weight: 700;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        # 三個按鈕：因為 CSS 全局設定了 .stButton > button 為綠色，這裡直接使用即可
        # 為了美觀，我們用 columns 讓它們緊湊一點
        b1, b2, b3 = st.columns(3)
        b1.button("📥 匯入", help="匯入 PDF 課表", use_container_width=True)
        b2.button("🎨 設計", help="更換課表樣式", use_container_width=True)
        b3.button("⬇️ 下載", help="下載課表圖片", use_container_width=True)

    # 顯示課表
    components.html_card("本週課表", "📅", """
        <div style="text-align:center; color:#888; padding:50px; border: 2px dashed #ddd; border-radius:10px;">
            <p>目前尚無課表資料</p>
            <small>請點擊右上角「匯入」按鈕上傳 PDF</small>
        </div>
    """)
    # 如果有真實資料，可以使用 st.dataframe(st.session_state.schedule_data) 
    # 但要記得包在 components.interactive_card_container 裡面才會好看