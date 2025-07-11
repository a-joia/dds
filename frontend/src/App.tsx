import React, { useEffect, useState } from 'react';
import './App.css';
import { Cluster, Database, Table, Field, fetchClusters, fetchDatabases, fetchTables, fetchFields, fetchEquivalents, addEquivalence, removeEquivalence, EquivalentNode, updateFieldMetaByPath, fetchPossiblyEquivalents, addPossiblyEquivalence, removePossiblyEquivalence, fetchTableGraph, TableGraphData } from './api';
import { GraphView } from './GraphView';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
  useParams,
  useLocation
} from 'react-router-dom';

// Minimal modern blue palette
const SIDEBAR_BG = '#1e2a38'; // main sidebar background
const CLUSTER_BG = '#254061'; // expanded cluster background
const TABLE_SELECTED_BORDER = '#4e8cff'; // blue left bar for selected table
const TABLE_HOVER_BORDER = '#497fc1'; // lighter blue for hover
const HOVER_BG = '#34547a'; // hover background for cluster/db
const TEXT_COLOR = '#fff';
const SUBTEXT_COLOR = '#b3c6e0';
const CARD_BG = '#fff';
const CARD_SHADOW = '0 2px 12px #0002';
const FIELD_BG = '#f7fafd';
const FIELD_BORDER = '#e3e8ee';
const FIELD_NAME_COLOR = '#1e2a38';
const FIELD_DESC_COLOR = '#3a4a5d';
const TYPE_PILL_BG = '#e6f0ff';
const TYPE_PILL_COLOR = '#2563eb';
const TYPE_PILL_BORDER = '#b3d0ff';
const SUBFIELD_BORDER = '#e3e8ee';
const FIELD_FONT = 'Montserrat, Inter, Segoe UI, Arial, sans-serif';

