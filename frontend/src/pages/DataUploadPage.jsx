import React, { useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopBar from "../components/layout/TopBar";
import { sidebarItems, uploadTemplates } from "../data/mockData";
import { getCurrentUser, getVisibleSidebarItems } from "../utils/auth";
import { uploadSalesFile } from "../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DataUploadPage() {
  const user = getCurrentUser();
  const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [errorText, setErrorText] = useState("");

  async function handleUpload() {
    console.log("handleUpload triggered");
    setMessage("");
    setErrorText("");

    if (!selectedFile) {
      setErrorText("Please choose a CSV file first.");
      console.log("No file selected");
      return;
    }

    try {
      setUploading(true);
      console.log("Uploading file:", selectedFile.name);

      // 先限制 1000 行测试，避免一下写太多
      const result = await uploadSalesFile(selectedFile,  null);

      console.log("Upload success:", result);

      setMessage(
        `Upload successful: ${result.filename}. Total CSV rows: ${result.row_count}. Inserted products: ${result.import_result?.inserted_products ?? 0}, inserted sales records: ${result.import_result?.inserted_sales_records ?? 0}`
      );
    } catch (error) {
      console.error("Upload failed:", error);
      setErrorText(error.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <Sidebar items={visibleSidebarItems} />

        <div className="flex-1 space-y-6">
          <TopBar title="Data Upload Page" subtitle="Import cleaned data into the system" />

          <div className="grid xl:grid-cols-[0.95fr_1.05fr] gap-6">
            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>Upload Center</CardTitle>
                <CardDescription>
                  Upload CSV files and import data into products and sales_records.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="rounded-3xl border-2 border-dashed p-8 text-center bg-slate-50 space-y-4">
                  <h3 className="text-lg font-semibold">Choose CSV file</h3>

                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null;
                      console.log("Selected file:", file);
                      setSelectedFile(file);
                      setMessage("");
                      setErrorText("");
                    }}
                    className="block mx-auto"
                  />

                  {selectedFile && (
                    <p className="text-sm text-slate-600">
                      Selected file: {selectedFile.name}
                    </p>
                  )}

                  {message && (
                    <div className="rounded-2xl border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700 text-left">
                      {message}
                    </div>
                  )}

                  {errorText && (
                    <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700 text-left">
                      {errorText}
                    </div>
                  )}

                  <div className="flex justify-center gap-3 mt-5">
                    <Button
                      className="rounded-2xl"
                      onClick={handleUpload}
                      disabled={uploading}
                    >
                      {uploading ? "Uploading..." : "Upload"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-0 shadow-md bg-white/85">
              <CardHeader>
                <CardTitle>Template Library</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {uploadTemplates.map((template) => (
                  <div key={template.title} className="rounded-3xl border p-5 bg-slate-50">
                    <h3 className="font-semibold">{template.title}</h3>
                    <div className="mt-4 rounded-2xl bg-white border p-4 text-sm text-slate-600 break-words">
                      {template.fields}
                    </div>
                  </div>
                ))}
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
// import { sidebarItems, uploadTemplates } from "../data/mockData";
// import { getCurrentUser, getVisibleSidebarItems, canUpload } from "../utils/auth";
// import { uploadSalesFile } from "../services/api";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";

// export default function DataUploadPage() {
//   const user = getCurrentUser();
//   const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
//   const allowUpload = canUpload(user);

//   const [selectedFile, setSelectedFile] = useState(null);
//   const [uploading, setUploading] = useState(false);

// async function handleUpload() {
//   if (!selectedFile) {
//     setErrorText("Please choose a CSV file first.");
//     return;
//   }

//   try {
//     setUploading(true);
//     setMessage("");
//     setErrorText("");

//     const result = await uploadSalesFile(selectedFile, 1000);

//     setMessage(
//       `Upload successful: ${result.filename}. Inserted products: ${result.import_result.inserted_products}, inserted sales records: ${result.import_result.inserted_sales_records}`
//     );
//   } catch (error) {
//     console.error(error);
//     setErrorText(error.message || "Upload failed");
//   } finally {
//     setUploading(false);
//   }
// }

//   // async function handleUpload() {
//   //   if (!selectedFile) {
//   //     alert("Please choose a file first");
//   //     return;
//   //   }

//   //   try {
//   //     setUploading(true);
//   //     const result = await uploadSalesFile(selectedFile);
//   //     alert("Upload success");
//   //     console.log("Upload result:", result);
//   //     setSelectedFile(null);
//   //   } catch (error) {
//   //     alert(error.message || "Upload failed");
//   //     console.error("Upload error:", error);
//   //   } finally {
//   //     setUploading(false);
//   //   }
//   // }

//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar title="Data Upload Page" subtitle="Import cleaned data into the system" />

//           <div className="grid xl:grid-cols-[0.95fr_1.05fr] gap-6">
//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Upload Center</CardTitle>
//                 <CardDescription>
//                   Upload CSV file and send it to backend import API.
//                 </CardDescription>
//               </CardHeader>

//               <CardContent className="space-y-4">
//                 {allowUpload ? (
//                   <div className="rounded-3xl border-2 border-dashed p-8 text-center bg-slate-50">
//                     <h3 className="text-lg font-semibold">Upload CSV File</h3>
//                     <p className="text-sm text-slate-500 mt-2">
//                       Choose a CSV file and send it to backend import endpoint.
//                     </p>

//                     <div className="mt-5 flex flex-col items-center gap-4">
//                       <input
//                         type="file"
//                         accept=".csv"
//                         onChange={(e) => setSelectedFile(e.target.files[0])}
//                         className="block w-full max-w-md text-sm text-slate-600
//                                    file:mr-4 file:py-2 file:px-4
//                                    file:rounded-xl file:border-0
//                                    file:text-sm file:font-semibold
//                                    file:bg-slate-200 file:text-slate-700
//                                    hover:file:bg-slate-300"
//                       />

//                       {selectedFile && (
//                         <p className="text-sm text-slate-600">
//                           Selected file: <span className="font-medium">{selectedFile.name}</span>
//                         </p>
//                       )}

//                       <div className="flex justify-center gap-3">
//                         <Button
//                           variant="outline"
//                           className="rounded-2xl"
//                           onClick={() => setSelectedFile(null)}
//                           disabled={!selectedFile || uploading}
//                         >
//                           Clear
//                         </Button>

//                         <Button
//                           className="rounded-2xl"
//                           onClick={handleUpload}
//                           disabled={uploading}
//                         >
//                           {uploading ? "Uploading..." : "Upload"}
//                         </Button>
//                       </div>
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="rounded-3xl border bg-amber-50 border-amber-300 p-8 text-center">
//                     <h3 className="text-lg font-semibold text-amber-800">No Upload Permission</h3>
//                     <p className="text-sm text-amber-700 mt-2">
//                       Your account is not allowed to upload product or sales data.
//                     </p>
//                   </div>
//                 )}
//               </CardContent>
//             </Card>

//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Template Library</CardTitle>
//               </CardHeader>

//               <CardContent className="space-y-4">
//                 {uploadTemplates.map((template) => (
//                   <div key={template.title} className="rounded-3xl border p-5 bg-slate-50">
//                     <h3 className="font-semibold">{template.title}</h3>
//                     <div className="mt-4 rounded-2xl bg-white border p-4 text-sm text-slate-600 break-words">
//                       {template.fields}
//                     </div>
//                   </div>
//                 ))}
//               </CardContent>
//             </Card>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
// ==========================================
// import React from "react";
// import Sidebar from "../components/layout/Sidebar";
// import TopBar from "../components/layout/TopBar";
// import { sidebarItems, uploadTemplates } from "../data/mockData";
// import { getCurrentUser, getVisibleSidebarItems, canUpload } from "../utils/auth";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";

// export default function DataUploadPage() {
//   const user = getCurrentUser();
//   const visibleSidebarItems = getVisibleSidebarItems(sidebarItems, user);
//   const allowUpload = canUpload(user);

//   return (
//     <div className="max-w-[1600px] mx-auto p-4 lg:p-6">
//       <div className="flex flex-col lg:flex-row gap-6">
//         <Sidebar items={visibleSidebarItems} />

//         <div className="flex-1 space-y-6">
//           <TopBar title="Data Upload Page" subtitle="Import cleaned data into the system" />

//           <div className="grid xl:grid-cols-[0.95fr_1.05fr] gap-6">
//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Upload Center</CardTitle>
//                 <CardDescription>Connect this part to your Python file import API later.</CardDescription>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 {allowUpload ? (
//                   <div className="rounded-3xl border-2 border-dashed p-8 text-center bg-slate-50">
//                     <h3 className="text-lg font-semibold">Drag CSV file here</h3>
//                     <p className="text-sm text-slate-500 mt-2">
//                       Or choose file and send to backend import endpoint.
//                     </p>
//                     <div className="flex justify-center gap-3 mt-5">
//                       <Button className="rounded-2xl">Choose File</Button>
//                       <Button variant="outline" className="rounded-2xl">
//                         Upload
//                       </Button>
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="rounded-3xl border bg-amber-50 border-amber-300 p-8 text-center">
//                     <h3 className="text-lg font-semibold text-amber-800">No Upload Permission</h3>
//                     <p className="text-sm text-amber-700 mt-2">
//                       Your account is not allowed to upload product or sales data.
//                     </p>
//                   </div>
//                 )}
//               </CardContent>
//             </Card>

//             <Card className="rounded-3xl border-0 shadow-md bg-white/85">
//               <CardHeader>
//                 <CardTitle>Template Library</CardTitle>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 {uploadTemplates.map((template) => (
//                   <div key={template.title} className="rounded-3xl border p-5 bg-slate-50">
//                     <h3 className="font-semibold">{template.title}</h3>
//                     <div className="mt-4 rounded-2xl bg-white border p-4 text-sm text-slate-600 break-words">
//                       {template.fields}
//                     </div>
//                   </div>
//                 ))}
//               </CardContent>
//             </Card>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }