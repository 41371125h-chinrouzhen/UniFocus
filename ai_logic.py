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
    除錯模式 (Debug Mode)：
    會直接在畫面上顯示錯誤原因，方便排查。
    """
    
    # 檢查金鑰是否存在
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ 嚴重錯誤：Secrets 中找不到 'GEMINI_API_KEY'。請檢查 Streamlit 設定。")
        return None

    # === 嘗試 Gemini ===
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 嘗試使用最舊但最穩定的模型名稱，排除模型問題
        # 如果這個能用，代表是 1.5-flash 你的帳號不能用
        model = genai.GenerativeModel('gemini-pro') 
        
        final_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        
        response = model.generate_content(final_prompt)
        if response and response.text:
            return response.text
            
    except Exception as e:
        # 這是關鍵！直接把錯誤印在畫面上
        st.error(f"❌ Gemini 連線失敗: {e}")

    # === 嘗試 Groq (如果有的話) ===
    if "GROQ_API_KEY" in st.secrets:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"❌ Groq 連線失敗: {e}")
    else:
        st.warning("⚠️ 未設定 GROQ_API_KEY，無法進行備援。")

    return None

# --- 功能函式 (直接回傳除錯訊息) ---

def get_weather_advice(weather_info, today_courses):
    res = get_ai_response(f"天氣：{weather_info}，課程：{today_courses}，給一句提醒。")
    return res if res else "❌ AI 故障，無法取得建議"

def generate_course_topics(course_name):
    res = get_ai_response(f"課程「{course_name}」的4個單元主題，用逗號分隔。")
    if not res: return ["AI故障", "請檢查", "API Key", "設定"]
    return [t.strip() for t in res.split(',')][:4]

def recommend_videos(course, topic):
    res = get_ai_response(f"課程「{course}」單元「{topic}」的學習資源。")
    return res if res else "❌ AI 故障"

def generate_mindmap_code(user_text):
    prompt = f"""
    將筆記轉為 Graphviz DOT 代碼。筆記：{user_text}
    要求：digraph G {{ rankdir=LR; node [fontname="Noto Sans CJK TC", shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78"]; ... }}
    只回傳代碼。
    """
    res = get_ai_response(prompt)
    if res: return res.replace("```dot", "").replace("```", "").strip()
    return None