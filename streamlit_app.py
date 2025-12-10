import streamlit as st
import google.generativeai as genai
import io
import json
import datetime
import os
import docx

# -------------------------------------------------------------
# --- 1. 配置与多语言/画像定义 ---
# -------------------------------------------------------------

st.set_page_config(page_title="Judi Global Legal", page_icon="⚖️", layout="wide")

# 语言选项
LANG_OPTIONS = {
    "🇨🇳 中文": "zh",
    "🇺🇸 English": "en"
}

# 用户画像定义 (不同画像对应不同的推荐模版和关注点)
USER_PERSONAS = {
    "zh": {
        "catering": "🍽️ 餐饮业态",
        "service": "💆 服务业态",
        "solo": "💻 一人公司/独立开发者",
        "overseas": "🚢 出海企业 (Cross-border)",
        "manufacturing": "🏭 制造业",
        "group": "🏢 大型集团"
    },
    "en": {
        "catering": "🍽️ Catering/Restaurant",
        "service": "💆 Service Industry",
        "solo": "💻 Solopreneur/Indie Hacker",
        "overseas": "🚢 Cross-border Enterprise",
        "manufacturing": "🏭 Manufacturing",
        "group": "🏢 Large Corporation"
    }
}

# 推荐模版数据库 (根据画像推荐)
RECOMMENDED_TEMPLATES = {
    "catering": ["餐厅租赁合同", "食品安全责任书", "厨房员工雇佣合同", "特许经营协议"],
    "service": ["服务服务协议 (SLA)", "客户隐私保密协议", "会员充值协议", "兼职劳务合同"],
    "solo": ["软件外包开发合同", "知识产权转让协议", "免责声明 (Disclaimer)", "单人公司章程"],
    "overseas": ["跨境数据传输协议", "海外代理商分销合同", "GDPR合规声明", "国际货物销售合同 (CISG)"],
    "manufacturing": ["OEM代工生产协议", "原材料采购合同", "工厂安全生产责任书", "供应链保密协议 (NDA)"],
    "group": ["股权激励计划书", "合资经营合同 (JV)", "企业合规管理章程", "高管聘用协议"]
}

# 翻译字典
TRANSLATIONS = {
    "zh": {
        "app_title": "iTerms 法律顾问",
        "subtitle": "汇聚全球法律智慧，24小时服务每位客户",
        "sidebar_settings": "设置",
        "select_persona": "选择你的企业身份",
        "select_persona_help": "AI将根据你的身份提供定制化法律建议",
        "tab_consult": "🤖 AI法律顾问",
        "tab_templates": "📄 合同模版",
        "tab_lawyers": "🌍 找全球律师/律所",
        "tab_review": "📂 文书审查",
        "target_region": "目标法律管辖区/国家",
        "chat_placeholder": "输入你的法律问题，例如：如何在这个国家设立分公司？",
        "template_intro": "基于您的 **{persona}** 身份，为您推荐以下律师背书级别的模版：",
        "generate_btn": "AI 起草该文书",
        "lawyer_search_title": "连接全球法律网络",
        "lawyer_city": "目标城市 (默认: 深圳市)",
        "lawyer_area": "需要咨询的领域",
        "find_lawyer_btn": "生成律师名片",
        "processing": "AI 正在思考中...",
        "upload_area": "上传合同/法律文件 (PDF/Word/Txt)",
        "review_btn": "开始风险审查",
        "review_result_title": "审查报告",
        "welcome_msg": "你好，我是Judi。作为**{persona}**的法律顾问，今天只需一杯咖啡的时间，我就能帮你解决法律难题。",
        "lawyer_card_intro": "为您匹配到以下律师资源：",
        "consult_agent": "咨询该律师智能体"
    },
    "en": {
        "app_title": "Judi Global Legal",
        "subtitle": "Silicon Valley Minimalist · Your AI Legal Partner",
        "sidebar_settings": "Settings",
        "select_persona": "Select User Persona",
        "select_persona_help": "AI tailored legal advice based on your profile",
        "tab_consult": "🤖 AI Consultant",
        "tab_templates": "📄 Templates",
        "tab_lawyers": "🌍 Find Lawyers",
        "tab_review": "📂 Doc Review",
        "target_region": "Target Jurisdiction/Country",
        "chat_placeholder": "Ask a legal question, e.g., How to incorporate here?",
        "template_intro": "Based on your **{persona}** profile, here are lawyer-endorsed templates:",
        "generate_btn": "Draft with AI",
        "lawyer_search_title": "Connect Global Legal Network",
        "lawyer_city": "Target City (Default: Shenzhen)",
        "lawyer_area": "Practice Area",
        "find_lawyer_btn": "Generate Lawyer Card",
        "processing": "AI is thinking...",
        "upload_area": "Upload Document (PDF/Word/Txt)",
        "review_btn": "Start Risk Review",
        "review_result_title": "Review Report",
        "welcome_msg": "Hi, I'm Judi. As a legal consultant for **{persona}**, I can solve your legal challenges in the time it takes to drink a coffee.",
        "lawyer_card_intro": "Matched Legal Resource:",
        "consult_agent": "Chat with Agent"
    }
}

