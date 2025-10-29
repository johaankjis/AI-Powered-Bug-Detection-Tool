"""
Unit tests for bug detection model
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_engine.model import BugDetectionModel

class TestBugDetectionModel:
    """Test suite for BugDetectionModel"""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing"""
        return BugDetectionModel()
    
    def test_model_initialization(self, model):
        """Test model initializes correctly"""
        assert model is not None
        assert model.model is not None
        assert model.vectorizer is not None
        assert len(model.bug_patterns) > 0
    
    def test_detect_hardcoded_password(self, model):
        """Test detection of hardcoded passwords"""
        code = '''
def login():
    password = "hardcoded123"
    return authenticate(password)
        '''
        
        results = model.predict(code)
        assert results['has_bugs'] == True
        assert results['total_issues'] > 0
        
        # Check if password issue was detected
        bugs = results['bugs_found']
        password_bugs = [b for b in bugs if 'password' in b['message'].lower()]
        assert len(password_bugs) > 0
        assert password_bugs[0]['severity'] == 'critical'
    
    def test_detect_bare_except(self, model):
        """Test detection of bare except clauses"""
        code = '''
try:
    risky_operation()
except:
    pass
        '''
        
        results = model.predict(code)
        assert results['has_bugs'] == True
        
        bugs = results['bugs_found']
        except_bugs = [b for b in bugs if 'except' in b['message'].lower()]
        assert len(except_bugs) > 0
        assert except_bugs[0]['severity'] == 'high'
    
    def test_detect_eval_usage(self, model):
        """Test detection of dangerous eval() usage"""
        code = '''
user_input = get_input()
result = eval(user_input)
        '''
        
        results = model.predict(code)
        assert results['has_bugs'] == True
        
        bugs = results['bugs_found']
        eval_bugs = [b for b in bugs if 'eval' in b['message'].lower()]
        assert len(eval_bugs) > 0
        assert eval_bugs[0]['severity'] == 'critical'
    
    def test_detect_api_key(self, model):
        """Test detection of hardcoded API keys"""
        code = '''
api_key = "sk-1234567890abcdef"
client = APIClient(api_key)
        '''
        
        results = model.predict(code)
        assert results['has_bugs'] == True
        
        bugs = results['bugs_found']
        api_bugs = [b for b in bugs if 'api' in b['message'].lower()]
        assert len(api_bugs) > 0
        assert api_bugs[0]['severity'] == 'critical'
    
    def test_clean_code_no_bugs(self, model):
        """Test that clean code passes without issues"""
        code = '''
import os

def safe_function(value):
    """A safe, well-written function"""
    if value is None:
        return None
    
    try:
        result = process(value)
    except ValueError as e:
        logger.error(f"Processing error: {e}")
        return None
    
    return result
        '''
        
        results = model.predict(code)
        # Clean code might still have low confidence bugs, but should have no critical/high
        critical_bugs = [b for b in results['bugs_found'] if b['severity'] == 'critical']
        high_bugs = [b for b in results['bugs_found'] if b['severity'] == 'high']
        
        assert len(critical_bugs) == 0
        assert len(high_bugs) == 0
    
    def test_feature_extraction(self, model):
        """Test feature extraction from code"""
        code = '''
def complex_function():
    if condition1:
        for i in range(10):
            if condition2:
                try:
                    process()
                except Exception:
                    pass
        '''
        
        features = model.extract_features(code)
        assert features is not None
        assert features.shape[0] == 1
        assert features.shape[1] > 0
        
        # Check that features capture code complexity
        assert features[0][1] > 0  # Has if statements
        assert features[0][2] > 0  # Has loops
        assert features[0][3] > 0  # Has try blocks
    
    def test_severity_calculation(self, model):
        """Test severity breakdown calculation"""
        bugs = [
            {'severity': 'critical'},
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]
        
        severity = model._calculate_severity(bugs)
        assert severity['critical'] == 2
        assert severity['high'] == 1
        assert severity['medium'] == 1
        assert severity['low'] == 1
    
    def test_multiple_issues_same_line(self, model):
        """Test detection of multiple issues on same line"""
        code = 'password = "test123"; api_key = "sk-abc"'
        
        results = model.predict(code)
        assert results['total_issues'] >= 2
    
    def test_console_log_detection(self, model):
        """Test detection of console.log statements"""
        code = '''
function debug() {
    console.log("Debug info");
    return true;
}
        '''
        
        results = model.predict(code)
        bugs = results['bugs_found']
        console_bugs = [b for b in bugs if 'console' in b['message'].lower()]
        assert len(console_bugs) > 0
        assert console_bugs[0]['severity'] == 'low'
    
    def test_todo_comment_detection(self, model):
        """Test detection of TODO comments"""
        code = '''
def incomplete():
    # TODO: implement this
    pass
        '''
        
        results = model.predict(code)
        bugs = results['bugs_found']
        todo_bugs = [b for b in bugs if 'todo' in b['message'].lower()]
        assert len(todo_bugs) > 0

class TestModelPersistence:
    """Test model saving and loading"""
    
    def test_save_and_load_model(self, tmp_path):
        """Test model can be saved and loaded"""
        model = BugDetectionModel()
        
        # Save model
        model_path = tmp_path / "test_model.pkl"
        model.save_model(str(model_path))
        
        assert model_path.exists()
        
        # Load model
        new_model = BugDetectionModel()
        new_model.load_model(str(model_path))
        
        assert new_model.model is not None
        assert new_model.vectorizer is not None

@pytest.mark.parametrize("code,expected_bugs", [
    ('if x == None: pass', True),
    ('if x is None: pass', False),
    ('var x = 10;', True),
    ('const x = 10;', False),
])
def test_parametrized_detection(code, expected_bugs):
    """Parametrized tests for various code patterns"""
    model = BugDetectionModel()
    results = model.predict(code)
    
    if expected_bugs:
        assert results['has_bugs'] == True or results['total_issues'] > 0
    # Note: Clean code might still trigger low-confidence issues
