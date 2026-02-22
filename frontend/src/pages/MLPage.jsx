import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Brain, RefreshCw, TrendingUp, Target, Cpu } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const RiskBar = ({ probability }) => {
    const pct = probability * 100;
    const color = pct >= 80 ? '#ff4444' : pct >= 60 ? '#ff8844' : pct >= 40 ? '#ffbb33' : '#00ff88';
    return (
        <div className="flex items-center gap-3">
            <div className="flex-1 h-2 bg-surface-dark rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }}></div>
            </div>
            <span className="text-sm font-mono font-bold" style={{ color }}>{pct.toFixed(1)}%</span>
        </div>
    );
};

export default function MLPage() {
    const [predictions, setPredictions] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.get('/ml/predictions/top').catch(() => ({ data: [] })),
            api.get('/ml/model/metrics').catch(() => ({ data: {} })),
        ]).then(([predRes, metRes]) => {

            setPredictions(predRes.data || []);
            setMetrics(metRes.data || {});
        }).finally(() => setLoading(false));
    }, []);

    const featureData = metrics?.feature_importance
        ? Object.entries(metrics.feature_importance).slice(0, 10).map(([name, value]) => ({
            name: name.replace(/_/g, ' '), importance: +(value * 100).toFixed(1),
        })).sort((a, b) => b.importance - a.importance)
        : [];

    return (
        <div>
            <Header title="ML Exploit Prediction" subtitle="XGBoost-powered vulnerability intelligence" />
            <div className="p-6 space-y-6">

                {/* Model Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {[
                        { label: 'ROC-AUC', value: metrics?.roc_auc?.toFixed(4), color: 'text-brand-400' },
                        { label: 'Precision', value: metrics?.precision?.toFixed(4), color: 'text-green-400' },
                        { label: 'Recall', value: metrics?.recall?.toFixed(4), color: 'text-amber-400' },
                        { label: 'F1 Score', value: metrics?.f1?.toFixed(4), color: 'text-cyan-400' },
                        { label: 'Model', value: metrics?.model_type?.toUpperCase(), color: 'text-purple-400' },
                    ].map(m => (
                        <div key={m.label} className="card text-center">
                            <p className="text-xs text-gray-500 uppercase tracking-wider">{m.label}</p>
                            <p className={`text-xl font-bold mt-1 font-mono ${m.color}`}>{m.value || '—'}</p>
                        </div>
                    ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Feature Importance */}
                    <div className="card">
                        <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-brand-400" /> Feature Importance
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={featureData} layout="vertical" margin={{ left: 100 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis type="number" stroke="#4b5563" tick={{ fontSize: 11 }} />
                                <YAxis type="category" dataKey="name" stroke="#4b5563" tick={{ fontSize: 11 }} width={100} />
                                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e293b', borderRadius: '8px', fontSize: '12px' }} />
                                <Bar dataKey="importance" fill="#6366f1" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Top Predictions */}
                    <div className="card">
                        <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
                            <Target className="w-4 h-4 text-red-400" /> Top Exploit Predictions
                        </h3>
                        <div className="space-y-3">
                            {predictions.slice(0, 6).map(p => (
                                <div key={p.cve_id} className="p-3 bg-surface-dark rounded-lg border border-surface-border hover:border-brand-500/30 transition-colors">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-mono text-sm text-brand-400 font-medium">{p.cve_id}</span>
                                        <span className={`badge ${p.risk_level === 'CRITICAL' ? 'badge-critical' : p.risk_level === 'HIGH' ? 'badge-high' : 'badge-medium'}`}>{p.risk_level}</span>
                                    </div>
                                    <RiskBar probability={p.exploit_probability} />
                                    <div className="mt-2 flex flex-wrap gap-1">
                                        {(p.key_factors || []).slice(0, 2).map((f, i) => (
                                            <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-surface-hover text-gray-400">{f}</span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
