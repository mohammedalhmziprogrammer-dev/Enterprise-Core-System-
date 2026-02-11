import axios from "axios";

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to add the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication
export const login = async (username, password) => {
  const response = await api.post("/token/", { username, password });
  if (response.data.access) {
    localStorage.setItem("access_token", response.data.access);
    localStorage.setItem("refresh_token", response.data.refresh);
  }
  return response.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// ============ USERS API ============
export const getUsers = async (params = {}) => {
  const response = await api.get("/users/users/", { params });
  return response.data;
};

export const getUser = async (id) => {
  const response = await api.get(`/users/users/${id}/`);
  return response.data;
};

export const createUser = async (userData) => {
  const response = await api.post("/users/users/", userData);
  return response.data;
};

export const updateUser = async (id, userData) => {
  const response = await api.patch(`/users/users/${id}/`, userData);
  return response.data;
};

export const deleteUser = async (id) => {
  const response = await api.delete(`/users/users/${id}/`);
  return response.data;
};

export const changePassword = async (
  oldPassword,
  newPassword,
  confirmPassword
) => {
  const response = await api.post("/users/users/change_password/", {
    old_password: oldPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
  });
  return response.data;
};

export const resetUserPassword = async (userId, newPassword) => {
  const response = await api.post(`/users/users/${userId}/reset_password/`, {
    new_password: newPassword,
  });
  return response.data;
};

export const assignUserRoles = async (userId, roleIds) => {
  const response = await api.post(`/users/users/${userId}/assign_roles/`, {
    role_ids: roleIds,
  });
  return response.data;
};

export const assignUserGroups = async (userId, groupIds) => {
  const response = await api.post(`/users/users/${userId}/assign_groups/`, {
    group_ids: groupIds,
  });
  return response.data;
};

export const getUserPermissions = async (userId) => {
  const response = await api.get(`/users/users/${userId}/permissions/`);
  return response.data;
};

export const assignUserStructures = async (userId, structureIds) => {
  const response = await api.post(`/users/users/${userId}/assign_structures/`, {
    structure_ids: structureIds,
  });
  return response.data;
};


export const getUserStatistics = async () => {
  const response = await api.get("/users/users/statistics/");
  return response.data;
};

export const getUserSubordinates = async (userId) => {
  const response = await api.get(`/users/users/${userId}/subordinates_list/`);
  return response.data;
};

// ============ ROLES API ============
export const getRoles = async () => {
  const response = await api.get("/users/role/");
  return response.data;
};

export const getRole = async (id) => {
  const response = await api.get(`/users/role/${id}/`);
  return response.data;
};

export const createRole = async (roleData) => {
  const response = await api.post("/users/role/", roleData);
  return response.data;
};

export const updateRole = async (id, roleData) => {
  const response = await api.patch(`/users/role/${id}/`, roleData);
  return response.data;
};

export const deleteRole = async (id) => {
  const response = await api.delete(`/users/role/${id}/`);
  return response.data;
};

export const assignRolePermissions = async (roleId, permissionIds) => {
  const response = await api.post(`/users/role/${roleId}/assign_permissions/`, {
    permission_ids: permissionIds,
  });
  return response.data;
};

export const getRoleUsers = async (roleId) => {
  const response = await api.get(`/users/role/${roleId}/users/`);
  return response.data;
};

export const assignRoleCodingCategories = async (roleId, categoryIds) => {
  const response = await api.post(
    `/users/role/${roleId}/assign_coding_categories/`,
    {
      category_ids: categoryIds,
    }
  );
  return response.data;
};

export const assignRoleCodings = async (roleId, codingIds) => {
  const response = await api.post(`/users/role/${roleId}/assign_codings/`, {
    coding_ids: codingIds,
  });
  return response.data;
};

// ============ GROUPS API ============
export const getGroups = async () => {
  const response = await api.get("/users/group/");
  return response.data;
};

export const getGroup = async (id) => {
  const response = await api.get(`/users/group/${id}/`);
  return response.data;
};

export const createGroup = async (groupData) => {
  const response = await api.post("/users/group/", groupData);
  return response.data;
};

export const updateGroup = async (id, groupData) => {
  const response = await api.patch(`/users/group/${id}/`, groupData);
  return response.data;
};

export const deleteGroup = async (id) => {
  const response = await api.delete(`/users/group/${id}/`);
  return response.data;
};

export const getGroupPermissions = async (groupId) => {
  const response = await api.get(`/users/group/${groupId}/group_per/`);
  return response.data;
};

export const assignGroupPermissions = async (groupId, permissionIds) => {
  const response = await api.post(
    `/users/group/${groupId}/assign_permissions/`,
    {
      permission_ids: permissionIds,
    }
  );
  return response.data;
};

export const getGroupUsers = async (groupId) => {
  const response = await api.get(`/users/group/${groupId}/users/`);
  return response.data;
};

export const getGroupStatistics = async () => {
  const response = await api.get("/users/group/statistics/");
  return response.data;
};

// ============ PERMISSIONS API ============
export const getPermissions = async (params = {}) => {
  const response = await api.get("/users/permissions/", { params });
  return response.data;
};

export const getPermission = async (id) => {
  const response = await api.get(`/users/permissions/${id}/`);
  return response.data;
};

export const getPermissionsByApp = async () => {
  const response = await api.get("/users/permissions/by_app/");
  return response.data;
};

export const getPermissionsByModel = async () => {
  const response = await api.get("/users/permissions/by_model/");
  return response.data;
};

// ============ CLIENTS API ============
// ============ CLIENTS API ============
export const getBeneficiaries = async () => {
  const response = await api.get("/clients/beneficiaries/");
  return response.data;
};

export const createBeneficiary = async (data) => {
  const config = data instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {};
  const response = await api.post("/clients/beneficiaries/", data, config);
  return response.data;
};

export const updateBeneficiary = async (id, data) => {
  const config = data instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {};
  const response = await api.patch(`/clients/beneficiaries/${id}/`, data, config);
  return response.data;
};

export const deleteBeneficiary = async (id) => {
  const response = await api.delete(`/clients/beneficiaries/${id}/`);
  return response.data;
};

export const getStructures = async () => {
  const response = await api.get("/clients/structures/");
  return response.data;
};

export const createStructure = async (data) => {
  const config = data instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {};
  const response = await api.post("/clients/structures/", data, config);
  return response.data;
};

export const updateStructure = async (id, data) => {
  const config = data instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {};
  const response = await api.patch(`/clients/structures/${id}/`, data, config);
  return response.data;
};

export const deleteStructure = async (id) => {
  const response = await api.delete(`/clients/structures/${id}/`);
  return response.data;
};

export const getLevels = async () => {
  const response = await api.get("/clients/levels/");
  return response.data;
};

export const createLevel = async (data) => {
  const response = await api.post("/clients/levels/", data);
  return response.data;
};

export const updateLevel = async (id, data) => {
  const response = await api.patch(`/clients/levels/${id}/`, data);
  return response.data;
};

export const deleteLevel = async (id) => {
  const response = await api.delete(`/clients/levels/${id}/`);
  return response.data;
};

export const getStructureTree = async () => {
  const response = await api.get("/clients/structures/tree/");
  return response.data;
};

export const getStructureChildren = async (id) => {
  const response = await api.get(`/clients/structures/${id}/children/`);
  return response.data;
};

export const getStructureParent = async (id) => {
  const response = await api.get(`/clients/structures/${id}/parent/`);
  return response.data;
};

// ============ APPS API ============
export const getApps = async () => {
  const response = await api.get("/apps/apps/");
  return response.data;
};

export const getAppTypes = async () => {
  const response = await api.get("/apps/types/");
  return response.data;
};

export const getAppVersions = async () => {
  const response = await api.get("/apps/versions/");
  return response.data;
};

// ============ CODINGS API ============
export const getCodingCategories = async () => {
  const response = await api.get("/codings/categories/");
  return response.data;
};

export const getCodings = async () => {
  const response = await api.get("/codings/codings/");
  return response.data;
};

// ============ RELEASES API ============
export const getReleases = async () => {
  const response = await api.get("/releases/releases/");
  return response.data;
};

export default api;
