# RAG Chatbot

## Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Streamlit, LangChain, and Chroma DB. The chatbot can process and answer questions based on information from uploaded JSON, PDF, and CSV files.

## Features

- Multiple file upload support (JSON, PDF, CSV)
- Automatic file type detection
- Vector store creation with progress bar
- Real-time streaming of chat responses
- Source citations for answers
- Conversation history

## Requirements

- Python 3.8+
- Streamlit
- LangChain
- Chroma DB
- OllamaEmbeddings
- PyPDF2 (for PDF processing)
- OpenAI API key (for ChatGPT integration)

## Installation

Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Use the sidebar to upload files and create vector stores

4. Start chatting with the RAG chatbot in the main interface

## Project Structure

- `app.py`: Main Streamlit application
- `model.py`: Backend logic for RAG model and vector store operations
- `requirements.txt`: List of Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.