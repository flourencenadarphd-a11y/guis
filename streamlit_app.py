"""
Standalone Streamlit App for GUIS
Combines backend and frontend in one file for easy deployment
"""
import streamlit as st
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend modules
try:
    from database import Database, University, Program
    from scraper import UniversityScraper, CourseScraper
    from translator import Translator
    from language_detector import LanguageDetector
    from ml_classifier import MLClassifier
    from metadata_checker import MetadataChecker
    from gotouni_checker import GotoUniChecker
    from ai_query import AIQuery
    from sqlalchemy.orm import Session
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    st.error(f"Backend modules not available: {e}")

import pandas as pd
from typing import Dict, Optional
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="GUIS - Global University Intelligence System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .status-visited { background-color: #d4edda; color: #155724; }
    .status-not-visited { background-color: #f8d7da; color: #721c24; }
    .status-english { background-color: #cfe2ff; color: #084298; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize backend components"""
    if not BACKEND_AVAILABLE:
        return None, None, None, None, None, None, None, None, None
    
    try:
        db = Database()
        university_scraper = UniversityScraper()
        course_scraper = CourseScraper()
        translator = Translator()
        language_detector = LanguageDetector()
        ml_classifier = MLClassifier()
        metadata_checker = MetadataChecker()
        goto_uni_checker = GotoUniChecker()
        ai_query = AIQuery()
        return db, university_scraper, course_scraper, translator, language_detector, ml_classifier, metadata_checker, goto_uni_checker, ai_query
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None, None, None, None, None, None, None

# Initialize
db, university_scraper, course_scraper, translator, language_detector, ml_classifier, metadata_checker, goto_uni_checker, ai_query = init_components()

def get_db_session():
    """Get database session"""
    if db:
        return db.get_session()
    return None

def fetch_universities(country: str):
    """Fetch universities for a country"""
    if not university_scraper or not translator or not goto_uni_checker:
        return None, "Backend not initialized"
    
    try:
        # Check if already in database
        session = get_db_session()
        if session:
            existing = session.query(University).filter(University.country == country).all()
            if existing:
                session.close()
                return [{
                    "original_name": u.original_name,
                    "translated_name": u.translated_name,
                    "exists_in_gotouniversity": u.exists_in_gotouniversity
                } for u in existing], f"Found {len(existing)} universities in database"
        
        # Fetch new universities
        university_names = university_scraper.fetch_universities(country)
        
        universities = []
        for name in university_names[:20]:  # Limit to 20 for demo
            translated = translator.translate(name)
            exists, matched_name, similarity = goto_uni_checker.check_exists(translated)
            
            if session:
                university = University(
                    original_name=name,
                    translated_name=translated,
                    country=country,
                    exists_in_gotouniversity=exists
                )
                session.add(university)
                universities.append({
                    "original_name": name,
                    "translated_name": translated,
                    "exists_in_gotouniversity": exists
                })
        
        if session:
            session.commit()
            session.close()
        
        return universities, f"Fetched {len(universities)} universities"
    except Exception as e:
        if session:
            session.close()
        return None, f"Error: {str(e)}"

def search_programs(country: str, course: str):
    """Search for programs"""
    if not course_scraper or not language_detector or not ml_classifier:
        return None, "Backend not initialized"
    
    try:
        session = get_db_session()
        if not session:
            return None, "Database not available"
        
        universities = session.query(University).filter(University.country == country).all()
        if not universities:
            session.close()
            return None, f"No universities found for {country}. Please fetch universities first."
        
        programs_found = []
        
        for university in universities[:5]:  # Limit to 5 for demo
            try:
                course_links = course_scraper.search_courses(
                    university.translated_name or university.original_name,
                    course
                )
                
                for link_info in course_links[:3]:  # Limit to 3 per university
                    url = link_info['url']
                    
                    # Check if exists
                    existing = session.query(Program).filter(Program.program_url == url).first()
                    if existing:
                        continue
                    
                    # Detect language
                    is_english, confidence = language_detector.detect_english(url)
                    
                    # Classify
                    level, ml_confidence = ml_classifier.classify(
                        link_info.get('title', course)
                    )
                    
                    # Get metadata
                    metadata = metadata_checker.check_metadata(url)
                    
                    # Create program
                    program = Program(
                        university_id=university.id,
                        course_name=course,
                        program_url=url,
                        level=level,
                        taught_in_english=is_english,
                        visited=False,
                        content_hash=metadata.get('content_hash'),
                        last_checked=metadata.get('last_checked'),
                        confidence_score=str(ml_confidence)
                    )
                    session.add(program)
                    
                    programs_found.append({
                        "university": university.translated_name or university.original_name,
                        "url": url,
                        "level": level,
                        "taught_in_english": is_english,
                        "confidence": ml_confidence
                    })
            except Exception as e:
                continue
        
        session.commit()
        
        ug_count = sum(1 for p in programs_found if p['level'] == 'UG')
        pg_count = sum(1 for p in programs_found if p['level'] == 'PG')
        
        session.close()
        return {
            "total": len(programs_found),
            "ug_count": ug_count,
            "pg_count": pg_count,
            "programs": programs_found
        }, f"Found {len(programs_found)} programs"
    except Exception as e:
        if session:
            session.close()
        return None, f"Error: {str(e)}"

def get_stats():
    """Get system statistics"""
    session = get_db_session()
    if not session:
        return None
    
    try:
        total_universities = session.query(University).count()
        total_programs = session.query(Program).count()
        ug_count = session.query(Program).filter(Program.level == 'UG').count()
        pg_count = session.query(Program).filter(Program.level == 'PG').count()
        visited_count = session.query(Program).filter(Program.visited == True).count()
        english_count = session.query(Program).filter(Program.taught_in_english == True).count()
        
        session.close()
        return {
            "total_universities": total_universities,
            "total_programs": total_programs,
            "ug_count": ug_count,
            "pg_count": pg_count,
            "visited_count": visited_count,
            "english_count": english_count
        }
    except:
        if session:
            session.close()
        return None

def main():
    """Main application"""
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🎓 Global University Intelligence System</h1>
            <p>Discover, Track, and Analyze University Programs Worldwide</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 System Statistics")
        stats = get_stats()
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🏫 Universities", stats.get("total_universities", 0))
                st.metric("📚 Programs", stats.get("total_programs", 0))
            with col2:
                st.metric("🎓 UG", stats.get("ug_count", 0))
                st.metric("🎯 PG", stats.get("pg_count", 0))
        else:
            st.info("No data yet. Start by fetching universities!")
        
        st.markdown("---")
        st.markdown("### ⚙️ System Status")
        if BACKEND_AVAILABLE and db:
            st.success("✅ Backend Ready")
        else:
            st.error("❌ Backend Not Available")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📚 Programs", "📈 Analytics"])
    
    # Tab 1: Search
    with tab1:
        st.markdown("### 🔍 Search for University Programs")
        
        col1, col2 = st.columns(2)
        with col1:
            country = st.text_input("🌍 Country", placeholder="e.g., Germany, France")
        with col2:
            course = st.text_input("📚 Course", placeholder="e.g., BSc IT, Computer Science")
        
        col1, col2 = st.columns(2)
        with col1:
            fetch_btn = st.button("🔍 Fetch Universities", type="primary", use_container_width=True)
        with col2:
            search_btn = st.button("🔍 Search Programs", type="primary", use_container_width=True)
        
        if fetch_btn and country:
            with st.spinner(f"Fetching universities for {country}..."):
                universities, message = fetch_universities(country)
                if universities:
                    st.success(f"✅ {message}")
                    df = pd.DataFrame(universities)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error(message)
        
        if search_btn and country and course:
            with st.spinner(f"Searching for {course} in {country}..."):
                result, message = search_programs(country, course)
                if result:
                    st.success(f"✅ {message}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total", result.get("total", 0))
                    with col2:
                        st.metric("UG", result.get("ug_count", 0))
                    with col3:
                        st.metric("PG", result.get("pg_count", 0))
                    
                    programs = result.get("programs", [])
                    if programs:
                        for i, prog in enumerate(programs, 1):
                            with st.expander(f"{i}. {prog.get('university')} - {prog.get('level')}"):
                                st.write(f"**URL:** {prog.get('url')}")
                                st.write(f"**Level:** {prog.get('level')}")
                                st.write(f"**English:** {'✅ Yes' if prog.get('taught_in_english') else '❌ No'}")
                                st.write(f"**Confidence:** {prog.get('confidence', 0):.2%}")
                else:
                    st.error(message)
    
    # Tab 2: Programs
    with tab2:
        st.markdown("### 📚 Programs Database")
        
        session = get_db_session()
        if session:
            programs = session.query(Program).join(University).all()
            if programs:
                display_data = []
                for program in programs:
                    uni = program.university
                    display_data.append({
                        "University": uni.translated_name or uni.original_name,
                        "Course": program.course_name,
                        "Level": program.level,
                        "English": "✅" if program.taught_in_english else "❌",
                        "Visited": "🟢" if program.visited else "🔴",
                        "URL": program.program_url[:50] + "..." if len(program.program_url) > 50 else program.program_url
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No programs found. Use the Search tab to find programs.")
            session.close()
        else:
            st.error("Database not available")
    
    # Tab 3: Analytics
    with tab3:
        st.markdown("### 📈 Analytics")
        stats = get_stats()
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Program Distribution")
                chart_data = pd.DataFrame({
                    'Level': ['UG', 'PG'],
                    'Count': [stats.get('ug_count', 0), stats.get('pg_count', 0)]
                })
                st.bar_chart(chart_data.set_index('Level'))
            with col2:
                st.markdown("#### Language Distribution")
                lang_data = pd.DataFrame({
                    'Language': ['English', 'Non-English'],
                    'Count': [
                        stats.get('english_count', 0),
                        stats.get('total_programs', 0) - stats.get('english_count', 0)
                    ]
                })
                st.bar_chart(lang_data.set_index('Language'))
        else:
            st.info("No data available yet.")

if __name__ == "__main__":
    main()

