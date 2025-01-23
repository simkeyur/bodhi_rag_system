import logging
import os

import streamlit as st

from src.chat import (  # type: ignore
    ensure_model_pulled,
    generate_response_streaming,
    get_embedding_model,
)
from src.ingestion import create_index, get_opensearch_client
from src.constants import OLLAMA_MODEL_NAME, OPENSEARCH_INDEX
from src.utils import setup_logging

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(page_title="Bodhi - Chatbot", page_icon="🤖")

# Apply Material Design-inspired CSS
st.markdown(
    """
    <style>
    /* Material Design Colors and Styling */
    body { background-color: #fafafa; color: #212121; font-family: 'Roboto', sans-serif; }
    .sidebar .sidebar-content { background-color: #004d40; color: white; padding: 20px; border-right: 1px solid #00332e; }
    .sidebar h2, .sidebar h4 { color: white; margin: 10px 0; }
    .block-container { background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .footer-text { font-size: 0.9rem; font-weight: 500; color: #616161; text-align: center; margin-top: 20px; }
    .stButton button { background-color: #00796b; color: white; border: none; border-radius: 4px; padding: 10px 16px; font-size: 14px; cursor: pointer; }
    .stButton button:hover { background-color: #004d40; color: white; }
    h1, h2, h3, h4 { color: #004d40; }
    .stChatMessage { background-color: #e0f2f1; color: #004d40; padding: 10px; border-radius: 6px; margin-bottom: 12px; }
    .stChatMessage.user { background-color: #004d40; color: white; }
    .sidebar .logo-container { text-align: center; margin-bottom: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)
logger.info("Custom CSS applied.")

# Main chatbot page rendering function
def render_chatbot_page() -> None:
    st.title("Bodhi - Chatbot 🤖")
    model_loading_placeholder = st.empty()

    if "use_hybrid_search" not in st.session_state:
        st.session_state["use_hybrid_search"] = True
    if "num_results" not in st.session_state:
        st.session_state["num_results"] = 5
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = 0.7

    with st.spinner("Connecting to OpenSearch..."):
        client = get_opensearch_client()
    index_name = OPENSEARCH_INDEX

    create_index(client)

    st.sidebar.markdown("<div class='logo-container'><h2>Bodhi</h2></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<h4>Interactive AI at Your Service</h4>", unsafe_allow_html=True)
    st.sidebar.checkbox(
        "Enable RAG mode", value=st.session_state["use_hybrid_search"]
    )
    st.sidebar.number_input(
        "Results in Context Window", 1, 10, st.session_state["num_results"], 1
    )
    st.sidebar.slider(
        "Response Temperature", 0.0, 1.0, st.session_state["temperature"], 0.1
    )
    st.sidebar.markdown("<div class='footer-text'>© 2025 Bodhi</div>", unsafe_allow_html=True)

    with model_loading_placeholder.container():
        st.spinner("Loading models...")

    if "embedding_models_loaded" not in st.session_state:
        with model_loading_placeholder:
            with st.spinner("Loading models..."):
                get_embedding_model()
                ensure_model_pulled(OLLAMA_MODEL_NAME)
                st.session_state["embedding_models_loaded"] = True
        model_loading_placeholder.empty()

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response_placeholder = st.empty()
                response_text = ""

                response_stream = generate_response_streaming(
                    prompt,
                    use_hybrid_search=st.session_state["use_hybrid_search"],
                    num_results=st.session_state["num_results"],
                    temperature=st.session_state["temperature"],
                    chat_history=st.session_state["chat_history"],
                )

                if response_stream is not None:
                    for chunk in response_stream:
                        if (
                            isinstance(chunk, dict)
                            and "message" in chunk
                            and "content" in chunk["message"]
                        ):
                            response_text += chunk["message"]["content"]
                            response_placeholder.markdown(response_text + "▌")
                        else:
                            logger.error("Unexpected chunk format.")

                response_placeholder.markdown(response_text)
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": response_text}
                )


if __name__ == "__main__":
    render_chatbot_page()
