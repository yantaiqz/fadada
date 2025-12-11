import streamlit as st
import google.generativeai as genai
import json
import os

# -------------------------------------------------------------
# --- 1. 配置与基础数据定义 ---
# -------------------------------------------------------------
st.set_page_config(
    page_title="iTerms | Legal Workspace", 
    page_icon="⚖️", 
    layout="wide",
    # 核心设置：初始化为展开状态
    initial_sidebar_state="expanded" 
)

# 语言选项
LANG_OPTIONS = {
    "🇨🇳 中文": "zh",
    "🇺🇸 English": "en"
}

# 20个主要国家列表
COUNTRY_LIST = [
    "🇨🇳 China (中国)", "🇺🇸 United States (美国)", "🇬🇧 United Kingdom (英国)", 
    "🇩🇪 Germany (德国)", "🇫🇷 France (法国)", "🇯🇵 Japan (日本)", 
    "🇰🇷 South Korea (韩国)", "🇸🇬 Singapore (新加坡)", "🇦🇺 Australia (澳大利亚)", 
    "🇨🇦 Canada (加拿大)", "🇮🇳 India (印度)", "🇧🇷 Brazil (巴西)", 
    "🇦🇪 UAE (阿联酋)", "🇸🇦 Saudi Arabia (沙特)", "🇻🇳 Vietnam (越南)", 
    "🇹🇭 Thailand (泰国)", "🇮🇩 Indonesia (印尼)", "🇲🇾 Malaysia (马来西亚)", 
    "🇲🇽 Mexico (墨西哥)", "🇿🇦 South Africa (南非)"
]

# 用户画像定义
USER_PERSONAS = {
    "zh": {
        "lawyer": "👨‍⚖️ 律师/法律从业者", 
        "catering": "🍽️ 餐饮业主",
        "service": "💆 服务业经营者",
        "solo": "💻 独立开发者/自由职业者",
        "overseas": "🚢 出海企业主",
        "manufacturing": "🏭 制造业经理",
        "group": "🏢 集团法务"
    },
    "en": {
        "lawyer": "👨‍⚖️ Lawyer / Legal Practitioner",
        "catering": "🍽️ Restaurant Owner",
        "service": "💆 Service Provider",
        "solo": "💻 Indie Hacker / Freelancer",
        "overseas": "🚢 Cross-border Founder",
        "manufacturing": "🏭 Manufacturing Manager",
        "group": "🏢 Corporate Counsel"
    }
}

# 法律文书库
RECOMMENDED_TEMPLATES = {
    "lawyer": [ 
        "法律服务聘用合同 (Retainer)", "利益冲突豁免函", "律师函 (Cease & Desist)", 
        "法律尽职调查清单 (DD List)", "客户保密协议 (Attorney-Client NDA)", "诉讼保全申请书", 
        "取证授权委托书", "法律意见书模版", "和解协议书", "风险代理收费协议"
    ],
    "catering": [
        "店铺租赁合同", "食品安全管理制度", "员工雇佣/劳务合同", "特许经营(加盟)协议", 
        "原材料采购长期供货协议", "装修工程施工合同", "外卖平台入驻协议", "消防安全责任书", 
        "顾客人身损害赔偿免责条款", "废弃油脂处理协议"
    ],
    "service": [
        "服务等级协议 (SLA)", "用户隐私政策 (Privacy Policy)", "会员服务/充值协议", "兼职人员劳务合同", 
        "场所租赁协议", "设备维护保养合同", "客户肖像权授权书", "预付款退款规则声明", 
        "合作推广协议", "知识产权归属声明"
    ],
    "solo": [
        "软件开发外包合同", "源代码知识产权转让协议", "网站免责声明 (Disclaimer)", "独立顾问咨询协议", 
        "SaaS 用户服务协议 (ToS)", "保密协议 (NDA)", "数据处理协议 (DPA)", "开源软件许可声明", 
        "远程工作合规声明", "股权/期权分配协议 (Co-founder)"
    ],
    "overseas": [
        "跨境数据传输条款 (SCCs)", "海外独家代理/分销协议", "GDPR 合规隐私声明", "国际货物销售合同 (CISG)", 
        "海外公司章程 (AoA)", "反洗钱 (AML) 合规声明", "出口管制合规承诺书", "跨境电商平台服务协议", 
        "国际劳务派遣合同", "海外商标授权协议"
    ],
    "manufacturing": [
        "OEM 委托加工合同", "原材料采购框架协议", "安全生产责任书", "供应链保密协议 (NDA)", 
        "产品质量保证协议", "设备融资租赁合同", "仓储物流运输合同", "技术秘密许可协议", 
        "工厂厂房租赁合同", "劳务外包协议"
    ],
    "group": [
        "员工期权激励计划 (ESOP)", "中外合资经营合同 (JV)", "集团合规管理章程", "高管聘用与竞业限制协议", 
        "公司并购意向书 (LOI)", "股东协议 (SHA)", "关联交易管理制度", "反商业贿赂声明", 
        "企业上市辅导协议", "重大资产重组协议"
    ]
}

