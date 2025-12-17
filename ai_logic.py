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
    最穩定的版本：
    1. 優先使用 gemini-1.5-flash (目前 Google 預設標準模型)
    2. 如果失敗，切換 Groq
    """
    
    # === 第一關：Gemini ===
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # 使用目前最通用的模型名稱
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 將 system_instruction 拼接到 prompt 中，相容性最高
            final_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            
            response = model.generate_content(final_prompt)
            if response and response.text:
                return response.text
    except Exception as e:
        print(f"Gemini Error: {e}") # 只在後台印出錯誤，不影響前台

    # === 第二關：Groq (備援) ===
    try:
        if "GROQ_API_KEY" in st.secrets:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")

    # 如果都失敗，回傳 None (讓前端顯示錯誤或不做動作)
    return None

# --- 功能函式 ---

def get_weather_advice(weather_info, today_courses):
    prompt = f"""
    現在天氣：{weather_info}
    今天課程：{today_courses}
    請給一句30字以內的繁體中文溫馨提醒，語氣活潑。
    """
    res = get_ai_response(prompt)
    return res if res else "今天天氣不錯，祝你有個美好的一天！"

def generate_course_topics(course_name):
    prompt = f"針對課程「{course_name}」，列出 4 個教學單元主題，用逗號分隔。"
    result = get_ai_response(prompt)
    if not result: return ["導論", "核心理論", "實務應用", "期末專題"]
    return [t.strip() for t in result.split(',') if t.strip()][:4]

def recommend_videos(course, topic):
    prompt = f"課程「{course}」單元「{topic}」，請提供 3 個核心觀念與 3 個 YouTube 搜尋關鍵字 (Markdown 列點)。"
    res = get_ai_response(prompt)
    return res if res else "⚠️ AI 連線忙碌中，請稍後再試。"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。
    筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    注意：只回傳代碼，不要包含 ```dot 或 ``` 標記。
    """
    result = get_ai_response(prompt)
    if result:
        # 簡單的清理邏輯
        return result.replace("```dot", "").replace("```", "").strip()
    return None