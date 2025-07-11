import sys,os
sys.path.append(os.path.join( os.path.dirname(os.path.abspath(__file__)), ".."))
import requests
from fastmcp import FastMCP
from api.client import DBDescClient, edit_by_path, rename_by_path, get_cluster_by_path, get_database_by_path, get_table_by_path, get_field_by_path
from typing import Any, Dict, Optional
from api.client import print_hierarchy_by_path,create_field_by_path

# Initialize the API client (connects to FastAPI backend)
client = DBDescClient(base_url="http://localhost:8000")

# Create the FastMCP server
mcp = FastMCP("DBDesc MCP Bridge")

@mcp.tool()
async def list_clusters() -> Any:
    """List all clusters."""
    return client.get_clusters()

@mcp.tool()
async def create_cluster(name: str) -> Any:
    """Create a new cluster."""
    return client.create_cluster(name)


@mcp.tool()
async def create_database_by_path(path: str) -> Any:
    """
    Create a database by path.
    Args:
        path: Path in format 'cluster/database'.
            - cluster: Name of the cluster (must exist)
            - database: Name of the new database to create
    Returns: The created database object.
    """
    return client.create_database_by_path(path)

@mcp.tool()
async def create_table_by_path(path: str) -> Any:
    """
    Create a table by path.
    Args:
        path: Path in format 'cluster/database/table'.
            - cluster: Name of the cluster (must exist)
            - database: Name of the database (must exist)
            - table: Name of the new table to create
    Returns: The created table object.
    """
    return client.create_table_by_path(path)

@mcp.tool()
async def create_field_by_paths(path: str, meta: Optional[Dict] = None) -> Any:
    """
    Create a field or subfield by path.
    Args:
        path: Path in format 'cluster/database/table/field' or 'cluster/database/table/field/subfield/...'.
            - cluster: Name of the cluster (must exist)
            - database: Name of the database (must exist)
            - table: Name of the table (must exist)
            - field/subfield: Name(s) of the field and any parent subfields
    Returns: The created field object.
    """
    return client.create_field_by_path(path, meta=meta)

@mcp.tool()
async def edit_field_by_path(path: str, data: Dict) -> Any:
    """
    Edit field data by path.
    Args:
        path: Path in format 'cluster/database/table/field' or 'cluster/database/table/field/subfield/...'.
            - cluster: Name of the cluster
            - database: Name of the database
            - table: Name of the table
            - field/subfield: Name(s) of the field and any parent subfields
        data: Dictionary of metadata to update (e.g., {"description": str, "type": str, "examples":str, "information":str, "type-details":str , ...<any other extra key> })
    Returns: The updated field object.
    """
    return await _run_sync(edit_by_path, path, data)


@mcp.tool()
async def  print_hierarchy_by_paths(path: str):
    """
    Print the complete hierarchy below a given path.
    
    Args:
        path: path string (e.g., 'cluster', 'cluster/database', 'cluster/database/table')
        
    Examples:
        print_hierarchy_by_path("mycluster")  # Shows all databases, tables, fields
        print_hierarchy_by_path("mycluster/mydb")  # Shows all tables, fields
        print_hierarchy_by_path("mycluster/mydb/mytable")  # Shows all fields
    Output:
        The hierarchy of paths idented by space character
    """
    return print_hierarchy_by_path(path)

import asyncio

def _run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, lambda: func(*args, **kwargs))

if __name__ == "__main__":
    # Run the MCP server with HTTP transport on port 8080
    mcp.run(transport="http", host="0.0.0.0", port=8088) 