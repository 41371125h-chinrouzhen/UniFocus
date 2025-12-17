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

    # --- 4. 顯示課表 ---
    st.markdown("---") 

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料，請點擊上方「匯入」按鈕。")
    else:
        try:
            # 防護 1: 從源頭就清除 NaN，防止字串拼接時出現 "nan"
            df = st.session_state.schedule_data.copy().fillna("")
            
            # --- 步驟 A: 資料加工 ---
            # 確保內容欄位都是字串
            df['活動名稱'] = df['活動名稱'].astype(str)
            df['地點'] = df['地點'].astype(str)

            df['內容'] = (
                '<div style="line-height:1.2; margin-bottom:4px;">'
                '<b>' + df['活動名稱'] + '</b><br>'
                '<span style="font-size:10px; color:#666; background:#f0f0f0; padding:1px 3px; border-radius:3px;">' + df['地點'] + '</span>'
                '</div>'
            )
            
            # --- 步驟 B: 定義範圍 ---
            TARGET_DAYS = ['一', '二', '三', '四', '五']
            PERIOD_MAP = {
                '1': '08:10-09:00', '2': '09:10-10:00', '3': '10:20-11:10', '4': '11:20-12:10',
                '5': '12:20-13:10', '6': '13:20-14:10', '7': '14:20-15:10', '8': '15:30-16:20',
                '9': '16:30-17:20', '10': '17:30-18:20', 
                'A': '18:40-19:30', 'B': '19:35-20:25', 'C': '20:30-21:20', 'D': '21:25-22:15'
            }
            TARGET_PERIODS = list(PERIOD_MAP.keys())

            # --- 步驟 C: 轉成 Pivot Table ---
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<hr style="margin:2px 0; border-top:1px dashed #ccc;">'.join(x)
            )
            
            # 防護 2: Pivot 後立刻補空值
            pivot_df = pivot_df.fillna("")

            # --- 步驟 D: 強制重整索引 ---
            # 防護 3: reindex 時指定 fill_value=""
            pivot_df = pivot_df.reindex(index=TARGET_PERIODS, columns=TARGET_DAYS, fill_value="")
            
            # --- 步驟 E: 美化索引 (加入時間) ---
            new_index = []
            for p in pivot_df.index:
                time_str = PERIOD_MAP.get(str(p), "")
                label = f"<div style='font-size:14px; font-weight:bold; color:#444;'>{p}</div><div style='font-size:10px; color:#888; margin-top:2px;'>{time_str}</div>"
                new_index.append(label)
            
            pivot_df.index = new_index
            pivot_df.index.name = None 
            
            # 防護 4: 最後檢查，把所有可能的 "nan" 字串強制換成空字串
            # 這能解決如果之前步驟有漏網之魚
            pivot_df = pivot_df.replace('nan', '', regex=False)
            pivot_df = pivot_df.replace('NaN', '', regex=False)
            
            # --- 步驟 F: 產生 HTML ---
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            # --- 步驟 G: CSS ---
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ 
                    font-family: "Noto Sans TC", sans-serif; 
                    margin: 0; 
                    padding: 0;
                }}
                .my-table {{
                    width: 100%;
                    border-collapse: collapse;
                    border-radius: 6px;
                    overflow: hidden;
                    font-size: 12px;
                    table-layout: fixed;
                }}
                .my-table th {{
                    background-color: #6B8E78;
                    color: white;
                    padding: 8px 4px;
                    text-align: center;
                    border: 1px solid #ddd;
                    width: 16%; 
                }}
                .my-table tbody th {{
                    background-color: #f9f9f9;
                    color: #555;
                    width: 80px; 
                    font-weight: normal;
                    vertical-align: middle;
                    border: 1px solid #ddd;
                }}
                .my-table td {{
                    padding: 4px;
                    border: 1px solid #eee;
                    text-align: center;
                    vertical-align: middle;
                    height: auto;
                    background-color: white;
                    word-wrap: break-word;
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
            
            components.html(final_html, height=800, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")