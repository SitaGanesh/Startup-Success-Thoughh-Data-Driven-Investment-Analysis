# Contributing to Startup Success Prediction

Welcome to the **Startup Success Through Data-Driven Investment Analysis** project! This comprehensive guide will help you contribute effectively to our end-to-end ML pipeline integrated with Amazon Nova AI services.

---

## Prerequisites & System Requirements

### **Development Environment**
- **Python**: 3.9+ (recommended 3.11+)
- **Node.js**: 18+ (for frontend development)
- **Git**: Latest version
- **VS Code**: Recommended IDE with extensions
- **AWS Account**: With Bedrock access (for Nova AI features)

### **Required VS Code Extensions**
```bash
# Python Development
ms-python.python
ms-python.flake8
ms-python.black-formatter

# Frontend Development  
bradlc.vscode-tailwindcss
esbenp.prettier-vscode

# Git & GitHub
GitHub.vscode-pull-request-github
```

### **AWS Services Access**
- **AWS Bedrock**: For Amazon Nova models access
- **IAM Permissions**: Bedrock API access with appropriate policies

---

## Quick Start Setup

### **Step 1: Clone & Fork Repository**
```bash
# Fork the repository first, then clone your fork
git clone https://github.com/YOUR-USERNAME/Startup-Success-Thoughh-Data-Driven-Investment-Analysis.git
cd Startup-Success-Thoughh-Data-Driven-Investment-Analysis

# Add upstream remote for keeping updated
git remote add upstream https://github.com/SitaGanesh/Startup-Success-Thoughh-Data-Driven-Investment-Analysis.git
```

### **Step 2: Backend Setup**
```bash
# Create Python virtual environment
python -m venv backend/venv

# Activate (Windows)
backend\venv\Scripts\activate

# Activate (Mac/Linux)
source backend/venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install ML package in development mode
cd ../ML
pip install -e .
```

### **Step 3: Frontend Setup**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Verify installation
npm run dev --version
```

### **Step 4: Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: AWS_BEARER_TOKEN_BEDROCK, AWS_BEDROCK_REGION
```

---

## Branch Management & Workflow

### **Branch Naming Convention**
```bash
# Feature branches
feature/startup-analysis-enhancement
feature/ml-model-optimization
feature/nova-chat-improvement

# Bug fixes
bugfix/prediction-api-error
bugfix/frontend-validation

# Documentation
docs/api-endpoint-updates
docs/troubleshooting-guide
```

### **Create & Switch Branch**
```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Or create from main
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

---

## Development Workflow

### **Backend Development**
```bash
# Start backend server
cd backend
python main.py
# Server runs on http://localhost:8000

# Access API documentation
# http://localhost:8000/docs

# Run ML pipeline tests
cd ../ML
python -m pytest tests/
```

### **Frontend Development**
```bash
# Start development server
cd frontend
npm run dev
# App runs on http://localhost:5173

# Build for production
npm run build

# Run linting
npm run lint

# Type checking (if TypeScript enabled)
npm run type-check
```

### **Full Stack Development**
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: ML Pipeline (if training)
cd ML && python src/components/model_trainer.py
```

---

## Code Standards & Guidelines

### **Python Code Standards**
```python
# Use Black for formatting
black .

# Use Flake8 for linting
flake8 .

# Follow PEP 8 guidelines
# Maximum line length: 88 characters
# Use type hints where possible
# Document functions with docstrings

def predict_startup_success(
    startup_data: Dict[str, Any], 
    model_path: str = "artifacts/model.pkl"
) -> Tuple[int, float]:
    """
    Predict startup success probability.
    
    Args:
        startup_data: Dictionary containing startup features
        model_path: Path to trained model file
        
    Returns:
        Tuple of (prediction, probability_score)
    """
    pass
```

### **JavaScript/React Code Standards**
```jsx
// Use Prettier for formatting
npm run lint

// Follow React best practices
// Use functional components with hooks
// Implement proper error boundaries
// Use meaningful component names

const PredictStartup = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({});
  
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    await onSubmit(formData);
  }, [formData, onSubmit]);

  return (
    <form onSubmit={handleSubmit} className="startup-form">
      {/* Form content */}
    </form>
  );
};
```

### **Commit Message Standards**
```bash
# Format: type(scope): description
# Types: feat, fix, docs, style, refactor, test, chore

feat(ml): add xgboost hyperparameter tuning
fix(api): resolve prediction endpoint timeout
docs(readme): update installation instructions
test(frontend): add unit tests for prediction form
refactor(nova): optimize client authentication
style(ui): improve responsive design for mobile
chore(deps): update scikit-learn to version 1.7.2
```

---

## Testing & Quality Assurance

### **Backend Testing**
```bash
# Run all tests
cd backend
python -m pytest

# Run specific test file
python -m pytest tests/test_predict_api.py

# Run with coverage
python -m pytest --cov=src tests/

# Run ML pipeline tests
cd ../ML
python -m pytest tests/
```

### **Frontend Testing**
```bash
# Run unit tests
cd frontend
npm test

# Run end-to-end tests
npm run test:e2e

# Check accessibility
npm run test:a11y
```

