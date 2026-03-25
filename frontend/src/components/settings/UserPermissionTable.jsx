import React, { useEffect, useState } from "react";
import { fetchUsers, updateUserPermissions } from "../../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function UserPermissionTable() {
  const [users, setUsers] = useState([]);
  const [savingId, setSavingId] = useState(null);

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch (error) {
        console.error(error);
      }
    }
    loadUsers();
  }, []);

  function handleToggle(userId, field) {
    setUsers((prev) =>
      prev.map((user) =>
        user.user_id === userId ? { ...user, [field]: !user[field] } : user
      )
    );
  }

  async function handleSave(user) {
    if (user.role !== "staff") return;

    try {
      setSavingId(user.user_id);

      await updateUserPermissions(user.user_id, {
        can_upload: user.can_upload,
        can_predict: user.can_predict,
        can_export: user.can_export,
        can_view_all_records: user.can_view_all_records,
        can_view_upload_records: user.can_view_upload_records,
        is_active: user.is_active,
      });
    } catch (error) {
      console.error(error);
      alert(error.message);
    } finally {
      setSavingId(null);
    }
  }

  return (
    <Card className="rounded-3xl border-0 shadow-md bg-white/85">
      <CardHeader>
        <CardTitle>User Permission Management</CardTitle>
        <CardDescription>
          Only administrators can see and modify ordinary staff permissions.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {users.map((user) => {
          const isAdminRow = user.role === "admin";

          return (
            <div key={user.user_id} className="rounded-3xl border bg-slate-50 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-lg font-semibold">{user.username}</h3>
                    <Badge className="rounded-full">{user.role}</Badge>
                    <Badge variant={user.is_active ? "default" : "secondary"} className="rounded-full">
                      {user.is_active ? "active" : "inactive"}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">{user.email}</p>
                </div>

                {!isAdminRow && (
                  <Button
                    className="rounded-2xl"
                    onClick={() => handleSave(user)}
                    disabled={savingId === user.user_id}
                  >
                    {savingId === user.user_id ? "Saving..." : "Save Changes"}
                  </Button>
                )}
              </div>

              <div className="grid sm:grid-cols-2 xl:grid-cols-6 gap-4 mt-5">
                <PermissionToggle
                  label="Upload Data"
                  checked={user.can_upload}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "can_upload")}
                />
                <PermissionToggle
                  label="Run Prediction"
                  checked={user.can_predict}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "can_predict")}
                />
                <PermissionToggle
                  label="Export Result"
                  checked={user.can_export}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "can_export")}
                />
                <PermissionToggle
                  label="View All Records"
                  checked={user.can_view_all_records}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "can_view_all_records")}
                />
                <PermissionToggle
                  label="View Upload Records"
                  checked={user.can_view_upload_records}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "can_view_upload_records")}
                />
                <PermissionToggle
                  label="Account Active"
                  checked={user.is_active}
                  disabled={isAdminRow}
                  onChange={() => handleToggle(user.user_id, "is_active")}
                />
              </div>

              {isAdminRow && (
                <p className="text-sm text-slate-500 mt-4">
                  Administrator permissions are fixed and cannot be edited here.
                </p>
              )}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

function PermissionToggle({ label, checked, disabled, onChange }) {
  return (
    <label className="rounded-2xl border bg-white p-4 flex items-center justify-between gap-3 cursor-pointer">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={onChange}
        className="h-4 w-4"
      />
    </label>
  );
}
// import React, { useEffect, useState } from "react";
// import { fetchUsers, updateUserPermissions } from "../../services/api";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Badge } from "@/components/ui/badge";

// export default function UserPermissionTable() {
//   const [users, setUsers] = useState([]);
//   const [savingId, setSavingId] = useState(null);

//   useEffect(() => {
//     async function loadUsers() {
//       const data = await fetchUsers();
//       setUsers(data);
//     }
//     loadUsers();
//   }, []);

