# LAIT - Legal AI Spend Optimizer

An enterprise-grade AI platform that helps in-house legal departments optimize outside counsel spend through intelligent invoice review, spend analytics, and vendor optimization.

## 🚀 Features

- **AI Invoice Analysis**
  - Automatic anomaly detection in billing entries
  - PDF parsing and data extraction
  - Smart validation of line items

- **Advanced Analytics**
  - Predictive spend forecasting
  - Vendor performance clustering
  - Interactive dashboards
  - Custom report generation

- **Security & Compliance**
  - Role-based access control (RBAC)
  - Audit logging
  - HTTPS enforcement
  - Rate limiting
  - Secure file handling

- **Real-Time Updates**
  - WebSocket notifications
  - Processing status tracking
  - Instant alerts for anomalies

- **User Experience**
  - Modern, responsive UI
  - Professional landing page
  - Streamlined onboarding
  - Intuitive dashboard navigation

## 📊 Technical Stack

### Frontend

- React 18 with TypeScript
- TailwindCSS for styling
- Chart.js for visualizations
- Socket.io for real-time updates
- JWT authentication
- Production-ready build pipeline

### Backend

- Python 3.11+ with Flask
- PostgreSQL for data storage
- Redis for caching and Celery
- AWS S3 for file storage
- ML pipeline with scikit-learn & XGBoost
- Comprehensive API documentation

### Infrastructure

- Docker and Docker Compose for containerization
- AWS ECS for container orchestration
- AWS RDS for managed PostgreSQL
- AWS S3 for file storage
- AWS ElastiCache for Redis
- Terraform for infrastructure as code

## 🚀 Getting Started

### Prerequisites

- Docker Desktop
- AWS CLI configured
- Node.js 18+
- Python 3.11+

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/yourusername/LAIT.git
cd LAIT
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development environment:

```bash
docker-compose up -d
```

4. Install frontend dependencies:

```bash
cd frontend
npm install
npm start
```

The application will be available at:

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs

### Running Tests

Backend tests:

```bash
cd backend
pytest
```

Frontend tests:

```bash
cd frontend
npm test
```

## 🌐 Deployment

### AWS Deployment

1. Configure AWS credentials:

```bash
aws configure
```

2. Deploy infrastructure:

```bash
cd terraform
terraform init
terraform apply
```

3. Push Docker images:

```bash
docker build -t lait-backend ./backend
docker build -t lait-frontend .
# Tag and push to ECR
```

## 📚 Documentation

- API documentation is available at `/api/docs`
- ML model documentation in `/backend/ml/README.md`
- Deployment guide in `/docs/deployment.md`

## 🔒 Security Features

- HTTPS enforcement in production
- JWT authentication with refresh tokens
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- Regular security audits
- Comprehensive audit logging

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

For support, please open an issue in the GitHub repository or contact the maintainers.
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
