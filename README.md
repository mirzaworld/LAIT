# LAIT - Enhanced Legal Intelligence System

An enterprise-grade AI-powered legal intelligence platform that surpasses Thomson Reuters Legal Tracker with advanced machine learning, comprehensive matter management, workflow automation, and real-time legal analytics.

## 📋 **Quick Start**

**Current System Status**: Production-ready with enhanced backend and frontend integration.

### **Access Points**

- **Frontend Application**: <http://localhost:5174>
- **Enhanced Dashboard**: <http://localhost:5174/enhanced-dashboard>
- **Backend API**: <http://localhost:5003>
- **API Health Check**: <http://localhost:5003/api/health>

### **Start the System**

```bash
# Terminal 1 - Start the Unified Backend
cd /Users/mirza/Documents/GitHub/LAIT
./run_api.sh
# or directly with: python backend/enhanced_app.py

# Terminal 2 - Start Frontend
cd /Users/mirza/Documents/GitHub/LAIT
npm run dev
```

## 📖 **Complete Documentation**

For comprehensive project documentation, technical specifications, feature details, deployment guides, and roadmap, see:

**[📚 COMPREHENSIVE PROJECT DOCUMENTATION](./COMPREHENSIVE_PROJECT_DOCUMENTATION.md)**

This document contains:

- ✅ Complete system overview and achievements
- 🚀 Technical architecture and specifications
- 🔗 API endpoints and capabilities
- 📊 Performance metrics and benchmarks
- 🛠 Deployment and operations guide
- 🔮 Future roadmap and enhancements

## 🚀 **System Features**

- **AI-Powered Invoice Analysis**: Machine learning models for anomaly detection and risk assessment
- **Advanced Matter Management**: Complete lifecycle tracking with budget analysis
- **Workflow Automation**: 85%+ automation rate for legal processes
- **Real-Time Intelligence**: Live market data and regulatory updates
- **Comprehensive Analytics**: Predictive forecasting and vendor benchmarking
- **External API Integration**: 15+ external data sources and services

## 🛠 **Technology Stack**

- **Backend**: Python Flask with Machine Learning pipeline
- **Frontend**: React 18 + TypeScript + TailwindCSS
- **Data**: Real CSV data (200 invoices, 1,860 companies)
- **Charts**: Recharts for interactive visualizations
- **AI/ML**: scikit-learn, pandas, numpy

## 📁 **Project Structure**

After consolidation, the project structure has been simplified:

```text
/LAIT
├── backend/                   # Unified backend codebase
│   ├── enhanced_app.py        # Main production backend (all features)
│   ├── celery_worker.py       # Background task processing
│   ├── app.py                 # Flask factory pattern alternative
│   ├── config.py              # Configuration settings
│   ├── models.py              # Data models
│   ├── logs/                  # Log files directory
│   └── archive/               # Legacy app files (archived)
│
├── src/                       # Frontend React application
│   ├── components/            # UI components
│   ├── pages/                 # Application pages
│   └── services/              # API services
│
├── data/                      # Data directory
├── run_api.sh                 # Starter script for backend
├── cleanup.sh                 # Maintenance utilities
└── requirements.txt           # Python dependencies
```

## 📞 **Support**

For detailed technical documentation, deployment guides, API references, and development instructions, please refer to the [Comprehensive Project Documentation](./COMPREHENSIVE_PROJECT_DOCUMENTATION.md).

---

## Version Information

LAIT Enhanced Legal Intelligence System - Version 2.1 Production Ready
