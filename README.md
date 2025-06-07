# Swasthya-AI
## Bridging India's Healthcare Access Gaps

## 📋 Project Overview

Swasthya-AI is an AI-powered healthcare platform that addresses critical gaps in India's healthcare system through three integrated services:

- **Medical Chatbot**: Personalized medical guidance with voice interactions
- **Emotional Diary**: Sentiment analysis and mood tracking with therapeutic support  
- **Prescription OCR**: Handwritten prescription digitization with generic alternatives

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Models**: LangChain, OpenAI GPT, Ollama LLMs
- **Sentiment Analysis**: PyTorch
- **OCR**: Tesseract
- **Automation**: n8n workflows
- **Database**: Supabase
- **TTS**: Google Text-to-Speech

## 🚀 Installation & Setup

### Prerequisites
- Docker
- Python 3.8+
- Git

### Step 1: Install n8n using Docker
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Step 2: Run n8n locally
n8n will be accessible at `http://localhost:5678`

### Step 3: Setup n8n architecture
1. Navigate to `http://localhost:5678`
2. Import workflow from `sample.json` file
3. This configures the automated OCR processing pipeline

### Step 4: Run the application
```bash
# Clone repository
git clone https://github.com/8riddesh/SwasthyaAi.git
cd SwasthyaAi

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Step 5: Access the application
Open `http://localhost:8501` in your browser

## 🔧 Configuration

Set up environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
N8N_WEBHOOK_URL=your_n8n_webhook_url
```

## 📱 Features

- Multilingual voice-enabled healthcare chatbot
- Real-time emotion tracking and therapeutic support
- Automated prescription digitization
- Text-to-speech accessibility features
- Secure data storage with vector embeddings
