export interface Field {
  id: number;
  name: string;
  meta?: Record<string, any>;
  subfields?: Field[];
}

export interface Table {
  id: number;
  name: string;
  fields?: Field[];
  meta?: Record<string, any>; // Allow for table description and metadata
}

export interface Database {
  id: number;
  name: string;
  tables?: Table[];
}

export interface Cluster {
  id: number;
  name: string;
  databases?: Database[];
}

export interface EquivalentNode {
  id: number;
  path: string;
}

export interface GraphNode {
  id: number;
  name: string;
  path: string;
  parent_id: number | null;
  meta: Record<string, any>;
}

export interface GraphEdge {
  id: number;
  from: number;
  to: number;
  from_path: string;
  to_path: string;
  type: string;
}

export interface ExternalConnection {
  edge_id: number;
  from_field_id: number;
  to_field_id: number;
  from_table: {
    id: number;
    name: string;
    database: string;
    cluster: string;
    path: string;
  };
  to_table: {
    id: number;
    name: string;
    database: string;
    cluster: string;
    path: string;
  };
  type: string;
}

export interface TableGraphData {
  table: {
    id: number;
    name: string;
  };
  nodes: GraphNode[];
  edges: GraphEdge[];
  external_connections: ExternalConnection[];
}

const API_URL = 'http://localhost:8000';

export async function fetchClusters(): Promise<Cluster[]> {
  const res = await fetch(`${API_URL}/clusters/`);
  if (!res.ok) throw new Error('Failed to fetch clusters');
  return res.json();
}

export async function fetchDatabases(clusterId: number): Promise<Database[]> {
  const res = await fetch(`${API_URL}/clusters/${clusterId}/databases/`);
  if (!res.ok) throw new Error('Failed to fetch databases');
  return res.json();
}

export async function fetchTables(databaseId: number): Promise<Table[]> {
  const res = await fetch(`${API_URL}/databases/${databaseId}/tables/`);
  if (!res.ok) throw new Error('Failed to fetch tables');
  return res.json();
}

export async function fetchFields(tableId: number): Promise<Field[]> {
  const res = await fetch(`${API_URL}/tables/${tableId}/fields/`);
  if (!res.ok) throw new Error('Failed to fetch fields');
  return res.json();
}

export async function fetchEquivalents(fieldPath: string): Promise<EquivalentNode[]> {
  const res = await fetch(`${API_URL}/fields/${fieldPath}/equivalence/`);
  if (!res.ok) throw new Error('Failed to fetch equivalents');
  const data = await res.json();
  return data.equivalents;
}

export async function addEquivalence(fromPath: string, toPath: string): Promise<void> {
  const res = await fetch(`${API_URL}/equivalence/?from_path=${encodeURIComponent(fromPath)}&to_path=${encodeURIComponent(toPath)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to add equivalence');
}

export async function removeEquivalence(fromPath: string, toPath: string): Promise<void> {
  const res = await fetch(`${API_URL}/equivalence/?from_path=${encodeURIComponent(fromPath)}&to_path=${encodeURIComponent(toPath)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to remove equivalence');
}

export async function fetchPossiblyEquivalents(fieldPath: string): Promise<EquivalentNode[]> {
  const res = await fetch(`${API_URL}/fields/${fieldPath}/possibly-equivalence/`);
  if (!res.ok) throw new Error('Failed to fetch possibly equivalents');
  const data = await res.json();
  return data.equivalents;
}

export async function addPossiblyEquivalence(fromPath: string, toPath: string): Promise<void> {
  const res = await fetch(`${API_URL}/possibly-equivalence/?from_path=${encodeURIComponent(fromPath)}&to_path=${encodeURIComponent(toPath)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to add possibly equivalence');
}

export async function removePossiblyEquivalence(fromPath: string, toPath: string): Promise<void> {
  const res = await fetch(`${API_URL}/possibly-equivalence/?from_path=${encodeURIComponent(fromPath)}&to_path=${encodeURIComponent(toPath)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to remove possibly equivalence');
}

export async function updateClusterByPath(clusterPath: string, data: Partial<Cluster>): Promise<Cluster> {
  const res = await fetch(`${API_URL}/clusters/by-path/${encodeURIComponent(clusterPath)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update cluster');
  return res.json();
}

export async function updateDatabaseByPath(cluster: string, database: string, data: Partial<Database>): Promise<Database> {
  const res = await fetch(`${API_URL}/databases/by-path/${encodeURIComponent(cluster)}/${encodeURIComponent(database)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update database');
  return res.json();
}

export async function updateTableByPath(cluster: string, database: string, table: string, data: Partial<Table>): Promise<Table> {
  const res = await fetch(`${API_URL}/tables/by-path/${encodeURIComponent(cluster)}/${encodeURIComponent(database)}/${encodeURIComponent(table)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update table');
  return res.json();
}

export async function updateFieldMetaByPath(fieldPath: string, meta: Record<string, any>): Promise<Field> {
  const res = await fetch(`${API_URL}/fields/by-path/${encodeURIComponent(fieldPath)}/meta`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(meta),
  });
  if (!res.ok) throw new Error('Failed to update field meta');
  return res.json();
}

export async function fetchTableGraph(tableId: number): Promise<TableGraphData> {
  const res = await fetch(`${API_URL}/tables/${tableId}/graph/`);
  if (!res.ok) throw new Error('Failed to fetch table graph');
  return res.json();
} 