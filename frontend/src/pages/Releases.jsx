import React, { useState, useEffect } from 'react';
import { getReleases } from '../api';
import { Loader2, Calendar, Box, Users, Layers } from 'lucide-react';

const Releases = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const result = await getReleases();
            setData(result);
        } catch (error) {
            console.error('Error fetching releases:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full p-8">
                <Loader2 className="spinner text-accent" />
            </div>
        );
    }

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <h1>Releases Management</h1>
                <p>Track and manage application releases and updates.</p>
            </header>

            <div className="grid-layout">
                {data.length === 0 ? (
                    <div className="glass-panel p-8 text-center" style={{ gridColumn: '1 / -1' }}>
                        <p className="empty-state">No releases found.</p>
                    </div>
                ) : (
                    data.map((release) => (
                        <div key={release.id} className="glass-panel card release-card">
                            <div className="release-header">
                                <div>
                                    <h3 className="release-title">{release.name}</h3>
                                    <span className={`badge ${release.is_update ? 'badge-update' : 'badge-new'}`}>
                                        {release.is_update ? 'Update' : 'New Release'}
                                    </span>
                                </div>
                                <div className="release-date">
                                    <Calendar className="meta-icon" />
                                    {formatDate(release.release_date)}
                                </div>
                            </div>

                            {release.descraption && (
                                <p className="release-desc">{release.descraption}</p>
                            )}

                            <div className="release-meta">
                                <div className="meta-row">
                                    <Box className="meta-icon" />
                                    <span className="meta-label">Apps:</span>
                                    <span className="meta-value" title={release.apps_details?.map(a => a.name).join(', ')}>
                                        {release.apps_details?.map(a => a.name).join(', ') || 'None'}
                                    </span>
                                </div>
                                <div className="meta-row">
                                    <Users className="meta-icon" />
                                    <span className="meta-label">Beneficiaries:</span>
                                    <span className="meta-value" title={release.beneficiary_details?.map(b => b.name).join(', ')}>
                                        {release.beneficiary_details?.map(b => b.name).join(', ') || 'None'}
                                    </span>
                                </div>
                                <div className="meta-row">
                                    <Layers className="meta-icon" />
                                    <span className="meta-label">Groups:</span>
                                    <span className="meta-value" title={release.groups_details?.map(g => g.name).join(', ')}>
                                        {release.groups_details?.map(g => g.name).join(', ') || 'None'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Releases;
