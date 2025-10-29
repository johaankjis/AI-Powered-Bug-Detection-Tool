"""
AI Bug Detection Model
Implements a machine learning model for detecting bugs in code
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import re
from typing import List, Dict, Tuple

class BugDetectionModel:
    """
    Machine Learning model for detecting potential bugs in code
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42
        )
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            token_pattern=r'\b\w+\b'
        )
        self.bug_patterns = self._load_bug_patterns()
        
    def _load_bug_patterns(self) -> List[Dict[str, str]]:
        """Load common bug patterns for detection"""
        return [
            {
                'pattern': r'==\s*None',
                'severity': 'medium',
                'message': 'Use "is None" instead of "== None"'
            },
            {
                'pattern': r'except\s*:',
                'severity': 'high',
                'message': 'Bare except clause - specify exception type'
            },
            {
                'pattern': r'eval\s*\(',
                'severity': 'critical',
                'message': 'Use of eval() is dangerous - security risk'
            },
            {
                'pattern': r'exec\s*\(',
                'severity': 'critical',
                'message': 'Use of exec() is dangerous - security risk'
            },
            {
                'pattern': r'var\s+\w+\s*=',
                'severity': 'low',
                'message': 'Use let or const instead of var in JavaScript'
            },
            {
                'pattern': r'console\.log\(',
                'severity': 'low',
                'message': 'Remove console.log before production'
            },
            {
                'pattern': r'TODO|FIXME|HACK',
                'severity': 'medium',
                'message': 'Unresolved TODO/FIXME comment'
            },
            {
                'pattern': r'password\s*=\s*["\']',
                'severity': 'critical',
                'message': 'Hardcoded password detected - security risk'
            },
            {
                'pattern': r'api[_-]?key\s*=\s*["\']',
                'severity': 'critical',
                'message': 'Hardcoded API key detected - security risk'
            },
            {
                'pattern': r'\.innerHTML\s*=',
                'severity': 'high',
                'message': 'Potential XSS vulnerability with innerHTML'
            }
        ]
    
    def extract_features(self, code: str) -> np.ndarray:
        """Extract features from code for ML model"""
        features = []
        
        # Code complexity metrics
        features.append(len(code.split('\n')))  # Line count
        features.append(code.count('if'))  # Conditional complexity
        features.append(code.count('for') + code.count('while'))  # Loop complexity
        features.append(code.count('try'))  # Exception handling
        features.append(code.count('def') + code.count('function'))  # Function count
        features.append(len(re.findall(r'\b[A-Z_]+\b', code)))  # Constants
        features.append(code.count('import') + code.count('require'))  # Dependencies
        
        # Code smell indicators
        features.append(1 if len(code) > 1000 else 0)  # Long file
        features.append(1 if code.count('\n') > 300 else 0)  # Too many lines
        features.append(code.count('# TODO') + code.count('// TODO'))  # TODOs
        
        return np.array(features).reshape(1, -1)
    
    def detect_pattern_bugs(self, code: str) -> List[Dict]:
        """Detect bugs using regex patterns"""
        bugs = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern_info in self.bug_patterns:
                if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                    bugs.append({
                        'line': i,
                        'severity': pattern_info['severity'],
                        'message': pattern_info['message'],
                        'code': line.strip(),
                        'type': 'pattern'
                    })
        
        return bugs
    
    def predict(self, code: str) -> Dict:
        """
        Predict if code contains bugs
        Returns detection results with confidence score
        """
        # Pattern-based detection
        pattern_bugs = self.detect_pattern_bugs(code)
        
        # ML-based detection (simulated for MVP)
        features = self.extract_features(code)
        
        # Calculate bug probability based on features
        complexity_score = features[0][1] + features[0][2]  # if + loops
        line_count = features[0][0]
        
        # Simple heuristic for MVP (would be replaced with trained model)
        bug_probability = min(0.95, (complexity_score * 0.1 + line_count * 0.001))
        has_bugs = bug_probability > 0.3 or len(pattern_bugs) > 0
        
        return {
            'has_bugs': has_bugs,
            'confidence': float(bug_probability),
            'bugs_found': pattern_bugs,
            'total_issues': len(pattern_bugs),
            'severity_breakdown': self._calculate_severity(pattern_bugs)
        }
    
    def _calculate_severity(self, bugs: List[Dict]) -> Dict[str, int]:
        """Calculate severity breakdown of detected bugs"""
        severity_count = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for bug in bugs:
            severity_count[bug['severity']] += 1
        return severity_count
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer
            }, f)
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.vectorizer = data['vectorizer']
