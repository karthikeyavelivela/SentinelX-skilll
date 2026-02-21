import React from 'react';
import Navbar from '../components/Navbar';
import { ShieldAlert, Activity, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 selection:bg-blue-500/30 flex flex-col relative">
            {/* Video Background fixed for entire page */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="object-cover w-full h-full opacity-40 mix-blend-screen"
                >
                    <source src="https://res.cloudinary.com/dzxuomajo/video/upload/v1771603012/142363-780562112_medium_mavpk6.mp4" type="video/mp4" />
                </video>
                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-b from-slate-950/20 via-slate-950/60 to-slate-950 z-0"></div>
            </div>

            <Navbar />

            {/* Hero Section */}
            <main className="relative flex flex-col items-center justify-center px-4 mt-32 flex-1 z-10 w-full mb-24">
                <div className="relative z-10 text-center max-w-4xl mx-auto py-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 text-sm font-medium text-blue-400 rounded-full bg-blue-500/10 border border-blue-500/20">
                        <span className="relative flex w-2 h-2">
                            <span className="absolute inline-flex w-full h-full bg-blue-400 rounded-full opacity-75 animate-ping"></span>
                            <span className="relative inline-flex w-2 h-2 bg-blue-500 rounded-full"></span>
                        </span>
                        System Online
                    </div>

                    <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight mb-8 drop-shadow-lg">
                        Secure Your Infrastructure with <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
                            SentinelX
                        </span>
                    </h1>

                    <p className="text-xl text-slate-200 mb-10 max-w-2xl mx-auto leading-relaxed drop-shadow-md">
                        Enterprise Exploit-Aware Vulnerability Intelligence Platform.
                        Detect, analyze, and remediate CVEs using cutting-edge graph analytics and machine learning.
                    </p>

                    <div className="flex items-center justify-center gap-6">
                        <Link to="/login" className="px-8 py-4 text-lg font-semibold text-white transition-all bg-blue-600 rounded-xl hover:bg-blue-500 hover:shadow-lg hover:shadow-blue-500/25 hover:-translate-y-0.5">
                            Get Started Now
                        </Link>
                        <Link to="/about" className="px-8 py-4 text-lg font-semibold transition-all border border-slate-700 rounded-xl hover:bg-slate-800 text-slate-300 hover:text-white backdrop-blur-md bg-slate-900/40">
                            Learn More
                        </Link>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 relative z-10 max-w-6xl mx-auto w-full px-4">
                    <div className="p-6 bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl hover:border-blue-500/50 transition-colors">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6 border border-blue-500/20">
                            <Activity className="w-6 h-6 text-blue-400" />
                        </div>
                        <h3 className="text-xl font-bold mb-3">Real-time Analysis</h3>
                        <p className="text-slate-400 leading-relaxed">Continuous monitoring and ingestion of NVD and CISA KEV data feeds with predictive scoring.</p>
                    </div>
                    <div className="p-6 bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl hover:border-purple-500/50 transition-colors">
                        <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6 border border-purple-500/20">
                            <ShieldAlert className="w-6 h-6 text-purple-400" />
                        </div>
                        <h3 className="text-xl font-bold mb-3">Graph Intelligence</h3>
                        <p className="text-slate-400 leading-relaxed">Map attack paths and visualize vulnerability chains to prioritize remediation effectively.</p>
                    </div>
                    <div className="p-6 bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl hover:border-emerald-500/50 transition-colors">
                        <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6 border border-emerald-500/20">
                            <Lock className="w-6 h-6 text-emerald-400" />
                        </div>
                        <h3 className="text-xl font-bold mb-3">Automated Remediation</h3>
                        <p className="text-slate-400 leading-relaxed">Deploy patch jobs instantly with integrated Ansible playbooks for your vulnerable assets.</p>
                    </div>
                </div>
            </main>
        </div>
    );
}