# -------------------------------------------------------------
# --- 2. CSS 样式 (Silicon Valley Minimalist) ---
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 全局字体与背景 */
    .stApp {
        background-color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        color: #1a202c;
    }
    
    /* 隐藏多余元素 */
    header, footer, [data-testid="stToolbar"] {visibility: hidden;}
    
    /* 标题样式 */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #000000 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        color: #718096;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* 侧边栏优化 */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }

    /* 卡片式布局 */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .card:hover {
        border-color: #cbd5e0;
        transform: translateY(-2px);
    }
    
    /* 律师名片样式 */
    .lawyer-card {
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        background: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
    }
    .lawyer-name { font-weight: bold; font-size: 1.2rem; color: #1e293b; }
    .lawyer-title { color: #64748b; font-size: 0.9rem; margin-bottom: 10px; }
    .tag {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 5px;
    }

    /* 按钮样式重置 */
    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #333333 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# --- 3. 核心逻辑与 API ---
# -------------------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing API Key")
    st.stop()
genai.configure(api_key=api_key)

def get_gemini_response(prompt, system_instruction):
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash', # 或者 gemini-1.5-pro
        system_instruction=system_instruction
    )
    response = model.generate_content(prompt)
    return response.text

# -------------------------------------------------------------
# --- 4. 侧边栏设置 ---
# -------------------------------------------------------------

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2245/2245128.png", width=60) # 示例图标
    
    # 语言选择
    lang_choice = st.selectbox("🌐 Language", list(LANG_OPTIONS.keys()))
    lang_code = LANG_OPTIONS[lang_choice]
    T = TRANSLATIONS[lang_code]
    
    st.markdown("---")
    st.subheader(T["sidebar_settings"])
    
    # 用户画像选择
    persona_options = USER_PERSONAS[lang_code]
    selected_persona_key = st.selectbox(
        T["select_persona"], 
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x],
        help=T["select_persona_help"]
    )
    current_persona_name = persona_options[selected_persona_key]

# -------------------------------------------------------------
# --- 5. 主界面 ---
# -------------------------------------------------------------

st.markdown(f"<h1>{T['app_title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{T['subtitle']}</div>", unsafe_allow_html=True)

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 欢迎语
    welcome = T["welcome_msg"].format(persona=current_persona_name)
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Tab 布局
tab1, tab2, tab3, tab4 = st.tabs([
    T["tab_consult"], 
    T["tab_templates"], 
    T["tab_lawyers"],
    T["tab_review"]
])

