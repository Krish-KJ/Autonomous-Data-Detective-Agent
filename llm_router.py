import os
import time
import streamlit as st
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import requests


def _track_usage(provider: str, input_msgs, output_text: str):
    """Track LLM usage in Streamlit session state for the cost tracker."""
    if 'llm_usage' not in st.session_state:
        st.session_state.llm_usage = []
    
    # Estimate tokens (rough heuristic: ~4 chars per token)
    input_text = " ".join([m.content for m in input_msgs if hasattr(m, 'content')])
    input_tokens = len(input_text) // 4
    output_tokens = len(output_text) // 4
    
    st.session_state.llm_usage.append({
        'provider': provider,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'timestamp': time.time()
    })


def get_api_key(key_name):
    """
    Retrieves API key from Streamlit secrets or OS environment.
    Cloud deployments use st.secrets; local runs use .env file.
    """
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    return os.environ.get(key_name, "")


def invoke_llm(messages, temperature=0.0):
    """
    Multi-provider LLM fallback system.
    Tries 3 Groq keys sequentially -> Google Gemini -> OpenRouter
    Returns tuple: (response_string, provider_name)
    """
    # 1. TIER 1 - PRIMARY: Groq (llama-3.1-8b-instant)
    groq_keys = [
        get_api_key("GROQ_API_KEY_1"),
        get_api_key("GROQ_API_KEY_2"),
        get_api_key("GROQ_API_KEY_3"),
        get_api_key("GROQ_API_KEY_4")
    ]
    
    for i, key in enumerate(groq_keys):
        if not key:
            continue
            
        try:
            print(f"Attempting Groq Engine with Key {i+1}...")
            
            llm = ChatGroq(
                api_key=key,
                model="llama-3.1-8b-instant",
                temperature=temperature,
                max_retries=1
            )
            response = llm.invoke(messages)
            provider = f"Groq (Key {i+1}) - llama-3.1-8b-instant"
            _track_usage(provider, messages, response.content)
            return response.content, provider
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Groq Key {i+1} failed: {error_msg}")
            
            if "rate limit" in error_msg or "429" in error_msg:
                print("Rate limit hit. Rotating to next Groq key...")
                continue
            elif "connection" in error_msg:
                print("Connection error. Waiting 2 seconds before rotating...")
                time.sleep(2)
                continue
            else:
                continue
    
    # 2. TIER 2 - SECONDARY FALLBACK: Gemini (gemini-1.5-flash)
    gemini_keys = [
        get_api_key("GEMINI_API_KEY_1"),
        get_api_key("GEMINI_API_KEY_2")
    ]
    
    for i, key in enumerate(gemini_keys):
        if not key:
            continue
            
        try:
            print(f"Falling back to TIER 2: Google Gemini 1.5 Flash (Key {i+1})...")
            llm = ChatGoogleGenerativeAI(
                google_api_key=key,
                model="gemini-1.5-flash",
                temperature=temperature,
                max_retries=1
            )
            response = llm.invoke(messages)
            provider = f"Gemini (Key {i+1}) - gemini-1.5-flash"
            _track_usage(provider, messages, response.content)
            return response.content, provider
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Gemini Key {i+1} failed: {error_msg}")
            if "rate limit" in error_msg or "429" in error_msg:
                 print("Gemini rate limited. Attempting next key if available...")
                 continue
            elif "connection" in error_msg:
                 time.sleep(2)
                 continue
            else:
                 continue
            
    # 3. TIER 3 - LAST RESORT: OpenRouter (meta-llama/llama-3.1-8b-instruct:free)
    openrouter_keys = [
        get_api_key("OPENROUTER_API_KEY_1"),
        get_api_key("OPENROUTER_API_KEY_2"),
        get_api_key("OPENROUTER_API_KEY_3"),
        get_api_key("OPENROUTER_API_KEY_4")
    ]
    
    for i, key in enumerate(openrouter_keys):
        if not key:
            continue
            
        try:
            print(f"Falling back to TIER 3: OpenRouter Llama 3.1 8B Free (Key {i+1})...")
            llm = ChatOpenAI(
                api_key=key,
                base_url="https://openrouter.ai/api/v1",
                model="meta-llama/llama-3.1-8b-instruct:free",
                temperature=temperature,
                max_retries=1,
                default_headers={
                    "HTTP-Referer": "https://github.com/sk191/Autonomous_Data_Detective", 
                    "X-Title": "Autonomous Data Detective Agent",
                }
            )
            response = llm.invoke(messages)
            provider = f"OpenRouter (Key {i+1}) - llama-3.1-8b-free"
            _track_usage(provider, messages, response.content)
            return response.content, provider
            
        except Exception as e:
            print(f"OpenRouter Key {i+1} failed: {str(e)}")
            continue

    # 4. Total Failure State
    print("ALL API PROVIDERS FAILED.")
    return "Error: All AI providers (Groq, Gemini, OpenRouter) are either rate-limited, unreachable, or missing/invalid API keys. Please update your API keys in the .env file.", "None — Offline"
