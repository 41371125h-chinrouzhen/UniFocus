# UniFocus：台師大智慧學習導航員 

## 專題提案—— 
[影片鏈接](https://youtu.be/aZ41LtePE0E)

## 網站指引
[網站網址](https://unifocus-s724bpbveb5cqwtjnpuvnm.streamlit.app/)

## 專題匯報
[YouTube](https://youtu.be/hDzHrMxe7U8)

## 📖 專案簡介 (Introduction)

大學生的學習生活充滿挑戰：課表查詢繁瑣、筆記散落各地、預習缺乏方向。Unifocus 利用 **Python Streamlit** 快速建構互動式網頁，結合 **Google Gemini** 與 **Groq (Llama 3)** 的雙模型 AI 架構，將被動的資訊查詢轉變為主動的學習引導。

## ✨ 核心功能 (Key Features)

### 1. 📅 智慧課表管理 (Smart Schedule)
- **PDF 自動解析**：支援台師大（NTNU）課表 PDF 一鍵匯入，利用 `pdfplumber` 自動清洗資料並視覺化。
- **沉浸式風格**：實作 CSS Injection，提供三種風格切換：
  - 🌿 **經典簡約**：清晰專業。
  - 👾 **像素遊戲**：復古 CRT 螢幕風格 (Pixel Art)。
  - ✏️ **手繪筆記**：擬真紙張與手寫字體風格。

### 2. 🤖 AI 學習大腦 (AI Assistant)
- **雙模型備援機制 (Resilience)**：優先呼叫 **Google Gemini 1.5 Flash**，若連線失敗或額度不足，自動切換至 **Groq (Llama 3)**，確保服務 99.9% 在線。
- **課前預習**：讀取課表，自動生成教學單元主題與推薦 YouTube 關鍵字。
- **課後總整**：
  - **筆記整理**：將雜亂筆記轉化為 Markdown 結構化重點。
  - **思維導圖**：利用 AI 生成 Graphviz DOT 代碼，即時繪製知識樹狀圖。

### 3. ☁️ 雲端同步與儀表板 (Cloud & Dashboard)
- **即時天氣建議**：串接 Open-Meteo API，結合天氣與當日課程，由 AI 生成貼心提醒。
- **資料漫遊**：整合 **Google Sheets API** 作為後端資料庫，實現帳號登入、課表存檔與倒數日設定的跨裝置同步。
- **專注工具**：內建番茄鐘計時器與學分計算機。

## 🛠️ 技術棧 (Tech Stack)

| 類別 | 技術/工具 | 用途 |
| :--- | :--- | :--- |
| **Frontend & App** | [Streamlit](https://streamlit.io/) | 網頁框架、狀態管理 (Session State) |
| **Data Processing** | Pandas, Numpy | 資料清洗、Pivot Table 轉換 |
| **File Parsing** | Pdfplumber | 解析非結構化 PDF 課表 |
| **Generative AI** | **Google Gemini API**<br>**Groq API** | 核心 AI 邏輯、備援機制 |
| **Database** | Google Sheets API<br>(Gspread, OAuth2) | NoSQL 風格的雲端資料儲存 |
| **Visualization** | Graphviz | 動態生成思維導圖 |
| **External API** | Open-Meteo | 即時天氣資訊 |

---
