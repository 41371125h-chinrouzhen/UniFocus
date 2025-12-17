import streamlit as st
import components
import pandas as pd
import styles
import data_manager
import pdf_parser
import time

def show():
    # --- 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 功能列 ---
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        b1, b2, b3 = st.columns(3)
        if b1.button("📥 匯入", use_container_width=True):
            st.session_state.show_upload = not st.session_state.show_upload
        if b2.button("🎨 設計", use_container_width=True):
            st.toast("功能開發中", icon="🚧")
        
        # 下載按鈕
        if not st.session_state.schedule_data.empty:
            csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
            b3.download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)
        else:
            b3.button("⬇️ 下載", disabled=True, use_container_width=True)

    # --- 上傳區塊 ---
    if st.session_state.show_upload:
        st.write("")
        with components.interactive_card_container("上傳課表", "📂"):
            uploaded_file = st.file_uploader("上傳 PDF", type=['pdf'])
            if uploaded_file and st.button("開始解析", use_container_width=True):
                with st.spinner("處理中..."):
                    parsed_df = pdf_parser.parse_ntnu(uploaded_file)
                    if parsed_df is not None and not parsed_df.empty:
                        st.session_state.schedule_data = parsed_df
                        data_manager.save_user_data(st.session_state.get('username','Guest'), parsed_df)
                        st.success("匯入成功！")
                        st.session_state.show_upload = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("解析失敗")

    # --- 課表顯示主體 (關鍵修改) ---
    st.write("")
    
    # 改用互動容器包裹
    with components.interactive_card_container("本週課表", "📅"):
        if st.session_state.schedule_data.empty:
            st.markdown("""
                <div style="text-align:center; color:#888; padding:50px;">
                    <div style="font-size:3rem;">📭</div>
                    <p>尚無資料，請點擊上方「匯入」</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 準備表格數據
            df = st.session_state.schedule_data.copy()
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:0.8em; color:#666; background:#f4f4f4; padding:2px 5px; border-radius:4px;">' + df['地點'] + '</span>'
            
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:4px 0; border-top:1px dashed #ddd;">'.join(x)
            ).fillna("")
            
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 渲染 HTML
            table_html = pivot_df.to_html(classes="schedule-table", escape=False)
            
            # CSS 樣式 (直接在這裡注入)
            st.markdown("""
                <style>
                .schedule-table { width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #eee; border-radius: 8px; overflow: hidden; }
                .schedule-table th { background: #6B8E78; color: white; padding: 10px; text-align: center; border-bottom: 2px solid #5a7a66; }
                .schedule-table tbody th { background: #f9f9f9; color: #555; border-right: 1px solid #eee; min-width: 60px; }
                .schedule-table td { background: white; padding: 10px; border-right: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0; text-align: center; height: 80px; vertical-align: top; }
                </style>
                <div style="overflow-x: auto;">
            """ + table_html + "</div>", unsafe_allow_html=True)