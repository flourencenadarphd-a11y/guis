"""
AI query module
Integrates Gemini or OpenAI for intelligent queries
"""
import os
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIQuery:
    """AI-powered query interface"""
    
    def __init__(self, provider: str = 'gemini', api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client based on provider"""
        if self.provider == 'gemini':
            try:
                import google.generativeai as genai
                if self.api_key:
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini client initialized")
                else:
                    logger.warning("Gemini API key not found")
            except ImportError:
                logger.warning("google-generativeai not installed")
        elif self.provider == 'openai':
            try:
                import openai
                if self.api_key:
                    openai.api_key = self.api_key
                    self.client = openai
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("OpenAI API key not found")
            except ImportError:
                logger.warning("openai not installed")
    
    def query(self, question: str, context: Optional[Dict] = None) -> str:
        """
        Send query to AI with context
        context can include: universities, programs, statistics, etc.
        """
        if not self.client:
            return "AI service not available. Please configure API key."
        
        try:
            # Build prompt with context
            prompt = self._build_prompt(question, context)
            
            if self.provider == 'gemini':
                response = self.client.generate_content(prompt)
                return response.text.strip()
            elif self.provider == 'openai':
                response = self.client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for university program information."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return f"Error processing query: {str(e)}"
    
    def _build_prompt(self, question: str, context: Optional[Dict]) -> str:
        """Build prompt with context"""
        prompt_parts = [question]
        
        if context:
            if 'universities' in context:
                prompt_parts.append(f"\nUniversities in database: {len(context['universities'])}")
            
            if 'programs' in context:
                prompt_parts.append(f"\nPrograms in database: {len(context['programs'])}")
                ug_count = sum(1 for p in context['programs'] if p.get('level') == 'UG')
                pg_count = sum(1 for p in context['programs'] if p.get('level') == 'PG')
                prompt_parts.append(f"Undergraduate: {ug_count}, Postgraduate: {pg_count}")
            
            if 'statistics' in context:
                stats = context['statistics']
                prompt_parts.append(f"\nStatistics: {stats}")
            
            if 'sample_data' in context:
                prompt_parts.append(f"\nSample data: {context['sample_data']}")
        
        return "\n".join(prompt_parts)
    
    def summarize_programs(self, programs: List[Dict]) -> str:
        """Generate summary of programs"""
        if not programs:
            return "No programs to summarize."
        
        question = f"Summarize the following {len(programs)} university programs. Highlight key trends, common features, and notable differences."
        context = {'programs': programs}
        return self.query(question, context)
    
    def compare_programs(self, program1: Dict, program2: Dict) -> str:
        """Compare two programs"""
        question = "Compare these two university programs and highlight their similarities and differences."
        context = {
            'sample_data': f"Program 1: {program1}\nProgram 2: {program2}"
        }
        return self.query(question, context)
    
    def get_insights(self, country: str, course: str, programs: List[Dict]) -> str:
        """Get insights about programs in a country for a course"""
        question = f"Provide insights about {course} programs in {country}. What are the trends, quality indicators, and recommendations?"
        context = {
            'programs': programs,
            'statistics': {
                'country': country,
                'course': course,
                'total': len(programs)
            }
        }
        return self.query(question, context)

