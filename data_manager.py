import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

JSON_FILE = 'google_key.json'
USER_DB_NAME = 'Unifocus_Database'

# 定義欄位
COLS_SCHEDULE = ['活動名稱', '地點', '星期', '時間/節次', '類型']
COLS_TASKS = ['活動名稱', '事項內容', '截止日期', '類型', '狀態']

def get_connection():
    if not os.path.exists(JSON_FILE): return None
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    client = gspread.authorize(creds)
    return client

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

# 為了相容性，保留此函式，但回傳空 DataFrame
def get_syllabus(course_name):
    return pd.DataFrame()
