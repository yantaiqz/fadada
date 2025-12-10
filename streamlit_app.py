import streamlit as st
import time
import random

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STATE MANAGEMENT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LexiFlow - Global Legal AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'language' not in st.session_state:
    st.session_state.language = '中文'
if 'generated_card' not in st.session_state:
    st.session_state.generated_card = None

# -----------------------------------------------------------------------------
# 2. TRANSLATION & DATA STORE
# -----------------------------------------------------------------------------
TRANS = {
    '中文': {
        'title': "LexiFlow 法律智能体",
        'subtitle': "硅谷极简风格 · 全球法律连接 · AI驱动",
        'sidebar_settings': "设置",
        'lang_select': "语言 / Language",
        'persona_select': "选择您的企业/个人画像",
        'nav_home': "首页概览",
        'nav_templates': "合同模版 (律师背书)",
        'nav_consult': "AI 法律咨询",
        'nav_draft': "AI 文书起草",
        'nav_lawyers': "找全球律师",
        'nav_firms': "找全球律所",
        'personas': ["餐饮/服务业态", "一人公司/自由职业", "出海/跨境电商", "制造业/实体工厂", "大型集团/上市企业"],
        'welcome': "欢迎回来",
        'welcome_desc': "根据您的 **{}** 画像，我们为您定制了以下法律服务。",
        'rec_templates': "推荐模版",
        'ai_consult_title': "全球法律 AI 咨询",
        'select_country': "选择法律管辖国家/地区",
        'input_question': "请输入您的法律问题...",
        'btn_ask': "开始咨询",
        'ai_thinking': "AI 正在分析判例与法条...",
        'draft_title': "智能法律文书起草",
        'draft_type': "选择文书类型",
        'draft_details': "输入关键条款/背景信息",
        'btn_draft': "生成草案",
        'lawyer_city': "输入城市 (默认: 深圳市)",
        'lawyer_find': "查找律师",
        'card_gen': "生成名片",
        'card_title': "律师电子名片",
        'firm_country': "输入国家 (默认: 中国)",
        'firm_find': "查找律所"
    },
    'English': {
        'title': "LexiFlow Legal AI",
        'subtitle': "Silicon Valley Minimalist · Global Connect · AI Driven",
        'sidebar_settings': "Settings",
        'lang_select': "Language",
        'persona_select': "Select User Persona",
        'nav_home': "Dashboard",
        'nav_templates': "Templates (Verified)",
        'nav_consult': "AI Consultation",
        'nav_draft': "AI Drafting",
        'nav_lawyers': "Global Lawyers",
        'nav_firms': "Global Law Firms",
        'personas': ["F&B / Service", "Solopreneur / Freelancer", "Cross-border / Export", "Manufacturing", "Large Enterprise"],
        'welcome': "Welcome Back",
        'welcome_desc': "Based on your **{}** profile, we curated these services.",
        'rec_templates': "Recommended Templates",
        'ai_consult_title': "Global AI Legal Consultation",
        'select_country': "Select Jurisdiction",
        'input_question': "Enter your legal question...",
        'btn_ask': "Start Consultation",
        'ai_thinking': "AI is analyzing precedents and statutes...",
        'draft_title': "AI Document Drafting",
        'draft_type': "Document Type",
        'draft_details': "Key Terms / Background Info",
        'btn_draft': "Generate Draft",
        'lawyer_city': "Enter City (Default: Shenzhen)",
        'lawyer_find': "Find Lawyers",
        'card_gen': "Generate Card",
        'card_title': "Lawyer Digital Card",
        'firm_country': "Enter Country (Default: China)",
        'firm_find': "Find Law Firms"
    }
}

# Persona-based Template Mapping
TEMPLATE_MAP = {
    "餐饮/服务业态": ["食品安全责任书", "商铺租赁合同 (利于承租方)", "员工入职合规包", "特许经营协议"],
    "F&B / Service": ["Food Safety Agreement", "Commercial Lease (Tenant Friendly)", "Employee Handbook", "Franchise Agreement"],
    "一人公司/自由职业": ["独立承包商协议", "保密协议 (NDA)", "知识产权转让协议", "服务费催收函"],
    "Solopreneur / Freelancer": ["Independent Contractor Agreement", "NDA", "IP Assignment Deed", "Payment Demand Letter"],
    "出海/跨境电商": ["GDPR 数据合规声明", "跨境销售条款 (ToS)", "国际物流服务合同", "美国商标注册申请"],
    "Cross-border / Export": ["GDPR Compliance Statement", "Cross-border Terms of Service", "International Logistics Contract", "US Trademark Application"],
    "制造业/实体工厂": ["OEM 代工协议", "供应链采购合同", "安全生产责任书", "设备融资租赁合同"],
    "Manufacturing": ["OEM Agreement", "Supply Chain Purchase Contract", "Safety Liability Agreement", "Equipment Lease"],
    "大型集团/上市企业": ["股权激励计划 (ESOP)", "并购意向书 (LOI)", "合规反腐败政策", "董事会决议模版"],
    "Large Enterprise": ["ESOP Plan", "Letter of Intent (M&A)", "Anti-Corruption Policy", "Board Resolution Template"]
}

