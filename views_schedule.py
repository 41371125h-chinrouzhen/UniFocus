import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time

def show():
    # --- 1. 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False

    # --- 2. 標題與按鈕區 ---
    st.markdown("### 📅 我的課表")
    
    col_btn = st.columns([1, 1, 1, 3]) # 調整按鈕排版
    
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

    # --- 3. 匯入功能區 (展開式) ---
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

    # --- 4. 顯示課表 (關鍵修復：直接渲染，不透過任何 Component) ---
    st.markdown("---") # 分隔線

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料，請點擊上方「匯入」按鈕。")
    else:
        try:
            # 複製資料以免影響原始檔
            df = st.session_state.schedule_data.copy()
            
            # 加工內容：加入 HTML 標籤 (粗體課名 + 灰色地點)
            # 注意：這裡的 HTML 標籤是為了表格內部的豐富顯示
            df['內容'] = '<b>' + df['活動名稱'] + '</b><br><span style="font-size:0.8em; color:gray">' + df['地點'] + '</span>'
            
            # 轉成週課表 (Pivot Table)
            pivot_df = df.pivot_table(
                index='時間/節次', 
                columns='星期', 
                values='內容', 
                aggfunc=lambda x: '<br><hr style="margin:2px 0">'.join(x)
            ).fillna("")
            
            # 排序星期
            days_order = ['一', '二', '三', '四', '五', '六', '日']
            existing_days = [d for d in days_order if d in pivot_df.columns]
            pivot_df = pivot_df[existing_days]
            
            # 產生 HTML 表格 (escape=False 非常重要，不然 <br> 會被顯示出來)
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            # 定義 CSS (直接寫在這裡，保證生效)
            custom_css = """
            <style>
                .my-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-family: sans-serif;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .my-table th {
                    background-color: #6B8E78;
                    color: white;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #ddd;
                }
                .my-table td {
                    padding: 10px;
                    border: 1px solid #ddd;
                    text-align: center;
                    vertical-align: top;
                    height: 80px;
                    background-color: white;
                }
                .my-table tr:nth-child(even) td {
                    background-color: #f9f9f9;
                }
                /* 強制覆蓋 Streamlit 的預設表格樣式 */
                table.dataframe { border: none !important; }
            </style>
            """
            
            # 組合 CSS 和 HTML
            final_html = f"{custom_css}<div style='overflow-x:auto'>{table_html}</div>"
            
            # 🚀 最終渲染指令 (Unsafe Allow HTML)
            st.markdown(final_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")
            # 如果真的渲染失敗，至少顯示原始資料讓你知道資料是對的
            st.dataframe(st.session_state.schedule_data)