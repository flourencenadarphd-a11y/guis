"""
Professional Streamlit frontend for GUIS
Modern, clean, and production-ready interface
"""
import streamlit as st
import requests
import pandas as pd
from typing import List, Dict, Optional
import time
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config with professional theme
st.set_page_config(
    page_title="GUIS - Global University Intelligence System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Header styling */
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
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    /* Program card */
    .program-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .program-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-visited {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-not-visited {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .status-english {
        background-color: #cfe2ff;
        color: #084298;
    }
    
    .status-gotouni {
        background-color: #fff3cd;
        color: #856404;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 6px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Success/Error messages */
    .stSuccess {
        border-radius: 6px;
    }
    
    .stError {
        border-radius: 6px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
""", unsafe_allow_html=True)


def make_api_request(endpoint: str, method: str = "GET", data: Dict = None, api_url: str = None, timeout: int = 30):
    """Make API request with comprehensive error handling"""
    try:
        base_url = api_url or API_BASE_URL
        url = f"{base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=data, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.warning(f"Resource not found: {endpoint}")
            return None
        elif response.status_code == 500:
            st.error(f"Server error: {response.text}")
            return None
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 **Connection Error**: Cannot connect to backend API. Please ensure the FastAPI server is running on port 8000.")
        st.info("💡 **Tip**: Start the backend server using: `cd backend && python main.py`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ **Timeout**: The request took too long. The server might be processing a large request.")
        return None
    except Exception as e:
        st.error(f"❌ **Error**: {str(e)}")
        return None


def display_stats(api_url: str = None):
    """Display system statistics in professional cards"""
    stats = make_api_request("/api/stats", api_url=api_url)
    if stats:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        metrics = [
            ("🏫", "Universities", stats.get("total_universities", 0), "#667eea"),
            ("📚", "Programs", stats.get("total_programs", 0), "#764ba2"),
            ("🎓", "Undergraduate", stats.get("ug_count", 0), "#f093fb"),
            ("🎯", "Postgraduate", stats.get("pg_count", 0), "#4facfe"),
            ("🌐", "English", stats.get("english_count", 0), "#43e97b"),
            ("✅", "Visited", stats.get("visited_count", 0), "#fa709a")
        ]
        
        cols = [col1, col2, col3, col4, col5, col6]
        for col, (icon, label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, {color}15 0%, {color}05 100%); 
                                border-radius: 8px; border-left: 4px solid {color};">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: {color};">{value}</div>
                        <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)


def create_program_card(program: Dict, university: Dict, index: int):
    """Create a professional program card"""
    visited = program.get("visited", False)
    english = program.get("taught_in_english", False)
    gotouni = university.get("exists_in_gotouniversity", False)
    level = program.get("level", "N/A")
    
    # Status badges
    visited_badge = "🟢 Visited" if visited else "🔴 Not Visited"
    english_badge = "✅ English" if english else "❌ Non-English"
    gotouni_badge = "⭐ In GotoUni" if gotouni else "📝 Not in GotoUni"
    level_badge = f"🎓 {level}"
    
    with st.container():
        st.markdown(f"""
            <div class="program-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; color: #333; font-size: 1.3rem;">
                            {index}. {university.get('translated_name') or university.get('original_name', 'Unknown University')}
                        </h3>
                        <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem;">
                            {program.get('course_name', 'N/A')}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-badge status-visited">{visited_badge}</span>
                        <span class="status-badge status-english">{english_badge}</span>
                        <span class="status-badge status-gotouni">{gotouni_badge}</span>
                        <span class="status-badge" style="background: #e7f3ff; color: #0066cc;">{level_badge}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Details in expander
        with st.expander("📋 View Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏫 University Information")
                st.write(f"**Original Name:** {university.get('original_name', 'N/A')}")
                st.write(f"**Translated Name:** {university.get('translated_name', 'N/A')}")
                st.write(f"**Country:** {university.get('country', 'N/A')}")
                st.write(f"**GotoUniversity Status:** {'✅ Exists in database' if gotouni else '❌ Not found in database'}")
            
            with col2:
                st.markdown("### 📚 Program Information")
                st.write(f"**Course Name:** {program.get('course_name', 'N/A')}")
                st.write(f"**Level:** {level}")
                st.write(f"**Language:** {'English' if english else 'Non-English'}")
                confidence = program.get('confidence_score', 'N/A')
                if confidence != 'N/A':
                    try:
                        conf_float = float(confidence)
                        st.write(f"**ML Confidence:** {conf_float:.1%}")
                    except:
                        st.write(f"**ML Confidence:** {confidence}")
                else:
                    st.write(f"**ML Confidence:** N/A")
            
            st.markdown("### 🔗 Program URL")
            url = program.get('program_url', 'N/A')
            if url != 'N/A':
                st.markdown(f"[{url}]({url})")
            else:
                st.write("N/A")
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if not visited:
                    if st.button("✅ Mark as Visited", key=f"visit_{program.get('id')}", use_container_width=True):
                        visit_result = make_api_request(
                            "/api/programs/visit",
                            method="POST",
                            data={"program_id": program.get("id")},
                            api_url=st.session_state.get('api_base_url', API_BASE_URL)
                        )
                        if visit_result:
                            st.success("✅ Program marked as visited!")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    st.info("✅ Already visited")
            
            with col_btn2:
                if url != 'N/A':
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration: none;"><button style="width: 100%; padding: 0.5rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">🔗 Open Link</button></a>', unsafe_allow_html=True)
            
            with col_btn3:
                if st.button("🔄 Refresh Metadata", key=f"refresh_{program.get('id')}", use_container_width=True):
                    st.info("Metadata refresh feature coming soon!")


def main():
    """Main application with professional layout"""
    
    # Professional Header
    st.markdown("""
        <div class="main-header">
            <h1>🎓 Global University Intelligence System</h1>
            <p>Discover, Track, and Analyze University Programs Worldwide</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API URL Configuration
        api_url = st.text_input(
            "API Base URL",
            value=API_BASE_URL,
            key="api_url_input",
            help="Enter the backend API URL (default: http://localhost:8000)"
        )
        
        if 'api_base_url' not in st.session_state:
            st.session_state.api_base_url = API_BASE_URL
        if api_url:
            st.session_state.api_base_url = api_url
        current_api_url = st.session_state.get('api_base_url', API_BASE_URL)
        
        # Connection Status
        st.markdown("---")
        st.markdown("### 🔌 Connection Status")
        test_response = make_api_request("/api/stats", api_url=current_api_url)
        if test_response:
            st.success("✅ Connected to backend")
        else:
            st.error("❌ Not connected")
        
        # Statistics Dashboard
        st.markdown("---")
        st.markdown("### 📊 System Statistics")
        display_stats(current_api_url)
        
        # AI Query Section
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        ai_question = st.text_area(
            "Ask a question about the data",
            key="ai_question",
            height=100,
            help="Get AI-powered insights about universities and programs"
        )
        if st.button("💬 Query AI", key="query_ai_btn", use_container_width=True):
            if ai_question:
                with st.spinner("🤔 AI is thinking..."):
                    result = make_api_request("/api/ai/query", method="POST", data={
                        "question": ai_question,
                        "context": None
                    }, api_url=current_api_url)
                    if result:
                        st.success("✅ AI Response:")
                        st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; border-left: 4px solid #667eea;">
                                {result.get("response", "No response")}
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a question")
        
        # Quick Actions
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("📥 Export Data", use_container_width=True):
            st.info("Export feature coming soon!")
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & Discover", "📚 Programs Database", "🏫 Universities", "📈 Analytics"])
    
    # Tab 1: Search & Discover
    with tab1:
        st.markdown("### 🔍 Search for University Programs")
        st.markdown("Discover universities and programs by country and course name.")
        
        # Search Form
        search_col1, search_col2 = st.columns([2, 1])
        
        with search_col1:
            country = st.text_input(
                "🌍 Country",
                placeholder="e.g., Germany, France, Austria, United States",
                key="search_country",
                help="Enter the country name to search for universities"
            )
        
        with search_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_universities_btn = st.button("🔍 Fetch Universities", type="primary", use_container_width=True)
        
        if fetch_universities_btn and country:
            with st.spinner(f"🔍 Fetching universities for {country}... This may take a few moments."):
                result = make_api_request("/api/universities/fetch", method="POST", data={"country": country}, api_url=current_api_url)
                if result:
                    st.success(f"✅ {result.get('message', '')}")
                    
                    # Display universities in a nice format
                    universities = result.get("universities", [])
                    if universities:
                        st.markdown(f"### 📋 Found {len(universities)} Universities")
                        
                        # Create a DataFrame for better display
                        uni_data = []
                        for uni in universities:
                            uni_data.append({
                                "Original Name": uni.get("original_name", "N/A"),
                                "Translated Name": uni.get("translated_name", "N/A"),
                                "In GotoUni": "✅ Yes" if uni.get("exists_in_gotouniversity") else "❌ No"
                            })
                        
                        df_unis = pd.DataFrame(uni_data)
                        st.dataframe(df_unis, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🎓 Search for Programs")
        
        program_col1, program_col2 = st.columns(2)
        
        with program_col1:
            program_country = st.text_input(
                "🌍 Country",
                value=country if country else "",
                placeholder="e.g., Germany",
                key="program_country"
            )
        
        with program_col2:
            course = st.text_input(
                "📚 Course Name",
                placeholder="e.g., BSc IT, MSc Data Science, Computer Science",
                key="program_course",
                help="Enter the course or program name to search for"
            )
        
        search_programs_btn = st.button("🔍 Search Programs", type="primary", use_container_width=True)
        
        if search_programs_btn and program_country and course:
            with st.spinner(f"🔍 Searching for {course} programs in {program_country}... This may take several minutes."):
                result = make_api_request("/api/programs/search", method="POST", data={
                    "country": program_country,
                    "course": course
                }, api_url=current_api_url, timeout=300)
                
                if result:
                    st.success(f"✅ {result.get('message', '')}")
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📚 Total Programs", result.get("total", 0))
                    with col2:
                        st.metric("🎓 Undergraduate", result.get("ug_count", 0))
                    with col3:
                        st.metric("🎯 Postgraduate", result.get("pg_count", 0))
                    
                    # Display programs
                    programs = result.get("programs", [])
                    if programs:
                        st.markdown(f"### 📋 Found {len(programs)} Programs")
                        for i, program in enumerate(programs, 1):
                            # Create a simplified card for search results
                            uni_name = program.get('university', 'Unknown')
                            with st.expander(f"{i}. {uni_name} - {program.get('level', 'N/A')} - {program.get('course_name', 'N/A')}", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**URL:** {program.get('url', 'N/A')}")
                                    st.write(f"**Level:** {program.get('level', 'N/A')}")
                                with col2:
                                    st.write(f"**English:** {'✅ Yes' if program.get('taught_in_english') else '❌ No'}")
                                    st.write(f"**Confidence:** {program.get('confidence', 0):.2%}")
    
    # Tab 2: Programs Database
    with tab2:
        st.markdown("### 📚 Programs Database")
        st.markdown("Browse and filter all programs in the database.")
        
        # Advanced Filters
        with st.expander("🔧 Advanced Filters", expanded=True):
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                # Get available countries from API
                filter_country = st.selectbox(
                    "🌍 Country",
                    ["All", "Germany", "France", "Austria", "UK", "USA", "Canada", "Australia"],
                    key="filter_country"
                )
            
            with filter_col2:
                filter_course = st.text_input(
                    "📚 Course Filter",
                    placeholder="Filter by course name",
                    key="filter_course"
                )
            
            with filter_col3:
                filter_level = st.selectbox(
                    "🎓 Level",
                    ["All", "UG", "PG"],
                    key="filter_level"
                )
            
            with filter_col4:
                filter_english = st.checkbox(
                    "🌐 English Only",
                    key="filter_english"
                )
                filter_visited = st.checkbox(
                    "✅ Visited Only",
                    key="filter_visited"
                )
        
        # Apply filters button
        apply_filters = st.button("🔍 Apply Filters", type="primary", use_container_width=True)
        
        if apply_filters or 'programs_loaded' not in st.session_state:
            # Build filters
            filters = {}
            if filter_country != "All":
                filters["country"] = filter_country
            if filter_course:
                filters["course"] = filter_course
            if filter_level != "All":
                filters["level"] = filter_level
            if filter_english:
                filters["english_only"] = True
            
            with st.spinner("📊 Loading programs..."):
                result = make_api_request("/api/programs", data=filters, api_url=current_api_url)
                
                if result:
                    st.session_state.programs_data = result
                    st.session_state.programs_loaded = True
                    
                    # Display summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📚 Total Programs", result.get("total", 0))
                    with col2:
                        st.metric("🎓 Undergraduate", result.get("ug_count", 0))
                    with col3:
                        st.metric("🎯 Postgraduate", result.get("pg_count", 0))
                    
                    # Display programs
                    programs = result.get("programs", [])
                    if programs:
                        # Filter by visited if needed
                        if filter_visited:
                            programs = [p for p in programs if p.get("visited", False)]
                        
                        st.markdown(f"### 📋 Programs ({len(programs)})")
                        
                        # Create DataFrame for table view
                        display_data = []
                        for program in programs:
                            uni = program.get("university", {})
                            display_data.append({
                                "ID": program.get("id"),
                                "University": uni.get("translated_name") or uni.get("original_name", "N/A"),
                                "Course": program.get("course_name", "N/A"),
                                "Level": program.get("level", "N/A"),
                                "English": "✅" if program.get("taught_in_english") else "❌",
                                "Visited": "🟢" if program.get("visited") else "🔴",
                                "GotoUni": "⭐" if uni.get("exists_in_gotouniversity") else "📝",
                                "URL": program.get("program_url", "N/A")[:50] + "..." if len(program.get("program_url", "")) > 50 else program.get("program_url", "N/A")
                            })
                        
                        df = pd.DataFrame(display_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Detailed program cards
                        st.markdown("### 📋 Program Details")
                        for i, program in enumerate(programs, 1):
                            create_program_card(program, program.get("university", {}), i)
                    else:
                        st.info("No programs found matching the filters.")
                else:
                    st.warning("Could not load programs. Please check your connection.")
    
    # Tab 3: Universities
    with tab3:
        st.markdown("### 🏫 Universities Database")
        st.markdown("View all universities in the system.")
        
        # Filter options
        uni_filter_col1, uni_filter_col2 = st.columns(2)
        with uni_filter_col1:
            uni_filter_country = st.selectbox(
                "🌍 Filter by Country",
                ["All"] + ["Germany", "France", "Austria", "UK", "USA", "Canada", "Australia"],
                key="uni_filter_country"
            )
        with uni_filter_col2:
            uni_filter_gotouni = st.selectbox(
                "⭐ GotoUniversity Status",
                ["All", "In Database", "Not in Database"],
                key="uni_filter_gotouni"
            )
        
        if st.button("🔄 Load Universities", use_container_width=True, type="primary"):
            with st.spinner("Loading universities..."):
                filters = {}
                if uni_filter_country != "All":
                    filters["country"] = uni_filter_country
                
                result = make_api_request("/api/universities", data=filters, api_url=current_api_url)
                
                if result:
                    universities = result.get("universities", [])
                    
                    # Filter by GotoUni status if needed
                    if uni_filter_gotouni == "In Database":
                        universities = [u for u in universities if u.get("exists_in_gotouniversity", False)]
                    elif uni_filter_gotouni == "Not in Database":
                        universities = [u for u in universities if not u.get("exists_in_gotouniversity", False)]
                    
                    if universities:
                        st.success(f"✅ Found {len(universities)} universities")
                        
                        # Create DataFrame
                        uni_data = []
                        for uni in universities:
                            uni_data.append({
                                "ID": uni.get("id"),
                                "Original Name": uni.get("original_name", "N/A"),
                                "Translated Name": uni.get("translated_name", "N/A"),
                                "Country": uni.get("country", "N/A"),
                                "GotoUni": "⭐ Yes" if uni.get("exists_in_gotouniversity") else "📝 No"
                            })
                        
                        df_unis = pd.DataFrame(uni_data)
                        st.dataframe(df_unis, use_container_width=True, hide_index=True)
                        
                        # Statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Universities", len(universities))
                        with col2:
                            gotouni_count = sum(1 for u in universities if u.get("exists_in_gotouniversity", False))
                            st.metric("In GotoUni", gotouni_count)
                        with col3:
                            st.metric("Not in GotoUni", len(universities) - gotouni_count)
                    else:
                        st.info("No universities found. Use the Search tab to fetch universities for a country.")
                else:
                    st.warning("Could not load universities. Please check your connection.")
        else:
            st.info("💡 Click 'Load Universities' to view all universities in the database. Use the Search tab to fetch new universities.")
    
    # Tab 4: Analytics
    with tab4:
        st.markdown("### 📈 Analytics & Insights")
        st.markdown("View analytics and insights about the data.")
        
        # Get stats
        stats = make_api_request("/api/stats", api_url=current_api_url)
        if stats:
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Program Distribution")
                chart_data = pd.DataFrame({
                    'Level': ['Undergraduate', 'Postgraduate'],
                    'Count': [stats.get('ug_count', 0), stats.get('pg_count', 0)]
                })
                st.bar_chart(chart_data.set_index('Level'))
            
            with col2:
                st.markdown("#### 🌐 Language Distribution")
                lang_data = pd.DataFrame({
                    'Language': ['English', 'Non-English'],
                    'Count': [
                        stats.get('english_count', 0),
                        stats.get('total_programs', 0) - stats.get('english_count', 0)
                    ]
                })
                st.bar_chart(lang_data.set_index('Language'))
            
            # Summary statistics
            st.markdown("### 📋 Summary Statistics")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Total Universities", stats.get("total_universities", 0))
                st.metric("Total Programs", stats.get("total_programs", 0))
            
            with summary_col2:
                st.metric("Undergraduate Programs", stats.get("ug_count", 0))
                st.metric("Postgraduate Programs", stats.get("pg_count", 0))
            
            with summary_col3:
                st.metric("English Programs", stats.get("english_count", 0))
                visited_pct = (stats.get("visited_count", 0) / stats.get("total_programs", 1)) * 100 if stats.get("total_programs", 0) > 0 else 0
                st.metric("Visited Programs", f"{stats.get('visited_count', 0)} ({visited_pct:.1f}%)")


if __name__ == "__main__":
    main()
