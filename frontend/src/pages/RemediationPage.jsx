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

    useEffect(() => {
        api.get('/remediation/jobs').then(r => setJobs(r.data)).catch(() => setJobs([])).finally(() => setLoading(false));
        api.get('/remediation/stats').then(r => setStats(r.data)).catch(() => setStats({}));
    }, []);

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
                    {display.map(job => {
                        const sc = STATUS_CONFIG[job.status] || STATUS_CONFIG.pending_approval;
                        const Icon = sc.icon;
                        return (
                            <div key={job.id} className={`card flex items-center gap-4 cursor-pointer hover:border-brand-500/40 ${sc.bg} border ${sc.border}`}>
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${sc.bg}`}>
                                    <Icon className={`w-6 h-6 ${sc.color}`} />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-sm font-semibold text-white">{job.asset_hostname || `Asset #${job.asset_id}`}</span>
                                        <span className="font-mono text-xs text-brand-400">{job.cve_id}</span>
                                        {job.is_dry_run && <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded border border-purple-500/30">DRY RUN</span>}
                                    </div>
                                    <div className="flex items-center gap-3 text-xs text-gray-500">
                                        <span>📦 {job.package_name}</span>
                                        <span>⏰ {new Date(job.created_at).toLocaleString()}</span>
                                        {job.scheduled_at && <span>📅 Scheduled: {new Date(job.scheduled_at).toLocaleString()}</span>}
                                    </div>
                                </div>

                                <span className={`badge ${job.risk_level === 'critical' ? 'badge-critical' : job.risk_level === 'high' ? 'badge-high' : 'badge-medium'}`}>
                                    {job.risk_level}
                                </span>

                                <div className={`px-3 py-1 rounded-lg text-xs font-medium ${sc.bg} ${sc.color} border ${sc.border}`}>
                                    {sc.label}
                                </div>

                                {/* Quick actions */}
                                <div className="flex gap-1">
                                    {job.status === 'pending_approval' && (
                                        <button onClick={() => api.post(`/remediation/jobs/${job.id}/approve`, { approved: true }).catch(() => { })}
                                            className="p-2 rounded-lg hover:bg-green-500/20 text-green-400 transition-colors" title="Approve">
                                            <CheckCircle className="w-4 h-4" />
                                        </button>
                                    )}
                                    {(job.status === 'approved' || job.status === 'scheduled') && (
                                        <button onClick={() => api.post(`/remediation/jobs/${job.id}/execute`).catch(() => { })}
                                            className="p-2 rounded-lg hover:bg-blue-500/20 text-blue-400 transition-colors" title="Execute">
                                            <Play className="w-4 h-4" />
                                        </button>
                                    )}
                                    {job.status === 'completed' && (
                                        <button onClick={() => api.post(`/remediation/jobs/${job.id}/rollback`).catch(() => { })}
                                            className="p-2 rounded-lg hover:bg-orange-500/20 text-orange-400 transition-colors" title="Rollback">
                                            <RotateCcw className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
