import streamlit as st
import components
import ai_logic

def show():
    if 'post_mode' not in st.session_state: st.session_state.post_mode = 'menu'
    
    # 初始化聊天記錄
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "同學好！我是你的 AI 助教，有什麼課業問題都可以問我喔！"}]

    c_title, c_back = st.columns([4, 1])
    with c_title: st.markdown("<h3 style='font-weight: 700; margin:0;'>課後總整</h3>", unsafe_allow_html=True)
    with c_back:
        if st.session_state.post_mode != 'menu':
            if st.button("↩️ 返回", use_container_width=True):
                st.session_state.post_mode = 'menu'
                st.rerun()

    st.write("")

    # === 模式 A: 選單 ===
    if st.session_state.post_mode == 'menu':
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>📝</h2><h4 style='text-align:center;'>筆記整理</h4>", unsafe_allow_html=True)
                if st.button("開啟", key="btn_note", use_container_width=True): st.session_state.post_mode = 'note'; st.rerun()
        with c2:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>🧠</h2><h4 style='text-align:center;'>思維導圖</h4>", unsafe_allow_html=True)
                if st.button("開啟", key="btn_map", use_container_width=True): st.session_state.post_mode = 'mindmap'; st.rerun()
        with c3:
            with st.container(border=True):
                st.markdown("<h2 style='text-align:center;'>🤖</h2><h4 style='text-align:center;'>AI 助教</h4>", unsafe_allow_html=True)
                if st.button("開啟", key="btn_ai", use_container_width=True): st.session_state.post_mode = 'ai'; st.rerun()

    # === 模式 B: 功能 ===
    elif st.session_state.post_mode == 'ai':
        # --- AI 真實對話視窗 ---
        with components.interactive_card_container("AI 助教 (問答模式)", "🤖"):
            # 顯示歷史訊息
            for msg in st.session_state.chat_history:
                st.chat_message(msg["role"]).write(msg["content"])

            # 輸入框
            if prompt := st.chat_input("輸入你的問題..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                
                with st.spinner("AI 思考中..."):
                    response = ai_logic.get_ai_response(prompt, system_instruction="你是一個蘇格拉底式的教學助教，引導學生思考。")
                    
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

    else:
        # 其他功能 (筆記 & 思維導圖)
        current = st.session_state.post_mode
        titles = {'note': '筆記整理', 'mindmap': '思維導圖'}
        icons = {'note': '📝', 'mindmap': '🧠'}
        
        c_left, c_right = st.columns([1, 1.2])
        
        with c_left:
            with components.interactive_card_container(f"{titles[current]} - 輸入", icons[current]):
                input_text = st.text_area("輸入內容...", height=300, key=f"in_{current}")
                btn = "⚡ 整理" if current == 'note' else "✨ 生成圖表"
                if st.button(btn, use_container_width=True):
                    if input_text:
                        with st.spinner("生成中..."):
                            if current == 'note':
                                st.session_state['res_note'] = ai_logic.get_ai_response(f"整理成Markdown重點：\n{input_text}")
                            else:
                                st.session_state['res_map'] = ai_logic.generate_mindmap_code(input_text)
                            st.rerun()

        with c_right:
            with components.interactive_card_container("結果", "📄"):
                if current == 'note' and 'res_note' in st.session_state:
                    st.markdown(st.session_state['res_note'])
                elif current == 'mindmap' and 'res_map' in st.session_state:
                    st.graphviz_chart(st.session_state['res_map'])
                else:
                    st.markdown("<div style='text-align:center; padding:50px; color:#ccc;'>結果區</div>", unsafe_allow_html=True)