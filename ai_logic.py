import google.generativeai as genai
import streamlit as st
import time
from groq import Groq

def configure_genai():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    return False

def get_ai_response(prompt, system_instruction=None):
    # 嘗試 1: Gemini (使用目前最穩定的 1.5 Flash)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash') # 改回穩定版
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = model.generate_content(full_prompt)
            return response.text
    except Exception as e_gemini:
        print(f"Gemini Error: {e_gemini}") # 印出錯誤到後台 logs
        
        # 嘗試 2: Groq (備援)
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
            
    # 如果都失敗，回傳具體錯誤提示
    return None

def get_weather_advice(weather_info, today_courses):
    prompt = f"""
    現在天氣：{weather_info}
    今天課程：{today_courses}
    請給一句30字以內的繁體中文溫馨提醒，語氣活潑。
    """
    res = get_ai_response(prompt)
    return res if res else "今天天氣不錯，祝你有個美好的一天！" # 預設值，避免顯示錯誤

def generate_course_topics(course_name):
    prompt = f"針對課程「{course_name}」，列出 4 個教學單元主題，用逗號分隔。"
    result = get_ai_response(prompt)
    if not result: return ["課程導論", "核心理論", "實務應用", "期末專題"]
    return [t.strip() for t in result.split(',') if t.strip()][:4]

def recommend_videos(course, topic):
    prompt = f"課程「{course}」單元「{topic}」，請提供 3 個核心觀念與 3 個 YouTube 搜尋關鍵字 (Markdown 列點)。"
    return get_ai_response(prompt) or "⚠️ AI 目前無法連線，請稍後再試。"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。
    筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼，不要 Markdown。
    """
    result = get_ai_response(prompt)
    if result:
        return result.replace("```dot", "").replace("```", "").strip()
    return None