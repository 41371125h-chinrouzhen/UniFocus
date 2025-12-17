import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import streamlit as st # 記得引入 streamlit

# --- 1. 定義資料庫常數 ---
JSON_FILE = 'google_key.json'
USER_DB_NAME = 'Unifocus_Database'

# 定義欄位結構
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']
COLS_TASKS = ['活動名稱', '事項內容', '截止日期', '類型', '狀態']

# --- 2. 連線設定 (關鍵修改處) ---
def get_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # A計畫：優先嘗試從 Streamlit Secrets 讀取 (部署環境)
    if "gcp_service_account" in st.secrets:
        try:
            # 將 TOML 設定轉回 Dictionary 格式給 gspread 使用
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client
        except Exception as e:
            print(f"Secrets 連線失敗: {e}")
            return None

    # B計畫：從檔案讀取 (Colab/本地環境)
    elif os.path.exists(JSON_FILE):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
            client = gspread.authorize(creds)
            return client
        except: return None
        
    else:
        return None

def _get_worksheet(client, wb_name, ws_title, cols=None):
    """通用開啟工作表函式"""
    try:
        sh = client.open(wb_name)
    except gspread.SpreadsheetNotFound:
        if wb_name == USER_DB_NAME: 
            sh = client.create(wb_name)
        else:
            return None 

    try:
        ws = sh.worksheet(ws_title)
    except gspread.WorksheetNotFound:
        if cols: 
            ws = sh.add_worksheet(title=ws_title, rows="100", cols="20")
            ws.append_row(cols)
        else:
            return None
    return ws

# --- 3. 資料讀寫函式 ---
def load_user_data(username):
    client = get_connection()
    if not client: return None, "資料庫連線失敗 (請檢查 Secrets)"
    try:
        ws = _get_worksheet(client, USER_DB_NAME, username, COLS_SCHEDULE)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        if df.empty: df = pd.DataFrame(columns=COLS_SCHEDULE)
        else: df = df.astype(str)
        return df, "Success"
    except Exception as e: return None, str(e)

def save_user_data(username, df):
    client = get_connection()
    if not client: return False
    try:
        ws = _get_worksheet(client, USER_DB_NAME, username, COLS_SCHEDULE)
        ws.clear()
        ws.append_row(COLS_SCHEDULE)
        if not df.empty: ws.append_rows(df.values.tolist())
        return True
    except: return False

def get_syllabus(course_name):
    return pd.DataFrame()
