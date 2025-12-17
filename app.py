import streamlit as st
import pandas as pd

# MVC
import styles
import components
import views_login
import views_home
import views_schedule
import views_prestudy
import views_poststudy
import views_profile
import data_manager

# --- 初始化設定 ---
st.set_page_config(page_title="UNIFOCUS", layout="wide", page_icon="🎓")

# Session State 初始化
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'page' not in st.session_state: st.session_state.page = "首頁"
if 'schedule_data' not in st.session_state: st.session_state.schedule_data = pd.DataFrame()

# 載入 CSS
styles.load_css()

# --- 路由邏輯 (Router) ---

if not st.session_state.logged_in:
    # 顯示登入畫面
    views_login.show()
else:
    # 顯示導航列
    components.render_navbar()
    
    # 頁面切換
    if st.session_state.page == "首頁":
        views_home.show()
    elif st.session_state.page == "我的課表":
        views_schedule.show()
    elif st.session_state.page == "課前預習":
        views_prestudy.show()
    elif st.session_state.page == "課後總整":
        views_poststudy.show()
    elif st.session_state.page == "個人主頁":
        views_profile.show()
