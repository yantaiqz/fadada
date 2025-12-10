import streamlit as st
import google.generativeai as genai
import json
import docx

# -------------------------------------------------------------
# --- 1. 配置与多语言/画像定义 ---
# -------------------------------------------------------------

st.set_page_config(page_title="iTerms | Legal Workspace", page_icon="⚖️", layout="wide")

# 语言选项
LANG_OPTIONS = {
    "🇨🇳 中文": "zh",
    "🇺🇸 English": "en"
}

# 用户画像定义
USER_PERSONAS = {
    "zh": {
        "catering": "🍽️ 餐饮业主",
        "service": "💆 服务业经营者",
        "solo": "💻 独立开发者/自由职业者",
        "overseas": "🚢 出海企业主",
        "manufacturing": "🏭 制造业经理",
        "group": "🏢 集团法务"
    },
    "en": {
        "catering": "🍽️ Restaurant Owner",
        "service": "💆 Service Provider",
        "solo": "💻 Indie Hacker / Freelancer",
        "overseas": "🚢 Cross-border Founder",
        "manufacturing": "🏭 Manufacturing Manager",
        "group": "🏢 Corporate Counsel"
    }
}

# 推荐模版数据库
RECOMMENDED_TEMPLATES = {
    "catering": ["店铺租赁合同", "食品安全承诺书", "员工雇佣协议", "特许经营授权书"],
    "service": ["服务等级协议 (SLA)", "客户隐私政策", "预付款服务协议", "兼职劳务合同"],
    "solo": ["软件开发外包合同", "知识产权转让协议", "免责声明 (Disclaimer)", "独立顾问协议"],
    "overseas": ["跨境数据传输条款", "海外独家代理协议", "GDPR 合规声明", "国际销售合同 (CISG)"],
    "manufacturing": ["OEM 委托加工合同", "采购框架协议", "安全生产责任书", "保密协议 (NDA)"],
    "group": ["期权激励计划", "合资经营合同 (JV)", "集团合规章程", "高管聘用协议"]
}

# 翻译字典
TRANSLATIONS = {
    "zh": {
        "tab_templates": "合同库", # 修改顺序 No.1
        "tab_consult": "咨询顾问", # 修改顺序 No.2
        "tab_lawyers": "寻找专家", # 修改顺序 No.3
        "tab_review": "文书审查", # 修改顺序 No.4
        "start_post": "开始咨询...",
        "connect_btn": "建立联系",
        "chat_placeholder": "在此输入法律问题...",
        "target_region_label": "管辖区域",
        "generate_btn": "AI 起草",
        "processing": "正在生成中...",
        "lawyer_card_title": "推荐的法律专家",
        "upload_text": "上传合同文件 (PDF/Docx)",
        "sidebar_headline": "高级法律会员"
    },
    "en": {
        "tab_templates": "Templates",
        "tab_consult": "Consultant",
        "tab_lawyers": "Find Experts",
        "tab_review": "Doc Review",
        "start_post": "Start a consultation...",
        "connect_btn": "Connect",
        "chat_placeholder": "Type your legal question...",
        "target_region_label": "Jurisdiction",
        "generate_btn": "Draft with AI",
        "processing": "Processing...",
        "lawyer_card_title": "Recommended Legal Experts",
        "upload_text": "Upload Contract (PDF/Docx)",
        "sidebar_headline": "Premium Legal Member"
    }
}

