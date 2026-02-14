"""
ML classification module for UG/PG classification
Uses SentenceTransformers for embeddings and scikit-learn for classification
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from typing import Tuple, Optional
import logging
import pickle
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLClassifier:
    """ML-based UG/PG classifier"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
        self.classifier = None
        self.is_trained = False
        # Store model in project root
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(project_root, 'ml_classifier_model.pkl')
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing model or initialize new one"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                    self.is_trained = True
                logger.info("Loaded existing ML classifier model")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
                self._initialize_classifier()
        else:
            self._initialize_classifier()
            self._train_initial_model()
    
    def _initialize_classifier(self):
        """Initialize the classifier"""
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.is_trained = False
    
    def _train_initial_model(self):
        """Train initial model with common examples"""
        # Training data: (text, label) where 0=UG, 1=PG
        training_data = [
            # Undergraduate examples
            ("Bachelor of Science in Computer Science", 0),
            ("BSc Information Technology", 0),
            ("Bachelor of Arts", 0),
            ("Undergraduate degree in Engineering", 0),
            ("BA in Business Administration", 0),
            ("Bachelor's program", 0),
            ("Undergraduate studies", 0),
            ("BSc IT", 0),
            ("BA Economics", 0),
            ("Bachelor degree", 0),
            
            # Postgraduate examples
            ("Master of Science in Data Science", 1),
            ("MSc Computer Science", 1),
            ("Master of Arts", 1),
            ("Postgraduate degree", 1),
            ("MA in Literature", 1),
            ("Master's program", 1),
            ("Graduate studies", 1),
            ("MSc Data Science", 1),
            ("PhD program", 1),
            ("Doctorate", 1),
            
            # Ambiguous cases
            ("Data Science program", 0),  # Default to UG if ambiguous
            ("Computer Science course", 0),
            ("Engineering program", 0),
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Train classifier
        self.classifier.fit(embeddings, labels)
        self.is_trained = True
        
        # Save model
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.classifier, f)
            logger.info("Initial ML classifier model trained and saved")
        except Exception as e:
            logger.warning(f"Failed to save model: {e}")
    
    def classify(self, program_title: str, page_content_snippet: Optional[str] = None) -> Tuple[str, float]:
        """
        Classify program as UG or PG
        Returns: (level: 'UG' or 'PG', confidence: float)
        """
        # First try rule-based
        rule_result = self._rule_based_classify(program_title)
        if rule_result[1] > 0.9:  # High confidence rule-based
            return rule_result
        
        # If ambiguous, use ML
        if self.is_trained:
            combined_text = program_title
            if page_content_snippet:
                combined_text += " " + page_content_snippet[:500]  # Limit snippet length
            
            # Generate embedding
            embedding = self.embedding_model.encode([combined_text])
            
            # Predict
            prediction = self.classifier.predict(embedding)[0]
            probabilities = self.classifier.predict_proba(embedding)[0]
            confidence = float(max(probabilities))
            
            level = 'PG' if prediction == 1 else 'UG'
            return level, confidence
        
        # Fallback to rule-based
        return rule_result
    
    def _rule_based_classify(self, text: str) -> Tuple[str, float]:
        """
        Rule-based classification
        Returns: (level, confidence)
        """
        text_lower = text.lower()
        
        # UG keywords
        ug_keywords = [
            'bachelor', 'bsc', 'ba', 'undergraduate', 'b.tech', 'btech',
            'bachelor\'s', 'bachelors', 'undergrad'
        ]
        
        # PG keywords
        pg_keywords = [
            'master', 'msc', 'ma', 'postgraduate', 'm.tech', 'mtech',
            'master\'s', 'masters', 'phd', 'doctorate', 'doctoral',
            'graduate', 'mba', 'mphil'
        ]
        
        ug_count = sum(1 for keyword in ug_keywords if keyword in text_lower)
        pg_count = sum(1 for keyword in pg_keywords if keyword in text_lower)
        
        if pg_count > ug_count and pg_count > 0:
            return 'PG', 0.95
        elif ug_count > pg_count and ug_count > 0:
            return 'UG', 0.95
        elif ug_count == pg_count and ug_count > 0:
            # Ambiguous
            return 'UG', 0.5  # Default to UG
        else:
            # No keywords found
            return 'UG', 0.3  # Default to UG with low confidence
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text"""
        return self.embedding_model.encode([text])[0]
    
    def update_model(self, texts: list, labels: list):
        """
        Update model with new training data
        labels: 0 for UG, 1 for PG
        """
        if not texts or not labels:
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Retrain or update classifier
        if self.is_trained:
            # Combine with existing training data if available
            # For simplicity, retrain on new data
            self.classifier.fit(embeddings, labels)
        else:
            self.classifier.fit(embeddings, labels)
            self.is_trained = True
        
        # Save updated model
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.classifier, f)
            logger.info("ML classifier model updated")
        except Exception as e:
            logger.warning(f"Failed to save updated model: {e}")

