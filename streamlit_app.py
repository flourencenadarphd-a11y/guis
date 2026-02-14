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
    """Fetch universities for a country - REAL-TIME UPDATES"""
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
        
        # Create real-time display container
        status_container = st.empty()
        results_container = st.empty()
        universities = []
        
        status_container.info("🔍 Searching Wikipedia and education portals...")
        
        university_names = university_scraper.fetch_universities(country)
        
        if not university_names:
            if session:
                session.close()
            status_container.empty()
            return None, f"No universities found for {country}. Try a different country name or check spelling."
        
        total = len(university_names)
        status_container.info(f"📝 Found {total} universities. Processing in real-time...")
        
        # Process and display in real-time
        for idx, name in enumerate(university_names):
            try:
                # Update status
                status_container.info(f"🔄 Processing: {name[:60]}... ({idx+1}/{total})")
                
                # Translate (ALWAYS translate, even if seems English)
                translated = translator.translate(name)
                
                # Log translation for debugging
                if translated == name:
                    logger.info(f"Translation kept same: '{name}' (may be English or translation failed)")
                else:
                    logger.info(f"Translation: '{name}' -> '{translated}'")
                
                # Check gotouniversity (IMPROVED ACCURACY)
                exists, matched_name, similarity = goto_uni_checker.check_exists(translated)
                logger.info(f"GotoUni check: {translated} -> exists={exists}, similarity={similarity:.2f}")
                
                # Store in database
                if session:
                    university = University(
                        original_name=name,  # ORIGINAL NAME
                        translated_name=translated,  # TRANSLATED NAME
                        country=country,
                        exists_in_gotouniversity=exists
                    )
                    session.add(university)
                    session.commit()  # Commit immediately for real-time
                
                # Add to results
                uni_data = {
                    "original_name": name,  # ORIGINAL
                    "translated_name": translated,  # TRANSLATED
                    "exists_in_gotouniversity": exists
                }
                universities.append(uni_data)
                
                # Display in real-time
                df = pd.DataFrame(universities)
                results_container.dataframe(df, width='stretch', hide_index=True)
                
            except Exception as e:
                logger.warning(f"Error processing {name}: {e}")
                continue
        
        if session:
            session.close()
        
        status_container.success(f"✅ Complete! Processed {len(universities)} universities")
        time.sleep(1)
        status_container.empty()
        
        return universities, f"✅ Successfully fetched and processed {len(universities)} universities"
    except Exception as e:
        if session:
            session.close()
        return None, f"Error: {str(e)}"

