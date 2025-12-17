import streamlit as st
import components
import pandas as pd
import styles
import data_manager
import pdf_parser
import time

def show():
    # --- 1. 初始化頁面狀態 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 2. 上方功能列 ---
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>我的課表</h3>", unsafe_allow_html=True)
    with c2:
        # 三個按鈕
        b1, b2, b3 = st.columns(3)
        
        # A. 匯入按鈕邏輯
        if b1.button("📥 匯入", help="匯入 PDF 課表", use_container_width=True):
            # 切換顯示狀態 (開 -> 關 / 關 -> 開)
            st.session_state.show_upload = not st.session_state.show_upload
            
        # B. 設計按鈕邏輯 (暫時提示)
        if b2.button("🎨 設計", help="更換課表樣式", use_container_width=True):
            st.toast("🎨 風格設計功能開發中，敬請期待！", icon="🚧")
            
        # C. 下載按鈕邏輯 (準備 CSV)
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
                            
                            # 3. 存入 Supabase 資料庫
                            user_id = st.session_state.get('username', 'Guest')
                            success = data_manager.save_user_data(user_id, parsed_df)
                            
                            if success:
                                st.success(f"✅ 成功匯入 {len(parsed_df)} 堂課程！")
                                st.session_state.show_upload = False # 成功後關閉上傳區
                                time.sleep(1) # 讓使用者看一下成功訊息
                                st.rerun() # 重新整理頁面顯示新課表
                            else:
                                st.error("❌ 解析成功但儲存失敗，請檢查網路或資料庫連線。")
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
        # 這裡我們使用 Pivot Table 將資料轉成「週課表」的矩陣格式，比較好讀
        try:
            df = st.session_state.schedule_data.copy()
            
            # 簡單的排序邏輯 (依照節次)
            # 這裡簡單處理，若要精確排序需要額外的 mapping function
            
            # 製作 Pivot Table (列=節次, 欄=星期, 值=科目+地點)
            # 組合顯示內容
            df['內容'] = df['活動名稱'] + '<br><span style="font-size:0.8em; color:#666">' + df['地點'] + '</span>'
            
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:2px 0">'.join(x) # 處理同一節兩堂課的情況
            ).fillna("")
            
            # 確保星期順序
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 將 DataFrame 轉為 HTML 表格
            table_html = pivot_df.to_html(classes="schedule-table", escape=False)
            
            # 注入表格 CSS (讓它變漂亮)
            st.markdown("""
                <style>
                .schedule-table { width: 100%; border-collapse: collapse; }
                .schedule-table th { background-color: #f1f1f1; padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; }
                .schedule-table td { padding: 10px; border: 1px solid #ddd; text-align: center; vertical-align: top; height: 80px; }
                </style>
            """, unsafe_allow_html=True)
            
            # 顯示在綠色卡片中
            components.html_card("本週課表", "📅", f"""
                <div style="overflow-x: auto;">
                    {table_html}
                </div>
            """)
            
        except Exception as e:
            st.error(f"課表顯示錯誤: {e}")
            st.dataframe(st.session_state.schedule_data) # 如果轉表失敗，至少顯示原始資料