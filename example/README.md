# Database Description Server Examples

This directory contains example scripts demonstrating how to use the Database Description Server API.

## Example Files

### Core Functionality Examples

- **`create_hierarchy.py`** - Basic example of creating clusters, databases, tables, and fields
- **`add_description.py`** - Example of adding markdown descriptions to fields and subfields
- **`equivalence_example.py`** - Example of creating and managing equivalence relationships between fields

### Path-Based API Examples

- **`create_new_nodes.py`** - Comprehensive test script for create/edit/delete operations with equivalences
- **`test_path_functions.py`** - Test script for the new path-based creation functions
- **`test_edit_by_path.py`** - Test script for field metadata editing and resource renaming
- **`edit_by_path_client_example.py`** - Simple example of using edit_by_path and rename_by_path functions

## Usage

To run any example:

```bash
python example/filename.py
```

Make sure the FastAPI server is running first:

```bash
uvicorn backend.main:app --reload
```

## Key Features Demonstrated

- **Hierarchical Data Creation**: Clusters → Databases → Tables → Fields → Subfields
- **Path-Based Operations**: Create and edit resources using path strings
- **Field Metadata**: Add descriptions, types, and constraints to fields
- **Equivalence Management**: Create equivalence and possibly equivalence relationships
- **Recursive Deletion**: Automatic cleanup of child resources and relationships 