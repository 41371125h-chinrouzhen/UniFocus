import streamlit as st
import datetime
import components

def show():
    # 頂部資訊
    c_title, c_info = st.columns([1, 1])
    with c_title:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>首頁 Dashboard</h3>", unsafe_allow_html=True)
    with c_info:
        now = datetime.datetime.now()
        st.markdown(f"""
            <div style="text-align:right;">
                <span class="dashboard-info">📅 {now.strftime("%Y-%m-%d %H:%M")} | 🌡️ 台北 24°C</span>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_left, col_right = st.columns([1.5, 1])

    # === 左側 ===
    with col_left:
        # 1. 今日動態 (改用互動容器)
        with components.interactive_card_container("今日動態", "🗓️"):
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            st.markdown(f"""
                <p style="color:#666; margin-bottom:10px;">Let's go! 今天是 {today_str}</p>
                <ul style="padding-left:20px; line-height:1.8; color:#333;">
                    <li><strong>09:00</strong> - 計算機概論</li>
                    <li><strong>13:00</strong> - 資料結構</li>
                </ul>
            """, unsafe_allow_html=True)

        # 2. 專注計時器
        with components.interactive_card_container("專注計時器", "⏱️"):
            c1, c2 = st.columns([2, 1])
            with c1: minutes = st.number_input("專注時間 (分)", 5, 120, 25, step=5)
            with c2: 
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("開始", use_container_width=True):
                    st.toast(f"開始 {minutes} 分鐘！", icon="🔥")
            st.markdown("<div style='text-align:center; color:#999; font-size:0.8em; margin-top:10px;'>保持專注</div>", unsafe_allow_html=True)

    # === 右側 ===
    with col_right:
        # 3. 學分 (改用互動容器)
        with components.interactive_card_container("本學期學分", "🎓"):
            credits = st.session_state.get('calculated_credits', 18)
            st.markdown(f"""
                <div style="text-align:center; padding:10px 0;">
                    <div style="font-size:4rem; font-weight:bold; color:#6B8E78; line-height:1;">{credits}</div>
                    <div style="color:#999; margin-top:5px;">AI 自動估算</div>
                </div>
            """, unsafe_allow_html=True)

        # 4. 倒數日
        with components.interactive_card_container("倒數日", "⏳"):
            target_name = st.text_input("目標", value=st.session_state.get('exam_name', '期中考'))
            target_date = st.date_input("日期", value=st.session_state.get('exam_date', datetime.date.today()))
            days = (target_date - datetime.date.today()).days
            
            # 更新狀態
            st.session_state.exam_name = target_name
            st.session_state.exam_date = target_date
            
            color = "#E67E22" if days >= 0 else "#999"
            label = "天" if days >= 0 else "已結束"
            st.markdown(f"""
                <div style="text-align:center; margin-top:10px; background:#FFF9F0; padding:10px; border-radius:8px;">
                    <span style="font-size:2.5rem; font-weight:bold; color:{color};">{abs(days)}</span>
                    <span style="color:{color};">{label}</span>
                </div>
            """, unsafe_allow_html=True)