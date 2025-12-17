import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time
import streamlit.components.v1 as components

def show():
    # --- 1. 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 2. 標題與按鈕區 ---
    st.markdown("### 📅 我的課表")
    
    col_btn = st.columns([1, 1, 1, 3])
    
    if col_btn[0].button("📥 匯入", use_container_width=True):
        st.session_state.show_upload = not st.session_state.show_upload
        
    if col_btn[1].button("🎨 設計", use_container_width=True):
        st.toast("功能開發中", icon="🚧")
        
    if not st.session_state.schedule_data.empty:
        csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
        col_btn[2].download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)

    # --- 3. 匯入功能區 ---
    if st.session_state.show_upload:
        with st.container(border=True):
            st.info("請上傳台師大課表 PDF")
            uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
            
            if uploaded_file and st.button("🚀 開始解析", use_container_width=True):
                with st.spinner("正在處理..."):
                    parsed_df = pdf_parser.parse_ntnu(uploaded_file)
                    if parsed_df is not None and not parsed_df.empty:
                        st.session_state.schedule_data = parsed_df
                        uid = st.session_state.get('username', 'Guest')
                        data_manager.save_user_data(uid, parsed_df)
                        st.success("匯入成功！")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("解析失敗，請確認 PDF 格式")

    # --- 4. 顯示課表 (完美排序 + 緊湊樣式) ---
    st.markdown("---") 

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料，請點擊上方「匯入」按鈕。")
    else:
        try:
            df = st.session_state.schedule_data.copy()
            
            # --- 步驟 A: 資料加工 ---
            # 縮小字體，讓顯示更精緻
            df['內容'] = (
                '<div style="line-height:1.2;">'
                '<b>' + df['活動名稱'] + '</b><br>'
                '<span style="font-size:10px; color:#666; background:#f0f0f0; padding:1px 3px; border-radius:3px;">' + df['地點'] + '</span>'
                '</div>'
            )
            
            # --- 步驟 B: 轉成 Pivot Table ---
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<hr style="margin:2px 0; border-top:1px dashed #ccc;">'.join(x)
            )
            
            # --- 步驟 C: 強制排序與補齊 (解決 10 在 1 前面 & 缺漏問題) ---
            # 定義完整的顯示順序
            ALL_DAYS = ['一', '二', '三', '四', '五', '六', '日']
            # 定義台師大完整節次 (包含 M, 1-10, A-D)
            # 這裡用字串 '1', '2'... 確保跟 PDF 解析出來的型態一致
            ALL_PERIODS = ['M'] + [str(i) for i in range(1, 11)] + ['A', 'B', 'C', 'D']
            
            # 使用 reindex 強制依照我們定義的順序排列
            # fill_value="" 會把原本沒有課的格子填成空白，確保該行/列出現
            pivot_df = pivot_df.reindex(index=ALL_PERIODS, columns=ALL_DAYS, fill_value="")
            
            # 移除全空的列 (可選：如果你不想顯示從來沒課的節次，例如 'M' 或 'D'，可以打開下面這行)
            # pivot_df = pivot_df.loc[~(pivot_df == "").all(axis=1)] 
            
            # --- 步驟 D: 產生 HTML ---
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            # --- 步驟 E: CSS 瘦身 (縮小表格) ---
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ 
                    font-family: "Noto Sans TC", sans-serif; 
                    margin: 0; 
                    padding: 0; /* 移除 body padding */
                }}
                .my-table {{
                    width: 100%;
                    border-collapse: collapse;
                    border-radius: 6px;
                    overflow: hidden;
                    font-size: 12px; /* 整體字體縮小 */
                    table-layout: fixed; /* 固定寬度，避免某欄特別寬 */
                }}
                .my-table th {{
                    background-color: #6B8E78;
                    color: white;
                    padding: 6px 4px; /* 縮小 Padding */
                    text-align: center;
                    border: 1px solid #ddd;
                    width: 13%; /* 強制平均分配寬度 */
                }}
                /* 左側節次欄位 */
                .my-table tbody th {{
                    background-color: #f9f9f9;
                    color: #555;
                    width: 5%;
                    font-weight: bold;
                }}
                .my-table td {{
                    padding: 4px; /* 縮小 Padding */
                    border: 1px solid #eee;
                    text-align: center;
                    vertical-align: middle;
                    height: auto; /* 讓高度自適應，不要固定 80px */
                    background-color: white;
                    word-wrap: break-word; /* 允許長字換行 */
                }}
                .my-table tr:nth-child(even) td {{
                    background-color: #fcfcfc;
                }}
            </style>
            </head>
            <body>
                {table_html}
            </body>
            </html>
            """
            
            # 渲染 iframe (高度可以稍微設大一點，讓它有捲軸也沒關係，或者設小一點讓它更緊湊)
            components.html(final_html, height=650, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")
            st.dataframe(st.session_state.schedule_data)