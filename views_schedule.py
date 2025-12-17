import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time
import streamlit.components.v1 as components

def show():
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False
    # 新增風格狀態
    if 'schedule_style' not in st.session_state: st.session_state.schedule_style = '經典簡約'

    st.markdown("### 📅 我的課表")
    col_btn = st.columns([1, 1, 1, 3])
    
    if col_btn[0].button("📥 匯入", use_container_width=True):
        st.session_state.show_upload = not st.session_state.show_upload
        st.session_state.show_design = False
        
    if col_btn[1].button("🎨 設計", use_container_width=True):
        if 'show_design' not in st.session_state: st.session_state.show_design = False
        st.session_state.show_design = not st.session_state.show_design
        st.session_state.show_upload = False

    if not st.session_state.schedule_data.empty:
        csv = st.session_state.schedule_data.to_csv(index=False).encode('utf-8-sig')
        col_btn[2].download_button("⬇️ 下載", data=csv, file_name='schedule.csv', mime='text/csv', use_container_width=True)

    # --- 匯入區 ---
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
                        st.success("匯入成功！"); st.rerun()
                    else: st.error("解析失敗")

    # --- 設計區 (新增風格選擇) ---
    if st.session_state.get('show_design', False):
        with st.container(border=True):
            st.markdown("#### 🎨 選擇課表風格")
            style_cols = st.columns(3)
            if style_cols[0].button("🌿 經典簡約", use_container_width=True): 
                st.session_state.schedule_style = '經典簡約'; st.rerun()
            if style_cols[1].button("👾 像素遊戲", use_container_width=True): 
                st.session_state.schedule_style = '像素遊戲'; st.rerun()
            if style_cols[2].button("✏️ 手繪筆記", use_container_width=True): 
                st.session_state.schedule_style = '手繪筆記'; st.rerun()

    st.markdown("---") 

    if st.session_state.schedule_data.empty:
        st.warning("📭 目前沒有課表資料")
    else:
        try:
            current_style = st.session_state.schedule_style
            df = st.session_state.schedule_data.copy().fillna("")
            
            # 根據風格設定 CSS
            if current_style == '像素遊戲':
                theme_color = "#2c3e50"
                font_import = "@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');"
                font_family = "'Press Start 2P', cursive"
                border_style = "4px solid #000"
                cell_bg = "#fff"
                header_bg = "#000"
                loc_style = "font-size:8px; color:#000; display:block; margin-top:5px;"
                
            elif current_style == '手繪筆記':
                theme_color = "#333"
                font_import = "@import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');"
                font_family = "'Patrick Hand', cursive"
                border_style = "2px solid #333"
                cell_bg = "#fff9c4" # 黃色便利貼底
                header_bg = "#333"
                loc_style = "font-size:12px; color:#555; background:rgba(255,255,255,0.5); padding:2px; border-radius:5px;"
                
            else: # 經典簡約 (預設)
                theme_color = "#6B8E78"
                font_import = ""
                font_family = "'Noto Sans TC', sans-serif"
                border_style = "1px solid #ddd"
                cell_bg = "#fff"
                header_bg = "#6B8E78"
                loc_style = "font-size:10px; color:#666; background:#f4f4f4; padding:1px 3px; border-radius:3px;"

            # 資料加工
            df['內容'] = (
                f'<div style="line-height:1.2;">'
                f'<b>' + df['活動名稱'] + '</b><br>'
                f'<span style="{loc_style}">' + df['地點'] + '</span>'
                f'</div>'
            )
            
            TARGET_DAYS = ['一', '二', '三', '四', '五']
            PERIOD_MAP = {'1': '08:10', '2': '09:10', '3': '10:20', '4': '11:20', '5': '12:20', '6': '13:20', '7': '14:20', '8': '15:30', '9': '16:30', '10': '17:30', 'A': '18:40', 'B': '19:35', 'C': '20:30', 'D': '21:25'}
            TARGET_PERIODS = list(PERIOD_MAP.keys())

            pivot_df = df.pivot_table(index='時間/節次', columns='星期', values='內容', aggfunc=lambda x: '<hr style="margin:2px 0; border-top:1px dashed #ccc;">'.join(x))
            pivot_df = pivot_df.fillna("").reindex(index=TARGET_PERIODS, columns=TARGET_DAYS, fill_value="")
            
            new_index = []
            for p in pivot_df.index:
                time_str = PERIOD_MAP.get(str(p), "")
                new_index.append(f"<div style='font-size:14px; font-weight:bold; color:{header_bg if current_style != '手繪筆記' else '#333'};'>{p}</div><div style='font-size:10px; color:#888;'>{time_str}</div>")
            
            pivot_df.index = new_index
            pivot_df.index.name = None 
            pivot_df = pivot_df.replace('nan', '', regex=False).replace('NaN', '', regex=False)
            
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                {font_import}
                body {{ font-family: {font_family}; margin: 0; padding: 0; }}
                .my-table {{ width: 100%; border-collapse: collapse; border-radius: { '0' if current_style == '像素遊戲' else '6px' }; overflow: hidden; font-size: 12px; table-layout: fixed; }}
                .my-table th {{ background-color: {header_bg}; color: white; padding: 8px 4px; text-align: center; border: {border_style}; width: 16%; }}
                .my-table tbody th {{ background-color: #f9f9f9; color: #555; width: 60px; font-weight: normal; vertical-align: middle; border: {border_style}; }}
                .my-table td {{ padding: 4px; border: {border_style}; text-align: center; vertical-align: middle; height: auto; background-color: {cell_bg}; word-wrap: break-word; }}
            </style>
            </head>
            <body>{table_html}</body>
            </html>
            """
            
            components.html(final_html, height=800, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")