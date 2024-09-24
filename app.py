import os
from typing import List
import streamlit as st
from typing import Any
from dotenv import load_dotenv
from services.chat import ChatService
from services.session import SessionService
from services.vector_store import VectorStoreService

# Initialize services
load_dotenv()
url = os.getenv('API_URL')
session_service = SessionService(url)
vector_store_service = VectorStoreService(url)
chat_service = ChatService(url)

class SessionInterface:
    @staticmethod
    def render():
        st.sidebar.selectbox(
            "Select context", 
            st.session_state.existing_stores, 
            key="chat_store", 
            on_change=SessionInterface._store_changed,
        )
        
        if st.sidebar.button("New Session", use_container_width=True):
            new_session_id = session_service.create()
            st.session_state['sessions'].append(new_session_id)
            SessionInterface._switch_session(new_session_id)
        
        sessions_expander = st.sidebar.expander("Sessions")
        SessionInterface._render_session_list(sessions_expander)
        SessionInterface._render_clear_sessions_button(sessions_expander)

    @staticmethod
    def _render_session_list(expander):
        for item in st.session_state['sessions']:
            container = expander.container()
            cols = container.columns([0.8, 0.2], vertical_alignment='center')
            if cols[0].button(item, key=f"session_{item}", use_container_width=True):
                SessionInterface._switch_session(item)
            if cols[1].button("❌", key=f"delete_{item}", use_container_width=True):
                SessionInterface._delete_session(item)

    @staticmethod
    def _render_clear_sessions_button(expander):
        if expander.button("⚠️ Delete All Sessions ⚠️", use_container_width=True):
            SessionInterface._clear_all_sessions()
    
    @staticmethod
    def _switch_session(session_id: str):
        st.session_state.session_id = session_id
        st.session_state.messages = SessionInterface._get_session_messages(session_id)
        SessionInterface._store_changed()
    
    @staticmethod
    def _store_changed():
        chat_service.build(st.session_state.chat_store)

    @staticmethod
    def _delete_session(session_id: str):
        session_service.delete(session_id)
        st.session_state['sessions'].remove(session_id)
        if st.session_state.session_id == session_id:
            st.session_state.session_id = None
        st.rerun()

    @staticmethod
    def _clear_all_sessions():
        session_service.clear()
        st.session_state.sessions.clear()
        st.session_state.messages.clear()
        st.session_state.session_id = None
        st.rerun()

    @staticmethod
    def _get_session_messages(session_id: str) -> List[dict]:
        messages = session_service.get(session_id)
        return [{"role": m.get('type'), "content": m.get('content')} for m in messages["messages"]]

class VectorStoreInterface:
    @staticmethod
    def render():
        VectorStoreInterface._render_update()
        VectorStoreInterface._render_create()
        VectorStoreInterface._render_delete()

    @staticmethod
    def _render_update():
        with st.sidebar.expander("Update Store"):
            selected_store = st.selectbox("Select Vector Store", st.session_state.existing_stores, key="existing_store")
            uploaded_files = st.file_uploader(f"Add file to {selected_store}", type=['json', 'pdf', 'csv'], accept_multiple_files=True, key="existing_store_files")

            if st.button("Add Files", key="add_to_existing_store", use_container_width=True):
                VectorStoreInterface._process_uploaded_files(selected_store, uploaded_files)

    @staticmethod
    def _process_uploaded_files(store: str, files: List[Any]):
        with st.spinner("Reading files.."):
            total_files = len(files)
            if total_files > 0:
                progress_bar = st.progress(0)
                status_text = st.empty()
                for i, file in enumerate(files):
                    status_text.text(f"Processing file {i+1} of {total_files}: {file.name}")
                    vector_store_service.update(store, file)
                    progress_bar.progress((i + 1) / total_files)
                progress_bar.empty()
                status_text.empty()
            st.toast(f"Vector store '{store}' updated successfully!")

    @staticmethod
    def _refresh_store_list():
        st.session_state.existing_stores = vector_store_service.get_all()
        st.rerun()

    @staticmethod
    def _render_create():
        with st.sidebar.expander("Create store"):
            new_store_name = st.text_input("New Vector Store", key="new_store_name")
            if st.button("Create", key="create_new_store", use_container_width=True):
                vector_store_service.create(new_store_name)
                VectorStoreInterface._refresh_store_list()

    @staticmethod
    def _render_delete():
        with st.sidebar.expander("Delete store"):
            delete_store = st.selectbox("Select Vector Store", st.session_state.existing_stores, key="delete_store")
            if delete_store == st.session_state.chat_store:
                st.error("Cannot delete store that is already selected!")
            
            delete_button = st.button("Delete", use_container_width=True, disabled=delete_store == st.session_state.chat_store)
            if delete_button:
                vector_store_service.delete(delete_store)
                VectorStoreInterface._refresh_store_list()

class ChatInterface:
    @staticmethod
    def render():
        ChatInterface._display_messages()
        ChatInterface._handle_user_input()

    @staticmethod
    def _display_messages():
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    @staticmethod
    def _handle_user_input():
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.chat_message("assistant"):
                ChatInterface._stream_response(prompt)

    @staticmethod
    def _stream_response(prompt: str):
        response_placeholder = st.empty()
        full_response = ""
        
        for chunk in chat_service.chat(st.session_state.chat_store, st.session_state.session_id, prompt):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

class App:
    @staticmethod
    def initialize_session_state():
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
        if "existing_stores" not in st.session_state:
            st.session_state.existing_stores = vector_store_service.get_all()
        if 'sessions' not in st.session_state:
            st.session_state['sessions'] = session_service.get_all()
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def render():
        st.title("💬 Stream Buddy")
        App.initialize_session_state()

        st.sidebar.header("Manage Session")
        SessionInterface.render()
        
        st.sidebar.header("Manage Vector Stores")
        VectorStoreInterface.render()

        if st.session_state.chat_store is not None and st.session_state.session_id is not None:
            ChatInterface.render()

if __name__ == "__main__":
    App.render()