import streamlit as st
import components
import ai_logic
import pandas as pd

def show():
    st.markdown("<h3 style='font-weight: 700; margin:0;'>課前預習</h3>", unsafe_allow_html=True)
    
    # 取得課程列表 (從課表資料庫中抓取)
    course_list = []
    if not st.session_state.schedule_data.empty:
        # 抓取「活動名稱」欄位並去除重複
        course_list = st.session_state.schedule_data['活動名稱'].unique().tolist()
    
    if not course_list:
        course_list = ["(無資料) 請先匯入課表"]

    # 初始化 Session State 用於儲存 AI 生成的主題 (避免每次重整都重新生成)
    if 'prestudy_topics' not in st.session_state:
        st.session_state.prestudy_topics = {}

    c1, c2 = st.columns([1, 1.2])
    
    # --- 左側：設定 ---
    with c1:
        with components.interactive_card_container("課程設定", "🔍"):
            # 1. 選擇課程
            selected_course = st.selectbox("選擇課程", course_list)
            
            # 2. 自動生成/顯示主題選項
            topic_options = ["(請先選擇課程)"]
            
            if selected_course != "(無資料) 請先匯入課表":
                # 如果還沒生成過這個課程的主題，就呼叫 AI
                if selected_course not in st.session_state.prestudy_topics:
                    with st.spinner(f"AI 正在分析「{selected_course}」的預習單元..."):
                        # 呼叫 ai_logic 生成 4 個主題
                        topics = ai_logic.generate_course_topics(selected_course)
                        st.session_state.prestudy_topics[selected_course] = topics
                
                # 讀取已生成的主題
                topic_options = st.session_state.prestudy_topics.get(selected_course, []) + ["✏️ 其他 (自訂主題)"]

            # 3. 選擇或輸入主題
            selected_topic_opt = st.radio("選擇預習單元", topic_options)
            
            final_topic = selected_topic_opt
            if selected_topic_opt == "✏️ 其他 (自訂主題)":
                final_topic = st.text_input("輸入自訂主題", placeholder="例如：期中考複習")

            st.write("")
            if st.button("✨ 生成預習指南", use_container_width=True):
                if final_topic and "請先選擇" not in final_topic:
                    with st.spinner("AI 正在尋找學習資源..."):
                        res = ai_logic.recommend_videos(selected_course, final_topic)
                        st.session_state['prestudy_result'] = res
                else:
                    st.warning("請選擇有效的課程與主題")
    
    # --- 右側：AI 結果 ---
    with c2:
        # 這裡放置結果
        content = st.session_state.get('prestudy_result', """
            <div style="color:#888; text-align:center; padding:60px; background:#f9f9f9; border-radius:8px;">
                <h4 style="color:#6B8E78; margin-bottom:10px;">👋 準備好開始預習了嗎？</h4>
                <p>請在左側選擇課程，<br>AI 會自動列出單元供您選擇。</p>
            </div>
        """)
        
        # 使用 unsafe_allow_html=True 確保 Markdown 渲染正確 (如果 ai_logic 回傳的是 md)
        # 為了美觀，我們用一個簡單的容器包住它
        with components.interactive_card_container("AI 學習指南", "📚"):
            st.markdown(content, unsafe_allow_html=True)