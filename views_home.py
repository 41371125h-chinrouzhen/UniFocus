import streamlit as st
import datetime
import components
import requests
import ai_logic
import data_manager
import time

# --- 取得天氣資料 ---
def get_real_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current=temperature_2m,weather_code&timezone=Asia%2FShanghai"
        res = requests.get(url, timeout=3).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        
        weather_desc = "晴朗"
        if code in [1, 2, 3]: weather_desc = "多雲"
        elif code in [45, 48]: weather_desc = "有霧"
        elif code >= 51: weather_desc = "有雨"
        
        return temp, weather_desc
    except Exception:
        return 24, "未知"

# --- 主頁面顯示邏輯 ---
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

    st.write("") # 頂部間距

    # === 3. 三欄佈局 (左、中、右) ===
    # 調整比例：左欄稍窄(0.8)，中欄最寬(1.2)，右欄標準(1)
    c_left, c_mid, c_right = st.columns([0.8, 1.2, 1])

    # --- 【最左欄】：網站介紹 ---
    with c_left:
        with components.interactive_card_container("關於 Unifocus", "👋"):
            st.markdown("""
            <div style="color:#555; font-size:0.95rem; line-height:1.8;">
                <b>歡迎來到 Unifocus！</b><br>
                這是一個專為大學生設計的智慧學習導航系統。<br><br>
                ✨ <b>特色功能：</b>
                <ul style="padding-left:15px; margin-top:5px;">
                    <li><b>智慧課表</b>：一鍵匯入 PDF，AI 自動解析。</li>
                    <li><b>AI 助教</b>：課前預習、筆記整理、思維導圖。</li>
                    <li><b>專注工具</b>：番茄鐘與考試倒數。</li>
                </ul>
                <br>
                讓學習更有條理，從今天開始！
            </div>
            """, unsafe_allow_html=True)

    # --- 【中欄】：今日動態 + 計時器 ---
    with c_mid:
        # A. 今日動態
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
                <div style="background:#E8F3EB; padding:10px; border-radius:8px; margin-bottom:15px; color:#446E5C; font-weight:bold; font-size:0.95em;">
                    💡 {st.session_state.ai_weather_advice}
                </div>
                <p style="color:#666; margin-bottom:5px; font-size:0.9em;">今日行程 ({today_week})：</p>
            """, unsafe_allow_html=True)
            
            if today_courses_list:
                for c in today_courses_list:
                    st.markdown(f"- 📚 **{c}**")
            else:
                st.markdown("- 🌴 自由時間")

        # B. 專注計時器
        with components.interactive_card_container("專注計時器", "⏱️"):
            c1, c2 = st.columns([2, 1])
            with c1: 
                minutes = st.number_input("時間 (分)", 1, 120, 25, step=5, key="focus_min")
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

    # --- 【最右欄】：學分 + 倒數日 ---
    with c_right:
        # C. 學分
        with components.interactive_card_container("本學期學分", "🎓"):
            settings = data_manager.load_settings(st.session_state.username)
            if 'manual_credits' in settings:
                current_credits = int(settings['manual_credits'])
            else:
                current_credits = 0
                if not st.session_state.schedule_data.empty:
                    current_credits = len(st.session_state.schedule_data['活動名稱'].unique()) * 2
            
            new_credits = st.number_input("總學分", value=current_credits, step=1, label_visibility="collapsed")
            
            if new_credits != current_credits:
                data_manager.save_setting(st.session_state.username, 'manual_credits', str(new_credits))
                st.rerun()
            
            st.markdown(f"""
                <div style="text-align:center; padding:15px 0;">
                    <div style="font-size:3.5rem; font-weight:bold; color:#6B8E78; line-height:1.1;">{new_credits}</div>
                    <div style="color:#999; font-size:0.8rem;">預估學分</div>
                </div>
            """, unsafe_allow_html=True)

        # D. 倒數日
        with components.interactive_card_container("倒數日", "⏳"):
            if 'exam_name' not in st.session_state:
                settings = data_manager.load_settings(st.session_state.username)
                st.session_state.exam_name = settings.get('exam_name', '期中考')
                date_str = settings.get('exam_date', '2025-06-20')
                try:
                    st.session_state.exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                except:
                    st.session_state.exam_date = datetime.date.today()

            days = (st.session_state.exam_date - datetime.date.today()).days
            color = "#E67E22" if days >= 0 else "#999"
            
            # 調整佈局：天數在上，設定在下，更適合窄欄位
            st.markdown(f"""
                <div style="text-align:center; background:#FFF9F0; padding:10px; border-radius:8px; margin-bottom:10px;">
                    <span style="font-size:2.2rem; font-weight:bold; color:{color}; line-height:1;">{abs(days)}</span>
                    <span style="font-size:0.8rem; color:{color};">天</span>
                </div>
            """, unsafe_allow_html=True)
            
            new_name = st.text_input("目標", value=st.session_state.exam_name, label_visibility="collapsed", placeholder="目標名稱")
            new_date = st.date_input("日期", value=st.session_state.exam_date, label_visibility="collapsed")
            
            if new_name != st.session_state.exam_name or new_date != st.session_state.exam_date:
                st.session_state.exam_name = new_name
                st.session_state.exam_date = new_date
                data_manager.save_setting(st.session_state.username, 'exam_name', new_name)
                data_manager.save_setting(st.session_state.username, 'exam_date', str(new_date))
                st.rerun()
            
            # 底部微調
            st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)