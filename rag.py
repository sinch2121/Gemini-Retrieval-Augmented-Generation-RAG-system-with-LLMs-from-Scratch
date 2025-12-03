import streamlit as st
import os
import io
from typing import Optional
from io import BytesIO
from google import genai
from google.genai.errors import APIError

from dotenv import load_dotenv
import os

load_dotenv()

print("API key loaded:", os.getenv("GOOGLE_API_KEY") is not None)


# -------- Document Parsing Section --------

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# Extract text from different document types
def read_document_content(uploaded_file):
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    try:
        # TXT / MD
        if file_extension in ['.txt', '.md']:
            return uploaded_file.getvalue().decode("utf-8")

        # PDF
        elif file_extension == '.pdf':
            if not PdfReader:
                return "Error: Cannot read PDF. Please install pypdf."

            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        # DOCX
        elif file_extension == '.docx':
            if not Document:
                return "Error: Cannot read DOCX. Please install python-docx."

            doc = Document(BytesIO(uploaded_file.getvalue()))
            text = "\n".join([p.text for p in doc.paragraphs])
            return text

        else:
            return f"Error: Unsupported file type: {file_extension}"

    except Exception as e:
        return f"Error reading file content: {e}"


# -------- Gemini API Handler --------

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"


class GeminiAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list, system_instruction: str) -> str:
        try:
            client = genai.Client(api_key=self.api_key)
            config = genai.types.GenerateContentConfig(system_instruction=system_instruction)

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            return response.text

        except APIError as e:
            return f"Error during live API call: A Gemini API error occurred. Details: {e}"

        except Exception as e:
            return f"Error during live API call: An unexpected error occurred. Details: {e}"


# -------- Streamlit UI --------

st.set_page_config(page_title="Gemini RAG Workshop", layout="wide")
st.title("First RAG System: Contextual Q&A with Gemini")

st.markdown("""
This application demonstrates the core concept of **Retrieval-Augmented Generation (RAG)**.
The LLM (Gemini) is forced to answer your questions *only* by referencing the document you provide.
Supported file types: `.txt`, `.md`, `.pdf`, `.docx`.
""")

# Session States
if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = ""

if 'rag_response' not in st.session_state:
    st.session_state.rag_response = {}

if 'user_prompt_input' not in st.session_state:
    st.session_state.user_prompt_input = ""

# Upload Document
uploaded_file = st.file_uploader(
    "1. Upload your data source",
    type=['txt', 'md', 'pdf', 'docx'],
    help="Upload a document that Gemini must reference."
)

if uploaded_file is not None:
    file_contents = read_document_content(uploaded_file)

    if file_contents.startswith("Error:"):
        st.error(file_contents)
        st.session_state.uploaded_text = ""
    else:
        st.session_state.uploaded_text = file_contents
        st.success(f"File '{uploaded_file.name}' loaded successfully ({len(file_contents)} characters)")

        with st.expander("Review Extracted Document Text"):
            display_text = file_contents[:2000] + (
                '\n[...Truncated for display...]' if len(file_contents) > 2000 else ''
            )
            st.code(display_text, language='text')

if not st.session_state.uploaded_text:
    st.info("Please upload a supported file to enable the Q&A section.")
    st.stop()

# User question section
st.subheader("2. Ask a Question Grounded in the Document")

st.text_area(
    "Enter your question:",
    placeholder="e.g., What is the main purpose of the first paragraph?",
    height=100,
    key='user_prompt_input'
)

gemini_api = GeminiAPI(api_key=API_KEY)


def run_rag_query():
    current_prompt = st.session_state.get('user_prompt_input', '').strip()

    if not current_prompt:
        st.error("Please enter a question.")
        return

    st.session_state.rag_response = {"prompt": current_prompt, "answer": None}

    with st.spinner(f"Generating grounded answer for: '{current_prompt[:50]}...'"):

        system_instruction = (
            "You are an expert Q&A system. Extract or summarize information strictly from the document. "
            "DO NOT use external knowledge. If the answer is not present, reply with: "
            "'I cannot find the answer in the provided document.'"
        )

        contents_payload = [
            {"parts": [{"text": st.session_state.uploaded_text}]},
            {"parts": [{"text": current_prompt}]}
        ]

        response_text = gemini_api.generate_content(
            model=MODEL_NAME,
            contents=contents_payload,
            system_instruction=system_instruction
        )

        st.session_state.rag_response["answer"] = response_text


# Button
st.button("3. Get Grounded Answer", on_click=run_rag_query, type="primary")

# Output section
st.subheader("RAG Response")

if st.session_state.get("rag_response") and st.session_state["rag_response"].get("answer"):
    st.markdown("---")
    st.markdown(f"**Question Asked:** {st.session_state['rag_response']['prompt']}")
    st.markdown(st.session_state["rag_response"]["answer"])
    st.markdown("---")
else:
    st.info("Your answer will appear here after clicking the button.")

st.caption("The RAG system works by injecting your document and question into a structured prompt.")
