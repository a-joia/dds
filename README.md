# Database Description Server

A web application for exploring, describing, and relating database schemas, with support for field-level equivalence and possibly equivalence relationships.

## Features
- Browse clusters, databases, tables, fields, and subfields
- Edit field metadata (description, type, etc.)
- Add/remove Equivalence and Possibly Equivalence relationships between fields
- Visualize equivalence and possibly equivalence for each field and subfield

## Setup

### Quick Start: Docker Compose (Recommended)

You can run the entire stack (backend, frontend, and MCP server) using Docker Compose:

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up
```
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- MCP server:  http://localhost:8088

If you want to reset the database, simply delete `dbdesc.db` before running compose. The backend will recreate it automatically.

### Manual Setup

#### Backend (FastAPI + SQLite)
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the server (from the project root!):**
   ```bash
   uvicorn backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

   **Note:** Do NOT run `python main.py` from inside the `backend/` folder. Always run from the project root, or use `python -m backend.main`.

#### Frontend (React)
1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Run the frontend:**
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:3000`.

#### MCP Server
- The MCP server bridges the REST API to the Model Context Protocol (MCP) for LLM/agent integrations.
- It is started automatically with Docker Compose, or you can run it manually:
  ```bash
  python api/mcp_server.py
  ```

#### Docker

```bash
docker-compose  build

docker-compose  up
```

## Usage
- Browse clusters, databases, tables, and fields in the sidebar.
- Click a field to view its details and equivalence relationships.
- Click "Edit" to modify field metadata or manage equivalence/possibly equivalence edges.
- In the edit page, you can add or remove both types of edges using the provided UI.
- In the table view, you can see all equivalence and possibly equivalence relationships for each field/subfield.

## Edge Types
- **Equivalence:** Strong equivalence between fields (blue section)
- **Possibly Equivalence:** Weaker/uncertain equivalence (orange section)

## Development
- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React, TypeScript
- MCP Server: FastMCP, Python

## Troubleshooting
- **ImportError: attempted relative import with no known parent package**
  - This happens if you run `python main.py` from inside the `backend/` folder. Always run from the project root using `uvicorn backend.main:app --reload` or `python -m backend.main`.
- **Database file missing:**
  - The backend will automatically create a new, empty `dbdesc.db` if it does not exist.

## License
MIT 