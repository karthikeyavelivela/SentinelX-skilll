import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import {
    Shield, Server, AlertTriangle, Wrench, TrendingUp, Activity,
    Target, Zap
} from 'lucide-react';
import {
    AreaChart, Area, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const KPICard = ({ title, value, subtitle, icon: Icon, color }) => (
    <div className="card group relative overflow-hidden bg-slate-800 border-slate-700 hover:border-blue-500/30">
        <div className={`absolute top-0 right-0 w-24 h-24 rounded-full blur-3xl opacity-10 ${color}`}></div>
        <div className="flex items-start justify-between relative">
            <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-1">{title}</p>
                <p className="text-3xl font-bold text-slate-100 mt-1">{value ?? '—'}</p>
                {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
            </div>
            <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
                <Icon className="w-6 h-6 text-slate-300" />
            </div>
        </div>
    </div>
);

export default function DashboardPage() {
    const [summary, setSummary] = useState({
        total_cves: 0, kev_listed: 0, critical_cves: 0, total_assets: 0,
        total_vulnerabilities: 0, open_vulnerabilities: 0, pending_patches: 0, completed_patches: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/dashboard/summary')
            .then(res => setSummary(res.data))
            .catch(() => {
                // Return empty state if API fails
                setSummary({
                    total_cves: 0, kev_listed: 0, critical_cves: 0, total_assets: 0,
                    total_vulnerabilities: 0, open_vulnerabilities: 0, pending_patches: 0, completed_patches: 0
                });
            })
            .finally(() => setLoading(false));
    }, []);

    // Empty data for charts when no real data exists
    const emptyTrendData = [{ date: 'No Data', cves: 0 }];
    const emptySeverityData = [{ name: 'No Data', value: 1, color: '#334155' }];

    return (
        <div>
            <Header title="Dashboard" subtitle="Security Posture Overview" />
            <div className="p-6 space-y-6">

                {/* KPI Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                    <KPICard title="Total CVEs" value={summary.total_cves?.toLocaleString()} subtitle="Threat Intelligence" icon={Shield} color="bg-blue-600" />
                    <KPICard title="Confirmed Exploits" value={summary.kev_listed} subtitle="CISA KEV Catalog" icon={AlertTriangle} color="bg-rose-600" />
                    <KPICard title="Monitored Assets" value={summary.total_assets} subtitle="Active Agents" icon={Server} color="bg-emerald-600" />
                    <KPICard title="Pending Patches" value={summary.pending_patches} subtitle="Action Required" icon={Wrench} color="bg-amber-600" />
                </div>

                {/* Secondary KPIs */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <KPICard title="Open Vulns" value={summary.open_vulnerabilities} icon={Target} color="bg-rose-500" />
                    <KPICard title="Critical Risk" value={summary.critical_cves} subtitle="CVSS ≥ 9.0" icon={Zap} color="bg-orange-500" />
                    <KPICard title="Remediated" value={summary.completed_patches} icon={Wrench} color="bg-blue-500" />
                </div>

                {/* Info Box if Empty */}
                {summary.total_cves === 0 && (
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 text-center">
                        <h3 className="text-lg font-semibold text-slate-200 mb-2">No Data Available</h3>
                        <p className="text-slate-400 mb-4">Run the ingestion script to populate threat intelligence data.</p>
                        <code className="bg-slate-900 px-3 py-1 rounded text-sm text-blue-400">python scripts/verify_ingestion_direct.py</code>
                    </div>
                )}

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* Trend Chart Placeholder */}
                    <div className="card lg:col-span-2">
                        <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-blue-400" /> Vulnerability Trend
                        </h3>
                        <div className="h-[280px] flex items-center justify-center text-slate-500 bg-slate-900/50 rounded-lg">
                            Chart data requires historical tracking (coming in v2)
                        </div>
                    </div>

                    {/* Severity Pie Placeholder */}
                    <div className="card">
                        <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                            <Activity className="w-4 h-4 text-blue-400" /> Severity Distribution
                        </h3>
                        <div className="h-[280px] flex items-center justify-center text-slate-500 bg-slate-900/50 rounded-lg">
                            No active vulnerabilities
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
