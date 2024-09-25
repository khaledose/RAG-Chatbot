# RAG Chatbot

## Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Streamlit, LangChain, and Chroma DB. The chatbot can process and answer questions based on information from uploaded JSON, PDF, CSV files, and web pages.

## Table of Contents

1. [Installation](#installation)
2. [Environment Setup](#environment-setup)
3. [Running the Application](#running-the-application)
4. [Project Structure](#project-structure)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Environment Setup

Create a `.env` file in the root directory with the following structure:

```
API_URL=<API_URL>
```

## Running the Application

Run the Streamlit app:

```
streamlit run app.py
```

## Project Structure

```
.
├── app.py
├── services
│   ├── BaseService.py
│   ├── ChatService.py
│   ├── SessionService.py
│   └── ContextService.py
├── .env
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.