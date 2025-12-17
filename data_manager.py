import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

# --- 1. 定義常數 ---
USER_DB_NAME = 'Unifocus_Database'
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']

# --- 2. 連線設定 ---
@st.cache_resource
def get_connection():
    """
    連線到 Google Sheets
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 嘗試從 Secrets 讀取 (Cloud 環境)
    if "gcp_service_account" in st.secrets:
        try:
            # 將 TOML 物件轉為 Python Dict
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            # 修正 private_key 的換行問題 (常見錯誤)
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client
        except Exception as e:
            st.error(f"Google Sheets 連線失敗: {e}")
            return None
            
    # 本地開發備用 (如果有 google_key.json)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
        return gspread.authorize(creds)
    except:
        st.error("找不到 Google 金鑰 (Secrets 或 google_key.json)")
        return None

def _get_worksheet(client, user_id):
    """取得或建立使用者的工作表"""
    try:
        sh = client.open(USER_DB_NAME)
    except gspread.SpreadsheetNotFound:
        try:
            sh = client.create(USER_DB_NAME)
            # 分享給你的 email (可選)
            # sh.share('your_email@gmail.com', perm_type='user', role='writer')
        except:
            return None

    # 嘗試開啟以 user_id 命名的分頁
    try:
        ws = sh.worksheet(user_id)
    except gspread.WorksheetNotFound:
        # 沒找到就新增一個
        ws = sh.add_worksheet(title=user_id, rows="100", cols="20")
        ws.append_row(COLS_SCHEDULE) # 寫入標題列
    return ws

# --- 3. 資料讀寫函式 (介面與 Supabase 版一致) ---

def load_user_data(user_id):
    """
    讀取使用者課表 (Google Sheets 版)
    """
    client = get_connection()
    if not client: return pd.DataFrame(columns=COLS_SCHEDULE), "Connection Error"

    try:
        ws = _get_worksheet(client, user_id)
        if not ws: return pd.DataFrame(columns=COLS_SCHEDULE), "Worksheet Error"

        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        # 處理空表格
        if df.empty:
            return pd.DataFrame(columns=COLS_SCHEDULE), "No Data"
        
        # 轉型為字串以避免格式問題
        df = df.astype(str)
        
        # 確保欄位齊全
        for col in COLS_SCHEDULE:
            if col not in df.columns:
                df[col] = ""
                
        return df[COLS_SCHEDULE], "Success"
        
    except Exception as e:
        return pd.DataFrame(columns=COLS_SCHEDULE), f"Error: {str(e)}"

def save_user_data(user_id, df):
    """
    儲存使用者課表 (Google Sheets 版)
    """
    client = get_connection()
    if not client: return False

    try:
        ws = _get_worksheet(client, user_id)
        
        # 清空舊資料
        ws.clear()
        
        # 寫入標題
        ws.append_row(COLS_SCHEDULE)
        
        # 寫入內容
        if not df.empty:
            # fillna 處理空值
            ws.append_rows(df.fillna("").values.tolist())
            
        return True
    except Exception as e:
        print(f"Google Sheet Save Error: {e}")
        return False