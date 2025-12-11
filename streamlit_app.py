import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
import time

# -------------------------------------------------------------
# --- 1. 配置与基础数据定义 ---
# -------------------------------------------------------------
st.set_page_config(
    page_title="iTerms | Global Legal Workspace", 
    page_icon="⚖️", 
    layout="wide",
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

# 用户画像定义 (保留4个)
USER_PERSONAS = {
    "zh": {
        "lawyer": "👨‍⚖️ 律师/法律从业者", 
        "group": "🏢 集团法务",
        "overseas": "🚢 出海企业主",
        "solo": "💻 个人/独立开发者"
    },
    "en": {
        "lawyer": "👨‍⚖️ Lawyer / Legal Practitioner",
        "group": "🏢 Corporate Counsel",
        "overseas": "🚢 Cross-border Founder",
        "solo": "💻 Individual / Indie Hacker"
    }
}

# 法律文书库 (针对4个身份优化)
RECOMMENDED_TEMPLATES = {
    "lawyer": [ 
        "法律服务聘用合同 (Retainer)", "利益冲突豁免函", "律师函 (Cease & Desist)", 
        "法律尽职调查清单 (DD List)", "客户保密协议 (Attorney-Client NDA)", "诉讼保全申请书", 
        "取证授权委托书", "法律意见书模版", "和解协议书", "风险代理收费协议"
    ],
    "group": [
        "员工期权激励计划 (ESOP)", "中外合资经营合同 (JV)", "集团合规管理章程", "高管聘用与竞业限制协议", 
        "公司并购意向书 (LOI)", "股东协议 (SHA)", "关联交易管理制度", "反商业贿赂声明", 
        "企业上市辅导协议", "重大资产重组协议"
    ],
    "overseas": [
        "跨境数据传输条款 (SCCs)", "海外独家代理/分销协议", "GDPR 合规隐私声明", "国际货物销售合同 (CISG)", 
        "海外公司章程 (AoA)", "反洗钱 (AML) 合规声明", "出口管制合规承诺书", "跨境电商平台服务协议", 
        "国际劳务派遣合同", "海外商标授权协议"
    ],
    "solo": [
        "软件开发外包合同", "源代码知识产权转让协议", "网站免责声明 (Disclaimer)", "独立顾问咨询协议", 
        "SaaS 用户服务协议 (ToS)", "保密协议 (NDA)", "数据处理协议 (DPA)", "开源软件许可声明", 
        "远程工作合规声明", "股权/期权分配协议 (Co-founder)"
    ]
}

# 模拟合规资讯流数据
MOCK_NEWS_FEED = [
    {
        "author": "Global Compliance Daily",
        "avatar": "🌐",
        "time": "2h • Edited",
        "content": "🇪🇺 **EU AI Act Update**: The European Parliament has reached a provisional agreement. Companies deploying high-risk AI systems must now conduct fundamental rights impact assessments. #AICompliance #GDPR #TechLaw",
        "likes": 428, "comments": 34
    },
    {
        "author": "Trade Law Insight",
        "avatar": "⚖️",
        "time": "5h",
        "content": "🇺🇸🇨🇳 **New Export Controls**: Key takeaways from the latest BIS ruling regarding semiconductor exports. Check the attached PDF for a summary of impacted HS codes. #ExportControl #InternationalTrade",
        "likes": 156, "comments": 12
    },
    {
        "author": "Singapore Legal Tech",
        "avatar": "🦁",
        "time": "1d",
        "content": "🇸🇬 Singapore's new framework for **Digital Token Payment Services** is live. Crypto exchanges looking to operate in SEA need to review their AML protocols immediately.",
        "likes": 892, "comments": 105
    }
]

# 翻译字典
TRANSLATIONS = {
    "zh": {
        "tab_news": "跨境合规资讯",
        "tab_consult": "全球法律咨询 (域外法查明)",
        "tab_lawyers": "海外律师",
        "tab_review": "涉外合同审查",
        "tab_templates": "文书模版与智能起草",
        
        "start_post": "发布合规动态或提问...",
        "start_consult": "输入法律问题，开启域外法查明...",
        "connect_btn": "建立联系",
        "chat_placeholder": "例如：德国《供应链尽职调查法》对中国供应商有什么具体要求？",
        "target_region_label": "选择目标国家/管辖区",
        "generate_btn": "AI 起草文书",
        "processing": "AI 正在生成中...",
        "lawyer_card_title": "全球法律专家网络",
        "upload_text": "上传涉外合同进行审查 (PDF/Docx)",
        "sidebar_headline": "高级法律会员",
        "sec_lawyers": "推荐律师",
        "sec_firms": "知名律所",
        "sec_courts": "司法/仲裁机构",
        "sec_agencies": "合规/财税/注册机构",
        "map_title": "全球法律资源分布图"
    },
    "en": {
        "tab_news": "Compliance News",
        "tab_consult": "Global Consultation",
        "tab_lawyers": "Overseas Lawyers",
        "tab_review": "Contract Review",
        "tab_templates": "Templates & Drafting",
        
        "start_post": "Start a post...",
        "start_consult": "Ask a question for foreign law ascertainment...",
        "connect_btn": "Connect",
        "chat_placeholder": "E.g., What are the capital requirements for a GmbH in Germany?",
        "target_region_label": "Target Jurisdiction",
        "generate_btn": "Draft Document",
        "processing": "Processing...",
        "lawyer_card_title": "Global Legal Expert Network",
        "upload_text": "Upload Contract for Review (PDF/Docx)",
        "sidebar_headline": "Premium Legal Member",
        "sec_lawyers": "Recommended Lawyers",
        "sec_firms": "Top Law Firms",
        "sec_courts": "Judicial & Arbitration",
        "sec_agencies": "Compliance & Agencies",
        "map_title": "Global Legal Resource Map"
    }
}

# -------------------------------------------------------------
# --- 2. CSS 样式 ---
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
    
    /* 核心修复：禁止侧边栏折叠 */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent; z-index: 1; }
    [data-testid="stToolbar"] > div:not([data-testid="stSidebarNav"]) { visibility: hidden; }
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: 1px solid #ddd;
        padding-top: 1rem !important;
    }

    /* 卡片通用样式 */
    .li-card {
        background: var(--card-bg);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        padding: 12px 16px; /* 稍微紧凑一点 */
        margin-bottom: 12px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.04);
    }

    /* 个人资料卡 */
    .profile-bg {
        background: #a0b4b7;
        height: 60px;
        border-radius: var(--radius) var(--radius) 0 0;
        margin: -12px -16px 0 -16px;
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

    /* Tabs 优化 */
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

    /* Feed 交互按钮 (Like/Comment) */
    .feed-action-btn {
        display: flex;
        align-items: center;
        padding: 10px 8px;
        border-radius: 4px;
        cursor: pointer;
        color: #666;
        font-weight: 600;
        font-size: 0.9rem;
        background: transparent;
        border: none;
        margin-right: 5px;
    }
    .feed-action-btn:hover { background-color: #f3f2ef; }

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
    .expert-icon.square { border-radius: 8px; }
    
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
# --- 3. API 与 逻辑 ---
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, system_instruction):
    if not api_key:
        return "⚠️ API Key Missing."
    model = genai.GenerativeModel(model_name='gemini-2.0-flash', system_instruction=system_instruction)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

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
# --- 4. 侧边栏 ---
# -------------------------------------------------------------
with st.sidebar:
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
            <div style="margin-top:10px; font-size:0.8rem; color:#666;">
                <b>1.2k</b> followers &nbsp;•&nbsp; <b>500+</b> connections
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="li-card" style="font-size:0.85rem;">
        <div style="font-weight:600; margin-bottom:8px;">Recent</div>
        <div style="color:#666; margin-bottom:4px;"># cross_border_compliance</div>
        <div style="color:#666; margin-bottom:4px;"># international_trade</div>
        <div style="color:#666; margin-bottom:4px;">⚖️ Global Legal Tech</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# --- 5. 主界面 Workspace ---
# -------------------------------------------------------------
if "messages" not in st.session_state or st.session_state.get("current_persona") != current_persona_name:
    st.session_state.messages = []
    st.session_state.current_persona = current_persona_name

consultant_instruction = f"""
Role: Professional International Legal Consultant named Judi.
User: {current_persona_name}.
Task: Foreign Law Ascertainment and Cross-border Advice.
Style: Professional, rigorous, concise (LinkedIn Article style).
"""

# Tabs 布局：5个模块
tab_news, tab_consult, tab_lawyers, tab_review, tab_templates = st.tabs([
    f"📰 {T['tab_news']}", 
    f"💬 {T['tab_consult']}", 
    f"🌍 {T['tab_lawyers']}",
    f"🛡️ {T['tab_review']}",
    f"📄 {T['tab_templates']}"
])

# --- Tab 1: 跨境合规资讯 (LinkedIn Feed Style) ---
with tab_news:
    # 顶部发布框
    st.markdown(f"""
    <div class="li-card" style="display:flex; align-items:center;">
        <div style="width:48px; height:48px; border-radius:50%; background:#eee; margin-right:15px; display:flex; align-items:center; justify-content:center; font-size:24px;">👨‍💼</div>
        <div style="flex-grow:1; border:1px solid #ccc; border-radius:30px; padding:12px 20px; color:#666; font-weight:600; cursor:pointer; background:white;">
            {T['start_post']}
        </div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding:0 5px;">
        <div style="border-top:1px solid #ccc; flex-grow:1; margin-right:10px;"></div>
        <div style="font-size:0.8rem; color:#666;">Sort by: <b>Top</b></div>
    </div>
    """, unsafe_allow_html=True)

    # 渲染模拟信息流
    for news in MOCK_NEWS_FEED:
        st.markdown(f"""
        <div class="li-card">
            <div style="display:flex; margin-bottom:10px;">
                <div style="width:48px; height:48px; background:#f3f2ef; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:24px; margin-right:10px;">
                    {news['avatar']}
                </div>
                <div>
                    <div style="font-weight:600; color:#191919;">{news['author']}</div>
                    <div style="font-size:0.8rem; color:#666;">{news['time']} • 🌐</div>
                </div>
                <div style="margin-left:auto; color:#666;">...</div>
            </div>
            <div style="font-size:0.95rem; color:#191919; line-height:1.5; margin-bottom:10px;">
                {news['content']}
            </div>
            <div style="font-size:0.8rem; color:#666; margin-bottom:10px;">
                👍 {news['likes']} • {news['comments']} comments
            </div>
            <hr style="border:0; border-top:1px solid #eee; margin:0 0 5px 0;">
            <div style="display:flex; justify-content:space-around;">
                <button class="feed-action-btn">👍 Like</button>
                <button class="feed-action-btn">💬 Comment</button>
                <button class="feed-action-btn">↗️ Share</button>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- Tab 2: 全球法律咨询 (域外法查明) ---
with tab_consult:
    st.markdown(f"""
    <div class="li-card" style="display:flex; align-items:center;">
        <div style="width:40px; height:40px; border-radius:50%; background:#eee; margin-right:15px; display:flex; align-items:center; justify-content:center;">⚖️</div>
        <div style="color:#666; font-weight:500;">
           {T['start_consult']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_country = st.selectbox(T["target_region_label"], COUNTRY_LIST, index=0)
    
    # 聊天记录
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👨‍💼"
        bg_color = "#f3f6f8" if msg["role"] == "assistant" else "#ffffff"
        st.markdown(f"""
        <div class="li-card" style="display:flex; flex-direction:row; gap:16px; background:{bg_color}; border:none;">
            <div style="font-size:28px;">{avatar}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:700; font-size:0.9rem; margin-bottom:4px; color:#191919;">
                    {'Judi (Global Legal Partner)' if msg['role']=='assistant' else 'You'}
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
            full_instruction = consultant_instruction + f" Target Jurisdiction: {selected_country}. Focus on Foreign Law Ascertainment."
            ai_reply = get_gemini_response(user_input, full_instruction)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()


# --- Tab 3: 海外律师 (Top World Map) ---
with tab_lawyers:
    # 1. 世界地图可视化 (使用 Streamlit Map)
    st.markdown(f"### 🗺️ {T['map_title']}")
    
    # 生成随机地图点模拟全球法律资源
    map_data = pd.DataFrame(
        np.random.randn(50, 2) / [2, 2] + [37.76, -122.4], # 简单的占位数据，实际应为真实坐标
        columns=['lat', 'lon'])
    # 添加几个主要城市的硬编码坐标以增加真实感
    major_hubs = pd.DataFrame({
        'lat': [40.7128, 51.5074, 35.6895, 1.3521, 22.3193, 48.8566], # NY, London, Tokyo, SG, HK, Paris
        'lon': [-74.0060, -0.1278, 139.6917, 103.8198, 114.1694, 2.3522]
    })
    st.map(major_hubs, zoom=1, size=200, color="#0a66c2") # 使用 LinkedIn Blue
    
    st.markdown("---")

    # 2. 专家列表
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


# --- Tab 4: 涉外合同审查 ---
with tab_review:
    st.markdown(f"""
    <div class="li-card" style="text-align:center; padding:60px 20px;">
        <div style="font-size:48px; margin-bottom:20px; color:var(--linkedin-blue);">🛡️</div>
        <h3 style="color:#191919;">{T['upload_text']}</h3>
        <p style="color:#666; margin-bottom:30px; max-width:500px; margin-left:auto; margin-right:auto;">
            Secure AI analysis for {current_persona_name}. Checks for cross-border risks, jurisdiction clauses, and compliance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.file_uploader("", label_visibility="collapsed")


# --- Tab 5: 文书模版与智能起草 ---
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
                            AI Draft
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
