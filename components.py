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
        # 導航按鈕
        n1, n2, n3, n4, n5 = st.columns(5)
        current = st.session_state.get('page', '首頁')
        
        def nav(page): st.session_state.page = page

        # 使用 type="primary" 來標示當前頁面，雖然我們 CSS 覆蓋了顏色，但這樣可以保留狀態感
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
    注意：content_html 必須是乾淨的 HTML 字串
    """
    st.markdown(f"""
        <div class="html-card-container">
            <div class="card-header-box">
                <span style="font-size: 1.2em;">{icon}</span> {title}
            </div>
            <div class="html-card-body">
                {content_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def interactive_card_container(title, icon):
    """
    互動卡片容器
    用法:
    with interactive_card_container("標題", "圖標"):
        st.text_input(...)
    """
    # 使用 border=True 創建一個實體容器，CSS 會把它變成卡片樣式
    container = st.container(border=True)
    with container:
        # 在容器最上方渲染標題
        st.markdown(f"""
            <div style="margin: -16px -16px 15px -16px;">
                <div class="card-header-box">
                    <span>{icon}</span> {title}
                </div>
            </div>
        """, unsafe_allow_html=True)
    return container