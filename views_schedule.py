import streamlit as st
import components
import pandas as pd
import styles
import data_manager
import pdf_parser
import time

def show():
    # --- 1. 初始化頁面狀態 ---
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False

    # --- 2. 上方功能列 ---
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        b1, b2, b3 = st.columns(3)
        
        # 按鈕邏輯
        if b1.button("📥 匯入", help="匯入 PDF", use_container_width=True):
            st.session_state.show_upload = not st.session_state.show_upload
            
        if b2.button("🎨 設計", help="樣式", use_container_width=True):
            st.toast("功能開發中", icon="🚧")
            
        # 下載按鈕
        if not st.session_state.schedule_data.empty:
            csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
            b3.download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)
        else:
            b3.button("⬇️ 下載", disabled=True, use_container_width=True)

    # --- 3. 匯入區塊 ---
    if st.session_state.show_upload:
        st.write("")
        with components.interactive_card_container("上傳課表", "📂"):
            uploaded_file = st.file_uploader("請上傳台師大課表 PDF", type=['pdf'])
            
            if uploaded_file is not None:
                if st.button("開始解析與儲存", use_container_width=True):
                    with st.spinner("處理中..."):
                        # 解析
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

# --- 4. 顯示課表主體 ---
    st.write("") 
    
    # 暫時註解掉容器，先測試直接顯示
    # with components.interactive_card_container("本週課表", "📅"):
    
    st.markdown(f"""
    <div style="
        background-color: white; 
        padding: 20px; 
        border-radius: 16px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;">
        <div style="background-color:#6B8E78; color:white; padding:10px 20px; border-radius:10px 10px 0 0; margin:-20px -20px 20px -20px; font-weight:bold;">
            📅 本週課表
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.schedule_data.empty:
        st.markdown("<div style='text-align:center; padding:50px; color:#888;'>📭 尚無課表資料</div>", unsafe_allow_html=True)
    else:
        try:
            df = st.session_state.schedule_data.copy()
            
            # 簡化內容，先求顯示成功
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br>' + df['地點']
            
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr>'.join(x)
            ).fillna("")
            
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 產生純淨的 HTML
            table_html = pivot_df.to_html(classes="schedule-table", escape=False)
            
            # 渲染
            st.markdown(f"""
                <style>
                .schedule-table {{ width: 100%; border-collapse: collapse; }}
                .schedule-table th {{ background: #6B8E78; color: white; padding: 8px; border: 1px solid #ddd; }}
                .schedule-table td {{ padding: 8px; border: 1px solid #ddd; text-align: center; }}
                </style>
                <div style="overflow-x: auto;">
                    {table_html}
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
            
    st.markdown("</div>", unsafe_allow_html=True) # 閉合卡片 div