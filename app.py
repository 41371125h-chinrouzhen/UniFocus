import streamlit as st
import pandas as pd
import datetime
import graphviz
import base64
import time

# 引入你的模組
import ai_logic
import data_manager
import pdf_parser

# --- 1. 設定與初始化 ---
st.set_page_config(
    page_title="Unifocus | 智慧學習導航", 
    layout="wide", 
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# 初始化 AI (只在第一次執行時跑)
if 'ai_configured' not in st.session_state:
    success = ai_logic.configure_genai()
    st.session_state.ai_configured = success
    if not success:
        st.toast("⚠️ AI 金鑰未設定或無效，將使用離線模式", icon="🔌")

# 顏色變數
COLOR_BG = "#F7F9F9"
COLOR_SIDE = "#FFFFFF"
COLOR_MAIN = "#6B8E78"
COLOR_TEXT = "#2C3E50"
COLOR_BTN_TXT = "#FFFFFF"

# === CSS 樣式優化 ===
st.markdown(f"""
    <style>
    /* 引入 Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Patrick+Hand&family=Press+Start+2P&display=swap');

    /* 全域字體設定 */
    .stApp {{ background-color: {COLOR_BG}; font-family: 'Noto Sans TC', sans-serif; }}
    
    /* 隱藏預設選單 */
    #MainMenu, footer {{ visibility: hidden; }}

    /* 卡片樣式 (Card Style) */
    .dashboard-card {{
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
    }}
    
    .card-title {{
        color: {COLOR_TEXT};
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* 按鈕樣式 (更現代化) */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }}
    
    /* 側邊欄樣式 */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_SIDE};
        border-right: 1px solid #E0E0E0;
    }}
    
    /* 表格樣式優化 */
    table {{ width: 100%; }}
    
    </style>
""", unsafe_allow_html=True)

# --- 2. 輔助函數 ---
def get_sort_key(period_str):
    if not isinstance(period_str, str): return 99
    # 簡單的節次排序對照表
    order_map = {
        '1':1, '2':2, '3':3, '4':4, '中午':5, '5':6, '6':7, '7':8, '8':9, '9':10, '10':11,
        'A':12, 'B':13, 'C':14, 'D':15
    }
    # 嘗試抓取第一個字元或代碼
    code = period_str.split(' ')[0]
    return order_map.get(code, 99)

def calculate_credits_flow(df):
    """計算學分的流程包裝"""
    if df.empty: return 0
    # 確保有「活動名稱」欄位
    if '活動名稱' not in df.columns: return 0
    
    hours_count = df['活動名稱'].value_counts().reset_index()
    hours_count.columns = ['name', 'hours']
    result = ai_logic.calculate_credits(hours_count.to_dict('records'))
    return result.get('total_credits', 0)

def graph_to_base64(dot_code):
    """將 Graphviz DOT 碼轉為圖片 Base64 字串"""
    try:
        # 設定 graphviz 編碼為 UTF-8 以支援中文
        graph = graphviz.Source(dot_code, encoding='utf-8')
        # 渲染為 PNG 格式
        png_bytes = graph.pipe(format='png')
        b64 = base64.b64encode(png_bytes).decode()
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        st.error(f"繪圖引擎錯誤 (請確認 Graphviz 是否安裝): {e}")
        return None

def generate_styled_schedule_html(df, style, bg_color, text_color, font_size):
    """生成各種風格的課表 HTML"""
    if df.empty: return "<div style='text-align:center; padding:50px; color:#888;'>尚無課表資料</div>"
    
    # 資料處理
    temp_df = df.copy()
    temp_df['SortKey'] = temp_df['時間/節次'].apply(get_sort_key)
    
    # Pivot Table: 轉成週課表格式
    pivot = temp_df.sort_values('SortKey').pivot_table(
        index='時間/節次', 
        columns='星期', 
        values='活動名稱', 
        aggfunc=lambda x: '<br>'.join(x), 
        fill_value=""
    )
    
    # 確保星期順序正確
    days_order = ['一','二','三','四','五','六','日']
    existing_days = [d for d in days_order if d in pivot.columns]
    final_df = pivot[existing_days]

    # 風格設定
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
        container_style += "border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);"
        css = f"table {{ border-collapse: collapse; width: 100%; font-family: {font_family}; color: {text_color}; }} th {{ background-color: rgba(0,0,0,0.03); font-size: {font_size}px; font-weight: 700; padding: 12px; border-bottom: 2px solid #eee; text-align: center; }} td {{ font-size: {font_size}px; padding: 16px; border-bottom: 1px solid #eee; text-align: center; vertical-align: middle; }} tr:hover td {{ background-color: rgba(107, 142, 120, 0.05); }}"

    html = f"<style>{css}</style><div style='{container_style}'>{final_df.to_html(classes='styled-table', escape=False)}</div>"
    return html

# --- 3. Session State 初始化 ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
# 確保 schedule_data 一定是有欄位的 DataFrame
if 'schedule_data' not in st.session_state: 
    st.session_state.schedule_data = pd.DataFrame(columns=data_manager.COLS_SCHEDULE if hasattr(data_manager, 'COLS_SCHEDULE') else ['時間/節次', '星期', '活動名稱'])
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

if 'calculated_credits' not in st.session_state: st.session_state.calculated_credits = 0
if 'exam_date' not in st.session_state: st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=7)
if 'exam_name' not in st.session_state: st.session_state.exam_name = "期中考"
if 'preview_topics' not in st.session_state: st.session_state.preview_topics = {}

