"""
utils/ai.py — Jitarth AI se baat karo
Streamlit app API call karke reply laata hai.
"""
import streamlit as st
import requests


def send_to_ai(question: str) -> str:
    """
    Jitarth AI Streamlit app pe request bhejo.
    Response text return karo.
    
    Note: Streamlit apps public API expose nahi karte by default.
    Is function mein 2 approaches hain:
      1. Agar tera AI REST endpoint deta hai → direct call
      2. Fallback: Claude API se reply (Anthropic key se)
    """

    # ── Approach 1: Tera Streamlit AI ka REST/API endpoint ──────────────────
    # Agar https://jitarth-ai.streamlit.app pe koi /api ya ?query= endpoint ho
    ai_url = st.secrets.get("JITARTH_AI_URL", "https://jitarth-ai.streamlit.app")
    api_endpoint = st.secrets.get("JITARTH_AI_API", "")

    if api_endpoint:
        try:
            resp = requests.post(
                api_endpoint,
                json={"question": question, "query": question},
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            if resp.status_code == 200:
                data = resp.json()
                # Common response keys try karo
                for key in ["answer", "response", "reply", "output", "result", "text"]:
                    if key in data:
                        return str(data[key])
                return str(data)
        except Exception as e:
            pass  # Fallback to next approach

    # ── Approach 2: Anthropic Claude API (fallback) ──────────────────────────
    anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": question}]
                },
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["content"][0]["text"]
        except Exception as e:
            return f"❌ AI se connect nahi ho paaya: {e}"

    # ── No API configured ────────────────────────────────────────────────────
    return (
        f"🔧 AI connected nahi hai abhi. "
        f"secrets.toml mein JITARTH_AI_API ya ANTHROPIC_API_KEY daalo.\n\n"
        f"Tumhara sawaal tha: *{question}*"
    )
