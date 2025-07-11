import requests
from typing import Any, Dict, List, Optional

class DBDescClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def create_cluster(self, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/clusters/", json={"name": name}).json()

    def get_clusters(self) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/clusters/").json()

    def delete_cluster(self, cluster_id: int) -> Any:
        return requests.delete(f"{self.base_url}/clusters/{cluster_id}").json()

    def update_cluster(self, cluster_id: int, name: str) -> Any:
        # First get the cluster to find its name
        clusters = self.get_clusters()
        cluster_name = None
        for c in clusters:
            if c['id'] == cluster_id:
                cluster_name = c['name']
                break
        if not cluster_name:
            raise ValueError(f"Cluster with ID {cluster_id} not found")
        return requests.patch(f"{self.base_url}/clusters/by-path/{cluster_name}", json={"name": name}).json()

    def create_database(self, cluster_id: int, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/clusters/{cluster_id}/databases/", json={"name": name}).json()

    def get_databases(self, cluster_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/clusters/{cluster_id}/databases/").json()

    def delete_database(self, database_id: int) -> Any:
        return requests.delete(f"{self.base_url}/databases/{database_id}").json()

    def update_database(self, database_id: int, name: str) -> Any:
        # First get the database to find its cluster and name
        clusters = self.get_clusters()
        for c in clusters:
            dbs = self.get_databases(c['id'])
            for db in dbs:
                if db['id'] == database_id:
                    return requests.patch(f"{self.base_url}/databases/by-path/{c['name']}/{db['name']}", json={"name": name}).json()
        raise ValueError(f"Database with ID {database_id} not found")

    def create_table(self, database_id: int, name: str) -> Dict[str, Any]:
        return requests.post(f"{self.base_url}/databases/{database_id}/tables/", json={"name": name}).json()

    def get_tables(self, database_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/databases/{database_id}/tables/").json()

    def delete_table(self, table_id: int) -> Any:
        return requests.delete(f"{self.base_url}/tables/{table_id}").json()

    def update_table(self, table_id: int, name: str) -> Any:
        # First get the table to find its cluster, database and name
        clusters = self.get_clusters()
        for c in clusters:
            dbs = self.get_databases(c['id'])
            for db in dbs:
                tables = self.get_tables(db['id'])
                for table in tables:
                    if table['id'] == table_id:
                        return requests.patch(f"{self.base_url}/tables/by-path/{c['name']}/{db['name']}/{table['name']}", json={"name": name}).json()
        raise ValueError(f"Table with ID {table_id} not found")

    def create_field(self, table_id: int, name: str, parent_id: Optional[int] = None, meta: Optional[dict] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {"name": name}
        if parent_id is not None:
            data["parent_id"] = parent_id
        if meta is not None:
            data["meta"] = meta
        return requests.post(f"{self.base_url}/tables/{table_id}/fields/", json=data).json()

    def get_fields(self, table_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/tables/{table_id}/fields/").json()

    def delete_field(self, field_id: int) -> Any:
        return requests.delete(f"{self.base_url}/fields/{field_id}").json()

    # Note: Field name updates are not supported by the backend (only meta updates)
    # def update_field(self, field_id: int, name: str) -> Any:
    #     return requests.patch(f"{self.base_url}/fields/{field_id}", json={"name": name}).json()

    def create_edge(self, from_field_id: int, to_field_id: int, type: str) -> Dict[str, Any]:
        data = {"from_field_id": from_field_id, "to_field_id": to_field_id, "type": type}
        return requests.post(f"{self.base_url}/edges/", json=data).json()

    def get_edges(self, field_id: int) -> List[Dict[str, Any]]:
        return requests.get(f"{self.base_url}/fields/{field_id}/edges/").json()

    def create_database_by_path(self, path: str) -> Dict[str, Any]:
        """
        Create a database by path (cluster/database).
        
        Args:
            path: Path in format "cluster/database"
            
        Returns:
            Created database object
            
        Raises:
            ValueError: If cluster doesn't exist or path format is invalid
        """
        parts = path.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid path format: '{path}'. Expected format: 'cluster/database'")
        
        cluster_name, database_name = parts
        
        # Check if cluster exists
        clusters = self.get_clusters()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            available_clusters = [c['name'] for c in clusters]
            raise ValueError(
                f"Cluster '{cluster_name}' does not exist.\n"
                f"Available clusters: {available_clusters}\n"
                f"Path provided: '{path}'\n"
                f"Please create the cluster first or use an existing cluster name."
            )
        
        # Create database in the cluster
        return self.create_database(cluster['id'], database_name)

    def create_table_by_path(self, path: str) -> Dict[str, Any]:
        """
        Create a table by path (cluster/database/table).
        
        Args:
            path: Path in format "cluster/database/table"
            
        Returns:
            Created table object
            
        Raises:
            ValueError: If cluster or database doesn't exist or path format is invalid
        """
        parts = path.split('/')
        if len(parts) != 3:
            raise ValueError(f"Invalid path format: '{path}'. Expected format: 'cluster/database/table'")
        
        cluster_name, database_name, table_name = parts
        
        # Check if cluster exists
        clusters = self.get_clusters()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            available_clusters = [c['name'] for c in clusters]
            raise ValueError(
                f"Cluster '{cluster_name}' does not exist.\n"
                f"Available clusters: {available_clusters}\n"
                f"Path provided: '{path}'\n"
                f"Please create the cluster first or use an existing cluster name."
            )
        
        # Check if database exists
        databases = self.get_databases(cluster['id'])
        database = None
        for db in databases:
            if db['name'] == database_name:
                database = db
                break
        
        if not database:
            available_databases = [db['name'] for db in databases]
            raise ValueError(
                f"Database '{database_name}' does not exist in cluster '{cluster_name}'.\n"
                f"Available databases in cluster '{cluster_name}': {available_databases}\n"
                f"Path provided: '{path}'\n"
                f"Please create the database first or use an existing database name."
            )
        
        # Create table in the database
        return self.create_table(database['id'], table_name)

    def create_field_by_path(self, path: str, meta: Optional[dict] = None) -> Dict[str, Any]:
        """
        Create a field by path (cluster/database/table/field or cluster/database/table/field/subfield/...).
        
        Args:
            path: Path in format "cluster/database/table/field" or "cluster/database/table/field/subfield/..."
            meta: Optional metadata for the field
            
        Returns:
            Created field object
            
        Raises:
            ValueError: If cluster, database, table, or any parent field doesn't exist or path format is invalid
        """
        parts = path.split('/')
        if len(parts) < 4:
            raise ValueError(
                f"Invalid path format: '{path}'. "
                f"Expected format: 'cluster/database/table/field' or 'cluster/database/table/field/subfield/...'"
            )
        
        cluster_name = parts[0]
        database_name = parts[1]
        table_name = parts[2]
        field_path = parts[3:]
        
        # Check if cluster exists
        clusters = self.get_clusters()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            available_clusters = [c['name'] for c in clusters]
            raise ValueError(
                f"Cluster '{cluster_name}' does not exist.\n"
                f"Available clusters: {available_clusters}\n"
                f"Path provided: '{path}'\n"
                f"Please create the cluster first or use an existing cluster name."
            )
        
        # Check if database exists
        databases = self.get_databases(cluster['id'])
        database = None
        for db in databases:
            if db['name'] == database_name:
                database = db
                break
        
        if not database:
            available_databases = [db['name'] for db in databases]
            raise ValueError(
                f"Database '{database_name}' does not exist in cluster '{cluster_name}'.\n"
                f"Available databases in cluster '{cluster_name}': {available_databases}\n"
                f"Path provided: '{path}'\n"
                f"Please create the database first or use an existing database name."
            )
        
        # Check if table exists
        tables = self.get_tables(database['id'])
        table = None
        for t in tables:
            if t['name'] == table_name:
                table = t
                break
        
        if not table:
            available_tables = [t['name'] for t in tables]
            raise ValueError(
                f"Table '{table_name}' does not exist in database '{database_name}' (cluster '{cluster_name}').\n"
                f"Available tables in database '{database_name}': {available_tables}\n"
                f"Path provided: '{path}'\n"
                f"Please create the table first or use an existing table name."
            )
        
        # Create field or subfield
        parent_id = None
        
        # If we have subfields, we need to traverse the field hierarchy
        if len(field_path) > 1:
            # Get all fields in the table
            all_fields = self.get_fields(table['id'])
            
            # Traverse the field path to find the parent
            for i, field_name in enumerate(field_path[:-1]):
                # Find the field with this name and the correct parent
                found_field = None
                for field in all_fields:
                    if field['name'] == field_name and field.get('parent_id') == parent_id:
                        found_field = field
                        break
                
                if not found_field:
                    # Build a helpful error message
                    if parent_id is None:
                        available_fields = [f['name'] for f in all_fields if f.get('parent_id') is None]
                        error_msg = f"Field '{field_name}' does not exist at the root level of table '{table_name}'."
                    else:
                        # Find the parent field name for better error message
                        parent_field_name = "unknown"
                        for field in all_fields:
                            if field['id'] == parent_id:
                                parent_field_name = field['name']
                                break
                        available_subfields = [f['name'] for f in all_fields if f.get('parent_id') == parent_id]
                        error_msg = f"Subfield '{field_name}' does not exist under field '{parent_field_name}' in table '{table_name}'."
                    
                    raise ValueError(
                        f"{error_msg}\n"
                        f"Path provided: '{path}'\n"
                        f"Failed at: '{'/'.join(parts[:3 + i + 1])}'\n"
                        f"Please create the missing field first or use an existing field name."
                    )
                
                parent_id = found_field['id']
        
        # Create the final field/subfield
        field_name = field_path[-1]
        return self.create_field(table['id'], field_name, parent_id=parent_id, meta=meta)

BASE_URL = 'http://localhost:8000'

def add_equivalence(from_path: str, to_path: str):
    r = requests.post(f'{BASE_URL}/equivalence/', params={
        'from_path': from_path,
        'to_path': to_path
    })
    r.raise_for_status()
    return r.json()

def remove_equivalence(from_path: str, to_path: str):
    r = requests.delete(f'{BASE_URL}/equivalence/', params={
        'from_path': from_path,
        'to_path': to_path
    })
    r.raise_for_status()
    return r.json()

def list_equivalents(field_path: str):
    r = requests.get(f'{BASE_URL}/fields/{field_path}/equivalence/')
    r.raise_for_status()
    return r.json()['equivalents']

def add_possibly_equivalence(from_path: str, to_path: str):
    import requests
    r = requests.post(f'{BASE_URL}/possibly-equivalence/', params={
        'from_path': from_path,
        'to_path': to_path
    })
    if not r.ok:
        raise Exception(f'Failed to add possibly equivalence: {r.text}')
    return r.json()

def remove_possibly_equivalence(from_path: str, to_path: str):
    import requests
    r = requests.delete(f'{BASE_URL}/possibly-equivalence/', params={
        'from_path': from_path,
        'to_path': to_path
    })
    if not r.ok:
        raise Exception(f'Failed to remove possibly equivalence: {r.text}')
    return r.json()

API_URL = 'http://localhost:8000'

NOT_FOUND = '__NOT_FOUND__'

def list_clusters():
    resp = requests.get(f'{API_URL}/clusters/')
    resp.raise_for_status()
    return resp.json()

def list_databases(cluster_id=None):
    if cluster_id is None:
        # List all databases for all clusters
        clusters = list_clusters()
        all_dbs = []
        for c in clusters:
            dbs = list_databases(c['id'])  # Use cluster ID
            all_dbs.extend(dbs)
        return all_dbs
    resp = requests.get(f'{API_URL}/clusters/{cluster_id}/databases/')
    resp.raise_for_status()
    return resp.json()

def list_tables(database_id=None):
    if database_id is None:
        # List all tables for all databases
        dbs = list_databases()
        all_tables = []
        for db in dbs:
            tables = list_tables(db['id'])  # Use database ID
            all_tables.extend(tables)
        return all_tables
    resp = requests.get(f'{API_URL}/databases/{database_id}/tables/')
    resp.raise_for_status()
    return resp.json()

def list_fields(table_id=None):
    if table_id is None:
        # List all fields for all tables
        tables = list_tables()
        all_fields = []
        for t in tables:
            fields = list_fields(t['id'])  # Use table ID
            all_fields.extend(fields)
        return all_fields
    resp = requests.get(f'{API_URL}/tables/{table_id}/fields/')
    resp.raise_for_status()
    return resp.json()

def edit_by_path(path: str, data: dict):
    """
    Edit field metadata by path.
    
    Args:
        path: field path string (e.g., 'cluster/database/table/field' or 'cluster/database/table/field/subfield')
        data: dict of metadata to update (e.g., {"description": "new description", "type": "string"})
        
    Returns:
        Updated field object
        
    Raises:
        ValueError: If path format is invalid or not a field path
    """
    parts = path.split('/')
    
    if len(parts) < 4:
        raise ValueError(
            f"Invalid field path format: '{path}'. "
            f"Expected format: 'cluster/database/table/field' or 'cluster/database/table/field/subfield'"
        )
    
    # Field: 'cluster/database/table/field' or 'cluster/database/table/field/subfield/...'
    url = f"{API_URL}/fields/by-path/{path}/meta"
    
    resp = requests.patch(url, json=data)
    resp.raise_for_status()
    return resp.json()

def rename_by_path(path: str, new_name: str):
    """
    Rename a cluster, database, or table by path.
    
    Args:
        path: path string (e.g., 'cluster', 'cluster/database', 'cluster/database/table')
        new_name: new name for the resource
        
    Returns:
        Updated resource object
        
    Raises:
        ValueError: If path format is invalid
    """
    parts = path.split('/')
    
    if len(parts) == 1:
        # Cluster: 'cluster'
        cluster_name = parts[0]
        url = f"{API_URL}/clusters/by-path/{cluster_name}"
    elif len(parts) == 2:
        # Database: 'cluster/database'
        cluster_name, database_name = parts
        url = f"{API_URL}/databases/by-path/{cluster_name}/{database_name}"
    elif len(parts) == 3:
        # Table: 'cluster/database/table'
        cluster_name, database_name, table_name = parts
        url = f"{API_URL}/tables/by-path/{cluster_name}/{database_name}/{table_name}"
    else:
        raise ValueError(
            f"Invalid rename path format: '{path}'. "
            f"Expected formats: 'cluster', 'cluster/database', or 'cluster/database/table'"
        )
    
    resp = requests.patch(url, json={"name": new_name})
    resp.raise_for_status()
    return resp.json()

def get_cluster_by_path(cluster: str):
    url = f"{API_URL}/clusters/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    clusters = resp.json()
    for c in clusters:
        if c['name'] == cluster:
            return c
    return NOT_FOUND

def get_database_by_path(cluster: str, database: str):
    url = f"{API_URL}/clusters/{cluster}/databases/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    dbs = resp.json()
    for db in dbs:
        if db['name'] == database:
            return db
    return NOT_FOUND

def get_table_by_path(cluster: str, database: str, table: str):
    url = f"{API_URL}/clusters/{cluster}/databases/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    dbs = resp.json()
    db_id = None
    for db in dbs:
        if db['name'] == database:
            db_id = db['id']
            break
    if db_id is None:
        return NOT_FOUND
    url = f"{API_URL}/databases/{db_id}/tables/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    tables = resp.json()
    for t in tables:
        if t['name'] == table:
            return t
    return NOT_FOUND

def get_field_by_path(cluster: str, database: str, table: str, *field_path: str):
    url = f"{API_URL}/clusters/{cluster}/databases/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    dbs = resp.json()
    db_id = None
    for db in dbs:
        if db['name'] == database:
            db_id = db['id']
            break
    if db_id is None:
        return NOT_FOUND
    url = f"{API_URL}/databases/{db_id}/tables/"
    resp = requests.get(url)
    if not resp.ok:
        return NOT_FOUND
    tables = resp.json()
    table_id = None
    for t in tables:
        if t['name'] == table:
            table_id = t['id']
            break
    if table_id is None:
        return NOT_FOUND
    # Traverse fields/subfields
    parent_id = None
    for idx, fname in enumerate(field_path):
        url = f"{API_URL}/tables/{table_id}/fields/"
        resp = requests.get(url)
        if not resp.ok:
            return NOT_FOUND
        fields = resp.json()
        found = None
        for f in fields:
            if f['name'] == fname and (f.get('parent_id') == parent_id or parent_id is None):
                found = f
                parent_id = f['id']
                break
        if found is None:
            return NOT_FOUND
    return found

def create_field_by_path(path: str, data: dict):
    import requests
    r = requests.post(f'{BASE_URL}/fields/by-path/{path}', json=data)
    if not r.ok:
        raise Exception(f'Failed to create field: {r.text}')
    return r.json()

def print_hierarchy_by_path(path: str, indent: int = 0):
    """
    Print the complete hierarchy below a given path.
    
    Args:
        path: path string (e.g., 'cluster', 'cluster/database', 'cluster/database/table')
        indent: indentation level for pretty printing (default: 0)
        
    Examples:
        print_hierarchy_by_path("mycluster")  # Shows all databases, tables, fields
        print_hierarchy_by_path("mycluster/mydb")  # Shows all tables, fields
        print_hierarchy_by_path("mycluster/mydb/mytable")  # Shows all fields
    """
    parts = path.split('/')
    
    if len(parts) == 1:
        # Cluster path: show all databases, tables, fields
        cluster_name = parts[0]
        print(" " * indent + f"📦 Cluster: {cluster_name}")
        
        # Get cluster
        clusters = requests.get(f"{API_URL}/clusters/").json()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            print(" " * (indent + 2) + "❌ Cluster not found")
            return
        
        # Get databases
        databases = requests.get(f"{API_URL}/clusters/{cluster['id']}/databases/").json()
        if not databases:
            print(" " * (indent + 2) + "📭 No databases found")
            return
        
        for db in databases:
            print(" " * (indent + 2) + f"🗄️ Database: {db['name']}")
            
            # Get tables
            tables = requests.get(f"{API_URL}/databases/{db['id']}/tables/").json()
            if not tables:
                print(" " * (indent + 4) + "📭 No tables found")
                continue
            
            for table in tables:
                print(" " * (indent + 4) + f"📋 Table: {table['name']}")
                
                # Get fields
                fields = requests.get(f"{API_URL}/tables/{table['id']}/fields/").json()
                if not fields:
                    print(" " * (indent + 6) + "📭 No fields found")
                    continue
                
                # Print fields recursively
                _print_fields_recursive(fields, indent + 6)
    
    elif len(parts) == 2:
        # Database path: show all tables, fields
        cluster_name, database_name = parts
        print(" " * indent + f"🗄️ Database: {database_name} (in cluster: {cluster_name})")
        
        # Get database
        clusters = requests.get(f"{API_URL}/clusters/").json()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            print(" " * (indent + 2) + "❌ Cluster not found")
            return
        
        databases = requests.get(f"{API_URL}/clusters/{cluster['id']}/databases/").json()
        database = None
        for db in databases:
            if db['name'] == database_name:
                database = db
                break
        
        if not database:
            print(" " * (indent + 2) + "❌ Database not found")
            return
        
        # Get tables
        tables = requests.get(f"{API_URL}/databases/{database['id']}/tables/").json()
        if not tables:
            print(" " * (indent + 2) + "📭 No tables found")
            return
        
        for table in tables:
            print(" " * (indent + 2) + f"📋 Table: {table['name']}")
            
            # Get fields
            fields = requests.get(f"{API_URL}/tables/{table['id']}/fields/").json()
            if not fields:
                print(" " * (indent + 4) + "📭 No fields found")
                continue
            
            # Print fields recursively
            _print_fields_recursive(fields, indent + 4)
    
    elif len(parts) == 3:
        # Table path: show all fields
        cluster_name, database_name, table_name = parts
        print(" " * indent + f"📋 Table: {table_name} (in database: {database_name}, cluster: {cluster_name})")
        
        # Get table
        clusters = requests.get(f"{API_URL}/clusters/").json()
        cluster = None
        for c in clusters:
            if c['name'] == cluster_name:
                cluster = c
                break
        
        if not cluster:
            print(" " * (indent + 2) + "❌ Cluster not found")
            return
        
        databases = requests.get(f"{API_URL}/clusters/{cluster['id']}/databases/").json()
        database = None
        for db in databases:
            if db['name'] == database_name:
                database = db
                break
        
        if not database:
            print(" " * (indent + 2) + "❌ Database not found")
            return
        
        tables = requests.get(f"{API_URL}/databases/{database['id']}/tables/").json()
        table = None
        for t in tables:
            if t['name'] == table_name:
                table = t
                break
        
        if not table:
            print(" " * (indent + 2) + "❌ Table not found")
            return
        
        # Get fields
        fields = requests.get(f"{API_URL}/tables/{table['id']}/fields/").json()
        if not fields:
            print(" " * (indent + 2) + "📭 No fields found")
            return
        
        # Print fields recursively
        _print_fields_recursive(fields, indent + 2)
    
    else:
        print(f"❌ Invalid path format: '{path}'. Expected: 'cluster', 'cluster/database', or 'cluster/database/table'")

def _flatten_fields(nested_fields: list) -> list:
    """
    Helper function to flatten nested field structure into a flat list.
    
    Args:
        nested_fields: list of field objects with nested subfields
        
    Returns:
        Flat list of all fields with parent_id set correctly
    """
    flat_fields = []
    
    def _flatten_recursive(fields, parent_id=None):
        for field in fields:
            # Create a copy of the field without subfields
            flat_field = {k: v for k, v in field.items() if k != 'subfields'}
            flat_field['parent_id'] = parent_id
            flat_fields.append(flat_field)
            
            # Recursively flatten subfields
            if field.get('subfields'):
                _flatten_recursive(field['subfields'], field['id'])
    
    _flatten_recursive(nested_fields)
    return flat_fields

def _print_fields_recursive(fields: list, indent: int, parent_id: Optional[int] = None):
    """
    Helper function to recursively print fields and their subfields.
    
    Args:
        fields: list of field objects (can be nested or flat)
        indent: indentation level
        parent_id: parent field ID (None for root fields)
    """
    # If fields have nested structure, flatten them first
    if fields and 'subfields' in fields[0]:
        fields = _flatten_fields(fields)
    
    # Filter fields by parent_id
    current_fields = [f for f in fields if f.get('parent_id') == parent_id]
    
    for field in current_fields:
        # Print field info
        field_info = f"🔧 Field: {field['name']}"
        if field.get('meta'):
            meta_str = ", ".join([f"{k}: {v}" for k, v in field['meta'].items()])
            field_info += f" ({meta_str})"
        print(" " * indent + field_info)
        
        # Recursively print subfields
        _print_fields_recursive(fields, indent + 2, field['id'])

if __name__ == '__main__':
    # Example usage:
    path1 = 'cluster1/database1/table2/field1'
    path2 = 'cluster1/database1/table2/field2/subfield1'
    print('Adding equivalence between', path1, 'and', path2)
    print(add_equivalence(path1, path2))
    print('Equivalents for', path1, ':')
    for eq in list_equivalents(path1):
        print('  ', eq['path'])
    print('Equivalents for', path2, ':')
    for eq in list_equivalents(path2):
        print('  ', eq['path'])
    print('Removing equivalence between', path1, 'and', path2)
    print(remove_equivalence(path1, path2))
    print('Equivalents for', path1, 'after removal:')
    for eq in list_equivalents(path1):
        print('  ', eq['path']) 