# 🤖 CRM Outreach Assistant
 
An AI-powered follow-up assistant for small business sales teams. Upload your leads CSV, automatically score and prioritize contacts, and generate personalized outreach messages — all from a clean Streamlit interface.
 
---
 
## ✨ Features
 
- **CSV Lead Import** — Upload your own leads CSV; data stays private to your browser session
- **Auto Enrichment** — Automatically fills missing columns, normalizes data, and computes priority scores
- **Priority Scoring** — Scores each lead 0–10 based on follow-up urgency, status, and interest level
- **Follow-Up Bucketing** — Classifies leads as *Overdue*, *Due Today*, or *Upcoming*
- **AI Message Generation** — Generates personalized follow-up messages using Groq's LLaMA 3.3 (70B) model with configurable tone
- **Lead Management** — Edit or delete individual leads directly in the UI
- **Analytics Dashboard** — Visual breakdowns of leads by status, interest level, and follow-up urgency
- **CSV Export** — Download your enriched and filtered lead list at any time
---
 
## 🗂️ Project Structure
 
```
crm-outreach-assistant/
│
├── Main_app/
│   └── app.py                  # Streamlit application entry point
│
├── model/
│   └── llm.py                  # FollowUpGenerator class (Groq LLaMA 3.3 integration)
│
├── important_functions/
│   ├── scoring.py              # Priority score computation and label logic
│   └── tools.py                # Session state init, data enrichment, bucketing
│
├── Database/
│   └── database.py             # SQLAlchemy SQLite engine setup
│
├── .gitignore
└── README.md
```
 
---