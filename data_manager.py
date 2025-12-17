import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import streamlit as st

JSON_FILE = 'google_key.json'
USER_DB_NAME = 'Unifocus_Database'

# 定義欄位
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']
COLS_TASKS = ['活動名稱', '事項內容', '截止日期', '類型', '狀態']

def get_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 1. 優先嘗試 Streamlit Secrets (雲端環境)
    if "gcp_service_account" in st.secrets:
        try:
            creds_dict = dict(st.secrets["gcp_service_account"])
            # 修正 TOML 換行問題
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            return gspread.authorize(creds)
        except:
            pass

    # 2. 其次嘗試本地檔案 (你原本的 Colab 程式碼)
    if os.path.exists(JSON_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
        client = gspread.authorize(creds)
        return client
        
    return None

def _get_worksheet(client, wb_name, ws_title, cols=None):
    try:
        sh = client.open(wb_name)
    except gspread.SpreadsheetNotFound:
        if wb_name == USER_DB_NAME: sh = client.create(wb_name)
        else: return None
    try:
        ws = sh.worksheet(ws_title)
    except gspread.WorksheetNotFound:
        if cols:
            ws = sh.add_worksheet(title=ws_title, rows="100", cols="20")
            ws.append_row(cols)
        else: return None
    return ws

def load_user_data(username):
    client = get_connection()
    if not client: return None, "金鑰錯誤"
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