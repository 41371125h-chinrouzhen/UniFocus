import streamlit as st
import datetime
import components
import requests
import time
import ai_logic
import data_manager

# 取得天氣資料 (Open-Meteo 免費 API)
def get_real_weather():
    try:
        # 台北座標
        url = "https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current=temperature_2m,weather_code&timezone=Asia%2FShanghai"
        res = requests.get(url).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        
        # 簡單的天氣代碼轉換
        weather_desc = "晴朗"
        if code in [1, 2, 3]: weather_desc = "多雲"
        elif code in [45, 48]: weather_desc = "有霧"
        elif code >= 51: weather_desc = "有雨"
        
        return temp, weather_desc
    except:
        return 24, "未知" # 備用

def show():
    # 1. 取得即時資訊
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    temp, weather_desc = get_real_weather()
    
    # 2. 頂部標題
    c_title, c_info = st.columns([1, 1])
    with c_title:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>首頁 Dashboard</h3>", unsafe_allow_html=True)
    with c_info:
        st.markdown(f"""
            <div style="text-align:right;">
                <span class="dashboard-info">
                    📅 {date_str} {time_str} &nbsp;|&nbsp; 🌡️ 台北 {temp}°C ({weather_desc})
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_left, col_right = st.columns([1.5, 1])

    # === 左側 ===
    with col_left:
        # A. 今日動態 + AI 提醒
        with components.interactive_card_container("今日動態", "🗓️"):
            # 1. 找出今天的課
            weekday_map = {0: '一', 1: '二', 2: '三', 3: '四', 4: '五', 5: '六', 6: '日'}
            today_week = weekday_map[now.weekday()]
            
            today_courses = []
            if not st.session_state.schedule_data.empty:
                df = st.session_state.schedule_data
                today_courses = df[df['星期'] == today_week]['活動名稱'].tolist()
            
            course_text = "、".join(today_courses) if today_courses else "今日無排定課程"

            # 2. AI 溫馨提醒 (存入 session 防止重整重複呼叫)
            if 'ai_weather_advice' not in st.session_state:
                with st.spinner("AI 正在觀察天氣..."):
                    advice = ai_logic.get_weather_advice(f"{temp}度 {weather_desc}", course_text)
                    st.session_state.ai_weather_advice = advice if advice else "天氣多變，注意保暖！"
            
            st.markdown(f"""
                <div style="background:#E8F3EB; padding:10px; border-radius:8px; margin-bottom:15px; color:#446E5C; font-weight:bold;">
                    💡 AI 貼心提醒：{st.session_state.ai_weather_advice}
                </div>
                <p style="color:#666; margin-bottom:5px;">今日行程 ({today_week})：</p>
            """, unsafe_allow_html=True)
            
            if today_courses:
                for c in today_courses:
                    st.markdown(f"- 📚 **{c}**")
            else:
                st.markdown("- 🌴 自由時間")

        # B. 真實專注計時器
        with components.interactive_card_container("專注計時器", "⏱️"):
            c1, c2 = st.columns([2, 1])
            with c1: 
                minutes = st.number_input("時間 (分)", 1, 120, 25, step=5, key="focus_min")
            with c2: 
                st.markdown("<br>", unsafe_allow_html=True)
                start_btn = st.button("開始", use_container_width=True)
            
            # 計時邏輯
            timer_ph = st.empty()
            if start_btn:
                total_sec = minutes * 60
                bar = st.progress(0)
                for i in range(total_sec):
                    left = total_sec - i
                    mins, secs = divmod(left, 60)
                    timer_ph.markdown(f"<h2 style='text-align:center; color:#E67E22;'>{mins:02d}:{secs:02d}</h2>", unsafe_allow_html=True)
                    bar.progress((i + 1) / total_sec)
                    time.sleep(1) # 真實等待
                timer_ph.markdown("<h2 style='text-align:center; color:#6B8E78;'>完成！🎉</h2>", unsafe_allow_html=True)
                st.balloons()

    # === 右側 ===
    with col_right:
        # C. 學分
        with components.interactive_card_container("本學期學分", "🎓"):
            credits = 0
            if not st.session_state.schedule_data.empty:
                # 簡單估算：一堂課算 1 學分 (可優化邏輯)
                credits = len(st.session_state.schedule_data)
            
            st.markdown(f"""
                <div style="text-align:center; padding:10px 0;">
                    <div style="font-size:4rem; font-weight:bold; color:#6B8E78; line-height:1;">{credits}</div>
                    <div style="color:#999; margin-top:5px;">課程總數估算</div>
                </div>
            """, unsafe_allow_html=True)

        # D. 倒數日 (新 UI + 存檔)
        with components.interactive_card_container("倒數日", "⏳"):
            # 讀取設定 (如果還沒讀過)
            if 'exam_name' not in st.session_state:
                settings = data_manager.load_settings(st.session_state.username)
                st.session_state.exam_name = settings.get('exam_name', '期中考')
                st.session_state.exam_date = datetime.datetime.strptime(settings.get('exam_date', '2025-06-20'), "%Y-%m-%d").date()

            # 新 UI: 左邊天數，右邊設定
            cd_col1, cd_col2 = st.columns([1, 1.5])
            
            days = (st.session_state.exam_date - datetime.date.today()).days
            color = "#E67E22" if days >= 0 else "#999"
            
            with cd_col1:
                st.markdown(f"""
                    <div style="text-align:center; background:#FFF9F0; padding:15px 5px; border-radius:8px; height:100%;">
                        <div style="font-size:2.5rem; font-weight:bold; color:{color}; line-height:1;">{abs(days)}</div>
                        <div style="font-size:0.8rem; color:{color};">天</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with cd_col2:
                new_name = st.text_input("目標", value=st.session_state.exam_name, label_visibility="collapsed")
                new_date = st.date_input("日期", value=st.session_state.exam_date, label_visibility="collapsed")
                
                # 存檔邏輯
                if new_name != st.session_state.exam_name or new_date != st.session_state.exam_date:
                    st.session_state.exam_name = new_name
                    st.session_state.exam_date = new_date
                    # 寫入資料庫
                    data_manager.save_setting(st.session_state.username, 'exam_name', new_name)
                    data_manager.save_setting(st.session_state.username, 'exam_date', str(new_date))
                    st.rerun()