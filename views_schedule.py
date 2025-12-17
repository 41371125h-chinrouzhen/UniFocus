import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time
import streamlit.components.v1 as components  # <--- 關鍵新元件

def show():
    # --- 1. 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 2. 標題與按鈕區 ---
    st.markdown("### 📅 我的課表")
    
    col_btn = st.columns([1, 1, 1, 3])
    
    # 匯入按鈕
    if col_btn[0].button("📥 匯入", use_container_width=True):
        st.session_state.show_upload = not st.session_state.show_upload
        
    # 設計按鈕
    if col_btn[1].button("🎨 設計", use_container_width=True):
        st.toast("功能開發中", icon="🚧")
        
    # 下載按鈕
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
                        # 存檔
                        uid = st.session_state.get('username', 'Guest')
                        data_manager.save_user_data(uid, parsed_df)
                        
                        st.success("匯入成功！")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("解析失敗，請確認 PDF 格式")

    # --- 4. 顯示課表 (改用 components.html 強制渲染) ---
    st.markdown("---") 

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料，請點擊上方「匯入」按鈕。")
    else:
        try:
            # 複製資料
            df = st.session_state.schedule_data.copy()
            
            # 加工內容
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:12px; color:#666; background:#f0f0f0; padding:2px 4px; border-radius:4px;">' + df['地點'] + '</span>'
            
            # 轉成週課表
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:2px 0; border:0; border-top:1px dashed #ccc;">'.join(x)
            ).fillna("")
            
            # 排序星期
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 產生 HTML 表格
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            # 定義完整的 HTML 頁面結構 (包含 CSS)
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ font-family: "Noto Sans TC", sans-serif; margin: 0; padding: 10px; }}
                .my-table {{
                    width: 100%;
                    border-collapse: collapse;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                    font-size: 14px;
                }}
                .my-table th {{
                    background-color: #6B8E78;
                    color: white;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #ddd;
                    white-space: nowrap;
                }}
                .my-table td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    text-align: center;
                    vertical-align: top;
                    height: 80px;
                    background-color: white;
                    min-width: 100px;
                }}
                .my-table tr:nth-child(even) td {{
                    background-color: #f9f9f9;
                }}
            </style>
            </head>
            <body>
                {table_html}
            </body>
            </html>
            """
            
            # 🔥 這裡是最重要的修改：使用 components.html 建立獨立視窗渲染
            # height=600 設定高度，scrolling=True 允許捲動
            components.html(final_html, height=600, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")
            st.dataframe(st.session_state.schedule_data)