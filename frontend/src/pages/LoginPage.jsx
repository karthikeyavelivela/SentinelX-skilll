import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, LogIn, ShieldCheck } from 'lucide-react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const { login, loading } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const result = await login(username, password);

        if (result.success) {
            navigate('/');
        } else {
            setError(result.error);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 relative selection:bg-blue-200">
            {/* Soft decorative shapes */}
            <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-br from-blue-600 to-indigo-700 slant-bg shadow-xl"></div>

            <div className="relative z-10 w-full max-w-[1000px] flex rounded-3xl overflow-hidden shadow-2xl bg-white mx-4 min-h-[600px]">

                {/* Left side: Information / Illustration */}
                <div className="hidden md:flex md:w-5/12 bg-slate-900 text-white flex-col justify-between p-12 relative overflow-hidden">
                    <div className="relative z-10">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center mb-6">
                            <ShieldCheck className="w-7 h-7" />
                        </div>
                        <h2 className="text-3xl font-bold mb-4 font-sans tracking-tight">SentinelX Security</h2>
                        <p className="text-slate-300 leading-relaxed text-sm">
                            Welcome back to your command center. Access real-time vulnerability intelligence, predictive analytics, and automated remediation pipelines in one place.
                        </p>
                    </div>

                    <div className="relative z-10 text-sm text-slate-400">
                        &copy; {new Date().getFullYear()} SentinelX Security Intel
                    </div>

                    {/* Decorative abstract elements */}
                    <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
                    <div className="absolute -top-32 -left-32 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
                </div>

                {/* Right side: Login Form */}
                <div className="w-full md:w-7/12 flex flex-col justify-center p-8 sm:p-16 bg-white">
                    <div className="max-w-md w-full mx-auto">
                        <h1 className="text-3xl font-bold text-slate-800 mb-2 font-sans tracking-tight">Sign in to your account</h1>
                        <p className="text-slate-500 mb-8 text-sm">Enter your credentials to access the dashboard.</p>

                        {error && (
                            <div className="mb-6 px-4 py-3 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm font-medium flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Username</label>
                                <input
                                    type="text" value={username} onChange={(e) => setUsername(e.target.value)} required
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all placeholder:text-slate-400"
                                    placeholder="e.g. admin"
                                />
                            </div>

                            <div className="relative">
                                <div className="flex justify-between items-center mb-1.5">
                                    <label className="block text-sm font-semibold text-slate-700">Password</label>
                                    <a href="#" className="text-xs font-semibold text-blue-600 hover:text-blue-500 transition-colors">Forgot password?</a>
                                </div>
                                <div className="relative">
                                    <input
                                        type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} required
                                        className="w-full px-4 py-3 pr-12 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all placeholder:text-slate-400"
                                        placeholder="••••••••"
                                    />
                                    <button
                                        type="button" onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                    >
                                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                            </div>

                            <button
                                type="submit" disabled={loading}
                                className="w-full py-3.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20 disabled:opacity-70 disabled:hover:bg-blue-600 mt-2 hover:-translate-y-0.5"
                            >
                                {loading ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                ) : (
                                    <>
                                        Sign In
                                        <LogIn className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </form>

                        <div className="mt-8 text-center text-sm text-slate-500">
                            Need help? <a href="#" className="font-semibold text-blue-600 hover:underline">Contact Support</a>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
}
