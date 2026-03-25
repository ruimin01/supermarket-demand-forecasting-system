import React from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import UserPermissionTable from "../components/settings/UserPermissionTable";
import CreateStaffAccountForm from "../components/settings/CreateStaffAccountForm";
import { sidebarItems } from "../data/mockData";
import { BASE_URL } from "../services/api";
import {
  getCurrentUser,
  canManageUsers,
  canUpload,
  canPredict,
  canExport,
  canViewAllRecords,
  canViewUploadRecords,
  getVisibleSidebarItems,
} from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Settings Page" subtitle="Account settings, system settings, and permission management" />

          <div className="grid xl:grid-cols-2 gap-6">
            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>Basic information of the currently logged-in user.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <InfoRow label="Username" value={user?.username || "Unknown"} />
                <InfoRow label="Email" value={user?.email || "Unknown"} />
                <InfoRow label="Role" value={user?.role || "Unknown"} />
                <InfoRow label="Account Status" value={user?.is_active ? "Active" : "Inactive"} />
                <Button variant="outline" className="rounded-2xl">
                  Change Password
                </Button>
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>System Settings</CardTitle>
                <CardDescription>Important runtime configuration used by the frontend.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <InfoRow label="Backend API Base URL" value={BASE_URL} />
                <InfoRow label="Database Type" value="MySQL" />
                <InfoRow label="Prediction Engine" value="GRU + XGBoost" />
                <InfoRow label="Default Forecast Window" value="7 days" />
                <InfoRow label="Default Export Format" value="CSV" />
              </CardContent>
            </Card>
          </div>

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>My Access Scope</CardTitle>
              <CardDescription>This block tells the user what functions are currently available.</CardDescription>
            </CardHeader>
            <CardContent className="grid sm:grid-cols-2 xl:grid-cols-6 gap-4">
              <PermissionStatusCard title="Upload Data" enabled={canUpload(user)} />
              <PermissionStatusCard title="Run Prediction" enabled={canPredict(user)} />
              <PermissionStatusCard title="Export Result" enabled={canExport(user)} />
              <PermissionStatusCard title="View All Records" enabled={canViewAllRecords(user)} />
              <PermissionStatusCard title="Manage Users" enabled={canManageUsers(user)} />
              <PermissionStatusCard title="View Upload Records" enabled={canViewUploadRecords(user)} />
            </CardContent>
          </Card>

          {canManageUsers(user) && (
            <>
              <CreateStaffAccountForm />
              <UserPermissionTable />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="rounded-2xl border bg-slate-50 p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-base font-medium mt-1 break-all">{value}</p>
    </div>
  );
}

function PermissionStatusCard({ title, enabled }) {
  return (
    <div className="rounded-2xl border bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-medium text-slate-700">{title}</p>
        <Badge variant={enabled ? "default" : "secondary"} className="rounded-full">
          {enabled ? "Enabled" : "Disabled"}
        </Badge>
      </div>
    </div>
  );
}
// import React from "react";
// import Sidebar from "../components/layout/Sidebar";
// import TopBar from "../components/layout/TopBar";
// import UserPermissionTable from "../components/settings/UserPermissionTable";
// import { sidebarItems } from "../data/mockData";
// import { BASE_URL } from "../services/api";
// import {
//   getCurrentUser,
//   canManageUsers,
//   canUpload,
//   canPredict,
//   canExport,
//   canViewAllRecords,
//   getVisibleSidebarItems,
// } from "../utils/auth";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Badge } from "@/components/ui/badge";
// import { Button } from "@/components/ui/button";

// export default function SettingsPage() {
//   const user = getCurrentUser();
//   const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar title="Settings Page" subtitle="Account settings, system settings, and permission management" />

//           <div className="grid xl:grid-cols-2 gap-6">
//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Account Settings</CardTitle>
//                 <CardDescription>Basic information of the currently logged-in user.</CardDescription>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 <InfoRow label="Username" value={user?.username || "Unknown"} />
//                 <InfoRow label="Email" value={user?.email || "Unknown"} />
//                 <InfoRow label="Role" value={user?.role || "Unknown"} />
//                 <InfoRow label="Account Status" value={user?.is_active ? "Active" : "Inactive"} />
//                 <Button variant="outline" className="rounded-2xl">
//                   Change Password
//                 </Button>
//               </CardContent>
//             </Card>

//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>System Settings</CardTitle>
//                 <CardDescription>Important runtime configuration used by the frontend.</CardDescription>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 <InfoRow label="Backend API Base URL" value={BASE_URL} />
//                 <InfoRow label="Database Type" value="MySQL" />
//                 <InfoRow label="Prediction Engine" value="GRU + XGBoost" />
//                 <InfoRow label="Default Forecast Window" value="7 days" />
//                 <InfoRow label="Default Export Format" value="CSV" />
//               </CardContent>
//             </Card>
//           </div>

//           <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//             <CardHeader>
//               <CardTitle>My Access Scope</CardTitle>
//               <CardDescription>This block tells the user what functions are currently available.</CardDescription>
//             </CardHeader>
//             <CardContent className="grid sm:grid-cols-2 xl:grid-cols-5 gap-4">
//               <PermissionStatusCard title="Upload Data" enabled={canUpload(user)} />
//               <PermissionStatusCard title="Run Prediction" enabled={canPredict(user)} />
//               <PermissionStatusCard title="Export Result" enabled={canExport(user)} />
//               <PermissionStatusCard title="View All Records" enabled={canViewAllRecords(user)} />
//               <PermissionStatusCard title="Manage Users" enabled={canManageUsers(user)} />
//             </CardContent>
//           </Card>

//           {canManageUsers(user) && <UserPermissionTable />}
//         </div>
//       </div>
//     </div>
//   );
// }

// function InfoRow({ label, value }) {
//   return (
//     <div className="rounded-2xl border bg-slate-50 p-4">
//       <p className="text-sm text-slate-500">{label}</p>
//       <p className="text-base font-medium mt-1 break-all">{value}</p>
//     </div>
//   );
// }

// function PermissionStatusCard({ title, enabled }) {
//   return (
//     <div className="rounded-2xl border bg-slate-50 p-4">
//       <div className="flex items-center justify-between gap-3">
//         <p className="text-sm font-medium text-slate-700">{title}</p>
//         <Badge variant={enabled ? "default" : "secondary"} className="rounded-full">
//           {enabled ? "Enabled" : "Disabled"}
//         </Badge>
//       </div>
//     </div>
//   );
// }