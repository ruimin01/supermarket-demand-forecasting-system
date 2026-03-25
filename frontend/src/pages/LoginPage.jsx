import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";
import { saveCurrentUser } from "../utils/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [errorText, setErrorText] = useState("");

  async function handleLogin() {
    try {
      setErrorText("");

      const result = await loginUser(form);

      if (result.success) {
        saveCurrentUser(result.data);
        navigate("/dashboard");
      }
    } catch (error) {
      setErrorText(error.message || "Login failed");
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-4 lg:p-6 min-h-screen flex items-center">
      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6 w-full">
        <Card className="rounded-3xl border-0 shadow-lg overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 text-white">
          <CardContent className="p-8 lg:p-10">
            <h1 className="text-4xl font-semibold">Login Page</h1>
            <p className="text-slate-200 mt-4 leading-7">
              Please sign in with your assigned username and password.
              If you do not have an account, please contact the administrator.
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border-0 shadow-lg bg-white/90">
          <CardHeader>
            <CardTitle className="text-2xl">Login</CardTitle>
            <CardDescription>Use username and password to access the internal system.</CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Username</label>
              <Input
                placeholder="Enter username"
                className="rounded-2xl h-11"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Password</label>
              <Input
                type="password"
                placeholder="Enter password"
                className="rounded-2xl h-11"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>

            {errorText && (
              <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
                {errorText}
              </div>
            )}

            <Button className="w-full rounded-2xl h-11" onClick={handleLogin}>
              Sign In
            </Button>

            <Button variant="outline" className="w-full rounded-2xl h-11" onClick={() => navigate("/")}>
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
// import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { loginUser } from "../services/api";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Input } from "@/components/ui/input";
// import { Button } from "@/components/ui/button";
// import { saveCurrentUser } from "../utils/auth";

// export default function LoginPage() {
//   const navigate = useNavigate();
//   const [form, setForm] = useState({ username: "", password: "" });

//   async function handleLogin() {
//   try {
//     const result = await loginUser(form);

//     if (result.success) {
//       saveCurrentUser(result.data);
//       navigate("/dashboard");
//     }
//   } catch (error) {
//     alert(error.message);
//   }
// }
// //  async function handleLogin() {
// //   const result = await loginUser(form);

// //   if (result.success) {
// //     saveCurrentUser(result.user);
// //     navigate("/dashboard");
// //   }
// // }

//   return (
//     <div className="max-w-6xl mx-auto p-4 lg:p-6 min-h-screen flex items-center">
//       <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6 w-full">
//         <Card className="rounded-3xl border-0 shadow-lg overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 text-white">
//           <CardContent className="p-8 lg:p-10">
//             <h1 className="text-4xl font-semibold">Login Page</h1>
//             <p className="text-slate-200 mt-4 leading-7">
//               After login, users enter the internal dashboard and access prediction, upload, history, and record pages.
//             </p>
//           </CardContent>
//         </Card>

//         <Card className="rounded-3xl border-0 shadow-lg bg-white/90">
//           <CardHeader>
//             <CardTitle className="text-2xl">Login</CardTitle>
//             <CardDescription>Connect this form to your Python authentication API later.</CardDescription>
//           </CardHeader>
//           <CardContent className="space-y-4">
//             <Input
//               placeholder="Username"
//               className="rounded-2xl h-11"
//               value={form.username}
//               onChange={(e) => setForm({ ...form, username: e.target.value })}
//             />
//             <Input
//               type="password"
//               placeholder="Password"
//               className="rounded-2xl h-11"
//               value={form.password}
//               onChange={(e) => setForm({ ...form, password: e.target.value })}
//             />
//             <Button className="w-full rounded-2xl h-11" onClick={handleLogin}>
//               Sign In
//             </Button>
//             <Button variant="outline" className="w-full rounded-2xl h-11" onClick={() => navigate("/")}>
//               Back to Home
//             </Button>
//           </CardContent>
//         </Card>
//       </div>
//     </div>
//   );
// }