export function getCurrentUser() {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}

export function saveCurrentUser(user) {
  localStorage.setItem("user", JSON.stringify(user));
}

export function clearCurrentUser() {
  localStorage.removeItem("user");
}

export function isAdmin(user) {
  return user?.role === "admin";
}

export function hasPermission(user, permissionKey) {
  return Boolean(user?.permissions?.[permissionKey]);
}

export function canUpload(user) {
  return hasPermission(user, "can_upload");
}

export function canPredict(user) {
  return hasPermission(user, "can_predict");
}

export function canExport(user) {
  return hasPermission(user, "can_export");
}

export function canViewAllRecords(user) {
  return hasPermission(user, "can_view_all_records");
}

export function canManageUsers(user) {
  return hasPermission(user, "can_manage_users");
}

export function canViewUploadRecords(user) {
  // 管理员强制可见，避免因为字段漏传导致管理员也看不到
  if (isAdmin(user)) return true;
  return hasPermission(user, "can_view_upload_records");
}

export function getVisibleSidebarItems(items, user) {
  return items.filter((item) => {
    if (item.path === "/upload-records" && !canViewUploadRecords(user)) return false;
    return true;
  });
}

// export function getCurrentUser() {
//   try {
//     const raw = localStorage.getItem("user");
//     return raw ? JSON.parse(raw) : null;
//   } catch (error) {
//     return null;
//   }
// }

// export function saveCurrentUser(user) {
//   localStorage.setItem("user", JSON.stringify(user));
// }

// export function clearCurrentUser() {
//   localStorage.removeItem("user");
// }

// export function isAdmin(user) {
//   return user?.role === "admin";
// }

// export function hasPermission(user, permissionKey) {
//   return Boolean(user?.permissions?.[permissionKey]);
// }

// export function canUpload(user) {
//   return hasPermission(user, "can_upload");
// }

// export function canPredict(user) {
//   return hasPermission(user, "can_predict");
// }

// export function canExport(user) {
//   return hasPermission(user, "can_export");
// }

// export function canViewAllRecords(user) {
//   return hasPermission(user, "can_view_all_records");
// }

// export function canManageUsers(user) {
//   return hasPermission(user, "can_manage_users");
// }

// export function canViewUploadRecords(user) {
//   return hasPermission(user, "can_view_upload_records");
// }

// export function getVisibleSidebarItems(items, user) {
//   return items.filter((item) => {
//     if (item.path === "/upload-records" && !canViewUploadRecords(user)) return false;
//     return true;
//   });
// }
// .....................
// export function getCurrentUser() {
//   try {
//     const raw = localStorage.getItem("user");
//     return raw ? JSON.parse(raw) : null;
//   } catch (error) {
//     return null;
//   }
// }

// export function saveCurrentUser(user) {
//   localStorage.setItem("user", JSON.stringify(user));
// }

// export function clearCurrentUser() {
//   localStorage.removeItem("user");
// }

// export function isAdmin(user) {
//   return user?.role === "admin";
// }

// export function hasPermission(user, permissionKey) {
//   return Boolean(user?.permissions?.[permissionKey]);
// }

// export function canUpload(user) {
//   return hasPermission(user, "can_upload");
// }

// export function canPredict(user) {
//   return hasPermission(user, "can_predict");
// }

// export function canExport(user) {
//   return hasPermission(user, "can_export");
// }

// export function canViewAllRecords(user) {
//   return hasPermission(user, "can_view_all_records");
// }

// export function canManageUsers(user) {
//   return hasPermission(user, "can_manage_users");
// }

// export function getVisibleSidebarItems(items, user) {
//   return items.filter((item) => {
//     if (item.path === "/upload" && !canUpload(user)) return false;
//     return true;
//   });
// }