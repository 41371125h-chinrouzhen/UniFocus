import streamlit as st
import datetime
import components

def show():
    # 1. 頂部標題與資訊欄
    c_title, c_info = st.columns([1, 1])
    
    with c_title:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>首頁 Dashboard</h3>", unsafe_allow_html=True)
    
    with c_info:
        # 取得現在時間
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        # 靠右顯示時間與溫度
        st.markdown(f"""
            <div style="text-align:right;">
                <span class="dashboard-info">
                    📅 {date_str} {time_str} &nbsp;|&nbsp; 🌡️ 台北 24°C
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.write("") # 間距

    # 2. 左右兩欄佈局
    col_left, col_right = st.columns([1.5, 1])

    # === 左側欄位 ===
    with col_left:
        # A. 今日動態 (HTML 卡片)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        components.html_card("今日動態", "🗓️", f"""
            <p style="color:#666;">今天是 {today_str} (週三)</p>
            <ul style="padding-left:20px; line-height:1.8; color:#333;">
                <li><strong>09:00</strong> - 計算機概論 (誠201)</li>
                <li><strong>13:00</strong> - 資料結構 (公館校區)</li>
                <li><strong>16:00</strong> - 社團會議</li>
            </ul>
        """)
        
        # B. 專注計時器 (互動卡片)
        with components.interactive_card_container("專注計時器", "⏱️"):
            c1, c2 = st.columns([2, 1])
            with c1:
                minutes = st.number_input("設定專注時間 (分鐘)", min_value=5, value=25, step=5)
            with c2:
                st.markdown("<br>", unsafe_allow_html=True) # 對齊按鈕
                if st.button("開始", use_container_width=True):
                    st.toast(f"開始 {minutes} 分鐘專注！加油！", icon="🔥")
            st.markdown("<div style='color:#888; font-size:0.9em; margin-top:10px;'>保持專注，遠離手機 📱</div>", unsafe_allow_html=True)

    # === 右側欄位 ===
    with col_right:
        # C. 本學期學分 (HTML 卡片)
        credits = st.session_state.get('calculated_credits', 18)
        components.html_card("本學期學分", "🎓", f"""
            <div style="text-align:center; padding:10px 0;">
                <div style="font-size:4rem; font-weight:bold; color:#6B8E78; line-height:1;">{credits}</div>
                <div style="color:#999; margin-top:5px;">AI 自動估算</div>
            </div>
        """)

        # D. 倒數日 (互動卡片)
        with components.interactive_card_container("倒數日", "⏳"):
            target_name = st.text_input("目標名稱", value=st.session_state.get('exam_name', '期中考'))
            target_date = st.date_input("目標日期", value=st.session_state.get('exam_date', datetime.date.today()))
            
            # 更新狀態
            st.session_state.exam_name = target_name
            st.session_state.exam_date = target_date
            
            days = (target_date - datetime.date.today()).days
            display_days = abs(days)
            color = "#E67E22" if days >= 0 else "#999"
            label = "天" if days >= 0 else "天 (已結束)"
            
            st.markdown(f"""
                <div style="text-align:center; margin-top:10px; padding:10px; background:#FFF9F0; border-radius:10px;">
                    <span style="font-size:2.5rem; font-weight:bold; color:{color};">{display_days}</span>
                    <span style="color:{color};">{label}</span>
                </div>
            """, unsafe_allow_html=True)