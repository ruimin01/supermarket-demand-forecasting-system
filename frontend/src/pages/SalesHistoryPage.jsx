import React, { useEffect, useState } from "react";
import { fetchSalesHistory } from "../services/api";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import SalesHistoryChart from "../components/charts/SalesHistoryChart";
import ResultList from "../components/common/ResultList";
import { sidebarItems, salesHistoryData } from "../data/mockData";
import { getCurrentUser, getVisibleSidebarItems } from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";


export default function SalesHistoryPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await fetchSalesHistory();
        setHistoryData(data);
      } catch (error) {
        console.error("Failed to fetch sales history:", error);
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Sales History Page" subtitle="Historical real sales data" />

          <Card className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardHeader>
              <CardTitle>Historical Actual Sales Trend</CardTitle>
              <CardDescription>
                This page shows only real historical sales data and the detailed daily value list.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {loading ? (
                <p>Loading sales history...</p>
              ) : (
                <>
                  <SalesHistoryChart data={historyData} />
                  <ResultList
                    items={historyData}
                    valueKey="sales"
                    title="Historical Sales List"
                    unit="kg"
                  />
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// export default function SalesHistoryPage() {
//   // const user = getCurrentUser();
//   // const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

//   // ...... 
//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar title="Sales History Page" subtitle="Historical real sales data" />

//           <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//             <CardHeader>
//               <CardTitle>Historical Actual Sales Trend</CardTitle>
//               <CardDescription>
//                 This page shows only real historical sales data and the detailed daily value list.
//               </CardDescription>
//             </CardHeader>
//             <CardContent className="space-y-6">
//               <SalesHistoryChart data={salesHistoryData} />
//               <ResultList items={salesHistoryData} valueKey="sales" title="Historical Sales List" unit="kg" />
//             </CardContent>
//           </Card>
//         </div>
//       </div>
//     </div>
//   );
// }