import streamlit as st
import os
from openai import OpenAI

# Page setup
st.set_page_config(
    page_title="CogniCore",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 CogniCore — All AIs in One")
st.caption("Powered by Grok + specialist pods | Made for Pratham in Mumbai")

# Sidebar API keys
with st.sidebar:
    st.header("🔑 API Keys")
    xai_key = st.text_input(
        "xAI API Key (required)",
        type="password",
        value=os.getenv("XAI_API_KEY", "")
    )
    openai_key = st.text_input(
        "OpenAI Key (optional — for images)",
        type="password",
        value=os.getenv("OPENAI_API_KEY", "")
    )
    st.info("Get xAI key: https://console.x.ai → sign in → API Keys → Create new key")

# Stop if no key
if not xai_key:
    st.error("Enter your xAI API key in the sidebar to start.")
    st.stop()

# Clients
grok_client = OpenAI(
    api_key=xai_key,
    base_url="https://api.x.ai/v1"
)

if openai_key:
    dalle_client = OpenAI(api_key=openai_key)

# Pods (specialists)
specialist_prompts = {
    "general": "You are CogniCore General — mix of ChatGPT, Claude, Gemini, Grok. Be helpful, fun, truthful.",
    "writing": "You are CogniCore Writing expert — Jasper + Claude + Sudowrite level. Perfect copy, stories, posts.",
    "coding": "You are CogniCore Coding boss — Copilot + Cursor level. Write/debug/explain any code.",
    "image": "You are CogniCore Image Pod — Midjourney + DALL-E. Output ONLY <prompt>perfect prompt here</prompt> first, then describe.",
    "research": "You are CogniCore Research — Elicit + Scite level. Summarize, cite, evidence-based.",
    "other": "You are CogniCore — pick best approach and answer."
}

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask CogniCore anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Router classify
    with st.spinner("Routing to pod..."):
        try:
            router_response = grok_client.chat.completions.create(
                model="grok-4.20-non-reasoning",
                messages=[{"role": "user", "content": f"Classify ONE word: general, writing, coding, image, research, other.\nQuery: {prompt}"}],
                max_tokens=10
            )
            category = router_response.choices[0].message.content.strip().lower()
        except Exception as e:
            st.error(f"Router failed: {str(e)}\nTry different model or check key.")
            category = "general"

    if category not in specialist_prompts:
        category = "other"

    system_prompt = specialist_prompts[category]
    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # Main response (no streaming)
    with st.chat_message("assistant"):
        with st.spinner(f"{category.upper()} Pod..."):
            try:
                response = grok_client.chat.completions.create(
                    model="grok-4.20-non-reasoning",
                    messages=full_messages,
                    stream=False
                )
                full_response = response.choices[0].message.content
                st.markdown(full_response)
            except Exception as e:
                st.error(f"Error: {str(e)}\n\nPossible fixes:\n- Wrong model name? Try 'grok-4.20-reasoning' or 'grok-4-1-fast-non-reasoning'\n- Invalid/expired key? Get new one at console.x.ai")

    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.caption("CogniCore v0.3 • Model: grok-4.20-non-reasoning • Fixed March 2026")
