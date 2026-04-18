'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Network,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Filter,
  Loader2,
  Music,
} from 'lucide-react';
import {
  getSonicMap,
  getCluster,
  type GraphNode,
  type GraphEdge,
  type SonicMapResponse,
} from '@/lib/feature-endpoints';
import { cn } from '@/lib/utils';

export default function SonicGraphPage() {
  const [data, setData] = useState<SonicMapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [clusterData, setClusterData] = useState<{
    source: { filename: string };
    similar: Array<{ filename: string; score: number; genre?: string[] }>;
  } | null>(null);
  const [threshold, setThreshold] = useState(0.6);
  const [nodeLimit, setNodeLimit] = useState(200);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const animFrameRef = useRef<number>(0);

  useEffect(() => {
    loadGraph();
  }, [threshold, nodeLimit]);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await getSonicMap(nodeLimit, threshold);
      // Assign initial positions using force layout approximation
      const nodes = resp.nodes.map((n, i) => ({
        ...n,
        x: Math.cos((i / resp.nodes.length) * Math.PI * 2) * 300 + 400,
        y: Math.sin((i / resp.nodes.length) * Math.PI * 2) * 300 + 400,
      }));
      setData({ ...resp, nodes });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [nodeLimit, threshold]);

  // Simple force-directed simulation
  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const nodes = [...data.nodes];
    const edges = data.edges;
    const vx = new Float32Array(nodes.length);
    const vy = new Float32Array(nodes.length);
    let iterations = 0;

    function simulate() {
      if (iterations > 200) {
        drawFinal();
        return;
      }

      // Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const force = 500 / (dist * dist);
          vx[i] += (dx / dist) * force;
          vy[i] += (dy / dist) * force;
          vx[j] -= (dx / dist) * force;
          vy[j] -= (dy / dist) * force;
        }
      }

      // Attraction along edges
      for (const edge of edges) {
        const si = parseInt(edge.source);
        const ti = parseInt(edge.target);
        if (si >= nodes.length || ti >= nodes.length) continue;
        const dx = nodes[ti].x - nodes[si].x;
        const dy = nodes[ti].y - nodes[si].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const force = dist * 0.01 * edge.weight;
        vx[si] += (dx / Math.max(dist, 1)) * force;
        vy[si] += (dy / Math.max(dist, 1)) * force;
        vx[ti] -= (dx / Math.max(dist, 1)) * force;
        vy[ti] -= (dy / Math.max(dist, 1)) * force;
      }

      // Apply velocity with damping
      for (let i = 0; i < nodes.length; i++) {
        nodes[i].x += vx[i] * 0.5;
        nodes[i].y += vy[i] * 0.5;
        vx[i] *= 0.8;
        vy[i] *= 0.8;
      }

      iterations++;
      draw(ctx!, canvas, nodes, edges);
      animFrameRef.current = requestAnimationFrame(simulate);
    }

    function drawFinal() {
      draw(ctx!, canvas, nodes, edges);
      setData((prev) => (prev ? { ...prev, nodes: [...nodes] } : null));
    }

    simulate();
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [data?.nodes.length]);

  const handleNodeClick = async (node: GraphNode) => {
    setSelectedNode(node);
    try {
      const result = await getCluster(node.filename, 8);
      setClusterData(result);
    } catch {
      setClusterData(null);
    }
  };

  // Canvas click handler
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data) return;

    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = (e.clientX - rect.left - offset.x) / zoom;
      const my = (e.clientY - rect.top - offset.y) / zoom;

      for (const node of data.nodes) {
        const dx = node.x - mx;
        const dy = node.y - my;
        if (dx * dx + dy * dy < 100) {
          handleNodeClick(node);
          return;
        }
      }
      setSelectedNode(null);
      setClusterData(null);
    };

    canvas.addEventListener('click', handleClick);
    return () => canvas.removeEventListener('click', handleClick);
  }, [data, zoom, offset]);

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <Network className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Sonic Graph</h1>
            <p className="text-sm text-white/50">
              Visualize sonic relationships between your samples
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-xs text-white/50">Threshold</label>
            <input
              type="range"
              min={0.1}
              max={0.95}
              step={0.05}
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-24 accent-cyan-500"
            />
            <span className="text-xs text-white/70 w-8">{threshold}</span>
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setZoom((z) => Math.min(z * 1.2, 5))}
              className="p-2 rounded-lg bg-white/5 text-white/50 hover:text-white hover:bg-white/10"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={() => setZoom((z) => Math.max(z / 1.2, 0.2))}
              className="p-2 rounded-lg bg-white/5 text-white/50 hover:text-white hover:bg-white/10"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <button
              onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }); }}
              className="p-2 rounded-lg bg-white/5 text-white/50 hover:text-white hover:bg-white/10"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Graph Canvas */}
        <div className="flex-1 rounded-2xl border border-white/10 bg-white/5 overflow-hidden relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
              <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
            </div>
          )}
          <canvas
            ref={canvasRef}
            width={800}
            height={600}
            className="w-full h-[600px] cursor-crosshair"
          />
          {data && (
            <div className="absolute bottom-4 left-4 flex gap-4 text-xs text-white/40">
              <span>{data.nodes.length} nodes</span>
              <span>{data.edges.length} edges</span>
              <span>{data.clusters.length} clusters</span>
            </div>
          )}
        </div>

        {/* Sidebar: Node Detail + Clusters */}
        <div className="w-80 space-y-4">
          {selectedNode ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 rounded-xl bg-white/5 border border-white/10"
            >
              <h3 className="text-sm font-bold text-white mb-2 truncate">
                {selectedNode.filename}
              </h3>
              <div className="space-y-1 text-xs text-white/60">
                {selectedNode.bpm && <p>BPM: {selectedNode.bpm}</p>}
                {selectedNode.key && <p>Key: {selectedNode.key}</p>}
                {selectedNode.energy && <p>Energy: {selectedNode.energy}</p>}
                {selectedNode.genre.length > 0 && (
                  <p>Genres: {selectedNode.genre.join(', ')}</p>
                )}
              </div>

              {clusterData && clusterData.similar.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-xs font-semibold text-white/80 mb-2">
                    Most Similar
                  </h4>
                  <div className="space-y-2">
                    {clusterData.similar.map((s) => (
                      <div
                        key={s.filename}
                        className="flex items-center gap-2 p-2 rounded-lg bg-white/5"
                      >
                        <Music className="h-3 w-3 text-cyan-400 flex-shrink-0" />
                        <span className="text-xs text-white/70 truncate flex-1">
                          {s.filename}
                        </span>
                        <span className="text-[10px] text-cyan-400">
                          {(s.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="p-6 rounded-xl bg-white/5 border border-white/10 text-center">
              <Network className="h-8 w-8 text-white/20 mx-auto mb-2" />
              <p className="text-xs text-white/40">
                Click a node to see details
              </p>
            </div>
          )}

          {/* Clusters */}
          {data && data.clusters.length > 0 && (
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <h3 className="text-xs font-semibold text-white/80 mb-3">
                Genre Clusters
              </h3>
              <div className="space-y-2">
                {data.clusters.slice(0, 8).map((c) => (
                  <div
                    key={c.label}
                    className="flex items-center justify-between"
                  >
                    <span className="text-xs text-white/60 truncate">
                      {c.label}
                    </span>
                    <span className="text-xs text-cyan-400 tabular-nums">
                      {c.count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function draw(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  nodes: GraphNode[],
  edges: GraphEdge[]
) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw edges
  ctx.strokeStyle = 'rgba(100, 200, 255, 0.08)';
  ctx.lineWidth = 0.5;
  for (const edge of edges) {
    const s = nodes[parseInt(edge.source)];
    const t = nodes[parseInt(edge.target)];
    if (!s || !t) continue;
    ctx.beginPath();
    ctx.moveTo(s.x, s.y);
    ctx.lineTo(t.x, t.y);
    ctx.globalAlpha = edge.weight * 0.3;
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // Draw nodes
  for (const node of nodes) {
    const hue = node.genre.length
      ? (node.genre[0].charCodeAt(0) * 15) % 360
      : 200;
    ctx.beginPath();
    ctx.arc(node.x, node.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${hue}, 70%, 60%, 0.8)`;
    ctx.fill();
    ctx.strokeStyle = `hsla(${hue}, 70%, 70%, 0.3)`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}
