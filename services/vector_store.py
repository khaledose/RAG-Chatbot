import requests
from typing import Dict, List, Any
from services.base import BaseService

class VectorStoreService(BaseService):
    def get_all(self) -> List[str]:
        url = f"{self.base_url}/vector_stores"
        response = requests.get(url)
        return self._handle_response(response)

    def create(self, store_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/vector_stores"
        data = {"store_name": store_name}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    def update(self, store_name: str, file: Any) -> Dict[str, str]:
        url = f"{self.base_url}/vector_stores/{store_name}"
        response = requests.post(
            url, 
            files={'file': (file.name, file.getvalue(), file.type)}
        )
        return self._handle_response(response)

    def delete(self, store_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/vector_stores"
        data = {"store_name": store_name}
        response = requests.delete(url, json=data)
        return self._handle_response(response)