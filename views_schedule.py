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
        # 三個按鈕
        b1, b2, b3 = st.columns(3)
        
        # A. 匯入按鈕邏輯
        if b1.button("📥 匯入", help="匯入 PDF 課表", use_container_width=True):
            # 切換顯示狀態
            st.session_state.show_upload = not st.session_state.show_upload
            
        # B. 設計按鈕邏輯
        if b2.button("🎨 設計", help="更換課表樣式", use_container_width=True):
            st.toast("🎨 風格設計功能開發中，敬請期待！", icon="🚧")
            
        # C. 下載按鈕邏輯
        if not st.session_state.schedule_data.empty:
            csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
            b3.download_button(
                label="⬇️ 下載",
                data=csv,
                file_name='my_schedule.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            b3.button("⬇️ 下載", disabled=True, use_container_width=True)

    # --- 3. 匯入區塊 (只有按下匯入按鈕時才會出現) ---
    if st.session_state.show_upload:
        st.write("") # 間距
        with components.interactive_card_container("上傳課表", "📂"):
            uploaded_file = st.file_uploader("請上傳台師大課表 PDF", type=['pdf'])
            
            if uploaded_file is not None:
                if st.button("開始解析與儲存", use_container_width=True):
                    with st.spinner("正在解析 PDF 並同步至雲端資料庫..."):
                        # 1. 解析 PDF
                        parsed_df = pdf_parser.parse_ntnu(uploaded_file)
                        
                        if parsed_df is not None and not parsed_df.empty:
                            # 2. 存入 Session State
                            st.session_state.schedule_data = parsed_df
                            
                            # 3. 存入 Google Sheets
                            user_id = st.session_state.get('username', 'Guest')
                            success = data_manager.save_user_data(user_id, parsed_df)
                            
                            if success:
                                st.success(f"✅ 成功匯入 {len(parsed_df)} 堂課程！")
                                st.session_state.show_upload = False # 成功後關閉上傳區
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ 解析成功但儲存失敗，請檢查網路或 Google Sheets 連線。")
                        else:
                            st.error("⚠️ 解析失敗：無法讀取 PDF 內容，請確認格式是否正確。")

    # --- 4. 顯示課表主體 ---
    st.write("") # 間距
    
    if st.session_state.schedule_data.empty:
        # 空狀態顯示
        components.html_card("本週課表", "📅", """
            <div style="text-align:center; color:#888; padding:60px 20px; border: 2px dashed #ddd; border-radius:10px; background:#fafafa;">
                <div style="font-size:3rem; margin-bottom:10px;">📭</div>
                <p style="font-size:1.1rem; color:#555;">目前尚無課表資料</p>
                <small style="color:#999;">請點擊右上角「📥 匯入」按鈕上傳 PDF</small>
            </div>
        """)
    else:
        # 有資料時顯示
        try:
            df = st.session_state.schedule_data.copy()
            
            # Pivot Table 邏輯
            # 這裡加上地點的顯示
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:0.85em; color:#666; background:#f0f0f0; padding:2px 6px; border-radius:4px;">' + df['地點'] + '</span>'
            
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:4px 0; border:0; border-top:1px dashed #eee;">'.join(x)
            ).fillna("")
            
            # 確保星期順序
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 轉為 HTML
            table_html = pivot_df.to_html(classes="schedule-table", escape=False)
            
            # === CSS 美化 ===
            st.markdown("""
                <style>
                .schedule-table {
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    border-radius: 8px;
                    overflow: hidden;
                    border: 1px solid #E0E0E0;
                }
                .schedule-table thead tr th {
                    background-color: #6B8E78;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    text-align: center;
                    border-bottom: 2px solid #5a7a66;
                }
                .schedule-table tbody tr th {
                    background-color: #f9f9f9;
                    font-weight: bold;
                    color: #555;
                    border-right: 1px solid #eee;
                    padding: 10px;
                    text-align: center;
                    vertical-align: middle;
                    min-width: 60px;
                }
                .schedule-table td {
                    padding: 12px;
                    border-bottom: 1px solid #f0f0f0;
                    border-right: 1px solid #f0f0f0;
                    text-align: center;
                    vertical-align: top;
                    background-color: white;
                    min-width: 100px;
                    height: 100px;
                    transition: background 0.2s;
                }
                .schedule-table td:hover {
                    background-color: #fcfcfc;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # 顯示在綠色卡片中
            components.html_card("本週課表", "📅", f"""
                <div style="overflow-x: auto; padding: 5px;">
                    {table_html}
                </div>
            """)
            
        except Exception as e:
            st.error(f"課表顯示錯誤: {e}")
            st.dataframe(st.session_state.schedule_data)