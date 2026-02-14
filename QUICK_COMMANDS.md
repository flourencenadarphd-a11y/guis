# ⚡ Quick Commands Reference

## 🧪 Testing

```bash
# Test standalone app
cd C:\guis
streamlit run streamlit_app.py

# Test system
py test_system.py

# Test imports
py -c "import fastapi, streamlit, sqlalchemy, numpy; print('✅ OK')"
```

## 📦 Installation

```bash
# Install all dependencies
py -m pip install -r requirements.txt

# Or use batch file
install_dependencies.bat
```

## 🔄 GitHub

```bash
# Initialize (first time)
cd C:\guis
git init
git add .
git commit -m "Initial commit: GUIS"
git remote add origin https://github.com/flourencenadarphd-a11y/guis.git
git branch -M main
git push -u origin main

# Or use batch file
PUSH_TO_GITHUB.bat
```

## 🚀 Deployment

1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. New app → Select `flourencenadarphd-a11y/guis`
4. Main file: `streamlit_app.py`
5. Deploy!

## 🔗 Links

- **Local**: http://localhost:8501
- **GitHub**: https://github.com/flourencenadarphd-a11y/guis
- **Streamlit Cloud**: https://guis.streamlit.app (after deployment)

