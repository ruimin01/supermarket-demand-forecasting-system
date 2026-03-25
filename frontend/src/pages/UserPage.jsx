import React from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems } from "../data/mockData";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function UserPage() {
  const navigate = useNavigate();

  function handleLogout() {
    // 后面如果你有 token / localStorage，可以在这里清掉
    // localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={sidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="User Page" subtitle="User account information" />

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>User Information</CardTitle>
              <CardDescription>
                This page is used to display current user information and logout action.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="rounded-3xl border p-5">
                <p className="text-sm text-slate-500">Username</p>
                <p className="text-lg font-medium mt-2">Admin User</p>
              </div>

              <div className="rounded-3xl border p-5">
                <p className="text-sm text-slate-500">Role</p>
                <p className="text-lg font-medium mt-2">Administrator</p>
              </div>

              <div className="pt-2">
                <Button
                  className="rounded-2xl bg-red-600 hover:bg-red-700 text-white"
                  onClick={handleLogout}
                >
                  Log Out
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}