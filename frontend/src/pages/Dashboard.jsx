import React from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems, stats } from "../data/mockData";
import {
  getCurrentUser,
  getVisibleSidebarItems,
  canUpload,
  canPredict,
  canExport,
  canManageUsers,
} from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const quickLinks = [
  { title: "Data Upload", path: "/upload", desc: "Import product and sales data first." },
  { title: "Demand Prediction", path: "/predict", desc: "Run GRU + XGBoost prediction." },
  { title: "Sales History", path: "/history", desc: "View historical actual sales data." },
  { title: "Forecast Records", path: "/records", desc: "Browse completed and uncompleted records." },
  { title: "Data Management", path: "/data-management", desc: "Explain database and backend integration." },
  { title: "Settings", path: "/settings", desc: "Configure API and system parameters." },
];

export default function Dashboard() {
  const navigate = useNavigate();

  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Dashboard" subtitle="Internal working area after login" />

          <Card className="rounded-3xl border-0 shadow-lg overflow-hidden bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 text-white">
            <CardContent className="p-8">
              <h1 className="text-4xl font-semibold">System Dashboard</h1>
              <p className="text-slate-200 mt-3 max-w-3xl leading-7">
                This page is only the dashboard overview. Use the quick navigation cards below to open each functional page.
              </p>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
            {stats.map((item) => (
              <Card key={item.title} className="rounded-3xl border-0 shadow-md bg-white/85">
                <CardContent className="p-5">
                  <p className="text-sm text-slate-500">{item.title}</p>
                  <h3 className="text-2xl font-semibold mt-2">{item.value}</h3>
                  <p className="text-sm text-slate-500 mt-1">{item.sub}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>My Permission Summary</CardTitle>
              <CardDescription>Visible permissions for the currently logged-in user.</CardDescription>
            </CardHeader>
            <CardContent className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
              <PermissionCard title="Upload Data" enabled={canUpload(user)} />
              <PermissionCard title="Run Prediction" enabled={canPredict(user)} />
              <PermissionCard title="Export Result" enabled={canExport(user)} />
              <PermissionCard title="Manage Users" enabled={canManageUsers(user)} />
            </CardContent>
          </Card>

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>Quick Navigation</CardTitle>
              <CardDescription>Ordered by your business workflow.</CardDescription>
            </CardHeader>
            <CardContent className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {quickLinks
                .filter((item) => {
                  if (item.path === "/upload" && !canUpload(user)) return false;
                  return true;
                })
                .map((item) => (
                  <button
                    key={item.title}
                    onClick={() => navigate(item.path)}
                    className="rounded-3xl border bg-slate-50 p-5 text-left hover:bg-slate-100 transition"
                  >
                    <h3 className="text-lg font-semibold">{item.title}</h3>
                    <p className="text-sm text-slate-500 mt-2 leading-6">{item.desc}</p>
                  </button>
                ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function PermissionCard({ title, enabled }) {
  return (
    <div className="rounded-2xl border bg-slate-50 p-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-700">{title}</p>
        <Badge variant={enabled ? "default" : "secondary"} className="rounded-full">
          {enabled ? "Enabled" : "Disabled"}
        </Badge>
      </div>
    </div>
  );
}