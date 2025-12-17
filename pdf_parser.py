import pdfplumber
import pandas as pd
import re
import numpy as np

def parse_ntnu(uploaded_file):
    """
    解析台師大課表 PDF (智慧增強版)
    """
    if uploaded_file is None:
        return None

    all_data = []

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            # 通常課表在第一頁，但也許有多頁
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    # 資料清理：去除換行與多餘空白
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).replace('\n', '').strip() if cell else '' for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    if not cleaned_table: continue

                    # 嘗試抓取標題列 (Header)
                    headers = cleaned_table[0]
                    
                    # 智慧判斷欄位索引 (比 iloc 更安全)
                    try:
                        # 預設索引 (如果找不到就用猜的)
                        idx_name = 1
                        idx_room = 5
                        idx_time = 8 # 原始格式可能有差異，這裡主要依賴關鍵字搜尋
                        
                        # 動態搜尋欄位位置
                        for i, h in enumerate(headers):
                            if "科目名稱" in h or "課程中文名稱" in h: idx_name = i
                            elif "教室" in h or "地點" in h: idx_room = i
                            elif "時間" in h or "節次" in h: idx_time = i # 這裡我們主要抓整合的時間欄位

                        # 從第二行開始解析資料
                        for row in cleaned_table[1:]:
                            if len(row) < 5: continue # 跳過無效行
                            
                            course_name = row[idx_name]
                            classroom = row[idx_room]
                            # 有些 PDF 把星期、節次、時間分開，有些合併
                            # 為了通用，我們這裡假設有一欄包含完整的時間資訊，或者我們自己組合
                            
                            # 根據你的舊程式碼，我們主要關注怎麼把資料轉成新介面需要的格式
                            # 這裡我們使用更穩健的方法：重新抓取該行的「星期」與「節次」
                            
                            # 在台師大 PDF 中，通常有獨立的「星期」跟「節次」欄位
                            # 如果 headers 裡有，我們就用；沒有就嘗試用正則表達式解析 row 裡面的內容
                            
                            # 為了最快適配你的需求，我們保留你的邏輯但增強它：
                            # 尋找 row 裡面看起來像星期的欄位
                            week_str = ""
                            for cell in row:
                                if cell in ['一', '二', '三', '四', '五', '六', '日']:
                                    week_str = cell
                                    break
                            
                            # 尋找 row 裡面看起來像節次的欄位 (例如 "3-4" 或 "7")
                            periods = []
                            for cell in row:
                                # 匹配數字或範圍 (如 0-10, 3-4)
                                if re.match(r'^\d+(-\d+)?$', cell) or cell in ['A', 'B', 'C', 'D', '中午']:
                                    # 處理範圍 (例如 3-4 轉成 [3, 4])
                                    if '-' in cell:
                                        try:
                                            start, end = map(int, cell.split('-'))
                                            periods = [str(i) for i in range(start, end + 1)]
                                        except:
                                            periods = [cell] # 解析失敗就維持原樣
                                    else:
                                        periods = [cell]
                                    break # 找到節次就停
                            
                            # 如果這行有課名但沒抓到星期 (可能是合併儲存格)，這在 pdfplumber 有時難處理
                            # 這裡我們先假設格式標準，若無星期則略過或沿用上一個 (需外部邏輯)
                            # 簡單起見，若沒抓到星期，我們跳過
                            if not week_str or not periods: 
                                continue

                            # 展開節次 (讓課表填滿格子)
                            for p in periods:
                                all_data.append({
                                    '活動名稱': course_name,
                                    '地點': classroom,
                                    '星期': week_str,
                                    '時間/節次': str(p), # 這裡只存單一節次，方便 Pivot Table
                                    '類型': '學校課程'
                                })

                    except Exception as e:
                        print(f"Row Parse Error: {e}")
                        continue

        if not all_data: return None

        final_df = pd.DataFrame(all_data)
        # 移除重複
        final_df = final_df.drop_duplicates()
        
        return final_df

    except Exception as e:
        print(f"PDF Error: {e}")
        return None