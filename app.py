import streamlit as st
from services.rag import RAGService
from services.vector_store import VectorStoreService
from dotenv import load_dotenv
from utils.files import create_temp_dir, detect_file_type

def reset_session():
    rag.reset(session_id)
    st.session_state.messages.clear()
    refresh_store_list()

def session_interface():
    session_store = st.sidebar.selectbox("Select Vector Store", st.session_state.existing_stores, key="chat_store")
    st.session_state.current_store = session_store
    reset_button = st.sidebar.button("Reset Session")
    if reset_button:
        reset_session()

def refresh_store_list():
    st.session_state.existing_stores = vector_store.get_all()
    st.rerun()

def update_store_interface():
    upload_expander = st.sidebar.expander(f"Update Store")
    selected_store = upload_expander.selectbox("Select Vector Store", st.session_state.existing_stores, key="existing_store")
    uploaded_files = upload_expander.file_uploader(f"Add file to {selected_store}", type=['json', 'pdf', 'csv'], accept_multiple_files=True, key="existing_store_files")
    upload_expander.subheader("Or")

    web_url = upload_expander.text_input(f"Add Web page to {selected_store}")
    if upload_expander.button("Add Files", key="add_to_existing_store", type="primary"):
        with st.sidebar.spinner("Reading files.."):
            total_files = len(uploaded_files)
            if total_files > 0:
                progress_bar = upload_expander.progress(0)
                status_text = upload_expander.empty()
                for i, file in enumerate(uploaded_files):
                    file_type = detect_file_type(file)
                    if file_type:
                        status_text.text(f"Processing file {i+1} of {total_files}: {file.name}")
                        vector_store.update(create_temp_dir(file), selected_store, file_type)
                        progress_bar.progress((i + 1) / total_files)
                progress_bar.empty()
                status_text.empty()
            
            if web_url:
                vector_store.update(web_url, selected_store, "web")
            
            st.toast(f"Vector store '{selected_store}' updated successfully!")

def create_store_interface():
    create_expander = st.sidebar.expander("Create store")
    new_store_name = create_expander.text_input("New Vector Store", key="new_store_name")
    
    if vector_store.exists(new_store_name):
        create_expander.error(f"Vector store '{new_store_name}' already exists!")

    if create_expander.button("Create", key="create_new_store", type="primary", disabled=vector_store.exists(new_store_name)):
        vector_store.create(new_store_name)
        refresh_store_list()

def delete_store_interface():
    delete_expander = st.sidebar.expander("Delete store")
    delete_store = delete_expander.selectbox("Select Vector Store", st.session_state.existing_stores, key="delete_store")
    if delete_store == st.session_state.current_store:
        delete_expander.error("Cannot delete store that is already selected!")
    delete_button = delete_expander.button("Delete", type="primary", disabled=delete_store == st.session_state.current_store)
    if delete_button:
        vector_store.delete(delete_store)
        refresh_store_list()

def sidebar_interface():
    st.sidebar.header("Manage Session")

    session_interface()
    
    st.sidebar.header("Manage Vector Stores")

    update_store_interface()
    
    create_store_interface()
    
    delete_store_interface()

def chat_interface():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            rag.build(st.session_state.get("current_store"))
            for chunk in rag.chat(session_id, prompt):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    st.title("💬 Enhanced RAG Chatbot")

    if "existing_stores" not in st.session_state:
        st.session_state.existing_stores = vector_store.get_all()

    if "current_store" not in st.session_state:
        st.session_state.current_store = None
    
    sidebar_interface()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    
    if st.session_state.current_store is not None:
        chat_interface()

if __name__ == "__main__":
    load_dotenv()
    session_id = "123"
    vector_store = VectorStoreService()
    rag = RAGService(vector_store)
    main()