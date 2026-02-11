import React, { useState, useEffect } from 'react';
import {
    getRoles, createRole, updateRole, deleteRole,
    getPermissions, assignRolePermissions, getRoleUsers,
    getCodingCategories, getCodings,
    assignRoleCodingCategories, assignRoleCodings
} from '../api';
import {
    Shield, Plus, Edit, Trash2, Users, Code, Tag,
    X, Search, Loader2, Check, AlertCircle, MoreHorizontal
} from 'lucide-react';

const RoleManagement = () => {
    const [roles, setRoles] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [codingCategories, setCodingCategories] = useState([]);
    const [codings, setCodings] = useState([]);

    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('create');
    const [selectedRole, setSelectedRole] = useState(null);
    const [formData, setFormData] = useState({});
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [roleUsers, setRoleUsers] = useState([]);

    useEffect(() => {
        fetchAllData();
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [rolesData, permsData, categoriesData, codingsData] = await Promise.all([
                getRoles(),
                getPermissions(),
                getCodingCategories(),
                getCodings()
            ]);
            setRoles(rolesData);
            setPermissions(permsData);
            setCodingCategories(categoriesData);
            setCodings(codingsData);
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('فشل تحميل البيانات');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateRole = () => {
        setModalType('create');
        setFormData({ name: '', permissions: [] });
        setShowModal(true);
    };

    const handleEditRole = (role) => {
        setModalType('edit');
        setSelectedRole(role);
        setFormData({ name: role.name });
        setShowModal(true);
    };

    const handleDeleteRole = async (roleId) => {
        if (window.confirm('هل أنت متأكد من حذف هذا الدور؟')) {
            try {
                await deleteRole(roleId);
                setSuccess('تم حذف الدور بنجاح');
                fetchAllData();
            } catch (error) {
                setError('فشل حذف الدور');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (modalType === 'create') {
                await createRole(formData);
                setSuccess('تم إنشاء الدور بنجاح');
            } else if (modalType === 'edit') {
                await updateRole(selectedRole.id, formData);
                setSuccess('تم تحديث الدور بنجاح');
            } else if (modalType === 'permissions') {
                await assignRolePermissions(selectedRole.id, formData.permission_ids);
                setSuccess('تم تعيين الصلاحيات بنجاح');
            } else if (modalType === 'categories') {
                await assignRoleCodingCategories(selectedRole.id, formData.category_ids);
                setSuccess('تم تعيين فئات الترميز بنجاح');
            } else if (modalType === 'codings') {
                await assignRoleCodings(selectedRole.id, formData.coding_ids);
                setSuccess('تم تعيين الترميزات بنجاح');
            }

            setShowModal(false);
            fetchAllData();
        } catch (error) {
            setError(error.response?.data?.detail || 'فشلت العملية');
        } finally {
            setLoading(false);
        }
    };

    const openPermissionsModal = (role) => {
        setModalType('permissions');
        setSelectedRole(role);
        setFormData({ permission_ids: role.permissions || [] });
        setShowModal(true);
    };

    const openCategoriesModal = (role) => {
        setModalType('categories');
        setSelectedRole(role);
        setFormData({ category_ids: role.codingCategory || [] });
        setShowModal(true);
    };

    const openCodingsModal = (role) => {
        setModalType('codings');
        setSelectedRole(role);
        setFormData({ coding_ids: role.coding || [] });
        setShowModal(true);
    };

    const viewRoleUsers = async (role) => {
        setModalType('users');
        setSelectedRole(role);
        try {
            const users = await getRoleUsers(role.id);
            setRoleUsers(users);
        } catch (error) {
            setError('فشل تحميل المستخدمين');
        }
        setShowModal(true);
    };

    const filteredRoles = roles.filter(role =>
        role.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const renderTable = () => {
        if (loading && !roles.length) {
            return (
                <div className="loading-container">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (filteredRoles.length === 0) {
            return <div className="empty-state">لا توجد أدوار متاحة.</div>;
        }

        return (
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>اسم الدور</th>
                            <th>عدد الصلاحيات</th>
                            <th>فئات الترميز</th>
                            <th>الترميزات</th>
                            <th style={{ width: '250px' }}>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredRoles.map((role) => (
                            <tr key={role.id}>
                                <td className="font-medium">
                                    <div className="flex items-center gap-2">
                                        <Shield size={16} className="text-accent" />
                                        {role.name}
                                    </div>
                                </td>
                                <td>
                                    <span className="badge badge-info text-xs">
                                        {role.permissions?.length || 0} صلاحية
                                    </span>
                                </td>
                                <td>{role.codingCategory?.length || 0}</td>
                                <td>{role.coding?.length || 0}</td>
                                <td>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => handleEditRole(role)} className="action-btn btn-edit" title="تعديل">
                                            <Edit size={16} />
                                        </button>
                                        <button onClick={() => openPermissionsModal(role)} className="action-btn" title="الصلاحيات">
                                            <Shield size={16} />
                                        </button>
                                        <button onClick={() => openCategoriesModal(role)} className="action-btn" title="فئات الترميز">
                                            <Tag size={16} />
                                        </button>
                                        <button onClick={() => openCodingsModal(role)} className="action-btn" title="الترميزات">
                                            <Code size={16} />
                                        </button>
                                        <button onClick={() => viewRoleUsers(role)} className="action-btn" title="المستخدمين">
                                            <Users size={16} />
                                        </button>
                                        <button onClick={() => handleDeleteRole(role.id)} className="action-btn btn-delete" title="حذف">
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
                    <h1>إدارة الأدوار</h1>
                    <p>إدارة الأدوار والصلاحيات والوصول.</p>
                </div>
                <button onClick={handleCreateRole} className="btn btn-primary">
                    <Plus size={18} />
                    <span>إضافة دور</span>
                </button>
            </header>

            <div className="card">
                <div className="mb-6 flex justify-between items-center">
                    <div className="search-box">
                        <Search className="search-icon" />
                        <input
                            type="text"
                            placeholder="بحث عن دور..."
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
                                {modalType === 'create' && 'إضافة دور جديد'}
                                {modalType === 'edit' && 'تعديل الدور'}
                                {modalType === 'permissions' && 'تعيين الصلاحيات'}
                                {modalType === 'categories' && 'تعيين فئات الترميز'}
                                {modalType === 'codings' && 'تعيين الترميزات'}
                                {modalType === 'users' && 'مستخدمي الدور'}
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
                                    <label>اسم الدور *</label>
                                    <input
                                        type="text"
                                        required
                                        value={formData.name || ''}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        className="input-field"
                                        placeholder="أدخل اسم الدور"
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

                            {modalType === 'categories' && (
                                <div className="categories-list">
                                    {codingCategories.map((category) => (
                                        <label key={category.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.category_ids?.includes(category.id)}
                                                onChange={(e) => {
                                                    const catIds = formData.category_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, category_ids: [...catIds, category.id] });
                                                    } else {
                                                        setFormData({ ...formData, category_ids: catIds.filter(id => id !== category.id) });
                                                    }
                                                }}
                                            />
                                            <span>{category.general_name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {modalType === 'codings' && (
                                <div className="codings-list">
                                    {codings.map((coding) => (
                                        <label key={coding.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.coding_ids?.includes(coding.id)}
                                                onChange={(e) => {
                                                    const codingIds = formData.coding_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, coding_ids: [...codingIds, coding.id] });
                                                    } else {
                                                        setFormData({ ...formData, coding_ids: codingIds.filter(id => id !== coding.id) });
                                                    }
                                                }}
                                            />
                                            <span>{coding.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {modalType === 'users' && (
                                <div className="users-list">
                                    {roleUsers.length > 0 ? (
                                        roleUsers.map((user) => (
                                            <div key={user.id} className="user-item">
                                                <Users size={16} />
                                                <span>{user.username} - {user.first_name} {user.last_name}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="empty-state">لا يوجد مستخدمين معينين لهذا الدور</p>
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

export default RoleManagement;
