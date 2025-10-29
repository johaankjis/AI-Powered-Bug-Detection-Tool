#!/usr/bin/env python3
"""
Calculate code quality metrics
"""

import os
from pathlib import Path

def calculate_metrics():
    """Calculate basic code quality metrics"""
    
    metrics = {
        'total_lines': 0,
        'total_files': 0,
        'avg_file_length': 0,
        'comment_lines': 0,
        'blank_lines': 0
    }
    
    code_files = list(Path('.').rglob('*.py')) + list(Path('.').rglob('*.js'))
    code_files = [f for f in code_files if 'node_modules' not in str(f)]
    
    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                metrics['total_files'] += 1
                metrics['total_lines'] += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        metrics['blank_lines'] += 1
                    elif stripped.startswith('#') or stripped.startswith('//'):
                        metrics['comment_lines'] += 1
        except:
            pass
    
    if metrics['total_files'] > 0:
        metrics['avg_file_length'] = metrics['total_lines'] / metrics['total_files']
    
    print("Code Quality Metrics:")
    print(f"  Total files: {metrics['total_files']}")
    print(f"  Total lines: {metrics['total_lines']}")
    print(f"  Average file length: {metrics['avg_file_length']:.1f}")
    print(f"  Comment ratio: {metrics['comment_lines'] / max(metrics['total_lines'], 1):.1%}")
    
    return metrics

if __name__ == "__main__":
    calculate_metrics()
