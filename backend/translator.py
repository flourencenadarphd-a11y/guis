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
        Translate text to English - ALWAYS ATTEMPTS TRANSLATION
        Returns original text only if translation fails or already English
        """
        if not text:
            return text
        
        # Check cache
        if text in self.cache:
            return self.cache[text]
        
        # Check if already English (but still try translation for accuracy)
        is_english = self._is_english(text)
        
        # ALWAYS try translation (even if seems English, to ensure accuracy)
        try:
            if self.use_gemini and self.gemini_api_key:
                translated = self._translate_with_gemini(text)
            else:
                translated = self._translate_with_google(text, source_lang)
            
            # If translation succeeded and is different
            if translated and translated.strip() and translated.lower() != text.lower():
                self.cache[text] = translated
                logger.info(f"Translated: '{text}' -> '{translated}'")
                return translated
            elif translated and translated.strip():
                # Translation returned same or similar - might be English
                self.cache[text] = translated
                return translated
            else:
                # Translation failed
                if is_english:
                    # Likely English, return original
                    self.cache[text] = text
                    return text
                else:
                    # Not English but translation failed - log and return original
                    logger.warning(f"Translation failed for '{text}', returning original")
                    self.cache[text] = text
                    return text
        except Exception as e:
            logger.warning(f"Translation error for '{text}': {e}")
            # If seems English, return original; otherwise log error
            if is_english:
                self.cache[text] = text
                return text
            else:
                logger.error(f"Could not translate non-English text '{text}': {e}")
                self.cache[text] = text
                return text
    
    def _is_english(self, text: str) -> bool:
        """Check if text is likely English - IMPROVED"""
        # Use langdetect for better accuracy
        try:
            from langdetect import detect, LangDetectException
            try:
                detected_lang = detect(text)
                return detected_lang == 'en'
            except LangDetectException:
                # If detection fails, check for non-English characters
                pass
        except ImportError:
            # Fallback if langdetect not available
            pass
        
        # Check for non-English characters (more reliable)
        text_lower = text.lower()
        # Common non-English characters/patterns
        non_english_patterns = [
            'ä', 'ö', 'ü', 'ß',  # German
            'é', 'è', 'ê', 'ë', 'à', 'â', 'ç',  # French
            'á', 'é', 'í', 'ó', 'ú', 'ñ',  # Spanish
            'č', 'ć', 'đ', 'š', 'ž',  # Slavic
            'å', 'æ', 'ø',  # Nordic
        ]
        
        # If contains non-English characters, likely not English
        if any(char in text for char in non_english_patterns):
            return False
        
        # Check if it's clearly English (all ASCII, common English words)
        english_indicators = ['university', 'college', 'institute', 'school', 'academy']
        has_english_word = any(indicator in text_lower for indicator in english_indicators)
        
        # If has English word AND no non-English characters, likely English
        if has_english_word and all(ord(c) < 128 for c in text):
            return True
        
        # Default: try to translate (assume not English)
        return False
    
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

