import streamlit as st
import datetime
import pandas as pd

# 引入我們拆分好的模組
import styles
import components
import views_home
import data_manager 
import ai_logic

# --- 1. 設定與初始化 ---
st.set_page_config(
    page_title="UNIFOCUS | 智慧學習導航",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# 初始化 Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = "JHi"
if 'page' not in st.session_state: st.session_state.page = "首頁"
if 'schedule_data' not in st.session_state: st.session_state.schedule_data = pd.DataFrame()
if 'calculated_credits' not in st.session_state: st.session_state.calculated_credits = 18

# --- 2. 載入視覺樣式 ---
styles.load_css()

# --- 3. 顯示導航列 ---
components.render_navbar()

# --- 4. 頁面路由 (Router) ---
# 這裡決定要顯示哪一個頁面的内容
if st.session_state.page == "首頁":
    views_home.show()

elif st.session_state.page == "我的課表":
    st.title("我的課表")
    st.info("🚧 開發中，請稍候...")
    # 未來建立 views_schedule.py 後，這裡改成 views_schedule.show()

elif st.session_state.page == "課前預習":
    st.title("課前預習")
    st.info("🚧 開發中，請稍候...")

elif st.session_state.page == "課後總整":
    st.title("課後總整")
    st.info("🚧 開發中，請稍候...")

elif st.session_state.page == "個人主頁":
    st.title("個人主頁")
    st.info("🚧 開發中，請稍候...")
