import { Bell, Search, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header({ title, subtitle }) {
    const { user } = useAuth();

    return (
        <header className="h-16 border-b border-slate-700 flex items-center justify-between px-6 bg-slate-800/80 backdrop-blur-sm sticky top-0 z-40">
            <div>
                <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
                {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
            </div>

            <div className="flex items-center gap-4">
                {/* Search */}
                <div className="relative hidden md:block">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search SentinelX..."
                        className="w-64 pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                </div>

                {/* Notifications */}
                <button className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 pulse-dot"></span>
                </button>

                {/* Settings */}
                <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
                    <Settings className="w-5 h-5" />
                </button>
            </div>
        </header>
    );
}
