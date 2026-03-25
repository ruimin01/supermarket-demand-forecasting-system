import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { stats } from "@/data/mockData";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="max-w-350 mx-auto p-4 lg:p-6 space-y-6">
      <Card className="rounded-3xl border-0 shadow-lg overflow-hidden bg-linear-to-r from-slate-900 via-slate-800 to-slate-700 text-white">
        <CardContent className="p-8 lg:p-10">
          <div className="grid lg:grid-cols-[1.5fr_0.9fr] gap-8 items-center">
            <div className="space-y-5">
              <Badge className="bg-white/15 hover:bg-white/15 text-white rounded-full px-3 py-1">
                Home Page
              </Badge>
              <h1 className="text-3xl lg:text-5xl font-semibold tracking-tight">
                Intelligent Product Demand Prediction for Supermarkets
              </h1>
              <p className="text-slate-200 max-w-3xl leading-7">
                Welcome to our program! This application is designed to help supermarkets predict product demand using advanced machine learning techniques. By analyzing historical sales data, seasonal trends, and other relevant factors, our system provides accurate forecasts to optimize inventory management and improve customer satisfaction.
              </p>
              <div className="flex gap-3">
                <Button className="rounded-2xl bg-white text-slate-900 hover:bg-slate-100" onClick={() => navigate("/login")}>
                  User Login
                </Button>
                <Button variant="secondary" className="rounded-2xl bg-white/10 text-white hover:bg-white/20" onClick={() => navigate("/dashboard")}>
                  Dashboard
                </Button>
              </div>
            </div>

          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map((item) => (
          <Card key={item.title} className="rounded-3xl border-0 shadow-md bg-white/85">
            <CardContent className="p-5">
              <p className="text-sm text-slate-500">{item.title}</p>
              <h3 className="text-2xl font-semibold mt-2">{item.value}</h3>
              <p className="text-sm text-slate-500 mt-1">{item.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}