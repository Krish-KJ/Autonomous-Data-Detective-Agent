import sys
import io
import contextlib
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

# Import local functionality
from llm_router import invoke_llm
from safe_executor import execute_pandas_code

# ==========================================
# 1. DEFINE SHARED STATE (AgentState)
# ==========================================

class AgentState(TypedDict):
    """
    Shared state that gets passed from one LangGraph Node (Agent) to another.
    This acts as the memory for the autonomous execution flow.
    """
    query: str
    
    # Input CSV details
    df_columns: List[str]
    df_dtypes: Dict[str, str]
    df_head: str
    
    # Multi-CSV support
    available_dataframes: str  # Description of all available dataframes
    
    # Data quality context
    data_quality_report: str
    
    # Flow tracking
    plan: str
    generated_code: str
    execution_result: str
    execution_error: str
    retry_count: int
    
    # Final Outputs
    figure_json: str
    insights: str
    

# ==========================================
# 2. DEFINE LANGGRAPH NODE AGENTS
# ==========================================

def planner_agent(state: AgentState):
    """
    Node 1: Planner Agent
    Reads the dataset columns/dtypes, quality report, and user query.
    Outputs a structured, step-by-step plan for the coder to follow.
    """
    print('--- PLANNER AGENT RUNNING ---')
    
    quality_ctx = ""
    if state.get('data_quality_report'):
        quality_ctx = f"\n\nData Quality Report:\n{state['data_quality_report']}"
    
    multi_df_ctx = ""
    if state.get('available_dataframes'):
        multi_df_ctx = f"\n\nAvailable DataFrames:\n{state['available_dataframes']}"
    
    sys_msg = SystemMessage(content=f"""You are a Data Science Architect.
    Analyze the user's query and the provided DataFrame schema.
    Create a detailed, step-by-step plan for writing python pandas code to answer the query.
    Do NOT write code. ONLY output the conceptual numbered steps.
    
    Primary DataFrame Columns: {state['df_columns']}
    DataTypes: {state['df_dtypes']}
    Data Sample:\n{state['df_head']}{quality_ctx}{multi_df_ctx}
    """)
    hum_msg = HumanMessage(content=f"Query: {state['query']}")
    
    response, _ = invoke_llm([sys_msg, hum_msg], temperature=0.1)
    return {"plan": response}


def code_writer_agent(state: AgentState):
    """
    Node 2: Code Writer Agent
    Reads the Planner's plan and writes Pandas code.
    """
    print('--- CODE WRITER AGENT RUNNING ---')
    
    multi_df_ctx = ""
    if state.get('available_dataframes'):
        multi_df_ctx = f"\n\nMultiple DataFrames are available. {state['available_dataframes']}\nUse the variable names listed above to reference each DataFrame."
    
    sys_msg = SystemMessage(content=f"""You are a Senior Python Pandas Developer.
    Write python code following the user's execution plan.
    
    Rules:
    1. The primary dataset is loaded in a pandas variable named `df`. DO NOT WRITE pd.read_csv().
    2. Start directly with df manipulations.
    3. Use print() to output actual numeric or tabular answers so the user can see them!
    4. ONLY RETURN THE COMPLETE EXECUTABLE PYTHON CODE in a ```python ... ``` block. No explanation.
    5. `pd` (pandas) and `np` (numpy) are already imported.
    
    Primary DataFrame Columns: {state['df_columns']}
    DataTypes: {state['df_dtypes']}{multi_df_ctx}
    """)
    hum_msg = HumanMessage(content=f"Plan to follow:\n{state['plan']}")
    
    response, _ = invoke_llm([sys_msg, hum_msg], temperature=0.0)
    
    code = response
    if "```python" in response:
        code = response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        code = response.split("```")[1].split("```")[0].strip()
        
    return {"generated_code": code, "retry_count": 0}


