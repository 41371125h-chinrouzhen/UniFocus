import streamlit as st
import styles
import data_manager
import pandas as pd
import time

def show():
    # 使用空白佔位讓內容垂直置中
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        # 1. 標題
        st.markdown('<div class="login-title">UNIFOCUS</div>', unsafe_allow_html=True)
        
        # 2. 登入卡片
        with st.container():
            # 卡片樣式
            st.markdown(f"""
                <div style="background-color:rgba(255,255,255,0.9); padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.1); backdrop-filter: blur(10px); text-align:center;">
                    <h3 style="color:{styles.COLOR_MAIN}; margin-bottom:20px;">🌿 智慧學習導航系統</h3>
                    <p style="color:#888; margin-bottom:30px;">請輸入您的學號以開始</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 輸入框
            uid = st.text_input("學號", placeholder="Enter Student ID", label_visibility="collapsed")
            
            st.write("") # 間距
            
            # 按鈕邏輯
            if st.button("登入 Login", use_container_width=True):
                if uid:
                    st.session_state.username = uid
                    
                    # === 關鍵修改：登入時去 Google Sheets 撈資料 ===
                    with st.spinner("正在連線雲端資料庫..."):
                        # 呼叫載入函式
                        df, msg = data_manager.load_user_data(uid)
                        
                        if df is not None and not df.empty:
                            # 如果雲端有資料，就存入 Session State
                            st.session_state.schedule_data = df
                            st.toast("歡迎回來！已為您載入雲端課表", icon="☁️")
                        else:
                            # 如果是新用戶或雲端沒資料，就給一個空的
                            st.session_state.schedule_data = pd.DataFrame()
                            st.toast("歡迎新朋友！請前往匯入課表", icon="👋")
                            
                        time.sleep(1) # 稍等一下讓使用者看到提示
                    
                    # 設定登入狀態並跳轉
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("請輸入學號")