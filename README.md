# supermarket-demand-forecasting-system

## Project Overview
This project is a **machine learning–based demand forecasting system for large-scale supermarkets**.  
The system aims to analyze historical sales data and predict future product demand to support
inventory management and procurement decision-making.

By integrating data preprocessing, machine learning models, and a web-based visualization system,
the project provides an intelligent solution for supermarket demand forecasting.

This project is also developed as a **graduation thesis project**, combining theoretical analysis
and system implementation.

---

## System Objectives
- Manage supermarket product and sales data
- Analyze historical sales trends
- Predict future product demand using machine learning models

---

## System Architecture
The system adopts a typical **frontend-backend-machine learning architecture**:

- **Frontend**: React.js + Ant Design  
- **Backend**: Python (Flask / FastAPI)  
- **Database**: MySQL  
- **Machine Learning**: scikit-learn  
- **Visualization**: ECharts / Recharts  

---

## Main Functional Modules
- Product Information Management
- Sales Data Management
- Demand Forecasting Module

---

## Machine Learning Models
The system implements and compares multiple machine learning models for demand forecasting:

- Linear Regression (Baseline model)
- Decision Tree Regression
- Random Forest Regression

## Development Environment
- Python 3.x
- Node.js
- MySQL
- scikit-learn
- React.js

---

## How to Run the Project

### 1. Backend Setup
1. Navigate to the backend directory:

cd backend

2. Install required Python dependencies: 

pip install -r requirements.txt

3. Start the backend service:

python app.py

2. Frontend Setup

### 2. Frontend Setup

1. Navigate to the frontend directory:

cd frontend

2. Install frontend dependencies:

npm install

3. Start the frontend development server:

npm start


###3. Machine Learning Model

The machine learning models are implemented using scikit-learn.

Model training scripts are located in the ml/ directory.

Pre-trained models can be saved and loaded by the backend for prediction.