def validator_agent(state: AgentState):
    """
    Node 3: Validator (Execution) Agent
    Uses the SafeExecutor to run `generated_code` against a global Pandas DataFrame.
    (Note: In a pure stateless environment, we must import the global df, but since this runs via Streamlit,
    we pass a placeholder dataframe reference if testing independently, or run securely via ast).
    """
    print('--- VALIDATOR AGENT RUNNING ---')
    code = state['generated_code']
    
    import streamlit as st
    target_df = st.session_state.get('current_df')
    dataframes = st.session_state.get('all_dataframes')
          
    # Execute securely with multi-df support
    res = execute_pandas_code(code, target_df, dataframes=dataframes)
    
    if res['success']:
        print("Execution Success:", res['output'])
        return {"execution_result": res['output'], "execution_error": None}
    else:
        print("Execution Failed:", res['error'])
        return {"execution_result": None, "execution_error": res['error']}


def error_fixer_agent(state: AgentState):
    """
    Node 4: Error Fixer Agent
    Triggered ONLY if validator_agent throws an execution_error.
    Reads the error trace and generated code, then returns corrected code.
    Maximum 3 retries handled via should_retry router.
    """
    print(f"--- ERROR FIXER AGENT RUNNING (Retry {state['retry_count'] + 1}) ---")
    sys_msg = SystemMessage(content="""You are a Python Debugging Expert.
    The previous pandas code generated an error.
    Read the Error Message and the faulty Code, then output the fully corrected Code.
    ONLY output Python code inside ```python ``` blocks.
    """)
    
    hum_msg = HumanMessage(content=f"""
    Faulty Code:
    {state['generated_code']}
    
    Error Trace:
    {state['execution_error']}
    """)
    
    response, _ = invoke_llm([sys_msg, hum_msg], temperature=0.0)
    
    # Extract corrected code
    code = response
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
        
    return {"generated_code": code, "retry_count": state['retry_count'] + 1}


def visualizer_agent(state: AgentState):
    """
    Node 5: Visualizer Agent
    Takes the successful dataframe and query, generates Plotly python code,
    executes it locally (safely), and returns the JSON serialization of the figure.
    """
    print('--- VISUALIZER AGENT RUNNING ---')
    sys_msg = SystemMessage(content=f"""You are a Plotly visualization expert who creates clean, colorful charts.
    Write python code using plotly.express (px) to chart the answer to the user query.
    
    Rules:
    1. df is already provided.
    2. Write clean code.
    3. ASSIGN THE FINAL FIGURE TO A VARIABLE NAMED `fig`.
    4. NO plt.show() or fig.show(), just assign it to `fig`.
    5. Output ONLY the python code in ```python ... ``` block.
    6. Do NOT set any template. Let the default theme apply.
    7. Use vibrant, visible colors. For scatter plots, ensure markers are large enough (size=8 minimum).
    8. Add a descriptive title using title= parameter.
    9. Use fig.update_layout() to add proper axis labels and clean margins.
    10. For bar charts, use the color parameter for variety when possible.
    
    Columns: {state['df_columns']}
    Query: {state['query']}
    """)
    hum_msg = HumanMessage(content="Create a chart for this.")
    
    response, _ = invoke_llm([sys_msg, hum_msg], temperature=0.0)
    
    plotly_code = response
    if "```python" in response:
        plotly_code = response.split("```python")[1].split("```")[0].strip()
        
    # Execute the plotly code to get the fig object
    import streamlit as st
    restricted_globals = {'df': st.session_state.get('current_df'), 'fig': None}
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        restricted_globals['px'] = px
        restricted_globals['go'] = go
        
        exec(plotly_code, restricted_globals)
        fig = restricted_globals.get('fig')
        
        if fig:
            # Clean up chart styling without overriding backgrounds
            fig.update_layout(
                font=dict(family='Helvetica, Arial, sans-serif', size=12),
                title_font_size=16,
                margin=dict(l=50, r=30, t=60, b=50)
            )
            fig_json = fig.to_json()
        else:
            fig_json = None
            
    except Exception as e:
        print("Plotly Gen Error:", str(e))
        fig_json = None
        
    return {"figure_json": fig_json}


