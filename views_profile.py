import streamlit as st
import components

def show():
    c_left, c_right = st.columns([1, 2.5])
    
    with c_left:
        # 個人資料卡
        with st.container():
            components.card_header("個人資料", "👤")
            with st.container():
                st.markdown('<div style="padding:20px; text-align:center;">', unsafe_allow_html=True)
                # 頭像
                st.markdown(f"""
                    <div style="width:100px; height:100px; background-color:#A89B93; border-radius:50%; margin:0 auto 20px auto; display:flex; justify-content:center; align-items:center; color:white; font-size:40px; font-weight:bold;">
                        {st.session_state.username[0].upper()}
                    </div>
                """, unsafe_allow_html=True)
                st.text_input("暱稱", value=st.session_state.username)
                st.text_input("學號", value="41071125H", disabled=True)
                st.button("儲存設定", use_container_width=True)
                
                st.divider()
                if st.button("登出", type="secondary", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        # 小視窗預覽
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            components.html_card("課表預覽", "📅", "<div style='height:150px; background:#eee;'>Mini Schedule</div>")
        with r1_c2:
            components.html_card("最近記錄", "🕒", "<ul><li>計算機概論筆記 (2小時前)</li><li>英文聽力練習 (昨天)</li></ul>")
            
        components.html_card("網站使用統計", "📊", "本週專注時數：12 小時 30 分鐘")