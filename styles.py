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
        
        /* 調整頂部間距 */
        .block-container {{
            padding-top: 2rem !important; 
            padding-bottom: 2rem !important;
        }}

        /* 隱藏預設元素 */
        #MainMenu, footer, header {{visibility: hidden;}}
        
        /* 2. 導航列按鈕樣式 */
        .nav-btn {{ border: none; background: transparent; color: {COLOR_TEXT}; }}

        /* 3. 卡片樣式 (互動與靜態通用) */
        
        /* 針對 st.container(border=True) 的樣式覆寫 */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            border: none !important; /* 移除預設灰框 */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 16px; /* 內距 */
        }}
        
        /* 純 HTML 卡片容器 */
        .html-card-container {{
            background-color: {COLOR_CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            overflow: hidden;
            margin-bottom: 20px;
            height: 100%;
        }}
        
        /* 卡片標題區塊 (綠色) */
        .card-header-box {{
            background-color: {COLOR_MAIN};
            color: white;
            padding: 12px 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
        }}
        
        .html-card-body {{ padding: 20px; }}
        
        /* 4. 按鈕樣式 (強制綠色) */
        .stButton > button {{
            background-color: {COLOR_MAIN} !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .stButton > button:hover {{
            box-shadow: 0 4px 12px rgba(107, 142, 120, 0.3);
            opacity: 0.95;
        }}

        /* 5. Dashboard 頂部資訊 */
        .dashboard-info {{
            font-size: 1rem;
            color: #555;
            background: #E8F3EB;
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            border: 1px solid #D1E0D6;
        }}
        </style>
    """, unsafe_allow_html=True)