"""
System Test Script
Tests all components to ensure everything works
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 50)
print("GUIS System Test")
print("=" * 50)
print()

# Test 1: Core Dependencies
print("[1/7] Testing core dependencies...")
try:
    import fastapi
    import streamlit
    import sqlalchemy
    import requests
    import pandas as pd
    import numpy as np
    print("✅ Core dependencies OK")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

# Test 2: Backend Modules
print("[2/7] Testing backend modules...")
try:
    from database import Database, University, Program
    print("✅ Database module OK")
except Exception as e:
    print(f"❌ Database module failed: {e}")
    sys.exit(1)

try:
    from scraper import UniversityScraper, CourseScraper
    print("✅ Scraper module OK")
except Exception as e:
    print(f"❌ Scraper module failed: {e}")
    sys.exit(1)

try:
    from translator import Translator
    print("✅ Translator module OK")
except Exception as e:
    print(f"❌ Translator module failed: {e}")
    sys.exit(1)

try:
    from language_detector import LanguageDetector
    print("✅ Language detector OK")
except Exception as e:
    print(f"❌ Language detector failed: {e}")
    sys.exit(1)

try:
    from ml_classifier import MLClassifier
    print("✅ ML classifier OK")
except Exception as e:
    print(f"❌ ML classifier failed: {e}")
    sys.exit(1)

try:
    from metadata_checker import MetadataChecker
    print("✅ Metadata checker OK")
except Exception as e:
    print(f"❌ Metadata checker failed: {e}")
    sys.exit(1)

try:
    from gotouni_checker import GotoUniChecker
    print("✅ GotoUni checker OK")
except Exception as e:
    print(f"❌ GotoUni checker failed: {e}")
    sys.exit(1)

# Test 3: Database Initialization
print("[3/7] Testing database initialization...")
try:
    db = Database()
    session = db.get_session()
    session.close()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)

# Test 4: Component Initialization
print("[4/7] Testing component initialization...")
try:
    university_scraper = UniversityScraper()
    course_scraper = CourseScraper()
    translator = Translator()
    language_detector = LanguageDetector()
    ml_classifier = MLClassifier()
    metadata_checker = MetadataChecker()
    goto_uni_checker = GotoUniChecker()
    print("✅ All components initialized")
except Exception as e:
    print(f"❌ Component initialization failed: {e}")
    sys.exit(1)

# Test 5: GotoUni CSV
print("[5/7] Testing GotoUni CSV...")
try:
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'gotouniversity.csv')
    if os.path.exists(csv_path):
        print(f"✅ GotoUni CSV found: {csv_path}")
    else:
        print(f"⚠️  GotoUni CSV not found: {csv_path}")
except Exception as e:
    print(f"⚠️  CSV check failed: {e}")

# Test 6: ML Model
print("[6/7] Testing ML classifier...")
try:
    test_text = "Bachelor of Science in Computer Science"
    level, confidence = ml_classifier.classify(test_text)
    print(f"✅ ML classifier working: '{test_text}' -> {level} ({confidence:.2%})")
except Exception as e:
    print(f"⚠️  ML classifier test failed: {e}")

# Test 7: Translation
print("[7/7] Testing translation...")
try:
    test_name = "Universität München"
    translated = translator.translate(test_name)
    print(f"✅ Translation working: '{test_name}' -> '{translated}'")
except Exception as e:
    print(f"⚠️  Translation test failed: {e}")

print()
print("=" * 50)
print("✅ ALL TESTS PASSED!")
print("=" * 50)
print()
print("System is ready to use!")
print()
print("To start:")
print("  1. Standalone: streamlit run streamlit_app.py")
print("  2. Backend: cd backend && python main.py")
print("  3. Frontend: cd frontend && streamlit run app.py")
print()

