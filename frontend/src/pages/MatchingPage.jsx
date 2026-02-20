import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { GitBranch, Play, RefreshCw } from 'lucide-react';

export default function MatchingPage() {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [triggering, setTriggering] = useState(false);

    useEffect(() => {
        api.get('/matching/results').then(r => setMatches(r.data.items || r.data || []))
            .catch(() => setMatches([]))
            .finally(() => setLoading(false));
    }, []);

    const triggerMatching = () => {
        setTriggering(true);
        api.post('/matching/trigger').catch(() => { }).finally(() => setTimeout(() => setTriggering(false), 2000));
    };

    const display = matches;

    return (
        <div>
            <Header title="Vulnerability Matching" subtitle={`${display.length} matches found`} />
            <div className="p-6 space-y-4">
                <div className="flex justify-end">
                    <button onClick={triggerMatching} disabled={triggering}
                        className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-500 disabled:opacity-50 transition-all">
                        <RefreshCw className={`w-4 h-4 ${triggering ? 'animate-spin' : ''}`} />
                        {triggering ? 'Running...' : 'Run Matching'}
                    </button>
                </div>

                <div className="card overflow-hidden p-0">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-xs text-gray-500 uppercase tracking-wider bg-surface-dark">
                                <th className="px-6 py-3 text-left">Asset</th>
                                <th className="px-6 py-3 text-left">CVE</th>
                                <th className="px-6 py-3 text-left">Software</th>
                                <th className="px-6 py-3 text-center">Confidence</th>
                                <th className="px-6 py-3 text-center">Status</th>
                                <th className="px-6 py-3 text-center">Matched</th>
                            </tr>
                        </thead>
                        <tbody>
                            {display.map(m => (
                                <tr key={m.id} className="border-t border-surface-border/50 hover:bg-surface-hover/30">
                                    <td className="px-6 py-3 text-gray-300 font-medium">{m.asset_hostname || `Asset #${m.asset_id}`}</td>
                                    <td className="px-6 py-3 font-mono text-brand-400">{m.cve_id}</td>
                                    <td className="px-6 py-3 text-gray-400">{m.software_name}</td>
                                    <td className="px-6 py-3 text-center">
                                        <div className="flex items-center justify-center gap-2">
                                            <div className="w-12 h-1.5 bg-surface-dark rounded-full overflow-hidden">
                                                <div className="h-full rounded-full bg-brand-500" style={{ width: `${(m.match_confidence || 0) * 100}%` }}></div>
                                            </div>
                                            <span className="text-xs font-mono text-gray-400">{((m.match_confidence || 0) * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-3 text-center">
                                        <span className={`badge ${m.status === 'open' ? 'badge-high' : m.status === 'remediated' ? 'badge-low' : 'badge-info'}`}>{m.status}</span>
                                    </td>
                                    <td className="px-6 py-3 text-center text-gray-500 text-xs">{m.matched_at ? new Date(m.matched_at).toLocaleString() : '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
