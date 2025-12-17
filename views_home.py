import streamlit as st
import datetime
import components # 引入上面的元件

def show():
    st.markdown("<h2 style='font-weight: 700; margin-bottom: 25px;'>首頁</h2>", unsafe_allow_html=True)

    # === 第一排：天氣 + 今日動態 ===
    row1_col1, row1_col2 = st.columns([1.5, 2.5])

    with row1_col1:
        # 天氣卡片内容
        weather_content = """
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 4rem;">🌥️</span>
                <div>
                    <div class="weather-temp">24°C</div>
                    <div style="color: #666; font-size: 0.9rem;">台北市，多雲時晴</div>
                </div>
            </div>
        """
        components.card_html("天氣預報", "🌤️", weather_content)

    with row1_col2:
        # 今日動態内容
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        activity_content = f"""
            <p style="font-weight: 500; margin-bottom: 10px;">Let's go! 今天是 {today_str}</p>
            <ul style="list-style-type: none; padding: 0; color: #333;">
                <li style="padding:5px 0">- [09:00] 計算機概論 (誠201)</li>
                <li style="padding:5px 0">- [13:00] 資料結構 (公館校區)</li>
            </ul>
        """
        components.card_html("今日動態", "🗓️", activity_content)

    # === 第二排：計時器 + 學分 + 倒數 ===
    st.write("") 
    r2_c1, r2_c2, r2_c3 = st.columns([1.2, 1, 1.2])

    # 1. 專注計時器
    with r2_c1:
        with st.container():
            components.card_interactive_header("專注計時器", "⏱️")
            with st.container():
                st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)
                minutes = st.number_input("設定分鐘", min_value=1, value=25, step=5)
                st.write("")
                if st.button("開始專注"):
                    st.toast(f"開始 {minutes} 分鐘專注！", icon="🔥")
                st.markdown('</div>', unsafe_allow_html=True)

    # 2. 本學期學分
    with r2_c2:
        credits = st.session_state.get('calculated_credits', 0)
        credit_content = f"""
            <div style="display: flex; flex-direction: column; justify-content: center; height: 180px;">
                <div class="credit-number">{credits}</div>
                <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 5px;">AI 自動估算</div>
            </div>
        """
        components.card_html("本學期學分", "🎓", credit_content)

    # 3. 重要日倒數
    with r2_c3:
        with st.container():
            components.card_interactive_header("重要日倒數", "⏳")
            with st.container():
                st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)
                new_name = st.text_input("目標名稱", value=st.session_state.get('exam_name', '期中考'))
                new_date = st.date_input("目標日期", value=st.session_state.get('exam_date', datetime.date.today()))
                
                # 簡單的狀態更新
                if new_name != st.session_state.get('exam_name'):
                    st.session_state.exam_name = new_name
                if new_date != st.session_state.get('exam_date'):
                    st.session_state.exam_date = new_date

                days_left = (new_date - datetime.date.today()).days
                st.markdown(f"""
                    <div style="text-align: center; margin-top: 15px;">
                        <span class="countdown-number">{abs(days_left)}</span>
                        <span style="color: #E67E22; font-size: 1.2rem; margin-left: 5px;">天</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)