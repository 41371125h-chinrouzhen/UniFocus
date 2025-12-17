import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import streamlit as st

JSON_FILE = 'google_key.json'
USER_DB_NAME = 'Unifocus_Database'
SETTINGS_WS_NAME = 'User_Settings' # 新增：專門存設定的工作表

# 定義欄位
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']
COLS_SETTINGS = ['user_id', 'key', 'value'] # 設定表的欄位

def get_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if "gcp_service_account" in st.secrets:
        try:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            return gspread.authorize(creds)
        except: pass

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
            ws = sh.add_worksheet(title=ws_title, rows="1000", cols="10")
            ws.append_row(cols)
        else: return None
    return ws

# --- 課表存取 ---
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

# --- 新增：設定存取 (倒數日用) ---
def save_setting(username, key, value):
    client = get_connection()
    if not client: return False
    try:
        ws = _get_worksheet(client, USER_DB_NAME, SETTINGS_WS_NAME, COLS_SETTINGS)
        # 簡單作法：讀取全部 -> 更新 -> 重寫 (適合小量數據)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        # 確保 DataFrame 有欄位
        if df.empty: df = pd.DataFrame(columns=COLS_SETTINGS)
        
        # 檢查是否已有該設定
        mask = (df['user_id'] == username) & (df['key'] == key)
        if mask.any():
            df.loc[mask, 'value'] = str(value)
        else:
            new_row = pd.DataFrame([{'user_id': username, 'key': key, 'value': str(value)}])
            df = pd.concat([df, new_row], ignore_index=True)
            
        ws.clear()
        ws.append_row(COLS_SETTINGS)
        ws.append_rows(df.values.tolist())
        return True
    except Exception as e:
        print(f"Save Setting Error: {e}")
        return False

def load_settings(username):
    client = get_connection()
    if not client: return {}
    try:
        ws = _get_worksheet(client, USER_DB_NAME, SETTINGS_WS_NAME, COLS_SETTINGS)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        if df.empty: return {}
        
        # 篩選該使用者的設定
        user_df = df[df['user_id'] == username]
        return dict(zip(user_df['key'], user_df['value']))
    except: return {}