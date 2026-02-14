"""
Translation module for university names
Uses deep_translator and optionally Gemini API
"""
from typing import Optional
import logging
from deep_translator import GoogleTranslator
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Translator:
    """Translates university names to English"""
    
    def __init__(self, use_gemini: bool = False, gemini_api_key: Optional[str] = None):
        self.use_gemini = use_gemini
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.translator = GoogleTranslator(source='auto', target='en')
        self.cache = {}  # Simple in-memory cache
    
    def translate(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to English
        Returns original text if already in English or translation fails
        """
        if not text:
            return text
        
        # Check cache
        if text in self.cache:
            return self.cache[text]
        
        # Check if already English
        if self._is_english(text):
            self.cache[text] = text
            return text
        
        # Try translation
        try:
            if self.use_gemini and self.gemini_api_key:
                translated = self._translate_with_gemini(text)
            else:
                translated = self._translate_with_google(text, source_lang)
            
            if translated and translated != text:
                self.cache[text] = translated
                return translated
            else:
                # Translation failed or same, return original
                self.cache[text] = text
                return text
        except Exception as e:
            logger.warning(f"Translation failed for '{text}': {e}")
            self.cache[text] = text
            return text
    
    def _is_english(self, text: str) -> bool:
        """Simple check if text is likely English"""
        # Check for common English words in university names
        english_indicators = [
            'university', 'college', 'institute', 'school', 'academy',
            'of', 'the', 'and', 'for', 'in', 'at'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in english_indicators)
    
    def _translate_with_google(self, text: str, source_lang: Optional[str] = None) -> Optional[str]:
        """Translate using Google Translator (deep_translator)"""
        try:
            if source_lang:
                translator = GoogleTranslator(source=source_lang, target='en')
            else:
                translator = self.translator
            
            translated = translator.translate(text)
            return translated
        except Exception as e:
            logger.error(f"Google translation error: {e}")
            return None
    
    def _translate_with_gemini(self, text: str) -> Optional[str]:
        """Translate using Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"Translate the following university name to English. Only return the translation, nothing else: {text}"
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini translation error: {e}")
            return None

