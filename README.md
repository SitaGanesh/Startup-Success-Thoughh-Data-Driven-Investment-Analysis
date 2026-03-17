# 🚀 Veritas - Startup Success Prediction Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-19.2.4-blue?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-green?style=flat-square&logo=fastapi)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?style=flat-square&logo=amazon-aws)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-Academic-lightgrey?style=flat-square)

> **🎯 Veritas: Bridging the Gap Between Predictive Data and Strategic Reasoning**

## Project Overview
This project builds a comprehensive end-to-end Machine Learning pipeline integrated with Amazon Nova AI services to predict whether a startup will be **successful (1)** or **failed (0)** based on historical features. The system combines:
- ✅ Binary prediction (Success / Failure) with probability scores
- 🤖 Amazon Nova AI-powered analysis and reasoning
- 🌐 Full-stack web application with React frontend and FastAPI backend
- 📊 Real-time market intelligence and document analysis

---

## 🌐 Veritas Frontend User Interface

![Predict Success Page](architecture-images/predict-success-page.png)
![Market Research Page](architecture-images/market-research.png)
![Document Analysis Page](architecture-images/document-analysis-page.png)
![Deep Startup Analysis Page](architecture-images/deep-startup-analysis-page.png)
![Landing Page](architecture-images/landing-page.png)

> **Experience Veritas**: A modern, intuitive interface that makes complex startup analysis simple and actionable.

---

## 🏗️ System Architecture

### **High-Level Data Flow**

![High-Level Architecture Diagram](architecture-images/high-level-architecture.png)

