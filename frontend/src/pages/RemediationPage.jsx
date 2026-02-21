import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Wrench, CheckCircle, XCircle, Clock, Play, RotateCcw, AlertTriangle, Shield } from 'lucide-react';

const STATUS_CONFIG = {
    pending_approval: { icon: Clock, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30', label: 'Pending' },
    approved: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30', label: 'Approved' },
    scheduled: { icon: Clock, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30', label: 'Scheduled' },
    in_progress: { icon: Play, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', label: 'Running' },
    dry_run_complete: { icon: Shield, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30', label: 'Dry Run Done' },
    completed: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30', label: 'Complete' },
    failed: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30', label: 'Failed' },
    rolled_back: { icon: RotateCcw, color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/30', label: 'Rolled Back' },
    cancelled: { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/30', label: 'Cancelled' },
};

export default function RemediationPage() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({});
    const [filter, setFilter] = useState('all');

    const fetchData = () => {
        api.get('/remediation/jobs').then(r => setJobs(r.data)).catch(() => setJobs([]));
        api.get('/remediation/stats').then(r => setStats(r.data)).catch(() => setStats({}));
    };

    useEffect(() => {
        fetchData();
        setLoading(false);
        const interval = setInterval(fetchData, 5000); // Poll every 5s for live updates
        return () => clearInterval(interval);
    }, []);

    const handleAction = (e, id, action, body = {}) => {
        e.stopPropagation();
        api.post(`/remediation/jobs/${id}/${action}`, body)
            .then(() => fetchData())
            .catch(console.error);
    };

    const display = (jobs).filter(j => filter === 'all' || j.status === filter);

    return (
        <div>
            <Header title="Automated Remediation" subtitle="Patch management & deployment" />
            <div className="p-6 space-y-6">

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-white">{stats.total_jobs || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Total Jobs</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-amber-400">{stats.pending_approval || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Pending Approval</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-green-400">{stats.completed || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Completed</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-red-400">{stats.failed || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Failed</p>
                    </div>
                </div>

                {/* Filter */}
                <div className="flex gap-2 flex-wrap">
                    {['all', 'pending_approval', 'approved', 'scheduled', 'in_progress', 'completed', 'failed'].map(f => (
                        <button key={f} onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all capitalize ${filter === f ? 'bg-brand-600/20 text-brand-400 border-brand-500/40' : 'text-gray-500 border-surface-border hover:text-gray-300'
                                }`}>
                            {f.replace(/_/g, ' ')}
                        </button>
                    ))}
                </div>

                {/* Pipeline */}
                <div className="space-y-3">
                    {display.length === 0 && !loading && (
                        <div className="text-center py-12 text-gray-500 card">
                            No remediation jobs found for this filter.
                        </div>
                    )}
                    {display.map(job => {
                        const sc = STATUS_CONFIG[job.status] || STATUS_CONFIG.pending_approval;
                        const Icon = sc.icon;
                        return (
                            <div key={job.id} className={`card flex items-center justify-between p-4 cursor-pointer hover:border-blue-500/40 ${sc.bg} border ${sc.border} rounded-xl transition-all`}>
                                <div className="flex items-center gap-4">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${sc.bg}`}>
                                        <Icon className={`w-6 h-6 ${sc.color} ${job.status === 'in_progress' ? 'animate-pulse' : ''}`} />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-sm font-semibold text-white">{job.asset_hostname || `Asset #${job.asset_id}`}</span>
                                            <span className="font-mono text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full">{job.cve_id}</span>
                                            {job.is_dry_run && <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded border border-purple-500/30">DRY RUN</span>}
                                        </div>
                                        <div className="flex items-center gap-3 text-xs text-slate-400">
                                            <span>📦 {job.package_name}</span>
                                            <span>⏰ {new Date(job.created_at).toLocaleString()}</span>
                                            {job.scheduled_at && <span>📅 Scheduled: {new Date(job.scheduled_at).toLocaleString()}</span>}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${job.risk_level === 'critical' ? 'bg-rose-500/20 text-rose-400' : job.risk_level === 'high' ? 'bg-orange-500/20 text-orange-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                        {(job.risk_level || 'UNKNOWN').toUpperCase()}
                                    </span>

                                    <div className={`px-3 py-1 rounded-lg text-xs font-medium ${sc.bg} ${sc.color} border ${sc.border}`}>
                                        {sc.label}
                                    </div>

                                    {/* Quick actions */}
                                    <div className="flex gap-1 ml-4 border-l border-slate-700 pl-4">
                                        {job.status === 'pending_approval' && (
                                            <button onClick={(e) => handleAction(e, job.id, 'approve', { approved: true })}
                                                className="p-2 rounded-lg hover:bg-green-500/20 text-emerald-400 transition-colors" title="Approve">
                                                <CheckCircle className="w-5 h-5" />
                                            </button>
                                        )}
                                        {(job.status === 'approved' || job.status === 'scheduled') && (
                                            <button onClick={(e) => handleAction(e, job.id, 'execute')}
                                                className="p-2 rounded-lg hover:bg-blue-500/20 text-blue-400 transition-colors" title="Execute">
                                                <Play className="w-5 h-5" />
                                            </button>
                                        )}
                                        {job.status === 'completed' && (
                                            <button onClick={(e) => handleAction(e, job.id, 'rollback')}
                                                className="p-2 rounded-lg hover:bg-orange-500/20 text-orange-400 transition-colors" title="Rollback">
                                                <RotateCcw className="w-5 h-5" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
