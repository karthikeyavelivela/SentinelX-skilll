import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard, Shield, Server, GitBranch, Brain, Activity,
    Wrench, LogOut, ChevronLeft, ChevronRight, Zap
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/cves', label: 'Vulnerabilities', icon: Shield },
    { path: '/assets', label: 'Assets', icon: Server },
    { path: '/matching', label: 'Matching', icon: GitBranch },
    { path: '/ml', label: 'Exploit Intel', icon: Brain },
    { path: '/graph', label: 'Attack Paths', icon: Activity },
    { path: '/risk', label: 'Risk Analysis', icon: Zap },
    { path: '/remediation', label: 'Remediation', icon: Wrench },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const { user, logout } = useAuth();
    const location = useLocation();

    return (
        <aside className={`fixed left-0 top-0 h-screen bg-slate-800 border-r border-slate-700 z-50 transition-all duration-300 flex flex-col ${collapsed ? 'w-[70px]' : 'w-[240px]'}`}>
            {/* Logo */}
            <div className="h-16 flex items-center px-4 border-b border-slate-700">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    {!collapsed && (
                        <div>
                            <h1 className="text-sm font-bold text-slate-100 tracking-wide">SENTINELX</h1>
                            <p className="text-[10px] text-blue-400 font-mono tracking-widest">SECURITY</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
                {navItems.map(({ path, label, icon: Icon }) => {
                    const isActive = location.pathname === path ||
                        (path !== '/' && location.pathname.startsWith(path));
                    return (
                        <NavLink
                            key={path}
                            to={path}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group
                ${isActive
                                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/30'
                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 border border-transparent'
                                }`}
                        >
                            <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                            {!collapsed && <span>{label}</span>}
                        </NavLink>
                    );
                })}
            </nav>

            {/* User / Collapse */}
            <div className="border-t border-slate-700 p-3">
                {!collapsed && user && (
                    <div className="flex items-center gap-3 mb-3 px-2">
                        <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-sm font-bold text-slate-200">
                            {user.username?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-200 truncate">{user.username}</p>
                            <p className="text-xs text-slate-500 uppercase">{user.role}</p>
                        </div>
                    </div>
                )}
                <div className="flex items-center gap-2">
                    <button
                        onClick={logout}
                        className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    >
                        <LogOut className="w-4 h-4" />
                        {!collapsed && 'Logout'}
                    </button>
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-700 transition-colors"
                    >
                        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                    </button>
                </div>
            </div>
        </aside>
    );
}
