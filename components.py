import streamlit as st
import styles

def render_navbar():
    """渲染功能性導航列 (使用 st.columns 模擬)"""
    # 建立一個容器，加上底線樣式
    st.markdown(f"""
        <style>
        .nav-container {{
            padding: 15px 0;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    col_logo, col_nav, col_user = st.columns([2, 5, 1])
    
    with col_logo:
        st.markdown(f"<h3 style='color:{styles.COLOR_TEXT}; margin:0; display:flex; align-items:center;'><span style='color:{styles.COLOR_MAIN}; font-size:1.5em; margin-right:5px;'>U</span> UNIFOCUS</h3>", unsafe_allow_html=True)
    
    with col_nav:
        # 使用 columns 放置按鈕，模擬橫向選單
        n1, n2, n3, n4, n5 = st.columns(5)
        pages = ["首頁", "我的課表", "課前預習", "課後總整", "個人主頁"]
        
        def nav_callback(page_name):
            st.session_state.page = page_name

        # 這裡我們用一點小技巧，根據當前頁面變更按鈕樣式 (Primary vs Secondary)
        current = st.session_state.get('page', '首頁')
        
        if n1.button("首頁", key="nav_home", type="primary" if current=="首頁" else "secondary", use_container_width=True): nav_callback("首頁")
        if n2.button("我的課表", key="nav_sch", type="primary" if current=="我的課表" else "secondary", use_container_width=True): nav_callback("我的課表")
        if n3.button("課前預習", key="nav_pre", type="primary" if current=="課前預習" else "secondary", use_container_width=True): nav_callback("課前預習")
        if n4.button("課後總整", key="nav_post", type="primary" if current=="課後總整" else "secondary", use_container_width=True): nav_callback("課後總整")
        if n5.button("個人主頁", key="nav_prof", type="primary" if current=="個人主頁" else "secondary", use_container_width=True): nav_callback("個人主頁")

    with col_user:
        username = st.session_state.get('username', 'Guest')
        first_letter = username[0].upper() if username else "G"
        st.markdown(f"""
            <div style="background-color:#A89B93; color:white; width:40px; height:40px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold; margin-left:auto;">
                {first_letter}
            </div>
        """, unsafe_allow_html=True)

def card_header(title, icon):
    """互動卡片的標題標記"""
    st.markdown(f'<div class="card-header card-marker"><span style="font-size: 1.2em;">{icon}</span> {title}</div>', unsafe_allow_html=True)

def html_card(title, icon, content):
    """純 HTML 卡片"""
    st.markdown(f"""
        <div class="html-card">
            <div class="card-header">
                <span style="font-size: 1.2em;">{icon}</span> {title}
            </div>
            <div class="card-body">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)