### **Architecture Components**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React)                       │
├─────────────────────────────────────────────────────────────────┤
│  Pages: Home | Predict | Compare | Analyze | Market | Document  │
│  Components: Navbar | Forms | Results Display | Chat Interface   │
│  API Client: Axios-based communication with backend             │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST API Calls
┌─────────────────────────────────────────────────────────────────┐
│                  Backend Layer (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  Core Routes:                                                   │
│  • /api/predict - ML prediction                                 │
│  • /api/nova/analyze - AI-powered startup analysis              │
│  • /api/nova/chat - Interactive advisor chat                   │
│  • /api/nova/market - Market intelligence reports              │
│  • /api/nova/document - Document/pitch analysis                 │
│  • /api/nova/agent - Agentic 4-step investment workflow        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────┐    ┌─────────────────────────────────┐
│      ML Pipeline Layer       │    │      Amazon Nova AI Layer        │
├─────────────────────────────┤    ├─────────────────────────────────┤
│  • Data Ingestion           │    │  • Text Analysis (Nova Pro/Lite) │
│  • Feature Engineering      │    │  • Multimodal Image Analysis     │
│  • Model Training           │    │  • Conversational AI Chat        │
│  • Prediction Pipeline      │    │  • Document Understanding        │
│  • Model Storage (PKL)      │    │  • Agentic Workflow Orchestration │
└─────────────────────────────┘    └─────────────────────────────────┘
                    │                               │
                    ▼                               ▼
        ┌─────────────────────────────────────────────────────┐
        │              Data & Storage Layer                  │
        ├─────────────────────────────────────────────────────┤
        │  • ML Artifacts: model.pkl, preprocessor.pkl       │
        │  • Training Data: CSV datasets                     │
        │  • Model Results: Performance metrics              │
        │  • Environment: AWS Bedrock Nova credentials        │
        └─────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow & Features

### **Core Capabilities**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![AWS](https://img.shields.io/badge/AWS_Bedrock-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)

### **Key Features**
- **ML Prediction Engine**: Random Forest, XGBoost, Logistic Regression, SVC, SVR
- **Amazon Nova AI Services**: Startup Analysis, Advisor Chat, Market Intelligence, Document Analysis
- **Real-time Processing**: Instant predictions with confidence scoring
- **Multimodal Analysis**: Text and image processing capabilities

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+ & Node.js 18+
- AWS Account with Bedrock access

### **Setup Commands**
```bash
# Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Frontend  
cd frontend && npm install

# Environment
cp .env.example .env  # Add AWS credentials
```

### **Run Application**
```bash
# Terminal 1: Backend
python main.py  # http://localhost:8000

# Terminal 2: Frontend
npm run dev     # http://localhost:5173
```

---

## Model Performance & Evaluation

### ML Model Metrics
- Primary Metric: ROC-AUC
- Secondary Metrics: Accuracy, Precision, Recall, F1-Score
- Best Model: Selected based on highest ROC-AUC
- Confidence Bands: Statistical uncertainty quantification

### Feature Importance
- Top Features: Funding metrics, startup age, market category
- Visualization: SHAP values for model explainability
- Interpretation: Business-relevant feature contributions

---

## Amazon Nova AI Capabilities

### Available Models
- amazon.nova-micro-v1:0 - Fast, cost-effective text processing
- amazon.nova-lite-v1:0 - Multimodal (text + images)
- amazon.nova-pro-v1:0 - Highest capability analysis
- amazon.nova-lite-v2:0 - Nova 2 series multimodal
- amazon.nova-pro-v2:0 - Nova 2 series highest capability

### AI Use Cases
1. Startup Analysis: Strategic assessment based on ML predictions
2. Investment Advisor: Q&A about funding and growth strategies
3. Market Research: Industry trends and competitive analysis
4. Document Intelligence: Pitch deck evaluation and recommendations
5. Agentic Workflow: Multi-step investment decision process

---

## Integration & Extensibility

### API Integration
- RESTful Design: Standard HTTP methods and status codes
- JSON Communication: Structured request/response format
- Error Handling: Comprehensive error messages and logging
- CORS Support: Cross-origin frontend integration

### Database Integration Ready
- Model Storage: PKL files for trained models
- Results Caching: Performance metrics storage
- User Data: Ready for user management integration
- Session Management: Chat history and user preferences

### Scalability Features
- Async Processing: Background model training
- Batch Predictions: Handle multiple startups simultaneously
- Load Balancing Ready: FastAPI production deployment
- Containerizable: Docker configuration prepared

---

## Testing & Validation

### Test Coverage
- API Tests: Endpoint validation and error handling
- ML Pipeline Tests: Data preprocessing and prediction accuracy
- Frontend Tests: Component rendering and user interactions
- Integration Tests: End-to-end workflow validation

### Quality Assurance
- Model Validation: Cross-validation and performance metrics
- Data Quality: Missing value handling and outlier detection
- API Reliability: Error handling and response validation
- User Experience: Interface responsiveness and error messages

---

## Business Impact & Use Cases

### Target Users
- Startup Founders: Evaluate success probability and improvement strategies
- Venture Capitalists: Data-driven investment decision support
- Accelerators: Startup screening and program selection
- Corporate Development: Acquisition target evaluation

### Value Proposition
- Quantitative Confidence: ML-based success probability
- Qualitative Insights: AI-powered strategic analysis
- Risk Assessment: Comprehensive risk factor identification
- Decision Support: Evidence-based investment recommendations

---

## Future Enhancements

### Technical Improvements
- Model Versioning: MLflow integration for model tracking
- Real-time Data: Live market data integration
- Advanced Analytics: Time-series forecasting capabilities
- Mobile App: React Native mobile application

### AI Enhancements
- Custom Models: Fine-tuned Nova models for startup domain
- Voice Interface: Speech-to-text for hands-free analysis
- Advanced Agents: More sophisticated agentic workflows
- Knowledge Graph: Industry relationship mapping

### Platform Features
- User Authentication: Multi-user support with profiles
- Collaboration Tools: Team-based analysis sharing
- Integration APIs: Third-party platform connections
- Analytics Dashboard: Usage and performance metrics

---

## 📚 Documentation

- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md) - Development contribution guide
- **Integration**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Frontend-backend integration
- **Setup**: [FRONTEND_SETUP.md](FRONTEND_SETUP.md) - React app configuration
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & solutions
- **Hackathon**: [HACKATHON_SUBMISSION.md](HACKATHON_SUBMISSION.md) - Amazon Nova Hackathon details
- **Testing**: [TEST_CASES_AND_RESULTS.md](TEST_CASES_AND_RESULTS.md) - Test documentation

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code contribution guidelines  
- Branch management workflow
- Testing requirements

### Quick Start for Contributors
```bash
# 1. Fork and clone
git clone https://github.com/your-username/Startup-Success-Thoughh-Data-Driven-Investment-Analysis.git

# 2. Create feature branch
git checkout -b your-feature-name

# 3. Install dependencies
# Follow setup instructions above

# 4. Make changes and test
# Run tests and validate functionality

# 5. Submit pull request
# With detailed description of changes
```

---

## 🎯 Amazon Nova Hackathon

- **Category**: Agentic AI & Multimodal Understanding
- **Compliance**: Full AWS Bedrock Nova integration  
- **Demo**: Complete working application with all features
- **Submission**: Ready-to-deploy solution with documentation

---

## 📞 Support & Contact

For questions, issues, or contributions:
- **Issues**: GitHub repository issue tracker
- **Documentation**: Comprehensive guides in repository
- **Community**: Collaboration through pull requests
