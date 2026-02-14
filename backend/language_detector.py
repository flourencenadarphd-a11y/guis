"""
Language detection module
Detects if program is taught in English
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import logging
from langdetect import detect, LangDetectException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects if a program page indicates English instruction"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def detect_english(self, url: str) -> Tuple[bool, float]:
        """
        Detect if program is taught in English
        Returns: (is_english: bool, confidence: float)
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return False, 0.0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Check HTML lang attribute
            html_lang = soup.find('html', lang=True)
            if html_lang:
                lang_attr = html_lang.get('lang', '').lower()
                if 'en' in lang_attr:
                    return True, 0.9
            
            # Method 2: Check for "Language of Instruction" text
            page_text = soup.get_text().lower()
            language_indicators = [
                'language of instruction: english',
                'taught in english',
                'instruction in english',
                'english language',
                'medium of instruction: english'
            ]
            
            for indicator in language_indicators:
                if indicator in page_text:
                    return True, 0.95
            
            # Method 3: Use langdetect on main content
            main_content = self._extract_main_content(soup)
            if main_content:
                try:
                    detected_lang = detect(main_content)
                    if detected_lang == 'en':
                        return True, 0.8
                    else:
                        return False, 0.7
                except LangDetectException:
                    pass
            
            # Method 4: Check percentage of English words
            english_ratio = self._calculate_english_ratio(page_text)
            if english_ratio > 0.7:
                return True, english_ratio
            elif english_ratio < 0.3:
                return False, 1.0 - english_ratio
            else:
                # Ambiguous
                return False, 0.5
        
        except Exception as e:
            logger.warning(f"Language detection error for {url}: {e}")
            return False, 0.0
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content from page (skip nav, footer, etc.)"""
        # Try to find main content areas
        main_selectors = [
            'main', 'article', '.content', '#content', '.main-content',
            '.program-description', '.course-description'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text()
        
        # Fallback: get body text, but remove common non-content elements
        body = soup.find('body')
        if body:
            # Remove script, style, nav, footer
            for tag in body.find_all(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            return body.get_text()
        
        return None
    
    def _calculate_english_ratio(self, text: str) -> float:
        """Calculate ratio of English words in text"""
        # Common English words
        common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
            'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one',
            'all', 'would', 'there', 'their', 'program', 'course', 'degree',
            'university', 'study', 'academic', 'bachelor', 'master'
        }
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        english_count = sum(1 for word in words if word in common_english_words)
        return english_count / len(words) if words else 0.0

