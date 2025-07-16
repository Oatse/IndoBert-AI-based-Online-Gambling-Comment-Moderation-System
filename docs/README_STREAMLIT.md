# Judol Remover - Streamlit Version

## 🔄 Migration from Node.js to Streamlit

This document describes the conversion of the Judol Remover application from Node.js/Express to Streamlit.

## 📋 What Changed

### ✅ Converted Components

1. **Express Server → Streamlit App**
   - `src/ui/server.js` → `streamlit_app.py`
   - Web dashboard with real-time updates
   - Interactive UI components

2. **Facebook API Integration**
   - Node.js FB SDK → Python requests + facebook-sdk
   - `streamlit_facebook.py` handles all Facebook API calls

3. **Spam Detection**
   - Direct integration with Python model (no bridge needed)
   - Existing `python/services/spam_detector.py` used directly

4. **Auto Monitoring**
   - `src/monitors/auto_monitor.js` → `streamlit_monitor.py`
   - Background monitoring with threading
   - Real-time statistics and logging

5. **UI Components**
   - React components → Streamlit widgets
   - Collapsible comments interface
   - Real-time updates using session state

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+** installed
2. **Facebook Page Access Token** and Page ID
3. **IndoBERT Model** files in `python/models/`

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Make sure your `.env` file contains:
   ```
   PAGE_ID=your_facebook_page_id
   PAGE_ACCESS_TOKEN=your_page_access_token
   MODEL_PATH=./python/models
   CONFIDENCE_THRESHOLD=0.8
   ```

3. **Run the application:**
   ```bash
   # Using the startup script (recommended)
   python run_streamlit.py
   
   # Or directly with Streamlit
   streamlit run streamlit_app.py
   ```

4. **Access the dashboard:**
   Open your browser to `http://localhost:8501`

## 🎯 Features

### Dashboard
- **Real-time monitoring status**
- **Statistics display** (comments processed, spam removed)
- **Recent posts and comments** with spam detection
- **Auto-refresh** for live updates

### Manual Check
- **Select specific posts** to check for spam
- **Batch processing** of comments
- **Detailed results** with confidence scores

### Test Detector
- **Single text testing** for spam detection
- **Batch testing** with multiple comments
- **Adjustable confidence threshold**

### Settings
- **Facebook API configuration**
- **Spam detection settings**
- **Auto monitor configuration**
- **System status information**

### Logs
- **Activity logging** for all actions
- **Filterable log entries**
- **Real-time log updates**

## 🔧 Configuration

### Streamlit Configuration
The app uses `.streamlit/config.toml` for Streamlit-specific settings:
- Server port and CORS settings
- Theme customization
- Performance optimizations

### Environment Variables
Key environment variables in `.env`:
- `PAGE_ID`: Facebook Page ID
- `PAGE_ACCESS_TOKEN`: Facebook Page Access Token
- `MODEL_PATH`: Path to IndoBERT model files
- `CONFIDENCE_THRESHOLD`: Minimum confidence for spam classification

## 🏗️ Architecture

### File Structure
```
├── streamlit_app.py          # Main Streamlit application
├── streamlit_facebook.py     # Facebook API wrapper
├── streamlit_monitor.py      # Auto monitoring service
├── run_streamlit.py          # Startup script
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── python/
    ├── models/              # IndoBERT model files
    └── services/
        └── spam_detector.py # Spam detection service
```

### Key Components

1. **StreamlitJudolRemover Class**
   - Main application controller
   - Handles UI rendering and state management
   - Integrates all services

2. **FacebookAPI Class**
   - Wrapper for Facebook Graph API
   - Handles posts, comments, and deletion operations
   - Error handling and rate limiting

3. **AutoMonitor Class**
   - Background monitoring service
   - Threaded execution for real-time monitoring
   - Callback system for events

4. **SpamDetector Class**
   - IndoBERT-based spam detection
   - Direct integration (no bridge needed)
   - Fallback regex patterns

## 🔄 Real-time Features

### Auto-refresh Mechanism
- **Session state** for data persistence
- **Automatic page refresh** when monitoring is active
- **Background threading** for continuous monitoring

### Live Updates
- **Statistics updates** in real-time
- **New comment detection** and processing
- **Activity logging** with timestamps

## 🎨 UI/UX Improvements

### Streamlit Advantages
- **Native Python integration** (no bridge needed)
- **Built-in widgets** for forms and controls
- **Automatic responsive design**
- **Easy deployment** and sharing

### Interactive Features
- **Collapsible post sections** for better organization
- **Real-time metrics** with visual indicators
- **Filterable logs** and search functionality
- **Batch operations** for efficiency

## 🔒 Security Considerations

### Token Management
- **Environment variables** for sensitive data
- **No hardcoded credentials** in source code
- **Secure token handling** in API calls

### Error Handling
- **Graceful degradation** when services fail
- **Comprehensive logging** for debugging
- **User-friendly error messages**

## 📊 Performance

### Optimizations
- **Caching** for Facebook API responses
- **Batch processing** for multiple comments
- **Controlled concurrency** to avoid rate limits
- **Efficient memory usage** with session state

### Monitoring
- **Performance metrics** in headers
- **Cache hit/miss tracking**
- **API response time monitoring**

## 🚀 Deployment

### Local Development
```bash
python run_streamlit.py
```

### Production Deployment
1. **Streamlit Cloud**: Push to GitHub and deploy via Streamlit Cloud
2. **Docker**: Create Dockerfile for containerized deployment
3. **Heroku**: Deploy using Heroku's Python buildpack
4. **AWS/GCP**: Deploy on cloud platforms with Python support

## 🔧 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure model files are in `python/models/`
   - Check file permissions and paths

2. **Facebook API Errors**
   - Verify access token validity
   - Check page permissions
   - Monitor rate limits

3. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version compatibility

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 📈 Future Enhancements

### Planned Features
- **Multi-language support** for international pages
- **Advanced analytics** and reporting
- **Webhook integration** for real-time notifications
- **Machine learning model updates** and retraining

### Scalability
- **Database integration** for persistent storage
- **Redis caching** for improved performance
- **Load balancing** for high-traffic scenarios
- **Microservices architecture** for large deployments

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Install development dependencies
3. Make changes and test locally
4. Submit pull request with description

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Include error handling and logging

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Create GitHub issue with reproduction steps
4. Include environment and configuration details
