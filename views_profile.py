import streamlit as st
import components
import pandas as pd

def show():
    c_left, c_right = st.columns([1, 2.5])
    
    with c_left:
        with components.interactive_card_container("個人資料", "👤"):
            st.markdown(f"""
                <div style="width:100px; height:100px; background-color:#A89B93; border-radius:50%; margin:0 auto 20px auto; display:flex; justify-content:center; align-items:center; color:white; font-size:40px; font-weight:bold;">
                    {st.session_state.username[0].upper()}
                </div>
            """, unsafe_allow_html=True)
            new_name = st.text_input("暱稱", value=st.session_state.username)
            if new_name != st.session_state.username:
                st.session_state.username = new_name
            st.text_input("學號", value=st.session_state.get('username', ''), disabled=True)
            st.write("")
            if st.button("登出", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

    with c_right:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            # === 真實課表預覽 ===
            preview_html = "<div style='color:#ccc; text-align:center; padding:20px;'>無課表資料</div>"
            if not st.session_state.schedule_data.empty:
                # 取前 3 筆顯示
                top3 = st.session_state.schedule_data.head(3)
                rows = ""
                for _, row in top3.iterrows():
                    rows += f"<li style='margin-bottom:5px;'><strong>{row['活動名稱']}</strong> <span style='font-size:0.8em; color:#888'>({row['星期']})</span></li>"
                preview_html = f"<ul style='padding-left:20px; color:#555;'>{rows}</ul>"
                
            components.html_card("課表預覽", "📅", preview_html)
            
        with r1_c2:
            components.html_card("最近記錄", "🕒", "<ul style='padding-left:20px; color:#555;'><li>計算機概論重點整理</li><li>資料結構思維導圖</li></ul>")
            
        components.html_card("網站使用統計", "📊", "本週已累積學習：<strong>12 小時</strong> <span style='color:green;'>(+5%)</span>")