# -----------------------------------------------------------------------------
# 3. CUSTOM CSS (SILICON VALLEY MINIMALIST)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Reset & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
        background-color: #ffffff;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Card Component Styling */
    .st-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .st-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.025em;
        color: #111827;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #000000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #374151;
        color: white;
        border: none;
    }
    
    /* Lawyer Card Specifics */
    .lawyer-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 400px;
        margin: 0 auto;
    }
    .lawyer-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #cbd5e1;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        color: white;
    }
    .lawyer-name { font-size: 1.25rem; font-weight: 700; color: #0f172a; }
    .lawyer-title { font-size: 0.875rem; color: #64748b; margin-bottom: 16px; }
    .lawyer-tags span {
        background-color: #e0f2fe;
        color: #0284c7;
        padding: 4px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        margin-right: 4px;
    }
    
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_text(key):
    return TRANS[st.session_state.language][key]

def render_lawyer_card(name, title, firm, specialty, city):
    return f"""
    <div class="lawyer-card">
        <div class="lawyer-avatar">{name[0]}</div>
        <div class="lawyer-name">{name}</div>
        <div class="lawyer-title">{title} | {firm}</div>
        <div class="lawyer-tags" style="margin-bottom: 12px;">
            <span>Verified</span>
            <span>AI-Powered</span>
            <span>{specialty}</span>
        </div>
        <p style="font-size: 0.8rem; color: #475569; text-align: center; margin-bottom: 20px;">
            Based in {city}. Specializing in corporate law and {specialty.lower()}.
            <br>Providing AI-augmented legal services.
        </p>
        <div style="width:100%; border-top: 1px dashed #cbd5e1; margin-bottom:15px;"></div>
        <div style="display:flex; justify-content:space-between; width:100%; font-size:0.75rem; color:#94a3b8;">
            <span>ID: #L88392</span>
            <span>LexiFlow Certified</span>
        </div>
    </div>
    """

# -----------------------------------------------------------------------------
# 5. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {get_text('sidebar_settings')}")
    
    # Language Toggle
    lang_choice = st.radio(
        get_text('lang_select'), 
        ['中文', 'English'], 
        index=0 if st.session_state.language == '中文' else 1
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

    st.markdown("---")
    
    # Persona Selection
    st.markdown(f"### {get_text('persona_select')}")
    selected_persona_index = 0
    persona = st.selectbox(
        "Persona", 
        get_text('personas'),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Navigation
    nav_options = [
        get_text('nav_home'),
        get_text('nav_templates'),
        get_text('nav_consult'),
        get_text('nav_draft'),
        get_text('nav_lawyers'),
        get_text('nav_firms')
    ]
    selection = st.radio("Navigation", nav_options, label_visibility="collapsed")

# -----------------------------------------------------------------------------
# 6. MAIN CONTENT
# -----------------------------------------------------------------------------

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(get_text('title'))
    st.caption(get_text('subtitle'))
with col2:
    # Just visual balance
    pass

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# --- HOME DASHBOARD ---
if selection == get_text('nav_home'):
    st.subheader(f"{get_text('welcome')} 👋")
    st.info(get_text('welcome_desc').format(persona))
    
    # Dashboard Grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="st-card">
            <h4>📄 {get_text('nav_templates')}</h4>
            <p style="color:#666; font-size:0.9rem">Access verified contracts tailored for {persona}.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="st-card">
            <h4>🤖 {get_text('nav_consult')}</h4>
            <p style="color:#666; font-size:0.9rem">24/7 AI legal advice across multiple jurisdictions.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="st-card">
            <h4>🌍 {get_text('nav_lawyers')}</h4>
            <p style="color:#666; font-size:0.9rem">Connect with experts in Shenzhen, New York, London...</p>
        </div>
        """, unsafe_allow_html=True)

# --- CONTRACT TEMPLATES ---
elif selection == get_text('nav_templates'):
    st.subheader(get_text('rec_templates'))
    st.markdown("Logic: *Lawyer verified templates based on your selected industry persona.*")
    
    templates = TEMPLATE_MAP.get(persona, [])
    
    for temp in templates:
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**📄 {temp}**")
                st.caption("Updated: 2023-10 | Verified by: King & Wood Mallesons (Mock)")
            with c2:
                st.button("Download", key=temp)
            st.divider()

# --- AI CONSULTATION ---
elif selection == get_text('nav_consult'):
    st.subheader(get_text('ai_consult_title'))
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        country = st.selectbox(get_text('select_country'), ["China", "USA", "Singapore", "UK", "Japan", "EU"])
    
    user_input = st.text_area(get_text('input_question'), height=150)
    
    if st.button(get_text('btn_ask')):
        if not user_input:
            st.warning("Please enter a question.")
        else:
            with st.spinner(get_text('ai_thinking')):
                time.sleep(1.5) # Simulate API latency
                st.markdown("### AI Analysis:")
                
                # Mock AI Response
                response_text = ""
                if st.session_state.language == '中文':
                    response_text = f"基于**{country}**的法律框架，针对您的问题：\n\n1. **适用法律**: 根据{country}合同法及相关判例...\n2. **风险提示**: 您需要注意条款中的免责声明...\n3. **建议行动**: 建议在起诉前先发送律师函..."
                else:
                    response_text = f"Based on **{country}** legal framework regarding your query:\n\n1. **Applicable Law**: According to {country} Contract Law and relevant precedents...\n2. **Risk Warning**: Pay attention to the liability exemption clauses...\n3. **Recommended Action**: It is advisable to send a Cease & Desist letter before litigation..."
                
                placeholder = st.empty()
                streamed_text = ""
                for char in response_text:
                    streamed_text += char
                    placeholder.markdown(streamed_text)
                    time.sleep(0.01)

# --- AI DRAFTING ---
elif selection == get_text('nav_draft'):
    st.subheader(get_text('draft_title'))
    
    doc_type = st.selectbox(get_text('draft_type'), ["NDA (保密协议)", "Employment Contract (雇佣合同)", "Service Agreement (服务协议)", "Cease & Desist (律师函)"])
    details = st.text_area(get_text('draft_details'), height=100)
    
    if st.button(get_text('btn_draft')):
        with st.spinner("Drafting..."):
            time.sleep(2)
            st.success("Draft Generated Successfully!")
            st.code(f"""
            [DRAFT - {doc_type.upper()}]
            
            THIS AGREEMENT is made on {time.strftime("%Y-%m-%d")}...
            
            BETWEEN:
            [Party A] AND [Party B]
            
            WHEREAS:
            {details if details else "[Insert Background Information Here]"}
            
            1. DEFINITIONS
            ...
            
            2. CONFIDENTIALITY
            ...
            
            (Signed by AI Legal Agent)
            """, language='markdown')

# --- FIND LAWYERS ---
elif selection == get_text('nav_lawyers'):
    st.subheader(get_text('lawyer_find'))
    
    l_col1, l_col2 = st.columns([3, 1])
    with l_col1:
        # Default City: Shenzhen
        city = st.text_input(get_text('lawyer_city'), value="Shenzhen" if st.session_state.language != '中文' else "深圳市")
    with l_col2:
        st.write("")
        st.write("") # Spacing
        search_btn = st.button("Search")
        
    st.markdown("---")
    
    # Mock Lawyers Data
    mock_lawyers = [
        {"name": "Alice Chen", "title": "Senior Partner", "firm": "Global Law Network", "specialty": "IP & Tech", "city": city},
        {"name": "David Wang", "title": "Associate", "firm": "Shenzhen Legal Hub", "specialty": "Corporate", "city": city},
        {"name": "Sarah Smith", "title": "Legal Counsel", "firm": "Cross-Border Solutions", "specialty": "International Trade", "city": city}
    ]
    
    # Display Results
    for idx, lawyer in enumerate(mock_lawyers):
        with st.container():
            c1, c2, c3 = st.columns([1, 4, 2])
            with c1:
                st.markdown(f"<div style='width:50px; height:50px; background:#eee; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>{lawyer['name'][0]}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{lawyer['name']}**")
                st.caption(f"{lawyer['title']} @ {lawyer['firm']}")
                st.caption(f"📍 {lawyer['city']} | 🏷️ {lawyer['specialty']}")
            with c3:
                # Generate Card Button logic
                if st.button(get_text('card_gen'), key=f"btn_card_{idx}"):
                    st.session_state.generated_card = lawyer
            st.divider()

    # Modal/Expander for Business Card
    if st.session_state.generated_card:
        st.markdown(f"### {get_text('card_title')}")
        card_html = render_lawyer_card(
            st.session_state.generated_card['name'],
            st.session_state.generated_card['title'],
            st.session_state.generated_card['firm'],
            st.session_state.generated_card['specialty'],
            st.session_state.generated_card['city']
        )
        st.markdown(card_html, unsafe_allow_html=True)
        
        c_act1, c_act2 = st.columns(2)
        with c_act1:
            st.button("📥 Save to Contacts (vCard)", key="dl_card")
        with c_act2:
            st.button("💬 Chat with AI Agent", key="chat_agent")

# --- FIND LAW FIRMS ---
elif selection == get_text('nav_firms'):
    st.subheader(get_text('firm_find'))
    
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        # Default Country: China
        country_firm = st.text_input(get_text('firm_country'), value="China" if st.session_state.language != '中文' else "中国")
    
    st.markdown("### Top Ranked Firms")
    
    firms = [
        "King & Wood Mallesons (金杜律师事务所)",
        "Zhong Lun Law Firm (中伦律师事务所)",
        "JunHe LLP (君合律师事务所)",
        "Dentons (大成)"
    ]
    
    for f in firms:
        st.markdown(f"""
        <div class="st-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-weight:bold; font-size:1.1rem;">{f}</span><br>
                <span style="color:#666; font-size:0.85rem;">Headquarters: {country_firm} | Rating: ⭐⭐⭐⭐⭐</span>
            </div>
            <button style="background:transparent; border:1px solid #ddd; padding:5px 10px; border-radius:4px; cursor:pointer;">View Profile</button>
        </div>
        """, unsafe_allow_html=True)
