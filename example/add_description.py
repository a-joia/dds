import sys,os
sys.path.append(os.path.join( os.path.dirname(os.path.abspath(__file__)), ".."))
import requests
from api.client import DBDescClient

client = DBDescClient(base_url="http://localhost:8000")

# Ensure a cluster, database, table, and field exist
cluster = client.create_cluster("Example Cluster")
db = client.create_database(cluster_id=cluster['id'], name="ExampleDB")
table = client.create_table(database_id=db['id'], name="ExampleTable")
field = client.create_field(table_id=table['id'], name="Field1")

# Add a markdown description to the field
field_id = field['id']
meta = field.get('meta', {})
meta['description'] = """
# Field1

This is a **markdown** description for Field1.
- It supports lists
- And formatting
"""

resp = requests.patch(f"http://localhost:8000/fields/{field_id}/meta", json=meta)
print("Updated field:", resp.json())

# Create a subfield and add a description to it
subfield = client.create_field(table_id=table['id'], name="SubField1", parent_id=field_id)
subfield_id = subfield['id']
sub_meta = subfield.get('meta', {})
sub_meta['description'] = """
## SubField1

This is a _markdown_ description for SubField1.
- Subfields can have their own descriptions
- And formatting too
"""

resp2 = requests.patch(f"http://localhost:8000/fields/{subfield_id}/meta", json=sub_meta)
print("Updated subfield:", resp2.json()) 