# -------------------------------------------------------------
# --- 2. CSS 样式 (Clean LinkedIn Style) ---
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 引入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    :root {
        --linkedin-blue: #0a66c2;
        --linkedin-blue-hover: #004182;
        --bg-color: #f3f2ef;
        --card-bg: #ffffff;
        --text-dark: #191919;
        --text-gray: #666666;
        --border-color: #e0dfdc;
        --radius: 8px;
    }

    /* 全局设置 */
    .stApp {
        background-color: var(--bg-color) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: var(--text-dark);
    }
    
    /* 隐藏默认 Header 和 Toolbar */
    header, footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* 卡片通用样式 */
    .li-card {
        background: var(--card-bg);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.04);
    }

    /* 侧边栏样式重写 */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: none;
        padding-top: 0rem;
    }
    
    /* 侧边栏个人卡片 - 简化版 */
    .profile-bg {
        background: #a0b4b7;
        height: 60px;
        border-radius: var(--radius) var(--radius) 0 0;
        margin: -16px -16px 0 -16px;
    }
    .profile-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        border: 2px solid white;
        background: #eee;
        margin: -36px auto 10px auto;
        display: block;
        text-align: center;
        line-height: 72px;
        font-size: 30px;
    }
    .profile-name {
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--text-dark);
    }
    .profile-headline {
        text-align: center;
        color: var(--text-gray);
        font-size: 0.85rem;
        margin-bottom: 5px;
    }

    /* Tabs 样式优化 */
    [data-testid="stTabs"] {
        background: white;
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 0 10px;
        margin-bottom: 20px;
    }
    [data-testid="stTabs"] button {
        color: var(--text-gray);
        font-weight: 600;
        border-bottom: 2px solid transparent;
        padding: 12px 16px;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--linkedin-blue) !important;
        border-bottom: 2px solid var(--linkedin-blue) !important;
    }

    /* 按钮样式 */
    .stButton > button {
        background-color: var(--linkedin-blue) !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: var(--linkedin-blue-hover) !important;
    }

    /* 聊天框输入 */
    .stTextInput > div > div > input {
        border-radius: 20px;
        background-color: #eef3f8;
        border: 1px solid transparent;
        padding: 10px 15px;
    }
    .stTextInput > div > div > input:focus {
        background-color: white;
        border-color: var(--text-dark);
        box-shadow: 0 0 0 1px var(--text-dark);
    }

    /* 律师卡片 */
    .lawyer-item {
        display: flex;
        align-items: flex-start;
        padding: 16px 0;
        border-bottom: 1px solid #eee;
    }
    .lawyer-item:last-child { border-bottom: none; }
    .lawyer-img {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #eef3f8;
        margin-right: 16px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# --- 3. 核心 API 设置 ---
# -------------------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, system_instruction):
    if not api_key:
        return "⚠️ 请配置 API Key 以使用 AI 功能。"
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash', 
        system_instruction=system_instruction
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# -------------------------------------------------------------
# --- 4. 侧边栏 (Profile Rail - 精简版) ---
# -------------------------------------------------------------

with st.sidebar:
    # 语言选择
    lang_choice = st.selectbox("Language / 语言", list(LANG_OPTIONS.keys()))
    lang_code = LANG_OPTIONS[lang_choice]
    T = TRANSLATIONS[lang_code]
    
    st.markdown("---")
    
    # 身份选择
    persona_options = USER_PERSONAS[lang_code]
    selected_persona_key = st.selectbox(
        "Identity / 身份", 
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x]
    )
    current_persona_name = persona_options[selected_persona_key]

    # 简化的个人卡片 (移除社交数据)
    st.markdown(f"""
    <div class="li-card" style="padding:0; overflow:hidden; margin-top: 20px;">
        <div class="profile-bg"></div>
        <div class="profile-avatar">👨‍💼</div>
        <div style="padding: 16px; padding-bottom: 24px;">
            <div class="profile-name">{current_persona_name}</div>
            <div class="profile-headline">{T['sidebar_headline']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# --- 5. 主界面 (Workspace) ---
# -------------------------------------------------------------

# 初始化 Session State
if "messages" not in st.session_state or st.session_state.get("current_persona") != current_persona_name:
    st.session_state.messages = []
    st.session_state.current_persona = current_persona_name

# System Instructions
consultant_instruction = f"""
Role: Professional Legal Consultant named Judi on a professional network platform.
User: {current_persona_name}.
Tone: Professional, concise, helpful, like a senior partner at a top firm.
"""

# Tabs 布局 - 调整顺序: 合同库 -> 咨询 -> 律师 -> 审查
tab_templates, tab_consult, tab_lawyers, tab_review = st.tabs([
    f"📄 {T['tab_templates']}", 
    f"💬 {T['tab_consult']}", 
    f"👥 {T['tab_lawyers']}",
    f"🛡️ {T['tab_review']}"
])

# --- Tab 1: 合同库 (Templates) ---
with tab_templates:
    st.markdown(f"### {T['tab_templates']}")
    rec_list = RECOMMENDED_TEMPLATES.get(selected_persona_key, [])
    
    # 使用 2 列布局展示模版
    cols = st.columns(2)
    for idx, template_name in enumerate(rec_list):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div class="li-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div style="width:48px; height:48px; background:#eef3f8; display:flex; align-items:center; justify-content:center; border-radius:4px;">
                            📄
                        </div>
                    </div>
                    <div style="margin-top:10px; font-weight:600; font-size:1.1rem; color:var(--linkedin-blue);">
                        {template_name}
                    </div>
                    <div style="font-size:0.9rem; color:#666; margin-bottom:15px;">
                         {current_persona_name} • Verified
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(T['generate_btn'], key=f"tpl_{idx}", use_container_width=True):
                    # 模拟生成逻辑
                    st.success(f"Drafting {template_name}...")
                    st.code("# DRAFT AGREEMENT\n\n1. PARTIES...", language="markdown")


# --- Tab 2: 咨询顾问 (Consultant - 全宽模式) ---
with tab_consult:
    # 移除了右侧的 "为您推荐" 列，改为全宽布局
    
    # 顶部状态栏
    st.markdown(f"""
    <div class="li-card" style="display:flex; align-items:center;">
        <div style="width:40px; height:40px; border-radius:50%; background:#eee; margin-right:15px; display:flex; align-items:center; justify-content:center;">👨‍💼</div>
        <div style="color:#666; font-weight:500;">
           {T['start_post']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 目标区域设定
    target_country = st.text_input(T["target_region_label"], value="China" if lang_code == 'en' else "中国")
    
    # 历史消息显示
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👨‍💼"
        bg_color = "#f3f6f8" if msg["role"] == "assistant" else "#ffffff"
        
        st.markdown(f"""
        <div class="li-card" style="display:flex; flex-direction:row; gap:16px; background:{bg_color}; border:none;">
            <div style="font-size:28px;">{avatar}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:700; font-size:0.9rem; margin-bottom:4px; color:#191919;">
                    {'Judi (AI Legal Partner)' if msg['role']=='assistant' else 'You'}
                </div>
                <div style="font-size:0.95rem; line-height:1.6; color:#191919;">{msg['content']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 输入框区域
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder=T["chat_placeholder"], label_visibility="collapsed")
        col_actions = st.columns([6, 1])
        with col_actions[1]:
            submitted = st.form_submit_button("Send ✈️")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(T["processing"]):
            full_instruction = consultant_instruction + f" Target Jurisdiction: {target_country}."
            ai_reply = get_gemini_response(user_input, full_instruction)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()


# --- Tab 3: 寻找专家 (Lawyers - 移除广告) ---
with tab_lawyers:
    st.markdown(f"""
    <div class="li-card">
        <h3>{T['lawyer_card_title']}</h3>
        <p style="color:#666; font-size:0.9rem;">Based on your profile: <b>{current_persona_name}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # 移除右侧广告列，使用全宽
    
    # 生成两个模拟律师数据
    mock_lawyers = [
        {"name": "Sarah Chen", "title": "Partner @ Global Law", "desc": "Specialist in Corporate Law & IP Protection"},
        {"name": "David Müller", "title": "Senior Counsel", "desc": "Expert in Cross-border Trade & EU Compliance"},
        {"name": "James Li", "title": "Legal Advisor", "desc": "Labor Law & Employment Contracts"}
    ]
    
    for lw in mock_lawyers:
        st.markdown(f"""
        <div class="li-card lawyer-item">
            <div class="lawyer-img">{lw['name'][0]}</div>
            <div class="lawyer-info" style="flex-grow:1;">
                <h4 style="margin:0; font-size:1.1rem; color:#191919;">{lw['name']}</h4>
                <p style="margin:4px 0 2px 0; color:#191919;">{lw['title']}</p>
                <p style="color:#666; font-size:0.9rem; margin:0;">{lw['desc']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 按钮独立一行，避免布局拥挤
        col_btn, _ = st.columns([1, 5])
        with col_btn:
            st.button(f"👤 {T['connect_btn']}", key=f"connect_{lw['name']}")


# --- Tab 4: 文书审查 (Review) ---
with tab_review:
    st.markdown(f"""
    <div class="li-card" style="text-align:center; padding:60px 20px;">
        <div style="font-size:48px; margin-bottom:20px; color:var(--linkedin-blue);">📂</div>
        <h3 style="color:#191919;">{T['upload_text']}</h3>
        <p style="color:#666; margin-bottom:30px; max-width:500px; margin-left:auto; margin-right:auto;">
            AI 自动扫描合同条款，识别潜在风险漏洞。安全、私密、高效。
        </p>
        <div style="max-width:400px; margin:0 auto;">
            </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", label_visibility="collapsed")
    
    if uploaded_file:
        st.info("Document uploaded. Analyzing risk factors...")
        # 模拟结果展示
        st.markdown("""
        <div class="li-card">
            <h4 style="color:#d93025; margin-top:0;">Risk Level: Medium ⚠️</h4>
            <hr style="border:0; border-top:1px solid #eee; margin:15px 0;">
            <p style="font-weight:600;">Analysis Report:</p>
            <ul style="color:#191919; line-height:1.6;">
                <li>Clause 4.2 contains ambiguous liability terms regarding force majeure.</li>
                <li>Missing specific jurisdiction definition for cross-border disputes (Art 9).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
