import streamlit as st
import components

def show():
    st.markdown("<h3 style='font-weight: 700;'>課後總整</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 0.8])
    
    with c1:
        with components.interactive_card_container("筆記整理", "📝"):
            st.text_area("輸入原始筆記", height=250, placeholder="在這裡貼上你的雜亂筆記，AI 會幫你整理成條列式重點...")
            st.button("⚡ 自動整理重點", use_container_width=True)

    with c2:
        with components.interactive_card_container("思維導圖", "🧠"):
            st.markdown("""
                <div style="height:200px; background:#F5F5F5; border-radius:8px; display:flex; justify-content:center; align-items:center; color:#aaa; margin-bottom:15px; border:1px solid #eee;">
                    圖表預覽區
                </div>
            """, unsafe_allow_html=True)
            st.button("✨ 生成架構圖", use_container_width=True)

    with c3:
        # AI 助教保留為 HTML 卡片，因為它主要是顯示對話框 (未來可改互動)
        components.html_card("AI 助教", "🤖", """
            <div style="height:310px; overflow-y:auto;">
                <div style="background:#E8F3EB; padding:10px; border-radius:10px 10px 10px 0; margin-bottom:10px; font-size:0.9rem;">
                    <strong>AI:</strong> 同學好！這週的「指標」概念比較抽象，需要我舉個例子嗎？
                </div>
                <div style="text-align:center; color:#ccc; margin-top:20px;">
                    <small>更多對話功能開發中...</small>
                </div>
            </div>
        """)