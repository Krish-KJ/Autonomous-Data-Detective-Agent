# 🕵️‍♂️ Autonomous Data Detective Agent

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#-setup--installation)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.0.1+-green)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-MultiAgent-orange)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**An autonomous multi-agent AI system for intelligent data analysis**

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage-guide)

</div>

---

## 📋 Overview

**Autonomous Data Detective** is a cutting-edge AI-powered data analysis platform that combines the power of **LangGraph**, **LangChain**, and **Streamlit** to create an intelligent, self-correcting analytics system.

Simply upload your CSV files, ask a question in plain English, and watch a **team of 6 specialized AI agents** automatically:
- 📊 Plan the analysis strategy
- 💻 Generate optimized Pandas code
- ✅ Execute code safely in a sandboxed environment
- 🔧 Auto-fix errors with intelligent debugging
- 📈 Create interactive Plotly visualizations
- 📝 Summarize findings with actionable insights

All with **PDF & Excel export**, **multi-file support**, **token tracking**, and **session persistence**.

---

## 🎯 Key Highlights

✨ **No Coding Required** — Ask questions in natural language  
🤖 **6-Agent Pipeline** — Specialized AI agents working in harmony  
🔒 **Enterprise Security** — AST-based sandboxing prevents code injection  
🔄 **Self-Healing** — Auto-fixes errors up to 3 times  
🌐 **LLM Redundancy** — Fallback cascade: Groq → Gemini → OpenRouter  
📂 **Multi-CSV Analysis** — Query across multiple datasets simultaneously  
📊 **Professional Reports** — Export to PDF or Excel with one click  
💾 **Session Management** — Save and resume analysis sessions  

---

## 🏗️ Architecture

### Agent Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ [1] PLANNER AGENT                                           │
│ → Analyzes dataset schema & user query                      │
│ → Creates step-by-step execution plan                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ [2] CODE WRITER AGENT                                       │
│ → Writes optimized Pandas code following the plan           │
│ → Handles multi-CSV variable injection                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ [3] VALIDATOR AGENT                                         │
│ → Safely executes code in sandboxed environment             │
│ → Captures stdout and errors                                │
└────────────────────┬────────────────────────────────────────┘
                     │
            ┌────────▼─────────┐
            │  Execution OK?   │
            └────────┬─────────┘
          No        │        Yes
            │       │        │
    ┌───────▼────┐  │    ┌───▼──────────────┐
    │ [4] ERROR  │  │    │ [5] VISUALIZER   │
    │ FIXER      │  │    │ → Creates Plotly │
    │ (Retry 3x) │  │    │ charts from data │
    └───────┬────┘  │    └───┬──────────────┘
            │       │        │
            └───────┬────────┘
                    │
        ┌───────────▼──────────────┐
        │ [6] INSIGHT GENERATOR    │
        │ → Formats findings       │
        │ → Structures report      │
        └───────────┬──────────────┘
                    │
            ┌───────▼──────────┐
            │  USER RESULTS    │
            │  • Insights      │
            │  • Charts        │
            │  • Code          │
            └──────────────────┘
```

### Agent Roles

| # | Agent | Function |
|---|:---|:---|
| 1️⃣ | **Planner** | Reads dataset schema, queries, and quality metrics. Outputs structured execution strategy. |
| 2️⃣ | **Code Writer** | Generates production-ready Pandas code from the plan. Handles complex operations elegantly. |
| 3️⃣ | **Validator** | Executes code safely using AST-checked, restricted globals. Captures output & errors. |
| 4️⃣ | **Error Fixer** | Receives error traces, generates corrected code. Feeds back to Validator (max 3 retries). |
| 5️⃣ | **Visualizer** | Creates interactive Plotly charts. Outputs figure JSON for embedding in reports. |
| 6️⃣ | **Insight Generator** | Transforms raw execution output into formatted findings with business context. |

**Bonus:** **Data Quality Agent** (non-LLM) detects issues on file upload: missing values, duplicates, outliers.

---

## ✨ Features

### Core Functionality
| Feature | Details |
|:---|:---|
| 🧠 **Natural Language Analysis** | Ask questions like a human would—no SQL or code needed |
| 📂 **Multi-File Support** | Upload multiple CSVs; reference each by name in queries |
| 🔍 **Automatic Data Quality** | Missing values, duplicates, outlier detection on upload |
| 📊 **Interactive Charts** | Plotly visualizations optimized for the query |
| 💭 **Conversational Memory** | Ask follow-up questions in a single session |

### Intelligence & Reliability
| Feature | Details |
|:---|:---|
| 🤖 **6-Agent Orchestration** | Specialized agents collaborate via LangGraph state machine |
| 🔄 **Self-Healing Loop** | Auto-detects and fixes code errors up to 3 times |
| 🔒 **Security Sandbox** | AST-based code validation blocks dangerous imports |
| 🌐 **Multi-Provider LLM Fallback** | Groq (primary) → Gemini (secondary) → OpenRouter (fallback) |
| ⚡ **Rate Limit Handling** | Automatic key rotation across 12 API keys |

### Analysis & Reporting
| Feature | Details |
|:---|:---|
| 📄 **PDF Export** | Professional multi-page report with charts and code |
| 📊 **Excel Export** | Multi-sheet workbook (one sheet per query) |
| 📈 **Token Tracking** | See LLM usage, cost estimates, and provider breakdown |
| 💾 **Session Persistence** | Save/load analysis sessions as JSON |
| 📋 **Code Visibility** | View generated code for transparency and learning |

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| **Frontend UI** | Streamlit (Custom Dark Theme) |
| **Agent Orchestration** | LangGraph (State Graph) |
| **LLM Integration** | LangChain (Multi-provider) |
| **LLM Providers** | Groq Llama 3.1, Google Gemini 1.5 Flash, OpenRouter |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly Express & Graph Objects |
| **PDF Generation** | ReportLab + Kaleido |
| **Excel Creation** | openpyxl |
| **Code Safety** | Python AST module |
| **Environment** | python-dotenv |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- 250MB disk space
- Active internet connection

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/sk191/Autonomous-Data-Detective.git
cd Autonomous-Data-Detective

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
# Copy .env.example to .env and fill in your API keys
# (See "Configuration" section below)

# 5. Launch
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📖 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/sk191/Autonomous-Data-Detective.git
cd Autonomous-Data-Detective
```