# --- Tab 1: AI 法律顾问 (Consultant) ---
with tab1:
    col_region, col_space = st.columns([1, 3])
    with col_region:
        target_country = st.text_input(T["target_region"], value="China" if lang_code == 'en' else "中国")
    
    # System Prompt for Consultant
    consultant_instruction = f"""
    You are Judi, a top-tier international lawyer.
    Current User Persona: {current_persona_name}.
    Target Jurisdiction: {target_country}.
    Language: {lang_code}.
    Style: Professional, concise, minimalist, risk-averse.
    Always provide citations or legal basis where possible.
    """

    # 聊天界面
    chat_container = st.container(height=400)
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(T["chat_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            with st.spinner(T["processing"]):
                response = get_gemini_response(prompt, consultant_instruction)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- Tab 2: 智能合同模版 (Templates) ---
with tab2:
    st.markdown(T["template_intro"].format(persona=current_persona_name))
    
    # 获取该画像的推荐模版
    rec_list = RECOMMENDED_TEMPLATES.get(selected_persona_key, [])
    
    cols = st.columns(2)
    for idx, template_name in enumerate(rec_list):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="card">
                <h3>📜 {template_name}</h3>
                <p style="color:#718096; font-size:0.9rem;">适用于 {current_persona_name} 的标准律师背书版本。</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{T['generate_btn']} - {template_name}", key=f"btn_{idx}"):
                with st.spinner(T["processing"]):
                    # 生成模版
                    draft_prompt = f"Please draft a professional '{template_name}' for a '{current_persona_name}' user. Jurisdiction: {target_country}. Include standard clauses for risk protection."
                    draft_content = get_gemini_response(draft_prompt, consultant_instruction)
                    st.text_area("Draft Result", draft_content, height=300)
                    st.success("Draft generated based on legal standards.")

# --- Tab 3: 找全球律师 (Global Network) ---
with tab3:
    st.subheader(T["lawyer_search_title"])
    
    lc1, lc2 = st.columns(2)
    with lc1:
        city = st.text_input(T["lawyer_city"], value="Shenzhen" if lang_code == 'en' else "深圳市")
    with lc2:
        area = st.text_input(T["lawyer_area"], value="Corporate/IP" if lang_code == 'en' else "公司法/知识产权")
        
    if st.button(T["find_lawyer_btn"], type="primary"):
        with st.spinner(T["processing"]):
            # Prompt 生成模拟名片数据 JSON
            card_prompt = f"""
            Generate a fictional but realistic top-tier lawyer profile for: City={city}, Area={area}.
            Output strictly valid JSON format with keys:
            "name", "firm", "title", "intro" (2 sentences), "tags" (list of 3 skills), 
            "template_specialty" (one document name), "legal_letter_style" (e.g. Tough/Concise).
            Language: {lang_code}.
            """
            try:
                # 稍微清洗一下返回，确保是JSON
                json_str = get_gemini_response(card_prompt, "You are a data generator. Output only JSON.").replace("```json", "").replace("```", "")
                data = json.loads(json_str)
                
                st.markdown(T["lawyer_card_intro"])
                
                # 渲染名片
                tags_html = "".join([f"<span class='tag'>{t}</span>" for t in data['tags']])
                
                st.markdown(f"""
                <div class="lawyer-card">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <div class="lawyer-name">{data['name']}</div>
                            <div class="lawyer-title">{data['firm']} | {data['title']}</div>
                        </div>
                        <div style="font-size:2rem;">⚖️</div>
                    </div>
                    <div style="margin: 10px 0;">{tags_html}</div>
                    <p style="color:#4a5568; font-size:0.95rem; line-height:1.5;">{data['intro']}</p>
                    <hr style="border:0; border-top:1px dashed #cbd5e0; margin:15px 0;">
                    <div style="font-size:0.85rem; color:#64748b;">
                        <div>📄 <b>擅长模版:</b> {data['template_specialty']}</div>
                        <div>📨 <b>函件风格:</b> {data['legal_letter_style']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 模拟“咨询智能体”按钮
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"💬 {T['consult_agent']} - {data['name']}"):
                    st.info(f"正在连接 {data['name']} 的 AI 数字分身... (Demo)")
                    
            except Exception as e:
                st.error("AI生成名片失败，请重试。")

# --- Tab 4: 文书审查 (Risk Review) ---
with tab4:
    uploaded_file = st.file_uploader(T["upload_area"], type=['pdf', 'docx', 'txt'])
    
    if uploaded_file and st.button(T["review_btn"]):
        with st.spinner(T["processing"]):
            # 读取文件逻辑 (简化版)
            content = ""
            if uploaded_file.type == "text/plain":
                content = uploaded_file.getvalue().decode("utf-8")
            elif "pdf" in uploaded_file.type:
                content = "[PDF content placeholder - requires OCR/Extraction]"
            elif "document" in uploaded_file.type: # docx
                doc = docx.Document(uploaded_file)
                content = "\n".join([p.text for p in doc.paragraphs])
            
            review_prompt = f"""
            Act as a strict compliance lawyer. Review the following contract content based on the persona '{current_persona_name}'.
            Highlight 3 Core Risks and provide amendments.
            Content snippet: {content[:2000]}...
            Language: {lang_code}
            """
            
            result = get_gemini_response(review_prompt, consultant_instruction)
            
            st.subheader(T["review_result_title"])
            st.markdown(result)
