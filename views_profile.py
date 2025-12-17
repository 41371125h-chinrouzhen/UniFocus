import streamlit as st
import components

def show():
    # 版面配置
    c_left, c_right = st.columns([1, 2.5])
    
    with c_left:
        # 個人資料卡 (使用 interactive_card_container 修復報錯)
        with components.interactive_card_container("個人資料", "👤"):
            st.markdown(f"""
                <div style="width:100px; height:100px; background-color:#A89B93; border-radius:50%; margin:0 auto 20px auto; display:flex; justify-content:center; align-items:center; color:white; font-size:40px; font-weight:bold;">
                    {st.session_state.username[0].upper()}
                </div>
            """, unsafe_allow_html=True)
            
            new_name = st.text_input("暱稱", value=st.session_state.username)
            if new_name != st.session_state.username:
                st.session_state.username = new_name
                st.rerun()
                
            st.text_input("學號", value=st.session_state.get('username', ''), disabled=True)
            
            st.write("")
            if st.button("登出系統", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

    with c_right:
        # 這裡保持使用 HTML 卡片，因為只是展示資訊
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            components.html_card("課表預覽", "📅", "<div style='height:150px; background:#f9f9f9; display:flex; align-items:center; justify-content:center; color:#aaa;'>Mini Schedule</div>")
        with r1_c2:
            components.html_card("最近記錄", "🕒", "<ul style='padding-left:20px; color:#555;'><li>計算機概論筆記 (2小時前)</li><li>英文聽力練習 (昨天)</li></ul>")
            
        components.html_card("網站使用統計", "📊", "本週專注時數：<strong>12 小時 30 分鐘</strong>")