### Step 2: Set Up Python Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get API Keys

Create a `.env` file with the following structure:

```env
# ==========================================
# TIER 1 - PRIMARY (Groq - Free Tier)
# Get keys: https://console.groq.com/keys
# ==========================================
GROQ_API_KEY_1="gsk_your_key_here"
GROQ_API_KEY_2="gsk_your_key_here"
GROQ_API_KEY_3="gsk_your_key_here"
GROQ_API_KEY_4="gsk_your_key_here"

# ==========================================
# TIER 2 - SECONDARY (Google Gemini - Free Tier)
# Get keys: https://aistudio.google.com/
# ==========================================
GEMINI_API_KEY_1="AIzaSy_your_key_here"
GEMINI_API_KEY_2="AIzaSy_your_key_here"

# ==========================================
# TIER 3 - FALLBACK (OpenRouter - Free Tier)
# Get keys: https://openrouter.ai/
# ==========================================
OPENROUTER_API_KEY_1="sk-or-v1-your_key_here"
OPENROUTER_API_KEY_2="sk-or-v1-your_key_here"
OPENROUTER_API_KEY_3="sk-or-v1-your_key_here"
OPENROUTER_API_KEY_4="sk-or-v1-your_key_here"
```

**Get Free API Keys:**
- **Groq**: [console.groq.com](https://console.groq.com) → Create multiple accounts for rate-limit rotation
- **Google Gemini**: [aistudio.google.com](https://aistudio.google.com) → Get API key immediately
- **OpenRouter**: [openrouter.ai](https://openrouter.ai) → Sign up for free tier access

### Step 5: Launch the Application

```bash
streamlit run app.py
```

Open your browser to **http://localhost:8501**

---

## 💻 Usage Guide

### Basic Workflow

1. **Upload CSV Files**
   - Click "📂 Data Source" in the sidebar
   - Select one or multiple CSV files
   - Files are automatically validated and profiled

2. **View Data Quality Report**
   - Expand "🔍 Data Quality Report"
   - See missing values, duplicates, outliers
   - Understand data distribution before querying

3. **Ask a Question**
   - Type your query in the chat input
   - Examples:
     - "What are the top 5 products by sales?"
     - "Show me the correlation between price and quantity sold"
     - "What percentage of orders were completed?"
     - "Which regions have the highest average revenue?"

4. **Watch the Agents Work**
   - See real-time progress of each agent
   - Green checkmarks indicate success
   - Red X indicates errors (auto-fixed)

5. **View Results**
   - 📝 **Insights**: Structured findings with key statistics
   - 📈 **Chart**: Interactive Plotly visualization
   - 💻 **Code**: View the generated Python code (expandable)

6. **Export Results**
   - **PDF**: Professional report with all queries, charts, and code
   - **Excel**: Multi-sheet workbook for further analysis
   - **Session**: JSON file to resume later

### Example Queries

**Sales Analysis:**
```
"What were the total sales by product category for Q3, and show me a bar chart?"
```

**Customer Insights:**
```
"Calculate the average order value by customer segment and identify the top 10 customers"
```

**Data Validation:**
```
"Check for duplicate orders and show me any orders with missing payment information"
```

**Time Series:**
```
"Plot monthly revenue trends over the past 2 years and identify any significant drops"
```

### Multi-File Analysis

When you upload multiple CSVs, each becomes a variable:
- `sales_data.csv` → Access as `sales_data`
- `customers.csv` → Access as `customers`
- `products.csv` → Access as `products`

**Query Example:**
```
"Join sales data with customer info and show top 10 customers by lifetime value"
```

The Code Writer automatically uses the correct variable names and merge operations.

---

## 📁 Project Structure

```
Autonomous-Data-Detective/
│
├── 📄 app.py
│   └── Main Streamlit UI
│       • File upload & preview
│       • Chat interface
│       • Session management
│       • PDF/Excel export buttons
│
├── 📄 graph.py
│   └── LangGraph agent pipeline
│       • 6-node StateGraph definition
│       • Conditional routing logic
│       • Agent node functions
│
├── 📄 llm_router.py
│   └── Multi-provider LLM orchestration
│       • Groq/Gemini/OpenRouter fallback
│       • Rate limit handling
│       • Token tracking
│
├── 📄 safe_executor.py
│   └── Secure code execution sandbox
│       • AST-based security validation
│       • Restricted globals & builtins
│       • Error capture & formatting
│
├── 📄 data_quality_agent.py
│   └── Automated EDA & profiling
│       • Missing value detection
│       • Duplicate row counting
│       • IQR-based outlier detection
│       • Data type summary
│
├── 📄 pdf_generator.py
│   └── Professional PDF report builder
│       • Multi-page formatting
│       • Chart embedding
│       • Code syntax highlighting
│       • ReportLab styling
│
├── 📄 requirements.txt
│   └── Python package dependencies
│
├── 📄 .env
│   └── API keys (create this file)
│
├── 📁 .streamlit/
│   └── config.toml (Streamlit configuration)
│
└── 📄 README.md
    └── This file
```

---

## 🔒 Security & Safety

### Code Sandboxing

The system prevents malicious code execution through multiple layers:

1. **AST Parsing** - All generated code is parsed and checked before execution
2. **Blocklist** - Dangerous imports are blocked: `os`, `sys`, `subprocess`, `eval`, `exec`
3. **Restricted Globals** - Only safe builtins are available in execution environment
4. **IO Capture** - All output is captured; no direct file system access
5. **Error Handling** - Graceful failure with detailed error messages

### Data Privacy

- All data processing happens **locally** on your machine
- No data is stored on external servers
- API keys are never logged or transmitted (except to their respective providers)
- Sessions saved as JSON remain on your local filesystem

---

## 🌐 Cloud Deployment (Streamlit Cloud)

### Deploy to Streamlit Community Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New App"
   - Select your GitHub repository
   - Set main file to `app.py`

3. **Add Secrets**
   - Click "Advanced settings"
   - Paste your API keys in TOML format:
   ```toml
   GROQ_API_KEY_1 = "gsk_xxxxx"
   GROQ_API_KEY_2 = "gsk_xxxxx"
   GEMINI_API_KEY_1 = "AIzaSy_xxxxx"
   OPENROUTER_API_KEY_1 = "sk-or-v1-xxxxx"
   ```

4. **Deploy**
   - Click "Deploy"
   - Your app is now live!

---

## 🐛 Troubleshooting

### Issue: "All API providers failed"

**Solution:**
- Verify `.env` file exists in project root
- Check API keys are valid and active
- Ensure internet connection is stable
- Try rotating to different API keys in `.env`

### Issue: "Code execution failed"

**Solution:**
- Check if your CSV files are properly formatted
- Ensure column names are valid Python identifiers
- Try a simpler query first
- View generated code to identify the issue

### Issue: Streamlit not starting

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run with verbose output
streamlit run app.py --logger.level=debug
```

### Issue: Large file takes too long

**Solution:**
- Process files with <500k rows for best performance
- Reduce file size before uploading
- Use simpler queries on large datasets

---

## 📊 Performance Tips

1. **Optimize CSV Files**
   - Remove unnecessary columns before uploading
   - Use numeric codes instead of long text descriptions
   - Keep datasets under 100MB

2. **Query Optimization**
   - Start with simple aggregations
   - Avoid complex joins on massive datasets
   - Use `groupby` for large categories

3. **API Performance**
   - The system will automatically rotate through API keys if rate-limited
   - Groq typically responds in 1-2 seconds (fastest)
   - Gemini fallback takes 3-5 seconds
   - OpenRouter free tier may have longer response times

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

You are free to:
- Use this commercially
- Modify the code
- Distribute copies
- Include in your own projects

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [LangChain](https://github.com/langchain-ai/langchain) — LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) — Agentic orchestration
- [Streamlit](https://streamlit.io) — Beautiful web UIs
- [Plotly](https://plotly.com) — Interactive visualizations
- [Groq](https://groq.com) — Fast LLM inference
- [Google AI](https://ai.google.dev) — Gemini API
- [OpenRouter](https://openrouter.ai) — LLM aggregation

---

## 📞 Support & Feedback

- **Issues**: [GitHub Issues](https://github.com/sk191/Autonomous-Data-Detective/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sk191/Autonomous-Data-Detective/discussions)
- **Email**: [Contact](mailto:your-email@example.com)

---

<div align="center">

**[⬆ Back to top](#-autonomous-data-detective-agent)**

Made with 🧠 AI, 💻 Code, and ☕ Coffee

</div>

