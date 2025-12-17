import streamlit as st

# --- 顏色定義 (設計規範) ---
COLOR_BG = "#FDFBF7"      # 米白色底色
COLOR_MAIN = "#6B8E78"    # 主調綠色
COLOR_TEXT = "#333333"    # 深灰文字
COLOR_CARD_BG = "#FFFFFF" # 卡片白色背景

def load_css():
    st.markdown(f"""
        <style>
        /* 引入 Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

        /* 全域設定 */
        .stApp {{
            background-color: {COLOR_BG};
            font-family: 'Noto Sans TC', sans-serif;
            color: {COLOR_TEXT};
        }}

        /* 隱藏預設元素 */
        #MainMenu, footer, header {{visibility: hidden;}}

        /* =========================
           導航列樣式
        ========================= */
        .navbar-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0px;
            margin-bottom: 30px;
        }}
        .navbar-logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLOR_TEXT};
            display: flex;
            align-items: center;
        }}
        .navbar-logo span {{
            color: {COLOR_MAIN};
            margin-right: 8px;
            font-size: 1.8rem;
        }}
        .navbar-links {{
            display: flex;
            gap: 25px;
            align-items: center;
        }}
        .nav-link {{
            color: {COLOR_TEXT};
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
            cursor: pointer;
            padding-bottom: 5px;
            transition: color 0.3s;
        }}
        .nav-link:hover {{
            color: {COLOR_MAIN};
        }}
        .nav-link.active {{
            color: {COLOR_MAIN};
            border-bottom: 2px solid {COLOR_MAIN};
        }}
        .user-avatar {{
            background-color: #A89B93;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            margin-left: 20px;
        }}

        /* =========================
           卡片通用樣式
        ========================= */
        /* 純 HTML 卡片 */
        .html-card {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            overflow: hidden;
            margin-bottom: 20px;
            height: 100%;
        }}
        
        /* 互動卡片容器 (Hack Streamlit VerticalBlock) */
        div[data-testid="stVerticalBlock"] > div:has(> .card-header-marker) {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding-bottom: 20px;
            border: none;
        }}

        /* 卡片標題列 */
        .card-header, .card-header-marker {{
            background-color: {COLOR_MAIN};
            color: white;
            padding: 12px 20px;
            font-weight: 700;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 10px;
            border-radius: 16px 16px 0 0; /* 確保上方圓角 */
        }}
        
        .card-body {{
            padding: 20px;
        }}

        /* 輸入框與按鈕優化 */
        [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input, [data-testid="stDateInput"] input {{
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            padding: 8px 12px;
        }}
        .stButton > button {{
            background-color: {COLOR_MAIN} !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
            font-weight: 700;
            width: 100%;
        }}
        
        /* 特定樣式 */
        .weather-temp {{ font-size: 2.5rem; font-weight: 700; line-height: 1.2; }}
        .credit-number {{ font-size: 4rem; font-weight: 700; color: {COLOR_MAIN}; text-align: center; }}
        .countdown-number {{ font-size: 3.5rem; font-weight: 700; color: #E67E22; text-align: center; }}
        
        </style>
    """, unsafe_allow_html=True)