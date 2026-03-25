import React, { useMemo, useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import ForecastLineChart from "../components/charts/ForecastLineChart";
import { sidebarItems, predictionCategories } from "../data/mockData";
import { runPrediction } from "../services/api";
import {
  getCurrentUser,
  getVisibleSidebarItems,
  canPredict,
  canExport,
} from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function DemandPredictionPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
  const allowPredict = canPredict(user);
  const allowExport = canExport(user);

  const [selectedCategory, setSelectedCategory] = useState("stable_short_term");
  const [stockCode, setStockCode] = useState("102900011008164");
  const [startDate, setStartDate] = useState("2023-06-01");
  const [endDate, setEndDate] = useState("2023-06-07");

  const [loading, setLoading] = useState(false);
  const [exportReady, setExportReady] = useState(false);
  const [errorText, setErrorText] = useState("");
  const [debugText, setDebugText] = useState("");
  const [resultData, setResultData] = useState([]);
  const [historyData, setHistoryData] = useState([]);
  const [summary, setSummary] = useState(null);

  const selected = useMemo(
    () =>
      predictionCategories.find((item) => item.value === selectedCategory) ||
      predictionCategories[0],
    [selectedCategory]
  );

  async function handleRunPrediction() {
    console.log("handleRunPrediction triggered");

    if (!allowPredict) {
      setErrorText("You do not have permission to run prediction.");
      return;
    }

    if (!stockCode || !startDate || !endDate) {
      setErrorText("Please fill in stock code, start date, and end date.");
      return;
    }

    try {
      setLoading(true);
      setErrorText("");
      setDebugText("Sending prediction request...");
      setExportReady(false);

      const payload = {
        predictionCategory: selectedCategory,
        stockCode,
        startDate,
        endDate,
      };

      console.log("Prediction request payload:", payload);

      const response = await runPrediction(payload);

      console.log("Prediction response:", response);

      setSummary(response.summary || null);
      setHistoryData(Array.isArray(response.history) ? response.history : []);
      setResultData(Array.isArray(response.list) ? response.list : []);
      setExportReady(Array.isArray(response.list) && response.list.length > 0);

      setDebugText(
        `Prediction finished. History rows: ${Array.isArray(response.history) ? response.history.length : 0}, forecast rows: ${Array.isArray(response.list) ? response.list.length : 0}.`
      );
    } catch (error) {
      console.error("Prediction failed:", error);
      setErrorText(error.message || "Prediction failed.");
      setSummary(null);
      setHistoryData([]);
      setResultData([]);
      setExportReady(false);
      setDebugText("Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  function handleExportResult() {
    if (!resultData.length) return;

    const csvRows = [
      ["Date", "PredictedSalesKilo"],
      ...resultData.map((item) => [
        item.date,
        item.predictedSalesKilo ?? "",
      ]),
    ];

    const csvContent = csvRows.map((row) => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `forecast_${stockCode}_${startDate}_${endDate}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  const totalPredicted = summary?.totalPredictedSalesKilo ?? 0;

  const chartData = useMemo(() => {
    const historyMapped = historyData.map((item) => ({
      date: item.date,
      historicalSales: item.sales,
      predictedSales: null,
    }));

    const forecastMapped = resultData.map((item) => ({
      date: item.date,
      historicalSales: null,
      predictedSales: item.predictedSalesKilo,
    }));

    return [...historyMapped, ...forecastMapped];
  }, [historyData, resultData]);

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar
            title="Demand Prediction Page"
            subtitle="Run category-based hybrid model prediction"
          />

          {!allowPredict && (
            <div className="rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-700">
              You do not have permission to run prediction.
            </div>
          )}

          <div className="grid xl:grid-cols-[1.05fr_0.95fr] gap-6">
            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>Prediction Form</CardTitle>
                <CardDescription>
                  Select the prediction category, enter a stock code, and choose a forecast date range.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Prediction Category</label>
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger className="rounded-2xl h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {predictionCategories.map((item) => (
                          <SelectItem key={item.value} value={item.value}>
                            {item.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Stock Code</label>
                    <Input
                      placeholder="Enter stock code"
                      className="rounded-2xl h-11"
                      value={stockCode}
                      onChange={(e) => setStockCode(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Start Date</label>
                    <Input
                      type="date"
                      className="rounded-2xl h-11"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">End Date</label>
                    <Input
                      type="date"
                      className="rounded-2xl h-11"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>

                {debugText && (
                  <div className="rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {debugText}
                  </div>
                )}

                {errorText && (
                  <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorText}
                  </div>
                )}

                <div className="flex flex-wrap gap-3">
                  <Button
                    type="button"
                    className="rounded-2xl h-11 px-5"
                    onClick={handleRunPrediction}
                    disabled={!allowPredict || loading}
                  >
                    {loading ? "Running..." : "Run Prediction"}
                  </Button>

                  <Button
                    type="button"
                    className={`rounded-2xl h-11 px-5 ${
                      exportReady && allowExport
                        ? "bg-green-600 hover:bg-green-700 text-white"
                        : ""
                    }`}
                    variant={exportReady && allowExport ? "default" : "outline"}
                    disabled={!allowExport || !exportReady}
                    onClick={handleExportResult}
                  >
                    Export Result
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>Prediction Result Preview</CardTitle>
                <CardDescription>
                  Historical trend and future forecast.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-5">
                <div className="rounded-3xl bg-slate-900 text-white p-6">
  <p className="text-sm text-slate-300">Total Predicted Sales</p>
  <h3 className="text-4xl font-semibold mt-2">
    {Number(totalPredicted).toFixed(2)} kg
  </h3>

  {summary?.evaluation ? (
    <div className="mt-4 text-sm text-slate-300 space-y-1">
      <p>MAE: {Number(summary.evaluation.MAE ?? 0).toFixed(2)}</p>
      <p>RMSE: {Number(summary.evaluation.RMSE ?? 0).toFixed(2)}</p>
      <p>sMAPE: {Number(summary.evaluation.sMAPE ?? 0).toFixed(2)}%</p>
      <p>Valid Actual Days: {summary.evaluation.valid_actual_days ?? 0}</p>
    </div>
  ) : (
    <div className="mt-4 text-sm text-slate-300">
      No actual values available for evaluation in this date range.
    </div>
  )}
</div>
                {/* <div className="rounded-3xl bg-slate-900 text-white p-6">
                  <p className="text-sm text-slate-300">Total Predicted Sales</p>
                  <h3 className="text-4xl font-semibold mt-2">
                    {Number(totalPredicted).toFixed(2)} kg
                  </h3>
                </div> */}

                <ForecastLineChart data={chartData} />

                <div className="rounded-3xl border bg-slate-50 p-4">
                  <h3 className="text-lg font-semibold mb-4">Predicted Daily Demand List</h3>

                  {resultData.length > 0 ? (
                    <div className="space-y-3">
                      {resultData.map((item) => (
                        <div
                          key={item.date}
                          className="rounded-2xl border bg-white px-4 py-3 flex items-center justify-between gap-4"
                        >
                          <div>
                            <p className="text-sm text-slate-500">Date</p>
                            <p className="font-medium">{item.date}</p>
                          </div>

                          <div>
                            <p className="text-sm text-slate-500">Predicted</p>
                            <p className="font-medium">
                              {Number(item.predictedSalesKilo ?? 0).toFixed(2)} kg
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500">
                      No prediction result yet.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
// import React, { useState } from "react";
// import Sidebar from "../components/layout/Sidebar";
// import TopBar from "../components/layout/TopBar";
// import ForecastLineChart from "../components/charts/ForecastLineChart";
// import { sidebarItems, predictionCategories } from "../data/mockData";
// import { runPrediction } from "../services/api";
// import {
//   getCurrentUser,
//   getVisibleSidebarItems,
//   canPredict,
//   canExport,
// } from "../utils/auth";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// import { Input } from "@/components/ui/input";
// import { Button } from "@/components/ui/button";

// export default function DemandPredictionPage() {
//   const user = getCurrentUser();
//   const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
//   const allowPredict = canPredict(user);
//   const allowExport = canExport(user);

//   const [selectedCategory, setSelectedCategory] = useState("stable_short_term");
//   const [stockCode, setStockCode] = useState("102900011008164");
//   const [startDate, setStartDate] = useState("2023-06-01");
//   const [endDate, setEndDate] = useState("2023-06-07");

//   const [loading, setLoading] = useState(false);
//   const [exportReady, setExportReady] = useState(false);
//   const [errorText, setErrorText] = useState("");
//   const [debugText, setDebugText] = useState("");
//   const [resultData, setResultData] = useState([]);
//   const [summary, setSummary] = useState(null);

//   async function handleRunPrediction() {
//     console.log("handleRunPrediction triggered");

//     if (!allowPredict) {
//       setErrorText("You do not have permission to run prediction.");
//       return;
//     }

//     if (!stockCode || !startDate || !endDate) {
//       setErrorText("Please fill in stock code, start date, and end date.");
//       return;
//     }

//     try {
//       setLoading(true);
//       setErrorText("");
//       setDebugText("Sending prediction request...");
//       setExportReady(false);

//       const payload = {
//         predictionCategory: selectedCategory,
//         stockCode,
//         startDate,
//         endDate,
//       };

//       console.log("Prediction request payload:", payload);

//       const response = await runPrediction(payload);

//       console.log("Prediction response:", response);

//       setSummary(response.summary || null);
//       setResultData(Array.isArray(response.list) ? response.list : []);
//       setExportReady(Array.isArray(response.list) && response.list.length > 0);

//       setDebugText(
//         `Prediction finished. Received ${Array.isArray(response.list) ? response.list.length : 0} rows.`
//       );
//     } catch (error) {
//       console.error("Prediction failed:", error);
//       setErrorText(error.message || "Prediction failed.");
//       setSummary(null);
//       setResultData([]);
//       setExportReady(false);
//       setDebugText("Prediction failed.");
//     } finally {
//       setLoading(false);
//     }
//   }

//   function handleExportResult() {
//     if (!resultData.length) return;

//     const csvRows = [
//       ["Date", "PredictedSalesKilo", "ActualSalesKilo"],
//       ...resultData.map((item) => [
//         item.date,
//         item.predictedSalesKilo ?? "",
//         item.actualSalesKilo ?? "",
//       ]),
//     ];

//     const csvContent = csvRows.map((row) => row.join(",")).join("\n");
//     const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
//     const url = URL.createObjectURL(blob);

//     const link = document.createElement("a");
//     link.href = url;
//     link.setAttribute("download", `forecast_${stockCode}_${startDate}_${endDate}.csv`);
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//   }

//   const totalPredicted = summary?.totalPredictedSalesKilo ?? 0;

//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar
//             title="Demand Prediction Page"
//             subtitle="Run category-based hybrid model prediction"
//           />

//           {!allowPredict && (
//             <div className="rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-700">
//               You do not have permission to run prediction.
//             </div>
//           )}

//           <div className="grid xl:grid-cols-[1.05fr_0.95fr] gap-6">
//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Prediction Form</CardTitle>
//                 <CardDescription>
//                   Select the prediction category, enter a stock code, and choose a forecast date range.
//                 </CardDescription>
//               </CardHeader>

//               <CardContent className="space-y-6">
//                 <div className="grid md:grid-cols-2 gap-4">
//                   <div className="space-y-2">
//                     <label className="text-sm font-medium">Prediction Category</label>
//                     <Select value={selectedCategory} onValueChange={setSelectedCategory}>
//                       <SelectTrigger className="rounded-2xl h-11">
//                         <SelectValue />
//                       </SelectTrigger>
//                       <SelectContent>
//                         {predictionCategories.map((item) => (
//                           <SelectItem key={item.value} value={item.value}>
//                             {item.label}
//                           </SelectItem>
//                         ))}
//                       </SelectContent>
//                     </Select>
//                   </div>

//                   <div className="space-y-2">
//                     <label className="text-sm font-medium">Stock Code</label>
//                     <Input
//                       placeholder="Enter stock code"
//                       className="rounded-2xl h-11"
//                       value={stockCode}
//                       onChange={(e) => setStockCode(e.target.value)}
//                     />
//                   </div>

//                   <div className="space-y-2">
//                     <label className="text-sm font-medium">Start Date</label>
//                     <Input
//                       type="date"
//                       className="rounded-2xl h-11"
//                       value={startDate}
//                       onChange={(e) => setStartDate(e.target.value)}
//                     />
//                   </div>

//                   <div className="space-y-2">
//                     <label className="text-sm font-medium">End Date</label>
//                     <Input
//                       type="date"
//                       className="rounded-2xl h-11"
//                       value={endDate}
//                       onChange={(e) => setEndDate(e.target.value)}
//                     />
//                   </div>
//                 </div>

//                 {debugText && (
//                   <div className="rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-700">
//                     {debugText}
//                   </div>
//                 )}

//                 {errorText && (
//                   <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
//                     {errorText}
//                   </div>
//                 )}

//                 <div className="flex flex-wrap gap-3">
//                   <Button
//                     type="button"
//                     className="rounded-2xl h-11 px-5"
//                     onClick={handleRunPrediction}
//                     disabled={!allowPredict || loading}
//                   >
//                     {loading ? "Running..." : "Run Prediction"}
//                   </Button>

//                   <Button
//                     type="button"
//                     className={`rounded-2xl h-11 px-5 ${
//                       exportReady && allowExport
//                         ? "bg-green-600 hover:bg-green-700 text-white"
//                         : ""
//                     }`}
//                     variant={exportReady && allowExport ? "default" : "outline"}
//                     disabled={!allowExport || !exportReady}
//                     onClick={handleExportResult}
//                   >
//                     Export Result
//                   </Button>
//                 </div>
//               </CardContent>
//             </Card>

//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Prediction Result Preview</CardTitle>
//                 <CardDescription>
//                   Predicted sales visualization and daily forecast list.
//                 </CardDescription>
//               </CardHeader>

//               <CardContent className="space-y-5">
//                 <div className="rounded-3xl bg-slate-900 text-white p-6">
//                   <p className="text-sm text-slate-300">Total Predicted Sales</p>
//                   <h3 className="text-4xl font-semibold mt-2">
//                     {Number(totalPredicted).toFixed(2)} kg
//                   </h3>

//                   {summary?.evaluation && (
//                     <div className="mt-4 text-sm text-slate-300 space-y-1">
//                       <p>MAE: {Number(summary.evaluation.MAE ?? 0).toFixed(2)}</p>
//                       <p>RMSE: {Number(summary.evaluation.RMSE ?? 0).toFixed(2)}</p>
//                       <p>sMAPE: {Number(summary.evaluation.sMAPE ?? 0).toFixed(2)}%</p>
//                     </div>
//                   )}
//                 </div>

//                 <ForecastLineChart data={resultData} />

//                 <div className="rounded-3xl border bg-slate-50 p-4">
//                   <h3 className="text-lg font-semibold mb-4">Predicted Daily Demand List</h3>

//                   {resultData.length > 0 ? (
//                     <div className="space-y-3">
//                       {resultData.map((item) => (
//                         <div
//                           key={item.date}
//                           className="rounded-2xl border bg-white px-4 py-3 flex items-center justify-between gap-4"
//                         >
//                           <div>
//                             <p className="text-sm text-slate-500">Date</p>
//                             <p className="font-medium">{item.date}</p>
//                           </div>

//                           <div>
//                             <p className="text-sm text-slate-500">Predicted</p>
//                             <p className="font-medium">
//                               {Number(item.predictedSalesKilo ?? 0).toFixed(2)} kg
//                             </p>
//                           </div>

//                           <div>
//                             <p className="text-sm text-slate-500">Actual</p>
//                             <p className="font-medium">
//                               {item.actualSalesKilo == null
//                                 ? "-"
//                                 : `${Number(item.actualSalesKilo).toFixed(2)} kg`}
//                             </p>
//                           </div>
//                         </div>
//                       ))}
//                     </div>
//                   ) : (
//                     <div className="text-sm text-slate-500">
//                       No prediction result yet.
//                     </div>
//                   )}
//                 </div>
//               </CardContent>
//             </Card>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
