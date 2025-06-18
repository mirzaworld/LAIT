# LAIT - Legal AI Spend Optimizer

An AI-powered platform to help in-house legal departments reduce outside counsel costs through intelligent invoice review, spend analytics, and vendor optimization.

## 🚀 Features

- **AI Invoice Analysis**: Automatically flag anomalies and billing pattern outliers
- **Predictive Spend Analytics**: Forecast future costs and identify budget risks
- **Vendor Performance Tracking**: Compare law firm performance metrics
- **Optimization Recommendations**: Get actionable insights to reduce costs
- **PDF Invoice Upload**: Upload and automatically extract data from invoice PDFs
- **Role-Based Access Control**: Secure user management with admin and regular user roles
- **Real-Time Notifications**: WebSocket-powered alerts for invoice processing and risks

## 📊 Technical Overview

### Frontend
- React with TypeScript
- React Router for navigation
- Chart.js for data visualization
- TailwindCSS for styling
- Socket.io client for real-time updates
- JWT authentication

### Backend
- Python Flask API with RESTful endpoints
- Flask-SocketIO for real-time communication
- SQLAlchemy ORM
- JWT-based authentication with role-based access
- Celery for background tasks
- scikit-learn ML models (Isolation Forest, XGBoost)
- PDF processing (pdfplumber)
- PostgreSQL database

### Infrastructure
- Docker and Docker Compose for containerization
- AWS S3 for document storage
- AWS RDS for production database
- Redis for message broker

## 🏗️ Project Structure

```
.
├── backend/               # Python Flask backend
│   ├── models/            # Machine learning models
│   ├── db/                # Database models and utilities
│   └── app.py             # Main Flask application
├── public/                # Static assets
└── src/                   # React frontend
    ├── components/        # Reusable UI components
    ├── pages/             # Page components
    ├── services/          # API services
    └── App.tsx            # Root component
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.8+)
- PostgreSQL

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/LAIT.git
   cd LAIT
   ```

2. Install frontend dependencies
   ```
   npm install
   ```

3. Install backend dependencies
   ```
   pip install -r backend/requirements.txt
   ```

4. Set up environment variables by editing the `.env` file with your local settings

5. Set up the database
   ```
   createdb legalspend
   ```

### Development

1. Start the backend server
   ```
   cd backend
   flask run
   ```

2. In a separate terminal, start the frontend development server
   ```
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

## 🧪 Machine Learning Models

The application uses several machine learning models:

1. **Invoice Anomaly Detection**: Identifies unusual billing patterns and flags potentially problematic invoices
2. **Spend Prediction**: Forecasts future legal spend based on historical data
3. **Vendor Clustering**: Groups vendors by performance metrics for benchmarking
