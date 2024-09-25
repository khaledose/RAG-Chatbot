import requests
from typing import Dict, List, Any
from services.BaseService import BaseService

class ContextService(BaseService):
    def get_all(self) -> List[str]:
        url = f"{self.base_url}/"
        response = requests.get(url)
        return self._handle_response(response)

    def create(self, context_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/"
        data = {"context_name": context_name}
        response = requests.post(url, json=data)
        return self._handle_response(response)

    def add_file(self, context_name: str, file: Any) -> Dict[str, str]:
        supported_files = ["application/pdf", "text/csv", "application/json", "text/plain"]
        file_type = file.type
        if file_type not in supported_files:    
            file_type = "text/plain"
        url = f"{self.base_url}/{context_name}/file"
        response = requests.post(
            url, 
            files={'file': (file.name, file.getvalue(), file_type)}
        )
        return self._handle_response(response)

    def add_webpage(self, context_name: str, url: str) -> Dict[str, str]:
        url = f"{self.base_url}/{context_name}/web?url={url}"
        response = requests.post(url)
        return self._handle_response(response)

    def delete(self, context_name: str) -> Dict[str, str]:
        url = f"{self.base_url}/"
        data = {"context_name": context_name}
        response = requests.delete(url, json=data)
        return self._handle_response(response)