# Python API Client for Database Description Server

This package provides a Python client for interacting with the FastAPI backend server.

## Usage

1. Install dependencies (if not already):
   ```bash
   pip install requests
   ```

2. Example usage:
   ```python
   from api.client import DBDescClient

   client = DBDescClient(base_url="http://localhost:8000")

   # Create a cluster
   cluster = client.create_cluster("Test Cluster")
   print("Created cluster:", cluster)

   # List clusters
   clusters = client.get_clusters()
   print("Clusters:", clusters)

   # Create a database in the cluster
   db = client.create_database(cluster_id=cluster['id'], name="TestDB")
   print("Created database:", db)

   # Create a table in the database
   table = client.create_table(database_id=db['id'], name="TestTable")
   print("Created table:", table)

   # Add a field to the table
   field = client.create_field(table_id=table['id'], name="Field1", meta={"type": "int"})
   print("Created field:", field)

   # List fields in the table
   fields = client.get_fields(table_id=table['id'])
   print("Fields:", fields)
   ```

3. No authentication is required. 