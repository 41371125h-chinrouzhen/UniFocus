import streamlit as st
import components
import pandas as pd
import styles
import data_manager
import pdf_parser
import time

def show():
    # --- 1. 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 2. 功能列 ---
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        b1, b2, b3 = st.columns(3)
        if b1.button("📥 匯入", use_container_width=True):
            st.session_state.show_upload = not st.session_state.show_upload
        if b2.button("🎨 設計", use_container_width=True):
            st.toast("功能開發中", icon="🚧")
        if not st.session_state.schedule_data.empty:
            csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
            b3.download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)
        else:
            b3.button("⬇️ 下載", disabled=True, use_container_width=True)

    # --- 3. 匯入區塊 ---
    if st.session_state.show_upload:
        st.write("")
        # 這裡直接使用簡單的 expander 或 container，避免樣式干擾
        with st.container(border=True):
            st.markdown("**上傳課表 PDF**")
            uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
            
            if uploaded_file and st.button("開始解析與儲存", use_container_width=True):
                with st.spinner("處理中..."):
                    parsed_df = pdf_parser.parse_ntnu(uploaded_file)
                    if parsed_df is not None and not parsed_df.empty:
                        st.session_state.schedule_data = parsed_df
                        # 存入 Google Sheets
                        user_id = st.session_state.get('username', 'Guest')
                        data_manager.save_user_data(user_id, parsed_df)
                        
                        st.success(f"✅ 成功匯入 {len(parsed_df)} 堂課程！")
                        st.session_state.show_upload = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("⚠️ 解析失敗，請確認 PDF 格式")

    # --- 4. 顯示課表 (直接渲染版) ---
    st.write("") 
    
    if st.session_state.schedule_data.empty:
        st.info("尚無資料，請點擊「匯入」上傳課表。")
    else:
        try:
            df = st.session_state.schedule_data.copy()
            
            # 準備資料
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:0.8em; color:#666">' + df['地點'] + '</span>'
            
            # 轉成週課表
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:2px 0; border-top:1px dashed #ccc;">'.join(x)
            ).fillna("")
            
            # 排序
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 生成 HTML
            table_html = pivot_df.to_html(classes="schedule-table", escape=False)
            
            # 直接使用 st.markdown 渲染，不透過 components
            st.markdown(f"""
            <style>
                .schedule-table {{ width: 100%; border-collapse: collapse; border: 1px solid #ddd; }}
                .schedule-table th {{ background: #6B8E78; color: white; padding: 10px; border: 1px solid #ddd; text-align: center; }}
                .schedule-table td {{ background: white; padding: 10px; border: 1px solid #ddd; text-align: center; vertical-align: top; height: 80px; }}
            </style>
            <div style="background:white; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                <div style="overflow-x: auto;">
                    {table_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"表格顯示錯誤: {e}")
            st.dataframe(st.session_state.schedule_data)