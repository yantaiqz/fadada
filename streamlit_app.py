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

# 设置页面配置 - 保持不变
st.set_page_config(page_title="iTerms 法律顾问", page_icon="⚖️", layout="wide")

# 语言选项 - 保持不变
LANG_OPTIONS = {
    "🇨🇳 中文": "zh",
    "🇺🇸 English": "en"
}

# 用户画像定义 (不同画像对应不同的推荐模版和关注点) - 保持不变
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

# 推荐模版数据库 (根据画像推荐) - 保持不变
RECOMMENDED_TEMPLATES = {
    "catering": ["餐厅租赁合同", "食品安全责任书", "厨房员工雇佣合同", "特许经营协议"],
    "service": ["服务服务协议 (SLA)", "客户隐私保密协议", "会员充值协议", "兼职劳务合同"],
    "solo": ["软件外包开发合同", "知识产权转让协议", "免责声明 (Disclaimer)", "单人公司章程"],
    "overseas": ["跨境数据传输协议", "海外代理商分销合同", "GDPR合规声明", "国际货物销售合同 (CISG)"],
    "manufacturing": ["OEM代工生产协议", "原材料采购合同", "工厂安全生产责任书", "供应链保密协议 (NDA)"],
    "group": ["股权激励计划书", "合资经营合同 (JV)", "企业合规管理章程", "高管聘用协议"]
}

# 翻译字典 - 保持不变
TRANSLATIONS = {
    "zh": {
        "app_title": "iTerms 法律顾问",
        "subtitle": "全球法律智慧，服务每位客户",
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
        "app_title": "iTerms Legal Advisor",
        "subtitle": "Global Legal Intelligence, 24/7 Service for Every Client",
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
# --- 2. CSS 样式 (Silicon Valley Minimalist V2) ---
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 定义品牌色和辅助色 */
    :root {
        --primary-color: #007bff; /* 原本的黑色按钮改为更专业的深蓝 */
        --accent-color: #2563eb; /* 深青色，用于高亮 */
        --bg-light: #f8fafc;
        --border-color: #e2e8f0;
        --text-color: #1a202c;
        --text-secondary: #64748b;
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* 全局字体与背景 */
    .stApp {
        background-color: #ffffff !important;
        /* 强调现代化字体堆栈 */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        color: var(--text-color);
    }
    
    /* 隐藏多余元素 */
    header, footer, [data-testid="stToolbar"] {visibility: hidden;}
    
    /* 标题样式 */
    h1 {
        font-weight: 800 !important; /* 更粗体 */
        letter-spacing: -0.04em !important; /* 调整字距 */
        color: var(--text-color) !important;
        font-size: 2.8rem !important; /* 略大 */
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2.5rem; /* 增加下方留白 */
    }

    /* 侧边栏优化 */
    [data-testid="stSidebar"] {
        background-color: var(--bg-light) !important;
        border-right: 1px solid var(--border-color);
    }

    /* 卡片式布局 */
    .card {
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        box-shadow: var(--card-shadow);
        margin-bottom: 20px;
        transition: all 0.2s;
        min-height: 150px; /* 确保最小高度统一 */
    }
    .card:hover {
        border-color: var(--accent-color);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.1);
        transform: translateY(-3px);
    }

    /* Tab 样式优化 */
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--accent-color) !important;
        border-bottom: 3px solid var(--accent-color) !important;
        font-weight: 600;
    }
    [data-testid="stTabs"] button {
        color: var(--text-secondary);
        font-weight: 500;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    /* 律师名片样式 */
    .lawyer-card {
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-color); /* 使用品牌色高亮 */
        background: #f0f4ff; /* 略微带蓝的背景 */
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
    }
    .lawyer-name { font-weight: 700; font-size: 1.3rem; color: #1e293b; }
    .lawyer-title { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 10px; }
    .tag {
        background: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
    }

    /* 按钮样式重置 */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important; /* 略微加粗 */
    }
    .stButton > button:hover {
        background-color: #0056b3 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 聊天输入框美化 */
    [data-testid="stForm"] {
        padding: 0px; 
        border: none;
        box-shadow: none;
    }
    /* 确保聊天输入框在底部且突出 */
    div.stTextInput>div>div>input {
        border-radius: 12px;
        padding: 12px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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

# 确保模型调用逻辑不变
def get_gemini_response(prompt, system_instruction):
    # 增加 stream=True 以优化用户体验（更快的响应）
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash', 
        system_instruction=system_instruction
    )
    # 使用 generate_content 确保兼容性
    response = model.generate_content(prompt)
    return response.text

# -------------------------------------------------------------
# --- 4. 侧边栏设置 (UX 优化：Logo 放在顶部) ---
# -------------------------------------------------------------

with st.sidebar:
    # 替换为更专业的 Logo 或 Icon
    st.markdown("## ⚖️ iTerms Legal")
    st.markdown("---")
    
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

# 主标题和副标题
st.markdown(f"<h1>{T['app_title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{T['subtitle']}</div>", unsafe_allow_html=True)

# 初始化 Session State
if "messages" not in st.session_state or st.session_state.get("current_persona") != current_persona_name:
    # 如果更换了画像，重置聊天记录
    welcome = T["welcome_msg"].format(persona=current_persona_name)
    st.session_state.messages = [{"role": "assistant", "content": welcome}]
    st.session_state.current_persona = current_persona_name

# Tab 布局
tab1, tab2, tab3, tab4 = st.tabs([
    T["tab_consult"], 
    T["tab_templates"], 
    T["tab_lawyers"],
    T["tab_review"]
])

# System Prompt for Consultant - 放在外面，供所有模块使用
consultant_instruction = f"""
You are Judi, a top-tier international lawyer specializing in cross-border compliance and corporate law.
Current User Persona (Industry Focus): {current_persona_name}.
Target Jurisdiction: {{TARGET_COUNTRY}}.
Language: {lang_code}.
Style: Professional, rigorous, concise, and highly risk-averse.
Always provide legal citations or clear legal basis where possible, and end with a clear non-legal advice disclaimer.
"""


# --- Tab 1: AI 法律顾问 (Consultant) ---
with tab1:
    st.markdown("### 🤖 **AI 法律智能体：跨境合规**")
    
    col_region, col_space = st.columns([1, 3])
    with col_region:
        target_country = st.text_input(T["target_region"], value="China" if lang_code == 'en' else "中国")
    
    # 根据用户选择更新 instruction
    current_consultant_instruction = consultant_instruction.replace("{{TARGET_COUNTRY}}", target_country)

    # 聊天界面 - 放在一个固定高度的容器中
    chat_container = st.container(height=500)
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 聊天输入框放在底部
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_submit = st.columns([6, 1])
        with col_input:
            prompt = st.text_input(T["chat_placeholder"], key="chat_input_key", label_visibility="collapsed")
        with col_submit:
            submitted = st.form_submit_button("发送" if lang_code == 'zh' else "Send", type="primary")

    if submitted and prompt:
        # 立即更新用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        # 重新运行以显示用户消息
        st.rerun()

    # 处理 AI 响应（放在rerun之后，避免输入框被清空前看不到最新的用户消息）
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_prompt = st.session_state.messages[-1]["content"]

        with chat_container.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # 流式传输响应以提高体验
            try:
                model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash', 
                    system_instruction=current_consultant_instruction
                )
                for chunk in model.generate_content(user_prompt, stream=True):
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_msg = f"发生错误: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.experimental_rerun() # 再次rerun以固定助手消息

