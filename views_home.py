import streamlit as st
import datetime
import components
import requests
import ai_logic
import data_manager

def get_real_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current=temperature_2m,weather_code&timezone=Asia%2FShanghai"
        res = requests.get(url, timeout=2).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        weather_desc = "晴朗"
        if code in [1, 2, 3]: weather_desc = "多雲"
        elif code >= 51: weather_desc = "有雨"
        return temp, weather_desc
    except:
        return 24, "未知"

def show():
    # 1. 資訊
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    temp, weather_desc = get_real_weather()
    
    # 頂部佈局調整，讓標題跟資訊更緊湊
    c_title, c_info = st.columns([1, 1])
    with c_title: st.markdown("<h3 style='font-weight: 700; margin:0;'>首頁 Dashboard</h3>", unsafe_allow_html=True)
    with c_info:
        st.markdown(f"<div style='text-align:right;'><span class='dashboard-info'>📅 {date_str} {time_str} &nbsp;|&nbsp; 🌡️ 台北 {temp}°C ({weather_desc})</span></div>", unsafe_allow_html=True)

    st.write("")
    col_left, col_right = st.columns([1.5, 1])

    # === 左側 ===
    with col_left:
        # A. 新增：網站介紹卡片
        with components.interactive_card_container("關於 Unifocus", "👋"):
            st.markdown("""
            <div style="color:#555; font-size:0.95rem; line-height:1.6;">
                歡迎來到 <b>Unifocus 智慧學習導航系統</b>！<br>
                這裡整合了你的<b>課表管理</b>、<b>AI 學習助手</b>與<b>專注工具</b>。
                無論是課前預習、課後整理筆記，或是考試倒數，Unifocus 都能幫你輕鬆搞定，讓學習變得更有條理。
            </div>
            """, unsafe_allow_html=True)

        # B. 今日動態
        with components.interactive_card_container("今日動態", "🗓️"):
            weekday_map = {0: '一', 1: '二', 2: '三', 3: '四', 4: '五', 5: '六', 6: '日'}
            today_week = weekday_map[now.weekday()]
            
            today_courses_list = []
            if not st.session_state.schedule_data.empty:
                df = st.session_state.schedule_data
                today_df = df[df['星期'] == today_week]
                if not today_df.empty:
                    today_df = today_df.sort_values('時間/節次')
                    today_courses_list = today_df['活動名稱'].unique().tolist()
            
            course_text = "、".join(today_courses_list) if today_courses_list else "今日無排定課程"

            if 'ai_weather_advice' not in st.session_state:
                try:
                    advice = ai_logic.get_weather_advice(f"{temp}度 {weather_desc}", course_text)
                    st.session_state.ai_weather_advice = advice if advice else "天氣多變，注意保暖！"
                except:
                    st.session_state.ai_weather_advice = "系統連線忙碌，出門請注意安全！"
            
            st.markdown(f"""
                <div style="background:#E8F3EB; padding:10px; border-radius:8px; margin-bottom:15px; color:#446E5C; font-weight:bold;">
                    💡 AI 貼心提醒：{st.session_state.ai_weather_advice}
                </div>
                <p style="color:#666; margin-bottom:5px;">今日行程 ({today_week})：</p>
            """, unsafe_allow_html=True)
            
            if today_courses_list:
                for c in today_courses_list:
                    st.markdown(f"- 📚 **{c}**")
            else:
                st.markdown("- 🌴 自由時間")

        # C. 專注計時器
        with components.interactive_card_container("專注計時器", "⏱️"):
            c1, c2 = st.columns([2, 1])
            with c1: minutes = st.number_input("時間 (分)", 1, 120, 25, step=5, key="focus_min")
            with c2: 
                st.markdown("<br>", unsafe_allow_html=True)
                start_btn = st.button("開始", use_container_width=True)
            
            timer_ph = st.empty()
            if start_btn:
                total_sec = minutes * 60
                bar = st.progress(0)
                for i in range(total_sec):
                    left = total_sec - i
                    mins, secs = divmod(left, 60)
                    timer_ph.markdown(f"<h2 style='text-align:center; color:#E67E22;'>{mins:02d}:{secs:02d}</h2>", unsafe_allow_html=True)
                    bar.progress((i + 1) / total_sec)
                    time.sleep(1)
                timer_ph.markdown("<h2 style='text-align:center; color:#6B8E78;'>完成！🎉</h2>", unsafe_allow_html=True)
                st.balloons()

    # === 右側 ===
    with col_right:
        # D. 學分 (調整間距)
        with components.interactive_card_container("本學期學分", "🎓"):
            settings = data_manager.load_settings(st.session_state.username)
            if 'manual_credits' in settings:
                current_credits = int(settings['manual_credits'])
            else:
                current_credits = 0
                if not st.session_state.schedule_data.empty:
                    current_credits = len(st.session_state.schedule_data['活動名稱'].unique()) * 2
            
            new_credits = st.number_input("總學分 (可修正)", value=current_credits, step=1)
            
            if new_credits != current_credits:
                data_manager.save_setting(st.session_state.username, 'manual_credits', str(new_credits))
                st.rerun()
            
            st.markdown(f"""
                <div style="text-align:center; padding:10px 0;">
                    <div style="font-size:3.5rem; font-weight:bold; color:#6B8E78; line-height:1.2;">{new_credits}</div>
                </div>
                <div style="height:15px;"></div>
            """, unsafe_allow_html=True)

        # E. 倒數日 (調整間距)
        with components.interactive_card_container("倒數日", "⏳"):
            if 'exam_name' not in st.session_state:
                settings = data_manager.load_settings(st.session_state.username)
                st.session_state.exam_name = settings.get('exam_name', '期中考')
                st.session_state.exam_date = datetime.datetime.strptime(settings.get('exam_date', '2025-06-20'), "%Y-%m-%d