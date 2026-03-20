import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="CogniCore", page_icon="🧠", layout="wide")
st.title("🧠 CogniCore — All AIs in One")
st.caption("Powered by Grok + specialist pods | Made for Pratham in Mumbai")

with st.sidebar:
    st.header("🔑 API Keys")
    xai_key = st.text_input("xAI API Key (required)", type="password", value=os.getenv("XAI_API_KEY", ""))
    openai_key = st.text_input("OpenAI Key (optional — for images)", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    st.info("Get free xAI key → console.x.ai")

if not xai_key:
    st.error("Please put your xAI key in the sidebar")
    st.stop()

grok_client = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")

if openai_key:
    dalle_client = OpenAI(api_key=openai_key)

specialist_prompts = {
    "general": "You are CogniCore General — mix of ChatGPT, Claude, Gemini, Grok. Be helpful and fun.",
    "writing": "You are CogniCore Writing expert — like Jasper + Claude + Sudowrite. Write anything perfectly.",
    "coding": "You are CogniCore Coding boss — like GitHub Copilot + Cursor. Write and fix code.",
    "image": "You are CogniCore Image maker — like Midjourney + DALL-E. First give <prompt>perfect prompt</prompt>, then describe.",
    "research": "You are CogniCore Research — like Elicit + Scite. Summarize smart papers.",
    "other": "You are CogniCore — choose best way and answer."
}

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask CogniCore anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking which pod..."):
        router_response = grok_client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": f"Classify in ONE word only: general, writing, coding, image, research, other. Query: {prompt}"}],
            max_tokens=10
        )
        category = router_response.choices[0].message.content.strip().lower()

    if category not in specialist_prompts:
        category = "other"

    system_prompt = specialist_prompts[category]
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        with st.spinner(f"CogniCore {category.upper()} is here..."):
     response = grok_client.chat.completions.create(
        model="grok-beta",
        messages=messages,
        stream=False
    )
full_response = response.choices[0].message.content
st.markdown(full_response)
            full_response = ""
            placeholder = st.empty()
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
