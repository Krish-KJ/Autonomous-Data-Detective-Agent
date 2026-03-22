import streamlit as st
import pandas as pd
import os
import json
import time
import plotly.io as pio
from io import BytesIO
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Set page config FIRST
st.set_page_config(
    page_title="Autonomous Data Detective Agent",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .agent-log {
        background-color: #1E212A;
        border-left: 4px solid #9146FF;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-family: monospace;
    }
    .status-running { color: #f39c12; }
    .status-success { color: #2ecc71; }
    .status-error { color: #e74c3c; }
    .quality-card {
        background: linear-gradient(135deg, #1E1B2E 0%, #2D2A40 100%);
        border: 1px solid #7C3AED;
        border-radius: 10px;
        padding: 16px;
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# Import backend
from graph import build_graph
from pdf_generator import generate_pdf_report
from data_quality_agent import run_data_quality_check, format_quality_report


def main():
    st.title("🕵️‍♂️ Autonomous Data Detective Agent")
    st.markdown("Upload your data, ask a question, and let a team of **6 AI Agents** analyze, code, debug, visualize, and summarize the results automatically.")

    # ── Session State Initialization ──
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_usage" not in st.session_state:
        st.session_state.llm_usage = []
    if "all_dataframes" not in st.session_state:
        st.session_state.all_dataframes = {}

    # ── Detect active LLM tier ──
    active_model_display = "Groq LLaMA 3.1"
    if not os.environ.get("GROQ_API_KEY_1") and os.environ.get("GEMINI_API_KEY_1"):
        active_model_display = "Google Gemini 1.5 Flash"
    elif not os.environ.get("GROQ_API_KEY_1") and not os.environ.get("GEMINI_API_KEY_1"):
        active_model_display = "OpenRouter (Free)"

    # =================================================================
    # SIDEBAR
    # =================================================================
    with st.sidebar:
        st.markdown(f"**🧠 Active Model:** `{active_model_display}`")
        st.divider()

        # ── Data Upload (Multi-CSV) ──
        st.header("📂 Data Source")
        uploaded_files = st.file_uploader(
            "Upload CSV Datasets", type=["csv"],
            accept_multiple_files=True
        )

        # ── Token Usage Tracker ──
        if st.session_state.llm_usage:
            st.divider()
            st.header("📊 Usage Stats")
            total_calls = len(st.session_state.llm_usage)
            total_tokens = sum(u['total_tokens'] for u in st.session_state.llm_usage)
            
            col1, col2 = st.columns(2)
            col1.metric("LLM Calls", total_calls)
            col2.metric("Est. Tokens", f"{total_tokens:,}")
            
            # Calls by provider
            providers = {}
            for u in st.session_state.llm_usage:
                p = u['provider'].split(' - ')[0]  # Just the provider name
                providers[p] = providers.get(p, 0) + 1
            for p, count in providers.items():
                st.caption(f"↳ {p}: {count} calls")

        # ── Export Buttons ──
        if st.session_state.messages:
            st.divider()
            st.header("📥 Export")
            total_q = sum(1 for m in st.session_state.messages if m['role'] == 'user')
            st.caption(f"{total_q} queries in this session")

            # PDF Export
            if st.button("📄 Generate PDF Report"):
                with st.spinner("Building PDF..."):
                    pdf_path = generate_pdf_report(
                        messages=st.session_state.messages,
                        output_path="Data_Detective_Report.pdf"
                    )
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name="Data_Detective_Report.pdf",
                    mime="application/pdf"
                )

            # Excel Export
            if st.button("📊 Export to Excel"):
                with st.spinner("Building Excel..."):
                    excel_buffer = _build_excel(st.session_state.messages)
                st.download_button(
                    "⬇️ Download Excel",
                    data=excel_buffer,
                    file_name="Data_Detective_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # ── Session Save/Load ──
        st.divider()
        st.header("💾 Session")
        
        # Save Session
        if st.session_state.messages:
            session_data = json.dumps({
                "messages": [
                    {"role": m["role"], "content": m["content"],
                     "code": m.get("code", ""), "chart": ""}  # Charts stripped for size
                    for m in st.session_state.messages
                ],
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }, indent=2)
            st.download_button(
                "💾 Save Session",
                data=session_data,
                file_name="detective_session.json",
                mime="application/json"
            )

        # Load Session
        session_file = st.file_uploader("Load a saved session", type=["json"], key="session_loader")
        if session_file:
            try:
                loaded = json.load(session_file)
                st.session_state.messages = loaded.get("messages", [])
                st.success(f"Session loaded ({len(st.session_state.messages)} messages)")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load session: {e}")

    # =================================================================
    # MAIN CONTENT
    # =================================================================
    if not uploaded_files:
        st.info("👈 Please upload one or more CSV files in the sidebar to get started.")
        return

    # ── Process Uploaded Files ──
    all_dfs = {}
    primary_df = None
    
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            name = uploaded_file.name
            all_dfs[name] = df
            if primary_df is None:
                primary_df = df
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")

    if not all_dfs:
        return

    # Store in session state for agents
    st.session_state['current_df'] = primary_df
    st.session_state['all_dataframes'] = all_dfs

    # ── Dataset Preview ──
    with st.expander(f"📋 Preview Datasets ({len(all_dfs)} files)", expanded=False):
        for name, frame in all_dfs.items():
            st.markdown(f"**{name}** — {frame.shape[0]} rows × {frame.shape[1]} columns")
            st.dataframe(frame.head(), use_container_width=True)

    # ── Data Quality Report ──
    with st.expander("🔍 Data Quality Report", expanded=False):
        for name, frame in all_dfs.items():
            report = run_data_quality_check(frame)
            st.markdown(f"### {name}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows", report['shape']['rows'])
            col2.metric("Columns", report['shape']['columns'])
            col3.metric("Duplicates", f"{report['duplicate_rows']} ({report['duplicate_pct']}%)")
            col4.metric("Missing", f"{report['total_missing_pct']}%")
            
            if report['missing']:
                st.markdown("**Columns with Missing Values:**")
                missing_df = pd.DataFrame([
                    {"Column": col, "Missing": info['missing_count'], "Percent": f"{info['missing_pct']}%"}
                    for col, info in report['missing'].items()
                ])
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
                
            if report['outliers']:
                st.markdown("**Outliers Detected (IQR):**")
                outlier_df = pd.DataFrame([
                    {"Column": col, "Outliers": info['count'], "Percent": f"{info['pct']}%", "Expected Range": info['range']}
                    for col, info in report['outliers'].items()
                ])
                st.dataframe(outlier_df, use_container_width=True, hide_index=True)
            
            if len(all_dfs) > 1:
                st.divider()

    # ── Build quality + multi-df context strings ──
    quality_report_str = format_quality_report(run_data_quality_check(primary_df))
    
    multi_df_desc = ""
    if len(all_dfs) > 1:
        parts = []
        for name, frame in all_dfs.items():
            safe_name = name.replace('.csv', '').replace(' ', '_').replace('-', '_')
            parts.append(f"- `{safe_name}`: columns = {list(frame.columns)}")
        multi_df_desc = "The following DataFrames are available by variable name:\n" + "\n".join(parts)

    # ── Chat History ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart"):
                try:
                    fig = pio.from_json(msg["chart"])
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
            if msg.get("code"):
                with st.expander("Show Generated Code"):
                    st.code(msg["code"], language="python")

    # ── Query Input ──
    query = st.chat_input("Ask a question about your data (e.g., 'What are the top 5 products by sales?')")

    if query:
        st.chat_message("user").write(query)
        st.session_state.messages.append({"role": "user", "content": query})

        # Prepare LangGraph State
        initial_state = {
            "query": query,
            "df_columns": list(primary_df.columns),
            "df_dtypes": {col: str(dtype) for col, dtype in primary_df.dtypes.items()},
            "df_head": primary_df.head().to_markdown(),
            "available_dataframes": multi_df_desc,
            "data_quality_report": quality_report_str,
            "plan": "",
            "generated_code": "",
            "execution_result": "",
            "execution_error": "",
            "retry_count": 0,
            "figure_json": "",
            "insights": ""
        }

        log_container = st.container()
        ai_graph = build_graph()

        with st.spinner("Agents are analyzing..."):
            for step_event in ai_graph.stream(initial_state, {"recursion_limit": 25}):
                for node_name, state_update in step_event.items():
                    with log_container:
                        if node_name == "planner":
                            st.markdown('<div class="agent-log"><span class="status-success">✓</span> <b>Planner Agent:</b> Created execution plan.</div>', unsafe_allow_html=True)
                        elif node_name == "coder":
                            st.markdown('<div class="agent-log"><span class="status-success">✓</span> <b>Code Writer Agent:</b> Wrote Python script.</div>', unsafe_allow_html=True)
                        elif node_name == "validator":
                            err = state_update.get("execution_error")
                            if err:
                                st.markdown('<div class="agent-log"><span class="status-error">✗</span> <b>Validator Agent:</b> Code failed. Triggering Auto-Fixer.</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="agent-log"><span class="status-success">✓</span> <b>Validator Agent:</b> Code executed successfully.</div>', unsafe_allow_html=True)
                        elif node_name == "fixer":
                            st.markdown(f'<div class="agent-log"><span class="status-running">↻</span> <b>Error Fixer Agent:</b> Applying corrections (Attempt {state_update.get("retry_count", 1)}/3).</div>', unsafe_allow_html=True)
                        elif node_name == "visualizer":
                            st.markdown('<div class="agent-log"><span class="status-success">✓</span> <b>Visualizer Agent:</b> Chart generated.</div>', unsafe_allow_html=True)
                        elif node_name == "insights":
                            st.markdown('<div class="agent-log"><span class="status-success">✓</span> <b>Insight Generator:</b> Report drafted.</div>', unsafe_allow_html=True)

        st.success("Analysis Complete!")

        # Rebuild final state from stream
        current_state = initial_state.copy()
        for step_event in ai_graph.stream(initial_state, {"recursion_limit": 25}):
            for node, diff in step_event.items():
                current_state.update(diff)

        # Append to chat history
        insights = current_state.get('insights', 'No insights generated.')
        code = current_state.get('generated_code', '')
        chart = current_state.get('figure_json', '')

        st.session_state.messages.append({
            "role": "assistant",
            "content": insights,
            "code": code,
            "chart": chart
        })

        st.rerun()


def _build_excel(messages: list) -> bytes:
    """Build a multi-sheet Excel workbook from session messages."""
    import openpyxl
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        query_num = 0
        i = 0
        while i < len(messages):
            msg = messages[i]
            if msg['role'] == 'user':
                query_num += 1
                sheet_name = f"Query {query_num}"[:31]  # Excel max sheet name length
                
                rows = [
                    {"Section": "User Query", "Content": msg['content']},
                ]
                
                if i + 1 < len(messages) and messages[i + 1]['role'] == 'assistant':
                    asst = messages[i + 1]
                    rows.append({"Section": "AI Insights", "Content": asst['content']})
                    if asst.get('code'):
                        rows.append({"Section": "Generated Code", "Content": asst['code']})
                    i += 2
                else:
                    i += 1
                    
                pd.DataFrame(rows).to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                i += 1
                
        # Summary sheet
        summary_rows = [
            {"Metric": "Total Queries", "Value": str(query_num)},
            {"Metric": "Total Messages", "Value": str(len(messages))},
        ]
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)
        
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    main()
