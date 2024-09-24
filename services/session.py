import requests
from uuid import UUID
from typing import Dict, List, Any
from services.base import BaseService

class SessionService(BaseService):
    def get_all(self) -> List[str]:
        url = f"{self.base_url}/session/"
        response = requests.get(url)
        return self._handle_response(response)

    def get(self, session_id: UUID) -> Dict[str, Any]:
        url = f"{self.base_url}/session/{session_id}"
        response = requests.get(url)
        return self._handle_response(response)

    def create(self) -> str:
        url = f"{self.base_url}/session/"
        response = requests.post(url)
        return self._handle_response(response)

    def delete(self, session_id: UUID) -> Dict[str, str]:
        url = f"{self.base_url}/session/{session_id}"
        response = requests.delete(url)
        return self._handle_response(response)

    def clear(self) -> Dict[str, str]:
        url = f"{self.base_url}/session"
        response = requests.delete(url)
        return self._handle_response(response)