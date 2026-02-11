import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Users, Shield, LayoutGrid, Code, Rocket, Settings,
    UserCog, Building, Database, FileText
} from 'lucide-react';

const Dashboard = () => {
    const navigate = useNavigate();

    const apps = [
        {
            id: 'clients',
            title: 'العملاء',
            icon: <Users size={40} />,
            color: '#3b82f6', // Blue
            path: '/clients'
        },
        {
            id: 'users',
            title: 'المستخدمين',
            icon: <UserCog size={40} />,
            color: '#10b981', // Green
            path: '/users'
        },
        {
            id: 'roles',
            title: 'الأدوار',
            icon: <Shield size={40} />,
            color: '#8b5cf6', // Purple
            path: '/role-management'
        },
        {
            id: 'groups',
            title: 'المجموعات',
            icon: <Building size={40} />,
            color: '#f59e0b', // Orange
            path: '/group-management'
        },
        {
            id: 'permissions',
            title: 'الصلاحيات',
            icon: <Database size={40} />,
            color: '#ef4444', // Red
            path: '/user-management'
        },
        {
            id: 'apps',
            title: 'التطبيقات',
            icon: <LayoutGrid size={40} />,
            color: '#06b6d4', // Cyan
            path: '/apps'
        },
        {
            id: 'codings',
            title: 'الترميز',
            icon: <Code size={40} />,
            color: '#ec4899', // Pink
            path: '/codings'
        },
        {
            id: 'releases',
            title: 'الإصدارات',
            icon: <Rocket size={40} />,
            color: '#6366f1', // Indigo
            path: '/releases'
        }
    ];

    return (
        <div className="dashboard-container fade-in p-8">
            <header className="mb-8 text-center">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">مرحباً بك في أفق</h1>
                <p className="text-gray-500">اختر تطبيقاً للبدء</p>
            </header>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
                {apps.map((app) => (
                    <div
                        key={app.id}
                        onClick={() => navigate(app.path)}
                        className="app-card bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-all cursor-pointer border border-gray-100 flex flex-col items-center justify-center gap-4 group"
                    >
                        <div
                            className="w-20 h-20 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110"
                            style={{ backgroundColor: `${app.color}15`, color: app.color }}
                        >
                            {app.icon}
                        </div>
                        <span className="font-semibold text-gray-700 text-lg">{app.title}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;
