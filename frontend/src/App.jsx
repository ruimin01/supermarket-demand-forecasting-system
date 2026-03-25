import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import DemandPredictionPage from "./pages/DemandPredictionPage";
import SalesHistoryPage from "./pages/SalesHistoryPage";
import DataUploadPage from "./pages/DataUploadPage";
import ForecastRecordsPage from "./pages/ForecastRecordsPage";
import DataManagementPage from "./pages/DataManagementPage";
import SettingsPage from "./pages/SettingsPage";
import UserPage from "./pages/UserPage";
import UploadRecordsPage from "./pages/UploadRecordsPage";

export default function App() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(148,163,184,0.18),_transparent_32%),linear-gradient(180deg,#f8fafc_0%,#eef2f7_100%)] text-slate-900">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/predict" element={<DemandPredictionPage />} />
        <Route path="/history" element={<SalesHistoryPage />} />
        <Route path="/upload" element={<DataUploadPage />} />
        <Route path="/records" element={<ForecastRecordsPage />} />
        <Route path="/data-management" element={<DataManagementPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/user" element={<UserPage />} />
        <Route path="/upload-records" element={<UploadRecordsPage />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}