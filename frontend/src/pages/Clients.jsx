import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
    getBeneficiaries, createBeneficiary, updateBeneficiary, deleteBeneficiary,
    getStructures, createStructure, updateStructure, deleteStructure,
    getLevels, createLevel, updateLevel, deleteLevel,
    getStructureTree, getStructureChildren
} from '../api';
import {
    Loader2, ChevronRight, ChevronDown, ChevronLeft, Folder, FileText,
    MoreHorizontal, Edit, Trash2, Eye, Plus, Search, Filter, X, Check, AlertCircle, Network
} from 'lucide-react';

// Family Tree Component
const FamilyTreeModal = ({ rootNode, onClose }) => {
    const [treeData, setTreeData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const buildTree = async () => {
            try {
                // Fetch all descendants
                const descendants = await getStructureChildren(rootNode.id);

                // Create a map for easy lookup
                const nodeMap = {};
                // Add root node to map
                nodeMap[rootNode.id] = { ...rootNode, children: [] };

                // Add all descendants to map
                descendants.forEach(node => {
                    nodeMap[node.id] = { ...node, children: [] };
                });

                // Build hierarchy
                const tree = nodeMap[rootNode.id];
                descendants.forEach(node => {
                    if (node.structure && nodeMap[node.structure]) {
                        nodeMap[node.structure].children.push(nodeMap[node.id]);
                    }
                });

                setTreeData(tree);
            } catch (err) {
                console.error("Failed to build tree", err);
            } finally {
                setLoading(false);
            }
        };

        buildTree();
    }, [rootNode]);

    // Premium Color Palette
    const colors = [
        { border: '#3b82f6', bg: '#eff6ff', text: '#1e40af' }, // Blue
        { border: '#10b981', bg: '#ecfdf5', text: '#065f46' }, // Emerald
        { border: '#8b5cf6', bg: '#f5f3ff', text: '#5b21b6' }, // Violet
        { border: '#f59e0b', bg: '#fffbeb', text: '#92400e' }, // Amber
        { border: '#ec4899', bg: '#fdf2f8', text: '#9d174d' }, // Pink
        { border: '#06b6d4', bg: '#ecfeff', text: '#155e75' }, // Cyan
        { border: '#f43f5e', bg: '#fff1f2', text: '#9f1239' }, // Rose
        { border: '#6366f1', bg: '#eef2ff', text: '#3730a3' }, // Indigo
        { border: '#84cc16', bg: '#f7fee7', text: '#3f6212' }, // Lime
        { border: '#14b8a6', bg: '#f0fdfa', text: '#115e59' }, // Teal
    ];

    const getColorForId = (id) => {
        if (!id) return colors[0];
        const index = id % colors.length;
        return colors[index];
    };

    const renderTreeNode = (node) => {
        const colorTheme = getColorForId(node.id);

        return (
            <li key={node.id}>
                <div
                    className="tree-node"
                    style={{
                        borderColor: colorTheme.border,
                        backgroundColor: colorTheme.bg,
                        borderLeftWidth: '4px',
                        borderLeftColor: colorTheme.border
                    }}
                >
                    {node.image && <img src={node.image} alt={node.name} className="node-image" />}
                    <div className="node-content">
                        <div className="node-name" style={{ color: colorTheme.text }}>{node.name}</div>
                        <div className="node-level">{node.level_name}</div>
                    </div>
                </div>
                {node.children && node.children.length > 0 && (
                    <ul>
                        {node.children.map(child => renderTreeNode(child))}
                    </ul>
                )}
            </li>
        );
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content large-modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>شجرة العائلة: {rootNode.name}</h2>
                    <button onClick={onClose} className="modal-close"><X /></button>
                </div>
                <div className="modal-body tree-view-container">
                    {loading ? (
                        <div className="flex justify-center p-8"><Loader2 className="spinner" /></div>
                    ) : (
                        <div className="org-tree">
                            <ul>
                                {treeData && renderTreeNode(treeData)}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const TreeRow = ({ node, level, onToggle, expandedNodes, onEdit, onDelete, onShowTree }) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes[node.id];

    return (
        <>
            <tr className="tree-row">
                <td style={{ paddingRight: `${level * 24 + 12}px` }}> {/* RTL Indentation */}
                    <div className="tree-cell-name">
                        {hasChildren ? (
                            <button
                                onClick={() => onToggle(node.id)}
                                className="tree-toggle"
                            >
                                {isExpanded ? <ChevronDown size={16} /> : <ChevronLeft size={16} />}
                            </button>
                        ) : (
                            <span className="w-6" />
                        )}
                        <span className="font-medium text-primary">{node.name}</span>
                    </div>
                </td>
                <td>
                    {node.level_name && (
                        <span className="badge badge-success text-xs">
                            {node.level_name}
                        </span>
                    )}
                </td>
                <td>
                    <span className="text-secondary text-sm">
                        {node.is_branch ? 'فرع' : 'هيكل رئيسي'}
                    </span>
                </td>
                <td>{node.order}</td>
                <td>
                    <div className="flex items-center gap-2">
                        <button onClick={() => onShowTree(node)} className="action-btn btn-view" title="شجرة العائلة">
                            <Network size={16} />
                        </button>
                        <button onClick={() => onEdit(node)} className="action-btn btn-edit" title="تعديل">
                            <Edit size={16} />
                        </button>
                        <button onClick={() => onDelete(node.id)} className="action-btn btn-delete" title="حذف">
                            <Trash2 size={16} />
                        </button>
                    </div>
                </td>
            </tr>
            {hasChildren && isExpanded && node.children.map(child => (
                <TreeRow
                    key={child.id}
                    node={child}
                    level={level + 1}
                    onToggle={onToggle}
                    expandedNodes={expandedNodes}
                    onEdit={onEdit}
                    onDelete={onDelete}
                    onShowTree={onShowTree}
                />
            ))}
        </>
    );
};

const Clients = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'beneficiaries');
    const [data, setData] = useState([]);
    const [levels, setLevels] = useState([]); // For structure modal
    const [structures, setStructures] = useState([]); // For parent structure selection
    const [loading, setLoading] = useState(false);
    const [expandedNodes, setExpandedNodes] = useState({});

    // Modal & CRUD State
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('create'); // create, edit
    const [selectedItem, setSelectedItem] = useState(null);
    const [formData, setFormData] = useState({});
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    // Tree Modal State
    const [showTreeModal, setShowTreeModal] = useState(false);
    const [treeRootNode, setTreeRootNode] = useState(null);

    useEffect(() => {
        const tab = searchParams.get('tab');
        if (tab) {
            setActiveTab(tab);
        }
    }, [searchParams]);

    useEffect(() => {
        fetchData();
        // Fetch auxiliary data for modals
        if (activeTab === 'structures') {
            fetchLevelsAndStructures();
        }
    }, [activeTab]);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        setSearchParams({ tab });
        setSearchTerm('');
        setError('');
        setSuccess('');
    };

    const fetchLevelsAndStructures = async () => {
        try {
            const [levelsData, structuresData] = await Promise.all([getLevels(), getStructures()]);
            setLevels(levelsData);
            setStructures(structuresData);
        } catch (err) {
            console.error("Failed to fetch auxiliary data", err);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            let result;
            if (activeTab === 'beneficiaries') {
                result = await getBeneficiaries();
            } else if (activeTab === 'structures') {
                result = await getStructureTree();
                // Auto-expand first level
                if (result && result.length > 0) {
                    const initialExpanded = {};
                    result.forEach(node => initialExpanded[node.id] = true);
                    setExpandedNodes(initialExpanded);
                }
            } else if (activeTab === 'levels') {
                result = await getLevels();
            }
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
        setFormData({});
        setShowModal(true);
    };

    const handleEdit = (item) => {
        setModalType('edit');
        setSelectedItem(item);
        setFormData({ ...item });
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('هل أنت متأكد من الحذف؟')) return;

        try {
            if (activeTab === 'beneficiaries') await deleteBeneficiary(id);
            else if (activeTab === 'structures') await deleteStructure(id);
            else if (activeTab === 'levels') await deleteLevel(id);

            setSuccess('تم الحذف بنجاح');
            fetchData();
        } catch (err) {
            setError('فشل الحذف');
        }
    };

    const handleShowTree = (node) => {
        setTreeRootNode(node);
        setShowTreeModal(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Prepare data
            let dataToSend = formData;
            const isMultipart = activeTab === 'beneficiaries' || activeTab === 'structures';

            if (isMultipart) {
                const formDataObj = new FormData();
                Object.keys(formData).forEach(key => {
                    if (key === 'image' && formData[key] instanceof File) {
                        formDataObj.append(key, formData[key]);
                    } else if (key === 'beneficiary' && Array.isArray(formData[key])) {
                        formData[key].forEach(id => formDataObj.append('beneficiary', id));
                    } else if (formData[key] !== null && formData[key] !== undefined) {
                        formDataObj.append(key, formData[key]);
                    }
                });
                dataToSend = formDataObj;
            }

            if (modalType === 'create') {
                if (activeTab === 'beneficiaries') await createBeneficiary(dataToSend);
                else if (activeTab === 'structures') await createStructure(dataToSend);
                else if (activeTab === 'levels') await createLevel(dataToSend);
                setSuccess('تم الإضافة بنجاح');
            } else {
                if (activeTab === 'beneficiaries') await updateBeneficiary(selectedItem.id, dataToSend);
                else if (activeTab === 'structures') await updateStructure(selectedItem.id, dataToSend);
                else if (activeTab === 'levels') await updateLevel(selectedItem.id, dataToSend);
                setSuccess('تم التحديث بنجاح');
            }
            setShowModal(false);
            fetchData();
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || 'فشلت العملية');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFormData({ ...formData, image: e.target.files[0] });
        }
    };

    const toggleNode = (nodeId) => {
        setExpandedNodes(prev => ({
            ...prev,
            [nodeId]: !prev[nodeId]
        }));
    };

    const filteredData = data.filter(item => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (item.name || item.public_name)?.toLowerCase().includes(term) ||
            item.description?.toLowerCase().includes(term);
    });

    const renderContent = () => {
        if (loading && !data.length) {
            return (
                <div className="loading-container">
                    <Loader2 className="spinner text-accent" />
                </div>
            );
        }

        if (!data || data.length === 0) {
            return <div className="empty-state">لا توجد بيانات متاحة.</div>;
        }

        if (activeTab === 'structures') {
            return (
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th style={{ width: '40%' }}>الاسم</th>
                                <th>المستوى</th>
                                <th>النوع</th>
                                <th>الترتيب</th>
                              
                                <th style={{ width: '150px' }}>الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((node) => (
                                <TreeRow
                                    key={node.id}
                                    node={node}
                                    level={0}
                                    onToggle={toggleNode}
                                    expandedNodes={expandedNodes}
                                    onEdit={handleEdit}
                                    onDelete={handleDelete}
                                    onShowTree={handleShowTree}
                                />
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }

        // Table view for Beneficiaries and Levels
        return (
            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>الاسم</th>
                            {activeTab === 'beneficiaries' && (
                                <>
                                    <th>الاسم الخاص</th>
                                    <th>الوصف</th>
                                    <th>الترتيب</th>
                                </>
                            )}
                            {activeTab === 'levels' && <th>الوصف</th>}
                            <th style={{ width: '150px' }}>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredData.map((item) => (
                            <tr key={item.id}>
                                <td className="font-medium">{item.name || item.public_name}</td>
                                {activeTab === 'beneficiaries' && (
                                    <>
                                        <td>{item.pravite_name}</td>
                                        <td>{item.description}</td>
                                        <td>{item.order}</td>
                                    </>
                                )}
                                {activeTab === 'levels' && <td>{item.description}</td>}
                                <td>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => handleEdit(item)} className="action-btn btn-edit" title="تعديل">
                                            <Edit size={16} />
                                        </button>
                                        <button onClick={() => handleDelete(item.id)} className="action-btn btn-delete" title="حذف">
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
                    <h1>إدارة العملاء</h1>
                    <p>إدارة المستفيدين والهياكل والمستويات.</p>
                </div>
                <button onClick={handleCreate} className="btn btn-primary">
                    <Plus size={18} />
                    <span>
                        {activeTab === 'beneficiaries' && 'إضافة مستفيد'}
                        {activeTab === 'structures' && 'إضافة هيكل'}
                        {activeTab === 'levels' && 'إضافة مستوى'}
                    </span>
                </button>
            </header>

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'beneficiaries' ? 'active' : ''}`}
                    onClick={() => handleTabChange('beneficiaries')}
                >
                    المستفيدين
                </button>
                <button
                    className={`tab-btn ${activeTab === 'structures' ? 'active' : ''}`}
                    onClick={() => handleTabChange('structures')}
                >
                    الهياكل التنظيمية
                </button>
                <button
                    className={`tab-btn ${activeTab === 'levels' ? 'active' : ''}`}
                    onClick={() => handleTabChange('levels')}
                >
                    المستويات
                </button>
            </div>

            <div className="card">
                <div className="mb-6 flex justify-between items-center">
                    <div className="search-box">
                        <Search className="search-icon" />
                        <input
                            type="text"
                            placeholder="بحث..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="input-field with-icon"
                        />
                    </div>
                </div>
                {renderContent()}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>
                                {modalType === 'create' ? 'إضافة' : 'تعديل'}
                                {' '}
                                {activeTab === 'beneficiaries' && 'مستفيد'}
                                {activeTab === 'structures' && 'هيكل'}
                                {activeTab === 'levels' && 'مستوى'}
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
                            <div className="form-grid">
                                {activeTab === 'beneficiaries' && (
                                    <>
                                        <div className="input-group">
                                            <label>الاسم العام *</label>
                                            <input
                                                type="text"
                                                required
                                                value={formData.public_name || ''}
                                                onChange={(e) => setFormData({ ...formData, public_name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>الاسم الخاص</label>
                                            <input
                                                type="text"
                                                value={formData.pravite_name || ''}
                                                onChange={(e) => setFormData({ ...formData, pravite_name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>الصورة</label>
                                            <input
                                                type="file"
                                                onChange={handleFileChange}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>الترتيب</label>
                                            <input
                                                type="number"
                                                value={formData.order || ''}
                                                onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group full-width">
                                            <label>الوصف</label>
                                            <textarea
                                                value={formData.description || ''}
                                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                                className="input-field"
                                                rows={2}
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>العنوان الأيمن</label>
                                            <input
                                                type="text"
                                                value={formData.right_address || ''}
                                                onChange={(e) => setFormData({ ...formData, right_address: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>العنوان الأيسر</label>
                                            <input
                                                type="text"
                                                value={formData.left_address || ''}
                                                onChange={(e) => setFormData({ ...formData, left_address: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                    </>
                                )}

                                {activeTab === 'structures' && (
                                    <>
                                        <div className="input-group">
                                            <label>الاسم *</label>
                                            <input
                                                type="text"
                                                required
                                                value={formData.name || ''}
                                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>المستوى</label>
                                            <select
                                                value={formData.level || ''}
                                                onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                                                className="input-field"
                                            >
                                                <option value="">اختر المستوى</option>
                                                {levels.map(l => (
                                                    <option key={l.id} value={l.id}>{l.name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="input-group">
                                            <label>الأب</label>
                                            <select
                                                value={formData.structure || ''}
                                                onChange={(e) => setFormData({ ...formData, structure: e.target.value })}
                                                className="input-field"
                                            >
                                                <option value="">بدون أب (رئيسي)</option>
                                                {structures.map(s => (
                                                    <option key={s.id} value={s.id}>{s.name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="input-group">
                                            <label>الصورة</label>
                                            <input
                                                type="file"
                                                onChange={handleFileChange}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>الترتيب</label>
                                            <input
                                                type="number"
                                                value={formData.order || ''}
                                                onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group full-width">
                                            <label>الوصف</label>
                                            <textarea
                                                value={formData.description || ''}
                                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                                className="input-field"
                                                rows={2}
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>العنوان الأيمن</label>
                                            <input
                                                type="text"
                                                value={formData.right_address || ''}
                                                onChange={(e) => setFormData({ ...formData, right_address: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>العنوان الأيسر</label>
                                            <input
                                                type="text"
                                                value={formData.left_address || ''}
                                                onChange={(e) => setFormData({ ...formData, left_address: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="checkbox-group">
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={formData.is_branch || false}
                                                    onChange={(e) => setFormData({ ...formData, is_branch: e.target.checked })}
                                                />
                                                <span>فرع؟</span>
                                            </label>
                                        </div>
                                    </>
                                )}

                                {activeTab === 'levels' && (
                                    <>
                                        <div className="input-group">
                                            <label>الاسم *</label>
                                            <input
                                                type="text"
                                                required
                                                value={formData.name || ''}
                                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                className="input-field"
                                            />
                                        </div>
                                        <div className="input-group">
                                            <label>الوصف</label>
                                            <textarea
                                                value={formData.description || ''}
                                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                                className="input-field"
                                                rows={3}
                                            />
                                        </div>
                                    </>
                                )}
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

            {/* Tree Modal */}
            {showTreeModal && treeRootNode && (
                <FamilyTreeModal
                    rootNode={treeRootNode}
                    onClose={() => setShowTreeModal(false)}
                />
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

export default Clients;
