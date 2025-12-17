import google.generativeai as genai
import streamlit as st
from groq import Groq
import re  # <--- 新增這個：用來暴力切割字串

def configure_genai():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    return False

def get_ai_response(prompt, system_instruction=None):
    """
    模型更新版 (2025/12 適用)：
    1. Gemini: 使用 gemini-1.5-flash
    2. Groq: 使用 llama-3.3-70b-versatile
    """
    
    # 安全設定
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
            model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
            final_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = model.generate_content(final_prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini 1.5 Flash 失敗: {e}")
            try:
                # 備用嘗試
                model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
                response = model.generate_content(final_prompt)
                if response and response.text: return response.text
            except: pass

    # === 第二關：Groq (Llama 3.3) ===
    if "GROQ_API_KEY" in st.secrets:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            messages = []
            if system_instruction: messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq 失敗: {e}")

    return "⚠️ AI 系統忙碌中，請稍後再試。"

# --- 功能函式 ---

def get_weather_advice(weather_info, today_courses):
    res = get_ai_response(f"天氣：{weather_info}，課程：{today_courses}，給一句提醒。")
    return res if res else "天氣多變，注意保暖！"

def generate_course_topics(course_name):
    # 1. 強化 Prompt，叫 AI 乖乖用逗號分隔
    prompt = f"針對課程「{course_name}」，列出 4 個教學單元主題。請純粹列出主題名稱，用「半形逗號 ,」分隔，不要有編號，不要有換行。"
    
    result = get_ai_response(prompt)
    
    # 保底機制
    if not result or "⚠️" in result: 
        return ["導論", "核心理論", "實務應用", "期末專題"]

    # 2. 暴力清洗資料 (關鍵修復點！)
    # 把常見的分隔符號全部替換成逗號
    text = result
    text = text.replace("、", ",")  # 處理頓號
    text = text.replace("\n", ",")  # 處理換行
    text = text.replace("；", ",")  # 處理分號
    text = text.replace(";", ",")
    
    # 3. 切割成列表
    raw_list = text.split(',')
    
    # 4. 清理每個選項 (去除前後空白、去除 "1." "Unit 1" 等編號)
    clean_list = []
    for item in raw_list:
        # 去除前後空白
        s = item.strip()
        # 用正規表達式去除開頭的 "1." "Unit 1:" 等雜訊
        s = re.sub(r'^(單元|Unit|Topic)?\s*\d+[\.:\s]*', '', s)
        # 如果不是空字串，就加入列表
        if s:
            clean_list.append(s)

    # 確保只有 4 個
    return clean_list[:4]

def recommend_videos(course, topic):
    res = get_ai_response(f"課程「{course}」單元「{topic}」的學習資源。")
    return res if res else "⚠️ AI 連線失敗"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼。
    """
    res = get_ai_response(prompt)
    if res and "digraph" in res:
        return res.replace("```dot", "").replace("```", "").strip()
    return None
