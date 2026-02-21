import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CVEsPage from './pages/CVEsPage';
import AssetsPage from './pages/AssetsPage';
import MatchingPage from './pages/MatchingPage';
import MLPage from './pages/MLPage';
import GraphPage from './pages/GraphPage';
import RiskPage from './pages/RiskPage';
import RemediationPage from './pages/RemediationPage';
import LandingPage from './pages/LandingPage';
import AboutPage from './pages/AboutPage';
import TeamPage from './pages/TeamPage';
import AgentScanPage from './pages/AgentScanPage';

function ProtectedLayout() {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" replace />;

    return (
        <div className="flex min-h-screen gradient-mesh">
            <Sidebar />
            <main className="flex-1 ml-[240px] transition-all duration-300">
                <Outlet />
            </main>
        </div>
    );
}

function ProtectedScanRoute({ children }) {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" replace />;
    return children;
}

function PublicRoute({ children }) {
    const { user } = useAuth();
    // If logged in, go to scan page first instead of dashboard to ensure scan happens
    if (user) return <Navigate to="/scan" replace />;
    return children;
}

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    {/* The root landing page and other marketing pages should always be accessible, even when logged in */}
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/team" element={<TeamPage />} />

                    {/* Only the login page should redirect away if the user is already authenticated */}
                    <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />

                    <Route path="/scan" element={<ProtectedScanRoute><AgentScanPage /></ProtectedScanRoute>} />

                    <Route element={<ProtectedLayout />}>
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/cves" element={<CVEsPage />} />
                        <Route path="/assets" element={<AssetsPage />} />
                        <Route path="/matching" element={<MatchingPage />} />
                        <Route path="/ml" element={<MLPage />} />
                        <Route path="/graph" element={<GraphPage />} />
                        <Route path="/risk" element={<RiskPage />} />
                        <Route path="/remediation" element={<RemediationPage />} />
                    </Route>

                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}
