'use client';

import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useChatStore } from '@/store/chatStore';
import { Search, Wrench, FileText } from 'lucide-react';

function QueryNode({ data }: { data: any }) {
  return (
    <div className="px-4 py-2 rounded-xl bg-primary/20 border-2 border-primary text-sm font-medium text-foreground max-w-[200px]">
      <div className="flex items-center gap-2">
        <Search className="h-3.5 w-3.5 text-primary shrink-0" />
        <span className="truncate">{data.label}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-primary !w-2 !h-2" />
    </div>
  );
}

function ToolNode({ data }: { data: any }) {
  return (
    <div className="px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-xs font-medium text-foreground">
      <Handle type="target" position={Position.Top} className="!bg-yellow-500 !w-2 !h-2" />
      <div className="flex items-center gap-1.5">
        <Wrench className="h-3 w-3 text-yellow-500 shrink-0" />
        <span>{data.label}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-yellow-500 !w-2 !h-2" />
    </div>
  );
}

function SourceNode({ data }: { data: any }) {
  return (
    <div className="px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/30 text-xs text-foreground max-w-[180px]">
      <Handle type="target" position={Position.Top} className="!bg-green-500 !w-2 !h-2" />
      <div className="flex items-center gap-1.5 mb-1">
        <FileText className="h-3 w-3 text-green-500 shrink-0" />
        <span className="font-medium">{data.label}</span>
      </div>
      {data.section && (
        <div className="text-[10px] text-foreground/50">{data.section}</div>
      )}
      {data.page != null && (
        <div className="text-[10px] text-foreground/40">p.{data.page}</div>
      )}
    </div>
  );
}

const nodeTypes = {
  query: QueryNode,
  tool: ToolNode,
  source: SourceNode,
};

export function CitationGraph() {
  const citationGraph = useChatStore((s) => s.citationGraph);

  const { nodes, edges } = useMemo(() => {
    if (!citationGraph) return { nodes: [], edges: [] };

    const rawNodes = citationGraph.nodes || [];
    const rawEdges = citationGraph.edges || [];

    // Layout: query at top, tools in middle, sources at bottom
    const queryNodes = rawNodes.filter((n: any) => n.type === 'query');
    const toolNodes = rawNodes.filter((n: any) => n.type === 'tool');
    const sourceNodes = rawNodes.filter((n: any) => n.type === 'source');

    const nodes: Node[] = [];

    // Query node centered
    queryNodes.forEach((n: any, i: number) => {
      nodes.push({ id: n.id, type: 'query', position: { x: 250, y: 0 }, data: n });
    });

    // Tool nodes spread horizontally
    const toolSpacing = 200;
    const toolStartX = 250 - ((toolNodes.length - 1) * toolSpacing) / 2;
    toolNodes.forEach((n: any, i: number) => {
      nodes.push({ id: n.id, type: 'tool', position: { x: toolStartX + i * toolSpacing, y: 100 }, data: n });
    });

    // Source nodes under their parent tool
    const toolChildCount: Record<string, number> = {};
    const toolChildIndex: Record<string, number> = {};
    rawEdges.forEach((e: any) => {
      if (e.source.startsWith('tool-')) {
        toolChildCount[e.source] = (toolChildCount[e.source] || 0) + 1;
      }
    });

    sourceNodes.forEach((n: any) => {
      const parentEdge = rawEdges.find((e: any) => e.target === n.id);
      const parentId = parentEdge?.source || 'tool-unknown';
      const parentNode = nodes.find((nd) => nd.id === parentId);
      const parentX = parentNode?.position.x || 250;

      const idx = toolChildIndex[parentId] || 0;
      toolChildIndex[parentId] = idx + 1;
      const total = toolChildCount[parentId] || 1;
      const spacing = 160;
      const startX = parentX - ((total - 1) * spacing) / 2;

      nodes.push({
        id: n.id,
        type: 'source',
        position: { x: startX + idx * spacing, y: 220 + (idx % 2) * 40 },
        data: n,
      });
    });

    const edges: Edge[] = rawEdges.map((e: any, i: number) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      animated: true,
      style: { stroke: 'rgba(139, 92, 246, 0.3)', strokeWidth: 2 },
    }));

    return { nodes, edges };
  }, [citationGraph]);

  if (!citationGraph || nodes.length === 0) return null;

  return (
    <div style={{ width: '100%', height: '100%' }} className="rounded-xl border border-border/50 bg-background/50 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        proOptions={{ hideAttribution: true }}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={false}
        minZoom={0.5}
        maxZoom={1.5}
      >
        <Background gap={20} size={1} color="rgba(255,255,255,0.03)" />
        <Controls showInteractive={false} className="!bg-background !border-border !shadow-none [&_button]:!bg-background [&_button]:!border-border [&_button]:!text-foreground/60" />
      </ReactFlow>
    </div>
  );
}
