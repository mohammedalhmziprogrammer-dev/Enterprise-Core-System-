import React, { useState, useEffect } from 'react';
import {
    getGroups, createGroup, updateGroup, deleteGroup,
    getPermissions, assignGroupPermissions, getGroupUsers,
    getGroupStatistics
} from '../api';
import {
    Users, Plus, Edit, Trash2, Shield, Eye,
    X, Search, Loader2, Check, AlertCircle, BarChart3
} from 'lucide-react';

const GroupManagement = () => {
    const [groups, setGroups] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [statistics, setStatistics] = useState([]);

    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('create');
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [formData, setFormData] = useState({});
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [groupUsers, setGroupUsers] = useState([]);

    useEffect(() => {
        fetchAllData();
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [groupsData, permsData, statsData] = await Promise.all([
                getGroups(),
                getPermissions(),
                getGroupStatistics()
            ]);
            setGroups(groupsData);
            setPermissions(permsData);
            setStatistics(statsData);
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('فشل تحميل البيانات');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateGroup = () => {
        setModalType('create');
        setFormData({ name: '', permissions: [] });
        setShowModal(true);
    };

    const handleEditGroup = (group) => {
        setModalType('edit');
        setSelectedGroup(group);
        setFormData({ name: group.name });
        setShowModal(true);
    };

    const handleDeleteGroup = async (groupId) => {
        if (window.confirm('هل أنت متأكد من حذف هذه المجموعة؟')) {
            try {
                await deleteGroup(groupId);
                setSuccess('تم حذف المجموعة بنجاح');
                fetchAllData();
            } catch (error) {
                setError('فشل حذف المجموعة');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (modalType === 'create') {
                await createGroup(formData);
                setSuccess('تم إنشاء المجموعة بنجاح');
            } else if (modalType === 'edit') {
                await updateGroup(selectedGroup.id, formData);
                setSuccess('تم تحديث المجموعة بنجاح');
            } else if (modalType === 'permissions') {
                await assignGroupPermissions(selectedGroup.id, formData.permission_ids);
                setSuccess('تم تعيين الصلاحيات بنجاح');
            }

            setShowModal(false);
            fetchAllData();
        } catch (error) {
            setError(error.response?.data?.detail || 'فشلت العملية');
        } finally {
            setLoading(false);
        }
    };

    const openPermissionsModal = (group) => {
        setModalType('permissions');
        setSelectedGroup(group);
        setFormData({ permission_ids: group.permissions || [] });
        setShowModal(true);
    };

    const viewGroupUsers = async (group) => {
        setModalType('users');
        setSelectedGroup(group);
        try {
            const users = await getGroupUsers(group.id);
            setGroupUsers(users);
        } catch (error) {
            setError('فشل تحميل المستخدمين');
        }
        setShowModal(true);
    };

    const filteredGroups = groups.filter(group =>
        group.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const renderTable = () => {
        if (loading && !groups.length) {
            return (
                <div className="loading-container">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (filteredGroups.length === 0) {
            return <div className="empty-state">لا توجد مجموعات متاحة.</div>;
        }

        return (
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>اسم المجموعة</th>
                            <th>عدد الصلاحيات</th>
                            <th>عدد المستخدمين</th>
                            <th style={{ width: '200px' }}>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredGroups.map((group) => (
                            <tr key={group.id}>
                                <td className="font-medium">
                                    <div className="flex items-center gap-2">
                                        <Users size={16} className="text-accent" />
                                        {group.name}
                                    </div>
                                </td>
                                <td>
                                    <span className="badge badge-info text-xs">
                                        {group.permissions?.length || 0} صلاحية
                                    </span>
                                </td>
                                <td>
                                    {/* Assuming statistics might have this info, or we can just show a placeholder if not directly in group object */}
                                    {statistics.find(s => s.id === group.id)?.user_count || 0} مستخدم
                                </td>
                                <td>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => handleEditGroup(group)} className="action-btn btn-edit" title="تعديل">
                                            <Edit size={16} />
                                        </button>
                                        <button onClick={() => openPermissionsModal(group)} className="action-btn" title="الصلاحيات">
                                            <Shield size={16} />
                                        </button>
                                        <button onClick={() => viewGroupUsers(group)} className="action-btn" title="المستخدمين">
                                            <Eye size={16} />
                                        </button>
                                        <button onClick={() => handleDeleteGroup(group.id)} className="action-btn btn-delete" title="حذف">
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </td>
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
                <div>
                    <h1>إدارة المجموعات</h1>
                    <p>إدارة مجموعات المستخدمين وصلاحياتهم.</p>
                </div>
                <button onClick={handleCreateGroup} className="btn btn-primary">
                    <Plus size={18} />
                    <span>إضافة مجموعة</span>
                </button>
            </header>

            {/* Statistics */}
            {statistics.length > 0 && (
                <div className="card mb-6">
                    <h3 className="mb-4 flex items-center gap-2 font-bold text-lg">
                        <BarChart3 size={20} className="text-accent" />
                        إحصائيات المجموعات
                    </h3>
                    <div className="stats-grid-3">
                        {statistics.slice(0, 6).map((stat) => (
                            <div key={stat.id} className="stat-item">
                                <div className="stat-label">{stat.name}</div>
                                <div className="stat-value">{stat.user_count} مستخدم</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="card">
                <div className="mb-6 flex justify-between items-center">
                    <div className="search-box">
                        <Search className="search-icon" />
                        <input
                            type="text"
                            placeholder="بحث عن مجموعة..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input-field with-icon"
                        />
                    </div>
                </div>
                {renderTable()}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>
                                {modalType === 'create' && 'إضافة مجموعة جديدة'}
                                {modalType === 'edit' && 'تعديل المجموعة'}
                                {modalType === 'permissions' && 'تعيين الصلاحيات'}
                                {modalType === 'users' && 'مستخدمي المجموعة'}
                            </h2>
                            <button onClick={() => setShowModal(false)} className="modal-close">
                                <X />
                            </button>
                        </div>

                        {error && (
                            <div className="error-message">
                                <AlertCircle size={16} />
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="modal-body">
                            {(modalType === 'create' || modalType === 'edit') && (
                                <div className="input-group">
                                    <label>اسم المجموعة *</label>
                                    <input
                                        type="text"
                                        required
                                        value={formData.name || ''}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        className="input-field"
                                        placeholder="أدخل اسم المجموعة"
                                    />
                                </div>
                            )}

                            {modalType === 'permissions' && (
                                <div className="permissions-list">
                                    {permissions.map((perm) => (
                                        <label key={perm.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.permission_ids?.includes(perm.id)}
                                                onChange={(e) => {
                                                    const permIds = formData.permission_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, permission_ids: [...permIds, perm.id] });
                                                    } else {
                                                        setFormData({ ...formData, permission_ids: permIds.filter(id => id !== perm.id) });
                                                    }
                                                }}
                                            />
                                            <span>{perm.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {modalType === 'users' && (
                                <div className="users-list">
                                    {groupUsers.length > 0 ? (
                                        groupUsers.map((user) => (
                                            <div key={user.id} className="user-item">
                                                <Users size={16} />
                                                <span>{user.username} - {user.first_name} {user.last_name}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="empty-state">لا يوجد مستخدمين في هذه المجموعة</p>
                                    )}
                                </div>
                            )}

                            {modalType !== 'users' && (
                                <div className="modal-footer">
                                    <button
                                        type="button"
                                        onClick={() => setShowModal(false)}
                                        className="btn btn-secondary"
                                    >
                                        إلغاء
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="btn btn-primary"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 className="spinner" />
                                                جاري المعالجة...
                                            </>
                                        ) : (
                                            'حفظ'
                                        )}
                                    </button>
                                </div>
                            )}
                        </form>
                    </div>
                </div>
            )}

            {/* Success Message */}
            {success && (
                <div className="toast toast-success">
                    <Check size={20} />
                    {success}
                </div>
            )}
        </div>
    );
};

export default GroupManagement;
