import streamlit as st
import styles

def show():
    # 使用空白佔位讓內容垂直置中 (簡單模擬)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        # 1. 綠色大標題 (背景模糊效果模擬在卡片外)
        st.markdown('<div class="login-title">UNIFOCUS</div>', unsafe_allow_html=True)
        
        # 2. 登入卡片
        with st.container():
            # 注入 CSS 讓這個 container 變成卡片樣式
            st.markdown(f"""
                <div style="background-color:rgba(255,255,255,0.9); padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.1); backdrop-filter: blur(10px); text-align:center;">
                    <h3 style="color:{styles.COLOR_MAIN}; margin-bottom:20px;">🌿 智慧學習導航系統</h3>
                    <p style="color:#888; margin-bottom:30px;">請輸入您的學號以開始</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 因為上面的 HTML 包不住 Streamlit 的 Input，我們在視覺上接續
            # 實際上 Input 會顯示在下方，我們用 CSS 把它修飾得像在卡片裡
            uid = st.text_input("學號", placeholder="Enter Student ID", label_visibility="collapsed")
            
            st.write("") # 間距
            if st.button("登入 Login", use_container_width=True):
                if uid:
                    st.session_state.username = uid
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("請輸入學號")