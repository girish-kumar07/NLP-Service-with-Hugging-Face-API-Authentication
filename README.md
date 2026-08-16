# NLP-Service-with-Hugging-Face-API-Authentication

A modular Python CLI application integrating Hugging Face's Inference API for sentiment analysis, Named Entity Recognition (NER), and language detection with secure user authentication.

## ✨ Features

- **🔐 Secure Authentication**: Password hashing using PBKDF2-HMAC-SHA256 with per-user salt (200,000 iterations)
- **🧠 NLP Capabilities**:
  - Sentiment Analysis (emotion detection: joy, sadness, anger, fear, surprise, disgust, neutral)
  - Named Entity Recognition (NER)
  - Language Detection
- **🔄 Smart Fallback Mechanism**: Automatically switches between 6+ candidate models if one fails
- **🗄️ SQLite Database**: User management with thread-safe connections
- **📝 Comprehensive Logging**: File-based logging for debugging and audit trails
- **🛡️ Error Handling**: Robust error handling for network failures, API errors, and model loading issues

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **API**: Hugging Face Inference API
- **Database**: SQLite
- **Libraries**: requests, python-dotenv
- **Authentication**: PBKDF2-HMAC-SHA256 (hashlib)

## 📁 Project Structure
