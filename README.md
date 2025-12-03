# Gemini-Retrieval-Augmented-Generation-RAG-system-with-LLMs-from-Scratch
This project implements a Retrieval-Augmented Generation (RAG) system using Google’s Gemini LLMs. The system allows users to upload documents (.txt, .md, .pdf, .docx) and ask questions grounded strictly in the content of the uploaded documents. The model generates answers based solely on the provided context, ensuring reliable and document-specific responses.

Key features include:

1. Multi-format document parsing – supports plain text, Markdown, PDF, and Word documents.

2. LLM-powered Q&A – integrates Google Gemini API to generate responses grounded in the uploaded content.

3. Streamlit-based interactive UI – easy-to-use web interface with sections for uploading documents, reviewing extracted text, and asking questions.

4. Error handling – provides clear messages if files are unsupported or API calls fail.

5. Session state management – stores uploaded content and responses for smooth user interaction.

This project demonstrates a practical application of RAG systems with large language models, ideal for building knowledge assistants, document-specific chatbots, and research tools.

Tech Stack & Libraries

1. Python

2. Streamlit – frontend interface

3. Google Gemini API – LLM backend

4. pypdf – PDF text extraction

5. python-docx – DOCX text extraction

6. python-dotenv – environment variable management

Usage

1. Clone the repository:

git clone https://github.com/yourusername/gemini-rag-project.git
cd gemini-rag-project


2. Install dependencies:

pip install -r requirements.txt


3. Set your Google API key in a .env file:

GOOGLE_API_KEY=your_api_key_here


4. Run the Streamlit app:

streamlit run app.py
