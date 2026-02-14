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
    
    def check_exists(self, translated_name: str, threshold: float = 0.85) -> Tuple[bool, Optional[str], float]:
        """
        Check if university exists in gotouniversity
        Returns: (exists: bool, matched_name: Optional[str], similarity: float)
        """
        if not translated_name:
            return False, None, 0.0
        
        translated_lower = translated_name.lower()
        
        # Exact match
        if translated_lower in self.universities:
            return True, translated_name, 1.0
        
        # Fuzzy match
        best_match = None
        best_similarity = 0.0
        
        for uni in self.universities:
            similarity = self._similarity(translated_lower, uni)
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