def search_programs(country: str, course: str):
    """Search for programs - REAL-TIME, ONE UNIVERSITY AT A TIME"""
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
        status_container = st.empty()
        results_container = st.empty()
        
        total_unis = len(universities)
        status_container.info(f"🔍 Searching {total_unis} universities. Processing one at a time...")
        
        # Process ONE university at a time, complete ALL links before moving to next
        for idx, university in enumerate(universities):
            try:
                uni_original = university.original_name  # ORIGINAL NAME
                uni_translated = university.translated_name or university.original_name
                in_gotouni = university.exists_in_gotouniversity
                
                # Update status
                status_container.info(f"🔍 [{idx+1}/{total_unis}] Searching: {uni_original[:60]}...")
                
                # Search for courses
                course_links = course_scraper.search_courses(uni_translated, course)
                
                if not course_links:
                    status_container.warning(f"⚠️ [{idx+1}/{total_unis}] No links found for {uni_original[:50]}")
                    continue
                
                status_container.info(f"✅ [{idx+1}/{total_unis}] Found {len(course_links)} links for {uni_original[:50]}. Processing all links...")
                
                # Process ALL links for this university before moving to next
                uni_programs = []
                for link_idx, link_info in enumerate(course_links):
                    url = link_info['url']
                    
                    # Check if exists
                    existing = session.query(Program).filter(Program.program_url == url).first()
                    if existing:
                        continue
                    
                    # Update link status
                    status_container.info(f"🔗 [{idx+1}/{total_unis}] Processing link {link_idx+1}/{len(course_links)}: {url[:60]}...")
                    
                    # Detect language
                    try:
                        is_english, lang_confidence = language_detector.detect_english(url)
                    except:
                        is_english, lang_confidence = False, 0.0
                    
                    # Detect delivery mode
                    try:
                        delivery_mode, mode_confidence = language_detector.detect_delivery_mode(url)
                    except:
                        delivery_mode, mode_confidence = "offline", 0.0
                    
                    # Classify (ML + Rule-based)
                    try:
                        # Get page content snippet for better ML classification
                        page_snippet = None
                        try:
                            from backend.scraper import CourseScraper
                            temp_scraper = CourseScraper()
                            response = temp_scraper._make_request(url)
                            if response and response.status_code == 200:
                                from bs4 import BeautifulSoup
                                soup = BeautifulSoup(response.content, 'html.parser')
                                page_snippet = soup.get_text()[:500]  # First 500 chars
                        except:
                            pass
                        
                        # Use ML classifier with page content
                        level, ml_confidence = ml_classifier.classify(
                            link_info.get('title', course),
                            page_content_snippet=page_snippet
                        )
                        logger.info(f"ML Classification: '{link_info.get('title', course)}' -> {level} (confidence: {ml_confidence:.2f})")
                    except Exception as e:
                        logger.warning(f"Classification error: {e}")
                        level, ml_confidence = 'UG', 0.5
                    
                    # Get metadata
                    try:
                        metadata = metadata_checker.check_metadata(url)
                    except:
                        metadata = {'content_hash': None, 'last_checked': datetime.utcnow()}
                    
                    # Create program
                    try:
                        from sqlalchemy import text
                        try:
                            session.execute(text("SELECT delivery_mode FROM programs LIMIT 1"))
                        except:
                            try:
                                session.execute(text("ALTER TABLE programs ADD COLUMN delivery_mode VARCHAR"))
                                session.execute(text("UPDATE programs SET delivery_mode = 'offline' WHERE delivery_mode IS NULL"))
                                session.commit()
                            except:
                                pass
                        
                        program = Program(
                            university_id=university.id,
                            course_name=course,
                            program_url=url,
                            level=level,
                            taught_in_english=is_english,
                            delivery_mode=delivery_mode,
                            visited=False,
                            content_hash=metadata.get('content_hash'),
                            last_checked=metadata.get('last_checked'),
                            confidence_score=str(ml_confidence)
                        )
                    except Exception as e:
                        logger.warning(f"Could not add delivery_mode: {e}")
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
                    session.commit()  # Commit immediately for real-time
                    
                    # Add to results
                    prog_data = {
                        "university_original": uni_original,  # ORIGINAL NAME
                        "university_translated": uni_translated,  # TRANSLATED NAME
                        "in_gotouniversity": in_gotouni,
                        "url": url,
                        "level": level,
                        "taught_in_english": is_english,
                        "delivery_mode": delivery_mode,
                        "confidence": ml_confidence,
                        "course_name": course
                    }
                    uni_programs.append(prog_data)
                    programs_found.append(prog_data)
                    
                    # Display in real-time
                    if programs_found:
                        df = pd.DataFrame(programs_found)
                        results_container.dataframe(df, width='stretch', hide_index=True)
                
                # University complete
                status_container.success(f"✅ [{idx+1}/{total_unis}] Completed {uni_original[:50]}: {len(uni_programs)} programs found")
                
            except Exception as e:
                logger.warning(f"Error processing {university.original_name}: {e}")
                status_container.error(f"❌ Error processing {university.original_name}: {str(e)}")
                continue
        
        session.close()
        
        status_container.success(f"✅ Complete! Found {len(programs_found)} programs total")
        time.sleep(1)
        
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
                            uni_original = prog.get('university_original', 'Unknown')  # ORIGINAL
                            uni_translated = prog.get('university_translated', uni_original)  # TRANSLATED
                            in_gotouni = prog.get('in_gotouniversity', False)
                            delivery = prog.get('delivery_mode', 'offline').title()
                            
                            with st.expander(f"{i}. {uni_original} - {prog.get('level')} - {course}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("### 🏫 University Information")
                                    st.write(f"**Original Name:** {uni_original}")
                                    st.write(f"**Translated Name:** {uni_translated}")
                                    st.write(f"**In GotoUniversity:** {'✅ Yes' if in_gotouni else '❌ No'}")
                                    st.write(f"**Country:** {country}")
                                with col2:
                                    st.markdown("### 📚 Program Information")
                                    st.write(f"**Course:** {course}")
                                    st.write(f"**Level:** {prog.get('level')}")
                                    st.write(f"**Language:** {'✅ English' if prog.get('taught_in_english') else '❌ Non-English'}")
                                    st.write(f"**Delivery Mode:** {delivery}")
                                    st.write(f"**ML Confidence:** {prog.get('confidence', 0):.1%}")
                                
                                st.markdown("### 🔗 Program URL")
                                if prog.get('url'):
                                    st.markdown(f"[{prog.get('url')}]({prog.get('url')})")
                                else:
                                    st.write("N/A")
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
            try:
                # Query programs
                programs = session.query(Program).join(University).all()
            except Exception as e:
                error_msg = str(e).lower()
                if 'delivery_mode' in error_msg or 'no such column' in error_msg:
                    st.warning("⚠️ **Database Schema Update Needed**")
                    st.info("""
                    **The database needs to be updated with the new schema.**
                    
                    **Quick Fix:**
                    1. Go to the **Search** tab
                    2. Fetch universities for any country (e.g., "Germany")
                    3. This will recreate the database with the correct schema
                    4. Then come back here - it will work!
                    
                    The database will be automatically recreated with all new features.
                    """)
                    session.close()
                    programs = []
                else:
                    st.error(f"Database error: {str(e)}")
                    st.info("💡 Try fetching universities first to initialize the database.")
                    session.close()
                    programs = []
            
            if programs:
                display_data = []
                for program in programs:
                    uni = program.university
                    display_data.append({
                        "ID": program.id,
                        "University (Original)": uni.original_name,
                        "University (Translated)": uni.translated_name or uni.original_name,
                        "In GotoUni": "✅" if uni.exists_in_gotouniversity else "❌",
                        "Course": program.course_name,
                        "Level": program.level,
                        "Language": "✅ English" if program.taught_in_english else "❌ Non-English",
                        "Delivery": (getattr(program, 'delivery_mode', 'offline') or 'offline').title(),
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

