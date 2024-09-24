import requests
from uuid import UUID
from typing import Dict
from services.base import BaseService

class ChatService(BaseService):
    def build(self, store_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/chat/build"
        data = {"store_name": store_name}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    def chat(self, store_name: str, session_id: UUID, question: str) -> str:
        url = f"{self.base_url}/chat"
        data = {
            "store_name": store_name,
            "session_id": str(session_id),
            "question": question
        }
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=1, decode_unicode=True)