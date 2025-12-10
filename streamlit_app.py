import streamlit as st
import google.generativeai as genai
import io
import json
import docx

# -------------------------------------------------------------
# --- 1. 配置与多语言/画像定义 ---
# -------------------------------------------------------------

st.set_page_config(page_title="iTerms | Legal Network", page_icon="⚖️", layout="wide")

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
        "nav_home": "首页",
        "nav_network": "人脉",
        "nav_jobs": "职位",
        "nav_messaging": "消息",
        "sidebar_profile": "个人档案",
        "sidebar_views": "谁看过你的档案",
        "sidebar_connections": "一度人脉",
        "tab_consult": "咨询顾问",
        "tab_templates": "合同库",
        "tab_lawyers": "寻找专家",
        "tab_review": "文书审查",
        "welcome_back": "欢迎回来, ",
        "start_post": "开始咨询或创建草案...",
        "suggested_for_you": "为您推荐",
        "connect_btn": "建立联系",
        "follow_btn": "关注",
        "chat_placeholder": "在此输入法律问题...",
        "target_region_label": "管辖区域",
        "generate_btn": "AI 起草",
        "processing": "正在生成中...",
        "lawyer_card_title": "推荐的法律专家",
        "upload_text": "上传合同文件 (PDF/Docx)"
    },
    "en": {
        "nav_home": "Home",
        "nav_network": "My Network",
        "nav_jobs": "Jobs",
        "nav_messaging": "Messaging",
        "sidebar_profile": "Profile",
        "sidebar_views": "Profile viewers",
        "sidebar_connections": "Connections",
        "tab_consult": "Consultant",
        "tab_templates": "Templates",
        "tab_lawyers": "Find Experts",
        "tab_review": "Doc Review",
        "welcome_back": "Welcome back, ",
        "start_post": "Start a consultation or draft...",
        "suggested_for_you": "Suggested for you",
        "connect_btn": "Connect",
        "follow_btn": "Follow",
        "chat_placeholder": "Type your legal question...",
        "target_region_label": "Jurisdiction",
        "generate_btn": "Draft with AI",
        "processing": "Processing...",
        "lawyer_card_title": "Recommended Legal Experts",
        "upload_text": "Upload Contract (PDF/Docx)"
    }
}

# -------------------------------------------------------------
# --- 2. CSS 样式 (LinkedIn Style) ---
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 引入字体：模拟系统字体栈 */
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
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Fira Sans", Ubuntu, Oxygen, "Oxygen Sans", Cantarell, "Droid Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Lucida Grande", Helvetica, Arial, sans-serif !important;
        color: var(--text-dark);
    }
    
    /* 隐藏默认 Header */
    header, footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* 顶部导航栏模拟 */
    .nav-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 52px;
        background: white;
        border-bottom: 1px solid var(--border-color);
        z-index: 9999;
        display: flex;
        align-items: center;
        padding: 0 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .nav-logo {
        font-size: 24px;
        font-weight: bold;
        color: var(--linkedin-blue);
        margin-right: 20px;
    }
    
    /* 卡片通用样式 */
    .li-card {
        background: var(--card-bg);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.04); /* 极细微的阴影 */
    }

    /* 侧边栏样式重写 (Profile Rail) */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: none;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: var(--text-gray);
        font-size: 0.85rem;
    }
    
    /* 侧边栏个人卡片 */
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
        cursor: pointer;
    }
    .profile-name:hover { text-decoration: underline; }
    .profile-headline {
        text-align: center;
        color: var(--text-gray);
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .stats-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        padding: 4px 0;
        color: var(--text-gray);
        font-weight: 600;
    }
    .stats-val { color: var(--linkedin-blue); }

    /* Tabs 样式优化 - 类似 LinkedIn 的 Sub-nav */
    [data-testid="stTabs"] {
        background: white;
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 0 10px;
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

    /* 按钮样式 - LinkedIn Blue Buttons */
    .stButton > button {
        background-color: var(--linkedin-blue) !important;
        color: white !important;
        border-radius: 24px !important; /* 胶囊按钮 */
        border: none !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: var(--linkedin-blue-hover) !important;
    }
    /* 次级按钮风格 (通过特定Key区分太复杂，这里统一样式，但在HTML中会有不同) */

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
        box-shadow: none;
    }

    /* 律师卡片 (People Card) */
    .lawyer-item {
        display: flex;
        align-items: flex-start;
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }
    .lawyer-item:last-child { border-bottom: none; }
    .lawyer-img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #eef3f8;
        margin-right: 12px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .lawyer-info h4 { margin: 0; font-size: 1rem; color: rgba(0,0,0,0.9); }
    .lawyer-info p { margin: 2px 0; font-size: 0.85rem; color: var(--text-gray); }
    
</style>

