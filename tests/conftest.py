"""
PyTest configuration and fixtures
"""

import pytest
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture(scope="session")
def sample_buggy_code():
    """Fixture providing sample buggy code"""
    return '''
def vulnerable_function():
    password = "hardcoded123"
    api_key = "sk-1234567890"
    
    try:
        result = eval(user_input)
    except:
        pass
    
    if result == None:
        console.log("Error")
    
    return result
    '''

@pytest.fixture(scope="session")
def sample_clean_code():
    """Fixture providing sample clean code"""
    return '''
import os
import logging

logger = logging.getLogger(__name__)

def safe_function(user_input):
    """Safely process user input"""
    password = os.getenv("PASSWORD")
    api_key = os.getenv("API_KEY")
    
    if user_input is None:
        logger.warning("No input provided")
        return None
    
    try:
        result = safe_parse(user_input)
    except ValueError as e:
        logger.error(f"Parse error: {e}")
        return None
    
    return result
    '''

@pytest.fixture
def temp_code_file(tmp_path):
    """Create temporary code file for testing"""
    def _create_file(content, filename="test.py"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return str(file_path)
    
    return _create_file
