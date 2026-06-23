# eci-discovery-brief-generator
AI-powered pre-sales tool that converts raw client discovery notes into structured briefs, risk assessments, and SOW drafts for ECI's offshore delivery workflow.

# ECI Discovery to Delivery Brief Generator

An AI-powered pre-sales assistant built for ECI's product and delivery workflow.
Converts raw client discovery notes into structured briefs, risk scores, and
draft Statements of Work - reducing handoff friction between client-facing PMs
and offshore delivery teams.

---

## The Problem It Solves

ECI's PMs sit between client discovery and offshore delivery across multiple
accounts simultaneously. The quality of that handoff directly determines whether
a project scopes correctly or drifts. This tool standardizes and accelerates
that process.

---

## What It Does

**Step 1 - Generate Structured Brief**
Paste raw meeting notes, email threads, or call transcripts. The tool extracts:
- Client problem statement
- Tech environment and stack signals
- Stakeholders and their priorities
- ECI service area match (Cloud, Data, Cybersecurity, App Dev, AI)
- Compliance signals (SEC, FINRA, DORA, GDPR)
- Open questions to resolve before SOW
- Risk flags for delivery

**Step 2 - Risk Assessment**
Automatically scores the engagement as High / Medium / Low risk based on
compliance signals, timeline pressure, vendor history, and budget ambiguity.

**Step 3 - Draft SOW Outline**
Generates a draft Statement of Work with scope, out-of-scope items, delivery
phases, team roles, key assumptions, and open items - ready for internal review.

---

## Tech Stack

- **LLM**: Llama 3.3-70b via Groq API (low latency, free tier)
- **UI**: Gradio (Blocks layout, multi-panel)
- **Environment**: Google Colab with Secrets-based API key management
- **Language**: Python

---

## How to Run

1. Open the notebook in Google Colab
2. Add your Groq API key to Colab Secrets as `GROQ_API_KEY` and enable notebook access
3. Run all three cells in order
4. Use the Gradio public link to access the UI

---

## Demo Workflow

Paste discovery notes like this:

> Met with CTO and Head of Infrastructure at a mid-size hedge fund in NYC.
> They are on Azure but have not migrated fully, still running some on-prem
> workloads. Main pain point is they cannot get clean data pipelines from their
> trading systems into reporting. Mentioned SEC audit coming up in Q3. Two
> previous vendors failed them. They want something done in 90 days. No
> in-house DevOps.

**Output:**
- Structured brief with SEC compliance flag
- HIGH RISK score with triggered keywords listed
- Draft SOW outline with phased delivery plan

---

## Built For

This project was built as a forward deployment simulation for ECI's Senior PM
role, demonstrating understanding of ECI's pre-sales to offshore delivery
workflow for regulated financial services clients (hedge funds, PE firms,
alternative investment managers).

---

## Author

Abhishek Singh
MBA, UC Davis Graduate School of Management
linkedin.com/in/aabhishek-singh/
