import streamlit as st
import os
from openai import OpenAI

# Page config
st.set_page_config(
    page_title="CogniCore",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 CogniCore — All AIs in One")
st.caption("Powered by Grok + specialist pods | Made for Pratham in Mumbai")

# Sidebar for API keys
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
    st.info("Get free xAI key at: https://console.x.ai")

# Stop if no xAI key
if not xai_key:
    st.error("Please enter your xAI API key in the sidebar to continue.")
    st.stop()

# Create clients
grok_client = OpenAI(
    api_key=xai_key,
    base_url="https://api.x.ai/v1"
)

if openai_key:
    dalle_client = OpenAI(api_key=openai_key)

# Specialist pods (simple classification)
specialist_prompts = {
    "general": "You are CogniCore General — a helpful mix of ChatGPT, Claude, Gemini, and Grok. Be friendly, truthful, and fun.",
    "writing": "You are CogniCore Writing expert — like Jasper, Copy.ai, Claude, Sudowrite. Write marketing, blogs, stories, anything perfectly.",
    "coding": "You are CogniCore Coding boss — GitHub Copilot + Cursor level. Write, debug, explain code in any language.",
    "image": "You are CogniCore Image Pod — Midjourney + DALL-E style. First output ONLY the perfect prompt inside <prompt>perfect prompt here</prompt> tags, then describe the image you would create.",
    "research": "You are CogniCore Research Pod — like Elicit, Scite, Consensus. Summarize papers, give evidence-based answers, cite when possible.",
    "other": "You are CogniCore — choose the best way to answer and respond accordingly."
}

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask CogniCore anything..."):
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Router: classify which pod
    with st.spinner("Routing to the best pod..."):
        router_response = grok_client.chat.completions.create(
            model="grok-2-latest",  # ← change to whatever model your console shows if this fails
            messages=[
                {"role": "user", "content": f"Classify this query into ONE word only: general, writing, coding, image, research, other.\nQuery: {prompt}"}
            ],
            max_tokens=10
        )
        category = router_response.choices[0].message.content.strip().lower()

    if category not in specialist_prompts:
        category = "other"

    # Build full messages with system prompt
    system_prompt = specialist_prompts[category]
    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # Get response (no streaming → clean output)
    with st.chat_message("assistant"):
        with st.spinner(f"CogniCore {category.upper()} Pod activated..."):
            try:
                response = grok_client.chat.completions.create(
                    model="grok-2-latest",
                    messages=full_messages,
                    stream=False
                )
                full_response = response.choices[0].message.content
                st.markdown(full_response)
            except Exception as e:
                st.error(f"Oops! Something went wrong: {str(e)}\n\nCheck your API key or try a different model name.")

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.caption("CogniCore v0.2 • Simple & clean version • Fixed for Streamlit Cloud")