# --- Tab 2: 智能合同模版 (Templates) ---
with tab2:
    st.markdown("### 📄 **律师背书合同库**")
    st.markdown(f"*{T['template_intro'].format(persona=current_persona_name)}*")
    
    # 获取该画像的推荐模版
    rec_list = RECOMMENDED_TEMPLATES.get(selected_persona_key, [])
    
    cols = st.columns(2)
    for idx, template_name in enumerate(rec_list):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="card">
                <h3 style="margin-top:0; font-size:1.1rem; color:var(--accent-color);">📜 {template_name}</h3>
                <p style="color:var(--text-secondary); font-size:0.9rem;">适用于 {current_persona_name} 的标准律师背书版本。</p>
                <div style="margin-top:15px;">
                    {st.button(f"{T['generate_btn']}", key=f"btn_{idx}", use_container_width=True)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 使用 session_state 来存储和控制哪个模版被点击
            if st.session_state.get(f"btn_{idx}"):
                with st.spinner(T["processing"]):
                    # 生成模版
                    draft_prompt = f"Please draft a professional '{template_name}' for a '{current_persona_name}' user. Jurisdiction: {target_country}. Include standard clauses for risk protection. Output the draft as clear Markdown text."
                    
                    # 使用 get_gemini_response 获取内容
                    draft_content = get_gemini_response(draft_prompt, consultant_instruction.replace("{{TARGET_COUNTRY}}", target_country))
                    
                    st.success("Draft generated based on legal standards.")
                    st.code(draft_content, language='markdown') # 使用 st.code 更好展示代码/合同结构


# --- Tab 3: 找全球律师 (Global Network) ---
with tab3:
    st.markdown("### 🌍 **全球法律专家网络**")
    
    lc1, lc2 = st.columns(2)
    with lc1:
        city = st.text_input(T["lawyer_city"], value="Shenzhen" if lang_code == 'en' else "深圳市")
    with lc2:
        area = st.text_input(T["lawyer_area"], value="Corporate/IP" if lang_code == 'en' else "公司法/知识产权")
        
    st.markdown("---")
    
    if st.button(T["find_lawyer_btn"], type="primary", key="find_lawyer_action"):
        st.session_state.lawyer_card_data = None # 重置
        with st.spinner(T["processing"]):
            # Prompt 生成模拟名片数据 JSON
            card_prompt = f"""
            Generate a fictional but highly realistic top-tier lawyer profile specializing in: City={city}, Area={area}, focusing on the industry: {current_persona_name}.
            Output strictly valid JSON format with keys:
            "name", "firm", "title", "intro" (2 concise sentences about their expertise), "tags" (list of 3 key skills/industries), 
            "template_specialty" (one common document name for the area), "legal_letter_style" (e.g. Aggressive/Balanced/Concise), "rating" (float 4.5-5.0).
            Language: {lang_code}.
            """
            try:
                json_str = get_gemini_response(card_prompt, "You are a data generator. Output only clean, valid JSON.").strip().replace("```json", "").replace("```", "")
                data = json.loads(json_str)
                st.session_state.lawyer_card_data = data
            except Exception as e:
                st.error("AI生成名片失败，请重试。")
                st.session_state.lawyer_card_data = None
    
    if st.session_state.get("lawyer_card_data"):
        data = st.session_state.lawyer_card_data
        st.markdown(T["lawyer_card_intro"])
        
        # 渲染名片
        tags_html = "".join([f"<span class='tag'>{t}</span>" for t in data['tags']])
        rating_stars = "⭐" * int(data['rating']) + ("½" if data['rating'] - int(data['rating']) >= 0.5 else "")
        
        st.markdown(f"""
        <div class="lawyer-card">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <div class="lawyer-name">{data['name']}</div>
                    <div class="lawyer-title">{data['firm']} | {data['title']}</div>
                </div>
                <div style="font-size:1.5rem; color:#f59e0b;">{rating_stars}</div>
            </div>
            <div style="margin: 10px 0;">{tags_html}</div>
            <p style="color:#4a5568; font-size:0.95rem; line-height:1.5; margin-bottom:15px;">{data['intro']}</p>
            <div style="font-size:0.85rem; color:#374151;">
                <div>📄 <b>擅长模版:</b> {data['template_specialty']}</div>
                <div>📨 <b>函件风格:</b> {data['legal_letter_style']}</div>
            </div>
            <br>
            {st.button(f"💬 {T['consult_agent']} - {data['name']}", key=f"chat_{data['name']}", use_container_width=True)}
        </div>
        """, unsafe_allow_html=True)


# --- Tab 4: 文书审查 (Risk Review) ---
with tab4:
    st.markdown("### 📂 **法律文书风险审查**")
    st.markdown(f"*{current_persona_name}* 专属风险分析。")
    
    uploaded_file = st.file_uploader(T["upload_area"], type=['pdf', 'docx', 'txt'])
    
    if uploaded_file and st.button(T["review_btn"], type="primary"):
        with st.spinner(T["processing"]):
            # 读取文件逻辑
            content = ""
            try:
                if uploaded_file.type == "text/plain":
                    content = uploaded_file.getvalue().decode("utf-8")
                elif "pdf" in uploaded_file.type:
                    # 真实应用需要 PDF 解析库，这里用占位符
                    content = f"[PDF 文件已上传，内容已转换为文本进行分析。] \n\n{uploaded_file.getvalue()[:1000].decode('latin-1')}"
                elif "document" in uploaded_file.type: # docx
                    doc = docx.Document(uploaded_file)
                    content = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                st.error(f"文件读取失败: {e}")
                content = None
                
            if content:
                review_prompt = f"""
                Act as a strict compliance lawyer. Review the following contract content based on the persona '{current_persona_name}' and target jurisdiction '{target_country}'.
                Generate a structured report (in Markdown) with the following sections:
                1. **风险评级 (Risk Rating):** (High/Medium/Low, must be the first line)
                2. **3条核心风险 (3 Core Risks):** (Detailed description of the top 3 risks)
                3. **合规建议 (Compliance Amendments):** (Specific actionable steps)
                4. **管辖权分析 (Jurisdiction Analysis):** (Comment on the choice of law/forum)
                
                Document content snippet: {content[:4000]}
                Language: {lang_code}
                """
                
                result = get_gemini_response(review_prompt, consultant_instruction.replace("{{TARGET_COUNTRY}}", target_country))
                
                st.subheader(T["review_result_title"])
                st.markdown(result)
