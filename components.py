import streamlit as st
import styles

def render_navbar():
    """渲染功能性導航列"""
    st.markdown("""
        <style>
        .nav-wrapper { margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)
    
    col_logo, col_nav, col_user = st.columns([2, 5, 1])
    
    with col_logo:
        st.markdown(f"<h3 style='color:{styles.COLOR_TEXT}; margin:0; display:flex; align-items:center;'><span style='color:{styles.COLOR_MAIN}; font-size:1.5em; margin-right:5px;'>U</span> UNIFOCUS</h3>", unsafe_allow_html=True)
    
    with col_nav:
        n1, n2, n3, n4, n5 = st.columns(5)
        
        def nav(page): st.session_state.page = page

        # 使用 CSS 類別來控制按鈕樣式 (由 styles.py 統一管理)
        if n1.button("首頁", use_container_width=True): nav("首頁")
        if n2.button("我的課表", use_container_width=True): nav("我的課表")
        if n3.button("課前預習", use_container_width=True): nav("課前預習")
        if n4.button("課後總整", use_container_width=True): nav("課後總整")
        if n5.button("個人主頁", use_container_width=True): nav("個人主頁")

    with col_user:
        username = st.session_state.get('username', 'Guest')
        first = username[0].upper() if username else "G"
        st.markdown(f"""
            <div style="background-color:#A89B93; color:white; width:38px; height:38px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-weight:bold; margin-left:auto;">
                {first}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 10px 0 20px 0; border: 0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

def html_card(title, icon, content_html):
    """
    純 HTML 卡片 (用於展示靜態資訊)
    關鍵修正：加入 unsafe_allow_html=True
    """
    st.markdown(f"""
        <div class="html-card-container">
            <div class="card-header-box">
                <span style="font-size: 1.1em; margin-right: 8px;">{icon}</span> {title}
            </div>
            <div class="html-card-body">
                {content_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def interactive_card_container(title, icon):
    """
    互動卡片容器 (用於包裹 Input/Button)
    使用 st.container(border=True) 並用 CSS 修飾頭部
    """
    container = st.container(border=True)
    with container:
        # 在容器内部渲染一個綠色的標題條
        # 使用負 margin 讓它貼滿容器頂部
        st.markdown(f"""
            <div style="background-color:{styles.COLOR_MAIN}; padding:12px 20px; margin:-16px -16px 15px -16px; color:white; font-weight:700; display:flex; align-items:center;">
                <span style="font-size: 1.1em; margin-right: 8px;">{icon}</span> {title}
            </div>
        """, unsafe_allow_html=True)
    return container