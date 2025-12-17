import google.generativeai as genai
import streamlit as st
import time

# --- 設定與初始化 ---
def configure_genai():
    """
    設定 Gemini API 金鑰。
    優先嘗試讀取 Streamlit Secrets，如果失敗則回傳 False。
    """
    try:
        # 嘗試從 Streamlit Cloud Secrets 讀取
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        # 開發階段如果沒有設定 Secrets，可以在這裡 print 錯誤方便除錯
        print(f"⚠️ AI 金鑰設定失敗: {e}")
        return False

# --- 通用 AI 呼叫函式 (含錯誤處理) ---
def call_gemini_api(prompt, fallback_text=""):
    """
    封裝 API 呼叫過程，加入錯誤處理機制。
    如果 API 呼叫失敗，回傳 fallback_text 以免程式崩潰。
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # 使用輕量快速模型
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI 連線暫時無法使用: {e}")
        return fallback_text

# 1. 課綱生成 (AI 版)
def generate_course_topics(course_name):
    """
    根據課程名稱，讓 AI 猜測可能的 4 個單元主題。
    """
    prompt = (
        f"請針對大學課程「{course_name}」，列出 4 個可能的教學單元主題。"
        f"請直接回傳這 4 個主題，用逗號分隔，不要有其他廢話。"
        f"例如：基礎理論, 實務應用, 案例分析, 期末專題"
    )
    
    # 呼叫 AI
    result = call_gemini_api(prompt, fallback_text="課程導論, 核心概念, 進階應用, 專題實作")
    
    # 清洗資料 (處理 AI 可能回傳的額外符號)
    topics = [t.strip() for t in result.split(',') if t.strip()]
    
    # 確保至少回傳一個列表
    if not topics:
        return ["課程導論", "核心概念", "進階應用", "專題實作"]
    
    return topics[:4] # 最多取 4 個

# 2. 影片與預習推薦 (AI 版)
def recommend_videos(course, topic):
    """
    推薦 YouTube 關鍵字與核心觀念。
    """
    prompt = (
        f"我是大學生，正在修「{course}」。針對單元「{topic}」，請提供："
        f"1. 三個學習這單元的核心觀念 (Key Concepts)。"
        f"2. 三個適合在 YouTube 搜尋的精確關鍵字 (Search Keywords)。"
        f"請用 Markdown 格式列點呈現，語氣要像學長姐給建議一樣親切。"
    )
    
    fallback = f"### 推薦學習資源\n目前無法連線 AI，建議直接搜尋 **{topic}** 相關影片。"
    return call_gemini_api(prompt, fallback_text=fallback)

# 3. 學分計算 (保持邏輯運算，不需要 AI)
def calculate_credits(courses_data):
    """
    純邏輯計算，不需要用到 AI Token，保持原樣以節省資源。
    """
    total = 0
    details = []
    for c in courses_data:
        try:
            # 確保 hours 是數字，處理可能的錯誤資料
            hrs = int(c.get('hours', 0))
        except:
            hrs = 0
            
        name = c.get('name', '')
        # 判斷體育課 (通常是 2 小時 1 學分，或 0 學分，這裡依據你原本邏輯設為 hrs - 1)
        is_pe = any(k in name for k in ["體育", "球", "瑜珈", "游泳"])
        creds = max(0, hrs - 1) if is_pe else hrs
        
        total += creds
        details.append({"name": name, "is_pe": is_pe, "hours": hrs, "credits": creds})
        
    return {"total_credits": total, "details": details}

# === 4. 思維導圖生成邏輯 (升級為真正的 AI 生成) ===
def generate_mindmap_code(user_text):
    """
    將使用者的筆記文字，透過 AI 轉換為 Graphviz DOT 語言。
    這樣即使筆記很亂，AI 也能理解結構。
    """
    if not user_text.strip():
        return None

    # 強大的 Prompt，教 AI 寫 Graphviz
    prompt = f"""
    你是一個整理筆記的助手。請將以下使用者的筆記轉換為 Graphviz DOT 語言代碼。
    
    使用者筆記：
    {user_text}
    
    要求：
    1. 使用 'digraph G {{ ... }}' 格式。
    2. 設定 graph 為 rankdir=LR (由左至右)。
    3. 設定 node 樣式：shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78", fontname="Noto Sans CJK TC"。
    4. 請分析筆記的邏輯結構，找出「核心主題」當作根節點，其他細節作為子節點。
    5. 不要使用 Markdown 代碼區塊符號 (```)，直接回傳 DOT 代碼純文字。
    6. 確保所有中文都能正常顯示。
    """

    # 備用方案：如果 AI 掛了，回傳一個簡單的範例圖
    fallback_dot = """
    digraph G {
        rankdir=LR;
        node [fontname="Noto Sans CJK TC"];
        "系統" -> "連線失敗";
        "建議" -> "稍後再試";
    }
    """
    
    dot_code = call_gemini_api(prompt, fallback_text=fallback_dot)
    
    # 清理 AI 有時會雞婆加上的 Markdown 標記
    dot_code = dot_code.replace("```dot", "").replace("```", "").strip()
    
    return dot_code