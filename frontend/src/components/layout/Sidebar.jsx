import React from "react";
import { NavLink } from "react-router-dom";
import {
  BarChart3,
  Database,
  FileText,
  LayoutDashboard,
  LineChart,
  Settings,
  Sparkles,
  Upload,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShoppingBasket } from "lucide-react";

const iconMap = {
  "/dashboard": LayoutDashboard,
  "/upload": Upload,
  "/predict": Sparkles,
  "/history": LineChart,
  "/records": BarChart3,
  "/upload-records": FileText,
  "/settings": Settings,
};

export default function Sidebar({ items }) {
  return (
    <div className="w-full lg:w-72 shrink-0">
      <Card className="rounded-3xl border-0 shadow-lg bg-white/85">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-slate-900 text-white flex items-center justify-center">
              <ShoppingBasket className="h-6 w-6" />
            </div>
            <div>
              <CardTitle className="text-lg">DemandVision</CardTitle>
              <CardDescription>Management Console</CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-2">
          {items.map((item) => {
            const Icon = iconMap[item.path] || Database;

            return (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) =>
                  `w-full rounded-2xl px-4 py-3 text-left transition flex items-center gap-3 ${
                    isActive ? "bg-slate-900 text-white shadow" : "bg-slate-50 hover:bg-slate-100 text-slate-700"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span className="text-sm font-medium">{item.label}</span>
              </NavLink>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
// import React from "react";
// import { NavLink } from "react-router-dom";
// import { BarChart3, Database, LayoutDashboard, LineChart, Settings, Sparkles, Upload } from "lucide-react";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { ShoppingBasket } from "lucide-react";

// const iconMap = {
//   "/dashboard": LayoutDashboard,
//   "/upload": Upload,
//   "/predict": Sparkles,
//   "/history": LineChart,
//   "/records": BarChart3,
//   "/data-management": Database,
//   "/settings": Settings,
// };

// export default function Sidebar({ items }) {
//   return (
//     <div className="w-full lg:w-72 shrink-0">
//       <Card className="rounded-3xl border-0 shadow-lg bg-white/85">
//         <CardHeader className="pb-3">
//           <div className="flex items-center gap-3">
//             <div className="h-12 w-12 rounded-2xl bg-slate-900 text-white flex items-center justify-center">
//               <ShoppingBasket className="h-6 w-6" />
//             </div>
//             <div>
//               <CardTitle className="text-lg">DemandVision</CardTitle>
//               <CardDescription>Management Console</CardDescription>
//             </div>
//           </div>
//         </CardHeader>

//         <CardContent className="space-y-2">
//           {items.map((item) => {
//             const Icon = iconMap[item.path];
//             return (
//               <NavLink
//                 key={item.id}
//                 to={item.path}
//                 className={({ isActive }) =>
//                   `w-full rounded-2xl px-4 py-3 text-left transition flex items-center gap-3 ${
//                     isActive ? "bg-slate-900 text-white shadow" : "bg-slate-50 hover:bg-slate-100 text-slate-700"
//                   }`
//                 }
//               >
//                 <Icon className="h-4 w-4" />
//                 <span className="text-sm font-medium">{item.label}</span>
//               </NavLink>
//             );
//           })}
//         </CardContent>
//       </Card>
//     </div>
//   );
// }