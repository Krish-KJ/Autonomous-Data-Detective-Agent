# 🕵️‍♂️ Autonomous Data Detective Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Integration-green)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-MultiAgent-orange)](https://github.com/langchain-ai/langgraph)

An autonomous multi-agent data analysis platform built with **LangGraph** and **Streamlit**. Upload one or more CSV files, ask questions in plain English, and a team of **6 specialized AI agents** will automatically plan, code, execute, debug, visualize, and summarize the results — with full PDF & Excel export.

---

## 📌 Architecture: 6-Agent LangGraph Pipeline

```
[USER QUERY] → Planner → Code Writer → Validator ←→ Error Fixer (3 retries)
                                            ↓
                                      Visualizer → Insight Generator → [RESULTS]
```

| Agent | Role |
|:---|:---|
| **Planner Agent** | Analyzes dataset schema and user query to create a step-by-step execution plan |
| **Code Writer Agent** | Generates optimized Pandas code following the plan |
| **Validator Agent** | Safely executes code in a sandboxed environment with AST security checks |
| **Error Fixer Agent** | Autonomously debugs and fixes code errors (up to 3 retry attempts) |
| **Visualizer Agent** | Creates interactive Plotly charts from the results |
| **Insight Generator Agent** | Summarizes findings with structured Key Findings and Summary sections |

Additionally, a **Data Quality Agent** runs on upload to flag missing values, duplicates, and outliers — no LLM call needed.

---

## ✨ Key Features

| Feature | Description |
|:---|:---|
| 🧠 **Multi-Provider LLM Fallback** | Groq → Gemini → OpenRouter cascading. Never fails mid-request. |
| 🔒 **Sandboxed Code Execution** | AST-based security blocks dangerous imports (`os`, `sys`, `subprocess`) before execution |
| 🔄 **Self-Healing Code Loop** | LangGraph cyclic retry: write → execute → catch error → fix → re-execute (3 attempts) |
| 📂 **Multi-CSV Support** | Upload multiple CSVs and query across them. Each file is injected as a named variable |
| 🔍 **Auto Data Quality Report** | Missing values, duplicates, outlier detection (IQR) shown on upload |
| 📊 **Token Usage Tracker** | Tracks LLM calls, token estimates, and provider breakdown per session |
| 💬 **Chat Memory** | Ask multiple follow-up questions in a single session with full conversation history |
| 📄 **PDF Export** | Modern multi-page PDF with all queries, insights, charts, and code |
| 📊 **Excel Export** | Multi-sheet `.xlsx` workbook — one sheet per query with insights and code |
| 💾 **Session Save/Load** | Save your analysis session as JSON, reload it later to continue |

---

## 🛠️ Tech Stack

| Category | Technologies |
|:---|:---|
| **Frontend** | Streamlit (Custom Dark Theme) |
| **AI Orchestration** | LangChain, LangGraph |
| **LLM Providers** | Groq (Llama 3.1 8B), Google Gemini 1.5 Flash, OpenRouter |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly |
| **PDF Generation** | ReportLab, Kaleido |
| **Excel Export** | openpyxl |

---

## 🚀 Setup & Installation

**Prerequisites:** Python 3.10+

### 1. Clone the Repository
```bash
git clone https://github.com/Shubham1919284/Autonomous-Data-Detective-Agent.git
cd Autonomous-Data-Detective-Agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```env
# Groq (Free tier — create multiple accounts for rate-limit rotation)
GROQ_API_KEY_1=gsk_your_key_here
GROQ_API_KEY_2=gsk_your_key_here
GROQ_API_KEY_3=gsk_your_key_here
GROQ_API_KEY_4=gsk_your_key_here

# Google Gemini (Free tier — https://aistudio.google.com/)
GEMINI_API_KEY_1=AIzaSy_your_key_here
GEMINI_API_KEY_2=AIzaSy_your_key_here

# OpenRouter (Free tier — https://openrouter.ai/)
OPENROUTER_API_KEY_1=sk-or-v1-your_key_here
OPENROUTER_API_KEY_2=sk-or-v1-your_key_here
OPENROUTER_API_KEY_3=sk-or-v1-your_key_here
OPENROUTER_API_KEY_4=sk-or-v1-your_key_here
```

### 5. Launch
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 🌐 Streamlit Cloud Deployment

1. Push this repo to your GitHub
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) → **New App**
3. Select your repo, set `app.py` as the main file
4. Under **Advanced Settings → Secrets**, paste your keys in TOML format:
   ```toml
   GROQ_API_KEY_1 = "gsk_xxxxx"
   GROQ_API_KEY_2 = "gsk_xxxxx"
   GEMINI_API_KEY_1 = "AIzaSyxxxx"
   OPENROUTER_API_KEY_1 = "sk-or-v1-xxxx"
   ```
5. Click **Deploy**

---

## 📁 Project Structure

```
Autonomous-Data-Detective-Agent/
├── app.py                  # Main Streamlit UI with chat interface
├── graph.py                # LangGraph 6-node agent pipeline
├── llm_router.py           # Multi-provider LLM fallback with token tracking
├── safe_executor.py        # AST-secured Python code sandbox
├── data_quality_agent.py   # Automated EDA & quality checks
├── pdf_generator.py        # Modern multi-query PDF report builder
├── requirements.txt        # Python dependencies
├── .env                    # API keys (git-ignored)
├── .gitignore
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── README.md
```

---

## 📄 Resume Bullet Points

> - **Architected an Autonomous Multi-Agent Data Analysis Platform** using LangGraph with 6 specialized AI agents (Planner, Coder, Validator, Error Fixer, Visualizer, Insight Generator) that autonomously analyze CSV datasets from natural language queries.
> - **Engineered a Fault-Tolerant LLM Cascading System** across Groq, Google Gemini, and OpenRouter with automatic rate-limit rotation, token usage tracking, and provider fallback ensuring near-100% uptime on free-tier APIs.
> - **Built a Sandboxed Python Execution Engine** with AST-based security scanning, blocking dangerous system imports while supporting multi-DataFrame analysis across uploaded CSV files.
> - **Designed a Multi-Format Export Pipeline** generating professional multi-page PDF reports (ReportLab) and multi-sheet Excel workbooks (openpyxl), with session persistence via JSON save/load functionality.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
