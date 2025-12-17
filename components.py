import streamlit as st

def render_navbar():
    """渲染頂部導航列 (模擬 HTML)"""
    current_page = st.session_state.get('page', '首頁')
    username = st.session_state.get('username', 'Guest')
    
    # 定義頁面與標籤
    pages = ["首頁", "我的課表", "課前預習", "課後總整", "個人主頁"]
    
    # 建立連結 HTML
    links_html = ""
    for p in pages:
        active_class = "active" if p == current_page else ""
        # 這裡的 onclick 暫時無法直接觸發 Python，實際切換需靠 Sidebar 或更進階的 Component。
        # 為了視覺效果，我們先顯示樣式。
        links_html += f'<a class="nav-link {active_class}">{p}</a>'

    st.markdown(f"""
        <div class="navbar-container">
            <div class="navbar-logo">
                <span>U</span> UNIFOCUS | 智慧學習導航
            </div>
            <div class="navbar-links">
                {links_html}
                <div class="user-avatar">
                    {username[:2].upper()}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def card_html(title, icon, content_html):
    """渲染純 HTML 靜態卡片"""
    st.markdown(f"""
        <div class="html-card">
            <div class="card-header">
                <span style="font-size: 1.3em;">{icon}</span> {title}
            </div>
            <div class="card-body">
                {content_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def card_interactive_header(title, icon):
    """渲染互動卡片的標題 (配合 CSS hack)"""
    st.markdown(f'<div class="card-header-marker"><span style="font-size: 1.3em;">{icon}</span> {title}</div>', unsafe_allow_html=True)