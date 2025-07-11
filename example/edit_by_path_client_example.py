import sys,os
sys.path.append(os.path.join( os.path.dirname(os.path.abspath(__file__)), ".."))
from api.client import edit_by_path, rename_by_path

# Example paths
cluster_name = 'mycluster'
database_name = 'mydatabase'
table_name = 'mytable'
field_path = f'{cluster_name}/{database_name}/{table_name}/myfield'

# 1. Rename cluster
result = rename_by_path(cluster_name, "mycluster_renamed")
print('Rename cluster:', result)

# 2. Rename database
result = rename_by_path(f'{cluster_name}/{database_name}', "mydatabase_renamed")
print('Rename database:', result)

# 3. Rename table
result = rename_by_path(f'{cluster_name}/{database_name}/{table_name}', "mytable_renamed")
print('Rename table:', result)

# 4. Edit field metadata (e.g., description)
result = edit_by_path(field_path, {"description": "Updated description via client!"})
print('Edit field metadata:', result) 