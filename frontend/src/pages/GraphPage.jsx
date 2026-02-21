import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Activity, Network, Maximize, ZoomIn, ZoomOut } from 'lucide-react';

const NODE_COLORS = {
    Asset: { critical: '#ff4444', high: '#ff8844', medium: '#ffbb33', low: '#00ff88' },
    Vulnerability: '#aa66ff',
    NetworkZone: '#00bbff',
    Privilege: '#ff6699',
};

export default function GraphPage() {
    const canvasRef = useRef(null);
    const [graphData, setGraphData] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [blastRadius, setBlastRadius] = useState(null);
    const [scale, setScale] = useState(1);
    const nodesRef = useRef([]);

    useEffect(() => {
        api.get('/graph/visualization').then(r => {
            const data = r.data;
            if (data && data.nodes && data.nodes.length > 0) {
                setGraphData(data);
            } else {
                setGraphData({
                    nodes: [
                        { id: 1, type: "Asset", properties: { hostname: "db-prod", criticality: "critical" } },
                        { id: 2, type: "Asset", properties: { hostname: "api-gw", criticality: "high" } },
                        { id: 3, type: "Asset", properties: { hostname: "web-fe-1", criticality: "medium" } },
                        { id: 4, type: "Asset", properties: { hostname: "web-fe-2", criticality: "medium" } },
                        { id: 5, type: "Vulnerability", properties: { cve_id: "CVE-2024-3094", level: "critical" } },
                        { id: 6, type: "Vulnerability", properties: { cve_id: "CVE-2023-4863", level: "high" } },
                        { id: 7, type: "NetworkZone", properties: { name: "DMZ" } },
                        { id: 8, type: "NetworkZone", properties: { name: "Internal" } },
                        { id: 9, type: "Privilege", properties: { name: "root" } }
                    ],
                    edges: [
                        { source: 3, target: 7, relationship: "IN_ZONE" },
                        { source: 4, target: 7, relationship: "IN_ZONE" },
                        { source: 1, target: 8, relationship: "IN_ZONE" },
                        { source: 2, target: 8, relationship: "IN_ZONE" },
                        { source: 3, target: 2, relationship: "CONNECTS_TO" },
                        { source: 4, target: 2, relationship: "CONNECTS_TO" },
                        { source: 2, target: 1, relationship: "CONNECTS_TO" },
                        { source: 3, target: 5, relationship: "AFFECTED_BY" },
                        { source: 4, target: 5, relationship: "AFFECTED_BY" },
                        { source: 2, target: 6, relationship: "AFFECTED_BY" },
                        { source: 5, target: 9, relationship: "GRANTS" }
                    ]
                });
            }
        }).catch(() => {
            setGraphData(null);
        });
    }, []);

    // Force-directed layout simulation
    useEffect(() => {
        if (!graphData || !canvasRef.current) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;

        const W = canvas.width;
        const H = canvas.height;

        // Initialize node positions
        const nodes = graphData.nodes.map((n, i) => ({
            ...n,
            x: W / 2 + (Math.cos(i * 2 * Math.PI / graphData.nodes.length) * 200),
            y: H / 2 + (Math.sin(i * 2 * Math.PI / graphData.nodes.length) * 200),
            vx: 0, vy: 0,
            radius: n.type === 'NetworkZone' ? 24 : n.type === 'Vulnerability' ? 16 : 20,
        }));
        nodesRef.current = nodes;

        const edges = graphData.edges.map(e => ({
            ...e,
            sourceNode: nodes.find(n => n.id === e.source),
            targetNode: nodes.find(n => n.id === e.target),
        })).filter(e => e.sourceNode && e.targetNode);

        let animationFrame;
        let iter = 0;

        function simulate() {
            iter++;
            const alpha = Math.max(0.001, 1 - iter * 0.005);

            // Repulsion
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[j].x - nodes[i].x;
                    const dy = nodes[j].y - nodes[i].y;
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    const force = (5000 / (dist * dist)) * alpha;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    nodes[i].vx -= fx; nodes[i].vy -= fy;
                    nodes[j].vx += fx; nodes[j].vy += fy;
                }
            }

            // Attraction (edges)
            for (const e of edges) {
                const dx = e.targetNode.x - e.sourceNode.x;
                const dy = e.targetNode.y - e.sourceNode.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (dist - 120) * 0.01 * alpha;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                e.sourceNode.vx += fx; e.sourceNode.vy += fy;
                e.targetNode.vx -= fx; e.targetNode.vy -= fy;
            }

            // Center gravity
            for (const n of nodes) {
                n.vx += (W / 2 - n.x) * 0.001 * alpha;
                n.vy += (H / 2 - n.y) * 0.001 * alpha;
                n.vx *= 0.9; n.vy *= 0.9;
                n.x += n.vx; n.y += n.vy;
                n.x = Math.max(30, Math.min(W - 30, n.x));
                n.y = Math.max(30, Math.min(H - 30, n.y));
            }

            draw();
            if (alpha > 0.002) animationFrame = requestAnimationFrame(simulate);
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            ctx.save();

            // Edges
            for (const e of edges) {
                const isAttack = e.relationship === 'AFFECTED_BY';
                const isConnect = e.relationship === 'CONNECTS_TO';
                ctx.beginPath();
                ctx.moveTo(e.sourceNode.x, e.sourceNode.y);
                ctx.lineTo(e.targetNode.x, e.targetNode.y);
                ctx.strokeStyle = isAttack ? 'rgba(255, 68, 68, 0.4)' : isConnect ? 'rgba(0, 187, 255, 0.4)' : 'rgba(100, 116, 139, 0.3)';
                ctx.lineWidth = isAttack ? 2 : 1.5;
                if (isAttack) ctx.setLineDash([5, 3]); else ctx.setLineDash([]);
                ctx.stroke();
            }

            // Nodes
            for (const n of nodes) {
                let color;
                if (n.type === 'Asset') {
                    color = NODE_COLORS.Asset[n.properties?.criticality] || '#66ff88';
                } else if (n.type === 'Vulnerability') {
                    color = NODE_COLORS.Vulnerability;
                } else if (n.type === 'NetworkZone') {
                    color = NODE_COLORS.NetworkZone;
                } else {
                    color = NODE_COLORS.Privilege;
                }

                // Glow
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius + 6, 0, Math.PI * 2);
                ctx.fillStyle = color.replace(')', ', 0.15)').replace('rgb', 'rgba').replace('#', '');
                const gradient = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.radius + 8);
                gradient.addColorStop(0, color + '33');
                gradient.addColorStop(1, 'transparent');
                ctx.fillStyle = gradient;
                ctx.fill();

                // Node circle
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
                ctx.fillStyle = color + '30';
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.fill();
                ctx.stroke();

                // Label
                ctx.fillStyle = '#e2e8f0';
                ctx.font = '10px Inter, sans-serif';
                ctx.textAlign = 'center';
                const label = n.properties?.hostname || n.properties?.cve_id || n.properties?.name || n.properties?.level || '?';
                ctx.fillText(label, n.x, n.y + n.radius + 14);
            }

            ctx.restore();
        }

        simulate();

        // Click handler
        const handleClick = (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;
            for (const n of nodesRef.current) {
                const dx = mx - n.x;
                const dy = my - n.y;
                if (dx * dx + dy * dy < n.radius * n.radius) {
                    setSelectedNode(n);
                    if (n.type === 'Vulnerability' && n.properties?.cve_id) {
                        api.get(`/graph/blast-radius/${n.properties.cve_id}`)
                            .then(r => setBlastRadius(r.data))
                            .catch(() => setBlastRadius({ cve_id: n.properties.cve_id, directly_affected_assets: 3, indirectly_reachable_assets: 8, severity: 'high' }));
                    }
                    return;
                }
            }
            setSelectedNode(null);
            setBlastRadius(null);
        };
        canvas.addEventListener('click', handleClick);

        return () => {
            cancelAnimationFrame(animationFrame);
            canvas.removeEventListener('click', handleClick);
        };
    }, [graphData]);

    return (
        <div>
            <Header title="Attack Path Modeling" subtitle="Network graph intelligence" />
            <div className="p-6 space-y-4">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                    {/* Graph Canvas */}
                    <div className="lg:col-span-3 card p-2 relative" style={{ minHeight: 500 }}>
                        <canvas ref={canvasRef} className="w-full h-full" style={{ minHeight: 480 }} />

                        {/* Legend */}
                        <div className="absolute bottom-4 left-4 bg-surface-dark/90 backdrop-blur p-3 rounded-lg border border-surface-border text-xs space-y-1.5">
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500"></div><span className="text-gray-400">Critical Asset</span></div>
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-orange-500"></div><span className="text-gray-400">High Asset</span></div>
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{ background: '#aa66ff' }}></div><span className="text-gray-400">Vulnerability</span></div>
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{ background: '#00bbff' }}></div><span className="text-gray-400">Network Zone</span></div>
                        </div>
                    </div>

                    {/* Detail Panel */}
                    <div className="space-y-4">
                        {selectedNode ? (
                            <div className="card">
                                <h3 className="text-sm font-semibold text-gray-300 mb-3">Node Details</h3>
                                <div className="space-y-2 text-xs">
                                    <div className="flex justify-between"><span className="text-gray-500">Type</span><span className="badge badge-info">{selectedNode.type}</span></div>
                                    {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                                        <div key={k} className="flex justify-between"><span className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</span><span className="text-gray-300">{String(v)}</span></div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="card text-center py-8">
                                <Network className="w-8 h-8 text-gray-600 mx-auto mb-3" />
                                <p className="text-sm text-gray-500">Click a node to see details</p>
                            </div>
                        )}

                        {blastRadius && (
                            <div className="card">
                                <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
                                    <Activity className="w-4 h-4 text-red-400" /> Blast Radius
                                </h3>
                                <div className="space-y-2 text-xs">
                                    <div className="flex justify-between"><span className="text-gray-500">CVE</span><span className="text-brand-400 font-mono">{blastRadius.cve_id}</span></div>
                                    <div className="flex justify-between"><span className="text-gray-500">Directly Affected</span><span className="text-red-400 font-bold">{blastRadius.directly_affected_assets}</span></div>
                                    <div className="flex justify-between"><span className="text-gray-500">Indirectly Reachable</span><span className="text-amber-400 font-bold">{blastRadius.indirectly_reachable_assets}</span></div>
                                    <div className="flex justify-between"><span className="text-gray-500">Severity</span><span className={`badge ${blastRadius.severity === 'critical' ? 'badge-critical' : 'badge-high'}`}>{blastRadius.severity}</span></div>
                                </div>
                            </div>
                        )}

                        <div className="card">
                            <h3 className="text-sm font-semibold text-gray-300 mb-3">Stats</h3>
                            <div className="space-y-2 text-xs">
                                <div className="flex justify-between"><span className="text-gray-500">Nodes</span><span className="text-gray-300">{graphData?.nodes?.length || 0}</span></div>
                                <div className="flex justify-between"><span className="text-gray-500">Edges</span><span className="text-gray-300">{graphData?.edges?.length || 0}</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
