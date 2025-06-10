#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def count_lines(directory='.'):
    total_lines = 0
    
    # Common code file extensions
    code_extensions = {'.py', '.html', '.css', '.js', '.json', '.txt', '.md', '.sql', '.yml', '.yaml'}
    
    # Directories to skip
    skip_dirs = {'__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', 'migrations'}
    
    for root, dirs, files in os.walk(directory):
        # Remove skip directories from the walk
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Only count files with code extensions
            if file_path.suffix.lower() in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    continue
    
    return total_lines

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    total = count_lines(directory)
    print(total)