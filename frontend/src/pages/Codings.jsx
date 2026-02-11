import React, { useState, useEffect } from 'react';
import { getCodingCategories, getCodings } from '../api';
import { Loader2 } from 'lucide-react';

const Codings = () => {
    const [activeTab, setActiveTab] = useState('categories');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setLoading(true);
        try {
            let result;
            if (activeTab === 'categories') {
                result = await getCodingCategories();
            } else if (activeTab === 'codings') {
                result = await getCodings();
            }
            setData(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderTable = () => {
        if (loading) {
            return (
                <div className="flex justify-center p-8">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (data.length === 0) {
            return <p className="empty-state p-4">No data available.</p>;
        }

        // Filter out internal fields
        const headers = Object.keys(data[0]).filter(key =>
            !['id', 'codingCategory_details'].includes(key)
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
                                                ? JSON.stringify(item[header]) // Fallback for objects
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

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <h1>Codings Management</h1>
                <p>Manage coding categories and individual codes.</p>
            </header>

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'categories' ? 'active' : ''}`}
                    onClick={() => setActiveTab('categories')}
                >
                    Categories
                </button>
                <button
                    className={`tab-btn ${activeTab === 'codings' ? 'active' : ''}`}
                    onClick={() => setActiveTab('codings')}
                >
                    Codings
                </button>
            </div>

            <div className="glass-panel content-panel">
                {renderTable()}
            </div>
        </div>
    );
};

export default Codings;
