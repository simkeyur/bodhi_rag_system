import logging
import os
import time

import streamlit as st
from PyPDF2 import PdfReader

from src.constants import OPENSEARCH_INDEX, TEXT_CHUNK_SIZE
from src.embeddings import generate_embeddings, get_embedding_model
from src.ingestion import (
    bulk_index_documents,
    create_index,
    delete_documents_by_document_name,
)
from src.opensearch import get_opensearch_client
from src.utils import chunk_text, setup_logging

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="Bodhi - Upload Documents", page_icon="📂")

# Apply Material Design-inspired CSS
st.markdown(
    """
    <style>
    /* Material Design-inspired styles */
    body { background-color: #fafafa; color: #212121; font-family: 'Roboto', sans-serif; }
    .sidebar .sidebar-content { background-color: #004d40; color: white; padding: 20px; border-right: 1px solid #00332e; }
    .sidebar h2, .sidebar h4 { color: white; margin: 10px 0; }
    .block-container { background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .footer-text { font-size: 0.9rem; font-weight: 500; color: #616161; text-align: center; margin-top: 20px; }
    .stButton button { background-color: #00796b; color: white; border: none; border-radius: 4px; padding: 10px 16px; font-size: 14px; cursor: pointer; }
    .stButton button:hover { background-color: #004d40; color: white; }
    .stButton.delete-button button { background-color: #d32f2f; color: white; font-size: 14px; border: none; }
    .stButton.delete-button button:hover { background-color: #b71c1c; }
    h1, h2, h3, h4 { color: #004d40; }
    .uploaded-doc-card { background-color: #e0f2f1; color: #004d40; border-radius: 6px; padding: 15px; margin-bottom: 12px; }
    .uploaded-doc-card:hover { box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add logo or placeholder
logo_path = "images/bodhi-logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=220)
else:
    st.sidebar.markdown("### Logo Placeholder")
    logger.warning("Logo not found, displaying placeholder.")

# Sidebar header
st.sidebar.markdown("<h2 style='text-align: center;'>Bodhi</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<h4 style='text-align: center;'>Your Document Assistant</h4>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown(
    "<div class='footer-text'>© 2025 Bodhi</div>",
    unsafe_allow_html=True,
)


def render_upload_page() -> None:
    st.title("Upload Documents 📂")

    # Placeholder for the loading spinner
    model_loading_placeholder = st.empty()

    # Load the embedding model if not already loaded
    if "embedding_models_loaded" not in st.session_state:
        with model_loading_placeholder:
            with st.spinner("Loading models for document processing..."):
                get_embedding_model()
                st.session_state["embedding_models_loaded"] = True
        model_loading_placeholder.empty()

    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # OpenSearch client and index setup
    with st.spinner("Connecting to OpenSearch..."):
        client = get_opensearch_client()
    create_index(client)

    # Query for existing documents
    query = {
        "size": 0,
        "aggs": {"unique_docs": {"terms": {"field": "document_name", "size": 10000}}},
    }
    response = client.search(index=OPENSEARCH_INDEX, body=query)
    document_names = [bucket["key"] for bucket in response["aggregations"]["unique_docs"]["buckets"]]

    # Upload files section
    uploaded_files = st.file_uploader(
        "Upload PDF documents", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Uploading and processing documents..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name in document_names:
                    st.warning(f"'{uploaded_file.name}' already exists in the index.")
                    continue

                file_path = save_uploaded_file(uploaded_file)
                reader = PdfReader(file_path)
                text = "".join([page.extract_text() for page in reader.pages])
                chunks = chunk_text(text, TEXT_CHUNK_SIZE, overlap=100)
                embeddings = generate_embeddings(chunks)

                documents_to_index = [
                    {
                        "doc_id": f"{uploaded_file.name}_{i}",
                        "text": chunk,
                        "embedding": embedding,
                        "document_name": uploaded_file.name,
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
                bulk_index_documents(documents_to_index)
                document_names.append(uploaded_file.name)

        st.success("Files uploaded and indexed successfully!")

    # Display uploaded documents
    if document_names:
        st.markdown("### Uploaded Documents")
        for idx, doc_name in enumerate(document_names, 1):
            with st.container():
                st.markdown(
                    f"<div class='uploaded-doc-card'><strong>{idx}. {doc_name}</strong></div>",
                    unsafe_allow_html=True,
                )


def save_uploaded_file(uploaded_file) -> str:
    """Save the uploaded file locally."""
    file_path = os.path.join("uploaded_files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"File saved: {file_path}")
    return file_path


if __name__ == "__main__":
    render_upload_page()
