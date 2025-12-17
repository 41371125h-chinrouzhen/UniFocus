import streamlit as st

# --- 顏色定義 ---
COLOR_BG = "#FDFBF7"      # 米白色底色
COLOR_MAIN = "#6B8E78"    # 主調綠色 (Unifocus Green)
COLOR_TEXT = "#333333"    # 深灰文字
COLOR_CARD_BG = "#FFFFFF" # 卡片白色背景
COLOR_ACCENT = "#E67E22"  # 提醒色 (橘)

def load_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

        /* 全域設定 */
        .stApp {{
            background-color: {COLOR_BG};
            font-family: 'Noto Sans TC', sans-serif;
            color: {COLOR_TEXT};
        }}

        /* 隱藏 Streamlit 預設元素 */
        #MainMenu, footer, header {{visibility: hidden;}}
        
        /* 移除按鈕預設邊框，讓它看起來像文字連結 */
        .nav-btn {{
            border: none;
            background: transparent;
            color: {COLOR_TEXT};
            font-weight: 500;
            padding: 0;
        }}
        .nav-btn:hover {{
            color: {COLOR_MAIN};
        }}

        /* 通用卡片樣式 */
        .html-card {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 0;
            margin-bottom: 20px;
            overflow: hidden;
            height: 100%;
        }}
        
        .card-header {{
            background-color: {COLOR_MAIN};
            color: white;
            padding: 12px 20px;
            font-weight: 700;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-body {{
            padding: 20px;
        }}

        /* 互動卡片容器修正 */
        div[data-testid="stVerticalBlock"] > div:has(> .card-marker) {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 0px;
            overflow: hidden;
            border: none;
        }}

        /* 按鈕樣式優化 */
        .stButton > button {{
            background-color: {COLOR_MAIN};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 16px; 
            transition: all 0.3s;
        }}
        .stButton > button:hover {{
            box-shadow: 0 4px 10px rgba(107, 142, 120, 0.4);
        }}

        /* 登入頁面特效 */
        .login-title {{
            font-size: 4rem; 
            font-weight: bold; 
            color: {COLOR_MAIN}; 
            text-align: center;
            margin-bottom: 20px;
            font-family: 'Times New Roman', serif; /* 模擬參考圖的字體 */
            font-style: italic;
        }}
        </style>
    """, unsafe_allow_html=True)