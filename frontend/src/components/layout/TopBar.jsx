import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getCurrentUser } from "../../utils/auth";

export default function TopBar({ title, subtitle }) {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p className="text-sm text-slate-500">{subtitle}</p>
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      </div>

      <div className="flex items-center gap-3">
        <div className="rounded-2xl border bg-white px-4 py-2 flex items-center gap-2 text-sm text-slate-700">
          <User className="h-4 w-4" />
          {currentUser?.username || "Unknown User"}
        </div>
                <Button  variant="outline"
          className="rounded-2xl"
          onClick={() => navigate("/")}
        >
          <ArrowRight className="mr-2 h-4 w-4" />
          Back to Home
        </Button>

        {/* <Button variant="outline" className="rounded-2xl" onClick={() => navigate("/dashboard")}>
          <ArrowRight className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button> */}
      </div>
    </div>
  );
}





// import React from "react";
// import { useNavigate } from "react-router-dom";
// import { ArrowRight, User } from "lucide-react";
// import { Button } from "@/components/ui/button";

// export default function TopBar({ title, subtitle }) {
//   const navigate = useNavigate();

//   return (
//     <div className="flex flex-wrap items-center justify-between gap-3">
//       <div>
//         <p className="text-sm text-slate-500">{subtitle}</p>
//         <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
//       </div>

//       <div className="flex items-center gap-3">
//         <Button
//   variant="outline"
//   className="rounded-2xl"
//   onClick={() => navigate("/user")}
// >
//   <User className="mr-2 h-4 w-4" />
//   Admin User
// </Button>
//         <Button  variant="outline"
//           className="rounded-2xl"
//           onClick={() => navigate("/")}
//         >
//           <ArrowRight className="mr-2 h-4 w-4" />
//           Back to Home
//         </Button>
//       </div>
//     </div>
//   );
// }