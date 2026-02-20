import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Shield, Search, Filter, ExternalLink, AlertTriangle, Clock, Download } from 'lucide-react';

const SEVERITIES = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export default function CVEsPage() {
    const [cves, setCves] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [severity, setSeverity] = useState('ALL');
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);

    useEffect(() => {
        setLoading(true);
        const params = { page, per_page: 25 };
        if (severity !== 'ALL') params.severity = severity;
        if (search) params.search = search;

        api.get('/cves', { params })
            .then(res => {
                setCves(res.data.items || res.data || []);
                setTotal(res.data.total || 0);
            })
            .catch(() => {
                setCves([]);
                setTotal(0);
            })
            .finally(() => setLoading(false));
    }, [page, severity, search]);

    const getBadge = (sev) => {
        const map = { CRITICAL: 'badge-critical', HIGH: 'badge-high', MEDIUM: 'badge-medium', LOW: 'badge-low' };
        return map[sev] || 'badge-info';
    };

    return (
        <div>
            <Header title="Vulnerability Intelligence" subtitle={`${total} CVEs tracked`} />
            <div className="p-6 space-y-4">

                {/* Filters Bar */}
                <div className="card flex flex-wrap items-center gap-4">
                    <div className="relative flex-1 min-w-[200px]">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input
                            type="text" placeholder="Search CVE ID, vendor, description..."
                            value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                            className="w-full pl-10 pr-4 py-2.5 bg-surface-dark border border-surface-border rounded-lg text-sm text-gray-300 placeholder-gray-600 focus:outline-none focus:border-brand-500"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-gray-500" />
                        {SEVERITIES.map(s => (
                            <button
                                key={s}
                                onClick={() => { setSeverity(s); setPage(1); }}
                                className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${severity === s
                                    ? 'bg-brand-600/20 text-brand-400 border-brand-500/40'
                                    : 'text-gray-500 border-surface-border hover:text-gray-300 hover:border-gray-600'
                                    }`}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Table */}
                <div className="card overflow-hidden p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-xs text-gray-500 uppercase tracking-wider bg-surface-dark">
                                    <th className="px-6 py-3 text-left">CVE ID</th>
                                    <th className="px-6 py-3 text-left">Description</th>
                                    <th className="px-6 py-3 text-left">Vendor</th>
                                    <th className="px-6 py-3 text-center">CVSS</th>
                                    <th className="px-6 py-3 text-center">EPSS</th>
                                    <th className="px-6 py-3 text-center">Severity</th>
                                    <th className="px-6 py-3 text-center">Flags</th>
                                    <th className="px-6 py-3 text-center">Published</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan={8} className="text-center py-12 text-gray-500">Loading vulnerabilities...</td></tr>
                                ) : cves.length === 0 ? (
                                    <tr><td colSpan={8} className="text-center py-12 text-gray-500">No CVEs found</td></tr>
                                ) : (
                                    cves.map((cve) => (
                                        <tr key={cve.cve_id} className="border-t border-surface-border/50 hover:bg-surface-hover/30 transition-colors cursor-pointer">
                                            <td className="px-6 py-4 font-mono text-brand-400 font-medium whitespace-nowrap">{cve.cve_id}</td>
                                            <td className="px-6 py-4 text-gray-300 max-w-md truncate">{cve.description}</td>
                                            <td className="px-6 py-4 text-gray-400 whitespace-nowrap">{cve.vendor || '—'}</td>
                                            <td className="px-6 py-4 text-center">
                                                <span className={`font-mono font-bold ${cve.cvss_v3_score >= 9 ? 'text-red-400' : cve.cvss_v3_score >= 7 ? 'text-orange-400' : cve.cvss_v3_score >= 4 ? 'text-amber-400' : 'text-green-400'}`}>
                                                    {cve.cvss_v3_score?.toFixed(1) || '—'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-center font-mono text-gray-300">{cve.epss_score ? `${(cve.epss_score * 100).toFixed(1)}%` : '—'}</td>
                                            <td className="px-6 py-4 text-center">
                                                <span className={`badge ${getBadge(cve.cvss_v3_severity)}`}>{cve.cvss_v3_severity || '—'}</span>
                                            </td>
                                            <td className="px-6 py-4 text-center whitespace-nowrap">
                                                <div className="flex items-center justify-center gap-1.5">
                                                    {cve.is_kev && <span className="badge badge-critical">KEV</span>}
                                                    {cve.has_public_exploit && <span className="badge badge-high">EXPLOIT</span>}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-center text-gray-500 whitespace-nowrap text-xs">
                                                {cve.published_date ? new Date(cve.published_date).toLocaleDateString() : '—'}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between px-6 py-3 bg-surface-dark border-t border-surface-border">
                        <p className="text-xs text-gray-500">{total} total CVEs</p>
                        <div className="flex items-center gap-2">
                            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                                className="px-3 py-1 text-xs bg-surface-card border border-surface-border rounded text-gray-400 hover:text-white disabled:opacity-30">Prev</button>
                            <span className="text-xs text-gray-400">Page {page}</span>
                            <button onClick={() => setPage(p => p + 1)} disabled={cves.length < 25}
                                className="px-3 py-1 text-xs bg-surface-card border border-surface-border rounded text-gray-400 hover:text-white disabled:opacity-30">Next</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
