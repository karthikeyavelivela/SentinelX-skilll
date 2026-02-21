import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Terminal, Database, Shield, Zap } from 'lucide-react';

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 py-24 relative mt-16 flex-1">
                {/* Background glow */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

                <h1 className="text-5xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                    About SentinelX
                </h1>

                <div className="prose prose-invert max-w-4xl text-lg text-slate-300 space-y-8">
                    <p className="leading-relaxed">
                        SentinelX is a cutting-edge Vulnerability Intelligence Platform designed for enterprise environments.
                        It integrates live data streams from NVD, CISA KEV, and Exploit-DB to provide real-time, actionable insights.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-16">
                        <div className="bg-slate-900/60 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
                            <Terminal className="w-8 h-8 text-blue-400 mb-4" />
                            <h3 className="text-xl font-bold text-white mb-2">Automated Ingestion</h3>
                            <p className="text-sm text-slate-400">Agent-based system scanning processes CVEs and matches vulnerabilities natively without manual intervention.</p>
                        </div>
                        <div className="bg-slate-900/60 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
                            <Database className="w-8 h-8 text-indigo-400 mb-4" />
                            <h3 className="text-xl font-bold text-white mb-2">Entity Resolution</h3>
                            <p className="text-sm text-slate-400">Uses ML indexing to match software CPEs to known enterprise assets reliably.</p>
                        </div>
                        <div className="bg-slate-900/60 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
                            <Zap className="w-8 h-8 text-purple-400 mb-4" />
                            <h3 className="text-xl font-bold text-white mb-2">EPSS Scoring</h3>
                            <p className="text-sm text-slate-400">Predictive exploit probabilities based on live EPSS feeds for smart risk prioritization.</p>
                        </div>
                        <div className="bg-slate-900/60 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
                            <Shield className="w-8 h-8 text-emerald-400 mb-4" />
                            <h3 className="text-xl font-bold text-white mb-2">Active Defense</h3>
                            <p className="text-sm text-slate-400">Integrated patch management loops that schedule and orchestrate fixes instantly.</p>
                        </div>
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}
