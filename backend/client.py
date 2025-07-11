import requests
from typing import Any, Dict, List, Optional

class DBDescClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def create_cluster(self, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/clusters/", json={"name": name}).json()

    def get_clusters(self) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/clusters/").json()

    def create_database(self, cluster_id: int, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/clusters/{cluster_id}/databases/", json={"name": name}).json()

    def get_databases(self, cluster_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/clusters/{cluster_id}/databases/").json()

    def create_table(self, database_id: int, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/databases/{database_id}/tables/", json={"name": name}).json()

    def get_tables(self, database_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/databases/{database_id}/tables/").json()

    def create_field(self, table_id: int, name: str, parent_id: Optional[int] = None, meta: Optional[dict] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {"name": name}
        if parent_id is not None:
            data["parent_id"] = parent_id
        if meta is not None:
            data["meta"] = meta
        return requests.post(f"{self.base_url}/tables/{table_id}/fields/", json=data).json()

    def get_fields(self, table_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/tables/{table_id}/fields/").json()

    def create_edge(self, from_field_id: int, to_field_id: int, type: str) -> Dict[str, Any]:
        data = {"from_field_id": from_field_id, "to_field_id": to_field_id, "type": type}
        return requests.post(f"{self.base_url}/edges/", json=data).json()

    def get_edges(self, field_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/fields/{field_id}/edges/").json() 