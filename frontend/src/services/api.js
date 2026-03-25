import { getCurrentUser } from "../utils/auth";
// 这里先写成占位版，后面你把 baseURL 改成自己的 Python 后端地址
const BASE_URL = "http://localhost:5000/api";

export async function loginUser(payload) {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Login failed");
  }

  return result;
}
// export async function loginUser(payload) {
//   // 后端预留:
//   // POST /api/login
//   // body: { username, password }
//   return Promise.resolve({
//     success: true,
//     token: "demo-token",
//     user: {
//       user_id: payload.username === "admin" ? 1 : 2,
//       username: payload.username,
//       email: payload.username === "admin" ? "admin@example.com" : "staff1@example.com",
//       role: payload.username === "admin" ? "admin" : "staff",
//       is_active: true,
//       permissions:
//         payload.username === "admin"
//           ? {
//               can_upload: true,
//               can_predict: true,
//               can_export: true,
//               can_view_all_records: true,
//               can_manage_users: true,
//             }
//           : {
//               can_upload: false,
//               can_predict: true,
//               can_export: false,
//               can_view_all_records: false,
//               can_manage_users: false,
//             },
//     },
//   });
// }
export async function fetchUsers() {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to fetch users");
  }

  return result.data;
}
// export async function fetchUsers() {
//   // 后面接后端:
//   // GET /api/users
//   return Promise.resolve([
//     {
//       user_id: 1,
//       username: "admin",
//       email: "admin@example.com",
//       role: "admin",
//       is_active: true,
//       can_upload: true,
//       can_predict: true,
//       can_export: true,
//       can_view_all_records: true,
//       can_manage_users: true,
//     },
//     {
//       user_id: 2,
//       username: "staff1",
//       email: "staff1@example.com",
//       role: "staff",
//       is_active: true,
//       can_upload: false,
//       can_predict: true,
//       can_export: false,
//       can_view_all_records: false,
//       can_manage_users: false,
//     },
//     {
//       user_id: 3,
//       username: "staff2",
//       email: "staff2@example.com",
//       role: "staff",
//       is_active: false,
//       can_upload: true,
//       can_predict: true,
//       can_export: false,
//       can_view_all_records: false,
//       can_manage_users: false,
//     },
//   ]);
// }
export async function updateUserPermissions(userId, payload) {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/users/${userId}/permissions`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
      ...payload,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to update permissions");
  }

  return result.data;
}
// export async function updateUserPermissions(userId, payload) {
//   // 后面接后端:
//   // PUT /api/users/:id/permissions
//   return Promise.resolve({
//     success: true,
//     user_id: userId,
//     ...payload,
//   });
// }


export async function fetchProducts() {
  // 后端预留:
  // GET /api/products
  return Promise.resolve([]);
}

export async function fetchSalesHistory(stockCode = "") {
  const url = stockCode
    ? `${BASE_URL}/sales-history?stock_code=${encodeURIComponent(stockCode)}`
    : `${BASE_URL}/sales-history`;

  const response = await fetch(url);
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to fetch sales history");
  }

  return result.data;
}
// export async function fetchSalesHistory() {
//   // 后端预留:
//   // GET /api/sales-history?stock_code=xxx
//   return Promise.resolve([]);
// }

export async function runPrediction(payload) {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/predict-runtime`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
      ...payload,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Prediction failed");
  }

  return result.data;
}

// export async function runPrediction(payload) {
//   const currentUser = getCurrentUser();

//   const response = await fetch(`${BASE_URL}/predict`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       currentUser,
//       ...payload,
//     }),
//   });

//   const result = await response.json();

//   if (!response.ok) {
//     throw new Error(result.message || "Prediction failed");
//   }

//   return result.data;
// }
// export async function runPrediction(payload) {
//   // 后端预留:
//   // POST /api/predict
//   // body:
//   // {
//   //   productType,
//   //   stockCode,
//   //   startDate,
//   //   endDate
//   // }
//   //
//   // 这里后端内部再去:
//   // 1. 查 MySQL
//   // 2. 做预处理
//   // 3. 调用 GRU + XGBoost
//   // 4. 返回预测结果
//   return Promise.resolve({
//     predictedSummary: "8.92 kg",
//     list: [
//       { date: "2023-07-01", demand: 8.6 },
//       { date: "2023-07-02", demand: 8.1 },
//       { date: "2023-07-03", demand: 7.9 },
//       { date: "2023-07-04", demand: 8.4 },
//       { date: "2023-07-05", demand: 8.8 },
//       { date: "2023-07-06", demand: 9.3 },
//       { date: "2023-07-07", demand: 8.9 },
//     ],
//   });
// }

export async function fetchForecastRecords() {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/forecast-history`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to fetch forecast records");
  }

  return result.data;
}
// export async function fetchForecastRecords() {
//   // 后端预留:
//   // GET /api/forecast-history
//   return Promise.resolve([]);
// }
// export async function uploadSalesFile(file) {
//   const currentUser = getCurrentUser();
//   const formData = new FormData();

//   formData.append("file", file);
//   formData.append("currentUser", JSON.stringify(currentUser));

//   const response = await fetch(`${BASE_URL}/upload-sales`, {
//     method: "POST",
//     body: formData,
//   });

//   const result = await response.json();

//   if (!response.ok) {
//     throw new Error(result.message || "Upload failed");
//   }

//   return result.data;
// }
// export async function uploadSalesFile(formData) {
//   // 后端预留:
//   // POST /api/upload-sales
//   return Promise.resolve({ success: true });
// }


// 新增
export async function uploadSalesFile(file, maxRows = null) {
  const currentUser = getCurrentUser();
  const formData = new FormData();

  formData.append("file", file);
  formData.append("currentUser", JSON.stringify(currentUser));

  if (maxRows !== null && maxRows !== undefined && maxRows !== "") {
    formData.append("maxRows", String(maxRows));
  }

  const response = await fetch(`${BASE_URL}/upload-sales`, {
    method: "POST",
    body: formData,
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Upload failed");
  }

  return result.data;
}

export async function fetchUploadRecords() {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/upload-records`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to fetch upload records");
  }

  return result.data;
}

export async function createStaffAccount(payload) {
  const currentUser = getCurrentUser();

  const response = await fetch(`${BASE_URL}/users/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      currentUser,
      ...payload,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.message || "Failed to create staff account");
  }

  return result.data;
}

export { BASE_URL };
