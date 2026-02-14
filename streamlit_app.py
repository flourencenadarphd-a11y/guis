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
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Searching Wikipedia and education portals...")
        progress_bar.progress(10)
        
        university_names = university_scraper.fetch_universities(country)
        
        if not university_names:
            if session:
                session.close()
            return None, f"No universities found for {country}. Try a different country name or check spelling."
        
        status_text.text(f"📝 Found {len(university_names)} universities. Processing...")
        progress_bar.progress(30)
        
        universities = []
        total = min(len(university_names), 50)  # Increased limit
        
        for idx, name in enumerate(university_names[:total]):
            try:
                status_text.text(f"🔄 Processing: {name[:50]}... ({idx+1}/{total})")
                progress_bar.progress(30 + int((idx / total) * 50))
                
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
            except Exception as e:
                logger.warning(f"Error processing {name}: {e}")
                continue
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
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return universities, f"✅ Successfully fetched and processed {len(universities)} universities"
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
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_unis = min(len(universities), 10)  # Increased limit
        
        for idx, university in enumerate(universities[:total_unis]):
            try:
                uni_name = university.translated_name or university.original_name
                status_text.text(f"🔍 Searching {uni_name[:50]}... ({idx+1}/{total_unis})")
                progress_bar.progress(int((idx / total_unis) * 50))
                
                course_links = course_scraper.search_courses(
                    uni_name,
                    course
                )
                
                if not course_links:
                    continue
                
                status_text.text(f"✅ Found {len(course_links)} links. Processing...")
                
                for link_info in course_links[:5]:  # Increased limit
                    url = link_info['url']
                    
                    # Check if exists
                    existing = session.query(Program).filter(Program.program_url == url).first()
                    if existing:
                        continue
                    
                    # Detect language
                    try:
                        is_english, lang_confidence = language_detector.detect_english(url)
                    except:
                        is_english, lang_confidence = False, 0.0
                    
                    # Classify
                    try:
                        level, ml_confidence = ml_classifier.classify(
                            link_info.get('title', course)
                        )
                    except:
                        level, ml_confidence = 'UG', 0.5  # Default fallback
                    
                    # Get metadata
                    try:
                        metadata = metadata_checker.check_metadata(url)
                    except:
                        metadata = {'content_hash': None, 'last_checked': datetime.utcnow()}
                    
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
                logger.warning(f"Error processing {university.original_name}: {e}")
                continue
        
        session.commit()
        session.close()
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        ug_count = sum(1 for p in programs_found if p['level'] == 'UG')
        pg_count = sum(1 for p in programs_found if p['level'] == 'PG')
        
        return {
            "total": len(programs_found),
            "ug_count": ug_count,
            "pg_count": pg_count,
            "programs": programs_found
        }, f"✅ Found {len(programs_found)} programs ({ug_count} UG, {pg_count} PG)"
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
            fetch_btn = st.button("🔍 Fetch Universities", type="primary", width='stretch')
        with col2:
            search_btn = st.button("🔍 Search Programs", type="primary", width='stretch')
        
        if fetch_btn and country:
            st.info(f"🔍 Starting search for universities in {country}. This may take 1-2 minutes...")
            universities, message = fetch_universities(country)
            if universities and len(universities) > 0:
                st.success(f"✅ {message}")
                st.markdown(f"### 📋 Found {len(universities)} Universities")
                df = pd.DataFrame(universities)
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Show summary
                gotouni_count = sum(1 for u in universities if u.get('exists_in_gotouniversity', False))
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Universities", len(universities))
                with col2:
                    st.metric("In GotoUni Database", gotouni_count)
            else:
                st.error(f"❌ {message}")
                st.info("💡 Tips:\n- Try different country name (e.g., 'United States' instead of 'USA')\n- Check spelling\n- Some countries may have limited data")
        
        if search_btn and country and course:
            if not country or not course:
                st.warning("⚠️ Please enter both country and course name")
            else:
                st.info(f"🔍 Searching for '{course}' programs in {country}. This may take 3-5 minutes...")
                result, message = search_programs(country, course)
                if result and result.get("total", 0) > 0:
                    st.success(f"✅ {message}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📚 Total Programs", result.get("total", 0))
                    with col2:
                        st.metric("🎓 Undergraduate", result.get("ug_count", 0))
                    with col3:
                        st.metric("🎯 Postgraduate", result.get("pg_count", 0))
                    
                    programs = result.get("programs", [])
                    if programs:
                        st.markdown(f"### 📋 Program Details ({len(programs)} programs)")
                        for i, prog in enumerate(programs, 1):
                            with st.expander(f"{i}. {prog.get('university')} - {prog.get('level')} - {course}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**University:** {prog.get('university')}")
                                    st.write(f"**Course:** {course}")
                                    st.write(f"**Level:** {prog.get('level')}")
                                with col2:
                                    st.write(f"**Language:** {'✅ English' if prog.get('taught_in_english') else '❌ Non-English'}")
                                    st.write(f"**ML Confidence:** {prog.get('confidence', 0):.1%}")
                                    if prog.get('url'):
                                        st.markdown(f"[🔗 Open Program Page]({prog.get('url')})")
                                st.write(f"**URL:** {prog.get('url')}")
                else:
                    st.error(f"❌ {message}")
                    if "No universities found" in message:
                        st.info("💡 **Tip**: First fetch universities for this country using the 'Fetch Universities' button above.")
                    else:
                        st.info("💡 **Tips**:\n- Make sure universities are fetched first\n- Try different course keywords\n- Some universities may not have public course pages")
    
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
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Add visit tracking
                st.markdown("### 📋 Program Actions")
                for program in programs:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{program.university.translated_name or program.university.original_name}** - {program.course_name}")
                    with col2:
                        if not program.visited:
                            if st.button("✅ Mark Visited", key=f"visit_{program.id}"):
                                program.visited = True
                                session.commit()
                                st.success("✅ Marked as visited!")
                                st.rerun()
                        else:
                            st.success("✅ Visited")
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

