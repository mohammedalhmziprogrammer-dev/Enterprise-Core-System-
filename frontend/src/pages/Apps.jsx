import React, { useState, useEffect } from 'react';
import { getApps, getAppTypes, getAppVersions } from '../api';
import { Loader2, AppWindow } from 'lucide-react';

const Apps = () => {
    const [activeTab, setActiveTab] = useState('apps');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setLoading(true);
        try {
            let result;
            if (activeTab === 'apps') {
                result = await getApps();
            } else if (activeTab === 'types') {
                result = await getAppTypes();
            } else if (activeTab === 'versions') {
                result = await getAppVersions();
            }
            setData(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderAppsGrid = () => {
        if (data.length === 0) {
            return <p className="empty-state p-4">No apps available.</p>;
        }

        return (
            <div className="apps-grid">
                {data.map((app) => (
                    <div key={app.app_label} className="glass-panel app-card">
                        <div className="app-icon">
                            {app.icon ? (
                                <img src={app.icon} alt={app.name} className="w-8 h-8 object-contain" />
                            ) : (
                                <AppWindow size={32} />
                            )}
                        </div>
                        <h3>{app.name || app.app_label}</h3>
                        {app.description && <p className="app-description">{app.description}</p>}
                        {app.url && (
                            <a href={app.url} className="app-link" target="_blank" rel="noopener noreferrer">
                                Open App
                            </a>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    const renderTable = () => {
        if (data.length === 0) {
            return <p className="empty-state p-4">No data available.</p>;
        }

        // Filter out internal fields and large objects
        const headers = Object.keys(data[0]).filter(key =>
            !['id', 'app', 'appVersion', 'icon', 'path'].includes(key)
        );

        return (
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            {headers.map(header => (
                                <th key={header}>{header.replace(/_/g, ' ').toUpperCase()}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((item, index) => (
                            <tr key={index}>
                                {headers.map(header => (
                                    <td key={header}>
                                        {typeof item[header] === 'boolean'
                                            ? (item[header] ? 'Yes' : 'No')
                                            : typeof item[header] === 'object'
                                                ? JSON.stringify(item[header])
                                                : item[header]}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderContent = () => {
        if (loading) {
            return (
                <div className="loading-container">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (activeTab === 'apps') {
            return renderAppsGrid();
        } else {
            return (
                <div className="glass-panel content-panel">
                    {renderTable()}
                </div>
            );
        }
    };

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <h1>Applications Management</h1>
                <p>Manage apps, types, and versions.</p>
            </header>

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'apps' ? 'active' : ''}`}
                    onClick={() => setActiveTab('apps')}
                >
                    Applications
                </button>
                <button
                    className={`tab-btn ${activeTab === 'types' ? 'active' : ''}`}
                    onClick={() => setActiveTab('types')}
                >
                    App Types
                </button>
                <button
                    className={`tab-btn ${activeTab === 'versions' ? 'active' : ''}`}
                    onClick={() => setActiveTab('versions')}
                >
                    App Versions
                </button>
            </div>

            <div className="content-section">
                {renderContent()}
            </div>
        </div>
    );
};

export default Apps;
