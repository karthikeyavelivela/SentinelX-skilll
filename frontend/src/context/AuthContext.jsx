import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        const saved = localStorage.getItem('vulnguard_user');
        return saved ? JSON.parse(saved) : null;
    });
    const [loading, setLoading] = useState(false);

    const login = async (username, password) => {
        setLoading(true);
        try {
            const { data } = await api.post('/auth/login', { username, password });
            localStorage.setItem('vulnguard_token', data.access_token);
            const userData = { username: data.username, role: data.role };
            localStorage.setItem('vulnguard_user', JSON.stringify(userData));
            setUser(userData);
            return { success: true };
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Login failed' };
        } finally {
            setLoading(false);
        }
    };

    const register = async (email, username, password, fullName) => {
        setLoading(true);
        try {
            await api.post('/auth/register', {
                email, username, password, full_name: fullName, role: 'analyst',
            });
            return await login(username, password);
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Registration failed' };
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('vulnguard_token');
        localStorage.removeItem('vulnguard_user');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
