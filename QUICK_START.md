# 🚀 GUIS Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start Backend

**Windows:**
```bash
start_backend.bat
```

**Or manually:**
```bash
cd backend
python main.py
```

✅ Backend running at: `http://localhost:8000`

## Step 3: Start Frontend

**Windows:**
```bash
start_frontend.bat
```

**Or manually:**
```bash
cd frontend
streamlit run app.py
```

✅ Frontend opens at: `http://localhost:8501`

## Step 4: Use the System

### Quick Example: Find IT Programs in Germany

1. **Open Frontend** → Go to "🔍 Search & Discover" tab
2. **Fetch Universities** → Enter "Germany" → Click "🔍 Fetch Universities"
3. **Search Programs** → Enter "BSc IT" → Click "🔍 Search Programs"
4. **View Results** → Browse found programs
5. **Mark Visited** → Click "✅ Mark as Visited" for programs you review

### That's It! 🎉

For detailed usage, see [USAGE_GUIDE.md](USAGE_GUIDE.md)

---

## 🎯 Common First Steps

1. ✅ Check connection status in sidebar (should be green)
2. ✅ Fetch universities for your target country
3. ✅ Search for your desired course/program
4. ✅ Filter and browse results
5. ✅ Mark interesting programs as visited

---

## ⚠️ Troubleshooting

**Backend won't start?**
- Check if port 8000 is available
- Verify Python version (3.8+)
- Check all dependencies installed

**Frontend can't connect?**
- Ensure backend is running
- Check API URL in sidebar
- Verify firewall settings

**No results found?**
- Try different country names
- Use broader course keywords
- Check internet connection

---

**Need Help?** See [USAGE_GUIDE.md](USAGE_GUIDE.md) for complete documentation.

