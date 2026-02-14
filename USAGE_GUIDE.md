# 🎓 GUIS - Complete Usage Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Frontend Overview](#frontend-overview)
3. [Step-by-Step Usage](#step-by-step-usage)
4. [Features Explained](#features-explained)
5. [Tips & Best Practices](#tips--best-practices)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- Backend server running

### Starting the Application

#### Step 1: Start Backend Server
```bash
# Windows
cd backend
python main.py

# Or use the batch file
start_backend.bat
```

The backend will start at: `http://localhost:8000`

#### Step 2: Start Frontend (New Terminal)
```bash
# Windows
cd frontend
streamlit run app.py

# Or use the batch file
start_frontend.bat
```

The frontend will open automatically at: `http://localhost:8501`

---

## 🖥️ Frontend Overview

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  🎓 Global University Intelligence System                │
│  Discover, Track, and Analyze University Programs        │
├──────────────┬───────────────────────────────────────────┤
│   SIDEBAR    │              MAIN CONTENT                  │
│              │                                            │
│ ⚙️ Config    │  [🔍 Search] [📚 Programs] [🏫 Uni] [📈]  │
│ 🔌 Status    │                                            │
│ 📊 Stats     │  Tab Content Area                          │
│ 🤖 AI        │                                            │
│ ⚡ Actions    │                                            │
└──────────────┴───────────────────────────────────────────┘
```

### Sidebar Components

1. **⚙️ Configuration**
   - API URL input (default: http://localhost:8000)
   - Change if backend is on different port/URL

2. **🔌 Connection Status**
   - Shows if frontend can connect to backend
   - ✅ Green = Connected
   - ❌ Red = Not Connected

3. **📊 System Statistics**
   - Real-time stats dashboard
   - Shows: Universities, Programs, UG/PG counts, etc.

4. **🤖 AI Assistant**
   - Ask questions about the data
   - Get AI-powered insights
   - Requires API key (Gemini/OpenAI)

5. **⚡ Quick Actions**
   - Refresh data
   - Export data (coming soon)

---

## 📖 Step-by-Step Usage

### Scenario 1: Finding Universities in a Country

**Goal**: Discover all universities in Germany

1. **Open the Frontend**
   - Navigate to `http://localhost:8501`
   - Ensure backend is running

2. **Go to Search Tab**
   - Click on "🔍 Search & Discover" tab

3. **Enter Country**
   - In the "🌍 Country" field, type: `Germany`
   - Click "🔍 Fetch Universities"

4. **Wait for Results**
   - System will scrape Wikipedia and other sources
   - This may take 30-60 seconds
   - Progress spinner will show

5. **View Results**
   - Table shows all found universities
   - Original names and translated names
   - GotoUniversity status

**Expected Output:**
```
✅ Fetched 50 universities
- Technical University of Munich
- Ludwig Maximilian University of Munich
- Heidelberg University
... (and more)
```

---

### Scenario 2: Searching for Specific Programs

**Goal**: Find "BSc IT" programs in Germany

1. **Ensure Universities are Fetched**
   - Complete Scenario 1 first, OR
   - System will fetch automatically if needed

2. **Enter Search Criteria**
   - Country: `Germany`
   - Course: `BSc IT` (or `Computer Science`, `Information Technology`)

3. **Click "🔍 Search Programs"**
   - System searches university websites
   - This may take 2-5 minutes
   - Be patient!

4. **Review Results**
   - Summary shows: Total, UG count, PG count
   - Expandable list of all programs
   - Each shows: University, Level, English status

**Expected Output:**
```
✅ Found 15 programs
📚 Total Programs: 15
🎓 Undergraduate: 12
🎯 Postgraduate: 3

Programs:
1. Technical University of Munich - UG - BSc IT
2. LMU Munich - UG - Computer Science
... (and more)
```

---

### Scenario 3: Browsing and Filtering Programs

**Goal**: Find all English-taught postgraduate programs

1. **Go to Programs Tab**
   - Click "📚 Programs Database"

2. **Set Filters**
   - Country: Select from dropdown (or "All")
   - Level: Select "PG"
   - Check "🌐 English Only"

3. **Click "🔍 Apply Filters"**
   - System loads matching programs

4. **View Results**
   - Table view with all programs
   - Detailed cards below
   - Click "📋 View Details" for more info

5. **Mark Programs as Visited**
   - Click "✅ Mark as Visited" button
   - Status updates immediately

---

### Scenario 4: Using AI Assistant

**Goal**: Get insights about programs

1. **Open Sidebar**
   - Scroll to "🤖 AI Assistant" section

2. **Enter Question**
   - Example: "What are the top 5 universities for Computer Science in Germany?"
   - Example: "Compare undergraduate vs postgraduate programs"
   - Example: "Which programs are taught in English?"

3. **Click "💬 Query AI"**
   - AI processes your question
   - Response appears below

**Note**: Requires API key (Gemini or OpenAI) to be set in environment variables.

---

### Scenario 5: Viewing Analytics

**Goal**: Understand data distribution

1. **Go to Analytics Tab**
   - Click "📈 Analytics"

2. **View Charts**
   - Program distribution (UG vs PG)
   - Language distribution (English vs Non-English)
   - Summary statistics

3. **Interpret Data**
   - Use charts to understand trends
   - Identify gaps in data
   - Plan next searches

---

## 🎯 Features Explained

### 1. University Discovery
- **Source**: Wikipedia, government portals
- **Translation**: Automatic translation to English
- **Deduplication**: Removes duplicate entries
- **GotoUniversity Check**: Verifies against CSV database

### 2. Program Search
- **Multi-Strategy**: Uses sitemap, search pages, common paths
- **Validation**: Only returns HTTP 200 pages with course keywords
- **Content Check**: Verifies academic structure keywords

### 3. Classification (UG/PG)
- **Rule-Based**: Keywords (Bachelor, Master, etc.)
- **ML-Powered**: SentenceTransformers + scikit-learn
- **Confidence Score**: Shows how certain the classification is

### 4. Language Detection
- **Methods**: HTML lang attribute, keywords, langdetect
- **Confidence**: Returns confidence score
- **Accuracy**: Multiple methods for reliability

### 5. Change Detection
- **Hash-Based**: SHA256 hash of page content
- **Header-Based**: ETag, Last-Modified headers
- **Automatic**: Detects when pages are updated

### 6. Visit Tracking
- **Manual**: Click button to mark as visited
- **Visual**: Green/red indicators
- **Persistent**: Stored in database

---

## 💡 Tips & Best Practices

### Search Tips

1. **Country Names**
   - Use full names: "Germany" not "DE"
   - Use English names: "United States" not "USA"
   - Be specific: "United Kingdom" not "UK"

2. **Course Names**
   - Be flexible: "Computer Science" finds "CS", "IT", etc.
   - Use abbreviations: "BSc IT" works
   - Try variations: "Data Science", "Data Analytics"

3. **Performance**
   - First search takes longer (scraping)
   - Subsequent searches are faster (cached)
   - Be patient with large countries

### Filtering Tips

1. **Start Broad**
   - First, search without filters
   - Then narrow down with filters

2. **Combine Filters**
   - Country + Level + English = Very specific results
   - Use "All" to see everything

3. **Save Searches**
   - Note down successful search terms
   - Reuse for similar searches

### Data Management

1. **Mark Visited**
   - Mark programs you've reviewed
   - Helps track progress
   - Filter by visited status

2. **Regular Updates**
   - Re-run searches periodically
   - System detects changes automatically
   - Metadata updates on refresh

3. **Export Data**
   - Use table view to copy data
   - Export feature coming soon
   - Use API directly for bulk export

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to backend API"

**Solutions:**
1. Check if backend is running: `http://localhost:8000`
2. Verify API URL in sidebar
3. Check firewall/antivirus settings
4. Try restarting backend server

### Problem: "No universities found"

**Solutions:**
1. Check country name spelling
2. Try different country name format
3. Check internet connection
4. Wikipedia might be blocking (try later)

### Problem: "No programs found"

**Solutions:**
1. Ensure universities are fetched first
2. Try different course keywords
3. Some universities might not have public course pages
4. Check if course name is too specific

### Problem: "Search taking too long"

**Solutions:**
1. This is normal for first-time searches
2. Large countries take longer
3. Check internet speed
4. Try smaller countries first

### Problem: "AI Assistant not working"

**Solutions:**
1. Check if API key is set: `GEMINI_API_KEY` or `OPENAI_API_KEY`
2. Verify API key is valid
3. Check API quota/limits
4. Try simpler questions

### Problem: "Programs showing incorrect level"

**Solutions:**
1. Check confidence score (low = uncertain)
2. Some programs are ambiguous
3. Use manual review for important decisions
4. ML model improves with more data

---

## 📊 Understanding the Data

### Program Status Indicators

- 🟢 **Visited**: You've reviewed this program
- 🔴 **Not Visited**: Not yet reviewed
- ✅ **English**: Program taught in English
- ❌ **Non-English**: Program in another language
- ⭐ **In GotoUni**: Found in GotoUniversity database
- 📝 **Not in GotoUni**: Not in database

### Level Classifications

- **UG (Undergraduate)**: Bachelor's level programs
- **PG (Postgraduate)**: Master's/PhD level programs

### Confidence Scores

- **High (80%+)**: Very certain classification
- **Medium (50-80%)**: Reasonably certain
- **Low (<50%)**: Uncertain, manual review recommended

---

## 🎓 Example Workflows

### Workflow 1: Research Study Options

1. Search universities in target country
2. Search for desired course
3. Filter by English + Level
4. Review program details
5. Mark interesting programs as visited
6. Export list for further research

### Workflow 2: Compare Programs

1. Search programs in multiple countries
2. Use Analytics tab to compare
3. Use AI Assistant for insights
4. Filter by specific criteria
5. Create shortlist

### Workflow 3: Track Changes

1. Search programs initially
2. Mark visited programs
3. Re-run search after some time
4. System detects changes automatically
5. Review updated programs

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review README.md
3. Check backend logs
4. Verify all dependencies installed

---

## 🎉 You're Ready!

You now know how to use GUIS effectively. Start exploring and discovering university programs worldwide!

**Happy Searching! 🎓**

