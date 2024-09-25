import requests
from uuid import UUID
from typing import Dict
from services.BaseService import BaseService

class ChatService(BaseService):
    def build(self, context_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/build"
        data = {"context_name": context_name}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    def chat(self, context_name: str, session_id: UUID, question: str) -> str:
        url = f"{self.base_url}/"
        data = {
            "context_name": context_name,
            "session_id": str(session_id),
            "question": question
        }
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=1, decode_unicode=True)