# 翻译字典
TRANSLATIONS = {
    "zh": {
        "tab_templates": "法律文书库", 
        "tab_consult": "咨询顾问", 
        "tab_lawyers": "寻找专家", 
        "tab_review": "文书审查", 
        "start_post": "开始咨询...",
        "connect_btn": "建立联系",
        "chat_placeholder": "在此输入法律问题，例如：当地设立分公司的最低资本要求...",
        "target_region_label": "选择目标国家/管辖区",
        "generate_btn": "AI 起草文书",
        "processing": "AI 正在生成中...",
        "lawyer_card_title": "法律专家与服务网络",
        "upload_text": "上传法律文件进行审查 (PDF/Docx)",
        "sidebar_headline": "高级法律会员",
        "sec_lawyers": "推荐律师",
        "sec_firms": "知名律所",
        "sec_courts": "司法/仲裁机构",
        "sec_agencies": "合规/财税/注册机构",
        "toggle_sidebar": "展开/收起侧边栏" 
    },
    "en": {
        "tab_templates": "Legal Documents",
        "tab_consult": "Consultant",
        "tab_lawyers": "Expert Network",
        "tab_review": "Doc Review",
        "start_post": "Start a consultation...",
        "connect_btn": "Connect",
        "chat_placeholder": "Ask a legal question...",
        "target_region_label": "Target Jurisdiction",
        "generate_btn": "Draft Document",
        "processing": "Processing...",
        "lawyer_card_title": "Legal Experts & Service Network",
        "upload_text": "Upload for Review (PDF/Docx)",
        "sidebar_headline": "Premium Legal Member",
        "sec_lawyers": "Recommended Lawyers",
        "sec_firms": "Top Law Firms",
        "sec_courts": "Judicial & Arbitration",
        "sec_agencies": "Compliance & Agencies",
        "toggle_sidebar": "Toggle Sidebar" 
    }
}

