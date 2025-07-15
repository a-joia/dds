import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from fastmcp import FastMCP
from api.path_client import PathClient
from typing import Any, Dict, Optional, List, Tuple
import asyncio

# Initialize the PathClient (connects to FastAPI backend)
client = PathClient(base_url="http://backend:8000")

# Create the FastMCP server
mcp = FastMCP("DBDesc MCP Bridge")

def _run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, lambda: func(*args, **kwargs))

# --- Create ---
@mcp.tool()
async def create_cluster(cluster_name: str) -> Any:
    return client.create_cluster(cluster_name)

@mcp.tool()
async def create_database(path: str) -> Any:
    return client.create_database(path)

@mcp.tool()
async def create_table(path: str) -> Any:
    return client.create_table(path)

@mcp.tool()
async def create_field(path: str, meta: Optional[Dict] = None) -> Any:
    return client.create_field(path, meta=meta)

# --- Edit ---
@mcp.tool()
async def edit_table_description(path: str, description: str) -> Any:
    return client.edit_table_description(path, description)

@mcp.tool()
async def edit_field_description(path: str, description: str) -> Any:
    return client.edit_field_description(path, description)

@mcp.tool()
async def edit_field_example(path: str, example: str) -> Any:
    return client.edit_field_example(path, example)

@mcp.tool()
async def edit_field_information(path: str, information: str) -> Any:
    return client.edit_field_information(path, information)

@mcp.tool()
async def add_field_metadata(path: str, metadata: Dict) -> Any:
    return client.add_field_metadata(path, metadata)

@mcp.tool()
async def edit_field_metadata(path: str, metadata: Dict) -> Any:
    return client.edit_field_metadata(path, metadata)

@mcp.tool()
async def edit_field_type(path: str, type_value: str) -> Any:
    return client.edit_field_type(path, type_value)

# --- Delete ---
@mcp.tool()
async def delete_cluster(path: str) -> Any:
    return client.delete_cluster(path)

@mcp.tool()
async def delete_database(path: str) -> Any:
    return client.delete_database(path)

@mcp.tool()
async def delete_table(path: str) -> Any:
    return client.delete_table(path)

@mcp.tool()
async def delete_field(path: str) -> Any:
    return client.delete_field(path)

# --- Get ---
@mcp.tool()
async def get_field(path: str) -> Any:
    return client.get_field(path)

@mcp.tool()
async def get_field_metadata(path: str, list_of_keys: Optional[List[str]] = None) -> Any:
    return client.get_field_metadata(path, list_of_keys)

# --- Edge ---
@mcp.tool()
async def add_edge(path1: str, path2: str) -> Any:
    return client.add_edge(path1, path2)

@mcp.tool()
async def remove_edge(path1: str, path2: str) -> Any:
    return client.remove_edge(path1, path2)

@mcp.tool()
async def get_edges(path: str) -> Any:
    return client.get_edges(path)

# --- List ---
@mcp.tool()
async def list_clusters() -> Any:
    return client.list_clusters()

@mcp.tool()
async def list_database(clusters: Optional[str] = None) -> Any:
    return client.list_database(clusters)

@mcp.tool()
async def list_fields(path: str = "") -> Any:
    return client.list_fields(path)

@mcp.tool()
async def get_hierarchy(path: str, filter: Optional[List[Tuple[str, Any]]] = None) -> Any:
    return client.get_hierarchy(path, filter)

@mcp.tool()
async def get_connected_databases(db_path: str) -> Any:
    return client.get_connected_databases(db_path)

if __name__ == "__main__":
    # Run the MCP server with HTTP transport on port 8088
    mcp.run(transport="http", host="0.0.0.0", port=8088) 