### **Integration Testing**
```bash
# Test API endpoints
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"funding_total_usd": 1000000, "founded_year": 2020}'

# Test Nova AI integration
curl -X POST http://localhost:8000/api/nova/analyze \
  -H "Content-Type: application/json" \
  -d '{"startup_data": {...}}'
```

---

## Pull Request Process

### **Pre-Submission Checklist**
- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] Documentation updated if needed
- [ ] No sensitive data in commits
- [ ] Branch is up-to-date with main
- [ ] Commit messages follow conventions

### **Create Pull Request**
```bash
# Push your feature branch
git push origin feature/your-feature-name

# Create PR via GitHub CLI
gh pr create --title "feat(ml): enhance prediction accuracy" \
  --body "## Description
- Added new feature engineering techniques
- Improved model validation
- Updated documentation

## Testing
- Unit tests: 
- Integration tests: 
- Manual testing: "
```

### **PR Review Process**
1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainer review required
3. **Integration Testing**: Full stack validation
4. **Documentation**: Ensure docs are updated
5. **Approval & Merge**: After successful review

---

## Bug Reporting & Issue Templates

### **Bug Report Template**
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11, macOS 13.0]
- Python: [e.g., 3.11.0]
- Node.js: [e.g., 18.17.0]
- Browser: [e.g., Chrome 120.0]

## Additional Context
Screenshots, logs, or additional information
```

### **Feature Request Template**
```markdown
## Feature Description
Clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches you thought about

## Additional Context
Any relevant information or constraints
```

---

## Project Structure for Contributors

```
Startup-Success-Thoughh-Data-Driven-Investment-Analysis/
├── CONTRIBUTING.md              # This file
├── README.md                   # Main project documentation
├── .env.example                # Environment variables template
├── backend/                    # FastAPI application
│   ├── main.py                # Main FastAPI app
│   ├── requirements.txt       # Python dependencies
│   └── tests/                # Backend tests
├── frontend/                   # React application
│   ├── src/                  # React source code
│   ├── package.json           # Node dependencies
│   └── __tests__/            # Frontend tests
├── ML/                        # Machine Learning pipeline
│   ├── src/                  # ML source code
│   ├── artifacts/             # Trained models
│   └── tests/                # ML tests
├── nova/                      # Amazon Nova integration
│   ├── client.py              # Nova API client
│   ├── agent.py               # Agentic workflows
│   └── tests/                # Nova tests
└── data/                      # Training datasets
```

---

## Development Tools & Scripts

### **Useful Scripts**
```bash
# Run full test suite
npm run test:all

# Format all code
npm run format:all

# Lint all code
npm run lint:all

# Build and deploy
npm run deploy:staging

# Database migrations (if applicable)
npm run db:migrate
```

### **Development Utilities**
```bash
# Check Python dependencies
pip-audit

# Check Node.js vulnerabilities
npm audit

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

---

## Additional Resources

### **Documentation**
- [API Documentation](http://localhost:8000/docs)
- [ML Pipeline Guide](ML/README.md)
- [Frontend Component Guide](frontend/README.md)
- [AWS Nova Integration](nova/README.md)

### **Learning Resources**
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Scikit-learn Guide](https://scikit-learn.org/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

### **Community**
- **Discussions**: GitHub Discussions tab
- **Issues**: GitHub Issues for bugs and features
- **Discord**: [Join our Discord](https://discord.gg/invite-link)

---

## Contribution Areas

### **High Priority Areas**
1. **ML Model Improvements**
   - Feature engineering enhancements
   - Model hyperparameter tuning
   - New algorithm implementations

2. **Frontend UX/UI**
   - Responsive design improvements
   - Accessibility enhancements
   - Performance optimizations

3. **Nova AI Integration**
   - New agentic workflows
   - Enhanced prompt engineering
   - Multimodal capabilities

### **Good First Issues**
- Documentation improvements
- Bug fixes with clear reproduction steps
- Unit test additions
- Code refactoring

---

## Recognition & Rewards

### **Contributor Recognition**
- **Hall of Fame**: Top contributors in README
- **Release Notes**: Mentioned in release announcements
- **Swag**: Merit-based project swag
- **Certificates**: Contribution certificates

### **Code of Conduct**
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow professional communication standards

---

## Getting Help

### **For Technical Issues**
1. Check existing [Issues](https://github.com/SitaGanesh/Startup-Success-Thoughh-Data-Driven-Investment-Analysis/issues)
2. Search [Discussions](https://github.com/SitaGanesh/Startup-Success-Thoughh-Data-Driven-Investment-Analysis/discussions)
3. Create new issue with detailed information

### **For General Questions**
- Start a discussion in GitHub Discussions
- Join our Discord community
- Email maintainers at [project-email@example.com]

---

## Final Checklist Before Contributing

- [ ] Read this entire guide
- [ ] Set up development environment
- [ ] Forked and cloned repository
- [ ] Created appropriate branch
- [ ] Tested changes locally
- [ ] Followed code standards
- [ ] Updated documentation
- [ ] Ready to submit PR

---

**Thank you for contributing to our project!** 

Every contribution, whether it's a bug fix, feature enhancement, documentation improvement, or community support, helps make this project better for everyone.

---

*Last updated: March 2026*
