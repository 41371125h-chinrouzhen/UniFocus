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
    純 HTML 卡片
    ⚠️ 這裡就是問題所在！必須加上 unsafe_allow_html=True
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
    """, unsafe_allow_html=True)  # <--- 請確保這一行一定要有 True

def interactive_card_container(title, icon):
    """
    互動卡片容器 (修復版)
    """
    # 建立一個容器
    container = st.container(border=True)
    
    # 在容器「內部」注入 CSS，這樣才能確保樣式正確套用到這個特定的區塊
    # 我們移除了複雜的 :has 選擇器，改用更直接的方式渲染標題
    with container:
        st.markdown(f"""
            <style>
            /* 針對這個容器內部的樣式調整 */
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                background-color: {styles.COLOR_CARD_BG};
                border-radius: 16px;
                border: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            </style>
            
            <div style="
                background-color:{styles.COLOR_MAIN}; 
                padding:12px 20px; 
                margin: -16px -16px 15px -16px; 
                color:white; 
                font-weight:700; 
                display:flex; 
                align-items:center;
                border-radius: 16px 16px 0 0;">
                <span style="font-size: 1.1em; margin-right: 8px;">{icon}</span> {title}
            </div>
        """, unsafe_allow_html=True)
        
    return container