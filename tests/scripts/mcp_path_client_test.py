import asyncio
from fastmcp import Client
import random
import string

def unique_name(prefix):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

client = Client("http://127.0.0.1:8088/mcp")

async def main():
    async with client:
        # --- Create ---
        cname = unique_name('cluster')
        dname = unique_name('db')
        tname = unique_name('table')
        fname = unique_name('field')
        print("Creating cluster:", cname)
        cluster = await client.call_tool("create_cluster", {"cluster_name": cname})
        print("Cluster:", cluster)
        db_path = f"{cname}/{dname}"
        print("Creating database:", db_path)
        db = await client.call_tool("create_database", {"path": db_path})
        print("Database:", db)
        table_path = f"{cname}/{dname}/{tname}"
        print("Creating table:", table_path)
        table = await client.call_tool("create_table", {"path": table_path})
        print("Table:", table)
        field_path = f"{cname}/{dname}/{tname}/{fname}"
        print("Creating field:", field_path)
        field = await client.call_tool("create_field", {"path": field_path, "meta": {"type": "int", "description": "desc"}})
        print("Field:", field)

        print("Editing field type...")
        await client.call_tool("edit_field_type", {"path": field_path, "type_value": "float"})

        # --- Edit ---
        print("Editing field description...")
        await client.call_tool("edit_field_description", {"path": field_path, "description": "newdesc"})
        print("Editing field example...")
        await client.call_tool("edit_field_example", {"path": field_path, "example": "eg1"})
        print("Editing field information...")
        await client.call_tool("edit_field_information", {"path": field_path, "information": "info1"})
        print("Adding field metadata...")
        await client.call_tool("add_field_metadata", {"path": field_path, "metadata": {"unit": "kg"}})
        print("Editing field metadata...")
        await client.call_tool("edit_field_metadata", {"path": field_path, "metadata": {"unit": "g"}})

        # --- Get ---
        print("Getting field...")
        field_info = await client.call_tool("get_field", {"path": field_path})
        print("Field info:", field_info)
        print("Getting field metadata...")
        meta = await client.call_tool("get_field_metadata", {"path": field_path})
        print("Field meta:", meta)

        # --- List ---
        print("Listing clusters...")
        clusters = await client.call_tool("list_clusters", {})
        print("Clusters:", clusters)
        print("Listing databases...")
        dbs = await client.call_tool("list_database", {"clusters": cname})
        print("Databases:", dbs)
        print("Listing fields...")
        fields = await client.call_tool("list_fields", {"path": table_path})
        print("Fields:", fields)
        print("Getting hierarchy...")
        hierarchy = await client.call_tool("get_hierarchy", {"path": table_path})
        print("Hierarchy:", hierarchy)

        # --- Edge ---
        fname2 = unique_name('field2')
        field_path2 = f"{cname}/{dname}/{tname}/{fname2}"
        print("Creating second field for edge:", field_path2)
        await client.call_tool("create_field", {"path": field_path2, "meta": {"type": "int"}})
        print("Adding edge...")
        await client.call_tool("add_edge", {"path1": field_path, "path2": field_path2})
        print("Getting edges...")
        edges = await client.call_tool("get_edges", {"path": field_path})
        print("Edges:", edges)
        print("Removing edge...")
        await client.call_tool("remove_edge", {"path1": field_path, "path2": field_path2})

        # --- Connected databases ---
        print("Getting connected databases...")
        connected = await client.call_tool("get_connected_databases", {"db_path": db_path})
        print("Connected databases:", connected)

        # --- Delete ---
        print("Deleting field2...")
        await client.call_tool("delete_field", {"path": field_path2})
        print("Deleting field...")
        await client.call_tool("delete_field", {"path": field_path})
        print("Deleting table...")
        await client.call_tool("delete_table", {"path": table_path})
        print("Deleting database...")
        await client.call_tool("delete_database", {"path": db_path})
        print("Deleting cluster...")
        await client.call_tool("delete_cluster", {"path": cname})
        print("All operations completed successfully.")

if __name__ == "__main__":
    asyncio.run(main()) 