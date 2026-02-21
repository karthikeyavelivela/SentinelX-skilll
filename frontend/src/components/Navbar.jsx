// src/components/Navbar.jsx
import { Link, useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Navbar() {
    const location = useLocation();

    // Transparent on landing/about/team, solid on other pages
    const isPublicPage = ['/', '/about', '/team'].includes(location.pathname);

    return (
        <nav className={`flex items-center justify-between px-8 py-4 transition-all duration-300 z-50 ${isPublicPage ? 'fixed w-full top-0 bg-transparent backdrop-blur-sm border-b border-white/10' : 'sticky top-0 bg-slate-900 border-b border-slate-800'}`}>
            <Link to="/" className="flex items-center gap-3 group">
                <span className="text-2xl font-black tracking-tight text-white drop-shadow-md">
                    SENTINEL<span className="text-blue-500">X</span>
                </span>
            </Link>
            <div className="flex items-center gap-8">
                <Link to="/" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors uppercase tracking-wider">Home</Link>
                <Link to="/about" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors uppercase tracking-wider">About</Link>
                <Link to="/team" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors uppercase tracking-wider">Team</Link>
                <Link to="/login" className="px-6 py-2.5 text-sm font-bold text-white transition-all bg-blue-600 rounded-full hover:bg-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.5)] hover:shadow-[0_0_25px_rgba(37,99,235,0.7)] hover:-translate-y-0.5 uppercase tracking-wider">
                    Sign In
                </Link>
            </div>
        </nav>
    );
}
