import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function ForecastLineChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="rounded-3xl border bg-slate-50 p-6 text-sm text-slate-500">
        No chart data yet.
      </div>
    );
  }

  return (
    <div className="rounded-3xl border bg-white p-4">
      <h3 className="text-lg font-semibold mb-4">Prediction Trend</h3>
      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" minTickGap={24} />
            <YAxis />
            <Tooltip />
            <Legend />

            <Line
              type="monotone"
              dataKey="historicalSales"
              name="Historical Actual Sales"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
            />

            <Line
              type="monotone"
              dataKey="predictedSales"
              name="Future Forecast"
              stroke="#16a34a"
              strokeWidth={2}
              dot={{ r: 3 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
// import React from "react";
// import {
//   LineChart,
//   Line,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   Legend,
//   ResponsiveContainer,
// } from "recharts";

// export default function ForecastLineChart({ data }) {
//   if (!data || data.length === 0) {
//     return (
//       <div className="rounded-3xl border bg-slate-50 p-6 text-sm text-slate-500">
//         No chart data yet.
//       </div>
//     );
//   }

//   return (
//     <div className="rounded-3xl border bg-white p-4">
//       <h3 className="text-lg font-semibold mb-4">Prediction Trend</h3>
//       <div className="h-[320px] w-full">
//         <ResponsiveContainer width="100%" height="100%">
//           <LineChart data={data}>
//             <CartesianGrid strokeDasharray="3 3" />
//             <XAxis dataKey="date" />
//             <YAxis />
//             <Tooltip />
//             <Legend />
//             <Line
//               type="monotone"
//               dataKey="predictedSalesKilo"
//               name="Predicted Sales"
//               strokeWidth={2}
//               dot={{ r: 3 }}
//             />
//             <Line
//               type="monotone"
//               dataKey="actualSalesKilo"
//               name="Actual Sales"
//               strokeWidth={2}
//               dot={{ r: 3 }}
//               connectNulls={false}
//             />
//           </LineChart>
//         </ResponsiveContainer>
//       </div>
//     </div>
//   );
// }
// import React from "react";
// import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";

// export default function ForecastLineChart({ data }) {
//   return (
//     <div className="h-[320px]">
//       <ResponsiveContainer width="100%" height="100%">
//         <LineChart data={data}>
//           <CartesianGrid strokeDasharray="3 3" />
//           <XAxis dataKey="date" />
//           <YAxis />
//           <Tooltip />
//           <Line type="monotone" dataKey="demand" strokeWidth={3} name="Predicted Demand" />
//         </LineChart>
//       </ResponsiveContainer>
//     </div>
//   );
// }