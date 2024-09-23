import os
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from services.vector_store import VectorStoreService
from config import SYSTEM_PROMPT, HISTORY_PROMPT

class RAGService:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.sessions = {}
        self.llm = None
        self.retriever = None
        self.rag_chain = None
    
    def _create_llm(self):
        self.llm = ChatOpenAI(
            base_url=os.getenv('API_URL'), 
            api_key=os.getenv('API_KEY'), 
            temperature=float(os.getenv('MODEL_TEMPERATURE', 0.7)),
            streaming=True,
        )

    def _create_retriever(self, store_name):
        vectorstore = self.vector_store.get(store_name)
        self.retriever = vectorstore.as_retriever()

    def _create_question_contextualizer(self):
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", HISTORY_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_history_aware_retriever(self.llm, self.retriever, contextualize_q_prompt)

    def _create_qa_chain(self):
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_stuff_documents_chain(self.llm, qa_prompt)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatMessageHistory()
        return self.sessions[session_id]

    def reset(self, session_id):
        self.sessions.pop(session_id, None)

    def build(self, store_name):
        self._create_llm()
        self._create_retriever(store_name)

        history_aware_retriever = self._create_question_contextualizer()
        qa_chain = self._create_qa_chain()

        self.rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    async def chat_async(self, session_id, question):
        runnable = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        async for token in runnable.astream({"input": question}, {"configurable": {"session_id": session_id}}):
            if 'answer' in token:
                yield token['answer']

    def chat(self, session_id, question):
        runnable = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        for token in runnable.stream({"input": question}, {"configurable": {"session_id": session_id}}):
            if 'answer' in token:
                yield token['answer']

