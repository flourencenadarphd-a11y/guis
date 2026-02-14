"""
FastAPI backend main application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import Database, University, Program
from scraper import UniversityScraper, CourseScraper
from translator import Translator
from language_detector import LanguageDetector
from ml_classifier import MLClassifier
from metadata_checker import MetadataChecker
from gotouni_checker import GotoUniChecker
from ai_query import AIQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title="GUIS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
university_scraper = UniversityScraper()
course_scraper = CourseScraper()
translator = Translator()
language_detector = LanguageDetector()
ml_classifier = MLClassifier()
metadata_checker = MetadataChecker()
goto_uni_checker = GotoUniChecker()
ai_query = AIQuery()


# Dependency
def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


# Pydantic models
class CountryRequest(BaseModel):
    country: str


class CourseRequest(BaseModel):
    country: str
    course: str


class ProgramVisitRequest(BaseModel):
    program_id: int


class AIQueryRequest(BaseModel):
    question: str
    context: Optional[Dict] = None


# API Endpoints
@app.get("/")
def root():
    return {"message": "GUIS API", "version": "1.0.0"}


@app.get("/api/universities")
def get_universities(
    country: Optional[str] = None,
    db_session: Session = Depends(get_db)
):
    """Get all universities with optional country filter"""
    try:
        query = db_session.query(University)
        if country:
            query = query.filter(University.country == country)
        
        universities = query.all()
        
        result = []
        for uni in universities:
            result.append({
                "id": uni.id,
                "original_name": uni.original_name,
                "translated_name": uni.translated_name,
                "country": uni.country,
                "exists_in_gotouniversity": uni.exists_in_gotouniversity,
                "created_at": uni.created_at.isoformat() if uni.created_at else None
            })
        
        return {
            "total": len(result),
            "universities": result
        }
    except Exception as e:
        logger.error(f"Error getting universities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/universities/fetch")
def fetch_universities(request: CountryRequest, db_session: Session = Depends(get_db)):
    """Fetch universities for a country"""
    try:
        # Check if already in database
        existing = db_session.query(University).filter(
            University.country == request.country
        ).all()
        
        if existing:
            return {
                "message": "Universities already in database",
                "count": len(existing),
                "universities": [
                    {
                        "id": u.id,
                        "original_name": u.original_name,
                        "translated_name": u.translated_name,
                        "exists_in_gotouniversity": u.exists_in_gotouniversity
                    }
                    for u in existing
                ]
            }
        
        # Fetch new universities
        university_names = university_scraper.fetch_universities(request.country)
        
        universities = []
        for name in university_names:
            # Translate if needed
            translated = translator.translate(name)
            
            # Check gotouniversity
            exists, matched_name, similarity = goto_uni_checker.check_exists(translated)
            
            # Create university record
            university = University(
                original_name=name,
                translated_name=translated,
                country=request.country,
                exists_in_gotouniversity=exists
            )
            db_session.add(university)
            universities.append({
                "original_name": name,
                "translated_name": translated,
                "exists_in_gotouniversity": exists
            })
        
        db_session.commit()
        
        return {
            "message": f"Fetched {len(universities)} universities",
            "count": len(universities),
            "universities": universities
        }
    except Exception as e:
        logger.error(f"Error fetching universities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/programs/search")
def search_programs(request: CourseRequest, db_session: Session = Depends(get_db)):
    """Search for programs matching course in universities from country"""
    try:
        # Get universities for country
        universities = db_session.query(University).filter(
            University.country == request.country
        ).all()
        
        if not universities:
            raise HTTPException(
                status_code=404,
                detail=f"No universities found for {request.country}. Please fetch universities first."
            )
        
        programs_found = []
        
        for university in universities:
            try:
                # Search for courses
                course_links = course_scraper.search_courses(
                    university.translated_name or university.original_name,
                    request.course
                )
                
                for link_info in course_links:
                    url = link_info['url']
                    
                    # Check if program already exists
                    existing = db_session.query(Program).filter(
                        Program.program_url == url
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Detect language
                    is_english, confidence = language_detector.detect_english(url)
                    
                    # Classify UG/PG
                    level, ml_confidence = ml_classifier.classify(
                        link_info.get('title', request.course)
                    )
                    
                    # Get metadata
                    metadata = metadata_checker.check_metadata(url)
                    
                    # Get embedding
                    embedding = ml_classifier.get_embedding(
                        f"{link_info.get('title', request.course)} {request.course}"
                    )
                    
                    # Create program record
                    program = Program(
                        university_id=university.id,
                        course_name=request.course,
                        program_url=url,
                        level=level,
                        taught_in_english=is_english,
                        visited=False,
                        content_hash=metadata.get('content_hash'),
                        embedding_vector=embedding.tobytes(),
                        last_checked=metadata.get('last_checked'),
                        last_modified_header=metadata.get('last_modified_header'),
                        etag=metadata.get('etag'),
                        confidence_score=str(ml_confidence)
                    )
                    db_session.add(program)
                    
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
        
        db_session.commit()
        
        # Count UG/PG
        ug_count = sum(1 for p in programs_found if p['level'] == 'UG')
        pg_count = sum(1 for p in programs_found if p['level'] == 'PG')
        
        return {
            "message": f"Found {len(programs_found)} programs",
            "total": len(programs_found),
            "ug_count": ug_count,
            "pg_count": pg_count,
            "programs": programs_found
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching programs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/programs")
def get_programs(
    country: Optional[str] = None,
    course: Optional[str] = None,
    level: Optional[str] = None,
    english_only: bool = False,
    db_session: Session = Depends(get_db)
):
    """Get programs with filters"""
    try:
        query = db_session.query(Program).join(University)
        
        if country:
            query = query.filter(University.country == country)
        
        if course:
            query = query.filter(Program.course_name.contains(course))
        
        if level:
            query = query.filter(Program.level == level)
        
        if english_only:
            query = query.filter(Program.taught_in_english == True)
        
        programs = query.all()
        
        result = []
        for program in programs:
            university = program.university
            result.append({
                "id": program.id,
                "university": {
                    "id": university.id,
                    "original_name": university.original_name,
                    "translated_name": university.translated_name,
                    "exists_in_gotouniversity": university.exists_in_gotouniversity
                },
                "course_name": program.course_name,
                "program_url": program.program_url,
                "level": program.level,
                "taught_in_english": program.taught_in_english,
                "visited": program.visited,
                "confidence_score": program.confidence_score
            })
        
        ug_count = sum(1 for p in programs if p.level == 'UG')
        pg_count = sum(1 for p in programs if p.level == 'PG')
        
        return {
            "total": len(result),
            "ug_count": ug_count,
            "pg_count": pg_count,
            "programs": result
        }
    
    except Exception as e:
        logger.error(f"Error getting programs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/programs/visit")
def mark_visited(request: ProgramVisitRequest, db_session: Session = Depends(get_db)):
    """Mark program as visited"""
    try:
        program = db_session.query(Program).filter(Program.id == request.program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        program.visited = True
        db_session.commit()
        
        return {"message": "Program marked as visited", "program_id": program.id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking visited: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/query")
def ai_query_endpoint(request: AIQueryRequest):
    """AI query endpoint"""
    try:
        response = ai_query.query(request.question, request.context)
        return {"response": response}
    except Exception as e:
        logger.error(f"AI query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats(db_session: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        total_universities = db_session.query(University).count()
        total_programs = db_session.query(Program).count()
        ug_count = db_session.query(Program).filter(Program.level == 'UG').count()
        pg_count = db_session.query(Program).filter(Program.level == 'PG').count()
        visited_count = db_session.query(Program).filter(Program.visited == True).count()
        english_count = db_session.query(Program).filter(Program.taught_in_english == True).count()
        
        return {
            "total_universities": total_universities,
            "total_programs": total_programs,
            "ug_count": ug_count,
            "pg_count": pg_count,
            "visited_count": visited_count,
            "english_count": english_count
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

