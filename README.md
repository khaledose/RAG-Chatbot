# RAG Chatbot

## Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Streamlit, LangChain, and Chroma DB. The chatbot can process and answer questions based on information from uploaded JSON, PDF, CSV files, and web pages.

## Table of Contents

1. [Installation](#installation)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Project Structure](#project-structure)
6. [Contributing](#contributing)
7. [License](#license)

## Installation

Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Environment Setup

Create a `.env` file in the root directory with the following structure:

```
API_URL=<LM_STUDIO_SERVER_URL>
API_KEY=<CAN_BE_ANYTHING>
MODEL_TEMPERATURE=<TEMPERATURE>
DB_DIR=<PATH_TO_CHROMA_DB>
EMBEDDING_MODEL=<EMBEDDING_MODEL_NAME>
```

Make sure to replace `your_api_key_here` with your actual API key.

## Configuration

The `config.py` file contains important system prompts for the RAG system:

- `SYSTEM_PROMPT`: This is used to instruct the AI model on how to answer questions based on the retrieved context. It must contain `{context}` which is the placeholder for embeddings to be added to the prompt.
- `HISTORY_PROMPT`: This is used to reformulate user questions in the context of the chat history, ensuring that the questions are standalone and can be understood without additional context.

You can modify these prompts in the `config.py` file to adjust the behavior of your RAG system as needed.


## Running the Application

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

## Project Structure

```
.
├── app.py
├── config.py
├── services
│   ├── rag.py
│   └── vector_store.py
├── utils
│   └── files.py
├── .env
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.