"""
Integration tests for the bug detection system
"""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_engine.model import BugDetectionModel
from ml_engine.detect import detect_bugs

class TestIntegration:
    """Integration tests for end-to-end workflows"""
    
    def test_detect_bugs_function(self):
        """Test the detect_bugs function"""
        code = '''
def vulnerable():
    password = "admin123"
    eval(user_input)
        '''
        
        results = detect_bugs(code)
        
        assert 'has_bugs' in results
        assert 'confidence' in results
        assert 'bugs_found' in results
        assert results['has_bugs'] == True
        assert results['total_issues'] > 0
    
    def test_full_pipeline(self):
        """Test complete detection pipeline"""
        # Create test file
        test_code = '''
import os

def process_data():
    api_key = "sk-test123"
    
    try:
        data = fetch_data(api_key)
    except:
        pass
    
    return data
        '''
        
        model = BugDetectionModel()
        results = model.predict(test_code)
        
        # Verify results structure
        assert isinstance(results, dict)
        assert 'has_bugs' in results
        assert 'confidence' in results
        assert 'bugs_found' in results
        assert 'total_issues' in results
        assert 'severity_breakdown' in results
        
        # Verify bug detection
        assert results['has_bugs'] == True
        assert results['total_issues'] >= 2  # api_key + bare except
        
        # Verify severity breakdown
        severity = results['severity_breakdown']
        assert severity['critical'] > 0  # api_key
        assert severity['high'] > 0  # bare except
    
    def test_batch_processing(self):
        """Test processing multiple files"""
        files = [
            'password = "test"',
            'const x = 10;',
            'eval(input)',
        ]
        
        model = BugDetectionModel()
        results = []
        
        for code in files:
            result = model.predict(code)
            results.append(result)
        
        assert len(results) == 3
        assert results[0]['has_bugs'] == True  # password
        assert results[2]['has_bugs'] == True  # eval
    
    def test_performance(self):
        """Test detection performance on larger code"""
        import time
        
        # Generate larger code sample
        code = '\n'.join([
            'def function_{}():'.format(i) +
            '\n    if condition:\n        pass'
            for i in range(100)
        ])
        
        model = BugDetectionModel()
        
        start = time.time()
        results = model.predict(code)
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 1.0  # Less than 1 second
        assert results is not None
    
    def test_empty_code(self):
        """Test handling of empty code"""
        model = BugDetectionModel()
        results = model.predict('')
        
        assert results['has_bugs'] == False
        assert results['total_issues'] == 0
    
    def test_malformed_code(self):
        """Test handling of malformed code"""
        model = BugDetectionModel()
        
        # Code with syntax errors should still be analyzed
        code = 'def broken( incomplete'
        results = model.predict(code)
        
        assert results is not None
        assert 'has_bugs' in results

class TestAccuracy:
    """Tests for model accuracy metrics"""
    
    def test_accuracy_threshold(self):
        """Test that model meets accuracy threshold"""
        model = BugDetectionModel()
        
        # Test cases with known bugs
        buggy_samples = [
            ('password = "test"', True),
            ('eval(input)', True),
            ('except:', True),
            ('api_key = "sk-123"', True),
            ('console.log("test")', True),
        ]
        
        correct = 0
        for code, expected_bug in buggy_samples:
            result = model.predict(code)
            if result['has_bugs'] == expected_bug:
                correct += 1
        
        accuracy = correct / len(buggy_samples)
        
        # Should meet 85% accuracy threshold
        assert accuracy >= 0.85, f"Accuracy {accuracy:.1%} below 85% threshold"
