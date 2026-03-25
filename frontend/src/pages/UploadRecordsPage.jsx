import React, { useEffect, useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems } from "../data/mockData";
import {
  getCurrentUser,
  getVisibleSidebarItems,
  canViewUploadRecords,
} from "../utils/auth";
import { fetchUploadRecords } from "../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function UploadRecordsPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
  const allowViewUploadRecords = canViewUploadRecords(user);

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUploadRecords() {
      if (!allowViewUploadRecords) {
        setLoading(false);
        return;
      }

      try {
        const data = await fetchUploadRecords();
        setRecords(data);
      } catch (error) {
        console.error("Failed to load upload records:", error);
      } finally {
        setLoading(false);
      }
    }

    loadUploadRecords();
  }, [allowViewUploadRecords]);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Upload Records Page" subtitle="Historical file upload records" />

          {!allowViewUploadRecords ? (
            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardContent className="p-8">
                <div className="rounded-3xl border bg-amber-50 border-amber-300 p-8 text-center">
                  <h3 className="text-lg font-semibold text-amber-800">No Permission</h3>
                  <p className="text-sm text-amber-700 mt-2">
                    Your account is not allowed to view upload records.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>File Upload Records</CardTitle>
                <CardDescription>Administrators can review uploaded file history here.</CardDescription>
              </CardHeader>

              <CardContent>
                {loading ? (
                  <div className="py-10 text-center text-slate-500">Loading upload records...</div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>File Name</TableHead>
                          <TableHead>Dataset Type</TableHead>
                          <TableHead>Uploaded By</TableHead>
                          <TableHead>Row Count</TableHead>
                          <TableHead>Upload Time</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {records.length > 0 ? (
                          records.map((record) => (
                            <TableRow key={record.file_id}>
                              <TableCell className="font-medium">{record.file_name}</TableCell>
                              <TableCell>{record.dataset_type}</TableCell>
                              <TableCell>{record.uploaded_by}</TableCell>
                              <TableCell>{record.row_count}</TableCell>
                              <TableCell>{record.upload_time}</TableCell>
                              <TableCell>
                                <Badge className="rounded-full">{record.status}</Badge>
                              </TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={6} className="text-center text-slate-500 py-8">
                              No upload records found.
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
