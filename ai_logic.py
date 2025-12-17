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
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e_gemini:
        # Fallback logic (Groq) omitted for brevity, keeping same as before
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
        except: pass
    return None

# --- 新增：天氣建議 ---
def get_weather_advice(weather_info, today_courses):
    prompt = f"""
    現在天氣狀況：{weather_info}
    今天使用者的課程/行程：{today_courses}
    
    請根據天氣和行程，給出一句溫馨簡短的提醒 (30字以內)。
    例如：今天有體育課且下雨，記得帶替換衣物和雨傘。
    """
    return get_ai_response(prompt)

# --- 舊有功能保持不變 ---
def generate_course_topics(course_name):
    prompt = f"針對課程「{course_name}」，列出 4 個教學單元主題，用逗號分隔，不要有廢話。"
    result = get_ai_response(prompt)
    if not result: return ["導論", "核心概念", "實務應用", "專題"]
    return [t.strip() for t in result.split(',') if t.strip()][:4]

def recommend_videos(course, topic):
    prompt = f"課程「{course}」單元「{topic}」，請提供 3 個核心觀念與 3 個 YouTube 搜尋關鍵字 (Markdown 列點)。"
    return get_ai_response(prompt) or "AI 忙碌中"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。
    筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼，不要 Markdown 標記。
    """
    result = get_ai_response(prompt)
    if result:
        return result.replace("```dot", "").replace("```", "").strip()
    return None