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

    # --- 4. 顯示課表 (關鍵修復部分) ---
    st.write("") 
    
    # 使用互動容器包裹
    with components.interactive_card_container("本週課表", "📅"):
        
        if st.session_state.schedule_data.empty:
            # 空狀態
            st.markdown("""
                <div style="text-align:center; color:#888; padding:50px;">
                    <div style="font-size:3rem; margin-bottom:10px;">📭</div>
                    <p>尚無課表資料</p>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            try:
                # 準備資料
                df = st.session_state.schedule_data.copy()
                
                # 格式化內容：粗體課名 + 灰色地點
                df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:0.8em; color:#666; background:#f4f4f4; padding:2px 4px; border-radius:4px;">' + df['地點'] + '</span>'
                
                # 轉成週課表格式 (Pivot)
                pivot_df = df.pivot_table(
                    index='時間/節次', 
                    columns='星期', 
                    values='內容', 
                    aggfunc=lambda x: '<br><hr style="margin:4px 0; border-top:1px dashed #ddd;">'.join(x)
                ).fillna("")
                
                # 排序星期
                days_order = ['一', '二', '三', '四', '五', '六', '日']
                existing_days = [d for d in days_order if d in pivot_df.columns]
                pivot_df = pivot_df[existing_days]
                
                # 1. 定義 CSS 樣式 (獨立變數，避免縮排錯誤)
                css_style = """
                <style>
                    .schedule-table { width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #E0E0E0; border-radius: 8px; overflow: hidden; font-family: sans-serif; }
                    .schedule-table thead tr th { background-color: #6B8E78; color: white; padding: 12px; text-align: center; border-bottom: 2px solid #5a7a66; }
                    .schedule-table tbody th { background-color: #f9f9f9; color: #555; border-right: 1px solid #eee; padding: 10px; text-align: center; min-width: 60px; font-weight: bold; }
                    .schedule-table td { background-color: white; padding: 10px; border-bottom: 1px solid #f0f0f0; border-right: 1px solid #f0f0f0; text-align: center; vertical-align: top; height: 80px; min-width: 100px; }
                    .schedule-table td:hover { background-color: #fcfcfc; }
                </style>
                """
                
                # 2. 轉成 HTML 表格
                table_html = pivot_df.to_html(classes="schedule-table", escape=False)
                
                # 3. 組合最終 HTML
                final_html = f'{css_style}<div style="overflow-x: auto;">{table_html}</div>'
                
                # 4. 渲染！ (這行最重要的 unsafe_allow_html=True)
                st.markdown(final_html, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"顯示錯誤: {e}")
                st.dataframe(st.session_state.schedule_data)