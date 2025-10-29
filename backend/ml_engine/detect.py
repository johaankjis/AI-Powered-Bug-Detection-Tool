"""
Bug detection inference script
"""

from model import BugDetectionModel
import sys
import json

def detect_bugs(code: str, model_path: str = None) -> dict:
    """
    Detect bugs in provided code
    
    Args:
        code: Source code to analyze
        model_path: Path to trained model (optional)
    
    Returns:
        Detection results dictionary
    """
    model = BugDetectionModel()
    
    if model_path:
        try:
            model.load_model(model_path)
        except FileNotFoundError:
            print("Warning: Model file not found, using default patterns")
    
    results = model.predict(code)
    return results

def main():
    """CLI interface for bug detection"""
    if len(sys.argv) < 2:
        print("Usage: python detect.py <code_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    print(f"Analyzing {file_path}...")
    results = detect_bugs(code)
    
    print("\n" + "="*50)
    print("BUG DETECTION RESULTS")
    print("="*50)
    print(f"Bugs Found: {results['has_bugs']}")
    print(f"Confidence: {results['confidence']:.2%}")
    print(f"Total Issues: {results['total_issues']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in results['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    
    if results['bugs_found']:
        print(f"\nDetailed Issues:")
        for bug in results['bugs_found']:
            print(f"\n  Line {bug['line']} [{bug['severity'].upper()}]")
            print(f"  Message: {bug['message']}")
            print(f"  Code: {bug['code']}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
