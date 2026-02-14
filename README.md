# Global University Intelligence System (GUIS)

A production-ready web application for discovering and tracking university programs worldwide. The system fetches universities by country, searches for specific courses, classifies programs (UG/PG), detects English instruction, and tracks visited links.

## 🎯 Features

- **University Discovery**: Fetch universities from Wikipedia and education portals
- **Translation**: Automatic translation of non-English university names
- **Course Search**: Intelligent search for programs matching course keywords
- **Classification**: ML-powered UG/PG classification with confidence scores
- **Language Detection**: Detects if programs are taught in English
- **Change Detection**: Tracks content changes using hash and HTTP headers
- **Visit Tracking**: Mark and track visited program links
- **GotoUniversity Integration**: Checks against gotouniversity.csv database
- **AI Queries**: Gemini/OpenAI integration for intelligent queries
- **Real-time Filtering**: Filter by country, course, level, and language

## 🏗️ Architecture

### Backend
- **FastAPI**: RESTful API server
- **SQLite + SQLAlchemy**: Database and ORM
- **BeautifulSoup**: Web scraping
- **SentenceTransformers**: ML embeddings
- **scikit-learn**: Classification models

### Frontend
- **Streamlit**: Interactive web interface

## 📁 Project Structure

```
guis/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py           # Database models
│   ├── scraper.py            # University and course scraping
│   ├── translator.py         # Translation module
│   ├── language_detector.py  # English detection
│   ├── ml_classifier.py      # UG/PG classification
│   ├── metadata_checker.py   # Change detection
│   ├── gotouni_checker.py    # GotoUniversity checker
│   └── ai_query.py           # AI integration
├── frontend/
│   └── app.py                # Streamlit frontend
├── data/
│   └── gotouniversity.csv     # University database
├── requirements.txt
└── README.md
```

## 🚀 Setup Instructions

### 1. Clone/Download the Project

```bash
cd guis
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data

Create `data/gotouniversity.csv` with university names (one per line, first column):

```csv
University Name
Harvard University
MIT
Stanford University
...
```

### 5. Configure API Keys (Optional)

For AI features, set environment variables:

```bash
# Windows
set GEMINI_API_KEY=your_key_here
set OPENAI_API_KEY=your_key_here

# Linux/Mac
export GEMINI_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
```

## 🏃 Running the Application

### Start Backend Server

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Start Frontend

In a new terminal:

```bash
cd frontend
streamlit run app.py
```

The frontend will open at `http://localhost:8501`

## 📖 Usage

### 1. Fetch Universities

1. Go to the **Search** tab
2. Enter a country (e.g., "Germany")
3. Click "Fetch Universities"
4. System will scrape and translate university names

### 2. Search Programs

1. Enter a country and course name (e.g., "Germany", "BSc IT")
2. Click "Search Programs"
3. System will search university websites and return valid program links
4. Results show UG/PG classification and English status

### 3. Browse and Filter

1. Go to the **Programs** tab
2. Apply filters (country, course, level, English only)
3. View programs in a table
4. Click to expand for details
5. Mark programs as visited

### 4. AI Queries

1. Use the sidebar AI Query section
2. Ask questions about the data
3. Get intelligent insights

## 🔧 API Endpoints

### Universities
- `POST /api/universities/fetch` - Fetch universities for a country
- `GET /api/universities` - Get all universities

### Programs
- `POST /api/programs/search` - Search for programs
- `GET /api/programs` - Get programs with filters
- `POST /api/programs/visit` - Mark program as visited

### Statistics
- `GET /api/stats` - Get system statistics

### AI
- `POST /api/ai/query` - Send AI query

## 🗄️ Database Schema

### Universities Table
- `id`: Primary key
- `original_name`: Original university name
- `translated_name`: English translation
- `country`: Country name
- `exists_in_gotouniversity`: Boolean

### Programs Table
- `id`: Primary key
- `university_id`: Foreign key
- `course_name`: Course name
- `program_url`: Program URL
- `level`: UG or PG
- `taught_in_english`: Boolean
- `visited`: Boolean
- `content_hash`: SHA256 hash
- `embedding_vector`: ML embedding
- `last_checked`: Timestamp
- `last_modified_header`: HTTP header
- `etag`: HTTP ETag
- `confidence_score`: ML confidence

## 🚀 Deployment to Streamlit Cloud

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/guis.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `frontend/app.py`
6. Add environment variables if needed:
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`
7. Click "Deploy"

### 3. Update API URL

In `frontend/app.py`, update `API_BASE_URL` to your deployed backend URL:

```python
API_BASE_URL = "https://your-backend-url.com"
```

### 4. Deploy Backend

Deploy FastAPI backend to:
- **Heroku**: Use `Procfile` with `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Auto-detects FastAPI
- **Render**: Use Python environment
- **AWS/GCP**: Use container or serverless

## 🧪 Testing

Test the API:

```bash
# Fetch universities
curl -X POST "http://localhost:8000/api/universities/fetch" \
  -H "Content-Type: application/json" \
  -d '{"country": "Germany"}'

# Search programs
curl -X POST "http://localhost:8000/api/programs/search" \
  -H "Content-Type: application/json" \
  -d '{"country": "Germany", "course": "BSc IT"}'
```

## 📝 Notes

- **Accuracy**: Only returns URLs with HTTP 200 status
- **Rate Limiting**: Built-in retry logic and exponential backoff
- **Caching**: Translation results are cached
- **ML Model**: Initial model is pre-trained, improves with usage
- **Change Detection**: Uses SHA256 hash and HTTP headers

## 🔒 Security Considerations

- Never commit API keys
- Use environment variables for secrets
- Validate all user inputs
- Implement rate limiting for production
- Use HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify all dependencies are installed
- Check database file permissions

### Frontend can't connect
- Ensure backend is running
- Check API_BASE_URL in app.py
- Verify CORS settings

### Scraping fails
- Some websites block scrapers
- Check internet connection
- Verify website URLs are accessible

### ML model errors
- Ensure sentence-transformers is installed
- Check disk space for model downloads
- Verify scikit-learn version compatibility

## 📧 Support

For issues and questions, please open an issue on GitHub.