def go_to(page): st.session_state.page = page

# --- 4. 程式主流程 ---

# === 登入頁面 ===
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='text-align: center; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>
                <h1 style='color: {COLOR_MAIN}; margin-bottom: 0;'>🌿 Unifocus</h1>
                <p style='color: #888; font-size: 0.9rem;'>智慧學習導航系統</p>
                <hr style='margin: 20px 0;'>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        uid = st.text_input("學號 / User ID", placeholder="請輸入學號登入", label_visibility="collapsed")
        
        if st.button("🚀 進入系統", use_container_width=True) and uid:
            with st.spinner("正在連線資料庫..."):
                # 呼叫 data_manager 載入資料
                df, _ = data_manager.load_user_data(uid)
                
                # 不管有沒有舊資料，都讓使用者進去 (新使用者 = 空資料)
                st.session_state.username = uid
                if df is not None and not df.empty:
                    st.session_state.schedule_data = df
                    st.session_state.calculated_credits = calculate_credits_flow(df)
                else:
                    st.session_state.schedule_data = pd.DataFrame(columns=['時間/節次', '星期', '活動名稱']) # 預設空表
                
                st.session_state.logged_in = True
                st.rerun()

# === 系統主畫面 ===
else:
    # --- Sidebar ---
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center; padding: 20px 0;'>
                <div style='width: 80px; height: 80px; background: linear-gradient(135deg, {COLOR_MAIN}, #88B090); border-radius: 50%; color: white; font-size: 32px; line-height: 80px; margin: 0 auto; box-shadow: 0 4px 10px rgba(107, 142, 120, 0.3);'>
                    {st.session_state.username[0].upper() if st.session_state.username else 'U'}
                </div>
                <h3 style='margin-top: 15px; color: {COLOR_TEXT};'>{st.session_state.username}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # 導覽選單
        menu_options = {
            "Dashboard": "🏠 首頁概覽",
            "Schedule": "📅 我的課表",
            "Design": "🎨 課表設計",
            "Preview": "📖 課前預習",
            "MindMap": "🧠 思維導圖"
        }
        
        for key, label in menu_options.items():
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == key else "secondary"):
                go_to(key)
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("登出系統"): 
            st.session_state.logged_in = False
            st.rerun()

    # --- Main Content ---
    c1, c2 = st.columns([5, 1])
    with c1: st.title(menu_options[st.session_state.page])

    # === 頁面 1: DASHBOARD ===
    if st.session_state.page == "Dashboard":
        r1, r2 = st.columns([2, 1])
        
        with r1:
            st.markdown("<div class='dashboard-card'><div class='card-title'>📅 今日動態</div>", unsafe_allow_html=True)
            if not st.session_state.schedule_data.empty:
                # 這裡可以加入更聰明的今日課程篩選邏輯
                st.info("💡 提示：點擊左側「我的課表」查看完整行程")
            else:
                st.warning("尚未匯入課表，請前往「我的課表」頁面上傳 PDF。")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 專注度圖表 (範例數據)
            st.markdown("### 📊 本週學習歷程")
            chart_data = pd.DataFrame({
                "專注時數": [2, 4, 1.5, 3, 5, 2, 1],
                "星期": ["一", "二", "三", "四", "五", "六", "日"]
            }).set_index("星期")
            st.bar_chart(chart_data, color=COLOR_MAIN)

        with r2:
            # 學分卡片
            st.markdown(
                f"""
                <div class='dashboard-card' style='text-align:center;'>
                    <div class='card-title' style='justify-content:center;'>本學期學分</div>
                    <h1 style='color:{COLOR_MAIN}; font-size: 3.5rem; margin: 10px 0;'>{st.session_state.calculated_credits}</h1>
                    <p style='color:#888; font-size:0.8rem; margin:0;'>AI 自動估算</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # 倒數計時器
            with st.container(border=True):
                st.markdown("#### ⏳ 倒數計時")
                new_name = st.text_input("目標名稱", value=st.session_state.exam_name)
                new_date = st.date_input("目標日期", value=st.session_state.exam_date)
                
                if new_name != st.session_state.exam_name or new_date != st.session_state.exam_date:
                    st.session_state.exam_name = new_name
                    st.session_state.exam_date = new_date
                    st.rerun()

                days_left = (st.session_state.exam_date - datetime.date.today()).days
                
                color = "#E67E22" if days_left > 3 else "#E74C3C"
                display_text = f"{abs(days_left)} 天" if days_left >= 0 else "已結束"
                
                st.markdown(f"<h2 style='text-align:center; color:{color}; font-size: 2.5rem; margin-top:10px;'>{display_text}</h2>", unsafe_allow_html=True)

    # === 頁面 2: SCHEDULE ===
    elif st.session_state.page == "Schedule":
        with st.expander("📥 匯入/更新課表 (PDF)", expanded=st.session_state.schedule_data.empty):
            up = st.file_uploader("上傳課表 PDF (支援台師大格式)", type=['pdf'])
            if up and st.button("開始解析"):
                with st.spinner("正在解析 PDF..."):
                    try:
                        res = pdf_parser.parse_ntnu(up)
                        if res is not None and not res.empty:
                            st.session_state.schedule_data = res
                            # 儲存到資料庫
                            data_manager.save_user_data(st.session_state.username, res)
                            st.session_state.calculated_credits = calculate_credits_flow(res)
                            st.success("✅ 匯入成功！")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("解析失敗，請確認 PDF 格式是否正確。")
                    except Exception as e:
                        st.error(f"解析發生錯誤: {e}")

        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        if not st.session_state.schedule_data.empty:
            # 呼叫風格化 HTML 函式 (預設樣式)
            html = generate_styled_schedule_html(st.session_state.schedule_data, "寫實質感 (Realistic)", "#FFFFFF", "#333", 16)
            st.components.v1.html(html, height=600, scrolling=True)
        else:
            st.info("📭 目前沒有課表資料，請上傳 PDF。")
        st.markdown("</div>", unsafe_allow_html=True)

    # === 頁面 3: DESIGN ===
    elif st.session_state.page == "Design":
        st.markdown("<div class='dashboard-card'><p>自訂你的課表風格，讓學習更有趣！</p></div>", unsafe_allow_html=True)
        
        c_control, c_preview = st.columns([1, 2])
        
        with c_control:
            st.markdown("#### 🛠️ 設計參數")
            style_mode = st.selectbox("風格選擇", ["寫實質感 (Realistic)", "手繪風 (Hand-drawn)", "像素風 (Pixel Art)"])
            
            col1, col2 = st.columns(2)
            with col1: bg_color = st.color_picker("背景顏色", "#FFF9C4" if style_mode == "手繪風 (Hand-drawn)" else "#FFFFFF")
            with col2: text_color = st.color_picker("文字顏色", "#333333")
            
            font_size = st.slider("字體大小", 12, 24, 16)
            
            st.info("💡 調整完參數後，右側會即時更新。")

        with c_preview:
            st.markdown("#### 🖼️ 預覽結果")
            if not st.session_state.schedule_data.empty:
                html_output = generate_styled_schedule_html(st.session_state.schedule_data, style_mode, bg_color, text_color, font_size)
                st.components.v1.html(html_output, height=600, scrolling=True)
                
                # 下載按鈕
                b64 = base64.b64encode(html_output.encode()).decode()
                st.markdown(
                    f'<a href="data:text/html;base64,{b64}" download="my_schedule.html" style="text-decoration:none; background:{COLOR_MAIN}; color:white; padding:12px 24px; border-radius:8px; display:block; text-align:center; font-weight:bold; margin-top:10px;">📥 下載 HTML 檔</a>', 
                    unsafe_allow_html=True
                )
            else:
                st.warning("請先至「我的課表」匯入資料")

    # === 頁面 4: PREVIEW ===
    elif st.session_state.page == "Preview":
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.markdown("<div class='dashboard-card'><div class='card-title'>🔍 課程設定</div>", unsafe_allow_html=True)
            
            # 取得課程列表
            courses = st.session_state.schedule_data['活動名稱'].unique().tolist() if not st.session_state.schedule_data.empty else []
            sel_course = st.selectbox("選擇課程", courses) if courses else st.selectbox("選擇課程", ["無資料"])

            if sel_course != "無資料":
                # AI 生成主題按鈕
                if st.button(f"🤖 分析「{sel_course}」主題", use_container_width=True):
                    with st.spinner("AI 正在分析課程架構..."):
                        # 呼叫 ai_logic
                        st.session_state.preview_topics[sel_course] = ai_logic.generate_course_topics(sel_course)
                        st.rerun()

                # 顯示主題選單
                if sel_course in st.session_state.preview_topics:
                    topic_list = st.session_state.preview_topics[sel_course]
                    sel_topic = st.radio("選擇學習單元", topic_list + ["✏️ 手動輸入主題..."])
                    
                    real_topic = st.text_input("請輸入自訂主題") if sel_topic == "✏️ 手動輸入主題..." else sel_topic

                    if st.button("✨ 生成預習指南", type="primary", use_container_width=True) and real_topic:
                         with st.spinner(f"AI 正在為您整理「{real_topic}」的學習資源..."):
                            st.session_state['preview_res'] = ai_logic.recommend_videos(sel_course, real_topic)
            else:
                st.info("請先匯入課表資料。")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='dashboard-card'><div class='card-title'>📚 AI 學習指南</div>", unsafe_allow_html=True)
            if 'preview_res' in st.session_state:
                st.markdown(st.session_state['preview_res'])
            else:
                st.info("👈 左側設定完畢後，AI 指南將顯示於此。")
            st.markdown("</div>", unsafe_allow_html=True)

    # === 頁面 5: MINDMAP ===
    elif st.session_state.page == "MindMap":
        st.markdown("<div class='dashboard-card'><div class='card-title'>🧠 AI 筆記視覺化</div>", unsafe_allow_html=True)
        
        c_input, c_output = st.columns([1, 2])
        
        with c_input:
            user_text = st.text_area("輸入你的筆記內容 (支援亂亂寫)", height=300, placeholder="例如：\n期末考重點\n1. React Hooks 用法\n2. API 串接流程\n3. 資料庫設計正規化")
            
            if st.button("✨ 繪製思維導圖", type="primary", use_container_width=True):
                if user_text:
                    with st.spinner("AI 正在理解你的筆記結構並繪圖..."):
                        # 1. 呼叫 AI 產生 DOT 碼
                        dot_code = ai_logic.generate_mindmap_code(user_text)
                        
                        if dot_code:
                            # 2. 轉換為圖片
                            img_src = graph_to_base64(dot_code)
                            st.session_state['mindmap_img'] = img_src
                        else:
                            st.error("AI 無法生成結構，請重試。")
        
        with c_output:
            if 'mindmap_img' in st.session_state and st.session_state['mindmap_img']:
                st.markdown(
                    f"""
                    <div style="text-align:center; background:#F9F9F9; padding:20px; border-radius:10px;">
                        <img src="{st.session_state['mindmap_img']}" style="max-width:100%; border:1px solid #ddd; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                        <br><br>
                        <a href="{st.session_state['mindmap_img']}" download="mindmap.png" style="text-decoration:none; color:{COLOR_MAIN}; font-weight:bold;">📥 下載圖片</a>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.info("請在左側輸入筆記，AI 將為您自動生成架構圖。")
        st.markdown("</div>", unsafe_allow_html=True)
        
