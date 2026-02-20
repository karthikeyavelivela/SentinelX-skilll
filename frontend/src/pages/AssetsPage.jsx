import { useState, useEffect } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import { Server, Plus, Wifi, WifiOff, Monitor, Clock, HardDrive } from 'lucide-react';

const CriticalityBadge = ({ level }) => {
    const cls = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' }[level] || 'badge-info';
    return <span className={`badge ${cls}`}>{level}</span>;
};

const RiskGauge = ({ score }) => {
    const color = score >= 80 ? '#ff4444' : score >= 60 ? '#ff8844' : score >= 40 ? '#ffbb33' : '#00ff88';
    return (
        <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 bg-surface-dark rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-500" style={{ width: `${score}%`, backgroundColor: color }}></div>
            </div>
            <span className="text-xs font-mono" style={{ color }}>{score}</span>
        </div>
    );
};

export default function AssetsPage() {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/assets').then(res => setAssets(res.data.items || res.data || []))
            .catch(() => setAssets([]))
            .finally(() => setLoading(false));
    }, []);

    const displayAssets = assets;

    return (
        <div>
            <Header title="Asset Inventory" subtitle={`${displayAssets.length} assets monitored`} />
            <div className="p-6 space-y-4">

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-white">{displayAssets.length}</p>
                        <p className="text-xs text-gray-500 mt-1">Total Assets</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-green-400">{displayAssets.filter(a => a.agent_status === 'online').length}</p>
                        <p className="text-xs text-gray-500 mt-1">Online</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-red-400">{displayAssets.filter(a => a.criticality === 'critical').length}</p>
                        <p className="text-xs text-gray-500 mt-1">Critical</p>
                    </div>
                    <div className="card text-center">
                        <p className="text-2xl font-bold text-amber-400">{displayAssets.filter(a => a.is_internet_facing).length}</p>
                        <p className="text-xs text-gray-500 mt-1">Internet Facing</p>
                    </div>
                </div>

                {/* Asset Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {displayAssets.map(asset => (
                        <div key={asset.id} className="card hover:border-brand-500/40 cursor-pointer group">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${asset.os_platform === 'windows' ? 'bg-blue-500/15' : asset.os_platform === 'darwin' ? 'bg-gray-500/15' : 'bg-orange-500/15'
                                        }`}>
                                        <Monitor className={`w-5 h-5 ${asset.os_platform === 'windows' ? 'text-blue-400' : asset.os_platform === 'darwin' ? 'text-gray-400' : 'text-orange-400'
                                            }`} />
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors">{asset.hostname}</h3>
                                        <p className="text-xs text-gray-500 font-mono">{asset.ip_address}</p>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1.5 ${asset.agent_status === 'online' ? 'text-green-400' : asset.agent_status === 'stale' ? 'text-amber-400' : 'text-red-400'}`}>
                                    <div className={`pulse-dot ${asset.agent_status === 'online' ? 'bg-green-400' : asset.agent_status === 'stale' ? 'bg-amber-400' : 'bg-red-400'}`}></div>
                                    <span className="text-[10px] uppercase tracking-wider font-medium">{asset.agent_status}</span>
                                </div>
                            </div>

                            <div className="space-y-2 text-xs text-gray-400">
                                <div className="flex justify-between"><span>OS</span><span className="text-gray-300">{asset.os_name}</span></div>
                                <div className="flex justify-between"><span>Zone</span><span className="text-gray-300 uppercase">{asset.network_zone}</span></div>
                                <div className="flex justify-between"><span>Unit</span><span className="text-gray-300 capitalize">{asset.business_unit}</span></div>
                                <div className="flex justify-between items-center"><span>Criticality</span><CriticalityBadge level={asset.criticality} /></div>
                                <div className="flex justify-between items-center"><span>Risk Score</span><RiskGauge score={asset.risk_score || 0} /></div>
                                <div className="flex justify-between"><span>Packages</span><span className="text-gray-300">{asset.software_count}</span></div>
                            </div>

                            {asset.is_internet_facing && (
                                <div className="mt-3 px-2 py-1 bg-amber-500/10 border border-amber-500/20 rounded-md text-[10px] text-amber-400 font-medium text-center uppercase tracking-wider">
                                    ⚠ Internet Facing
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
