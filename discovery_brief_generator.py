

# ================================================================================

# Cell 0
!pip install groq gradio

from google.colab import userdata
import groq
import gradio as gr

GROQ_API_KEY = userdata.get('GROQ_API_KEY')
client = groq.Groq(api_key=GROQ_API_KEY)

# ================================================================================

# Cell 1
SYSTEM_PROMPT = """
You are a Senior Product Manager at ECI, a Modern MSP serving hedge funds,
private equity firms, and alternative investment clients.

ECI's service areas include:
- AI and Data Solutions (ELLA platform, data pipelines, data warehousing)
- Cloud and Infrastructure (AWS, Azure managed cloud, cloud migration)
- Cybersecurity and Compliance (Managed XDR, GRC, dark web monitoring)
- Application Development and DevOps
- Managed IT Services

Given raw discovery notes from a client meeting, extract and return a
structured JSON with these exact keys:

{
  "client_problem": "1-2 sentence summary of the core business problem",
  "tech_environment": ["list of tech stack or tools mentioned"],
  "stakeholders": [{"name_or_role": "", "priority": ""}],
  "eci_service_match": ["relevant ECI service areas from the list above"],
  "open_questions": ["ambiguities that must be resolved before SOW"],
  "risk_flags": ["scope, compliance, timeline, or budget risks"],
  "offshore_handoff_notes": "what the delivery lead needs to know upfront",
  "compliance_signals": ["any regulatory mentions: SEC, FINRA, DORA, GDPR, etc."]
}

Return ONLY valid JSON. No preamble, no explanation, no markdown backticks.
"""

import json
import re

def generate_brief(discovery_notes):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Discovery notes:\n\n{discovery_notes}"}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if model adds them anyway
        raw = re.sub(r"```json|```", "", raw).strip()

        data = json.loads(raw)

        output = f"""
=== CLIENT BRIEF ===

PROBLEM:
{data['client_problem']}

ECI SERVICE MATCH:
{chr(10).join(f"  - {s}" for s in data['eci_service_match'])}

COMPLIANCE SIGNALS:
{chr(10).join(f"  - {c}" for c in data['compliance_signals']) if data['compliance_signals'] else '  - None flagged'}

STAKEHOLDERS:
{chr(10).join(f"  - {s['name_or_role']} : {s['priority']}" for s in data['stakeholders'])}

OPEN QUESTIONS BEFORE SOW:
{chr(10).join(f"  - {q}" for q in data['open_questions'])}

RISK FLAGS:
{chr(10).join(f"  - {r}" for r in data['risk_flags'])}

=== OFFSHORE DELIVERY NOTES ===
{data['offshore_handoff_notes']}

TECH ENVIRONMENT:
{chr(10).join(f"  - {t}" for t in data['tech_environment'])}
        """
        return output.strip()

    except json.JSONDecodeError as e:
        return f"JSON parsing failed: {str(e)}\n\nRaw model output:\n{raw}"
    except Exception as e:
        return f"Error: {str(e)}"

# ================================================================================

# Cell 2
def generate_sow(brief_output):
    if not brief_output or "Error" in brief_output:
        return "Please generate a brief first before creating the SOW."

    sow_prompt = """
You are a Senior Product Manager at ECI drafting a Statement of Work outline
for a client in the financial services sector.

Based on the structured brief below, generate a professional SOW outline with these sections:

1. Project Overview (2-3 sentences)
2. Scope of Work (bullet list of deliverables)
3. Out of Scope (what ECI will NOT deliver)
4. Proposed ECI Team (roles only, no names)
5. Delivery Phases with estimated timelines
6. Key Assumptions
7. Open Items to Resolve Before Signing

Keep it concise. This is a draft for internal review, not a final client document.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": sow_prompt},
            {"role": "user", "content": f"Structured Brief:\n\n{brief_output}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def compute_risk_score(brief_output):
    if not brief_output:
        return "No brief generated yet."
    risk_keywords = ["SEC", "FINRA", "DORA", "GDPR", "audit", "90 days", "60 days",
                     "failed", "no in-house", "budget not stated", "two previous vendors"]
    hits = [kw for kw in risk_keywords if kw.lower() in brief_output.lower()]
    count = len(hits)
    if count >= 3:
        level = "HIGH RISK"
        detail = "Multiple compliance, timeline, or vendor-history flags detected. Escalate to Director before SOW."
    elif count >= 1:
        level = "MEDIUM RISK"
        detail = "Some flags present. Review open questions before committing to scope."
    else:
        level = "LOW RISK"
        detail = "No major flags detected. Standard delivery process applies."
    return f"{level} ({count} flag(s) detected)\n\nTriggered by: {', '.join(hits) if hits else 'None'}\n\n{detail}"


with gr.Blocks(title="ECI Discovery to Delivery Brief Generator") as demo:
    gr.Markdown("# ECI Discovery to Delivery Brief Generator")
    gr.Markdown("Built for ECI's pre-sales workflow: raw discovery notes in, structured brief and SOW draft out.")

    with gr.Row():
        notes_input = gr.Textbox(
            lines=15,
            label="Paste Discovery Notes Here",
            placeholder="Paste raw meeting notes, email thread, or call transcript..."
        )
        brief_output = gr.Textbox(lines=15, label="Structured Brief")

    generate_btn = gr.Button("Generate Brief", variant="primary")

    with gr.Row():
        risk_output = gr.Textbox(label="Risk Assessment", lines=4)
        sow_output = gr.Textbox(label="Draft SOW Outline", lines=15)

    sow_btn = gr.Button("Generate Draft SOW", variant="secondary")

    generate_btn.click(fn=generate_brief, inputs=notes_input, outputs=brief_output)
    generate_btn.click(fn=compute_risk_score, inputs=brief_output, outputs=risk_output)
    sow_btn.click(fn=generate_sow, inputs=brief_output, outputs=sow_output)

demo.launch(share=True)

# ================================================================================

# Cell 3
import json
from google.colab import _message

# Get the notebook JSON
nb = _message.blocking_request('get_ipynb')['ipynb']

# Extract code cells
all_code = "\n\n# " + "="*80 + "\n\n"
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        all_code += f"# Cell {i}\n"
        all_code += ''.join(cell['source'])
        all_code += "\n\n# " + "="*80 + "\n\n"

# Save to a .py file
with open('entire_notebook.py', 'w') as f:
    f.write(all_code)

# Print all code (optional)
print(all_code)

