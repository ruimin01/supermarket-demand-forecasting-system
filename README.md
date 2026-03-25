
# supermarket-demand-forecasting-system

## Project Overview
This project is a **machine learning–based supermarket demand forecasting system** developed as an undergraduate thesis project.

The system integrates:

- **Frontend** for user interaction and visualization
- **Backend** for API services and model invocation
- **MySQL database** for product and sales data storage
- **Hybrid machine learning models** for product demand prediction


---

## Project Features
- User login and role-based access control
- Product and sales data storage in MySQL
- Historical sales data visualization
- Product demand prediction by selected stock code and forecast date range
- CSV export of prediction results
- Upload record management
- Hybrid forecasting model based on **GRU + XGBoost**

---

## System Architecture
The system follows a **frontend-backend-database-machine learning** architecture.

### Frontend
- React
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts

### Backend
- Python
- Flask
- Flask-CORS

### Database
- MySQL

### Machine Learning
- TensorFlow / Keras
- XGBoost
- scikit-learn
- pandas / numpy

---

## Current Prediction Categories
The current system design supports 1 prediction categories:

- `stable_short_term`
More will be added in the future:
- `high_volatility_short_term`
- `stable_long_term`
- `high_volatility_long_term`

At the current stage, the backend prediction API is first connected for:

- **Naibaicai**
- `stock_code = 102900011008164`
- `prediction_category = stable_short_term`

Other categories can be expanded in the same way.

---

## Main Functional Modules
- Dashboard
- User login and permission management
- Data upload / import
- Upload record viewing
- Sales history visualization
- Demand prediction page
- Forecast result export

---

## Development Environment
Required Software
Python 3.11 recommended
Node.js 18+ recommended
MySQL 8.x recommended
Git
Python Libraries

## Main backend dependencies include:

Flask
Flask-CORS
pymysql
python-dotenv
pandas
numpy
scikit-learn
tensorflow
xgboost
joblib
matplotlib
Frontend Libraries

## Main frontend dependencies include:

React
Vite
Tailwind CSS
shadcn/ui
Recharts
react-router-dom
---
## Environment Preparation
1. Clone the Repository
git clone <your-repository-url>
cd supermarket-demand-forecasting-system
2. Backend Setup
Step 1: Enter backend directory
cd backend
Step 2: Create virtual environment
python -m venv .venv311
Step 3: Activate virtual environment
Windows PowerShell
.venv311\Scripts\Activate.ps1
Windows CMD
.venv311\Scripts\activate
macOS / Linux
source .venv311/bin/activate
Step 4: Install backend dependencies
pip install -r requirements.txt
3. Frontend Setup
Step 1: Enter frontend directory
cd frontend
Step 2: Install dependencies
npm install
Step 3: Start frontend development server
npm run dev
## Database Setup
1. Create MySQL Database
2. Configure Backend Database Connection
3. Test Database Connection
## Running the System
1. Start Backend

In backend/:

python app.py

Default backend address:

http://127.0.0.1:5000
2. Start Frontend

In frontend/:

npm run dev

Then open the local frontend address shown in the terminal, usually:

http://127.0.0.1:5173

## Current Model

The project uses a hybrid forecasting framework based on GRU + XGBoost.

Workflow
Read historical sales data from MySQL
Aggregate and prepare product-specific time series
Generate time features and lag features
Train GRU model
Train XGBoost for residual correction
Save trained model artifacts
Run future date-range prediction