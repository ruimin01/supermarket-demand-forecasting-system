import React from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems } from "../data/mockData";
import { getCurrentUser, getVisibleSidebarItems } from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function DataManagementPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Data Management Page" subtitle="Frontend, backend, and database integration" />

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>System Integration Logic</CardTitle>
              <CardDescription>Useful for your chapter 5 explanation.</CardDescription>
            </CardHeader>
            <CardContent className="grid lg:grid-cols-3 gap-4">
              <div className="rounded-3xl border p-6 bg-slate-50">
                <h3 className="text-lg font-semibold">React Frontend</h3>
                <p className="text-sm text-slate-600 mt-2 leading-6">
                  Sends login, upload, history query, and prediction requests.
                </p>
              </div>

              <div className="rounded-3xl border p-6 bg-slate-50">
                <h3 className="text-lg font-semibold">Python Backend</h3>
                <p className="text-sm text-slate-600 mt-2 leading-6">
                  Reads MySQL, preprocesses data, and calls GRU + XGBoost.
                </p>
              </div>

              <div className="rounded-3xl border p-6 bg-slate-50">
                <h3 className="text-lg font-semibold">MySQL Database</h3>
                <p className="text-sm text-slate-600 mt-2 leading-6">
                  Stores products, sales records, forecast results, and upload logs.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}