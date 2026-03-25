import React, { useEffect, useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems } from "../data/mockData";
import {
  getCurrentUser,
  getVisibleSidebarItems,
  canViewAllRecords,
} from "../utils/auth";
import { fetchForecastRecords } from "../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function ForecastRecordsPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
  const allowViewAll = canViewAllRecords(user);

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecords() {
      try {
        const data = await fetchForecastRecords();
        setRecords(data);
      } catch (error) {
        console.error("Failed to load forecast records:", error);
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
  }, []);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Forecast Records Page" subtitle="Prediction history records" />

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>Prediction Records</CardTitle>
              <CardDescription>
                {allowViewAll
                  ? "You are viewing all forecast records."
                  : "You are viewing your own forecast records only."}
              </CardDescription>
            </CardHeader>

            <CardContent>
              {loading ? (
                <div className="py-10 text-center text-slate-500">Loading forecast records...</div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Product</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Range</TableHead>
                        <TableHead>Predicted Demand</TableHead>
                        <TableHead>Model</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {records.length > 0 ? (
                        records.map((record, index) => (
                          <TableRow key={`${record.product}-${record.range_text || record.range}-${index}`}>
                            <TableCell className="font-medium">{record.product}</TableCell>
                            <TableCell>{record.type}</TableCell>
                            <TableCell>{record.range_text || record.range}</TableCell>
                            <TableCell>{record.demand}</TableCell>
                            <TableCell>{record.model}</TableCell>
                            <TableCell>
                              <Badge className="rounded-full">{record.status}</Badge>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={6} className="text-center text-slate-500 py-8">
                            No forecast records found.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
// import React, { useEffect, useState } from "react";
// import { fetchForecastRecords } from "../services/api";
// import Sidebar from "../components/layout/Sidebar";
// import TopBar from "../components/layout/TopBar";
// import { sidebarItems, forecastRecords } from "../data/mockData";
// import {
//   getCurrentUser,
//   getVisibleSidebarItems,
//   canViewAllRecords,
// } from "../utils/auth";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Badge } from "@/components/ui/badge";
// import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

// export default function ForecastRecordsPage() {
//   const user = getCurrentUser();
//   const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
//   const allowViewAll = canViewAllRecords(user);
// const [records, setRecords] = useState([]);
// const [loading, setLoading] = useState(true);

// useEffect(() => {
//   async function loadRecords() {
//     try {
//       const data = await fetchForecastRecords();
//       setRecords(data);
//     } catch (error) {
//       console.error(error);
//     } finally {
//       setLoading(false);
//     }
//   }

//   loadRecords();
// }, []);
//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar title="Forecast Records Page" subtitle="Prediction history records" />

//           <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//             <CardHeader>
//               <CardTitle>Prediction Records</CardTitle>
//               <CardDescription>
//                 {allowViewAll
//                   ? "You are viewing all forecast records."
//                   : "You are viewing your own forecast records only."}
//               </CardDescription>
//             </CardHeader>
//             <CardContent>
//               <div className="overflow-x-auto">
//                 <Table>
//                   <TableHeader>
//                     <TableRow>
//                       <TableHead>Product</TableHead>
//                       <TableHead>Type</TableHead>
//                       <TableHead>Range</TableHead>
//                       <TableHead>Predicted Demand</TableHead>
//                       <TableHead>Model</TableHead>
//                       <TableHead>Status</TableHead>
//                     </TableRow>
//                   </TableHeader>
//                   <TableBody>
//                     {records.map((record) => (
//                       <TableRow key={`${record.product}-${record.range}`}>
//                         <TableCell className="font-medium">{record.product}</TableCell>
//                         <TableCell>{record.type}</TableCell>
//                         <TableCell>{record.range}</TableCell>
//                         <TableCell>{record.demand}</TableCell>
//                         <TableCell>{record.model}</TableCell>
//                         <TableCell>
//                           <Badge className="rounded-full">
//                             {record.status}
//                           </Badge>
//                         </TableCell>
//                       </TableRow>
//                     ))}
//                   </TableBody>
//                 </Table>
//               </div>
//             </CardContent>
//           </Card>
//         </div>
//       </div>
//     </div>
//   );
// }