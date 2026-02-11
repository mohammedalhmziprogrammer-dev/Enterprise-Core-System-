import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom';
import { logout } from '../api';
import {
    LogOut,
    LayoutDashboard,
    Users,
    Settings,
    AppWindow,
    Code,
    Rocket,
    ChevronDown,
    ChevronRight,
    ChevronLeft, // RTL
    User,
    Search,
    Bell,
    Menu
} from 'lucide-react';

const NavItem = ({ item, isActive, toggleSubmenu, openSubmenus }) => {
    const hasChildren = item.children && item.children.length > 0;
    const isOpen = openSubmenus[item.path];

    return (
        <div className="nav-item-container">
            <Link
                to={hasChildren ? '#' : item.path}
                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                onClick={(e) => {
                    if (hasChildren) {
                        e.preventDefault();
                        toggleSubmenu(item.path);
                    }
                }}
            >
                <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.label}</span>
                </div>
                {hasChildren && (
                    isOpen ? <ChevronDown size={16} /> : <ChevronLeft size={16} /> // RTL Arrow
                )}
            </Link>
            {hasChildren && isOpen && (
                <div className="submenu">
                    {item.children.map(child => (
                        <Link
                            key={child.path}
                            to={child.path}
                            className={`nav-item sub-item ${isActive(child.path) ? 'active' : ''}`}
                        >
                            <span>{child.label}</span>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};

const Layout = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [openSubmenus, setOpenSubmenus] = useState({});

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    const toggleSubmenu = (path) => {
        setOpenSubmenus(prev => ({
            ...prev,
            [path]: !prev[path]
        }));
    };

    const navItems = [
        {
            path: '/dashboard',
            label: 'لوحة التحكم',
            icon: <LayoutDashboard size={20} />
        },
        {
            path: '/clients',
            label: 'العملاء',
            icon: <Users size={20} />,
            children: [
                { path: '/clients?tab=beneficiaries', label: 'المستفيدين' },
                { path: '/clients?tab=structures', label: 'الهياكل' },
                { path: '/clients?tab=levels', label: 'المستويات' }
            ]
        },
        {
            path: '/users-app', // Virtual path for grouping
            label: 'المستخدمين',
            icon: <Users size={20} />,
            children: [
                { path: '/users', label: 'قائمة المستخدمين' },
                { path: '/role-management', label: 'الأدوار' },
                { path: '/group-management', label: 'المجموعات' },
                { path: '/user-management', label: 'الصلاحيات' }
            ]
        },
        {
            path: '/apps',
            label: 'التطبيقات',
            icon: <AppWindow size={20} />,
            children: [
                { path: '/apps', label: 'التطبيقات' },
            ]
        },
        {
            path: '/codings',
            label: 'الترميز',
            icon: <Code size={20} />,
            children: [
                { path: '/codings', label: 'قائمة الترميز' },
            ]
        },
        {
            path: '/releases',
            label: 'الإصدارات',
            icon: <Rocket size={20} />
        }
    ];

    // Helper to get current page title
    const getCurrentTitle = () => {
        // Simple logic for demo, can be enhanced
        const path = location.pathname;
        if (path.includes('dashboard')) return 'لوحة التحكم';
        if (path.includes('clients')) return 'العملاء';
        if (path.includes('users')) return 'المستخدمين';
        if (path.includes('apps')) return 'التطبيقات';
        if (path.includes('codings')) return 'الترميز';
        if (path.includes('releases')) return 'الإصدارات';
        return '';
    };

    return (
        <div className="layout" dir="rtl">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <h2>أفق</h2>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map(item => (
                        <NavItem
                            key={item.path}
                            item={item}
                            isActive={isActive}
                            toggleSubmenu={toggleSubmenu}
                            openSubmenus={openSubmenus}
                        />
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <button onClick={handleLogout} className="nav-item logout-btn">
                        <LogOut size={20} />
                        <span>تسجيل الخروج</span>
                    </button>
                </div>
            </aside>

            <div className="main-content">
                <header className="top-bar">
                    <div className="breadcrumbs">
                        <Menu size={20} className="text-secondary cursor-pointer" />
                        <span className="text-secondary">/</span>
                        <span className="font-bold text-primary">{getCurrentTitle()}</span>
                    </div>

                    <div className="user-menu">
                        <Search size={20} className="text-secondary cursor-pointer" />
                        <Bell size={20} className="text-secondary cursor-pointer" />
                        <div className="flex items-center gap-2 cursor-pointer">
                            <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center text-white font-bold">
                                M
                            </div>
                            <span className="text-sm font-medium">Mohammed</span>
                        </div>
                    </div>
                </header>

                <main className="page-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