<div class="nav-bar">
    <div class="nav-logo">in <span style="font-size:18px; color:#666;">| Legal</span></div>
    <div style="flex-grow:1;"></div>
    <div style="font-size:14px; font-weight:600; color:#666; margin-left:20px; cursor:pointer;">Home</div>
    <div style="font-size:14px; color:#666; margin-left:20px; cursor:pointer;">My Network</div>
    <div style="font-size:14px; color:#666; margin-left:20px; cursor:pointer;">Jobs</div>
    <div style="font-size:14px; color:#666; margin-left:20px; cursor:pointer;">Messaging</div>
</div>
<div style="height: 40px;"></div> """, unsafe_allow_html=True)


# -------------------------------------------------------------
# --- 3. 核心 API 设置 ---
# -------------------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    # 仅为演示，实际应报错
    pass 
else:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, system_instruction):
    if not api_key:
        return "⚠️ Please config API Key to generate content."
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
# --- 4. 侧边栏 (Profile Rail) ---
# -------------------------------------------------------------

with st.sidebar:
    # 语言选择
    lang_choice = st.selectbox("Language / 语言", list(LANG_OPTIONS.keys()))
    lang_code = LANG_OPTIONS[lang_choice]
    T = TRANSLATIONS[lang_code]
    
    # 身份选择
    persona_options = USER_PERSONAS[lang_code]
    selected_persona_key = st.selectbox(
        "Identity", 
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x]
    )
    current_persona_name = persona_options[selected_persona_key]

    # 模拟 LinkedIn 左侧 Profile Rail
    st.markdown(f"""
    <div class="li-card" style="padding:0; overflow:hidden;">
        <div class="profile-bg"></div>
        <div class="profile-avatar">👨‍💼</div>
        <div style="padding: 16px;">
            <div class="profile-name">{current_persona_name}</div>
            <div class="profile-headline">Premium Legal Member</div>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
            <div class="stats-row">
                <span>{T['sidebar_views']}</span>
                <span class="stats-val">42</span>
            </div>
            <div class="stats-row">
                <span>{T['sidebar_connections']}</span>
                <span class="stats-val">158</span>
            </div>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
            <div style="font-size:0.8rem; font-weight:600; color:#000;">
                ⭐ Saved Items
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 模拟 "Recent" 模块
    st.markdown(f"""
    <div class="li-card">
        <div style="font-size:0.8rem; margin-bottom:10px;"><b>Recent</b></div>
        <div style="font-size:0.8rem; color:#666; margin-bottom:5px;"># commercial_law</div>
        <div style="font-size:0.8rem; color:#666; margin-bottom:5px;"># {selected_persona_key}_trends</div>
        <div style="font-size:0.8rem; color:#666; margin-bottom:5px;">👥 Legal Tech Group</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# --- 5. 主界面 (Feed & Dashboard) ---
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

# Tabs 布局 - 模拟主内容导航
tab1, tab2, tab3, tab4 = st.tabs([
    f"💬 {T['tab_consult']}", 
    f"📄 {T['tab_templates']}", 
    f"👥 {T['tab_lawyers']}",
    f"🛡️ {T['tab_review']}"
])

# --- Tab 1: 法律顾问 (Messaging/Feed Style) ---
with tab1:
    # 模拟 "Start a post" 区域作为输入框提示
    st.markdown(f"""
    <div class="li-card" style="display:flex; align-items:center;">
        <div style="width:48px; height:48px; border-radius:50%; background:#eee; margin-right:15px; display:flex; align-items:center; justify-content:center;">👨‍💼</div>
        <div style="flex-grow:1; border:1px solid #ccc; border-radius:30px; padding:12px 20px; color:#666; font-weight:600;">
            {T['start_post']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 聊天区域
    col1, col2 = st.columns([3, 1]) # 右侧留白或放广告位
    
    with col1:
        # 目标区域设定
        target_country = st.text_input(T["target_region_label"], value="China" if lang_code == 'en' else "中国")
        
        # 历史消息显示
        for msg in st.session_state.messages:
            avatar = "🤖" if msg["role"] == "assistant" else "👨‍💼"
            bg_color = "#f3f6f8" if msg["role"] == "assistant" else "#ffffff"
            align = "flex-start" 
            
            st.markdown(f"""
            <div class="li-card" style="display:flex; flex-direction:row; gap:10px; background:{bg_color}; border:none;">
                <div style="font-size:24px;">{avatar}</div>
                <div style="flex-grow:1;">
                    <div style="font-weight:700; font-size:0.9rem; margin-bottom:4px;">
                        {'Judi (AI Legal Partner)' if msg['role']=='assistant' else 'You'}
                    </div>
                    <div style="font-size:0.95rem; line-height:1.5;">{msg['content']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 输入框
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("", placeholder=T["chat_placeholder"], label_visibility="collapsed")
            col_actions = st.columns([6, 1])
            with col_actions[1]:
                submitted = st.form_submit_button("Send ✈️")

        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            # 模拟回复
            with st.spinner(T["processing"]):
                full_instruction = consultant_instruction + f" Target Jurisdiction: {target_country}."
                ai_reply = get_gemini_response(user_input, full_instruction)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

    with col2:
        # 模拟右侧推荐栏 (LinkedIn Right Rail)
        st.markdown(f"""
        <div class="li-card">
            <div style="font-size:0.9rem; font-weight:600; margin-bottom:12px;">{T['suggested_for_you']}</div>
            <div style="display:flex; margin-bottom:10px;">
                <div style="width:40px; height:40px; background:#ddd; margin-right:10px;"></div>
                <div>
                    <div style="font-size:0.85rem; font-weight:600;">Legal Tech Daily</div>
                    <button style="border:1px solid #666; background:none; border-radius:15px; padding:2px 10px; font-size:0.8rem; margin-top:2px;">+ {T['follow_btn']}</button>
                </div>
            </div>
             <div style="display:flex;">
                <div style="width:40px; height:40px; background:#ddd; margin-right:10px;"></div>
                <div>
                    <div style="font-size:0.85rem; font-weight:600;">Global Compliance</div>
                    <button style="border:1px solid #666; background:none; border-radius:15px; padding:2px 10px; font-size:0.8rem; margin-top:2px;">+ {T['follow_btn']}</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- Tab 2: 合同模版 (Job/Course Cards Style) ---
with tab2:
    st.markdown(f"### {T['suggested_for_you']}")
    rec_list = RECOMMENDED_TEMPLATES.get(selected_persona_key, [])
    
    # Grid Layout
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
                        <div style="color:#666; font-size:1.2rem;">...</div>
                    </div>
                    <div style="margin-top:10px; font-weight:600; font-size:1.1rem; color:var(--linkedin-blue);">
                        {template_name}
                    </div>
                    <div style="font-size:0.9rem; color:#666; margin-bottom:15px;">
                        Standard • {current_persona_name} • Verified
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(T['generate_btn'], key=f"tpl_{idx}", use_container_width=True):
                    # 模拟生成逻辑
                    st.success(f"Drafting {template_name}...")
                    st.code("# DRAFT AGREEMENT\n\n1. PARTIES...", language="markdown")


# --- Tab 3: 找律师 (People/Network Style) ---
with tab3:
    st.markdown(f"""
    <div class="li-card">
        <h3>{T['lawyer_card_title']}</h3>
        <p style="color:#666; font-size:0.9rem;">Based on your profile: <b>{current_persona_name}</b></p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        # 生成两个模拟律师数据
        mock_lawyers = [
            {"name": "Sarah Chen", "title": "Partner @ Global Law", "desc": "Specialist in Corporate Law & IP Protection"},
            {"name": "David Müller", "title": "Senior Counsel", "desc": "Expert in Cross-border Trade & EU Compliance"}
        ]
        
        for lw in mock_lawyers:
            # 模拟 LinkedIn "People" 卡片
            st.markdown(f"""
            <div class="li-card lawyer-item">
                <div class="lawyer-img">{lw['name'][0]}</div>
                <div class="lawyer-info" style="flex-grow:1;">
                    <h4>{lw['name']} <span style="font-weight:400; color:#666; font-size:0.8rem;">• 2nd</span></h4>
                    <p>{lw['title']}</p>
                    <p style="color:#666; font-size:0.8rem;">{lw['desc']}</p>
                    <div style="margin-top:5px; font-size:0.8rem; color:#666;">
                        <span style="display:inline-block; vertical-align:middle;">👥</span> 12 mutual connections
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            col_btn, _ = st.columns([1, 4])
            with col_btn:
                st.button(f"👤 {T['connect_btn']}", key=f"connect_{lw['name']}")

    with c2:
        st.image("https://placehold.co/300x250/png?text=Ad:+Legal+Conf+2025", caption="Promoted", use_column_width=True)


# --- Tab 4: 文书审查 (Document UI) ---
with tab4:
    st.markdown(f"""
    <div class="li-card" style="text-align:center; padding:40px 20px;">
        <div style="font-size:40px; margin-bottom:20px;">📂</div>
        <h3 style="color:#000;">{T['upload_text']}</h3>
        <p style="color:#666; margin-bottom:20px;">
            Get AI-powered risk analysis instantly. Private & Secure.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", label_visibility="collapsed")
    
    if uploaded_file:
        st.info("Document uploaded. Analyzing risk factors...")
        # 模拟结果展示
        st.markdown("""
        <div class="li-card">
            <h4 style="color:#d93025;">Risk Level: Medium ⚠️</h4>
            <hr>
            <p><b>Analysis Report:</b></p>
            <ul>
                <li>Clause 4.2 contains ambiguous liability terms.</li>
                <li>Missing jurisdiction definition for cross-border disputes.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
