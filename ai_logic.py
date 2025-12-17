import google.generativeai as genai
import streamlit as st
import time
from groq import Groq

# 設定優先順序：根據你之前的測試，2.5 是存在的，所以放第一位
MODEL_PRIORITY = [
    'gemini-2.5-flash',
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash',
    'gemini-pro'
]

def configure_genai():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    return False

def get_ai_response(prompt, system_instruction=None):
    """
    智慧型 AI 呼叫器：
    1. 自動輪詢所有可能的 Gemini 模型
    2. 失敗時自動切換 Groq
    3. 顯示具體錯誤原因方便除錯
    """
    
    # 步驟 1: 嘗試 Gemini 系列
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        last_error = ""
        
        # 迴圈嘗試每一個模型
        for model_name in MODEL_PRIORITY:
            try:
                # 建立模型
                model = genai.GenerativeModel(model_name)
                
                # 組合 Prompt
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                
                # 發送請求
                response = model.generate_content(full_prompt)
                
                # 如果成功，直接回傳結果
                if response and response.text:
                    return response.text
                    
            except Exception as e:
                # 記錄錯誤但繼續嘗試下一個
                error_msg = str(e)
                print(f"嘗試 {model_name} 失敗: {error_msg}")
                last_error = error_msg
                continue
        
        # 如果 Gemini 全部失敗，在後台印出最後一個錯誤
        print(f"Gemini 全面失敗，最後錯誤: {last_error}")

    # 步驟 2: 嘗試 Groq (備援)
    try:
        if "GROQ_API_KEY" in st.secrets:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
    except Exception as e_groq:
        print(f"Groq Error: {e_groq}")

    # 步驟 3: 如果真的全掛了，回傳具體錯誤訊息給前端顯示
    # 這樣你就不會只看到 "None"，而是看到具體原因
    if "GEMINI_API_KEY" not in st.secrets:
        return "⚠️ 設定錯誤：找不到 GEMINI_API_KEY，請檢查 Secrets。"
    
    return f"⚠️ AI 服務暫時無法使用。\nGoogle Error: {last_error}\n請稍後再試。"

# --- 功能函式 (保持不變) ---

def get_weather_advice(weather_info, today_courses):
    prompt = f"""
    現在天氣：{weather_info}
    今天課程：{today_courses}
    請給一句30字以內的繁體中文溫馨提醒，語氣活潑。
    """
    res = get_ai_response(prompt)
    # 如果回傳的是錯誤訊息(以⚠️開頭)，就給預設值
    if res and res.startswith("⚠️"): return "天氣多變，出門請注意安全！"
    return res if res else "祝你有個美好的一天！"

def generate_course_topics(course_name):
    prompt = f"針對課程「{course_name}」，列出 4 個教學單元主題，用逗號分隔。"
    result = get_ai_response(prompt)
    if not result or result.startswith("⚠️"): return ["導論", "核心理論", "實務應用", "期末專題"]
    return [t.strip() for t in result.split(',') if t.strip()][:4]

def recommend_videos(course, topic):
    prompt = f"課程「{course}」單元「{topic}」，請提供 3 個核心觀念與 3 個 YouTube 搜尋關鍵字 (Markdown 列點)。"
    return get_ai_response(prompt)

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。
    筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼，不要 Markdown。
    """
    return get_ai_response(prompt)