//   function handleToggle(userId, field) {
//     setUsers((prev) =>
//       prev.map((user) =>
//         user.user_id === userId ? { ...user, [field]: !user[field] } : user
//       )
//     );
//   }

//   async function handleSave(user) {
//     if (user.role !== "staff") return;

//     setSavingId(user.user_id);
//     await updateUserPermissions(user.user_id, {
//       can_upload: user.can_upload,
//       can_predict: user.can_predict,
//       can_export: user.can_export,
//       can_view_all_records: user.can_view_all_records,
//       is_active: user.is_active,
//     });
//     setSavingId(null);
//   }

//   return (
//     <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//       <CardHeader>
//         <CardTitle>User Permission Management</CardTitle>
//         <CardDescription>
//           Only administrators can see and modify ordinary staff permissions.
//         </CardDescription>
//       </CardHeader>

//       <CardContent className="space-y-4">
//         {users.map((user) => {
//           const isAdminRow = user.role === "admin";

//           return (
//             <div key={user.user_id} className="rounded-3xl border bg-slate-50 p-5">
//               <div className="flex flex-wrap items-start justify-between gap-3">
//                 <div>
//                   <div className="flex items-center gap-2 flex-wrap">
//                     <h3 className="text-lg font-semibold">{user.username}</h3>
//                     <Badge className="rounded-full">{user.role}</Badge>
//                     <Badge variant={user.is_active ? "default" : "secondary"} className="rounded-full">
//                       {user.is_active ? "active" : "inactive"}
//                     </Badge>
//                   </div>
//                   <p className="text-sm text-slate-500 mt-1">{user.email}</p>
//                 </div>

//                 {!isAdminRow && (
//                   <Button
//                     className="rounded-2xl"
//                     onClick={() => handleSave(user)}
//                     disabled={savingId === user.user_id}
//                   >
//                     {savingId === user.user_id ? "Saving..." : "Save Changes"}
//                   </Button>
//                 )}
//               </div>

//               <div className="grid sm:grid-cols-2 xl:grid-cols-5 gap-4 mt-5">
//                 <PermissionToggle
//                   label="Upload Data"
//                   checked={user.can_upload}
//                   disabled={isAdminRow}
//                   onChange={() => handleToggle(user.user_id, "can_upload")}
//                 />
//                 <PermissionToggle
//                   label="Run Prediction"
//                   checked={user.can_predict}
//                   disabled={isAdminRow}
//                   onChange={() => handleToggle(user.user_id, "can_predict")}
//                 />
//                 <PermissionToggle
//                   label="Export Result"
//                   checked={user.can_export}
//                   disabled={isAdminRow}
//                   onChange={() => handleToggle(user.user_id, "can_export")}
//                 />
//                 <PermissionToggle
//                   label="View All Records"
//                   checked={user.can_view_all_records}
//                   disabled={isAdminRow}
//                   onChange={() => handleToggle(user.user_id, "can_view_all_records")}
//                 />
//                 <PermissionToggle
//                   label="Account Active"
//                   checked={user.is_active}
//                   disabled={isAdminRow}
//                   onChange={() => handleToggle(user.user_id, "is_active")}
//                 />
//               </div>

//               {isAdminRow && (
//                 <p className="text-sm text-slate-500 mt-4">
//                   Administrator permissions are fixed and cannot be edited here.
//                 </p>
//               )}
//             </div>
//           );
//         })}
//       </CardContent>
//     </Card>
//   );
// }

// function PermissionToggle({ label, checked, disabled, onChange }) {
//   return (
//     <label className="rounded-2xl border bg-white p-4 flex items-center justify-between gap-3 cursor-pointer">
//       <span className="text-sm font-medium text-slate-700">{label}</span>
//       <input
//         type="checkbox"
//         checked={checked}
//         disabled={disabled}
//         onChange={onChange}
//         className="h-4 w-4"
//       />
//     </label>
//   );
// }