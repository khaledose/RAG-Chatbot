import streamlit as st
import mimetypes
from model import create_rag_chain, create_vector_store, get_existing_vector_stores, is_valid_store_name, update_embeddings_db, create_vector_store
from langchain.schema import Document

def detect_file_type(file):
    if file is None:
        return None
    
    file_type = mimetypes.guess_type(file.name)[0]
    if file_type:
        if 'json' in file_type:
            return 'json'
        elif 'pdf' in file_type:
            return 'pdf'
        elif 'csv' in file_type:
            return 'csv'
    
    file_extension = file.name.split('.')[-1].lower()
    if file_extension in ['json', 'pdf', 'csv']:
        return file_extension
    
    return None

def handle_vector_store_creation(uploaded_files, store_name):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    total_files = len(uploaded_files)
    for i, file in enumerate(uploaded_files):
        file_type = detect_file_type(file)
        if file_type:
            status_text.text(f"Processing file {i+1} of {total_files}: {file.name}")
            update_embeddings_db(file, store_name, file_type)
            progress_bar.progress((i + 1) / total_files)
    
    progress_bar.empty()
    status_text.empty()
    st.sidebar.success(f"Vector store '{store_name}' created successfully!")
    st.rerun()

def vector_store_management_sidebar():
    st.sidebar.header("Vector Store Management")

    # Section 1: Create a new vector store (without file upload)
    st.sidebar.subheader("Create New Vector Store")
    new_store_name = st.sidebar.text_input("New Vector Store Name", key="new_store_name")
    
    if new_store_name:
        if is_valid_store_name(new_store_name):
            if st.sidebar.button("Create", key="create_new_store", type="primary"):
                # Create an empty vector store (without uploading files)
                # This can simply create a Chroma store without any documents
                create_vector_store(new_store_name)
                st.sidebar.success(f"New vector store '{new_store_name}' created successfully!")
                st.rerun()
        else:
            st.sidebar.error("This vector store name already exists. Please choose a unique name.")

    st.sidebar.markdown("---")  # Add a separator

    # Section 2: Manage existing vector stores
    st.sidebar.subheader("Manage Existing Vector Stores")
    existing_stores = get_existing_vector_stores()
    selected_store = st.sidebar.selectbox("Select Vector Store", existing_stores, key="existing_store")

    if selected_store:
        # Allow file upload for selected store
        uploaded_files_existing_store = st.sidebar.file_uploader(f"Upload files to '{selected_store}'", type=['json', 'pdf', 'csv'], accept_multiple_files=True, key="existing_store_files")

        if uploaded_files_existing_store:
            if st.sidebar.button("Add Files", key="add_to_existing_store", type="primary"):
                handle_vector_store_creation(uploaded_files_existing_store, selected_store)

    return selected_store

def format_docs(docs):
    return "\n\n".join(f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs)

def chat_interface(rag_chain):
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            for chunk in rag_chain.stream({"input": prompt}):
                if isinstance(chunk, Document):  # This is a source document
                    st.write(f"Source: {chunk.metadata.get('source', 'Unknown')}")
                    st.write(chunk.page_content)
                else:  # This is a response chunk
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    st.title("💬 Enhanced RAG Chatbot")

    selected_store = vector_store_management_sidebar()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    
    if "rag_chain" not in st.session_state or st.session_state.get("current_store") != selected_store:
        st.session_state.rag_chain = create_rag_chain(selected_store)
        st.session_state.current_store = selected_store

    chat_interface(st.session_state.rag_chain)

if __name__ == "__main__":
    main()