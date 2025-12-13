import streamlit as st
import pandas as pd
import datetime
import ai_logic, data_manager, pdf_parser
import graphviz
import base64
import random

# --- 1. 設定 ---
st.set_page_config(page_title="Unifocus", layout="wide", page_icon="🌿")

COLOR_BG = "#F7F9F9"
COLOR_SIDE = "#FFFFFF"
COLOR_MAIN = "#6B8E78"
COLOR_TEXT = "#2C3E50"
COLOR_BTN_TXT = "#F7F9F9"
COLOR_ACCENT = "#E67E22"

# === CSS 修正：合併 V16 的精美樣式與 V17 的字體引入 ===
st.markdown(f"""
    <style>
    /* 1. 引入字體 (新功能) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Patrick+Hand&family=Press+Start+2P&display=swap');

    /* 2. 全域設定 */
    .stApp {{ background-color: {COLOR_BG}; font-family: 'Microsoft JhengHei', sans-serif; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* 3. 側邊欄優化 */
    [data-testid="stSidebar"] {{ background-color: {COLOR_SIDE}; border-right: 1px solid #E0E0E0; }}
    [data-testid="stSidebar"] .stButton > button {{
        background-color: {COLOR_MAIN}; color: {COLOR_BTN_TXT} !important;
        border: none; border-radius: 10px; width: 100%; transition: all 0.3s ease;
    }}

    /* 4. 通用卡片樣式 */
    .dashboard-card {{
        background-color: #FFFFFF; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; border: 1px solid #EFEFEF;
    }}

    /* 5. 卡片標題 (找回綠色邊框) */
    .card-title {{
        color: {COLOR_TEXT}; font-weight: 700; font-size: 1.1em; margin-bottom: 15px;
        border-left: 4px solid {COLOR_MAIN}; padding-left: 10px;
    }}

    /* 6. 行程列表樣式 (找回標籤與排版) */
    .schedule-item {{ padding: 12px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; }}
    .time-badge {{ background-color: {COLOR_MAIN}; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.85em; width: 50px; text-align: center; margin-right: 10px; }}
    .nav-pill {{ display: inline-block; padding: 6px 14px; margin-right: 8px; border-radius: 15px; background-color: #E8F3EB; color: {COLOR_MAIN}; font-size: 0.85em; font-weight: 600; }}

    /* 7. 輸入框優化 */
    .stTextArea textarea {{
        border-radius: 12px; border: 1px solid #ddd; padding: 15px; background-color: #fff;
    }}

    /* 8. 互動卡片樣式 (找回倒數計時卡的設計) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #EFEFEF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        padding: 20px;
    }}
    /* 讓倒數標題輸入框變漂亮 */
    div[data-testid="stTextInput"] input {{
        font-weight: bold;
        color: #2C3E50;
        font-size: 1.1em;
        border: none;
        border-bottom: 1px solid #ddd;
        background: transparent;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-bottom: 2px solid #6B8E78;
        box-shadow: none;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 邏輯與輔助函數 ---
def get_sort_key(period_str):
    if not isinstance(period_str, str): return 99
    code = period_str.split(' ')[0]
    return {'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'A':11,'B':12,'C':13}.get(code, 99)

def calculate_credits_flow(df):
    if df.empty: return 0
    hours_count = df['活動名稱'].value_counts().reset_index()
    hours_count.columns = ['name', 'hours']
    result = ai_logic.calculate_credits(hours_count.to_dict('records'))
    return result.get('total_credits', 0)

def graph_to_base64(dot_code):
    try:
        graph = graphviz.Source(dot_code)
        png_bytes = graph.pipe(format='png')
        b64 = base64.b64encode(png_bytes).decode()
        return f"data:image/png;base64,{b64}"
    except: return None

def generate_styled_schedule_html(df, style, bg_color, text_color, font_size):
    if df.empty: return "<div style='text-align:center; padding:50px;'>無課表資料</div>"
    df['SortKey'] = df['時間/節次'].apply(get_sort_key)
    pivot = df.sort_values('SortKey').pivot_table(index='時間/節次', columns='星期', values='活動名稱', aggfunc=lambda x: '<br>'.join(x), sort=False)
    days = [d for d in ['一','二','三','四','五','六','日'] if d in pivot.columns]
    final_df = pivot[days]

    css = ""
    container_style = f"background-color: {bg_color}; padding: 20px; width: 100%; overflow-x: auto;"

    if style == "手繪風 (Hand-drawn)":
        font_family = "'Patrick Hand', 'Comic Sans MS', cursive"
        container_style += "border: 2px solid #333; border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;"
        css = f"table {{ border-collapse: separate; border-spacing: 10px; width: 100%; font-family: {font_family}; color: {text_color}; }} th {{ font-size: {int(font_size)+4}px; border-bottom: 2px solid {text_color}; transform: rotate(-2deg); padding: 10px; }} td {{ font-size: {font_size}px; border: 2px solid {text_color}; border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px; padding: 15px; background: rgba(255,255,255,0.4); box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }}"

    elif style == "像素風 (Pixel Art)":
        font_family = "'Press Start 2P', monospace"
        container_style += "border: 4px solid #000;"
        css = f"table {{ border-collapse: collapse; width: 100%; font-family: {font_family}; color: {text_color}; }} th {{ font-size: {int(font_size)-2}px; background: #000; color: #fff; padding: 15px; text-transform: uppercase; }} td {{ font-size: {int(font_size)-4}px; border: 2px solid #000; padding: 10px; background: #fff; image-rendering: pixelated; }} tr:nth-child(even) td {{ background: #eee; }}"

    elif style == "寫實質感 (Realistic)":
        font_family = "'Noto Sans TC', sans-serif"
        container_style += "border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"
        css = f"table {{ border-collapse: collapse; width: 100%; font-family: {font_family}; color: {text_color}; }} th {{ font-size: {font_size}px; font-weight: 700; padding: 15px; border-bottom: 1px solid rgba(0,0,0,0.1); text-align: left; }} td {{ font-size: {font_size}px; padding: 20px; border-bottom: 1px solid rgba(0,0,0,0.05); transition: 0.3s; }} tr:hover td {{ background-color: rgba(255,255,255,0.5); }}"

    html = f"<style>{css}</style><div style='{container_style}'>{final_df.to_html(classes='styled-table', escape=False)}</div>"
    return html

# --- 3. 初始化 ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'schedule_data' not in st.session_state: st.session_state.schedule_data = pd.DataFrame(columns=data_manager.COLS_SCHEDULE)
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

if 'calculated_credits' not in st.session_state: st.session_state.calculated_credits = 0
if 'exam_date' not in st.session_state: st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=7)
if 'exam_name' not in st.session_state: st.session_state.exam_name = "期中考"
if 'preview_topics' not in st.session_state: st.session_state.preview_topics = {}

def go_to(page): st.session_state.page = page

# --- 4. 登入介面 ---
if not st.session_state.logged_in:
    _, c2, _ = st.columns([1, 0.8, 1])
    with c2:
        st.markdown("<br><br><div class='login-container'><h2 style='color:#6B8E78'>🌿 Unifocus</h2><p style='color:#888'>智慧學習導航系統</p></div>", unsafe_allow_html=True)
        uid = st.text_input("User ID", placeholder="請輸入學號", label_visibility="collapsed")
        if st.button("🚀 進入系統") and uid:
            df, _ = data_manager.load_user_data(uid)
            if df is not None:
                st.session_state.username = uid
                st.session_state.schedule_data = df
                st.session_state.calculated_credits = calculate_credits_flow(df)
                st.session_state.logged_in = True
                st.rerun()

# --- 5. 主系統 ---
else:
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; padding:10px'><div style='width:60px; height:60px; background:#6B8E78; border-radius:50%; color:white; font-size:24px; line-height:60px; margin:0 auto'>{st.session_state.username[0].upper()}</div><h3 style='margin-top:10px'>{st.session_state.username}</h3></div><hr>", unsafe_allow_html=True)
        if st.button("🏠 首頁概覽"): go_to("Dashboard")
        if st.button("📅 我的課表"): go_to("Schedule")
        if st.button("🎨 課表設計"): go_to("Design")
        if st.button("📖 課前預習"): go_to("Preview")
        if st.button("🧠 思維導圖"): go_to("MindMap")

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("登出系統", type="secondary"): st.session_state.logged_in = False; st.rerun()

    c1, c2 = st.columns([4, 1.5])
    with c1: st.markdown(f"## {st.session_state.page}")

    # === DASHBOARD ===
    if st.session_state.page == "Dashboard":
        r1, r2 = st.columns([2, 1])
        with r1:
            html = "<div class='schedule-item'>詳細行程請見「我的課表」</div>" if not st.session_state.schedule_data.empty else "<div style='color:#999; padding:20px; text-align:center'>今日無課程</div>"
            st.markdown(f"<div class='dashboard-card'><div class='card-title'>📅 今日概覽</div>{html}</div>", unsafe_allow_html=True)
            st.markdown("### 📊 本週專注度")
            st.bar_chart({"專注": [30, 50, 40, 70, 60]})
        with r2:
            st.markdown(f"<div class='dashboard-card' style='text-align:center'><div class='card-title' style='justify-content:center'>本學期學分</div><h1 style='color:#6B8E78; font-size:3em'>{st.session_state.calculated_credits}</h1><p style='color:#888; font-size:0.8em'>AI 自動估算</p></div>", unsafe_allow_html=True)
            with st.container(border=True):
                c_title, c_date = st.columns([3, 1])
                with c_title:
                    new_name = st.text_input("倒數標題", value=st.session_state.exam_name, label_visibility="collapsed")
                    if new_name != st.session_state.exam_name: st.session_state.exam_name = new_name; st.rerun()
                with c_date:
                    new_date = st.date_input("日期", value=st.session_state.exam_date, label_visibility="collapsed")
                    if new_date != st.session_state.exam_date: st.session_state.exam_date = new_date; st.rerun()
                days_left = (st.session_state.exam_date - datetime.date.today()).days

                if days_left < 0:
                    num_color, label, days_display = "#999", "天 (已結束)", abs(days_left)
                elif days_left <= 3:
                    num_color, label, days_display = "#E74C3C", "天 ⚠️", days_left
                else:
                    num_color, label, days_display = "#E67E22", "天", days_left

                st.markdown(f"<div style='text-align:center; margin-top:-10px;'><h1 style='color:{num_color}; font-size:3.5em; margin:0;'>{days_display}</h1><p style='color:#888; font-weight:bold;'>{label}</p><small style='color:#aaa;'>{st.session_state.exam_date}</small></div>", unsafe_allow_html=True)

    # === SCHEDULE ===
    elif st.session_state.page == "Schedule":
        with st.expander("📥 匯入/更新課表 (PDF)"):
            up = st.file_uploader("上傳課表PDF", type=['pdf'])
            if up and st.button("解析與更新"):
                res = pdf_parser.parse_ntnu(up)
                if res is not None:
                    st.session_state.schedule_data = res
                    data_manager.save_user_data(st.session_state.username, res)
                    st.session_state.calculated_credits = calculate_credits_flow(res)
                    st.success("更新成功！"); st.rerun()
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        if not st.session_state.schedule_data.empty:
            df = st.session_state.schedule_data.copy()
            df['SortKey'] = df['時間/節次'].apply(get_sort_key)
            pivot = df.sort_values('SortKey').pivot_table(index='時間/節次', columns='星期', values='活動名稱', aggfunc=lambda x: '<br>'.join(x), sort=False)
            days = [d for d in ['一','二','三','四','五','六','日'] if d in pivot.columns]
            st.write(pivot[days].to_html(escape=False), unsafe_allow_html=True)
        else: st.info("無資料")
        st.markdown("</div>", unsafe_allow_html=True)

    # === DESIGN ===
    elif st.session_state.page == "Design":
        st.markdown("<div class='dashboard-card'><div class='card-title'>🎨 課表設計師</div><p>自訂你的課表風格，讓學習更有趣！</p></div>", unsafe_allow_html=True)
        c_control, c_preview = st.columns([1, 2])
        with c_control:
            st.markdown("#### 🛠️ 設計參數")
            style_mode = st.selectbox("風格選擇", ["手繪風 (Hand-drawn)", "寫實質感 (Realistic)", "像素風 (Pixel Art)"])
            col1, col2 = st.columns(2)
            with col1: bg_color = st.color_picker("背景顏色", "#FFF9C4" if style_mode == "手繪風 (Hand-drawn)" else "#FFFFFF")
            with col2: text_color = st.color_picker("文字顏色", "#333333")
            font_size = st.slider("字體大小", 12, 24, 16)
        with c_preview:
            st.markdown("#### 🖼️ 預覽結果")
            if not st.session_state.schedule_data.empty:
                html_output = generate_styled_schedule_html(st.session_state.schedule_data, style_mode, bg_color, text_color, font_size)
                st.components.v1.html(html_output, height=600, scrolling=True)
                b64 = base64.b64encode(html_output.encode()).decode()
                st.markdown(f'<a href="data:text/html;base64,{b64}" download="my_schedule.html" style="text-decoration:none; background:#6B8E78; color:white; padding:10px 20px; border-radius:5px; display:block; text-align:center; font-weight:bold;">📥 下載 HTML 檔</a>', unsafe_allow_html=True)
            else: st.warning("請先至「我的課表」匯入資料")

    # === PREVIEW ===
    elif st.session_state.page == "Preview":
        st.markdown("<div class='dashboard-card'><div class='card-title'>📖 智慧課前預習</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            courses = st.session_state.schedule_data['活動名稱'].unique().tolist() if not st.session_state.schedule_data.empty else []
            sel_course = st.selectbox("選擇課程", courses) if courses else st.selectbox("選擇課程", ["無資料"])

            if sel_course != "無資料":
                if sel_course not in st.session_state.preview_topics:
                    if st.button(f"🔍 載入「{sel_course}」主題"):
                        with st.spinner("AI 正在分析課程主題..."):
                            st.session_state.preview_topics[sel_course] = ai_logic.generate_course_topics(sel_course)
                            st.rerun()
                if sel_course in st.session_state.preview_topics:
                    topic_list = st.session_state.preview_topics[sel_course]
                    sel_topic = st.selectbox("選擇學習主題", topic_list + ["✏️ 手動輸入主題..."])
                    real_topic = st.text_input("請輸入自訂主題") if sel_topic == "✏️ 手動輸入主題..." else sel_topic

                    if st.button("✨ 生成預習指南", use_container_width=True) and real_topic:
                         with st.spinner("正在搜尋推薦影片與筆記..."):
                            st.session_state['preview_res'] = ai_logic.recommend_videos(sel_course, real_topic)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            if 'preview_res' in st.session_state: st.markdown(st.session_state['preview_res'])
            else: st.info("👈 請選擇課程與主題以開始")
            st.markdown("</div>", unsafe_allow_html=True)

    # === MINDMAP ===
    elif st.session_state.page == "MindMap":
        st.markdown("<div class='dashboard-card'><div class='card-title'>🧠 AI 思維導圖</div></div>", unsafe_allow_html=True)
        user_text = st.text_area("輸入筆記內容", height=300, placeholder="例如：\n期末專題\n前端\n後端")
        if st.button("✨ 繪製思維導圖", use_container_width=True):
            if user_text:
                with st.spinner("繪製中..."):
                    dot_code = ai_logic.generate_mindmap_code(user_text)
                    if dot_code:
                        img_src = graph_to_base64(dot_code)
                        if img_src:
                            st.markdown(f'<div class="dashboard-card" style="text-align:center"><img src="{img_src}" style="max-width:100%;"><br><br><a href="{img_src}" download="mindmap.png">📥 下載圖片</a></div>', unsafe_allow_html=True)
