import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Github, Linkedin, Twitter } from 'lucide-react';

const team = [
    { name: 'Karthikeya Velivea', role: 'Lead Architect', color: 'bg-[#FF6B6B]' },
    { name: 'Ramya Sri Kodali', role: 'Security Analyst', color: 'bg-[#4ECDC4]' },
    { name: 'Chevuru Jhanavi', role: 'Backend Engineer', color: 'bg-[#FFE66D]' },
    { name: 'Sura Vinay', role: 'Frontend Developer', color: 'bg-[#A8E6CF]' }
];

export default function TeamPage() {
    return (
        <div className="min-h-screen bg-[#F7F7F7] text-slate-900 font-mono flex flex-col">
            <div className="bg-black text-white rounded-b-3xl relative z-20 shadow-[0_10px_0px_0px_rgba(0,0,0,1)]">
                <Navbar />
            </div>

            <div className="max-w-6xl mx-auto px-4 py-32 flex-1 relative z-10 pt-48">
                <div className="mb-16 border-4 border-black p-8 bg-yellow-300 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1 hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] transition-transform">
                    <h1 className="text-6xl font-black uppercase tracking-tighter mb-4">The Squad</h1>
                    <p className="text-xl font-bold">The masterminds behind SentinelX.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    {team.map((member, idx) => (
                        <div
                            key={idx}
                            className={`border-4 border-black p-8 ${member.color} shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:-translate-y-1 hover:shadow-[16px_16px_0px_0px_rgba(0,0,0,1)] transition-all duration-200`}
                        >
                            <div className="flex items-center justify-between mb-8">
                                <h3 className="text-4xl font-black uppercase tracking-tight">{member.name}</h3>
                                <div className="w-16 h-16 rounded-full border-4 border-black bg-white flex items-center justify-center overflow-hidden">
                                    <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${member.name}`} alt={member.name} className="w-full h-full object-cover" />
                                </div>
                            </div>

                            <p className="text-2xl font-bold mb-8 border-b-4 border-black pb-4 inline-block">{member.role}</p>

                            <div className="flex gap-4">
                                <button className="p-3 border-4 border-black bg-white hover:bg-black hover:text-white transition-colors cursor-pointer text-black">
                                    <Github className="w-6 h-6" />
                                </button>
                                <button className="p-3 border-4 border-black bg-white hover:bg-black hover:text-white transition-colors cursor-pointer text-black">
                                    <Linkedin className="w-6 h-6" />
                                </button>
                                <button className="p-3 border-4 border-black bg-white hover:bg-black hover:text-white transition-colors cursor-pointer text-black">
                                    <Twitter className="w-6 h-6" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-auto border-t-8 border-black">
                <Footer />
            </div>
        </div>
    );
}
