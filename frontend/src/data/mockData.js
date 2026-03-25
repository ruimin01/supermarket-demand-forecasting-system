export const sidebarItems = [
  { id: "dashboard", label: "Dashboard", path: "/dashboard" },
  { id: "upload", label: "Data Upload", path: "/upload" },
  { id: "predict", label: "Demand Prediction", path: "/predict" },
  { id: "history", label: "Sales History", path: "/history" },
  { id: "records", label: "Forecast Records", path: "/records" },
  { id: "upload-records", label: "Upload Records", path: "/upload-records" },
  { id: "settings", label: "Settings", path: "/settings" },
];

export const predictionCategories = [
  {
    value: "stable_short_term",
    label: "Stable short-term data",
    tag: "Short-term / Stable",
    description: "Used for products with relatively stable short-term demand patterns.",
  },
  {
    value: "high_volatility_short_term",
    label: "High-volatility short-term data",
    tag: "Short-term / Volatile",
    description: "Used for products with highly fluctuating short-term demand patterns.",
  },
  {
    value: "stable_long_term",
    label: "Stable long-term data",
    tag: "Long-term / Stable",
    description: "Used for products with relatively stable long-term demand patterns.",
  },
  {
    value: "high_volatility_long_term",
    label: "High-volatility long-term data",
    tag: "Long-term / Volatile",
    description: "Used for products with highly fluctuating long-term demand patterns.",
  },
];

// export const productTypes = [
//   {
//     value: "stable_short_term",
//     label: "Broccoli",
//     tag: "Stable",
//     description: "Suitable for relatively stable daily demand.",
//   },
//   {
//     value: "hot-water-bag",
//     label: "Hot Water Bag",
//     tag: "Volatile",
//     description: "High spikes, frequent zero-demand days.",
//   },
//   {
//     value: "water-chestnut",
//     label: "Water Chestnut",
//     tag: "Seasonal",
//     description: "Strong seasonality and periodic demand cycles.",
//   },
//   {
//     value: "leafy-vegetable",
//     label: "Leafy Vegetable Group",
//     tag: "Category",
//     description: "Category-level prediction for grouped replenishment.",
//   },
// ];

export const stats = [
  { title: "Supported Product Types", value: "4", sub: "Stable short-term data / High-volatility short-term data / Stable long-term data / High-volatility long-term data" },
  { title: "Machine Learning Method", value: "GRU + XGBoost", sub: "Hybrid deep learning model" },
  { title: "Data Management System", value: "Achieve data visualization", sub: "Historical data and Forecasting data" },
  { title: "System", value: "Technology", sub: "React + Python + MySQL" },
];

export const forecastPreviewData = [
  { date: "2023-07-01", demand: 8.6 },
  { date: "2023-07-02", demand: 8.1 },
  { date: "2023-07-03", demand: 7.9 },
  { date: "2023-07-04", demand: 8.4 },
  { date: "2023-07-05", demand: 8.8 },
  { date: "2023-07-06", demand: 9.3 },
  { date: "2023-07-07", demand: 8.9 },
];

export const salesHistoryData = [
  { date: "2023-06-20", sales: 7.8 },
  { date: "2023-06-21", sales: 8.2 },
  { date: "2023-06-22", sales: 7.4 },
  { date: "2023-06-23", sales: 6.9 },
  { date: "2023-06-24", sales: 7.1 },
  { date: "2023-06-25", sales: 8.4 },
  { date: "2023-06-26", sales: 9.0 },
  { date: "2023-06-27", sales: 8.7 },
  { date: "2023-06-28", sales: 8.1 },
];

export const forecastRecords = [
  {
    product: "Broccoli",
    type: "Stable",
    range: "2023-07-01 to 2023-07-07",
    demand: "8.92 kg",
    model: "GRU + XGBoost",
    status: "completed",
  },
  {
    product: "Hot Water Bag",
    type: "Volatile",
    range: "2023-12-05 to 2023-12-11",
    demand: "72 pcs",
    model: "GRU + XGBoost",
    status: "completed",
  },
  {
    product: "Water Chestnut",
    type: "Seasonal",
    range: "2023-11-12 to 2023-11-18",
    demand: "15.34 kg",
    model: "GRU + XGBoost",
    status: "uncompleted",
  },
];

export const uploadTemplates = [
  {
    title: "Product Master Template",
    fields: "dataset_type, stock_code, product_name, category_name, unit, country",
  },
  {
    title: "Sales Record Template",
    fields:
      "dataset_type, stock_code, sales_date, year, month, day_of_week, is_weekend, quantity_sold, quantity_unit",
  },
];