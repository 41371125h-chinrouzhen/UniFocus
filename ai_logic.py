import google.generativeai as genai
import streamlit as st
import time
from groq import Groq

# --- 初始化設定 ---
def configure_genai():
    """
    只需確認金鑰是否存在於 Secrets 中
    """
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    return False

# --- 核心：AI 呼叫路由器 (Router) ---
def get_ai_response(prompt, system_instruction=None):
try:
        # 修改這裡：使用你清單中的最新模型名稱
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e_gemini:
        print(f"⚠️ Gemini 連線失敗，切換備援: {e_gemini}")
        
        # === 第二關：Groq (Llama 3) ===
        try:
            if "GROQ_API_KEY" in st.secrets:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction or "You are a helpful study assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-8b-8192", # 使用 Llama 3 8B 模型，速度極快
                )
                return chat_completion.choices[0].message.content
            else:
                print("⚠️ 未設定 Groq Key，跳過備援")
        except Exception as e_groq:
            print(f"❌ Groq 連線也失敗: {e_groq}")
    
    # === 第三關：全面棄守 ===
    return None

# --- 功能 1: 課綱生成 ---
def generate_course_topics(course_name):
    prompt = (
        f"請針對大學課程「{course_name}」，列出 4 個可能的教學單元主題。"
        f"請直接回傳這 4 個主題，用逗號分隔，不要有其他廢話。"
        f"例如：基礎理論, 實務應用, 案例分析, 期末專題"
    )
    
    result = get_ai_response(prompt)
    
    # 備用資料 (如果 AI 全掛了)
    if not result:
        return ["課程導論", "核心概念", "進階應用", "專題實作"]
    
    # 資料清洗
    topics = [t.strip() for t in result.replace("，", ",").split(',') if t.strip()]
    return topics[:4] if topics else ["課程導論", "核心概念", "進階應用", "專題實作"]

# --- 功能 2: 影片與預習推薦 ---
def recommend_videos(course, topic):
    prompt = (
        f"我是大學生，正在修「{course}」。針對單元「{topic}」，請提供："
        f"1. 三個學習這單元的核心觀念 (Key Concepts)。"
        f"2. 三個適合在 YouTube 搜尋的精確關鍵字 (Search Keywords)。"
        f"請用 Markdown 格式列點呈現，語氣要像學長姐給建議一樣親切。"
    )
    
    result = get_ai_response(prompt, system_instruction="你是一個熱心的大學助教。")
    
    if not result:
        return f"### ⚠️ 系統離線\n目前 AI 服務忙碌中，建議直接至 YouTube 搜尋 **{topic}**。"
        
    return result

# --- 功能 3: 學分計算 (不需要 AI) ---
def calculate_credits(courses_data):
    total = 0
    details = []
    for c in courses_data:
        try:
            hrs = int(c.get('hours', 0))
        except:
            hrs = 0
        name = c.get('name', '')
        is_pe = any(k in name for k in ["體育", "球", "瑜珈", "游泳"])
        creds = max(0, hrs - 1) if is_pe else hrs
        total += creds
        details.append({"name": name, "is_pe": is_pe, "hours": hrs, "credits": creds})
    return {"total_credits": total, "details": details}

# --- 功能 4: 思維導圖生成 ---
def generate_mindmap_code(user_text):
    if not user_text.strip(): return None

    prompt = f"""
    請將使用者的筆記轉換為 Graphviz DOT 語言代碼。
    筆記內容：
    {user_text}
    
    要求：
    1. 格式為 digraph G {{ rankdir=LR; ... }}
    2. 節點樣式：shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78", fontname="Noto Sans CJK TC"
    3. 找出核心主題當作根節點。
    4. 不要使用 Markdown 代碼區塊 (```)，只回傳純文字代碼。
    """
    
    result = get_ai_response(prompt, system_instruction="你是一個 Graphviz 專家。")
    
    if result:
        # 清理可能殘留的 Markdown
        return result.replace("```dot", "").replace("```", "").strip()
    
    return None
