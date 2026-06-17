# 🤖 CRM Outreach Assistant
 
An AI-powered follow-up assistant for small business sales teams. Upload your leads CSV, automatically score and prioritize contacts, and generate personalized outreach messages — all from a clean Streamlit interface.
 
Try App Here : [ CRM-MANAGEMENT-ASSISTANT](https://crm-management-assistant.streamlit.app/)
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
 
## 🚀 Getting Started
 
### 1. Clone the Repository
 
```bash
git clone https://github.com/MLbyTharun/crm-outreach-assistant.git
cd crm-outreach-assistant
```
 
### 2. Create a Virtual Environment
 
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```
 
### 3. Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
### 4. Set Up Environment Variables
 
Create a `.env` file in the project root:
 
```env
GROQ_API_KEY=your_groq_api_key_here
```
 
> Get your free Groq API key at [console.groq.com](https://console.groq.com)
 
### 5. Run the App
 
```bash
streamlit run Main_app/app.py
```
 
---
 
## 📋 CSV Format
 
Your leads CSV must contain at least a `name` and `contact` column. All other columns are optional and will be auto-filled if missing.
 
| Column | Required | Description |
|---|---|---|
| `name` | ✅ | Contact's full name |
| `contact` | ✅ | Email or phone number |
| `company` | ❌ | Company name |
| `status` | ❌ | `New`, `Interested`, `Follow-up Needed`, or `Closed` |
| `interest_level` | ❌ | `Low`, `Medium`, or `High` |
| `notes` | ❌ | Free-text notes about the lead |
| `last_interaction` | ❌ | Date of last contact (YYYY-MM-DD) |
| `next_followup` | ❌ | Scheduled follow-up date (YYYY-MM-DD) |
 
A downloadable template is available directly within the app on the upload screen.
 
---
 
## 🧠 Priority Scoring Logic
 
Each lead receives a score from **0 to 10** based on three components:
 
| Component | Values |
|---|---|
| **Urgency** (next follow-up date) | Overdue → +4, Due Today → +2, Within 3 days → +1 |
| **Status weight** | Follow-up Needed → 4, Interested → 3, New → 2, Closed → 0 |
| **Interest weight** | High → 3, Medium → 2, Low → 1 |
 
Scores are then labeled:
- 🔴 **Hot** — Score ≥ 8
- 🟡 **Warm** — Score ≥ 5
- 🟢 **Cool** — Score < 5
---
 
## 🤖 AI Message Generation
 
The app uses **Groq's `llama-3.3-70b-versatile`** model to generate short, personalized outreach messages. You can choose from four tones:
 
- Professional
- Friendly
- Polite
- Persuasive
Messages are grounded in the customer's actual notes and always end with a clear next step. Generated messages are stored in session history per lead.
 
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| Data Processing | [Pandas](https://pandas.pydata.org/) |
| AI / LLM | [Groq Python SDK](https://github.com/groq/groq-python) — LLaMA 3.3 70B |
| Database | [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite |
| Env Management | [python-dotenv](https://github.com/theskumar/python-dotenv) |
 
---
 
## 🔒 Privacy
 
All uploaded lead data is stored only in the current browser session. It is never shared between users or persisted to a server. Each session is completely independent.
 
---
 
## 📄 License
 
This project is open source. Feel free to fork, modify, and build on it.
 