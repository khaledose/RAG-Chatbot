import tempfile
import os
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import JSONLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompts import SYSTEM_PROMPT, API_URL, API_KEY, MODEL_TEMPERATURE

def create_temp_dir(file):
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, file.name)
    with open(path, "wb") as f:
        f.write(file.getvalue())
    return path

def load_document(file_path, file_type):
    if file_type == 'json':
        return JSONLoader(file_path=file_path, jq_schema='.', text_content=False).load()
    elif file_type == 'pdf':
        return PyPDFLoader(file_path=file_path).load()
    elif file_type == 'csv':
        return CSVLoader(file_path=file_path).load()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def create_vector_store(store_name):
    # Create an empty Chroma vector store with no documents
    local_embeddings = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
    return Chroma(
        collection_name=store_name,
        embedding_function=local_embeddings,
        persist_directory=f'./chroma/{store_name}'
    )

def update_embeddings_db(file, store_name, file_type):
    file_path = create_temp_dir(file)
    docs = load_document(file_path, file_type)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)

    local_embeddings = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
    return Chroma.from_documents(
        collection_name=store_name,
        documents=chunks,
        embedding=local_embeddings,
        persist_directory=f'./chroma/{store_name}'
    )

def get_existing_vector_stores():
    chroma_dir = './chroma'
    if not os.path.exists(chroma_dir):
        print(f"Directory '{chroma_dir}' not found.")
        return []
    
    return [d for d in os.listdir(chroma_dir) if os.path.isdir(os.path.join(chroma_dir, d))]

def is_valid_store_name(name):
    existing_stores = get_existing_vector_stores()
    return name not in existing_stores

def create_rag_chain(vector_store_name):
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma(persist_directory=f"./chroma/{vector_store_name}", embedding_function=embedding_function)
    retriever = vector_db.as_retriever()

    llm = ChatOpenAI(
        base_url=API_URL, 
        api_key=API_KEY, 
        temperature=MODEL_TEMPERATURE,
        streaming=True,
    )

    prompt = PromptTemplate(template=SYSTEM_PROMPT, input_variables=["context", "question"])

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain