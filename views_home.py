import streamlit as st
import datetime
import components

def show():
    st.markdown("<h3 style='font-weight: 700; margin-bottom: 20px;'>首頁 Dashboard</h3>", unsafe_allow_html=True)

    # 第一排
    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        # 天氣
        components.html_card("天氣預報", "🌤️", """
            <div style="display:flex; align-items:center; gap:15px;">
                <span style="font-size:3.5rem;">🌥️</span>
                <div>
                    <div style="font-size:2rem; font-weight:bold;">24°C</div>
                    <div style="color:#666;">台北市，多雲</div>
                </div>
            </div>
        """)
    with c2:
        # 今日動態
        today = datetime.date.today().strftime("%Y-%m-%d")
        components.html_card("今日動態", "🗓️", f"""
            <p>今天是 {today} (週三)</p>
            <ul style="padding-left:20px; color:#555;">
                <li>09:00 - 計算機概論</li>
                <li>13:00 - 資料結構</li>
            </ul>
        """)

    # 第二排
    c3, c4, c5 = st.columns([1.2, 1, 1.2])
    
    with c3: # 計時器
        with st.container():
            components.card_header("專注計時器", "⏱️")
            with st.container():
                st.markdown('<div style="padding:15px;">', unsafe_allow_html=True)
                t = st.number_input("分鐘", 1, 120, 25, label_visibility="collapsed")
                st.button("開始專注", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with c4: # 學分
        components.html_card("本學期學分", "🎓", f"""
            <div style="text-align:center; padding:10px;">
                <h1 style="font-size:3.5rem; color:#6B8E78; margin:0;">{st.session_state.get('calculated_credits', 18)}</h1>
                <small style="color:#999;">AI 自動估算</small>
            </div>
        """)

    with c5: # 倒數
        with st.container():
            components.card_header("倒數日", "⏳")
            with st.container():
                st.markdown('<div style="padding:15px;">', unsafe_allow_html=True)
                target = st.text_input("目標", value="期中考", label_visibility="collapsed")
                days = 10 # 模擬數據
                st.markdown(f"<h2 style='text-align:center; color:#E67E22; margin:10px 0;'>{days} 天</h2>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)