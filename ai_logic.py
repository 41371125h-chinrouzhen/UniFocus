import json
import random
import time

# --- 模擬 AI 核心 ---
def configure_genai():
    print("✅ [模擬模式] AI 系統已就緒")
    return True

# 1. 課綱生成
def generate_course_topics(course_name):
    time.sleep(0.5)
    return [f"{course_name}導論", "核心概念", "實務應用", "期末專題"]

# 2. 影片推薦
def recommend_videos(course, topic):
    time.sleep(0.8)
    return f"### [模擬結果]\n針對 {course}-{topic} 的學習資源...\n(內容省略)"

# 3. 學分計算
def calculate_credits(courses_data):
    total = 0
    details = []
    for c in courses_data:
        hrs = int(c.get('hours', 0))
        name = c.get('name', '')
        is_pe = any(k in name for k in ["體育", "球", "瑜珈", "游泳"])
        creds = max(0, hrs - 1) if is_pe else hrs
        total += creds
        details.append({"name": name, "is_pe": is_pe, "hours": hrs, "credits": creds})
    return {"total_credits": total, "details": details}

# === 4. [新增] 思維導圖生成邏輯 ===
def generate_mindmap_code(user_text):
    """
    將文字轉換為 Graphviz DOT 語言。
    邏輯：第一行是中心，其餘是分支。
    """
    if not user_text.strip():
        return None

    lines = [L.strip() for L in user_text.split('\n') if L.strip()]
    if not lines: return None

    root = lines[0]
    branches = lines[1:]

    # 如果使用者只打了一行，我們幫他隨機生一點分支，讓他覺得 AI 很厲害
    if not branches:
        branches = ["概念 A", "概念 B", "延伸思考", "重點筆記"]

    # 組合 Graphviz DOT 語法
    # 注意：fontname="Noto Sans CJK TC" 是顯示中文的關鍵
    dot_code = f"""
    digraph G {{
        rankdir=LR;
        node [shape=box, style="filled,rounded", fillcolor="#E8F3EB", color="#6B8E78", fontname="Noto Sans CJK TC"];
        edge [color="#aaa"];

        "{root}" [shape=ellipse, fillcolor="#6B8E78", fontcolor="white", fontsize=16];

    """

    for branch in branches:
        # 簡單處理：如果分支裡有冒號，切分成兩層
        if "：" in branch or ":" in branch:
            parts = branch.replace("：", ":").split(":")
            parent = parts[0]
            child = parts[1]
            dot_code += f'    "{root}" -> "{parent}";\n'
            dot_code += f'    "{parent}" -> "{child}";\n'
        else:
            dot_code += f'    "{root}" -> "{branch}";\n'

    dot_code += "}"
    return dot_code
