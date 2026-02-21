// src/components/Footer.jsx
import React from 'react';
import { Shield, Github, Twitter, Linkedin, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
    return (
        <footer className="bg-slate-950 border-t border-slate-800 pt-16 pb-8 relative z-10 w-full overflow-hidden">
            {/* Background glow for footer */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-blue-600/5 rounded-[100%] blur-3xl pointer-events-none"></div>

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    {/* Brand */}
                    <div className="col-span-1 md:col-span-1">
                        <Link to="/" className="flex items-center gap-3 group mb-6">
                            <span className="text-2xl font-black tracking-tight text-white drop-shadow-md">
                                SENTINEL<span className="text-blue-500">X</span>
                            </span>
                        </Link>
                        <p className="text-slate-400 text-sm leading-relaxed mb-6">
                            Enterprise Exploit-Aware Vulnerability Intelligence Platform. Advanced detection and remediation backed by graph intelligence.
                        </p>
                        <div className="flex gap-4">
                            <a href="#" className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-blue-400 hover:border-blue-500/50 transition-colors">
                                <Twitter className="w-4 h-4" />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-blue-400 hover:border-blue-500/50 transition-colors">
                                <Github className="w-4 h-4" />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-blue-400 hover:border-blue-500/50 transition-colors">
                                <Linkedin className="w-4 h-4" />
                            </a>
                        </div>
                    </div>

                    {/* Links */}
                    <div>
                        <h4 className="text-white font-bold mb-6 tracking-wider uppercase text-sm">Platform</h4>
                        <ul className="space-y-3">
                            <li><Link to="/about" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">How it Works</Link></li>
                            <li><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Threat Intelligence</a></li>
                            <li><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Integrations</a></li>
                            <li><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Enterprise APi</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold mb-6 tracking-wider uppercase text-sm">Company</h4>
                        <ul className="space-y-3">
                            <li><Link to="/about" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">About Us</Link></li>
                            <li><Link to="/team" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Our Team</Link></li>
                            <li><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Careers</a></li>
                            <li><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">Contact</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold mb-6 tracking-wider uppercase text-sm">Subscribe</h4>
                        <p className="text-slate-400 text-sm mb-4">Get the latest vulnerability intelligence updates.</p>
                        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800 focus-within:border-blue-500/50 transition-colors">
                            <div className="pl-3 flex items-center justify-center text-slate-500">
                                <Mail className="w-4 h-4" />
                            </div>
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="w-full bg-transparent border-none text-sm text-white px-3 py-2 outline-none focus:ring-0 placeholder-slate-600"
                            />
                            <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors">
                                Join
                            </button>
                        </div>
                    </div>
                </div>

                <div className="pt-8 border-t border-slate-900 flex flex-col md:flex-row items-center justify-between">
                    <p className="text-slate-500 text-sm mb-4 md:mb-0">
                        &copy; {new Date().getFullYear()} SentinelX Intelligence. All rights reserved.
                    </p>
                    <div className="flex gap-6">
                        <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Privacy Policy</a>
                        <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Terms of Service</a>
                        <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Security</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
