import streamlit as st
import components
import ai_logic

def show():
    # 初始化狀態：預設模式為 'menu' (選單)
    if 'post_mode' not in st.session_state: st.session_state.post_mode = 'menu'
    
    # 標題區 (加入返回按鈕)
    c_title, c_back = st.columns([4, 1])
    with c_title:
        st.markdown("<h3 style='font-weight: 700; margin:0;'>課後總整</h3>", unsafe_allow_html=True)
    with c_back:
        # 如果不是在選單模式，顯示返回按鈕
        if st.session_state.post_mode != 'menu':
            if st.button("↩️ 返回選單", use_container_width=True):
                st.session_state.post_mode = 'menu'
                st.rerun()

    st.write("")

    # === 模式 A: 選單模式 (三個可點擊的卡片) ===
    if st.session_state.post_mode == 'menu':
        c1, c2, c3 = st.columns(3)
        
        # 為了模擬「點擊卡片」，我們用大按鈕
        with c1:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>📝</h2>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align:center;'>筆記整理</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#888;'>將雜亂筆記轉為重點</p>", unsafe_allow_html=True)
                if st.button("開啟 筆記整理", use_container_width=True, key="btn_note"):
                    st.session_state.post_mode = 'note'
                    st.rerun()

        with c2:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>🧠</h2>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align:center;'>思維導圖</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#888;'>文字自動轉成架構圖</p>", unsafe_allow_html=True)
                if st.button("開啟 思維導圖", use_container_width=True, key="btn_map"):
                    st.session_state.post_mode = 'mindmap'
                    st.rerun()
                    
        with c3:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>🤖</h2>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align:center;'>AI 助教</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#888;'>有問題隨時問我</p>", unsafe_allow_html=True)
                if st.button("開啟 AI 助教", use_container_width=True, key="btn_ai"):
                    st.session_state.post_mode = 'ai'
                    st.rerun()

    # === 模式 B: 功能放大模式 ===
    else:
        # 根據模式決定標題
        titles = {'note': '筆記整理', 'mindmap': '思維導圖', 'ai': 'AI 助教'}
        icons = {'note': '📝', 'mindmap': '🧠', 'ai': '🤖'}
        
        current = st.session_state.post_mode
        
        # 左右佈局：左輸入，右輸出
        c_left, c_right = st.columns([1, 1.2])
        
        with c_left:
            with components.interactive_card_container(f"{titles[current]} - 輸入", icons[current]):
                input_text = st.text_area("請輸入內容...", height=300, key=f"input_{current}")
                
                # 不同模式的按鈕文字
                btn_label = "⚡ 開始整理" if current == 'note' else "✨ 生成圖表" if current == 'mindmap' else "💬 發送訊息"
                
                if st.button(btn_label, use_container_width=True):
                    if input_text.strip():
                        with st.spinner("AI 思考中..."):
                            if current == 'note':
                                # 呼叫筆記整理
                                res = ai_logic.get_ai_response(f"請將筆記整理成 Markdown 重點：\n{input_text}")
                                st.session_state['res_note'] = res
                            elif current == 'mindmap':
                                # 呼叫思維導圖
                                code = ai_logic.generate_mindmap_code(input_text)
                                st.session_state['res_mindmap'] = code
                            elif current == 'ai':
                                # 呼叫對話
                                res = ai_logic.get_ai_response(f"學生問：{input_text}\n請用蘇格拉底教學法回答：")
                                st.session_state['res_ai'] = res
                            st.rerun()

        with c_right:
            with components.interactive_card_container("生成結果", "📄"):
                # 根據不同模式顯示結果
                if current == 'note' and 'res_note' in st.session_state:
                    st.markdown(st.session_state['res_note'])
                    
                elif current == 'mindmap' and 'res_mindmap' in st.session_state:
                    try:
                        st.graphviz_chart(st.session_state['res_mindmap'])
                    except:
                        st.error("圖表生成失敗")
                        
                elif current == 'ai' and 'res_ai' in st.session_state:
                    st.info(st.session_state['res_ai'])
                    
                else:
                    st.markdown("<div style='text-align:center; padding:50px; color:#ccc;'>結果將顯示於此</div>", unsafe_allow_html=True)