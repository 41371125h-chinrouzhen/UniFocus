import google.generativeai as genai
import streamlit as st
from groq import Groq

def configure_genai():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    return False

def get_ai_response(prompt, system_instruction=None):
    """
    模型更新版 (2025/12 適用)：
    1. Gemini: 使用 gemini-1.5-flash
    2. Groq: 使用 llama-3.3-70b-versatile (替代已下架的 llama3)
    """
    
    # --- 安全設定 (防止 AI 拒絕回答導致 None) ---
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # === 第一關：Gemini 1.5 Flash ===
    if "GEMINI_API_KEY" in st.secrets:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # 使用目前最穩定的 1.5 Flash
            model = genai.GenerativeModel(
                'gemini-2.5-flash',
                safety_settings=safety_settings
            )
            
            final_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            
            response = model.generate_content(final_prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini 1.5 Flash 失敗: {e}")
            # 如果 1.5 失敗，嘗試 fallback 到 2.0 (如果有的話)
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp', safety_settings=safety_settings)
                response = model.generate_content(final_prompt)
                if response and response.text: return response.text
            except:
                pass

    # === 第二關：Groq (Llama 3.3) ===
    if "GROQ_API_KEY" in st.secrets:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            chat_completion = client.chat.completions.create(
                messages=messages,
                # 更新為最新的 Llama 3.3 模型
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq 失敗: {e}")
            # 備用 Groq 模型
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.1-8b-instant",
                )
                return chat_completion.choices[0].message.content
            except:
                pass

    # 如果全失敗，回傳錯誤提示 (不要回傳 None 讓程式崩潰)
    return "⚠️ AI 系統忙碌中，請稍後再試。"

# --- 功能函式 ---

def get_weather_advice(weather_info, today_courses):
    res = get_ai_response(f"天氣：{weather_info}，課程：{today_courses}，給一句提醒。")
    return res if res else "天氣多變，注意保暖！"

def generate_course_topics(course_name):
    res = get_ai_response(f"課程「{course_name}」的4個單元主題，用逗號分隔。")
    if not res or "⚠️" in res: return ["導論", "核心理論", "實務應用", "期末專題"]
    return [t.strip() for t in res.split(',')][:4]

def recommend_videos(course, topic):
    res = get_ai_response(f"課程「{course}」單元「{topic}」的學習資源。")
    return res if res else "⚠️ AI 連線失敗"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼，不要 Markdown。
    """
    res = get_ai_response(prompt)
    if res and "digraph" in res:
        return res.replace("```dot", "").replace("```", "").strip()
    return None