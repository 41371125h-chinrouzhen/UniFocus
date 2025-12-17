import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time
import streamlit.components.v1 as components

def show():
    # --- 1. 初始化 ---
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False
    # 新增：設計主題狀態 (預設綠色)
    if 'schedule_theme' not in st.session_state: st.session_state.schedule_theme = '#6B8E78'

    # --- 2. 標題與按鈕區 ---
    st.markdown("### 📅 我的課表")
    col_btn = st.columns([1, 1, 1, 3])
    
    if col_btn[0].button("📥 匯入", use_container_width=True):
        st.session_state.show_upload = not st.session_state.show_upload
        st.session_state.show_design = False # 互斥開啟
        
    if col_btn[1].button("🎨 設計", use_container_width=True):
        # 切換設計選單
        if 'show_design' not in st.session_state: st.session_state.show_design = False
        st.session_state.show_design = not st.session_state.show_design
        st.session_state.show_upload = False # 互斥開啟

    if not st.session_state.schedule_data.empty:
        csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
        col_btn[2].download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)

    # --- 3. 匯入功能區 ---
    if st.session_state.show_upload:
        with st.container(border=True):
            st.info("請上傳台師大課表 PDF")
            uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
            if uploaded_file and st.button("🚀 開始解析", use_container_width=True):
                with st.spinner("處理中..."):
                    parsed_df = pdf_parser.parse_ntnu(uploaded_file)
                    if parsed_df is not None and not parsed_df.empty:
                        st.session_state.schedule_data = parsed_df
                        data_manager.save_user_data(st.session_state.get('username','Guest'), parsed_df)
                        st.success("匯入成功！")
                        st.rerun()
                    else:
                        st.error("解析失敗")

    # --- 3.5 設計功能區 (實作換色) ---
    if st.session_state.get('show_design', False):
        with st.container(border=True):
            st.markdown("#### 🎨 自訂主題")
            c1, c2, c3 = st.columns(3)
            # 點擊按鈕更換主題色
            if c1.button("🌿 經典綠", use_container_width=True): 
                st.session_state.schedule_theme = '#6B8E78'
                st.rerun()
            if c2.button("🌊 海洋藍", use_container_width=True): 
                st.session_state.schedule_theme = '#4A90E2'
                st.rerun()
            if c3.button("🌸 櫻花粉", use_container_width=True): 
                st.session_state.schedule_theme = '#E27D60'
                st.rerun()

    # --- 4. 顯示課表 ---
    st.markdown("---") 

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料，請點擊上方「匯入」按鈕。")
    else:
        try:
            # 取得當前主題色
            theme_color = st.session_state.schedule_theme
            
            df = st.session_state.schedule_data.copy().fillna("")
            
            # 使用主題色微調地點標籤的顏色 (淡化版)
            df['內容'] = (
                '<div style="line-height:1.2; margin-bottom:4px;">'
                '<b>' + df['活動名稱'] + '</b><br>'
                '<span style="font-size:10px; color:#555; background:#f4f4f4; padding:1px 3px; border-radius:3px; border:1px solid #ddd;">' + df['地點'] + '</span>'
                '</div>'
            )
            
            TARGET_DAYS = ['一', '二', '三', '四', '五']
            PERIOD_MAP = {
                '1': '08:10-09:00', '2': '09:10-10:00', '3': '10:20-11:10', '4': '11:20-12:10',
                '5': '12:20-13:10', '6': '13:20-14:10', '7': '14:20-15:10', '8': '15:30-16:20',
                '9': '16:30-17:20', '10': '17:30-18:20', 
                'A': '18:40-19:30', 'B': '19:35-20:25', 'C': '20:30-21:20', 'D': '21:25-22:15'
            }
            TARGET_PERIODS = list(PERIOD_MAP.keys())

            pivot_df = df.pivot_table(index='時間/節次', columns='星期', values='內容', aggfunc=lambda x: '<hr style="margin:2px 0; border-top:1px dashed #ccc;">'.join(x))
            pivot_df = pivot_df.fillna("").reindex(index=TARGET_PERIODS, columns=TARGET_DAYS, fill_value="")
            
            new_index = []
            for p in pivot_df.index:
                time_str = PERIOD_MAP.get(str(p), "")
                # 節次數字也跟隨主題色，但深一點
                new_index.append(f"<div style='font-size:14px; font-weight:bold; color:{theme_color};'>{p}</div><div style='font-size:10px; color:#888; margin-top:2px;'>{time_str}</div>")
            
            pivot_df.index = new_index
            pivot_df.index.name = None 
            pivot_df = pivot_df.replace('nan', '', regex=False).replace('NaN', '', regex=False)
            
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ font-family: "Noto Sans TC", sans-serif; margin: 0; padding: 0; }}
                .my-table {{ width: 100%; border-collapse: collapse; border-radius: 6px; overflow: hidden; font-size: 12px; table-layout: fixed; }}
                /* 使用變數 theme_color 控制表頭顏色 */
                .my-table th {{ background-color: {theme_color}; color: white; padding: 8px 4px; text-align: center; border: 1px solid #ddd; width: 16%; }}
                .my-table tbody th {{ background-color: #f9f9f9; color: #555; width: 80px; font-weight: normal; vertical-align: middle; border: 1px solid #ddd; }}
                .my-table td {{ padding: 4px; border: 1px solid #eee; text-align: center; vertical-align: middle; height: auto; background-color: white; word-wrap: break-word; }}
                .my-table tr:nth-child(even) td {{ background-color: #fcfcfc; }}
            </style>
            </head>
            <body>{table_html}</body>
            </html>
            """
            
            components.html(final_html, height=800, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")