# -------------------------------------------------------------
# --- 2. CSS 样式 (核心修复：禁止侧边栏折叠) ---
# -------------------------------------------------------------
st.markdown("""
<style>
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

    .stApp {
        background-color: var(--bg-color) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: var(--text-dark);
    }
    
    /* ================================================================= */
    /* === 核心修复：禁止侧边栏折叠 (Force Sidebar Expanded) === */
    /* ================================================================= */
    
    /* 1. 隐藏侧边栏内部右上角的关闭按钮 (X 或 <) */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. 隐藏主界面左上角的展开按钮 (>) - 以防万一它处于折叠状态 */
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 3. 隐藏Header decoration，防止干扰 */
    header[data-testid="stHeader"] {
        background: transparent;
        z-index: 1; 
    }
    
    /* ================================================================= */

    /* 仅隐藏工具栏的Deploy/Setting */
    [data-testid="stToolbar"] > div:not([data-testid="stSidebarNav"]) {
        visibility: hidden;
    }

    /* 侧边栏样式微调 */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: 1px solid #ddd; /* 加上边框让分隔更明显 */
        padding-top: 1rem !important;
    }

    /* 卡片通用样式 */
    .li-card {
        background: var(--card-bg);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.04);
    }

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

    /* Tabs */
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

    /* 按钮 */
    .stButton > button {
        background-color: var(--linkedin-blue) !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
    }
    .stButton > button:hover {
        background-color: var(--linkedin-blue-hover) !important;
    }

    /* 专家列表样式 */
    .expert-row {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }
    .expert-row:last-child { border-bottom: none; }
    .expert-icon {
        width: 48px;
        height: 48px;
        background: #eef3f8;
        border-radius: 50%; 
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-right: 12px;
    }
    .expert-icon.square {
        border-radius: 8px; 
    }
    .expert-info h4 { margin: 0; font-size: 1rem; color: #191919; font-weight: 600; }
    .expert-info p { margin: 2px 0; font-size: 0.85rem; color: #666; }
    
    /* 分区标题 */
    .section-header {
        font-size: 1rem;
        font-weight: 700;
        color: #191919;
        margin-top: 20px;
        margin-bottom: 10px;
        padding-left: 5px;
        border-left: 4px solid var(--linkedin-blue);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# --- 3. 移除不需要的侧边栏切换逻辑 ---
# -------------------------------------------------------------
# 原有的 toggle_sidebar 函数和 session_state 逻辑已移除，
# 因为我们通过 CSS 强制侧边栏始终显示且不可折叠。

# -------------------------------------------------------------
# --- 4. API 与 逻辑 ---
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, system_instruction):
    if not api_key:
        return "⚠️ API Key Missing."
    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=system_instruction)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# 模拟专家数据生成函数
def get_mock_experts(country):
    loc = country.split(" ")[0]
    return {
        "lawyers": [
            {"name": f"Alice Wang ({loc})", "title": "Corporate Partner", "firm": "Global Law LLP"},
            {"name": f"John Smith ({loc})", "title": "Senior Counsel", "firm": "Smith & Associates"},
            {"name": f"Maria Garcia ({loc})", "title": "IP Specialist", "firm": "Tech Legal Group"},
            {"name": f"David Kim ({loc})", "title": "Labor Law Expert", "firm": "Workforce Legal"}
        ],
        "firms": [
            {"name": f"King & Wood ({loc} Office)", "type": "Full Service"},
            {"name": f"Dentons {loc}", "type": "Global Network"},
            {"name": f"Clifford Chance {loc}", "type": "Corporate/Finance"},
            {"name": f"Baker McKenzie {loc}", "type": "Cross-border"}
        ],
        "institutions": [
            {"name": f"Supreme Court of {loc}", "type": "Judicial Body"},
            {"name": f"{loc} Arbitration Commission", "type": "Arbitration"},
            {"name": f"{loc} IP Court", "type": "Specialized Court"},
            {"name": f"Ministry of Justice ({loc})", "type": "Government"}
        ],
        "agencies": [
            {"name": f"{loc} Tax Solutions", "type": "Tax & Accounting"},
            {"name": f"Visa & Immigration {loc}", "type": "Immigration Services"},
            {"name": f"{loc} Corporate Registry", "type": "Registration Agent"},
            {"name": f"Compliance First {loc}", "type": "Risk Management"}
        ]
    }

# -------------------------------------------------------------
# --- 5. 页面逻辑开始 (移除手动切换按钮) ---
# -------------------------------------------------------------
# 既然侧边栏禁止折叠，主界面的切换按钮也不再需要。

# -------------------------------------------------------------
# --- 6. 侧边栏 ---
# -------------------------------------------------------------
with st.sidebar:
    # 保存语言选择到session_state
    lang_choice = st.selectbox("Language / 语言", list(LANG_OPTIONS.keys()), key="lang_choice")
    lang_code = LANG_OPTIONS[lang_choice]
    T = TRANSLATIONS[lang_code]
    
    st.markdown("---")
    
    persona_options = USER_PERSONAS[lang_code]
    selected_persona_key = st.selectbox(
        "Identity / 身份", 
        options=list(persona_options.keys()),
        format_func=lambda x: persona_options[x]
    )
    current_persona_name = persona_options[selected_persona_key]

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
# --- 7. 主界面 Workspace ---
# -------------------------------------------------------------
if "messages" not in st.session_state or st.session_state.get("current_persona") != current_persona_name:
    st.session_state.messages = []
    st.session_state.current_persona = current_persona_name

consultant_instruction = f"""
Role: Professional Legal Consultant named Judi on a professional network platform.
User: {current_persona_name}.
Style: LinkedIn professional, concise, authoritative.
"""

tab_templates, tab_consult, tab_lawyers, tab_review = st.tabs([
    f"📄 {T['tab_templates']}", 
    f"💬 {T['tab_consult']}", 
    f"👥 {T['tab_lawyers']}",
    f"🛡️ {T['tab_review']}"
])

# --- Tab 1: 法律文书库 ---
with tab_templates:
    st.markdown(f"### {T['tab_templates']}")
    rec_list = RECOMMENDED_TEMPLATES.get(selected_persona_key, [])
    
    cols = st.columns(2)
    for idx, template_name in enumerate(rec_list):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div class="li-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <div style="width:40px; height:40px; background:#eef3f8; display:flex; align-items:center; justify-content:center; border-radius:4px;">
                            📄
                        </div>
                        <div style="font-size:0.8rem; color:#666; background:#f3f2ef; padding:2px 8px; border-radius:10px; height:fit-content;">
                            DOCX
                        </div>
                    </div>
                    <div style="font-weight:600; font-size:1.05rem; color:var(--linkedin-blue); height: 40px; overflow:hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                        {template_name}
                    </div>
                    <div style="font-size:0.85rem; color:#666; margin-top:10px;">
                         Verified • {current_persona_name}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(T['generate_btn'], key=f"tpl_{idx}", use_container_width=True):
                    st.success(f"Drafting {template_name}...")

# --- Tab 2: 咨询顾问 ---
with tab_consult:
    st.markdown(f"""
    <div class="li-card" style="display:flex; align-items:center;">
        <div style="width:40px; height:40px; border-radius:50%; background:#eee; margin-right:15px; display:flex; align-items:center; justify-content:center;">👨‍💼</div>
        <div style="color:#666; font-weight:500;">
           {T['start_post']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_country = st.selectbox(T["target_region_label"], COUNTRY_LIST, index=0)
    
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

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder=T["chat_placeholder"], label_visibility="collapsed")
        col_actions = st.columns([6, 1])
        with col_actions[1]:
            submitted = st.form_submit_button("Send ✈️")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner(T["processing"]):
            full_instruction = consultant_instruction + f" Target Jurisdiction: {selected_country}."
            ai_reply = get_gemini_response(user_input, full_instruction)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()

# --- Tab 3: 寻找专家 ---
with tab_lawyers:
    st.markdown(f"""
    <div class="li-card">
        <h3>{T['lawyer_card_title']}</h3>
        <p style="color:#666; font-size:0.9rem;">Verified network for: <b>{current_persona_name}</b></p>
    </div>
    """, unsafe_allow_html=True)

    expert_country = st.selectbox(f"{T['target_region_label']} (Experts)", COUNTRY_LIST, index=0, key="expert_country")
    mock_data = get_mock_experts(expert_country)
    
    def render_expert_section(title, items, icon, is_square=False):
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, item in enumerate(items):
            with cols[i % 2]:
                border_radius = "8px" if is_square else "50%"
                st.markdown(f"""
                <div class="li-card expert-row" style="margin-bottom:10px; padding:12px;">
                    <div class="expert-icon" style="border-radius:{border_radius};">
                        {icon}
                    </div>
                    <div class="expert-info">
                        <h4>{item['name']}</h4>
                        <p>{item.get('title', item.get('type'))}</p>
                        <p style="font-size:0.8rem; color:#666;">{item.get('firm', '')}</p>
                    </div>
                    <div style="flex-grow:1; text-align:right;">
                         <button style="border:1px solid #0a66c2; color:#0a66c2; background:white; border-radius:15px; padding:2px 12px; font-weight:600; cursor:pointer;">+</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    render_expert_section(T['sec_lawyers'], mock_data['lawyers'], "⚖️")
    render_expert_section(T['sec_firms'], mock_data['firms'], "🏢", is_square=True)
    render_expert_section(T['sec_courts'], mock_data['institutions'], "🏛️", is_square=True)
    render_expert_section(T['sec_agencies'], mock_data['agencies'], "💼", is_square=True)

# --- Tab 4: 文书审查 ---
with tab_review:
    st.markdown(f"""
    <div class="li-card" style="text-align:center; padding:60px 20px;">
        <div style="font-size:48px; margin-bottom:20px; color:var(--linkedin-blue);">🛡️</div>
        <h3 style="color:#191919;">{T['upload_text']}</h3>
        <p style="color:#666; margin-bottom:30px; max-width:500px; margin-left:auto; margin-right:auto;">
            Secure AI analysis for {current_persona_name}.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.file_uploader("", label_visibility="collapsed")
