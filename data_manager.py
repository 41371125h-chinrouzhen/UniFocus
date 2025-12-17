import streamlit as st
from supabase import create_client
import pandas as pd
import json

# --- 1. 定義資料庫常數 ---
TABLE_NAME = "schedules" 

# 定義 DataFrame 欄位結構 (必須與前端顯示對應)
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']

# --- 2. 連線設定 ---
@st.cache_resource
def init_connection():
    """
    初始化 Supabase 連線
    使用 cache 避免每次重新整理都重連
    """
    try:
        # 確保你的 .streamlit/secrets.toml 裡有 [supabase] 區塊
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ 資料庫連線失敗: {e}")
        return None

# --- 3. 資料讀寫函式 ---

def load_user_data(user_id):
    """
    讀取使用者課表
    """
    supabase = init_connection()
    if not supabase:
        return pd.DataFrame(columns=COLS_SCHEDULE), "Connection Error"

    try:
        # 查詢資料庫
        response = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id).execute()
        
        # 檢查是否有資料
        if response.data and len(response.data) > 0:
            # 取得 JSON 並轉回 DataFrame
            json_data = response.data[0]['schedule_json']
            if json_data:
                df = pd.DataFrame(json_data)
                # 確保欄位齊全
                for col in COLS_SCHEDULE:
                    if col not in df.columns:
                        df[col] = ""
                return df[COLS_SCHEDULE], "Success"
        
        # 沒資料回傳空表
        return pd.DataFrame(columns=COLS_SCHEDULE), "No Data"

    except Exception as e:
        return pd.DataFrame(columns=COLS_SCHEDULE), f"Error: {str(e)}"

def save_user_data(user_id, df):
    """
    儲存使用者課表 (Upsert: 更新或新增)
    """
    supabase = init_connection()
    if not supabase: return False

    try:
        # 1. 轉為 JSON 格式 (處理 NaN)
        schedule_json = df.fillna("").to_dict(orient='records')
        
        # 2. 準備寫入資料
        data = {
            "user_id": user_id,
            "schedule_json": schedule_json
        }
        
        # 3. 執行寫入
        supabase.table(TABLE_NAME).upsert(data, on_conflict="user_id").execute()
        return True
    except Exception as e:
        print(f"Save Error: {e}")
        return False