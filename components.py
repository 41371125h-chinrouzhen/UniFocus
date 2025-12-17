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

        # 按鈕樣式由 styles.py 統一控制，這裡只負責邏輯
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
    已修復：加入 unsafe_allow_html=True，解決顯示源碼的問題
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
    互動卡片容器 (解決方案：強制統一 CSS)
    
    這段程式碼會做三件事：
    1. 注入 CSS，找到這個容器並強制設定 padding 為 20px，背景為白色，加上陰影 (模擬 HTML 卡片)。
    2. 渲染標題列，使用 -20px 的負邊距 (Negative Margin) 讓它往上、往左、往右延伸，蓋住內距，達成「滿版標題」效果。
    3. 下方的 widgets 因為容器原本就有 20px padding，所以會自然與邊緣保持距離，不會貼邊。
    """
    
    # 1. 注入針對此容器的強制樣式 (利用 :has 選取器定位)
    st.markdown(f"""
        <style>
        /* 定位包含 .interactive-card-header 的父容器 */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.interactive-card-header) {{
            background-color: {styles.COLOR_CARD_BG} !important;
            border-radius: 16px !important;
            border: none !important; /* 移除 Streamlit 預設灰框 */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            padding: 20px !important; /* 強制內距統一為 20px */
        }}
        </style>
    """, unsafe_allow_html=True)

    # 2. 建立容器 (border=True 用於產生結構，但我們用上面的 CSS 把它的預設樣式蓋掉了)
    container = st.container(border=True)
    
    with container:
        # 3. 渲染滿版標題 (使用 margin: -20px 抵消容器的 padding: 20px)
        st.markdown(f"""
            <div class="interactive-card-header" style="
                background-color:{styles.COLOR_MAIN}; 
                padding:12px 20px; 
                margin: -20px -20px 20px -20px; /* 關鍵：負邊距填滿四周 */
                color:white; 
                font-weight:700; 
                display:flex; 
                align-items:center;
                border-radius: 16px 16px 0 0;">
                <span style="font-size: 1.1em; margin-right: 8px;">{icon}</span> {title}
            </div>
        """, unsafe_allow_html=True)
        
        # 在這裡之後放入的 st.text_input 等元件，
        # 會因為容器本身有 padding: 20px，自動顯示在正確的位置，看起來跟 HTML 卡片一模一樣。
        
    return container