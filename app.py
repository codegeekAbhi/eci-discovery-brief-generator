import streamlit as st
import json
import re
from groq import Groq

# ---- Page config ----
st.set_page_config(
    page_title="ECI Discovery Brief Generator",
    page_icon="assets/eci_logo.png",  # remove this line if you don't have logo
    layout="wide"
)

# ---- Load CSS ----
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---- Groq client ----
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---- Prompts ----
BRIEF_PROMPT = """
You are a Senior Product Manager at ECI, a Modern MSP serving hedge funds,
private equity firms, and alternative investment clients.

ECI's service areas:
- AI and Data Solutions (ELLA platform, data pipelines, data warehousing)
- Cloud and Infrastructure (AWS, Azure managed cloud, cloud migration)
- Cybersecurity and Compliance (Managed XDR, GRC, dark web monitoring)
- Application Development and DevOps
- Managed IT Services

Given raw discovery notes, return ONLY valid JSON with these exact keys:
{
  "client_problem": "1-2 sentence summary",
  "tech_environment": ["list of tech/tools mentioned"],
  "stakeholders": [{"name_or_role": "", "priority": ""}],
  "eci_service_match": ["matching ECI service areas"],
  "open_questions": ["ambiguities to resolve before SOW"],
  "risk_flags": ["scope, compliance, timeline, or budget risks"],
  "offshore_handoff_notes": "what the delivery lead needs to know upfront",
  "compliance_signals": ["SEC, FINRA, DORA, GDPR, etc."]
}

Return ONLY valid JSON. No preamble, no markdown backticks.
"""

SOW_PROMPT = """
You are a Senior Product Manager at ECI drafting a Statement of Work outline
for a financial services client.

Based on the structured brief, generate a professional SOW with these sections:
1. Project Overview
2. Scope of Work
3. Out of Scope
4. Proposed ECI Team (roles only)
5. Delivery Phases with estimated timelines
6. Key Assumptions
7. Open Items to Resolve Before Signing

Keep it concise. Internal review draft only.
"""

# ---- Helper functions ----
def call_groq(system_prompt, user_content, temperature=0.2):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()


def generate_brief(notes):
    raw = call_groq(BRIEF_PROMPT, f"Discovery notes:\n\n{notes}")
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def compute_risk(data):
    risk_keywords = [
        "sec", "finra", "dora", "gdpr", "audit", "90 days", "60 days",
        "failed", "no in-house", "budget not stated", "previous vendors"
    ]
    brief_text = json.dumps(data).lower()
    hits = [kw for kw in risk_keywords if kw in brief_text]
    count = len(hits)
    if count >= 3:
        return "HIGH", hits
    elif count >= 1:
        return "MEDIUM", hits
    return "LOW", hits


def generate_sow(brief_json):
    brief_text = json.dumps(brief_json, indent=2)
    return call_groq(SOW_PROMPT, f"Structured Brief:\n\n{brief_text}", temperature=0.3)


# ---- UI ----
st.markdown("""
<div class="eci-header">
    <h1>ECI Discovery to Delivery Brief Generator</h1>
    <p>Pre-sales workflow tool: raw discovery notes in, structured brief and SOW draft out.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="eci-divider">', unsafe_allow_html=True)

# ---- Input ----
notes = st.text_area(
    "Paste Discovery Notes Here",
    placeholder="Paste raw meeting notes, email thread, or call transcript...",
    height=220
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    generate_btn = st.button("Generate Brief")
with col2:
    sow_btn = st.button("Generate SOW Draft")

# ---- Session state ----
if "brief_data" not in st.session_state:
    st.session_state.brief_data = None

# ---- Generate Brief ----
if generate_btn:
    if not notes.strip():
        st.warning("Please paste discovery notes before generating.")
    else:
        with st.spinner("Analyzing discovery notes..."):
            try:
                st.session_state.brief_data = generate_brief(notes)
            except Exception as e:
                st.error(f"Failed to parse model output: {str(e)}")

# ---- Render Brief ----
if st.session_state.brief_data:
    data = st.session_state.brief_data
    risk_level, hits = compute_risk(data)

    st.markdown('<hr class="eci-divider">', unsafe_allow_html=True)

    # Risk badge
    risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}[risk_level]
    hits_display = ", ".join(hits) if hits else "None"
    st.markdown(f"""
    <div class="{risk_class}">
        {risk_level} RISK - Triggered by: {hits_display}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Client Problem</div>', unsafe_allow_html=True)
        st.markdown(f"<p>{data['client_problem']}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">ECI Service Match</div>', unsafe_allow_html=True)
        for s in data['eci_service_match']:
            st.markdown(f"<li>{s}</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Compliance Signals</div>', unsafe_allow_html=True)
        signals = data['compliance_signals'] if data['compliance_signals'] else ["None flagged"]
        for c in signals:
            st.markdown(f"<li>{c}</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Tech Environment</div>', unsafe_allow_html=True)
        for t in data['tech_environment']:
            st.markdown(f"<li>{t}</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Stakeholders</div>', unsafe_allow_html=True)
        for s in data['stakeholders']:
            st.markdown(f"<li><b>{s['name_or_role']}</b> : {s['priority']} priority</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Open Questions Before SOW</div>', unsafe_allow_html=True)
        for q in data['open_questions']:
            st.markdown(f"<li>{q}</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Risk Flags</div>', unsafe_allow_html=True)
        for r in data['risk_flags']:
            st.markdown(f"<li>{r}</li>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="eci-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Offshore Handoff Notes</div>', unsafe_allow_html=True)
        st.markdown(f"<p>{data['offshore_handoff_notes']}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---- SOW Draft ----
if sow_btn:
    if not st.session_state.brief_data:
        st.warning("Generate a brief first before creating the SOW.")
    else:
        with st.spinner("Drafting Statement of Work..."):
            sow = generate_sow(st.session_state.brief_data)
            st.markdown('<hr class="eci-divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Draft SOW Outline</div>', unsafe_allow_html=True)
            st.markdown('<div class="eci-card">', unsafe_allow_html=True)
            st.markdown(sow)
            st.markdown('</div>', unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<div class="eci-footer">
    Built for ECI's pre-sales workflow | Abhishek Singh | UC Davis MBA 2026
</div>
""", unsafe_allow_html=True)
