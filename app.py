import os
from typing import List
import streamlit as st
from typing import Any
from dotenv import load_dotenv
from services.ChatService import ChatService
from services.SessionService import SessionService
from services.ContextService import ContextService

# Initialize services
load_dotenv()
url = os.getenv('API_URL')
session_service = SessionService(f'{url}/sessions')
context_service = ContextService(f'{url}/contexts')
chat_service = ChatService(f'{url}/chat')

class SessionInterface:
    @staticmethod
    def render():
        st.sidebar.selectbox(
            "Select context", 
            st.session_state.contexts, 
            key="chat_context", 
            on_change=SessionInterface._context_changed,
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
        SessionInterface._context_changed()
    
    @staticmethod
    def _context_changed():
        chat_service.build(st.session_state.chat_context)

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

class ContextInterface:
    @staticmethod
    def render():
        ContextInterface._render_update()
        ContextInterface._render_create()
        ContextInterface._render_delete()

    @staticmethod
    def _render_update():
        with st.sidebar.expander("Update Context"):
            selected_context = st.selectbox("Select Context", st.session_state.contexts, key="existing_context")
            uploaded_files = st.file_uploader(f"Add file to {selected_context}", type=['json', 'pdf', 'csv', 'txt', 'md'], accept_multiple_files=True, key="existing_context_files")

            if st.button("Add Files", key="add_to_existing_context", use_container_width=True):
                ContextInterface._process_uploaded_files(selected_context, uploaded_files)

    @staticmethod
    def _process_uploaded_files(context: str, files: List[Any]):
        with st.spinner("Reading files.."):
            total_files = len(files)
            if total_files > 0:
                progress_bar = st.progress(0)
                status_text = st.empty()
                for i, file in enumerate(files):
                    status_text.text(f"Processing file {i+1} of {total_files}: {file.name}")
                    context_service.update(context, file)
                    progress_bar.progress((i + 1) / total_files)
                progress_bar.empty()
                status_text.empty()
            st.toast(f"Context '{context}' updated successfully!")

    @staticmethod
    def _refresh_context_list():
        st.session_state.contexts = context_service.get_all()
        st.rerun()

    @staticmethod
    def _render_create():
        with st.sidebar.expander("Create Context"):
            new_context_name = st.text_input("Name", key="new_context_name")
            if st.button("Create", key="create_new_context", use_container_width=True):
                context_service.create(new_context_name)
                ContextInterface._refresh_context_list()

    @staticmethod
    def _render_delete():
        with st.sidebar.expander("Delete Context"):
            delete_context = st.selectbox("Select Context", st.session_state.contexts, key="delete_context")
            if delete_context == st.session_state.chat_context:
                st.error(f"Cannot delete {delete_context} that is already selected!")
            
            delete_button = st.button("Delete", use_container_width=True, disabled=delete_context == st.session_state.chat_context)
            if delete_button:
                context_service.delete(delete_context)
                ContextInterface._refresh_context_list()

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
        
        for chunk in chat_service.chat(st.session_state.chat_context, st.session_state.session_id, prompt):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

class App:
    @staticmethod
    def initialize_session_state():
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
        if "contexts" not in st.session_state:
            st.session_state.contexts = context_service.get_all()
        if 'sessions' not in st.session_state:
            st.session_state.sessions = session_service.get_all()
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def render():
        st.title("Admin Dashboard")
        App.initialize_session_state()

        st.sidebar.header("Session Management")
        SessionInterface.render()
        
        st.sidebar.header("Context Management")
        ContextInterface.render()

        if st.session_state.chat_context is None:
            st.warning("Please select a context.")
        elif st.session_state.session_id is None:
            st.warning("Please Select a session.")
        else:
            ChatInterface.render()

if __name__ == "__main__":
    App.render()