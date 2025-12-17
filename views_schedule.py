import streamlit as st
import pandas as pd
import data_manager
import pdf_parser
import time
import streamlit.components.v1 as components

def show():
    if 'show_upload' not in st.session_state: st.session_state.show_upload = False
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

    # --- 設計區 ---
    if st.session_state.get('show_design', False):
        with st.container(border=True):
            st.markdown("#### 🎨 選擇沉浸式風格")
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
            
            # === 定義進階 CSS 樣式 ===
            if current_style == '像素遊戲':
                font_import = "@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');"
                font_family = "'Press Start 2P', cursive"
                # 復古 CRT 螢幕網格背景
                bg_style = """
                    background-color: #000;
                    background-image: linear-gradient(rgba(0, 255, 0, 0.1) 1px, transparent 1px),
                                      linear-gradient(90deg, rgba(0, 255, 0, 0.1) 1px, transparent 1px);
                    background-size: 20px 20px, 20px 20px;
                    border: 4px solid #33ff00;
                    box-shadow: 0 0 20px rgba(51, 255, 0, 0.5);
                    padding: 20px;
                """
                text_color = "#33ff00"
                header_bg = "#000"
                border_color = "#33ff00"
                cell_bg = "transparent"
                loc_bg = "#33ff00"; loc_text = "#000"
                
            elif current_style == '手繪筆記':
                font_import = "@import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');"
                font_family = "'Patrick Hand', cursive"
                # 擬真筆記本橫線紙背景
                bg_style = """
                    background-color: #fffbf0;
                    background-image: repeating-linear-gradient(transparent, transparent 23px, #e5e0d8 24px);
                    border: 1px solid #ddd;
                    box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
                    transform: rotate(-1deg); /* 稍微傾斜增加真實感 */
                    padding: 25px;
                """
                text_color = "#333"
                header_bg = "transparent"
                border_color = "#555"
                cell_bg = "transparent"
                loc_bg = "rgba(255,255,0,0.3)"; loc_text = "#555" # 螢光筆效果
                
            else: # 經典簡約
                font_import = "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap');"
                font_family = "'Noto Sans TC', sans-serif"
                bg_style = "background: white; padding: 0;"
                text_color = "#333"
                header_bg = "#6B8E78"
                border_color = "#ddd"
                cell_bg = "white"
                loc_bg = "#f4f4f4"; loc_text = "#666"

            # 資料加工
            df['內容'] = (
                f'<div style="line-height:1.3;">'
                f'<b style="font-size:1.1em;">' + df['活動名稱'] + '</b><br>'
                f'<span style="font-size:0.85em; color:{loc_text}; background:{loc_bg}; padding:2px 4px; border-radius:4px;">' + df['地點'] + '</span>'
                f'</div>'
            )
            
            TARGET_DAYS = ['一', '二', '三', '四', '五']
            PERIOD_MAP = {'1': '08:10', '2': '09:10', '3': '10:20', '4': '11:20', '5': '12:20', '6': '13:20', '7': '14:20', '8': '15:30', '9': '16:30', '10': '17:30', 'A': '18:40', 'B': '19:35', 'C': '20:30', 'D': '21:25'}
            TARGET_PERIODS = list(PERIOD_MAP.keys())

            pivot_df = df.pivot_table(index='時間/節次', columns='星期', values='內容', aggfunc=lambda x: '<hr style="margin:4px 0; border:0; border-top:1px dashed ' + border_color + ';">'.join(x))
            pivot_df = pivot_df.fillna("").reindex(index=TARGET_PERIODS, columns=TARGET_DAYS, fill_value="")
            
            new_index = []
            for p in pivot_df.index:
                time_str = PERIOD_MAP.get(str(p), "")
                new_index.append(f"<div style='font-size:1.2em; font-weight:bold;'>{p}</div><div style='font-size:0.8em; opacity:0.8;'>{time_str}</div>")
            
            pivot_df.index = new_index
            pivot_df.index.name = None 
            pivot_df = pivot_df.replace('nan', '', regex=False).replace('NaN', '', regex=False)
            
            table_html = pivot_df.to_html(classes="my-table", escape=False)
            
            # 組合最終 HTML
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                {font_import}
                body {{ font-family: {font_family}; margin: 0; padding: 20px; background:transparent; }}
                /* 外層容器，負責背景紋理和整體風格 */
                .schedule-container {{
                    {bg_style}
                    border-radius: 12px;
                    overflow: hidden;
                    color: {text_color};
                }}
                .my-table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
                
                /* 表頭樣式差異化 */
                .my-table thead th {{ 
                    background-color: {header_bg}; 
                    color: {'#33ff00' if current_style == '像素遊戲' else text_color if current_style == '手繪筆記' else 'white'};
                    padding: 12px 4px; 
                    text-align: center; 
                    border-bottom: 2px solid {border_color}; 
                    {'border-top: 2px solid ' + border_color if current_style == '手繪筆記' else ''};
                    width: 16%;
                    font-size: 1.1em;
                }}
                
                /* 左側節次欄 */
                .my-table tbody th {{ 
                    background-color: { 'transparent' if current_style != '經典簡約' else '#f9f9f9'}; 
                    color: {text_color}; 
                    width: 70px; 
                    vertical-align: middle; 
                    border-right: 2px solid {border_color}; 
                    text-align: center;
                }}
                
                /* 內容儲存格 */
                .my-table td {{ 
                    padding: 8px; 
                    border: 1px solid {border_color}; 
                    text-align: center; 
                    vertical-align: middle; 
                    height: auto; 
                    background-color: {cell_bg}; 
                    word-wrap: break-word; 
                }}
                
                /* 像素風特殊處理：移除內部邊框，只留網格背景 */
                {'.my-table td, .my-table th { border: none !important; }' if current_style == '像素遊戲' else ''}
                
            </style>
            </head>
            <body>
                <div class="schedule-container">
                    <div style="overflow-x:auto;">
                        {table_html}
                    </div>
                </div>
            </body>
            </html>
            """
            
            components.html(final_html, height=850, scrolling=True)

        except Exception as e:
            st.error(f"顯示錯誤: {e}")