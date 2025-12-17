import streamlit as st

# --- 顏色定義 ---
COLOR_BG = "#FDFBF7"      # 米白色底色
COLOR_MAIN = "#6B8E78"    # 主調綠色
COLOR_TEXT = "#333333"    # 深灰文字
COLOR_CARD_BG = "#FFFFFF" # 卡片白色背景

def load_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

        /* 1. 全域設定 & 減少頂部留白 */
        .stApp {{
            background-color: {COLOR_BG};
            font-family: 'Noto Sans TC', sans-serif;
            color: {COLOR_TEXT};
        }}
        
        /* 關鍵：將內容往上移 */
        .block-container {{
            padding-top: 1.5rem !important; 
            padding-bottom: 2rem !important;
            max-width: 95% !important; /* 讓寬度稍微寬一點 */
        }}

        /* 隱藏預設元素 */
        #MainMenu, footer, header {{visibility: hidden;}}
        
        /* 2. 導航列按鈕樣式 */
        .nav-btn {{
            border: none;
            background: transparent;
            color: {COLOR_TEXT};
            font-weight: 500;
            padding: 0;
        }}

        /* 3. 卡片通用樣式 (修復互動卡片) */
        
        /* 覆寫 st.container(border=True) 的樣式，讓它變成我們的卡片 */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            border: none !important; /* 移除預設灰框 */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 0 !important;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        
        /* 卡片標題區塊 */
        .card-header-box {{
            background-color: {COLOR_MAIN};
            color: white;
            padding: 12px 20px;
            font-weight: 700;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px; /* 標題跟內容的距離 */
        }}
        
        /* 4. 按鈕樣式 (包含匯入、下載等) */
        .stButton > button {{
            background-color: {COLOR_MAIN} !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            height: auto;
            padding: 8px 16px;
            transition: all 0.3s;
        }}
        .stButton > button:hover {{
            box-shadow: 0 4px 10px rgba(107, 142, 120, 0.4);
            opacity: 0.9;
        }}

        /* 5. 純 HTML 卡片修正 */
        .html-card-container {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            overflow: hidden;
            margin-bottom: 20px;
            height: 100%;
        }}
        .html-card-body {{
            padding: 20px;
        }}
        
        /* Dashboard 頂部資訊 */
        .dashboard-info {{
            font-size: 1rem;
            color: #666;
            background: #E8F3EB;
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)