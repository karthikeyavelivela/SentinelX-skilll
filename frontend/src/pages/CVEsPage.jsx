import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Search, Filter, ShieldAlert, ChevronLeft, ChevronRight, Activity } from 'lucide-react';

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

    const getBadgeClass = (sev) => {
        if (!sev) return 'bg-slate-100 text-slate-500 border-slate-200';
        const s = sev.toUpperCase();
        if (s.includes('CRITICAL')) return 'bg-rose-50 border-rose-200 text-rose-700';
        if (s.includes('HIGH')) return 'bg-orange-50 border-orange-200 text-orange-700';
        if (s.includes('MEDIUM')) return 'bg-amber-50 border-amber-200 text-amber-700';
        return 'bg-emerald-50 border-emerald-200 text-emerald-700';
    };

    return (
        <div className="min-h-screen bg-slate-50/50">
            <Header title="Vulnerability Intelligence" subtitle={`${total.toLocaleString()} CVEs tracked globally`} />

            <div className="p-6 max-w-[1600px] mx-auto space-y-6">

                {/* Controls Bar */}
                <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200/60 flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="relative w-full md:w-96">
                        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input
                            type="text" placeholder="Search by CVE ID, vendor, or keywords..."
                            value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
                        />
                    </div>

                    <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 hide-scrollbar">
                        <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
                            <Filter className="w-4 h-4 text-slate-400 ml-2" />
                            {SEVERITIES.map(s => (
                                <button
                                    key={s}
                                    onClick={() => { setSeverity(s); setPage(1); }}
                                    className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all ${severity === s
                                        ? 'bg-white text-blue-600 shadow-sm border border-slate-200/50'
                                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                                        }`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Data Table */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead>
                                <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-medium">
                                    <th className="px-6 py-4 rounded-tl-2xl">Vulnerability</th>
                                    <th className="px-6 py-4">Context</th>
                                    <th className="px-6 py-4">Scores</th>
                                    <th className="px-6 py-4 text-center">Threat Intel</th>
                                    <th className="px-6 py-4 text-right rounded-tr-2xl">Published</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-16 text-center">
                                            <div className="flex flex-col items-center justify-center text-slate-400">
                                                <Activity className="w-8 h-8 mb-3 animate-pulse text-blue-500" />
                                                <p>Fetching intelligence data...</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : cves.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-16 text-center text-slate-500">
                                            <ShieldAlert className="w-8 h-8 mx-auto mb-3 text-slate-300" />
                                            <p>No vulnerabilities found matching your criteria.</p>
                                        </td>
                                    </tr>
                                ) : (
                                    cves.map((cve) => (
                                        <tr key={cve.cve_id} className="hover:bg-slate-50/50 transition-colors group">
                                            {/* Vulnerability ID & Severity */}
                                            <td className="px-6 py-4">
                                                <div className="flex flex-col gap-1.5 align-start">
                                                    <span className="font-mono font-bold text-slate-700 group-hover:text-blue-600 transition-colors">
                                                        {cve.cve_id}
                                                    </span>
                                                    <span className={`w-fit px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getBadgeClass(cve.cvss_v3_severity)}`}>
                                                        {cve.cvss_v3_severity || 'UNKNOWN'}
                                                    </span>
                                                </div>
                                            </td>

                                            {/* Context */}
                                            <td className="px-6 py-4 max-w-md">
                                                <p className="text-slate-600 text-sm line-clamp-2 leading-relaxed">
                                                    {cve.description}
                                                </p>
                                                {cve.vendor && (
                                                    <div className="mt-2 flex items-center gap-2">
                                                        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Vendor</span>
                                                        <span className="text-xs text-slate-600 font-medium px-2 py-0.5 bg-slate-100 rounded-md">
                                                            {cve.vendor}
                                                        </span>
                                                    </div>
                                                )}
                                            </td>

                                            {/* Scores */}
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-4">
                                                    <div>
                                                        <p className="text-[10px] font-semibold text-slate-400 mb-0.5 uppercase">CVSS</p>
                                                        <p className={`font-mono font-bold ${cve.cvss_v3_score >= 9 ? 'text-rose-600' : cve.cvss_v3_score >= 7 ? 'text-orange-500' : 'text-slate-600'}`}>
                                                            {cve.cvss_v3_score?.toFixed(1) || '—'}
                                                        </p>
                                                    </div>
                                                    <div className="h-8 w-px bg-slate-200"></div>
                                                    <div>
                                                        <p className="text-[10px] font-semibold text-slate-400 mb-0.5 uppercase">EPSS</p>
                                                        <p className="font-mono font-medium text-slate-600">
                                                            {cve.epss_score ? `${(cve.epss_score * 100).toFixed(1)}%` : '—'}
                                                        </p>
                                                    </div>
                                                </div>
                                            </td>

                                            {/* Threat Intel Flags */}
                                            <td className="px-6 py-4 text-center">
                                                <div className="flex flex-wrap justify-center gap-1.5">
                                                    {cve.is_kev && (
                                                        <span className="px-2 py-1 bg-red-50 text-red-600 border border-red-200 rounded-md text-[10px] font-bold tracking-wide">
                                                            CISA KEV
                                                        </span>
                                                    )}
                                                    {cve.has_public_exploit && (
                                                        <span className="px-2 py-1 bg-purple-50 text-purple-600 border border-purple-200 rounded-md text-[10px] font-bold tracking-wide">
                                                            EXPLOIT
                                                        </span>
                                                    )}
                                                    {!cve.is_kev && !cve.has_public_exploit && (
                                                        <span className="text-slate-300 text-xs">—</span>
                                                    )}
                                                </div>
                                            </td>

                                            {/* Published */}
                                            <td className="px-6 py-4 text-right">
                                                <span className="text-xs text-slate-500 font-medium bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-100">
                                                    {cve.published_date ? new Date(cve.published_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : 'Unknown'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="px-6 py-4 bg-slate-50/50 border-t border-slate-200 flex items-center justify-between">
                        <p className="text-sm font-medium text-slate-500">
                            Showing <span className="text-slate-700">{Math.min((page - 1) * 25 + 1, total)}</span> to <span className="text-slate-700">{Math.min(page * 25, total)}</span> of <span className="text-slate-700">{total.toLocaleString()}</span> entries
                        </p>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                                className="p-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-blue-600 disabled:opacity-50 disabled:hover:bg-white disabled:hover:text-slate-600 transition-colors shadow-sm"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <span className="text-sm font-medium text-slate-600 px-2 w-20 text-center">Page {page}</span>
                            <button
                                onClick={() => setPage(p => p + 1)} disabled={cves.length < 25}
                                className="p-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-blue-600 disabled:opacity-50 disabled:hover:bg-white disabled:hover:text-slate-600 transition-colors shadow-sm"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
