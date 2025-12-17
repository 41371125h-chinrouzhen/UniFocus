import streamlit as st
import components
import pandas as pd

def show():
    # 上方功能列
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<h3 style='font-weight: 700;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        # 三個小按鈕並排
        b1, b2, b3 = st.columns(3)
        b1.button("📥", help="匯入")
        b2.button("🎨", help="設計")
        b3.button("⬇️", help="下載")

    # 顯示課表 (模擬數據)
    st.markdown('<div class="html-card" style="padding:20px; min-height:500px;">', unsafe_allow_html=True)
    
    if st.session_state.schedule_data.empty:
         st.info("尚無課表資料，請點擊右上角 📥 匯入")
    else:
        st.dataframe(st.session_state.schedule_data, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)