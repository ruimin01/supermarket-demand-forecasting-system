import React from "react";

export default function ResultList({ items, valueKey = "demand", title = "Result List", unit = "" }) {
  return (
    <div className="rounded-3xl border bg-slate-50 p-5">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.date}
            className="rounded-2xl bg-white border px-4 py-3 flex items-center justify-between text-sm"
          >
            <span className="text-slate-600">{item.date}</span>
            <span className="font-medium text-slate-900">
              {item[valueKey]} {unit}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}