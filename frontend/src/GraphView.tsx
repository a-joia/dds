import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { TableGraphData, GraphNode, GraphEdge, ExternalConnection, fetchFields } from './api';

interface GraphViewProps {
  graphData: TableGraphData;
  onClose: () => void;
  onRemoveField?: (fieldId: number) => void;
  onAddTable?: (tableId: number) => void;
  includedTables?: Set<number>;
  setGraphData: (data: TableGraphData) => void;
  setIncludedTables: (tables: Set<number>) => void;
  layoutMode: 'force' | 'hierarchy';
  setLayoutMode: React.Dispatch<React.SetStateAction<'force' | 'hierarchy'>>;
  // Hierarchy params
  hierarchyYScale: number;
  setHierarchyYScale: (v: number) => void;
  hierarchyXScale: number;
  setHierarchyXScale: (v: number) => void;
  hierarchyLabelRotation: number;
  setHierarchyLabelRotation: (v: number) => void;
  // Force params
  forceLinkDistance: number;
  setForceLinkDistance: (v: number) => void;
  forceChargeStrength: number;
  setForceChargeStrength: (v: number) => void;
  forceCollisionRadius: number;
  setForceCollisionRadius: (v: number) => void;
  forceCenterStrength: number;
  setForceCenterStrength: (v: number) => void;
}

