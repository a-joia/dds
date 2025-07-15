import re
from typing import Any, Dict, List, Optional, Tuple, Union
from .client import DBDescClient, APIClientError

class PathClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = DBDescClient(base_url)

    # --- Create ---
    def create_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Create a cluster by name."""
        return self.client.create_cluster(cluster_name)

    def create_database(self, path: str) -> Dict[str, Any]:
        """Create a database by path: cluster/database."""
        return self.client.create_database_by_path(path)

    def create_table(self, path: str) -> Dict[str, Any]:
        """Create a table by path: cluster/database/table."""
        return self.client.create_table_by_path(path)

    def create_field(self, path: str, meta: Optional[dict] = None) -> Dict[str, Any]:
        """Create a field by path: cluster/database/table/field[/subfield...]."""
        return self.client.create_field_by_path(path, meta)

    # --- Edit ---
    def edit_table_description(self, path: str, description: str) -> Any:
        """Edit the description of a table by path."""
        cluster, database, table = path.split("/", 2)
        return self.client.update_table_by_path(cluster, database, table, {"description": description})

    def edit_field_description(self, path: str, description: str) -> Any:
        """Edit the description of a field by path."""
        return self._patch_field_meta(path, {"description": description})

    def edit_field_example(self, path: str, example: str) -> Any:
        """Edit the example of a field by path."""
        return self._patch_field_meta(path, {"example": example})

    def edit_field_information(self, path: str, information: str) -> Any:
        """Edit the information of a field by path."""
        return self._patch_field_meta(path, {"information": information})

    def edit_field_type(self, path: str, type_value: str) -> Any:
        """Edit the type of a field by path."""
        return self._patch_field_meta(path, {"type": type_value})

    def add_field_metadata(self, path: str, metadata: Dict[str, Any]) -> Any:
        """Add (merge) metadata to a field by path."""
        current = self.get_field_metadata(path)
        if current is None:
            current = {}
        merged = {**current, **metadata}
        return self._patch_field_meta(path, merged)

    def edit_field_metadata(self, path: str, metadata: Dict[str, Any]) -> Any:
        """Overwrite only the provided keys in the field's metadata by path."""
        current = self.get_field_metadata(path)
        if current is None:
            current = {}
        updated = {**current, **metadata}
        return self._patch_field_meta(path, updated)

    # --- Delete ---
    def delete_cluster(self, path: str) -> Any:
        """Delete a cluster by name (path = cluster_name)."""
        return self.client.delete_cluster_by_path(path)

    def delete_database(self, path: str) -> Any:
        """Delete a database by path (cluster/database)."""
        cluster, database = path.split("/", 1)
        return self.client.delete_database_by_path(cluster, database)

    def delete_table(self, path: str) -> Any:
        """Delete a table by path (cluster/database/table)."""
        cluster, database, table = path.split("/", 2)
        return self.client.delete_table_by_path(cluster, database, table)

    def delete_field(self, path: str) -> Any:
        """Delete a field by path (cluster/database/table/field[/subfield...])."""
        return self.client.delete_field_by_path(path)

    # --- Get ---
    def get_field(self, path: str) -> Dict[str, Any]:
        """Get all information of a field by path."""
        return self.client.get_field_by_path(path)

    def get_field_metadata(self, path: str, list_of_keys: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get metadata of a field by path. Optionally filter by keys."""
        meta = self.client.get_field_meta_by_path(path)
        if meta is None:
            return None
        if list_of_keys is not None:
            return {k: meta.get(k) for k in list_of_keys if k in meta}
        return meta

    def get_connected_databases(self, db_path: str) -> List[str]:
        """Given a database path (cluster/database), return all other databases connected to it by any edge."""
        cluster, database = db_path.split("/", 1)
        # Get all tables in this database
        tables = self.client.get_tables_by_database_name(cluster, database)
        connected_databases = set()
        for table in tables:
            table_path = f"{cluster}/{database}/{table['name']}"
            field_paths = self.client.list_field_paths_by_table_path(cluster, database, table['name'])
            for field_path in field_paths:
                # Get all edges for this field
                equivalents = self.client.get_equivalents(field_path)
                for eq in equivalents:
                    eq_path = eq['path']
                    # eq_path: cluster2/database2/table2/field...
                    eq_parts = eq_path.split("/")
                    if len(eq_parts) >= 3:
                        eq_db_path = f"{eq_parts[0]}/{eq_parts[1]}"
                        if eq_db_path != db_path:
                            connected_databases.add(eq_db_path)
        return sorted(connected_databases)

    # --- Edge ---
    def add_edge(self, path1: str, path2: str) -> Any:
        """Add an edge between two fields by path."""
        return self.client.add_equivalence(path1, path2)

    def remove_edge(self, path1: str, path2: str) -> Any:
        """Remove an edge between two fields by path (removes both directions)."""
        return self.client.remove_equivalence(path1, path2)

    def get_edges(self, path: str) -> List[Dict[str, Any]]:
        """Get all edges for a field by path."""
        return self.client.get_equivalents(path)

    # --- List ---
    def list_clusters(self) -> List[str]:
        """List all cluster names."""
        return [c['name'] for c in self.client.get_clusters()]

    def list_database(self, clusters: Optional[Union[str, List[str]]] = None) -> List[str]:
        """List all database paths for given clusters (or all if None)."""
        result = []
        clusters_list = []
        if clusters is None:
            clusters_list = self.list_clusters()
        elif isinstance(clusters, str):
            clusters_list = [clusters]
        else:
            clusters_list = clusters
        for cluster in clusters_list:
            dbs = self.client.get_databases_by_cluster_name(cluster)
            for db in dbs:
                result.append(f"{cluster}/{db['name']}")
        return result

    def list_fields(self, path: str = "") -> List[str]:
        """List all field paths derived from the input path."""
        if not path:
            # List all fields in all tables
            clusters = self.list_clusters()
            result = []
            for cluster in clusters:
                dbs = self.client.get_databases_by_cluster_name(cluster)
                for db in dbs:
                    tables = self.client.get_tables_by_database_name(cluster, db['name'])
                    for table in tables:
                        result.extend(self.client.list_field_paths_by_table_path(cluster, db['name'], table['name']))
            return result
        else:
            parts = path.split("/")
            if len(parts) == 3:
                return self.client.list_field_paths_by_table_path(*parts)
            else:
                # Filter all field paths that start with the given path
                all_fields = self.list_fields("")
                return [f for f in all_fields if f.startswith(path)]

    def get_hierarchy(self, path: str, filter: Optional[List[Tuple[str, Any]]] = None) -> List[str]:
        """Return a list of all field paths derived from the input path, optionally filtered by metadata key-value pairs."""
        all_fields = self.list_fields(path)
        if not filter:
            return all_fields
        filtered = []
        for fpath in all_fields:
            meta = self.get_field_metadata(fpath)
            if meta is None:
                continue
            if all(meta.get(k) == v for k, v in filter):
                filtered.append(fpath)
        return filtered

    # --- Internal helpers ---
    def _patch_field_meta(self, path: str, meta: Dict[str, Any]) -> Any:
        """Patch (update) the meta of a field by path, always including the current meta (if any) to ensure required keys like 'type' are present."""
        current = self.get_field_metadata(path)
        if current is not None:
            merged = {**current, **meta}
        else:
            merged = meta
        return self.client.patch_field_meta_by_path(path, merged) 