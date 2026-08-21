import React, { useMemo, useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  FiShare2,
  FiUser,
  FiPhone,
  FiMail,
  FiKey,
  FiGlobe,
  FiBriefcase,
  FiMapPin,
  FiInfo,
  FiX,
} from 'react-icons/fi';

const NODE_COLORS = {
  PERSON: { bg: '#083344', border: '#06b6d4', text: '#22d3ee' },
  PHONE: { bg: '#064e3b', border: '#10b981', text: '#34d399' },
  EMAIL: { bg: '#312e81', border: '#6366f1', text: '#818cf8' },
  CRYPTO_ADDRESS: { bg: '#451a03', border: '#f59e0b', text: '#fbbf24' },
  IP_ADDRESS: { bg: '#4c1d95', border: '#8b5cf6', text: '#a78bfa' },
  ORG: { bg: '#1e3a8a', border: '#3b82f6', text: '#60a5fa' },
  LOCATION: { bg: '#4c0519', border: '#f43f5e', text: '#fb7185' },
};

// Custom Cyber Node Component
const ForensicNode = ({ data }) => {
  const colors = NODE_COLORS[data.type] || { bg: '#0f172a', border: '#475569', text: '#94a3b8' };
  return (
    <div
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
      }}
      className="px-3.5 py-2.5 rounded-xl border-2 shadow-lg shadow-black/40 min-w-[140px] max-w-[200px] text-left transition-all hover:scale-105"
    >
      <div className="flex items-center justify-between gap-1 mb-1">
        <span
          style={{ color: colors.text }}
          className="text-[9px] font-mono font-bold uppercase tracking-wider truncate"
        >
          {data.type}
        </span>
      </div>
      <div className="text-xs font-semibold font-mono text-slate-100 truncate" title={data.label}>
        {data.label}
      </div>
    </div>
  );
};

const nodeTypes = {
  forensicNode: ForensicNode,
};

export const GraphView = ({ entities = [], relationships = [], minConfidence = 0.5 }) => {
  const [selectedNode, setSelectedNode] = useState(null);

  // Compute Layout Positions (Circular / Ring Layout)
  const { initialNodes, initialEdges } = useMemo(() => {
    // Filter relationships by confidence
    const filteredRels = relationships.filter(
      (r) => parseFloat(r.confidence || 0) >= minConfidence
    );

    // Map entity ID -> entity
    const entMap = new Map();
    entities.forEach((e) => entMap.set(e.id, e));

    const totalNodes = entities.length;
    const radius = Math.max(220, totalNodes * 35);
    const centerX = 350;
    const centerY = 280;

    const nodes = entities.map((ent, idx) => {
      const angle = (idx / (totalNodes || 1)) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: ent.id,
        type: 'forensicNode',
        position: { x, y },
        data: {
          label: ent.value,
          type: ent.entity_type,
          entity: ent,
        },
      };
    });

    const edges = filteredRels
      .filter((r) => entMap.has(r.source_entity_id) && entMap.has(r.target_entity_id))
      .map((r) => {
        const conf = parseFloat(r.confidence || 0.8);
        return {
          id: r.id || `${r.source_entity_id}-${r.target_entity_id}`,
          source: r.source_entity_id,
          target: r.target_entity_id,
          label: `${r.relationship_type} (${(conf * 100).toFixed(0)}%)`,
          animated: r.relationship_type.includes('CALL') || r.relationship_type.includes('MESSAGE'),
          style: {
            stroke: conf > 0.85 ? '#06b6d4' : '#6366f1',
            strokeWidth: conf > 0.85 ? 2.5 : 1.5,
          },
          labelStyle: {
            fill: '#e2e8f0',
            fontWeight: 600,
            fontSize: 10,
            fontFamily: 'monospace',
          },
          labelBgStyle: {
            fill: '#0f172a',
            fillOpacity: 0.85,
            rx: 4,
            ry: 4,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: conf > 0.85 ? '#06b6d4' : '#6366f1',
          },
        };
      });

    return { initialNodes: nodes, initialEdges: edges };
  }, [entities, relationships, minConfidence]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes/edges if data changes
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node.data.entity);
  }, []);

  return (
    <div className="relative w-full h-[600px] rounded-2xl overflow-hidden glass-panel border border-slate-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={2}
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls className="bg-slate-900/90 border border-slate-800 text-slate-200 fill-slate-200 rounded-xl" />
        <MiniMap
          nodeColor={(n) => NODE_COLORS[n.data.type]?.border || '#3b82f6'}
          maskColor="rgba(8, 12, 20, 0.7)"
          className="bg-slate-950/90 border border-slate-800 rounded-xl"
        />
      </ReactFlow>

      {/* Node Inspector Drawer */}
      {selectedNode && (
        <div className="absolute right-4 top-4 bottom-4 w-80 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-2xl z-20 flex flex-col justify-between text-left animate-in slide-in-from-right duration-200">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <FiInfo className="text-cyan-400 w-4 h-4" />
                <span className="text-sm font-semibold text-slate-100">Entity Inspector</span>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              >
                <FiX className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] font-mono text-slate-500 uppercase block">ENTITY TYPE</span>
                <span className="text-cyan-400 font-mono font-bold text-sm">{selectedNode.entity_type}</span>
              </div>

              <div>
                <span className="text-[10px] font-mono text-slate-500 uppercase block">DISCOVERED VALUE</span>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-slate-200 break-all text-xs">
                  {selectedNode.value}
                </div>
              </div>

              {selectedNode.artifact_id && (
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">ORIGINATING ARTIFACT</span>
                  <span className="text-slate-400 font-mono text-xs">#{selectedNode.artifact_id}</span>
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <button
              onClick={() => {
                navigator.clipboard.writeText(selectedNode.value);
              }}
              className="w-full py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/40 text-cyan-300 font-semibold text-xs transition-all text-center"
            >
              Copy Entity Value
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