interface D3Node extends GraphNode {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface D3Link extends GraphEdge {
  source: D3Node;
  target: D3Node;
}

// Move dfs above removeTableFromGraph so it is in scope
function dfs(tid: number, tableAdj: Map<number, Set<number>>, reachable: Set<number>) {
  if (reachable.has(tid)) return;
  reachable.add(tid);
  if (tableAdj.has(tid)) {
    Array.from(tableAdj.get(tid) || []).forEach(neighbor => {
      dfs(neighbor, tableAdj, reachable);
    });
  }
}

export function GraphView({ graphData, onClose, onRemoveField, onAddTable, includedTables, setGraphData, setIncludedTables, layoutMode, setLayoutMode, hierarchyYScale, setHierarchyYScale, hierarchyXScale, setHierarchyXScale, hierarchyLabelRotation, setHierarchyLabelRotation, forceLinkDistance, setForceLinkDistance, forceChargeStrength, setForceChargeStrength, forceCollisionRadius, setForceCollisionRadius, forceCenterStrength, setForceCenterStrength }: GraphViewProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<D3Node | null>(null);
  const [simulation, setSimulation] = useState<d3.Simulation<D3Node, D3Link> | null>(null);
  const [nodeDetailsCollapsed, setNodeDetailsCollapsed] = useState(false);
  const [externalConnectionsCollapsed, setExternalConnectionsCollapsed] = useState(false);
  const [controlsCollapsed, setControlsCollapsed] = useState(true);
  // Local state for layout params
  const [localHierarchyYScale, setLocalHierarchyYScale] = useState(hierarchyYScale);
  const [localHierarchyXScale, setLocalHierarchyXScale] = useState(hierarchyXScale);
  const [localHierarchyLabelRotation, setLocalHierarchyLabelRotation] = useState(hierarchyLabelRotation);
  // Default values for layout params
  const DEFAULT_HIERARCHY_Y_SCALE = 1;
  const DEFAULT_HIERARCHY_X_SCALE = 1;
  const DEFAULT_HIERARCHY_ROT = 0;

  // Sync local state with props when layoutMode changes
  useEffect(() => {
    setLocalHierarchyYScale(hierarchyYScale);
    setLocalHierarchyXScale(hierarchyXScale);
    setLocalHierarchyLabelRotation(hierarchyLabelRotation);
  }, [layoutMode, hierarchyYScale, hierarchyXScale, hierarchyLabelRotation]);

  // Handler to reset local controls to fixed default values
  function handleReset() {
    setLocalHierarchyYScale(DEFAULT_HIERARCHY_Y_SCALE);
    setLocalHierarchyXScale(DEFAULT_HIERARCHY_X_SCALE);
    setLocalHierarchyLabelRotation(DEFAULT_HIERARCHY_ROT);
  }

  // Helper to switch to force and then back to hierarchy
  function forceHierarchyRerender() {
    setLayoutMode('force');
    setTimeout(() => setLayoutMode('hierarchy'), 0);
  }

  // Handler to apply changes (force re-layout for hierarchy)
  function handleApply() {
    if (layoutMode === 'hierarchy') {
      setHierarchyYScale(localHierarchyYScale);
      setHierarchyXScale(localHierarchyXScale);
      setHierarchyLabelRotation(localHierarchyLabelRotation);
      forceHierarchyRerender();
    }
  }

  // Dummy state to force re-render for hierarchy apply
  const [hierarchyApplyKey, setHierarchyApplyKey] = useState(0);

  // Helper to trigger hierarchical layout
  const applyHierarchicalLayout = () => {
    if (!svgRef.current || !graphData) return;
    const svg = d3.select(svgRef.current);
    const graphContainer = svg.select('.graph-container');
    if (!graphContainer.empty()) {
      // Get nodes by level
      const nodes: D3Node[] = graphData.nodes.map(node => ({ ...node }));
      // Compute depth for each node
      const nodeMap: Record<number, D3Node> = {};
      nodes.forEach(node => { nodeMap[node.id] = node; });
      const getDepth = (node: D3Node): number => {
        let depth = 0;
        let current = node;
        while (current.parent_id !== null && current.parent_id !== undefined) {
          const parent = nodeMap[current.parent_id];
          if (!parent) break;
          depth += 1;
          current = parent;
        }
        return depth;
      };
      const levels: Record<number, number> = {};
      nodes.forEach(node => {
        levels[node.id] = getDepth(node);
      });
      // Group nodes by level
      const maxLevel = Math.max(...Object.values(levels));
      const nodesByLevel: D3Node[][] = Array.from({ length: maxLevel + 1 }, () => []);
      nodes.forEach(node => {
        const lvl = levels[node.id] ?? 0;
        nodesByLevel[lvl].push(node);
      });
      // Layout
      const width = 1200;
      const height = 800;
      const baseY = height / (maxLevel + 2);
      nodesByLevel.forEach((levelNodes, i) => {
        const xStep = (width / (levelNodes.length + 1)) * hierarchyXScale;
        const yStep = baseY * hierarchyYScale;
        levelNodes.forEach((node, j) => {
          node.fx = (j + 1) * xStep;
          node.fy = (i + 1) * yStep;
        });
      });
      // Animate transition for nodes
      graphContainer.selectAll('g').transition().duration(800)
        .attr('transform', (d: any) => {
          if (!d) return '';
          const node = nodes.find(n => n.id === d.id);
          return node ? `translate(${node.fx},${node.fy})` : '';
        });
      // Animate transition for edges
      graphContainer.selectAll('line').transition().duration(800)
        .attr('x1', (d: any) => {
          if (!d || !d.source) return 0;
          const node = nodes.find(n => n.id === d.source.id);
          return node ? node.fx : d.x1;
        })
        .attr('y1', (d: any) => {
          if (!d || !d.source) return 0;
          const node = nodes.find(n => n.id === d.source.id);
          return node ? node.fy : d.y1;
        })
        .attr('x2', (d: any) => {
          if (!d || !d.target) return 0;
          const node = nodes.find(n => n.id === d.target.id);
          return node ? node.fx : d.x2;
        })
        .attr('y2', (d: any) => {
          if (!d || !d.target) return 0;
          const node = nodes.find(n => n.id === d.target.id);
          return node ? node.fy : d.y2;
        });
      // Stop simulation
      if (simulation) simulation.stop();
      // Apply label rotation in hierarchy mode
      graphContainer.selectAll('text')
        .transition().duration(800)
        .attr('transform', `rotate(${hierarchyLabelRotation})`);
    }
  };

  // Restore force layout
  const restoreForceLayout = () => {
    if (simulation) simulation.alpha(1).restart();
    // Unfix nodes
    if (!svgRef.current || !graphData) return;
    const svg = d3.select(svgRef.current);
    const graphContainer = svg.select('.graph-container');
    if (!graphContainer.empty()) {
      graphContainer.selectAll('g').each(function (d: any) {
        if (d) {
          d.fx = null;
          d.fy = null;
        }
      });
    }
  };

  // D3 graph initialization: only when graphData changes
  useEffect(() => {
    if (!svgRef.current || !graphData) return;
    
    console.log('Graph data received:', graphData);
    console.log('Nodes:', graphData.nodes);
    console.log('Edges:', graphData.edges);
    console.log('Node IDs:', graphData.nodes.map(n => n.id));

    // Validate data
    if (!graphData.nodes || graphData.nodes.length === 0) {
      console.warn('No nodes to display');
      return;
    }

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();

    const width = 1200;
    const height = 800;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        const { transform } = event;
        
        // Apply transform to the main group
        svg.select('.graph-container').attr('transform', transform);
      });

    // Apply zoom to SVG
    svg.call(zoom);

    // Create main container for the graph
    const graphContainer = svg.append('g')
      .attr('class', 'graph-container');

    // Create nodes and links
    const nodes: D3Node[] = graphData.nodes.map(node => ({ ...node }));
    console.log('Rendering nodes:', nodes);
    
    // Create a map of node IDs for quick lookup
    const nodeIds = new Set(nodes.map(n => n.id));
    
    // Filter edges to only include those where both source and target nodes exist
    const validEdges = graphData.edges.filter(edge => {
      const hasFrom = nodeIds.has(edge.from);
      const hasTo = nodeIds.has(edge.to);
      if (!hasFrom || !hasTo) {
        console.warn(`Filtering out edge ${edge.id}: from=${edge.from} (exists: ${hasFrom}), to=${edge.to} (exists: ${hasTo})`);
      }
      return hasFrom && hasTo;
    });
    console.log('Rendering edges:', validEdges);
    
    const links: D3Link[] = validEdges.map(edge => {
      const source = nodes.find(n => n.id === edge.from);
      const target = nodes.find(n => n.id === edge.to);
      if (!source || !target) {
        console.error(`Invalid edge: source=${edge.from}, target=${edge.to}`);
        return null;
      }
      return {
        ...edge,
        source,
        target
      };
    }).filter((link): link is D3Link => link !== null);
    
    console.log('Final links:', links);

    // Create force simulation with error handling
    let sim: d3.Simulation<D3Node, D3Link> | null = null;
    try {
      sim = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2).strength(1))
        .force('collision', d3.forceCollide().radius(30));
    } catch (error) {
      console.error('Error creating D3 simulation:', error);
      return;
    }

    if (!sim) {
      console.error('Failed to create D3 simulation');
      return;
    }

    // Create arrow markers (in defs, outside the graph container)
    svg.append('defs').selectAll('marker')
      .data(['equivalence', 'possibly_equivalence', 'contains'])
      .enter().append('marker')
      .attr('id', d => d)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 5)
      .attr('markerHeight', 5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', d => {
        if (d === 'equivalence' || d === 'possibly_equivalence') return 'M2,-5L8,0L2,5 M8,-5L2,0L8,5'; // double-headed arrow
        return 'M0,-5L10,0L0,5'; // single arrow
      })
      .attr('fill', d => {
        if (d === 'equivalence') return 'rgba(37,99,235,0.5)';
        if (d === 'possibly_equivalence') return 'rgba(180,83,9,0.5)';
        return 'rgba(107,114,128,0.5)'; // Gray for contains
      });

    // Create bidirectional arrow markers for possibly equivalence edges (double tip)
    svg.append('defs').selectAll('marker')
      .data(['possibly_equivalence_bidirectional'])
      .enter().append('marker')
      .attr('id', d => d)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 5)
      .attr('markerHeight', 5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M2,-5L8,0L2,5 M8,-5L2,0L8,5') // double-headed arrow
      .attr('fill', 'rgba(180,83,9,0.5)');

    // Create links
    const link = graphContainer.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', d => {
        if (d.type === 'equivalence') return 'rgba(37,99,235,0.5)';
        if (d.type === 'possibly_equivalence') return 'rgba(180,83,9,0.5)';
        return 'rgba(107,114,128,0.5)'; // Gray for contains
      })
      .attr('stroke-width', 2)
      .attr('marker-end', d => {
        if (d.type === 'equivalence') return 'url(#equivalence)';
        if (d.type === 'possibly_equivalence') return 'url(#possibly_equivalence_bidirectional)';
        return `url(#${d.type})`;
      });

    // Create nodes
    const nodeGroups = graphContainer.append('g')
      .selectAll('g')
      .data(nodes)
      .enter().append('g');

    // Add circles to nodes
    nodeGroups.append('circle')
      .attr('r', d => d.id < 0 ? 10 : 8) // Smaller radius for table node
      .attr('fill', d => {
        if (d.id < 0) {
          // Different colors for different table nodes
          if (d.id === -1) return '#dc2626'; // Red for primary table
          if (d.id === -2) return '#ea580c'; // Orange for second table
          if (d.id === -3) return '#d97706'; // Amber for third table
          if (d.id === -4) return '#ca8a04'; // Yellow for fourth table
          return '#dc2626'; // Default red for other table nodes
        }
        return d.parent_id === null || d.parent_id < 0 ? '#2563eb' : '#10b981'; // Blue for root fields, green for subfields
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('click', (event, d) => setSelectedNode(d))
      .on('mouseover', function(event, d) {
        const radius = d.id < 0 ? 12 : 12;
        d3.select(this).attr('r', radius);
        showTooltip(event, d);
      })
      .on('mouseout', function(event, d) {
        const radius = d.id < 0 ? 10 : 8;
        d3.select(this).attr('r', radius);
        hideTooltip();
      });

    // Add labels to nodes
    nodeGroups.append('text')
      .text(d => d.name)
      .attr('x', 12)
      .attr('y', 4)
      .attr('font-size', '12px')
      .attr('fill', '#374151');

    // Create tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    function showTooltip(event: MouseEvent, d: D3Node) {
      tooltip.transition()
        .duration(200)
        .style('opacity', 0.9);
      tooltip.html(`
        <strong>${d.name}</strong><br/>
        Path: ${d.path}<br/>
        Type: ${d.meta.type || 'N/A'}<br/>
        Description: ${d.meta.description || 'No description available'}
      `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    }

    function hideTooltip() {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
    }

    function dragstarted(event: d3.D3DragEvent<SVGGElement, D3Node, D3Node>, d: D3Node) {
      if (sim && !event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: d3.D3DragEvent<SVGGElement, D3Node, D3Node>, d: D3Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: d3.D3DragEvent<SVGGElement, D3Node, D3Node>, d: D3Node) {
      if (sim && !event.active) sim.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Only apply drag and simulation if in force layout
    if (layoutMode === 'force') {
      nodeGroups.call(
        d3.drag<SVGGElement, D3Node>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      );
      try {
        sim = d3.forceSimulation(nodes)
          .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
          .force('charge', d3.forceManyBody().strength(-300))
          .force('center', d3.forceCenter(width / 2, height / 2).strength(1))
          .force('collision', d3.forceCollide().radius(30));
      } catch (error) {
        console.error('Error creating D3 simulation:', error);
        return;
      }
      if (!sim) {
        console.error('Failed to create D3 simulation');
        return;
      }
      sim.on('tick', () => {
        link
          .attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y);
        nodeGroups
          .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
      });
    } else {
      // In hierarchy mode, set node positions directly
      nodeGroups.attr('transform', (d: any) => `translate(${d.fx},${d.fy})`);
      link
        .attr('x1', (d: any) => d.source.fx)
        .attr('y1', (d: any) => d.source.fy)
        .attr('x2', (d: any) => d.target.fx)
        .attr('y2', (d: any) => d.target.fy);
    }
    setSimulation(sim);

    // Cleanup
    return () => {
      if (sim) sim.stop();
      tooltip.remove();
    };
  }, [graphData, layoutMode, hierarchyYScale, hierarchyXScale, hierarchyLabelRotation, forceLinkDistance, forceChargeStrength, forceCollisionRadius, forceCenterStrength]);

  // Layout effect: apply layout when layoutMode changes
  useEffect(() => {
    if (layoutMode === 'hierarchy') {
      if (simulation) simulation.stop(); // Explicitly stop simulation
      applyHierarchicalLayout();
    } else if (layoutMode === 'force') {
      if (simulation) simulation.alpha(1).restart(); // Only restart in force mode
      restoreForceLayout();
    }
    // eslint-disable-next-line
  }, [layoutMode]);

  // When a new table is added, reset to force layout
  useEffect(() => {
    if (!onAddTable) return;
    const orig = onAddTable;
    const wrapped = async (tableId: number) => {
      setLayoutMode('force');
      await orig(tableId);
    };
    // Replace onAddTable with wrapped version
    // (This requires App to pass the prop as a variable, not inline)
  }, [onAddTable, setLayoutMode]);

  const handleRemoveField = (fieldId: number) => {
    if (onRemoveField) {
      onRemoveField(fieldId);
    }
  };

  // When a new table is added, or when clicking external connections, reset to force layout
  function handleAddTableWithForceLayout(tableId: number) {
    setLayoutMode('force');
    if (onAddTable) onAddTable(tableId);
  }

  // External Connections: toggle add/remove table
  function handleToggleTable(tableId: number) {
    if (includedTables && includedTables.has(tableId)) {
      if (onRemoveField) onRemoveField(tableId);
    } else {
      handleAddTableWithForceLayout(tableId);
    }
  }

  // Add this function inside the GraphView component
  function removeTableFromGraph(tableId: number) {
    if (!includedTables || !graphData || !includedTables.has(tableId)) return;

    console.log('Before removal: nodes', graphData.nodes);
    console.log('Before removal: edges', graphData.edges);

    // Find the table path from external_connections
    let tablePath = '';
    const extConn = graphData.external_connections.find(conn => conn.from_table.id === tableId || conn.to_table.id === tableId);
    if (extConn) {
      tablePath = extConn.from_table.id === tableId ? extConn.from_table.path : extConn.to_table.path;
    } else {
      const tableNode = graphData.nodes.find(n => n.meta && n.meta.type === 'table' && n.id < 0 && (n.path || '').length > 0 && (n.path.split('/')[2] === String(tableId) || n.name.endsWith(String(tableId))));
      if (tableNode) {
        tablePath = tableNode.path;
      }
    }
    console.log('Table path for removal:', tablePath);

    // Remove all nodes whose path starts with tablePath
    const nodesToRemoveArr = graphData.nodes.filter(node => node.path && tablePath && node.path.startsWith(tablePath));
    const nodesToRemove = new Set(nodesToRemoveArr.map(node => node.id));
    console.log('Removing nodes for table', tableId, Array.from(nodesToRemove));

    // Remove all edges connected to those nodes
    let newEdges = graphData.edges.filter(edge =>
      !nodesToRemove.has(edge.from) && !nodesToRemove.has(edge.to)
    );

    // Remove nodes
    let newNodes = graphData.nodes.filter(node => !nodesToRemove.has(node.id));

    // Remove external_connections related to this table
    let newExternalConnections = graphData.external_connections.filter(conn =>
      conn.from_table.id !== tableId && conn.to_table.id !== tableId
    );

    // Remove table from includedTables
    let newIncludedTables = new Set(includedTables);
    newIncludedTables.delete(tableId);

    // --- Robust: Only keep the connected component containing the primary table node ---
    // 1. Find the node ID of the primary table node
    const primaryTableId = Array.from(includedTables)[0];
    let primaryTableNodeId: number | null = null;
    for (const node of newNodes) {
      if (node.meta && node.meta.type === 'table') {
        // Try to match by path to external_connections
        for (const conn of newExternalConnections) {
          if ((conn.from_table.id === primaryTableId && conn.from_table.path === node.path) ||
              (conn.to_table.id === primaryTableId && conn.to_table.path === node.path)) {
            primaryTableNodeId = node.id;
          }
        }
        // Fallback: match by name
        if (primaryTableNodeId === null && node.name && graphData.table.name && node.name === graphData.table.name) {
          primaryTableNodeId = node.id;
        }
      }
    }
    if (primaryTableNodeId === null) {
      // Fallback: use -1 if present
      const fallbackNode = newNodes.find(n => n.id === -1);
      if (fallbackNode) primaryTableNodeId = -1;
    }
    console.log('Primary table node id:', primaryTableNodeId);

    // 2. Traverse the graph from the primary table node
    const reachableNodeIds = new Set<number>();
    if (primaryTableNodeId !== null) {
      const stack = [primaryTableNodeId];
      while (stack.length > 0) {
        const curr = stack.pop();
        if (curr === undefined || reachableNodeIds.has(curr)) continue;
        reachableNodeIds.add(curr);
        // Find all neighbors
        for (const edge of newEdges) {
          if (edge.from === curr && !reachableNodeIds.has(edge.to)) stack.push(edge.to);
          if (edge.to === curr && !reachableNodeIds.has(edge.from)) stack.push(edge.from);
        }
      }
    }
    // 3. Only keep nodes/edges in the reachable set
    const finalNodes = newNodes.filter(node => reachableNodeIds.has(node.id));
    const finalEdges = newEdges.filter(edge => reachableNodeIds.has(edge.from) && reachableNodeIds.has(edge.to));
    console.log('After connectivity filter: keeping nodes', finalNodes.map(n => n.id));
    console.log('After connectivity filter: keeping edges', finalEdges.map(e => e.id));

    // 4. Update includedTables to only include tables with at least one node in the finalNodes
    const finalTableIds = new Set<number>();
    for (const node of finalNodes) {
      if (node.meta && node.meta.type === 'table') {
        for (const conn of newExternalConnections) {
          if (conn.from_table.path === node.path) finalTableIds.add(conn.from_table.id);
          if (conn.to_table.path === node.path) finalTableIds.add(conn.to_table.id);
        }
      }
    }
    // Always include the primary table id
    finalTableIds.add(primaryTableId);
    const finalIncludedTables = new Set(Array.from(newIncludedTables).filter(tid => finalTableIds.has(tid)));

    // 5. Remove external_connections for tables not in finalIncludedTables
    // Do not filter external_connections; always keep the full set
    const finalExternalConnections = graphData.external_connections;

    // Update graph
    setGraphData({
      ...graphData,
      nodes: finalNodes,
      edges: finalEdges,
      external_connections: finalExternalConnections,
    });
    setIncludedTables(finalIncludedTables);
  }

  // Build a map from field ID to field name for quick lookup, and a cache for missing names
  const fieldIdToName = new Map<number, string>();
  for (const node of graphData.nodes) {
    fieldIdToName.set(node.id, node.name);
  }
  const [fieldNameCache, setFieldNameCache] = useState<{ [key: number]: string | undefined }>({});
  const [fieldNameLoading, setFieldNameLoading] = useState<{ [key: number]: boolean }>({});

  // Recursive search for fieldId in fields and subfields
  function findFieldById(fieldsArr: any[], fieldId: number): any | undefined {
    for (const f of fieldsArr) {
      if (f.id === fieldId) return f;
      if (f.subfields && Array.isArray(f.subfields)) {
        const found = findFieldById(f.subfields, fieldId);
        if (found) return found;
      }
    }
    return undefined;
  }

  async function ensureFieldName(tableId: number, fieldId: number) {
    if (fieldIdToName.has(fieldId) || fieldNameCache[fieldId]) return;
    setFieldNameLoading(prev => ({ ...prev, [fieldId]: true }));
    try {
      const fields = await fetchFields(tableId);
      const found = findFieldById(fields, fieldId);
      if (found) {
        setFieldNameCache(prev => ({ ...prev, [fieldId]: found.name }));
      } else {
        setFieldNameCache(prev => ({ ...prev, [fieldId]: '(unknown)' }));
      }
    } catch {
      setFieldNameCache(prev => ({ ...prev, [fieldId]: '(unknown)' }));
    } finally {
      setFieldNameLoading(prev => ({ ...prev, [fieldId]: false }));
    }
  }

  // Build a map from table name to real (positive) table ID using external_connections
  const tableNameToId = new Map<string, number>();
  for (const conn of graphData.external_connections) {
    tableNameToId.set(conn.from_table.name, conn.from_table.id);
    tableNameToId.set(conn.to_table.name, conn.to_table.id);
  }

  // Add state for collapsing the Active Tables panel
  const [activeTablesCollapsed, setActiveTablesCollapsed] = useState(false);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '20px',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <div>
            <h2 style={{ margin: 0, color: '#2563eb' }}>
              Graph View: {graphData.table.name}
            </h2>
            <p style={{ margin: '5px 0 0 0', color: '#666' }}>
              {graphData.nodes.length} fields, {graphData.edges.length} connections
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Close
          </button>
        </div>

        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <button
            onClick={() => setLayoutMode('hierarchy')}
            style={{
              background: layoutMode === 'hierarchy' ? '#2563eb' : '#f3f4f6',
              color: layoutMode === 'hierarchy' ? 'white' : '#2563eb',
              border: '1px solid #2563eb',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Hierarchical Layout
          </button>
          <button
            onClick={() => setLayoutMode('force')}
            style={{
              background: layoutMode === 'force' ? '#2563eb' : '#f3f4f6',
              color: layoutMode === 'force' ? 'white' : '#2563eb',
              border: '1px solid #2563eb',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Force Layout
          </button>
        </div>

        <div style={{ flex: 1, overflow: 'hidden', border: '1px solid #e5e7eb', borderRadius: '4px', position: 'relative' }}>
          <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
          
          {/* Zoom Instructions */}
          <div style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            borderRadius: '4px',
            padding: '8px 12px',
            fontSize: '12px',
            maxWidth: '200px'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Navigation:</div>
            <div>• Mouse wheel: Zoom in/out</div>
            <div>• Drag background: Pan around</div>
            <div>• Drag nodes: Move nodes</div>
          </div>
        </div>

        {/* Node details and external connections side by side */}
        <div style={{ display: 'flex', flexDirection: 'row', gap: 16, marginTop: 12, justifyContent: 'flex-start', alignItems: 'flex-start' }}>
          {/* Collapsible Layout Controls */}
          <div style={{ minWidth: 340, maxWidth: 400, fontSize: 13 }}>
            <div
              style={{
                background: '#f5f7fa',
                borderRadius: '4px',
                border: '1px solid #e5e7eb',
                marginBottom: 8,
                boxShadow: '0 1px 4px rgba(0,0,0,0.03)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: 15,
                color: '#2563eb',
                padding: '10px 14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                userSelect: 'none',
              }}
              onClick={() => setControlsCollapsed(c => !c)}
            >
              <span>Layout Parameters</span>
              <span style={{ fontSize: 13 }}>{controlsCollapsed ? '▶' : '▼'}</span>
            </div>
            {!controlsCollapsed && (
              <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 4, padding: '16px 18px', marginBottom: 8, display: 'flex', flexDirection: 'column', gap: 12, fontSize: 12 }}>
                {layoutMode === 'hierarchy' && (
                  <>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Y Scale
                      <input type="range" min={0.5} max={3} step={0.01} value={localHierarchyYScale} onChange={e => setLocalHierarchyYScale(Number(e.target.value))} />
                      <input type="number" min={0.5} max={3} step={0.01} value={localHierarchyYScale} onChange={e => setLocalHierarchyYScale(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      X Scale
                      <input type="range" min={0.5} max={3} step={0.01} value={localHierarchyXScale} onChange={e => setLocalHierarchyXScale(Number(e.target.value))} />
                      <input type="number" min={0.5} max={3} step={0.01} value={localHierarchyXScale} onChange={e => setLocalHierarchyXScale(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Label Rotation
                      <input type="range" min={-90} max={90} value={localHierarchyLabelRotation} onChange={e => setLocalHierarchyLabelRotation(Number(e.target.value))} />
                      <input type="number" min={-90} max={90} value={localHierarchyLabelRotation} onChange={e => setLocalHierarchyLabelRotation(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                  </>
                )}
                {layoutMode === 'force' && (
                  <>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Link Distance
                      <input type="range" min={20} max={300} value={forceLinkDistance} onChange={e => setForceLinkDistance(Number(e.target.value))} />
                      <input type="number" min={20} max={300} value={forceLinkDistance} onChange={e => setForceLinkDistance(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Charge Strength
                      <input type="range" min={-1000} max={1000} value={forceChargeStrength} onChange={e => setForceChargeStrength(Number(e.target.value))} />
                      <input type="number" min={-1000} max={1000} value={forceChargeStrength} onChange={e => setForceChargeStrength(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Collision Radius
                      <input type="range" min={5} max={100} value={forceCollisionRadius} onChange={e => setForceCollisionRadius(Number(e.target.value))} />
                      <input type="number" min={5} max={100} value={forceCollisionRadius} onChange={e => setForceCollisionRadius(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      Center Strength
                      <input type="range" min={0} max={5} step={0.01} value={forceCenterStrength} onChange={e => setForceCenterStrength(Number(e.target.value))} />
                      <input type="number" min={0} max={5} step={0.01} value={forceCenterStrength} onChange={e => setForceCenterStrength(Number(e.target.value))} style={{ width: 60 }} />
                    </label>
                  </>
                )}
                <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 10 }}>
                  <button
                    onClick={handleReset}
                    style={{
                      background: '#f3f4f6',
                      color: '#2563eb',
                      border: '1px solid #2563eb',
                      borderRadius: 4,
                      padding: '8px 18px',
                      fontWeight: 600,
                      fontSize: 15,
                      cursor: 'pointer',
                    }}
                  >Reset</button>
                  <button
                    onClick={handleApply}
                    style={{
                      background: '#2563eb',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      padding: '8px 18px',
                      fontWeight: 600,
                      fontSize: 15,
                      cursor: 'pointer',
                    }}
                  >Apply</button>
                </div>
              </div>
            )}
          </div>
          {selectedNode && (
            <div style={{
              background: '#f5f7fa',
              borderRadius: '4px',
              border: '1px solid #e5e7eb',
              overflow: 'hidden',
              fontSize: '13px',
              maxWidth: 340,
              boxShadow: '0 1px 4px rgba(0,0,0,0.03)'
            }}>
              <div 
                style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '10px',
                  cursor: 'pointer',
                  background: nodeDetailsCollapsed ? '#f3f4f6' : '#f5f7fa',
                  borderBottom: nodeDetailsCollapsed ? 'none' : '1px solid #e5e7eb',
                  fontSize: '14px'
                }}
                onClick={() => setNodeDetailsCollapsed(!nodeDetailsCollapsed)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    fontSize: '12px', 
                    transition: 'transform 0.2s',
                    transform: nodeDetailsCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)'
                  }}>
                    ▼
                  </span>
                  <h3 style={{ margin: 0, color: '#374151', fontSize: '15px', fontWeight: 700 }}>
                    {selectedNode.name}
                  </h3>
                </div>
              </div>
              {!nodeDetailsCollapsed && (
                <div style={{ padding: '10px' }}>
                  <p style={{ margin: '4px 0', color: '#666', fontSize: '13px' }}>
                    <strong>Path:</strong> {selectedNode.path}
                  </p>
                  <p style={{ margin: '4px 0', color: '#666', fontSize: '13px' }}>
                    <strong>Type:</strong> {selectedNode.meta.type || 'N/A'}
                  </p>
                  <p style={{ margin: '4px 0', color: '#666', fontSize: '13px' }}>
                    <strong>Description:</strong> {selectedNode.meta.description || 'No description available'}
                  </p>
                </div>
              )}
            </div>
          )}
          {/* External Connections and Active Tables side by side */}
          <div style={{ display: 'flex', flexDirection: 'row', gap: 12, alignItems: 'flex-start', flex: 1, minWidth: 0 }}>
            {/* External Connections Panel */}
            {graphData.external_connections && graphData.external_connections.length > 0 && (
              <div style={{
                background: '#e0e7ef',
                borderRadius: '4px',
                border: '1px solid #b6c2d1',
                padding: '10px',
                minWidth: 320,
                maxWidth: 520,
                fontSize: 12,
                boxShadow: '0 1px 4px rgba(0,0,0,0.03)',
                marginLeft: 0,
                overflowX: 'auto',
                overflowY: 'auto',
                whiteSpace: 'normal',
                maxHeight: 220,
              }}>
                <div style={{ fontWeight: 700, color: '#2563eb', marginBottom: 6, cursor: 'pointer' }}
                  onClick={() => setExternalConnectionsCollapsed(c => !c)}>
                  External Connections {externalConnectionsCollapsed ? '▶' : '▼'}
                </div>
                {!externalConnectionsCollapsed && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 220, overflowY: 'auto', overflowX: 'auto' }}>
                    {/* Build external table list from external_connections, only for tables truly connected to the main graph */}
                    {(() => {
                      if (!includedTables) return null;
                      // 1. Compute reachable node IDs from the primary table node
                      const primaryTableId = Array.from(includedTables)[0];
                      let primaryTableNodeId: number | null = null;
                      for (const node of graphData.nodes) {
                        if (node.meta && node.meta.type === 'table') {
                          if (node.id === -1 && graphData.table.id === primaryTableId) primaryTableNodeId = node.id;
                          // Try to match by name
                          if (primaryTableNodeId === null && node.name && graphData.table.name && node.name === graphData.table.name) {
                            primaryTableNodeId = node.id;
                          }
                        }
                      }
                      if (primaryTableNodeId === null) {
                        const fallbackNode = graphData.nodes.find(n => n.id === -1);
                        if (fallbackNode) primaryTableNodeId = -1;
                      }
                      // Traverse the graph from the primary table node
                      const reachableNodeIds = new Set<number>();
                      if (primaryTableNodeId !== null) {
                        const stack = [primaryTableNodeId];
                        while (stack.length > 0) {
                          const curr = stack.pop();
                          if (curr === undefined || reachableNodeIds.has(curr)) continue;
                          reachableNodeIds.add(curr);
                          for (const edge of graphData.edges) {
                            if (edge.from === curr && !reachableNodeIds.has(edge.to)) stack.push(edge.to);
                            if (edge.to === curr && !reachableNodeIds.has(edge.from)) stack.push(edge.from);
                          }
                        }
                      }
                      // 2. Build external table map, only for tables with at least one edge to a reachable node
                      const extTableMap = new Map();
                      for (const conn of graphData.external_connections) {
                        // Only consider if one end is in includedTables and the other is not, and the includedTables end is reachable
                        let extTable, extFieldId, thisTable, thisFieldId, thisNodeId, extNodeId;
                        if (includedTables.has(conn.from_table.id) && !includedTables.has(conn.to_table.id)) {
                          thisTable = conn.from_table;
                          thisFieldId = conn.from_field_id;
                          thisNodeId = conn.from_field_id;
                          extTable = conn.to_table;
                          extFieldId = conn.to_field_id;
                          extNodeId = conn.to_field_id;
                        } else if (!includedTables.has(conn.from_table.id) && includedTables.has(conn.to_table.id)) {
                          thisTable = conn.to_table;
                          thisFieldId = conn.to_field_id;
                          thisNodeId = conn.to_field_id;
                          extTable = conn.from_table;
                          extFieldId = conn.from_field_id;
                          extNodeId = conn.from_field_id;
                        } else {
                          continue;
                        }
                        // Only show if the includedTables end is reachable
                        if (!reachableNodeIds.has(thisNodeId)) continue;
                        if (!extTableMap.has(extTable.id)) {
                          extTableMap.set(extTable.id, { table: extTable, connections: [] });
                        }
                        extTableMap.get(extTable.id).connections.push({
                          thisTable, thisFieldId, extTable, extFieldId, conn, thisNodeId, extNodeId
                        });
                      }
                      // 3. Deduplicate edges (by from/to node IDs, regardless of direction)
                      return Array.from(extTableMap.values())
                        .filter(({ table }) => !includedTables.has(table.id))
                        .map(({ table, connections }) => {
                          const seenEdges = new Set<string>();
                          const uniqueConnections = connections.filter((c: any) => {
                            const key = c.thisNodeId < c.extNodeId
                              ? `${c.thisNodeId}_${c.extNodeId}`
                              : `${c.extNodeId}_${c.thisNodeId}`;
                            if (seenEdges.has(key)) return false;
                            seenEdges.add(key);
                            return true;
                          });
                          return (
                            <div
                              key={table.id}
                              style={{
                                background: includedTables && includedTables.has(table.id) ? '#dbeafe' : '#fff',
                                border: includedTables && includedTables.has(table.id) ? '1px solid #2563eb' : '1px solid #b6c2d1',
                                borderRadius: 4,
                                padding: '7px 12px',
                                cursor: 'pointer',
                                color: includedTables && includedTables.has(table.id) ? '#2563eb' : '#374151',
                                fontWeight: includedTables && includedTables.has(table.id) ? 700 : 500,
                                transition: 'all 0.2s',
                                marginBottom: 2
                              }}
                              onClick={() => handleToggleTable(table.id)}
                            >
                              <div style={{ fontWeight: 700 }}>{table.name}{includedTables && includedTables.has(table.id) ? ' (Remove)' : ' (Add)'}</div>
                              {/* Show all field connections for this table */}
                              <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>
                                {uniqueConnections.map((c: any, idx: number) => {
                                  const thisFieldName = fieldIdToName.get(c.thisFieldId) || fieldNameCache[c.thisFieldId] || (fieldNameLoading[c.thisFieldId] ? '...' : c.thisFieldId);
                                  const extFieldName = fieldIdToName.get(c.extFieldId) || fieldNameCache[c.extFieldId] || (fieldNameLoading[c.extFieldId] ? '...' : c.extFieldId);
                                  // Debug: log extFieldId, extFieldName, and node
                                  const extNode = graphData.nodes.find(n => n.id === c.extFieldId);
                                  console.log('External field debug:', {extFieldId: c.extFieldId, extFieldName, extNode});
                                  // Fetch external field name if missing
                                  if (!fieldIdToName.has(c.extFieldId) && !fieldNameCache[c.extFieldId] && !fieldNameLoading[c.extFieldId]) {
                                    ensureFieldName(c.extTable.id, c.extFieldId);
                                  }
                                  return (
                                    <div key={idx} style={{ marginBottom: 2 }}>
                                      <span style={{ color: '#2563eb' }}>{c.thisTable.name}</span>
                                      <span>:</span>
                                      <span style={{ fontWeight: 600 }}>{thisFieldName}</span>
                                      <span style={{ color: '#888', margin: '0 4px' }}>→</span>
                                      <span style={{ color: '#2563eb' }}>{c.extTable.name}</span>
                                      <span>:</span>
                                      <span style={{ fontWeight: 600 }}>{extFieldName}</span>
                                      <span style={{ color: '#888', margin: '0 4px' }}>[{c.conn.type}]</span>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          );
                        });
                    })()}
                  </div>
                )}
              </div>
            )}
            {/* Active Tables Panel */}
            {!includedTables ? null : (
              <div style={{
                background: '#f5f7fa',
                border: '1px solid #e5e7eb',
                borderRadius: 4,
                padding: '10px 14px',
                fontSize: 13,
                minWidth: 220,
                maxWidth: 320,
                maxHeight: 220,
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}>
                <div style={{ fontWeight: 700, color: '#2563eb', marginBottom: 8, cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                  onClick={() => setActiveTablesCollapsed(c => !c)}>
                  <span>Active Tables:</span>
                  <span style={{ marginLeft: 8 }}>{activeTablesCollapsed ? '▶' : '▼'}</span>
                </div>
                {!activeTablesCollapsed && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {Array.from(includedTables ?? []).map((tableId, idx) => {
                      let tableName = '';
                      const tableNode = graphData.nodes.find(n => n.meta && n.meta.type === 'table' && (n.id === -1 ? graphData.table.id === tableId : n.path && n.path.split('/')[2] === String(tableId)));
                      if (tableNode) {
                        tableName = tableNode.name;
                      } else {
                        const extConn = graphData.external_connections.find(conn => conn.from_table.id === tableId || conn.to_table.id === tableId);
                        if (extConn) {
                          tableName = extConn.from_table.id === tableId ? extConn.from_table.name : extConn.to_table.name;
                        } else {
                          tableName = `Table ${tableId}`;
                        }
                      }
                      const isPrimary = idx === 0;
                      return (
                        <span key={tableId} style={{ display: 'flex', alignItems: 'center', background: '#e0e7ef', borderRadius: 4, padding: '4px 10px', marginBottom: 4 }}>
                          <span style={{ fontWeight: 600, color: '#2563eb', marginRight: 6 }}>{tableName}</span>
                          <button
                            onClick={() => {
                              if (!isPrimary) removeTableFromGraph(tableId);
                            }}
                            disabled={isPrimary}
                            style={{
                              background: isPrimary ? '#ccc' : '#ef4444',
                              color: 'white',
                              border: 'none',
                              borderRadius: 3,
                              padding: '2px 8px',
                              fontSize: 12,
                              cursor: isPrimary ? 'not-allowed' : 'pointer',
                              marginLeft: 2
                            }}
                            title={isPrimary ? 'Cannot remove the primary table' : 'Remove table'}
                          >Remove</button>
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div style={{
          marginTop: '15px',
          padding: '10px',
          background: '#f3f4f6',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#666'
        }}>
          <strong>Legend:</strong> Red/Orange circles = table nodes, Blue circles = root fields, Green circles = subfields, 
          Blue double arrows = bidirectional equivalence, Orange double arrows = bidirectional possibly equivalence, Gray arrows = contains
        </div>
      </div>
    </div>
  );
} 