def insight_generator_agent(state: AgentState):
    """
    Node 6: Insight Generator Agent
    Reads the `execution_result` (the print outputs from successful code).
    Summarizes it into bullet points for the user.
    """
    print('--- INSIGHT GENERATOR RUNNING ---')
    # If the code failed entirely (hit max retries), handle elegantly
    if state.get('execution_error'):
        return {"insights": "The agents were unable to automatically resolve the code error after maximum retries. Please check the 'Code' tab for the error detail and try rephrasing your query."}
        
    sys_msg = SystemMessage(content="""You are a Senior Data Analyst presenting findings to stakeholders.
    Read the output logs generated by data scripts and the original user query.
    
    Structure your response EXACTLY like this using markdown:
    
    ### Key Findings
    - **Finding 1 title:** Detailed explanation with specific numbers from the data.
    - **Finding 2 title:** Another insight with concrete values.
    - **Finding 3 title:** Additional observation with data-backed evidence.
    
    ### Summary
    A 2-3 sentence executive summary tying all findings together. Include any notable trends, outliers, or actionable takeaways.
    
    Rules:
    1. Always reference SPECIFIC numbers, percentages, or values from the data output.
    2. Do NOT explain HOW you got the answer, only WHAT the data reveals.
    3. Use professional, analytical language suitable for a business report.
    4. If there are notable patterns or outliers, highlight them explicitly.
    """)
    hum_msg = HumanMessage(content=f"User Query: {state['query']}\n\nData Output:\n{state['execution_result']}")
    
    response, _ = invoke_llm([sys_msg, hum_msg], temperature=0.7)
    
    return {"insights": response}


# ==========================================
# 3. DEFINE CONDITIONAL ROUTING EDGE
# ==========================================
def should_retry(state: AgentState):
    """
    Checks if execution threw an error.
    If yes, go to error_fixer_agent.
    If yes AND retry_count >= 2, degradation (skip to insight generator).
    If no error, go to visualizer.
    """
    error = state.get('execution_error')
    retries = state.get('retry_count', 0)
    
    if error:
        if retries >= 3:
            print(f"MAX RETRIES ({retries}) REACHED! ABORTING FIX LOOP.")
            return "max_retries_reached"
        else:
            return "fix_error"
    else:
        return "success"


# ==========================================
# 4. BUILD THE GRAPH
# ==========================================
def build_graph():
    """
    Compiles the directed StateGraph.
    
    ASCII Flow Diagram:
    
    [START] --> planner_agent
                   |
                   v
              code_writer_agent
                   |
                   v
    +-------> validator_agent ------+
    |              |                |
    | (fix_error)  |                |
    +---- error_fixer_agent         | (success)
                                    |
                            visualizer_agent
                                    |
                                    v
                          insight_generator_agent --> [END]
                          
    * Note: If validator hits max_retries, it skips to insight_generator_agent.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("planner", planner_agent)
    workflow.add_node("coder", code_writer_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("fixer", error_fixer_agent)
    workflow.add_node("visualizer", visualizer_agent)
    workflow.add_node("insights", insight_generator_agent)
    
    # Add Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "validator")
    
    # Conditional edge from Validator
    workflow.add_conditional_edges(
        "validator",
        should_retry,
        {
            "fix_error": "fixer",
            "success": "visualizer",
            "max_retries_reached": "insights" # Graceful degradation
        }
    )
    
    # Fixer feeds back into Validator
    workflow.add_edge("fixer", "validator")
    
    # Visualizer flows to Insights
    workflow.add_edge("visualizer", "insights")
    
    # End
    workflow.add_edge("insights", END)
    
    return workflow.compile()
