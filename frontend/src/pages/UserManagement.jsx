import React, { useState, useEffect } from 'react';
import { Group, Loader2 } from "lucide-react";
import {
    getUsers, createUser, updateUser, deleteUser,
    getRoles, getGroups, getPermissions, getStructures,
    assignUserRoles, assignUserStructures, getUserPermissions,
    resetUserPassword, getUserStatistics,assignUserGroups
} from '../api';
import {
    Users as UsersIcon, UserPlus, Edit, Trash2, Key, Shield,
    Building, X, Search, Filter, Check, AlertCircle, Eye
} from 'lucide-react';

const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [structures, setStructures] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [groups,setGroups]=useState([])

    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('create'); // create, edit, roles, structures, permissions, password
    const [selectedUser, setSelectedUser] = useState(null);
    const [formData, setFormData] = useState({});
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({
        is_active: '',
        is_staff: '',
        data_visibility: ''
    });
    const [showFilters, setShowFilters] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchAllData();
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [usersData, rolesData, groupsData, structuresData, permissionsData, statsData] = await Promise.all([
                getUsers(),
                getRoles(),
                getGroups(),
                getStructures(),
                getPermissions(),
                getUserStatistics(),

            ]);
            setUsers(usersData);
            setRoles(rolesData);
            // console.log("roles added")
            setStructures(structuresData);
            setPermissions(permissionsData);
            setStatistics(statsData);
            setGroups(groupsData)
             console.log("grpup added")
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('فشل تحميل البيانات');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = () => {
        setModalType('create');
        setFormData({
            username: '',
            email: '',
            password: '',
            first_name: '',
            last_name: '',
            is_active: true,
            data_visibility: 'self',
            stractures: [],
            direct_manager: null
        });
        setShowModal(true);
    };

    const handleEditUser = (user) => {
        setModalType('edit');
        setSelectedUser(user);
        setFormData({
            first_name: user.first_name,
            last_name: user.last_name,
            email: user.email,
            is_active: user.is_active,
            data_visibility: user.data_visibility,
            stractures: user.stractures || [],
            direct_manager: user.direct_manager
        });
        setShowModal(true);
    };

    const handleDeleteUser = async (userId) => {
        if (window.confirm('هل أنت متأكد من حذف هذا المستخدم؟')) {
            try {
                await deleteUser(userId);
                setSuccess('تم حذف المستخدم بنجاح');
                fetchAllData();
            } catch (error) {
                setError('فشل حذف المستخدم');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (modalType === 'create') {
                await createUser(formData);
                setSuccess('تم إنشاء المستخدم بنجاح');
                //  console.log("add in here added")
            } else if (modalType === 'edit') {
                await updateUser(selectedUser.id, formData);
                setSuccess('تم تحديث المستخدم بنجاح');
            } else if (modalType === 'roles') {
                await assignUserRoles(selectedUser.id, formData.role_ids);
                setSuccess('تم تعيين الأدوار بنجاح');
            }
             else if (modalType === 'groups') {
                await assignUserGroups(selectedUser.id, formData.group_ids);
                setSuccess('تم تعيين المجموعات بنجاح');
            } else if (modalType === 'structures') {
                await assignUserStructures(selectedUser.id, formData.structure_ids);
                setSuccess('تم تعيين الهياكل بنجاح');
            } else if (modalType === 'password') {
                await resetUserPassword(selectedUser.id, formData.new_password);
                setSuccess('تم إعادة تعيين كلمة المرور بنجاح');
            }

            setShowModal(false);
            fetchAllData();
        } catch (error) {
            setError(error.response?.data?.detail || 'فشلت العملية');
        } finally {
            setLoading(false);
        }
    };

    const openRolesModal = (user) => {
        setModalType('roles');
        setSelectedUser(user);
        setFormData({ role_ids:user.roles || [] });
        setShowModal(true);
    };
    
    const openGroupsModal = (user) => {
        setModalType('groups');
        setSelectedUser(user);
        setFormData({ group_ids: user.groups || [] });
        setShowModal(true);
    };

    const openStructuresModal = (user) => {
        setModalType('structures');
        setSelectedUser(user);
        setFormData({ structure_ids: user.stractures || [] });
        setShowModal(true);
    };

    const openPasswordModal = (user) => {
        setModalType('password');
        setSelectedUser(user);
        setFormData({ new_password: '' });
        setShowModal(true);
    };

    const openPermissionsModal = async (user) => {
        setModalType('permissions');
        setSelectedUser(user);
        try {
            const perms = await getUserPermissions(user.id);
            setFormData({ permissions: perms });
        } catch (error) {
            setError('فشل تحميل الصلاحيات');
        }
        setShowModal(true);
    };

    const filteredUsers = users.filter(user => {
        const matchesSearch =
            user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.email?.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesFilters =
            (filters.is_active === '' || user.is_active.toString() === filters.is_active) &&
            (filters.is_staff === '' || user.is_staff.toString() === filters.is_staff) &&
            (filters.data_visibility === '' || user.data_visibility === filters.data_visibility);

        return matchesSearch && matchesFilters;
    });

    return (
        <div className="page-container fade-in">
            {/* Header with Statistics */}
            <header className="page-header">
                <div>
                    <h1>إدارة الصلاحيات</h1>
                    <p>إدارة المستخدمين، الأدوار، الصلاحيات، والهيكل التنظيمي.</p>
                </div>
                <button onClick={handleCreateUser} className="btn btn-primary">
                    <UserPlus size={18} />
                    <span>إضافة مستخدم</span>
                </button>
            </header>

            {/* Statistics Cards */}
            {statistics && (
                <div className="stats-grid-4 mb-6">
                    <div className="stat-card glass-panel">
                        <div className="stat-icon bg-blue">
                            <UsersIcon />
                        </div>
                        <div className="stat-content">
                            <div className="stat-label">إجمالي المستخدمين</div>
                            <div className="stat-value">{statistics.total_users}</div>
                        </div>
                    </div>
                    <div className="stat-card glass-panel">
                        <div className="stat-icon bg-green">
                            <Check />
                        </div>
                        <div className="stat-content">
                            <div className="stat-label">المستخدمين النشطين</div>
                            <div className="stat-value">{statistics.active_users}</div>
                        </div>
                    </div>
                    <div className="stat-card glass-panel">
                        <div className="stat-icon bg-purple">
                            <Shield />
                        </div>
                        <div className="stat-content">
                            <div className="stat-label">المديرين</div>
                            <div className="stat-value">{statistics.staff_users}</div>
                        </div>
                    </div>
                    <div className="stat-card glass-panel">
                        <div className="stat-icon bg-orange">
                            <AlertCircle />
                        </div>
                        <div className="stat-content">
                            <div className="stat-label"> المستخدمين غيرالنشطين </div>
                            <div className="stat-value">{statistics.inactive_users}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Search and Filters */}
            <div className="card mb-6">
                <div className="flex gap-4 items-center">
                    <div className="search-box flex-1">
                        <Search className="search-icon" />
                        <input
                            type="text"
                            placeholder="بحث عن مستخدم..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input-field with-icon"
                        />
                    </div>
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className="btn btn-secondary"
                    >
                        <Filter size={18} />
                        <span>تصفية</span>
                    </button>
                </div>

                {showFilters && (
                    <div className="filters-grid mt-4">
                        <div className="input-group">
                            <label>الحالة</label>
                            <select
                                value={filters.is_active}
                                onChange={(e) => setFilters({ ...filters, is_active: e.target.value })}
                                className="input-field"
                            >
                                <option value="">الكل</option>
                                <option value="true">نشط</option>
                                <option value="false">غير نشط</option>
                            </select>
                        </div>
                        <div className="input-group">
                            <label>المدير</label>
                            <select
                                value={filters.is_staff}
                                onChange={(e) => setFilters({ ...filters, is_staff: e.target.value })}
                                className="input-field"
                            >
                                <option value="">الكل</option>
                                <option value="true">مدير</option>
                                <option value="false">غير مدير</option>
                            </select>
                        </div>
                        <div className="input-group">
                            <label>رؤية البيانات</label>
                            <select
                                value={filters.data_visibility}
                                onChange={(e) => setFilters({ ...filters, data_visibility: e.target.value })}
                                className="input-field"
                            >
                                <option value="">الكل</option>
                                <option value="self">شخصي فقط</option>
                                <option value="department">القسم</option>
                                <option value="all">كل البيانات</option>
                            </select>
                        </div>
                    </div>
                )}
            </div>

            {/* Users Table */}
            <div className="card">
                {loading && !users.length ? (
                    <div className="loading-container">
                        <Loader2 className="spinner text-accent" />
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>اسم المستخدم</th>
                                    <th>الاسم</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>الحالة</th>
                                    <th>الدور</th>
                                    <th>رؤية البيانات</th>
                                    <th style={{ width: '250px' }}>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map((user) => (
                                    <tr key={user.id}>
                                        <td className="font-medium">{user.username}</td>
                                        <td>{user.first_name} {user.last_name}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            {user.is_active ? (
                                                <span className="badge badge-success text-xs flex items-center gap-1 w-fit">
                                                    <Check size={12} /> نشط
                                                </span>
                                            ) : (
                                                <span className="badge badge-error text-xs flex items-center gap-1 w-fit">
                                                    <X size={12} /> غير نشط
                                                </span>
                                            )}
                                        </td>
                                        <td>
                                            {user.is_superuser ? (
                                                <span className="badge badge-purple text-xs">مسؤول فائق</span>
                                            ) : user.is_staff ? (
                                                <span className="badge badge-blue text-xs">مدير</span>
                                            ) : (
                                                <span className="badge badge-gray text-xs">مستخدم</span>
                                            )}
                                        </td>
                                        <td>
                                            <span className="text-secondary text-sm">
                                                {user.data_visibility === 'self' && 'شخصي'}
                                                {user.data_visibility === 'department' && 'القسم'}
                                                {user.data_visibility === 'all' && 'الكل'}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="flex items-center gap-2">
                                                <button onClick={() => handleEditUser(user)} className="action-btn btn-edit" title="تعديل">
                                                    <Edit size={16} />
                                                </button>
                                                <button onClick={() => openRolesModal(user)} className="action-btn" title="الأدوار">
                                                    <Shield size={16} />
                                                </button>
                                                  <button onClick={() => openGroupsModal(user)} className="action-btn" title="المجموعات">
                                                    <Group size={16} />
                                                </button>
                                                <button onClick={() => openStructuresModal(user)} className="action-btn" title="الهياكل">
                                                    <Building size={16} />
                                                </button>
                                                <button onClick={() => openPasswordModal(user)} className="action-btn" title="كلمة المرور">
                                                    <Key size={16} />
                                                </button>
                                                <button onClick={() => openPermissionsModal(user)} className="action-btn" title="الصلاحيات">
                                                    <Eye size={16} />
                                                </button>
                                                <button onClick={() => handleDeleteUser(user.id)} className="action-btn btn-delete" title="حذف">
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>
                                {modalType === 'create' && 'إضافة مستخدم جديد'}
                                {modalType === 'edit' && 'تعديل المستخدم'}
                                {modalType === 'roles' && 'تعيين الأدوار'}
                                 {modalType === 'groups' && 'تعيين المجموعات'}
                                {modalType === 'structures' && 'تعيين الهياكل'}
                                {modalType === 'password' && 'إعادة تعيين كلمة المرور'}
                                {modalType === 'permissions' && 'صلاحيات المستخدم'}
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
                                <>
                                    <div className="form-grid">
                                        {modalType === 'create' && (
                                            <div className="input-group">
                                                <label>اسم المستخدم *</label>
                                                <input
                                                    type="text"
                                                    required
                                                    value={formData.username || ''}
                                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                                    className="input-field"
                                                />
                                            </div>
                                        )}
                                        <div className="input-group">
                                            <label>الاسم الأول *</label>
                                            <input
                                                type="text"
                                                required
                                                value={formData.first_name || ''}
                                                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>اسم العائلة *</label>
                                            <input
                                                type="text"
                                                required
                                                value={formData.last_name || ''}
                                                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>البريد الإلكتروني *</label>
                                            <input
                                                type="email"
                                                required
                                                value={formData.email || ''}
                                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        {modalType === 'create' && (
                                            <div className="input-group">
                                                <label>كلمة المرور *</label>
                                                <input
                                                    type="password"
                                                    required
                                                    value={formData.password || ''}
                                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                                    className="input-field"
                                                />
                                            </div>
                                        )}
                                        <div className="input-group">
                                            <label>رؤية البيانات</label>
                                            <select
                                                value={formData.data_visibility || 'self'}
                                                onChange={(e) => setFormData({ ...formData, data_visibility: e.target.value })}
                                                className="input-field"
                                            >
                                                <option value="self">شخصي فقط</option>
                                                <option value="department">القسم</option>
                                                <option value="all">كل البيانات</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.is_active || false}
                                                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                            />
                                            <span>نشط</span>
                                        </label>
                                        {modalType === 'create' && (
                                            <>
                                                <label className="checkbox-label">
                                                    <input
                                                        type="checkbox"
                                                        checked={formData.is_staff || false}
                                                        onChange={(e) => setFormData({ ...formData, is_staff: e.target.checked })}
                                                    />
                                                    <span>مدير</span>
                                                </label>
                                              
                                            </>
                                        )}
                                    </div>
                                </>
                            )}

                            {modalType === 'roles' && (
                                <div className="roles-list">
                                    {roles.map((role) => (
                                        <label key={role.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.role_ids?.includes(role.id)}
                                                onChange={(e) => {
                                                    const roleIds = formData.role_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, role_ids: [...roleIds, role.id] });
                                                    } else {
                                                        setFormData({ ...formData, role_ids: roleIds.filter(id => id !== role.id) });
                                                    }
                                                }}
                                            />
                                            <span>{role.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}
                              {modalType === 'groups' && (
                                <div className="groups-list">
                                    {groups.map((group) => (
                                        <label key={group.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.group_ids?.includes(group.id)}
                                                onChange={(e) => {
                                                    const groupIds = formData.group_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, group_ids: [...groupIds, group.id] });
                                                    } else {
                                                        setFormData({ ...formData, group_ids: groupIds.filter(id => id !== group.id) });
                                                    }
                                                }}
                                            />
                                            <span>{group.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {modalType === 'structures' && (
                                <div className="structures-list">
                                    {structures.map((structure) => (
                                        <label key={structure.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.structure_ids?.includes(structure.id)}
                                                onChange={(e) => {
                                                    const structureIds = formData.structure_ids || [];
                                                    if (e.target.checked) {
                                                        setFormData({ ...formData, structure_ids: [...structureIds, structure.id] });
                                                    } else {
                                                        setFormData({ ...formData, structure_ids: structureIds.filter(id => id !== structure.id) });
                                                    }
                                                }}
                                            />
                                            <span>{structure.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {modalType === 'password' && (
                                <div className="input-group">
                                    <label>كلمة المرور الجديدة *</label>
                                    <input
                                        type="password"
                                        required
                                        value={formData.new_password || ''}
                                        onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
                                        className="input-field"
                                        placeholder="أدخل كلمة المرور الجديدة"
                                    />
                                </div>
                            )}

                            {modalType === 'permissions' && formData.permissions && (
                                <div className="permissions-view">
                                    <div className="permissions-section">
                                        <h3>كل الصلاحيات</h3>
                                        <div className="permissions-grid">
                                            {formData.permissions.all_permissions?.map((perm) => (
                                                <div key={perm.id} className="permission-item">
                                                    <Shield size={14} />
                                                    <span>{perm.name}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {modalType !== 'permissions' && (
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

export default UserManagement;