function FieldPage() {
  const { cluster, database, table, '*': fieldPath } = useParams();
  const navigate = useNavigate();
  const [meta, setMeta] = React.useState<Record<string, any> | null>(null);
  const [originalMeta, setOriginalMeta] = React.useState<Record<string, any> | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [equivalents, setEquivalents] = React.useState<any[]>([]);
  const [editMode, setEditMode] = React.useState(false);
  // Add this constant at the top of FieldPage
  const EDITABLE_FIELDS = ['type', 'type-details', 'description', 'information', 'examples'];
  const TYPE_OPTIONS = ['boolean', 'datetime', 'decimal', 'guid', 'int', 'long', 'real', 'string', 'timespan', 'dynamic'];

  const fullPath = `${cluster}/${database}/${table}${fieldPath ? '/' + fieldPath : ''}`;

  React.useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`http://localhost:8000/fields/by-path/${encodeURIComponent(fullPath)}/meta`)
      .then(res => {
        console.log('Fetch status:', res.status);
        if (!res.ok) throw new Error('Failed to load');
        return res.json();
      })
      .then(data => {
        console.log('Field meta response:', data);
        let meta = data.meta || {};
        if (!('description' in meta)) {
          meta.description = '';
        }
        if (!('information' in meta)) {
          meta.information = '';
        }
        if (!('examples' in meta)) {
          meta.examples = '';
        }
        setMeta(meta);
        setOriginalMeta(meta);
        setLoading(false);
      })
      .catch(e => {
        console.error('Error in fetch:', e);
        setError('Failed to load field');
        setLoading(false);
      });
    fetchEquivalents(fullPath)
      .then(setEquivalents)
      .catch(() => setEquivalents([]));
  }, [fullPath]);

  const handleChange = (key: string, value: any) => {
    setMeta(m => ({ ...m, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await updateFieldMetaByPath(fullPath, meta || {});
      setOriginalMeta(meta);
      setEditMode(false);
    } catch (e: any) {
      setError('Failed to save changes');
    }
    setSaving(false);
  };

  const handleCancel = () => {
    setMeta(originalMeta);
    setEditMode(false);
  };

  if (loading) return <div style={{ padding: 40 }}>Loading...</div>;
  if (error) return <div style={{ padding: 40, color: '#b91c1c' }}>{error}</div>;

  return (
    <div style={{ padding: '40px 0', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 18 }}>
        <button onClick={() => navigate('/')} style={{ background: '#f3f4f6', border: 'none', borderRadius: 6, padding: '7px 18px', cursor: 'pointer', color: '#2563eb', fontWeight: 600 }}>← Back to Table</button>
        {!editMode && (
          <button onClick={() => setEditMode(true)} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '7px 18px', fontWeight: 600, cursor: 'pointer', fontSize: 15 }}>Edit</button>
        )}
      </div>
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.03)', padding: '28px 48px', position: 'relative', width: '90%', maxWidth: 900, margin: '0 auto' }}>
        <div style={{ fontSize: 26, fontWeight: 800, color: '#2563eb', marginBottom: 8 }}>{fieldPath ? fieldPath.split('/').slice(-1)[0] : table}</div>
        <div style={{ color: '#6b7280', fontSize: 15, marginBottom: 18 }}>
          Path: <span style={{ color: '#222' }}>{fullPath}</span>
        </div>
        {/* Meta fields */}
        {editMode ? (
          EDITABLE_FIELDS.map(key => (
            <div key={key} style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>{key.charAt(0).toUpperCase() + key.slice(1)}</div>
              {key === 'type' ? (
                <select
                  value={meta?.[key] || ''}
                  onChange={e => handleChange(key, e.target.value)}
                  style={{ width: '100%', borderRadius: 6, border: '1px solid #e5e7eb', padding: 8, fontSize: 15 }}
                >
                  <option value="">Select type...</option>
                  {TYPE_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : key === 'description' || key === 'information' || key === 'examples' ? (
                <textarea
                  value={meta?.[key] || ''}
                  onChange={e => handleChange(key, e.target.value)}
                  rows={4}
                  style={{ width: '100%', borderRadius: 6, border: '1px solid #e5e7eb', padding: 8, fontSize: 15 }}
                />
              ) : (
                <input
                  value={meta?.[key] || ''}
                  onChange={e => handleChange(key, e.target.value)}
                  style={{ width: '100%', borderRadius: 6, border: '1px solid #e5e7eb', padding: 8, fontSize: 15 }}
                />
              )}
            </div>
          ))
        ) : (
          meta && Object.keys(meta).length > 0 ? (
            <>
              {/* Description label and content */}
              <div style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>Description</div>
              <div style={{ color: '#222', fontSize: 15, background: '#f8fafc', borderRadius: 6, padding: '7px 12px', minHeight: 28, marginBottom: 16 }}>
                {meta.description && meta.description.trim() !== '' ? (
                  <ReactMarkdown
                    components={{
                      code({node, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = (props && 'inline' in props) ? (props as any).inline : false;
                        function omitRef(props: any) {
                          const { ref, ...rest } = props;
                          return rest;
                        }
                        return !isInline && match ? (
                          <SyntaxHighlighter
                            style={dracula as any}
                            language={match[1]}
                            PreTag="div"
                            {...omitRef(props)}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>{children}</code>
                        );
                      }
                    }}
                  >
                    {meta.description}
                  </ReactMarkdown>
                ) : (
                  <span style={{ color: '#888' }}>No description available</span>
                )}
              </div>
              {/* Information label and content */}
              <div style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>Information</div>
              <div style={{ color: '#222', fontSize: 15, background: '#f8fafc', borderRadius: 6, padding: '7px 12px', minHeight: 28, marginBottom: 16 }}>
                {meta.information && meta.information.trim() !== '' ? (
                  <ReactMarkdown
                    components={{
                      code({node, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = (props && 'inline' in props) ? (props as any).inline : false;
                        function omitRef(props: any) {
                          const { ref, ...rest } = props;
                          return rest;
                        }
                        return !isInline && match ? (
                          <SyntaxHighlighter
                            style={dracula as any}
                            language={match[1]}
                            PreTag="div"
                            {...omitRef(props)}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>{children}</code>
                        );
                      }
                    }}
                  >
                    {meta.information}
                  </ReactMarkdown>
                ) : (
                  <span style={{ color: '#888' }}>No information available</span>
                )}
              </div>
              {/* Examples label and content */}
              <div style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>Examples</div>
              <div style={{ color: '#222', fontSize: 15, background: '#f8fafc', borderRadius: 6, padding: '7px 12px', minHeight: 28, marginBottom: 16 }}>
                {meta.examples && meta.examples.trim() !== '' ? (
                  <ReactMarkdown
                    components={{
                      code({node, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = (props && 'inline' in props) ? (props as any).inline : false;
                        function omitRef(props: any) {
                          const { ref, ...rest } = props;
                          return rest;
                        }
                        return !isInline && match ? (
                          <SyntaxHighlighter
                            style={dracula as any}
                            language={match[1]}
                            PreTag="div"
                            {...omitRef(props)}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>{children}</code>
                        );
                      }
                    }}
                  >
                    {meta.examples}
                  </ReactMarkdown>
                ) : (
                  <span style={{ color: '#888' }}>No examples available</span>
                )}
              </div>
              {/* Render other meta fields if any, except description/information/examples/type/type-details */}
              {Object.entries(meta).map(([key, value]) => (
                !['description', 'information', 'examples', 'type', 'type-details'].includes(key) && (
                  <div key={key} style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                    <div style={{ color: '#222', fontSize: 15, background: '#f8fafc', borderRadius: 6, padding: '7px 12px', minHeight: 28 }}>{value || <span style={{ color: '#888' }}>No value</span>}</div>
                  </div>
                )
              ))}
            </>
          ) : (
            <div style={{ color: '#888', marginBottom: 16 }}>No metadata available.</div>
          )
        )}
        {/* Save/Cancel buttons (edit mode only) */}
        {editMode && (
          <div style={{ display: 'flex', gap: 12, marginTop: 10 }}>
            <button onClick={handleSave} disabled={saving} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 22px', fontWeight: 700, cursor: 'pointer', fontSize: 15 }}>Save</button>
            <button onClick={handleCancel} disabled={saving} style={{ background: '#f3f4f6', color: '#222', border: 'none', borderRadius: 6, padding: '8px 22px', fontWeight: 600, cursor: 'pointer', fontSize: 15 }}>Cancel</button>
          </div>
        )}
        {/* Equivalence section */}
        <div style={{ marginTop: 28 }}>
          <div style={{ fontWeight: 700, color: '#2563eb', fontSize: 17, marginBottom: 6 }}>Equivalence</div>
          {equivalents.length > 0 ? (
            <ul style={{ paddingLeft: 18, color: '#1e2a38', fontSize: 15 }}>
              {equivalents.map(eq => (
                <li key={eq.id} style={{ display: 'flex', alignItems: 'center', gap: 8, position: 'relative', padding: '2px 0' }}>
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{eq.path}</span>
                  {editMode && (
                    <RemoveEquivalenceButton currentPath={fullPath} eqPath={eq.path} onRemoved={() => fetchEquivalents(fullPath).then(setEquivalents)} />
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ color: '#888' }}>No equivalents.</div>
          )}
          {editMode && (
            <div style={{ marginTop: 24, background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', padding: '24px 32px', maxWidth: 520, marginLeft: 'auto', marginRight: 'auto' }}>
              <div style={{ fontWeight: 700, color: '#2563eb', fontSize: 18, marginBottom: 12, letterSpacing: 0.5 }}>Add Equivalence</div>
              <AddEquivalenceForm currentPath={fullPath} onAdded={() => fetchEquivalents(fullPath).then(setEquivalents)} />
            </div>
          )}
        </div>
        {/* Possibly Equivalence section */}
        <div style={{ marginTop: 36 }}>
          <div style={{ fontWeight: 700, color: '#b45309', fontSize: 17, marginBottom: 6 }}>Possibly Equivalence</div>
          <PossiblyEquivalenceSection currentPath={fullPath} editMode={editMode} />
        </div>
      </div>
    </div>
  );
}

function App() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCluster, setExpandedCluster] = useState<number | null>(null);
  const [expandedDatabase, setExpandedDatabase] = useState<number | null>(null);
  const [databases, setDatabases] = useState<Record<number, Database[]>>({});
  const [tables, setTables] = useState<Record<number, Table[]>>({});
  const [selectedTable, setSelectedTable] = useState<{ clusterId: number, dbId: number, tableId: number } | null>(null);
  const [fields, setFields] = useState<Field[] | null>(null);
  const [showGraph, setShowGraph] = useState(false);
  const [graphData, setGraphData] = useState<TableGraphData | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [includedTables, setIncludedTables] = useState<Set<number>>(new Set());
  const navigate = useNavigate();
  const [layoutMode, setLayoutMode] = useState<'force' | 'hierarchy'>('force');

  // Layout parameter state
  const [hierarchyYScale, setHierarchyYScale] = useState(1);
  const [hierarchyXScale, setHierarchyXScale] = useState(1);
  const [hierarchyLabelRotation, setHierarchyLabelRotation] = useState(0);
  const [forceLinkDistance, setForceLinkDistance] = useState(100);
  const [forceChargeStrength, setForceChargeStrength] = useState(-300);
  const [forceCollisionRadius, setForceCollisionRadius] = useState(30);
  const [forceCenterStrength, setForceCenterStrength] = useState(1);

  useEffect(() => {
    setLoading(true);
    fetchClusters()
      .then(data => {
        setClusters(data);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const handleExpandCluster = (clusterId: number) => {
    setExpandedCluster(clusterId === expandedCluster ? null : clusterId);
    if (!databases[clusterId]) {
      fetchDatabases(clusterId).then(dbs => {
        setDatabases(prev => ({ ...prev, [clusterId]: dbs }));
      });
    }
  };

  const handleExpandDatabase = (dbId: number, clusterId: number) => {
    setExpandedDatabase(dbId === expandedDatabase ? null : dbId);
    if (!tables[dbId]) {
      fetchTables(dbId).then(tbls => {
        setTables(prev => ({ ...prev, [dbId]: tbls }));
      });
    }
  };

  const handleSelectTable = (clusterId: number, dbId: number, tableId: number) => {
    setSelectedTable({ clusterId, dbId, tableId });
    setFields(null);
    fetchFields(tableId).then(setFields);
    navigate('/'); // Return to main table view
  };

  const handleShowGraph = async () => {
    if (!selectedTable) return;
    
    setGraphLoading(true);
    try {
      const data = await fetchTableGraph(selectedTable.tableId);
      setGraphData(data);
      setIncludedTables(new Set([selectedTable.tableId]));
      setShowGraph(true);
    } catch (error) {
      console.error('Failed to load graph:', error);
    } finally {
      setGraphLoading(false);
    }
  };

  const handleCloseGraph = () => {
    setShowGraph(false);
    setGraphData(null);
    setIncludedTables(new Set());
  };

  const handleRemoveFieldFromGraph = async (fieldId: number) => {
    // This would need to be implemented to actually remove the field from the database
    console.log('Remove field:', fieldId);
    // For now, just close the graph
    handleCloseGraph();
  };

  const handleAddTableToGraph = async (tableId: number) => {
    if (includedTables.has(tableId)) {
      console.log('Table already included:', tableId);
      return;
    }
    
    setGraphLoading(true);
    try {
      // Fetch the new table's graph data
      const newTableData = await fetchTableGraph(tableId);
      
      // Merge the data
      if (graphData) {
        // Create a new table node ID for the new table to avoid conflicts
        const newTableNodeId = -(Math.max(...graphData.nodes.map(n => Math.abs(n.id))) + 1);
        
        // Update the new table's nodes to use the new table node ID
        const updatedNewNodes = newTableData.nodes.map(node => {
          if (node.id === -1) { // This is the table node
            return { ...node, id: newTableNodeId };
          } else if (node.parent_id === -1) { // This is a root field that should connect to the new table node
            return { ...node, parent_id: newTableNodeId };
          }
          return node;
        });
        
        // Update the new table's edges to use the new table node ID
        const updatedNewEdges = newTableData.edges.map(edge => {
          if (edge.from === -1) {
            return { ...edge, from: newTableNodeId };
          }
          if (edge.to === -1) {
            return { ...edge, to: newTableNodeId };
          }
          return edge;
        });

        // Find cross-table equivalence edges from external connections
        const crossTableEdges = [];
        for (const extConn of graphData.external_connections) {
          if (extConn.from_table.id === tableId || extConn.to_table.id === tableId) {
            // This external connection involves the table we're adding
            // Use the field IDs from the external connection
            const fromFieldId = extConn.from_field_id;
            const toFieldId = extConn.to_field_id;
            
            // Determine which field belongs to the new table and which belongs to the existing graph
            let newTableFieldId: number, existingFieldId: number;
            if (extConn.from_table.id === tableId) {
              newTableFieldId = fromFieldId;
              existingFieldId = toFieldId;
            } else {
              newTableFieldId = toFieldId;
              existingFieldId = fromFieldId;
            }
            
            // Check if the existing field is in the current graph
            const existingField = graphData.nodes.find(node => node.id === existingFieldId);
            
            if (existingField) {
              // Find the new table field to get its path
              const newTableField = updatedNewNodes.find(node => node.id === newTableFieldId);
              
              if (newTableField) {
                // Create the cross-table equivalence edge
                crossTableEdges.push({
                  id: -(Math.max(...graphData.nodes.map(n => Math.abs(n.id))) + crossTableEdges.length + 1),
                  from: newTableFieldId,
                  to: existingFieldId,
                  from_path: newTableField.path,
                  to_path: existingField.path,
                  type: extConn.type
                });
              }
            }
          }
        }
        
        const mergedData: TableGraphData = {
          table: graphData.table, // Keep the original table as primary
          nodes: [...graphData.nodes, ...updatedNewNodes],
          edges: [...graphData.edges, ...updatedNewEdges, ...crossTableEdges],
          external_connections: [...graphData.external_connections, ...newTableData.external_connections]
        };
        
        setGraphData(mergedData);
        setIncludedTables(prev => new Set(Array.from(prev).concat(tableId)));
      }
    } catch (error) {
      console.error('Failed to add table to graph:', error);
    } finally {
      setGraphLoading(false);
    }
  };

  const handleRemoveTableFromGraph = (tableId: number) => {
    if (!includedTables.has(tableId) || !graphData) return;

    // Remove all nodes belonging to the table
    const nodesToRemove = new Set(
      graphData.nodes.filter(node => {
        // Table node: id === -1 or negative and path includes table name
        if (node.id === -1 && graphData.table.id === tableId) return true;
        // For merged graphs, table node id is negative and matches tableId
        if (node.meta && node.meta.type === 'table' && node.id < 0 && node.id !== -1) {
          // Try to match by table name or id in path
          return node.path && node.path.split('/')[2] === String(tableId);
        }
        // Field nodes: check if their path includes the table name or their parent table id
        if (node.path && node.path.split('/')[2] === String(tableId)) return true;
        return false;
      }).map(node => node.id)
    );

    // Remove all edges connected to those nodes
    const newEdges = graphData.edges.filter(edge =>
      !nodesToRemove.has(edge.from) && !nodesToRemove.has(edge.to)
    );

    // Remove nodes
    const newNodes = graphData.nodes.filter(node => !nodesToRemove.has(node.id));

    // Remove external_connections related to this table
    const newExternalConnections = graphData.external_connections.filter(conn =>
      conn.from_table.id !== tableId && conn.to_table.id !== tableId
    );

    // Remove table from includedTables
    const newIncludedTables = new Set(includedTables);
    newIncludedTables.delete(tableId);

    setGraphData({
      ...graphData,
      nodes: newNodes,
      edges: newEdges,
      external_connections: newExternalConnections,
    });
    setIncludedTables(newIncludedTables);
  };

  // Helper to get names for selected table
  const getSelectedNames = () => {
    if (!selectedTable) return { cluster: '', db: '', table: '' };
    const cluster = clusters.find(c => c.id === selectedTable.clusterId);
    const db = cluster?.databases?.find(d => d.id === selectedTable.dbId);
    const table = db?.tables?.find(t => t.id === selectedTable.tableId);
    return {
      cluster: cluster?.name || '',
      db: db?.name || '',
      table: table?.name || '',
    };
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'Segoe UI, Arial, sans-serif' }}>
      <aside style={{
        width: 300,
        background: SIDEBAR_BG,
        color: TEXT_COLOR,
        padding: 0,
        overflowY: 'auto',
        borderRight: '1px solid #22304a',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
      }}>
        <div style={{ padding: '28px 24px 16px 24px', borderBottom: '1px solid #22304a', fontWeight: 700, fontSize: 22, letterSpacing: 1, background: 'rgba(30,42,56,0.95)', zIndex: 2 }}>
          Clusters
        </div>
        {/* Make this area scrollable */}
        <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
          {loading && <div style={{ padding: 24, color: SUBTEXT_COLOR }}>Loading...</div>}
          {error && <div style={{ color: '#ff6b6b', padding: 24 }}>{error}</div>}
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {clusters.map(cluster => (
              <li key={cluster.id}>
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: 17,
                    margin: '14px 0 6px 0',
                    padding: '10px 18px',
                    borderRadius: 6,
                    background: expandedCluster === cluster.id ? CLUSTER_BG : 'none',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onClick={() => handleExpandCluster(cluster.id)}
                  onMouseOver={e => (e.currentTarget.style.background = HOVER_BG)}
                  onMouseOut={e => (e.currentTarget.style.background = expandedCluster === cluster.id ? CLUSTER_BG : 'none')}
                >
                  {cluster.name}
                </div>
                {expandedCluster === cluster.id && databases[cluster.id] && (
                  <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0 }}>
                    {databases[cluster.id].map(db => (
                      <li key={db.id}>
                        <div
                          style={{
                            fontWeight: 500,
                            fontSize: 15,
                            margin: '6px 0 4px 0',
                            padding: '8px 36px',
                            borderRadius: 5,
                            background: 'none', // No background for database
                            cursor: 'pointer',
                            color: SUBTEXT_COLOR,
                            transition: 'color 0.2s',
                          }}
                          onClick={() => handleExpandDatabase(db.id, cluster.id)}
                          onMouseOver={e => (e.currentTarget.style.background = HOVER_BG)}
                          onMouseOut={e => (e.currentTarget.style.background = 'none')}
                        >
                          {db.name}
                        </div>
                        {expandedDatabase === db.id && tables[db.id] && (
                          <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0 }}>
                            {tables[db.id].map(table => (
                              <li key={table.id}>
                                <button
                                  style={{
                                    background: 'none',
                                    color: selectedTable && selectedTable.tableId === table.id ? '#fff' : SUBTEXT_COLOR,
                                    border: 'none',
                                    cursor: 'pointer',
                                    textAlign: 'left',
                                    padding: '8px 54px',
                                    borderRadius: 5,
                                    width: '100%',
                                    fontWeight: selectedTable && selectedTable.tableId === table.id ? 600 : 400,
                                    fontSize: 15,
                                    margin: '3px 0',
                                    boxShadow: 'none',
                                    borderLeft: selectedTable && selectedTable.tableId === table.id ? `4px solid ${TABLE_SELECTED_BORDER}` : '4px solid transparent',
                                    transition: 'border 0.2s, color 0.2s',
                                  }}
                                  onClick={() => handleSelectTable(cluster.id, db.id, table.id)}
                                  onMouseOver={e => (e.currentTarget.style.borderLeft = `4px solid ${TABLE_HOVER_BORDER}`)}
                                  onMouseOut={e => (e.currentTarget.style.borderLeft = selectedTable && selectedTable.tableId === table.id ? `4px solid ${TABLE_SELECTED_BORDER}` : '4px solid transparent')}
                                >
                                  {table.name}
                                </button>
                              </li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </div>
        {/* Team name at the bottom */}
        <div style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 32,
          textAlign: 'center',
          color: '#b3c6e0',
          fontWeight: 700,
          fontSize: 14,
          letterSpacing: 2,
          opacity: 0.7,
          userSelect: 'none',
        }}>
          ACCIA Database Explorer
        </div>
      </aside>
      <main style={{ flex: 1, padding: 0, background: '#f8fafc', overflowY: 'auto' }}>
        <Routes>
          <Route path="/field/:cluster/:database/:table/*" element={<FieldPage />} />
          <Route path="*" element={
            <div style={{ padding: 40 }}>
              {/* The original main content goes here (table view) */}
              {selectedTable ? (
                <div>
                  {/* Table header card */}
                  <div style={{
                    background: '#f8fafc',
                    boxShadow: 'none',
                    borderRadius: 0,
                    padding: '0 0 18px 0',
                    marginBottom: 32,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    gap: 8,
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center', 
                      width: '100%',
                      marginBottom: 2 
                    }}>
                      <div style={{ fontSize: 28, fontWeight: 800, color: '#2563eb' }}>
                        {getSelectedNames().table}
                      </div>
                      <button
                        onClick={handleShowGraph}
                        disabled={graphLoading}
                        style={{
                          background: '#2563eb',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '10px 20px',
                          cursor: graphLoading ? 'not-allowed' : 'pointer',
                          fontSize: '14px',
                          fontWeight: 600,
                          opacity: graphLoading ? 0.6 : 1
                        }}
                      >
                        {graphLoading ? 'Loading...' : 'View Graph'}
                      </button>
                    </div>
                    <div style={{ color: '#6b7a90', fontSize: 17, fontWeight: 500 }}>
                      Cluster: <span style={{ color: '#222', fontWeight: 600 }}>{getSelectedNames().cluster}</span> &nbsp;|&nbsp; Database: <span style={{ color: '#222', fontWeight: 600 }}>{getSelectedNames().db}</span>
                    </div>
                  </div>
                  {/* Fields panel */}
                  <div style={{
                    background: 'none',
                    boxShadow: 'none',
                    borderRadius: 0,
                    padding: 0,
                    minHeight: 200,
                  }}>
                    {fields ? (
                      fields.length > 0 ? (
                        <FieldTree fields={fields} level={0} clusterName={getSelectedNames().cluster} dbName={getSelectedNames().db} tableName={getSelectedNames().table} parentPath={`${getSelectedNames().cluster}/${getSelectedNames().db}/${getSelectedNames().table}`} idToPathMap={{}} />
                      ) : (
                        <div style={{ color: '#888' }}>No fields found for this table.</div>
                      )
                    ) : (
                      <div>Loading fields...</div>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', marginTop: 80 }}>
                  <h2 style={{ fontSize: 28, color: '#4e8cff', marginBottom: 12 }}>Welcome</h2>
                  <p style={{ color: '#555', fontSize: 18 }}>Select a table from the sidebar to view its fields and subfields.</p>
                </div>
              )}
            </div>
          } />
        </Routes>
      </main>
      
      {/* Graph View Modal */}
      {showGraph && graphData && (
        <>
          <GraphView
            graphData={graphData}
            onClose={handleCloseGraph}
            onRemoveField={handleRemoveTableFromGraph}
            onAddTable={handleAddTableToGraph}
            includedTables={includedTables}
            setGraphData={setGraphData}
            setIncludedTables={setIncludedTables}
            layoutMode={layoutMode}
            setLayoutMode={setLayoutMode}
            // Hierarchy params
            hierarchyYScale={hierarchyYScale}
            setHierarchyYScale={setHierarchyYScale}
            hierarchyXScale={hierarchyXScale}
            setHierarchyXScale={setHierarchyXScale}
            hierarchyLabelRotation={hierarchyLabelRotation}
            setHierarchyLabelRotation={setHierarchyLabelRotation}
            // Force params
            forceLinkDistance={forceLinkDistance}
            setForceLinkDistance={setForceLinkDistance}
            forceChargeStrength={forceChargeStrength}
            setForceChargeStrength={setForceChargeStrength}
            forceCollisionRadius={forceCollisionRadius}
            setForceCollisionRadius={setForceCollisionRadius}
            forceCenterStrength={forceCenterStrength}
            setForceCenterStrength={setForceCenterStrength}
          />
        </>
      )}
    </div>
  );
}

function FieldTree({ fields, level, clusterName, dbName, tableName, parentPath, idToPathMap }: { fields: Field[]; level: number; clusterName: string; dbName: string; tableName: string; parentPath: string; idToPathMap: Record<number, string> }) {
  const [equivalentsMap, setEquivalentsMap] = React.useState<Record<string, EquivalentNode[]>>({});
  const [loadingEq, setLoadingEq] = React.useState<Record<string, boolean>>({});
  const navigate = useNavigate();

  React.useEffect(() => {
    fields.forEach(field => {
      const path = `${parentPath}/${field.name}`;
      if (equivalentsMap[path] === undefined) {
        setLoadingEq(prev => ({ ...prev, [path]: true }));
        fetchEquivalents(path)
          .then(eq => setEquivalentsMap(prev => ({ ...prev, [path]: eq })))
          .catch(() => setEquivalentsMap(prev => ({ ...prev, [path]: [] })))
          .finally(() => setLoadingEq(prev => ({ ...prev, [path]: false })));
      }
    });
  }, [fields, parentPath]);

  function buildIdToPathMap(fields: Field[], currentPath: string, map: Record<number, string>) {
    for (const f of fields) {
      const path = `${currentPath}/${f.name}`;
      map[f.id] = path;
      if (f.subfields && f.subfields.length > 0) {
        buildIdToPathMap(f.subfields, path, map);
      }
    }
  }

  // Only build the map at the top level
  React.useEffect(() => {
    if (level === 0) {
      const map: Record<number, string> = {};
      buildIdToPathMap(fields, parentPath, map);
      // Pass the map down via props
      // setIdToPathMap(map); // This state is now managed by the parent component
    }
  }, [fields, parentPath, level]);

  // State to hold the id-to-path map at the top level
  const [idToPathMapState, setIdToPathMap] = React.useState<Record<number, string>>(idToPathMap || {});
  const effectiveIdToPathMap = level === 0 ? idToPathMapState : idToPathMap;

  // State for expanded/collapsed equivalence sections
  const [expandedEq, setExpandedEq] = React.useState<Record<string, boolean>>({});

  const toggleEquivalence = (path: string) => {
    setExpandedEq(prev => ({ ...prev, [path]: !prev[path] }));
  };

  // State for expanded/collapsed fields
  const [expandedFields, setExpandedFields] = React.useState<Record<string, boolean>>(() => ({}));

  const toggleField = (path: string) => {
    setExpandedFields(prev => ({ ...prev, [path]: !prev[path] }));
  };

  return (
    <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0 }}>
      {fields.map((field: Field, idx: number) => {
        const path = `${parentPath}/${field.name}`;
        // Calculate margin for vertical spacing
        // For top-level fields, reduce vertical space between fields
        // For subfields, increase vertical space between field and subfields
        const isLast = idx === fields.length - 1;
        let liStyle: React.CSSProperties = {
          margin: level === 0 ? (isLast ? '0 0 18px 0' : '0 0 10px 0') : '0 0 14px 0', // less space between top-level fields, more between field and subfield
        };
        return (
          <li key={field.id} style={liStyle}>
            <div style={{
              background: level === 0 ? '#fff' : CARD_BG,
              border: level === 0 ? 'none' : `1px solid #e5e7eb`,
              borderLeft: level === 0 ? 'none' : '1px solid #e5e7eb',
              borderRadius: level === 0 ? 8 : 7,
              padding: level === 0 ? '18px 22px' : '14px 18px',
              marginLeft: 0,
              minWidth: 0,
              position: 'relative',
              zIndex: 1,
              transition: 'box-shadow 0.2s',
              boxShadow: level === 0 ? '0 1px 4px rgba(0,0,0,0.02)' : 'none',
              marginTop: 0,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                <span
                  style={{ cursor: 'pointer', userSelect: 'none', marginRight: 8, fontSize: 11 }}
                  onClick={() => toggleField(path)}
                >
                  {expandedFields[path] !== false ? '▼' : '▶'}
                </span>
                <span
                  style={{
                    fontFamily: FIELD_FONT,
                    fontWeight: level === 0 ? 800 : 400,
                    fontSize: level === 0 ? 17 : 14,
                    color: '#2563eb',
                    marginRight: 12,
                    letterSpacing: 0.5,
                    cursor: 'pointer',
                    textDecoration: 'none',
                    transition: 'color 0.2s',
                  }}
                  onClick={() => {
                    // Build the field path for the URL
                    const fieldPath = path.split('/').slice(3).join('/');
                    navigate(`/field/${clusterName}/${dbName}/${tableName}/${fieldPath}`);
                  }}
                  onMouseOver={e => (e.currentTarget.style.color = '#1d4ed8')}
                  onMouseOut={e => (e.currentTarget.style.color = '#2563eb')}
                >
                  {field.name}
                </span>
                {field.meta && field.meta.type && (
                  <span style={{
                    background: '#e0e7ff',
                    color: '#3730a3',
                    borderRadius: 8,
                    fontSize: 13,
                    fontWeight: 600,
                    padding: '2px 10px',
                    marginLeft: 2,
                    letterSpacing: 0.5,
                    userSelect: 'none',
                  }}>
                    {field.meta.type}
                  </span>
                )}
              </div>
              {expandedFields[path] === true && (
                <>
                  {/* Description label and content */}
                  <div style={{ marginBottom: 4, marginLeft: 2, fontWeight: 600, color: '#374151', fontSize: 15 }}>Description</div>
                  <div style={{ marginBottom: 8, marginLeft: 2, background: FIELD_BG, borderRadius: 8, padding: level === 0 ? '10px 18px' : '8px 14px', fontSize: 15, color: FIELD_DESC_COLOR, boxShadow: 'none' }}>
                    {field.meta && field.meta.description && field.meta.description.trim() !== '' ? (
                      <ReactMarkdown>{field.meta.description}</ReactMarkdown>
                    ) : (
                      'No description available'
                    )}
                  </div>
                  {/* Information label and content */}
                  <div style={{ marginBottom: 4, marginLeft: 2, fontWeight: 600, color: '#374151', fontSize: 15 }}>Information</div>
                  <div style={{ marginBottom: 8, marginLeft: 2, background: FIELD_BG, borderRadius: 8, padding: level === 0 ? '10px 18px' : '8px 14px', fontSize: 15, color: FIELD_DESC_COLOR, boxShadow: 'none' }}>
                    {field.meta && field.meta.information && field.meta.information.trim() !== '' ? (
                      <ReactMarkdown>{field.meta.information}</ReactMarkdown>
                    ) : (
                      <span style={{ color: '#888' }}>No information available</span>
                    )}
                  </div>
                  {/* Examples label and content */}
                  <div style={{ marginBottom: 4, marginLeft: 2, fontWeight: 600, color: '#374151', fontSize: 15 }}>Examples</div>
                  <div style={{ marginBottom: 8, marginLeft: 2, background: FIELD_BG, borderRadius: 8, padding: level === 0 ? '10px 18px' : '8px 14px', fontSize: 15, color: FIELD_DESC_COLOR, boxShadow: 'none' }}>
                    {field.meta && field.meta.examples && field.meta.examples.trim() !== '' ? (
                      <ReactMarkdown>{field.meta.examples}</ReactMarkdown>
                    ) : (
                      <span style={{ color: '#888' }}>No examples available</span>
                    )}
                  </div>
                  {field.subfields && field.subfields.length > 0 && (
                    <>
                      <div style={{ margin: '8px 0 4px 2px', fontWeight: 600, color: '#374151', fontSize: 15 }}>Subfields</div>
                      <FieldTree fields={field.subfields} level={level + 1} clusterName={clusterName} dbName={dbName} tableName={tableName} parentPath={path} idToPathMap={effectiveIdToPathMap} />
                    </>
                  )}
                  {/* Equivalence section */}
                  {(equivalentsMap[path] && equivalentsMap[path].length > 0 && !loadingEq[path]) && (
                    <div style={{ marginTop: 10, fontSize: 14, color: '#2563eb', fontWeight: 600 }}>
                      <span
                        style={{ cursor: 'pointer', userSelect: 'none', display: 'inline-block', fontSize: 11 }}
                        onClick={() => toggleEquivalence(path)}
                        onMouseOver={e => e.currentTarget.style.color = '#1d4ed8'}
                        onMouseOut={e => e.currentTarget.style.color = '#2563eb'}
                      >
                        {expandedEq[path] ? '▼' : '▶'} Equivalence
                      </span>
                      {expandedEq[path] && (
                        <ul style={{ margin: '6px 0 0 0', padding: 0, listStyle: 'none' }}>
                          {equivalentsMap[path].map(eqNode => (
                            <li key={eqNode.id} style={{ color: '#1e2a38', fontWeight: 400, fontSize: 14, marginLeft: 0, display: 'flex', alignItems: 'center' }}>
                              {eqNode.path}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                  {/* Possibly Equivalence section */}
                  <PossiblyEquivalenceTableSection path={path} />
                </>
              )}
            </div>
            {/* Divider line, except after the last field */}
            {idx !== fields.length - 1 && (
              <div style={{ borderBottom: '1px solid #e3e8ee', margin: '0 0 0 0', width: '100%' }} />
            )}
          </li>
        );
      })}
    </ul>
  );
}

// Add this component at the bottom of the file (or before export default App)
function AddEquivalenceForm({ currentPath, onAdded, addFn }: { currentPath: string, onAdded: () => void, addFn?: (fromPath: string, toPath: string) => Promise<void> }) {
  const [clusters, setClusters] = React.useState<Cluster[]>([]);
  const [selectedCluster, setSelectedCluster] = React.useState<Cluster | null>(null);
  const [databases, setDatabases] = React.useState<Database[]>([]);
  const [selectedDatabase, setSelectedDatabase] = React.useState<Database | null>(null);
  const [tables, setTables] = React.useState<Table[]>([]);
  const [selectedTable, setSelectedTable] = React.useState<Table | null>(null);
  const [fields, setFields] = React.useState<Field[]>([]);
  const [selectedFieldPath, setSelectedFieldPath] = React.useState<string[]>([]);
  const [adding, setAdding] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetchClusters().then(setClusters);
  }, []);

  React.useEffect(() => {
    if (selectedCluster) {
      fetchDatabases(selectedCluster.id).then(setDatabases);
      setSelectedDatabase(null);
      setTables([]);
      setSelectedTable(null);
      setFields([]);
      setSelectedFieldPath([]);
    }
  }, [selectedCluster]);

  React.useEffect(() => {
    if (selectedDatabase) {
      fetchTables(selectedDatabase.id).then(setTables);
      setSelectedTable(null);
      setFields([]);
      setSelectedFieldPath([]);
    }
  }, [selectedDatabase]);

  React.useEffect(() => {
    if (selectedTable) {
      fetchFields(selectedTable.id).then(setFields);
      setSelectedFieldPath([]);
    }
  }, [selectedTable]);

  // Recursive field selector for subfields
  function FieldSelector({ fields, level }: { fields: Field[], level: number }) {
    const currentValue = selectedFieldPath[level] || '';
    return (
      <>
        <select
          value={currentValue}
          onChange={e => {
            const value = e.target.value;
            // Update the path up to this level, set this value, and reset deeper levels
            const newPath = [...selectedFieldPath.slice(0, level), value];
            setSelectedFieldPath(newPath);
          }}
          style={{ marginRight: 8, marginBottom: 8 }}
        >
          <option value="">Select field...</option>
          {fields.map(f => (
            <option key={f.name} value={f.name}>{f.name}</option>
          ))}
        </select>
        {/* If a field is selected and has subfields, show next selector */}
        {(() => {
          const selected = fields.find(f => f.name === currentValue);
          if (selected && selected.subfields && selected.subfields.length > 0 && currentValue) {
            return <FieldSelector fields={selected.subfields} level={level + 1} />;
          }
          return null;
        })()}
      </>
    );
  }

  const selectedPath = selectedCluster && selectedDatabase && selectedTable && selectedFieldPath.length > 0 && selectedFieldPath[selectedFieldPath.length - 1] !== ''
    ? `${selectedCluster.name}/${selectedDatabase.name}/${selectedTable.name}/${selectedFieldPath.filter(Boolean).join('/')}`
    : '';

  const handleAdd = async () => {
    if (!selectedPath || selectedPath === currentPath) {
      setError('Please select a valid field (not the current one).');
      return;
    }
    setAdding(true);
    setError(null);
    try {
      if (addFn) {
        await addFn(currentPath, selectedPath);
      } else {
        await addEquivalence(currentPath, selectedPath);
      }
      setSelectedCluster(null);
      setDatabases([]);
      setSelectedDatabase(null);
      setTables([]);
      setSelectedTable(null);
      setFields([]);
      setSelectedFieldPath([]);
      onAdded();
    } catch (e: any) {
      setError('Failed to add equivalence');
    }
    setAdding(false);
  };

  const handleClear = () => {
    setSelectedCluster(null);
    setDatabases([]);
    setSelectedDatabase(null);
    setTables([]);
    setSelectedTable(null);
    setFields([]);
    setSelectedFieldPath([]);
    setError(null);
  };

  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>
        <select value={selectedCluster?.id || ''} onChange={e => {
          const c = clusters.find(cl => cl.id === Number(e.target.value));
          setSelectedCluster(c || null);
        }} style={{ minWidth: 120 }}>
          <option value="">Select cluster...</option>
          {clusters.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={selectedDatabase?.id || ''} onChange={e => {
          const d = databases.find(db => db.id === Number(e.target.value));
          setSelectedDatabase(d || null);
        }} style={{ minWidth: 120 }} disabled={!selectedCluster}>
          <option value="">Select database...</option>
          {databases.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <select value={selectedTable?.id || ''} onChange={e => {
          const t = tables.find(tbl => tbl.id === Number(e.target.value));
          setSelectedTable(t || null);
        }} style={{ minWidth: 120 }} disabled={!selectedDatabase}>
          <option value="">Select table...</option>
          {tables.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        {/* Field and subfield selectors */}
        {fields.length > 0 && selectedTable && (
          <FieldSelector fields={fields} level={0} />
        )}
      </div>
      {selectedPath && (
        <div style={{ color: '#2563eb', fontSize: 14, marginBottom: 8 }}>Selected path: <span style={{ fontWeight: 600 }}>{selectedPath}</span></div>
      )}
      <button onClick={handleAdd} disabled={adding || !selectedPath || selectedPath === currentPath} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 28px', fontWeight: 700, cursor: 'pointer', fontSize: 16, marginRight: 10, boxShadow: '0 1px 4px #2563eb22', transition: 'background 0.2s' }}>Add</button>
      <button onClick={handleClear} disabled={!(selectedCluster || selectedDatabase || selectedTable || selectedFieldPath.length > 0)} style={{ background: '#f3f4f6', color: '#222', border: '1px solid #e5e7eb', borderRadius: 8, padding: '10px 28px', fontWeight: 600, cursor: 'pointer', fontSize: 16 }}>Clear</button>
      {error && <div style={{ color: '#b91c1c', marginTop: 8 }}>{error}</div>}
    </div>
  );
}

// Update RemoveEquivalenceButton to be a minimal icon button with tooltip, only visible on hover
function RemoveEquivalenceButton({ currentPath, eqPath, onRemoved }: { currentPath: string, eqPath: string, onRemoved: () => void }) {
  const [removing, setRemoving] = React.useState(false);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', height: 24 }}>
      <button
        onClick={async () => {
          setRemoving(true);
          try {
            await removeEquivalence(currentPath, eqPath);
            onRemoved();
          } catch (e) {}
          setRemoving(false);
        }}
        disabled={removing}
        title="Remove equivalence"
        style={{
          background: 'none',
          border: 'none',
          color: '#b91c1c',
          cursor: 'pointer',
          fontSize: 18,
          padding: 0,
          marginLeft: 4,
          opacity: removing ? 0.5 : 0.7,
          transition: 'opacity 0.2s',
          visibility: 'hidden',
        }}
        className="remove-eq-btn"
      >
        🗑️
      </button>
      <style>{`
        li:hover .remove-eq-btn { visibility: visible !important; }
      `}</style>
    </span>
  );
}

function PossiblyEquivalenceSection({ currentPath, editMode }: { currentPath: string, editMode: boolean }) {
  const [equivalents, setEquivalents] = React.useState<any[]>([]);
  React.useEffect(() => {
    fetchPossiblyEquivalents(currentPath).then(setEquivalents).catch(() => setEquivalents([]));
  }, [currentPath]);

  return (
    <>
      {equivalents.length > 0 ? (
        <ul style={{ paddingLeft: 18, color: '#b45309', fontSize: 15 }}>
          {equivalents.map(eq => (
            <li key={eq.id} style={{ display: 'flex', alignItems: 'center', gap: 8, position: 'relative', padding: '2px 0' }}>
              <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{eq.path}</span>
              {editMode && (
                <RemovePossiblyEquivalenceButton currentPath={currentPath} eqPath={eq.path} onRemoved={() => fetchPossiblyEquivalents(currentPath).then(setEquivalents)} />
              )}
            </li>
          ))}
        </ul>
      ) : (
        <div style={{ color: '#b45309', opacity: 0.7 }}>No possibly equivalents.</div>
      )}
      {editMode && (
        <div style={{ marginTop: 24, background: '#fff7ed', border: '1px solid #fde68a', borderRadius: 12, boxShadow: '0 2px 8px rgba(191, 132, 6, 0.04)', padding: '24px 32px', maxWidth: 520, marginLeft: 'auto', marginRight: 'auto' }}>
          <div style={{ fontWeight: 700, color: '#b45309', fontSize: 18, marginBottom: 12, letterSpacing: 0.5 }}>Add Possibly Equivalence</div>
          <AddEquivalenceForm currentPath={currentPath} onAdded={() => fetchPossiblyEquivalents(currentPath).then(setEquivalents)} addFn={addPossiblyEquivalence} />
        </div>
      )}
    </>
  );
}

function RemovePossiblyEquivalenceButton({ currentPath, eqPath, onRemoved }: { currentPath: string, eqPath: string, onRemoved: () => void }) {
  const [removing, setRemoving] = React.useState(false);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', height: 24 }}>
      <button
        onClick={async () => {
          setRemoving(true);
          try {
            await removePossiblyEquivalence(currentPath, eqPath);
            onRemoved();
          } catch (e) {}
          setRemoving(false);
        }}
        disabled={removing}
        title="Remove possibly equivalence"
        style={{
          background: 'none',
          border: 'none',
          color: '#b45309',
          cursor: 'pointer',
          fontSize: 18,
          padding: 0,
          marginLeft: 4,
          opacity: removing ? 0.5 : 0.7,
          transition: 'opacity 0.2s',
          visibility: 'hidden',
        }}
        className="remove-eq-btn"
      >
        🗑️
      </button>
      <style>{`
        li:hover .remove-eq-btn { visibility: visible !important; }
      `}</style>
    </span>
  );
}

function PossiblyEquivalenceTableSection({ path }: { path: string }) {
  const [equivs, setEquivs] = React.useState<EquivalentNode[] | null>(null);
  const [expanded, setExpanded] = React.useState(false);
  React.useEffect(() => {
    if (equivs === null) {
      fetchPossiblyEquivalents(path).then(setEquivs).catch(() => setEquivs([]));
    }
  }, [path]);
  if (!equivs || equivs.length === 0) return null;
  return (
    <div style={{ marginTop: 8, fontSize: 14, color: '#b45309', fontWeight: 600 }}>
      <span
        style={{ cursor: 'pointer', userSelect: 'none', display: 'inline-block', fontSize: 11 }}
        onClick={() => setExpanded(e => !e)}
        onMouseOver={e => e.currentTarget.style.color = '#d97706'}
        onMouseOut={e => e.currentTarget.style.color = '#b45309'}
      >
        {expanded ? '▼' : '▶'} Possibly Equivalence
      </span>
      {expanded && (
        <ul style={{ margin: '6px 0 0 0', padding: 0, listStyle: 'none' }}>
          {equivs.map(eqNode => (
            <li key={eqNode.id} style={{ color: '#b45309', fontWeight: 400, fontSize: 14, marginLeft: 0, display: 'flex', alignItems: 'center' }}>
              {eqNode.path}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
