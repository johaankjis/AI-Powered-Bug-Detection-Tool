#!/usr/bin/env python3
"""
Project-wide bug scanning script
Scans all code files and generates comprehensive report
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_engine.model import BugDetectionModel

def scan_project(root_dir='.', extensions=['.py', '.js', '.ts', '.jsx', '.tsx']):
    """Scan all code files in project"""
    
    model = BugDetectionModel()
    all_results = {
        'total_files': 0,
        'files_with_bugs': 0,
        'total_issues': 0,
        'severity_breakdown': {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        },
        'files': [],
        'confidence': 0.0
    }
    
    # Find all code files
    code_files = []
    for ext in extensions:
        code_files.extend(Path(root_dir).rglob(f'*{ext}'))
    
    # Filter out node_modules, venv, etc.
    code_files = [
        f for f in code_files 
        if 'node_modules' not in str(f) 
        and 'venv' not in str(f)
        and '.git' not in str(f)
        and 'dist' not in str(f)
    ]
    
    print(f"Scanning {len(code_files)} files...")
    
    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            results = model.predict(code)
            
            all_results['total_files'] += 1
            if results['has_bugs']:
                all_results['files_with_bugs'] += 1
            
            all_results['total_issues'] += results['total_issues']
            
            # Aggregate severity
            for severity, count in results['severity_breakdown'].items():
                all_results['severity_breakdown'][severity] += count
            
            all_results['files'].append({
                'path': str(file_path),
                'has_bugs': results['has_bugs'],
                'total_issues': results['total_issues'],
                'confidence': results['confidence']
            })
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    # Calculate average confidence
    if all_results['total_files'] > 0:
        all_results['confidence'] = sum(
            f['confidence'] for f in all_results['files']
        ) / all_results['total_files']
    
    # Save results
    with open('scan_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate HTML report
    generate_html_report(all_results)
    
    print("\n" + "="*60)
    print("PROJECT SCAN COMPLETE")
    print("="*60)
    print(f"Files scanned: {all_results['total_files']}")
    print(f"Files with bugs: {all_results['files_with_bugs']}")
    print(f"Total issues: {all_results['total_issues']}")
    print(f"Average confidence: {all_results['confidence']:.2%}")
    print("\nSeverity breakdown:")
    for severity, count in all_results['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    print("="*60)
    
    return all_results

def generate_html_report(results):
    """Generate HTML report of scan results"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bug Detection Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
            .critical {{ color: #d32f2f; }}
            .high {{ color: #f57c00; }}
            .medium {{ color: #fbc02d; }}
            .low {{ color: #388e3c; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #333; color: white; }}
        </style>
    </head>
    <body>
        <h1>AI Bug Detection Report</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Files:</strong> {results['total_files']}</p>
            <p><strong>Files with Bugs:</strong> {results['files_with_bugs']}</p>
            <p><strong>Total Issues:</strong> {results['total_issues']}</p>
            <p><strong>Confidence:</strong> {results['confidence']:.1%}</p>
            
            <h3>Severity Breakdown</h3>
            <ul>
                <li class="critical">Critical: {results['severity_breakdown']['critical']}</li>
                <li class="high">High: {results['severity_breakdown']['high']}</li>
                <li class="medium">Medium: {results['severity_breakdown']['medium']}</li>
                <li class="low">Low: {results['severity_breakdown']['low']}</li>
            </ul>
        </div>
        
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Status</th>
                <th>Issues</th>
                <th>Confidence</th>
            </tr>
    """
    
    for file_info in results['files']:
        status = "⚠️ Issues" if file_info['has_bugs'] else "✅ Clean"
        html += f"""
            <tr>
                <td>{file_info['path']}</td>
                <td>{status}</td>
                <td>{file_info['total_issues']}</td>
                <td>{file_info['confidence']:.1%}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    with open('scan_report.html', 'w') as f:
        f.write(html)

if __name__ == "__main__":
    scan_project()
