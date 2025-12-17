import streamlit as st
import components
import ai_logic
import graphviz

def show():
    # 標題
    st.markdown("<h3 style='font-weight: 700; margin:0;'>課後總整</h3>", unsafe_allow_html=True)
    st.write("") # 間距

    # 版面配置
    c1, c2, c3 = st.columns([1, 1, 0.8])
    
    # --- 左區塊：筆記整理 ---
    with c1:
        with components.interactive_card_container("筆記整理", "📝"):
            # 1. 輸入區
            user_note = st.text_area(
                "輸入原始筆記", 
                height=250, 
                placeholder="例如：\n老師說期中考會考指標(Pointer)\n還有記憶體位址的概念\nStack跟Heap的差別...",
                key="note_input"
            )
            
            # 2. 按鈕邏輯
            if st.button("⚡ 自動整理重點", use_container_width=True):
                if user_note.strip():
                    with st.spinner("AI 正在閱讀你的筆記..."):
                        # 呼叫 AI (這裡我們復用 ai_logic 的通用函式，請看下方說明)
                        # 暫時用簡單 prompt 測試，之後可以寫進 ai_logic
                        prompt = f"請將以下雜亂的筆記整理成清晰的條列式重點 (Markdown 格式)，並標註關鍵字：\n\n{user_note}"
                        response = ai_logic.get_ai_response(prompt)
                        
                        if response:
                            st.session_state['summary_result'] = response
                            st.rerun()
                        else:
                            st.error("AI 連線失敗，請稍後再試")
                else:
                    st.warning("請先輸入筆記內容")
            
            # 3. 顯示結果 (如果有)
            if 'summary_result' in st.session_state:
                st.markdown("---")
                st.markdown("#### 📄 整理結果")
                st.markdown(st.session_state['summary_result'])

    # --- 中區塊：思維導圖 ---
    with c2:
        with components.interactive_card_container("思維導圖", "🧠"):
            # 顯示區域
            mindmap_container = st.empty()
            
            # 如果已經有生成的圖，就顯示
            if 'mindmap_dot' in st.session_state:
                try:
                    mindmap_container.graphviz_chart(st.session_state['mindmap_dot'])
                except Exception as e:
                    mindmap_container.error(f"繪圖失敗: {e}")
            else:
                mindmap_container.markdown("""
                    <div style="height:200px; background:#F5F5F5; border-radius:8px; display:flex; justify-content:center; align-items:center; color:#aaa; margin-bottom:15px; border:1px solid #eee;">
                        圖表預覽區
                    </div>
                """, unsafe_allow_html=True)

            # 按鈕邏輯
            if st.button("✨ 生成架構圖", use_container_width=True):
                # 這裡需要讀取左邊輸入的筆記
                current_note = st.session_state.get("note_input", "")
                
                if current_note.strip():
                    with st.spinner("AI 正在構思架構圖..."):
                        # 呼叫 ai_logic 生成 DOT 碼
                        dot_code = ai_logic.generate_mindmap_code(current_note)
                        
                        if dot_code:
                            st.session_state['mindmap_dot'] = dot_code
                            st.rerun()
                        else:
                            st.error("AI 無法生成結構，請嘗試更具體的筆記內容")
                else:
                    st.warning("請在左側「筆記整理」區輸入內容")

    # --- 右區塊：AI 助教 ---
    with c3:
        components.html_card("AI 助教", "🤖", """
            <div style="height:310px; overflow-y:auto; padding-right:5px;">
                <div style="background:#E8F3EB; padding:12px; border-radius:10px 10px 10px 0; margin-bottom:10px; font-size:0.95rem; line-height:1.5;">
                    <strong>AI:</strong> 同學好！<br>
                    我是你的學習助手。把你上課聽不懂的地方貼在左邊，我幫你整理成重點和圖表！
                </div>
                <div style="text-align:center; color:#ccc; margin-top:20px;">
                    <small>更多對話功能開發中...</small>
                </div>
            </div>
        """)