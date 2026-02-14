"""
Gotouniversity checker module
Checks if translated university exists in gotouniversity.csv
"""
import csv
import os
from typing import Optional, Tuple
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GotoUniChecker:
    """Checks university existence in gotouniversity database"""
    
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            # Default to project root data directory
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(project_root, 'data', 'gotouniversity.csv')
        self.csv_path = csv_path
        self.universities = set()
        self._load_csv()
    
    def _load_csv(self):
        """Load universities from CSV file"""
        if not os.path.exists(self.csv_path):
            logger.warning(f"CSV file not found: {self.csv_path}")
            return
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header if exists
                for row in reader:
                    if row:
                        # Assume first column is university name
                        university_name = row[0].strip()
                        if university_name:
                            self.universities.add(university_name.lower())
            logger.info(f"Loaded {len(self.universities)} universities from CSV")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
    
    def check_exists(self, translated_name: str, threshold: float = 0.80) -> Tuple[bool, Optional[str], float]:
        """
        Check if university exists in gotouniversity - IMPROVED ACCURACY
        Returns: (exists: bool, matched_name: Optional[str], similarity: float)
        """
        if not translated_name:
            return False, None, 0.0
        
        translated_lower = translated_name.lower().strip()
        translated_words = set(translated_lower.split())
        
        # Exact match
        if translated_lower in self.universities:
            return True, translated_name, 1.0
        
        # Method 1: Token-based matching (more accurate)
        best_match = None
        best_similarity = 0.0
        
        for uni in self.universities:
            uni_words = set(uni.split())
            
            # Calculate word overlap
            if translated_words and uni_words:
                common_words = translated_words.intersection(uni_words)
                word_overlap = len(common_words) / max(len(translated_words), len(uni_words))
            else:
                word_overlap = 0.0
            
            # Calculate string similarity
            string_sim = self._similarity(translated_lower, uni)
            
            # Combined score (weighted: 60% word overlap, 40% string similarity)
            combined_score = (word_overlap * 0.6) + (string_sim * 0.4)
            
            # Bonus for containing key words
            key_words = ['university', 'college', 'institute', 'school']
            if any(kw in translated_lower and kw in uni for kw in key_words):
                combined_score += 0.1
            
            # Penalty for very different lengths
            length_diff = abs(len(translated_lower) - len(uni)) / max(len(translated_lower), len(uni))
            if length_diff > 0.5:
                combined_score *= 0.8
            
            if combined_score > best_similarity:
                best_similarity = combined_score
                best_match = uni
        
        # Method 2: Check if key words match (for partial matches)
        if best_similarity < threshold:
            # Extract key words from translated name
            key_terms = [w for w in translated_words if len(w) > 3 and w not in ['the', 'of', 'and', 'in', 'at']]
            
            for uni in self.universities:
                uni_words = set(uni.split())
                matching_key_terms = sum(1 for term in key_terms if term in uni_words)
                
                if matching_key_terms >= 2:  # At least 2 key terms match
                    similarity = matching_key_terms / max(len(key_terms), 3)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = uni
        
        if best_similarity >= threshold:
            return True, best_match, best_similarity
        
        return False, None, best_similarity
    
    def _similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _levenshtein_distance(self, str1: str, str2: str) -> int:
        """Calculate Levenshtein distance (alternative method)"""
        if len(str1) < len(str2):
            return self._levenshtein_distance(str2, str1)
        
        if len(str2) == 0:
            return len(str1)
        
        previous_row = range(len(str2) + 1)
        for i, c1 in enumerate(str1):
            current_row = [i + 1]
            for j, c2 in enumerate(str2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

