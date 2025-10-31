# AI-Powered Bug Detection Tool

An intelligent bug detection system that uses machine learning and pattern recognition to automatically identify potential bugs, security vulnerabilities, and code quality issues in your codebase.

## 🚀 Features

- **AI-Powered Detection**: Machine learning model trained to identify common bug patterns
- **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, and more
- **Pattern-Based Analysis**: Detects security vulnerabilities and code smells using regex patterns
- **Severity Classification**: Categorizes issues by severity (Critical, High, Medium, Low)
- **REST API**: Easy-to-use API for integration with CI/CD pipelines
- **Batch Scanning**: Analyze multiple files in a single request
- **HTML Reports**: Generate comprehensive HTML reports for project scans
- **Real-time Analysis**: Get instant feedback on code quality

## 📋 Detected Issues

The tool identifies various types of bugs and vulnerabilities:

### Security Issues (Critical)
- Hardcoded passwords and API keys
- Use of dangerous functions like `eval()` and `exec()`
- Potential XSS vulnerabilities with `innerHTML`

### Code Quality Issues (High/Medium)
- Bare except clauses without exception types
- Use of `== None` instead of `is None`
- Unresolved TODO/FIXME comments
- Use of `var` instead of `let`/`const` in JavaScript

### Best Practice Issues (Low)
- Console.log statements in production code
- Code complexity indicators

## 🏗️ Architecture

The project consists of two main components:

### Backend API (`/backend/api`)
- Node.js/Express REST API server
- Handles HTTP requests and response formatting
- Manages temporary file operations
- Provides health check and batch scanning endpoints

### ML Engine (`/backend/ml_engine`)
- Python-based machine learning model
- Pattern-based bug detection using regex
- Feature extraction from code
- RandomForest classifier for bug prediction
- Model persistence (save/load trained models)

## 🛠️ Technologies Used

### Backend
- **Node.js** - API server runtime
- **Express** - Web framework
- **CORS** - Cross-origin resource sharing

### ML Engine
- **Python 3.x** - Core ML development
- **scikit-learn** - Machine learning algorithms
- **NumPy** - Numerical computing
- **TF-IDF Vectorization** - Text feature extraction

### Testing
- **pytest** - Python unit testing
- **Jest** - JavaScript testing framework
- **pytest-cov** - Code coverage for Python

## 📦 Installation

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8 or higher
- npm or yarn

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/johaankjis/AI-Powered-Bug-Detection-Tool.git
cd AI-Powered-Bug-Detection-Tool
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node.js dependencies (root)**
```bash
npm install
```

4. **Install API dependencies**
```bash
cd backend/api
npm install
cd ../..
```

5. **Train the model (optional)**
```bash
python backend/ml_engine/train.py
```

## 🚀 Usage

### Starting the API Server

```bash
cd backend/api
npm start
```

The API server will start on `http://localhost:3001` (default port).

For development with auto-reload:
```bash
npm run dev
```

### Scanning Code via API

**Single File Scan**
```bash
curl -X POST http://localhost:3001/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "code": "password = \"hardcoded123\"\nif x == None: pass",
    "language": "python",
    "filename": "example.py"
  }'
```

**Batch Scan**
```bash
curl -X POST http://localhost:3001/api/scan/batch \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"filename": "file1.py", "code": "..."},
      {"filename": "file2.js", "code": "..."}
    ]
  }'
```

**Check Supported Languages**
```bash
curl http://localhost:3001/api/languages
```

### Command-Line Usage

**Scan a single file**
```bash
python backend/ml_engine/detect.py path/to/your/file.py
```

**Scan entire project**
```bash
python scripts/scan_project.py
```

This generates:
- `scan_results.json` - Detailed JSON results
- `scan_report.html` - Visual HTML report

**Calculate code metrics**
```bash
python scripts/calculate_metrics.py
```

## 📊 API Reference

### Endpoints

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Bug Detection API",
  "version": "1.0.0",
  "timestamp": "2025-10-31T16:52:52.980Z"
}
```

#### `POST /api/scan`
Analyze a single code file

**Request Body:**
```json
{
  "code": "string (required)",
  "language": "string (optional, default: python)",
  "filename": "string (optional, default: temp.py)"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "has_bugs": true,
    "confidence": 0.87,
    "total_issues": 3,
    "severity_breakdown": {
      "critical": 1,
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "bugs_found": [
      {
        "line": 5,
        "severity": "critical",
        "message": "Hardcoded API key detected",
        "code": "api_key = \"sk-1234\"",
        "type": "pattern"
      }
    ]
  },
  "metadata": {
    "lines_analyzed": 50,
    "file_size": 1024,
    "scan_duration_ms": 150
  }
}
```

#### `POST /api/scan/batch`
Analyze multiple files

**Request Body:**
```json
{
  "files": [
    {"filename": "file1.py", "code": "..."},
    {"filename": "file2.js", "code": "..."}
  ]
}
```

#### `GET /api/languages`
Get supported programming languages

**Response:**
```json
{
  "supported": ["python", "javascript", "typescript", "java"],
  "experimental": ["go", "rust", "ruby"]
}
```

## 🧪 Testing

### Run Python tests
```bash
pytest tests/ -v
```

### Run tests with coverage
```bash
pytest tests/ --cov=backend/ml_engine --cov-report=html
```

### Run API tests
```bash
cd backend/api
npm test
```

### Run all tests with coverage
```bash
npm run test:ci
```

## 📁 Project Structure

```
AI-Powered-Bug-Detection-Tool/
├── backend/
│   ├── api/                    # REST API server
│   │   ├── server.js          # Express server
│   │   ├── routes/            # API route handlers
│   │   ├── tests/             # API tests
│   │   └── package.json       # API dependencies
│   └── ml_engine/             # Machine Learning engine
│       ├── model.py           # Bug detection model
│       ├── detect.py          # Detection script
│       └── train.py           # Model training
├── scripts/                    # Utility scripts
│   ├── scan_project.py        # Project-wide scanner
│   ├── calculate_metrics.py   # Code metrics
│   └── deploy.sh              # Deployment script
├── tests/                      # Test suite
│   ├── test_model.py          # Model unit tests
│   ├── test_integration.py    # Integration tests
│   └── conftest.py            # Pytest configuration
├── package.json               # Root dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

- `PORT` - API server port (default: 3001)
- `NODE_ENV` - Environment mode (development/production)

### Model Configuration

Edit `backend/ml_engine/model.py` to customize:
- Bug detection patterns
- Model hyperparameters
- Feature extraction logic
- Severity thresholds

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow existing code style
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with scikit-learn for machine learning capabilities
- Uses Express.js for robust API server
- Pattern detection inspired by common security best practices
- Testing frameworks: pytest and Jest

## 🐛 Reporting Issues

Found a bug? Have a feature request? Please open an issue on GitHub with:
- Clear description of the problem/request
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Code samples if applicable

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check existing documentation
- Review the API examples

## 🗺️ Roadmap

- [ ] Support for more programming languages
- [ ] Deep learning model integration
- [ ] IDE plugins (VS Code, IntelliJ)
- [ ] GitHub Actions integration
- [ ] Custom rule configuration
- [ ] Machine learning model fine-tuning
- [ ] Real-time collaboration features
- [ ] Advanced visualization dashboard

---

**Made with ❤️ for better code quality**
