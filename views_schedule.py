# ... (前面的 import 和 上傳邏輯不變) ...

    # --- 4. 顯示課表主體 ---
    st.write("") # 間距
    
    if st.session_state.schedule_data.empty:
        # ... (空狀態顯示不變) ...
        pass
    else:
        try:
            df = st.session_state.schedule_data.copy()
            
            # Pivot Table 邏輯 (保持不變)
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
            
            # === CSS 美化 (讓表格變漂亮) ===
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
                    background-color: #6B8E78; /* 綠色表頭 */
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    text-align: center;
                    border-bottom: 2px solid #5a7a66;
                }
                .schedule-table tbody tr th {
                    background-color: #f9f9f9; /* 左側節次欄灰底 */
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
                    height: 100px; /* 固定高度讓格子整齊 */
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