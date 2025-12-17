import streamlit as st
import components
import pandas as pd
import datetime

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
            if new_name != st.session_state.username: st.session_state.username = new_name
            st.text_input("學號", value=st.session_state.get('username', ''), disabled=True)
            st.write("")
            if st.button("登出", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

    with c_right:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            # === 真實課表預覽 (今日課程) ===
            now = datetime.datetime.now()
            weekday_map = {0: '一', 1: '二', 2: '三', 3: '四', 4: '五', 5: '六', 6: '日'}
            today_week = weekday_map[now.weekday()]
            
            preview_html = f"<div style='color:#ccc; text-align:center; padding:20px;'>今天 ({today_week}) 無課程</div>"
            
            if not st.session_state.schedule_data.empty:
                df = st.session_state.schedule_data
                # 篩選今天的課
                today_courses = df[df['星期'] == today_week]
                
                if not today_courses.empty:
                    # 排序節次 (簡單字串排序，可優化)
                    today_courses = today_courses.sort_values('時間/節次')
                    rows = ""
                    for _, row in today_courses.iterrows():
                        rows += f"<li style='margin-bottom:8px; display:flex; justify-content:space-between;'><span><strong>{row['活動名稱']}</strong></span> <span style='font-size:0.8em; color:#6B8E78; background:#E8F3EB; padding:2px 6px; border-radius:10px;'>第 {row['時間/節次']} 節</span></li>"
                    preview_html = f"<ul style='padding-left:0; list-style-type:none; color:#555;'>{rows}</ul>"
            
            components.html_card("今日課表預覽", "📅", preview_html)
            
        with r1_c2:
            components.html_card("最近記錄", "🕒", "<ul style='padding-left:20px; color:#555;'><li>計算機概論重點整理</li><li>資料結構思維導圖</li></ul>")
            
        components.html_card("網站使用統計", "📊", "本週已累積學習：<strong>12 小時</strong> <span style='color:green;'>(+5%)</span>")