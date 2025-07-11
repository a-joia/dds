import sys,os
sys.path.append(os.path.join( os.path.dirname(os.path.abspath(__file__)), ".."))
from api.client import DBDescClient

client = DBDescClient(base_url="http://localhost:8000")

# Create a cluster
test_cluster = client.create_cluster("acciatartaruswestus.westus")
print("Created cluster:", test_cluster)

# Create a database in the cluster
test_db = client.create_database(cluster_id=test_cluster['id'], name="PlatformUPAWest")
print("Created database:", test_db)

# Create a table in the database
test_table = client.create_table(database_id=test_db['id'], name="SecondVeryNiceTable")
print("Created table:", test_table)

# Add a field to the table
field = client.create_field(table_id=test_table['id'], name="Field1", meta={"type": "string"})
print("Created field:", field)

field = client.create_field(table_id=test_table['id'], name="Field2", meta={"type": "string"})
print("Created field:", field)

field = client.create_field(table_id=test_table['id'], name="Field3", meta={"type": "string"})
print("Created field:", field)


# Add a subfield to the field
subfield = client.create_field(table_id=test_table['id'], name="SubField1", parent_id=field['id'], meta={"type": "int"})
print("Created subfield:", subfield)

# Fetch and print the full field hierarchy
fields = client.get_fields(table_id=test_table['id'])
print("Field hierarchy:", fields) 