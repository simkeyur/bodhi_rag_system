import logging
import os

import streamlit as st

from src.utils import setup_logging

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Bodhi - Your Conversational Platform",
    page_icon="🤖"
)

# Material Design-inspired CSS
def apply_custom_css() -> None:
    """Applies Material Design-inspired CSS styling to the page."""
    st.markdown(
        """
        <style>
        /* Material Design-inspired styles */
        body {
            background-color: #fafafa; /* Light grey background */
            color: #212121; /* Dark grey text */
            font-family: 'Roboto', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #004d40; /* Dark teal for sidebar */
            color: white;
            padding: 20px;
            border-right: 1px solid #00332e; /* Subtle border for sidebar */
        }
        .sidebar h2, .sidebar h4 {
            color: white; /* White text for sidebar headers */
            margin: 10px 0;
        }
        .block-container {
            background-color: white; /* White background for content */
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); /* Elevated look */
        }
        /* Center and style footer text */
        .footer-text {
            font-size: 0.9rem;
            font-weight: 500;
            color: #757575; /* Subtle grey */
            text-align: center;
            margin-top: 20px;
        }
        /* Modern button styling */
        .stButton button {
            background-color: #00796b; /* Teal color */
            color: white;
            border-radius: 4px;
            padding: 10px 16px;
            font-size: 14px;
            border: none;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* Subtle shadow */
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #004d40; /* Darker teal on hover */
            color: white;
        }
        h1, h2, h3, h4 {
            color: #004d40; /* Consistent teal headings */
        }
        /* Link styles */
        a {
            color: #00796b;
            text-decoration: none;
        }
        a:hover {
            color: #004d40;
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    logger.info("Applied Material Design-inspired CSS styling.")

# Function to display logo or placeholder
def display_logo(logo_path: str) -> None:
    """Displays the logo in the sidebar or a placeholder if not found."""
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=220)
        logger.info("Logo displayed.")
    else:
        st.sidebar.markdown("### Logo Placeholder")
        logger.warning("Logo not found, displaying placeholder.")

# Function to display main content
def display_main_content() -> None:
    """Renders the primary content of the application."""
    st.title("Bodhi Document Assistant 📄🤖")
    st.markdown(
        """
        Welcome to the Intelligent Document Assistant platform.
        
        This application leverages advanced AI technology to assist with document management and retrieval. Users can seamlessly interact with the AI assistant or upload documents for efficient processing and information extraction.
        
        **Key Features:**
        - **Conversational AI**: Engage in a dynamic and intelligent conversation powered by the latest Large Language Models (LLMs).
        - **Document Management**: Upload PDF documents, and retrieve insights using a robust Hybrid RAG System powered by OpenSearch.
        
        **Please select a feature from the sidebar to get started.**
        """,
        unsafe_allow_html=True,
    )
    logger.info("Main content successfully rendered.")


# Function to display sidebar content
def display_sidebar_content() -> None:
    """Displays headers and footer content in the sidebar."""
    st.sidebar.markdown(
        "<h2 style='text-align: center;'>Bodhi</h2>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<h4 style='text-align: center;'>Your Conversational Platform</h4>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        """
        <div class="footer-text">
            © 2025 Bodhi
        </div>
        """,
        unsafe_allow_html=True,
    )
    logger.info("Displayed sidebar content.")

# Main execution
if __name__ == "__main__":
    apply_custom_css()
    display_logo("images/bodhi-logo.png")
    display_sidebar_content()
    display_main_content()
