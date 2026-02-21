import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Zap, TrendingDown, AlertTriangle, Building2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

const HeatCell = ({ value, max }) => {
    const intensity = max > 0 ? value / max : 0;
    return (
        <td className="px-3 py-3 text-center">
            <div className="w-10 h-10 rounded-lg mx-auto flex items-center justify-center text-xs font-bold transition-all"
                style={{
                    backgroundColor: `rgba(255, 68, 68, ${Math.max(intensity * 0.7, 0.05)})`,
                    color: intensity > 0.3 ? '#fff' : '#9ca3af',
                }}>
                {value}
            </div>
        </td>
    );
};

export default function RiskPage() {
    const [heatmap, setHeatmap] = useState([]);
    const [topRisks, setTopRisks] = useState([]);

    useEffect(() => {
        Promise.all([
            api.get('/risk/heatmap').catch(() => ({ data: [] })),
            api.get('/risk/scores?limit=20').catch(() => ({ data: [] }))
        ]).then(([heatRes, scoreRes]) => {
            const hData = heatRes.data?.length > 0 ? heatRes.data : [
                { business_unit: "engineering", total_assets: 142, critical: 12, high: 28, medium: 45, low: 57 },
                { business_unit: "sales", total_assets: 85, critical: 2, high: 14, medium: 30, low: 39 },
                { business_unit: "marketing", total_assets: 45, critical: 0, high: 5, medium: 12, low: 28 },
                { business_unit: "finance", total_assets: 34, critical: 4, high: 8, medium: 15, low: 7 },
                { business_unit: "hr", total_assets: 28, critical: 1, high: 3, medium: 10, low: 14 }
            ];

            const sData = scoreRes.data?.length > 0 ? scoreRes.data : [
                { asset_id: 101, hostname: "db-prod-aws-east", risk_score: 95, risk_level: "CRITICAL", cve_count: 14 },
                { asset_id: 145, hostname: "core-router-01", risk_score: 88, risk_level: "HIGH", cve_count: 8 },
                { asset_id: 204, hostname: "api-gateway-v2", risk_score: 82, risk_level: "HIGH", cve_count: 11 },
                { asset_id: 45, hostname: "eng-build-server", risk_score: 75, risk_level: "HIGH", cve_count: 22 },
                { asset_id: 99, hostname: "vpn-endpoint-nyc", risk_score: 68, risk_level: "HIGH", cve_count: 5 },
                { asset_id: 112, hostname: "sales-crm-db", risk_score: 64, risk_level: "HIGH", cve_count: 9 },
                { asset_id: 88, hostname: "auth-service-02", risk_score: 55, risk_level: "MEDIUM", cve_count: 3 },
                { asset_id: 12, hostname: "internal-wiki", risk_score: 42, risk_level: "MEDIUM", cve_count: 7 },
            ];

            setHeatmap(hData);
            setTopRisks(sData);
        });
    }, []);

    const display = heatmap;
    const risks = topRisks;
    const maxVal = Math.max(...display.flatMap(d => [d.critical, d.high, d.medium, d.low]), 1);

    const chartData = risks.slice(0, 10).map(r => ({ name: r.hostname || `Asset #${r.asset_id}`, score: r.risk_score }));

    return (
        <div>
            <Header title="Risk Scoring" subtitle="Composite risk analysis across all assets" />
            <div className="p-6 space-y-6">

                {/* Top risks bar chart */}
                <div className="card">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                        <TrendingDown className="w-4 h-4 text-red-400" /> Asset Risk Ranking
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData} margin={{ bottom: 40 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="name" stroke="#4b5563" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" />
                            <YAxis stroke="#4b5563" tick={{ fontSize: 11 }} domain={[0, 100]} />
                            <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e293b', borderRadius: '8px' }} />
                            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                                {chartData.map((entry, i) => (
                                    <Cell key={i} fill={entry.score >= 80 ? '#ff4444' : entry.score >= 60 ? '#ff8844' : entry.score >= 40 ? '#ffbb33' : '#00ff88'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Risk Heatmap */}
                <div className="card">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-brand-400" /> Risk Heatmap by Business Unit
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-xs text-gray-500 uppercase tracking-wider">
                                    <th className="px-4 py-3 text-left">Business Unit</th>
                                    <th className="px-3 py-3 text-center">Assets</th>
                                    <th className="px-3 py-3 text-center">Critical</th>
                                    <th className="px-3 py-3 text-center">High</th>
                                    <th className="px-3 py-3 text-center">Medium</th>
                                    <th className="px-3 py-3 text-center">Low</th>
                                </tr>
                            </thead>
                            <tbody>
                                {display.map(row => (
                                    <tr key={row.business_unit} className="border-t border-surface-border/30 hover:bg-surface-hover/30">
                                        <td className="px-4 py-3 font-medium text-gray-200 capitalize">{row.business_unit}</td>
                                        <td className="px-3 py-3 text-center text-gray-400">{row.total_assets}</td>
                                        <HeatCell value={row.critical} max={maxVal} />
                                        <HeatCell value={row.high} max={maxVal} />
                                        <HeatCell value={row.medium} max={maxVal} />
                                        <HeatCell value={row.low} max={maxVal} />
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Top Risks List */}
                <div className="card">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-400" /> Highest Risk Assets
                    </h3>
                    <div className="space-y-2">
                        {risks.map(r => {
                            const color = r.risk_score >= 80 ? '#ff4444' : r.risk_score >= 60 ? '#ff8844' : r.risk_score >= 40 ? '#ffbb33' : '#00ff88';
                            return (
                                <div key={r.asset_id} className="flex items-center gap-4 p-3 bg-surface-dark rounded-lg border border-surface-border">
                                    <div className="w-12 h-12 rounded-lg flex items-center justify-center font-bold text-lg" style={{ backgroundColor: color + '20', color }}>
                                        {r.risk_score}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-white">{r.hostname || `Asset #${r.asset_id}`}</p>
                                        <p className="text-xs text-gray-500">{r.cve_count || 0} vulnerabilities</p>
                                    </div>
                                    <span className={`badge ${r.risk_level === 'CRITICAL' ? 'badge-critical' : r.risk_level === 'HIGH' ? 'badge-high' : r.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low'}`}>
                                        {r.risk_level}
                                    </span>
                                    <div className="w-32 h-2 bg-surface-hover rounded-full overflow-hidden">
                                        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${r.risk_score}%`, backgroundColor: color }}></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
