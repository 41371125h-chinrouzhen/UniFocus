import pdfplumber
import pandas as pd
import numpy as np

def parse_ntnu(file):
    try:
        with pdfplumber.open(file) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            if not tables: return None
            
            table_data = tables[0]
            # 清理資料：去除換行符號
            cleaned_data = [[cell.replace('\n', ' ').strip() if cell else '' for cell in row] for row in table_data if any(cell and cell.strip() for cell in row)]
            
            # 建立 DataFrame (假設標準格式)
            # 這裡的欄位名稱是對應 NTNU 選課系統輸出的 PDF
            raw_columns = ['課程中文名稱', '上課教室', '星期', '節次', '上課時間']
            
            # 嘗試抓取對應欄位，若格式不同可能需要調整
            # 這裡做一個簡單的容錯，假設前幾欄就是我們需要的
            try:
                df = pd.DataFrame(cleaned_data[1:], columns=raw_columns)
            except:
                # 如果欄位對不上，嘗試用索引取值
                df = pd.DataFrame(cleaned_data[1:])
                df = df.iloc[:, [1, 5, 6, 7, 8]] # 假設的欄位位置，需視實際PDF調整
                df.columns = raw_columns

            # 處理合併儲存格 (填補星期)
            df['星期'] = df['星期'].replace('', np.nan).fillna(method='ffill')
            
            final_df = pd.DataFrame()
            final_df['活動名稱'] = df['課程中文名稱']
            final_df['地點'] = df['上課教室'].apply(lambda x: x.replace(' ', '') if x else x)
            final_df['星期'] = df['星期']
            final_df['時間/節次'] = df['節次'] + " (" + df['上課時間'] + ")"
            final_df['類型'] = '學校課程'
            
            return final_df
    except Exception as e:
        print(f"PDF Parse Error: {e}")
        return None
