import React, { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser } from '../api';
import { Loader2, Search, Plus, Edit, Trash2, Eye, MoreHorizontal, Check, X, AlertCircle } from 'lucide-react';

const Users = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('create');
    const [selectedUser, setSelectedUser] = useState(null);
    const [formData, setFormData] = useState({});
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const result = await getUsers();
            setData(result);
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('فشل تحميل البيانات');
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = () => {
        setModalType('create');
        setFormData({
            username: '',
            email: '',
            password: '',
            first_name: '',
            last_name: '',
            is_active: true,
            phone: '',
           
        });
        setShowModal(true);
    };

    const handleEdit = (user) => {
        setModalType('edit');
        setSelectedUser(user);
        setFormData({
            first_name: user.first_name,
            last_name: user.last_name,
            email: user.email,
            is_active: user.is_active,
            phone: user.phone
        });
        setShowModal(true);
    };

    const handleDelete = async (userId) => {
        if (!window.confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return;

        try {
            await deleteUser(userId);
            setSuccess('تم حذف المستخدم بنجاح');
            fetchData();
        } catch (err) {
            setError('فشل حذف المستخدم');
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
            } else {
                await updateUser(selectedUser.id, formData);
                setSuccess('تم تحديث المستخدم بنجاح');
            }
            setShowModal(false);
            fetchData();
        } catch (err) {
            setError(err.response?.data?.detail || 'فشلت العملية');
        } finally {
            setLoading(false);
        }
    };

    const filteredData = data.filter(user =>
        user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.last_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const renderTable = () => {
        if (loading && !data.length) {
            return (
                <div className="loading-container">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (filteredData.length === 0) {
            return <div className="empty-state">لا يوجد مستخدمين.</div>;
        }

        return (
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>اسم المستخدم</th>
                            <th>الاسم الكامل</th>
                            <th>البريد الإلكتروني</th>
                            <th>الحالة</th>
                            <th>الهاتف</th>
                            <th> تاريخ الانضمام</th>
                            <th style={{ width: '120px' }}>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredData.map((user) => (
                            <tr key={user.id}>
                                <td className="font-medium">{user.username}</td>
                                <td>{`${user.first_name || ''} ${user.last_name || ''}`}</td>
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
                                <td>{user.phone}</td>
                                <td className="text-secondary text-sm">
                                    {user.date_joined ? new Date(user.date_joined).toLocaleDateString('ar-SA') : '-'}
                                </td>
                                <td>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => handleEdit(user)} className="action-btn btn-edit" title="تعديل">
                                            <Edit size={16} />
                                        </button>
                                        <button onClick={() => handleDelete(user.id)} className="action-btn btn-delete" title="حذف">
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
                    <h1>قائمة المستخدمين</h1>
                    <p>إدارة المستخدمين وصلاحياتهم.</p>
                </div>
                <button onClick={handleCreate} className="btn btn-primary">
                    <Plus size={18} />
                    <span>مستخدم جديد</span>
                </button>
            </header>

            <div className="card">
                <div className="mb-6 flex justify-between items-center">
                    <div className="search-box">
                        <Search className="search-icon" />
                        <input
                            type="text"
                            placeholder="بحث عن مستخدم..."
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
                            <h2>{modalType === 'create' ? 'إضافة مستخدم' : 'تعديل مستخدم'}</h2>
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
                            <div className="form-grid">
                                {modalType === 'create' && (
                                    <>
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
                                    </>
                                )}
                                <div className="input-group">
                                    <label>الاسم الأول</label>
                                    <input
                                        type="text"
                                        value={formData.first_name || ''}
                                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="input-group">
                                    <label>الاسم الأخير</label>
                                    <input
                                        type="text"
                                        value={formData.last_name || ''}
                                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="input-group">
                                    <label>البريد الإلكتروني</label>
                                    <input
                                        type="email"
                                        value={formData.email || ''}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        className="input-field"
                                    />
                                </div>
                                  <div className="input-group">
                                    <label> الهاتف</label>
                                    <input
                                        type="number"
                                        value={formData.phone || ''}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        className="input-field"
                                    />
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
                               
                            </div>

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

export default Users;
