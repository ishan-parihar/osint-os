#!/usr/bin/env python3
"""
Systematic fix for MyPy type errors in OSINT-OS backend
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

def run_mypy_check(path: str) -> Tuple[int, List[str]]:
    """Run MyPy on a path and return error count and errors."""
    cmd = [
        sys.executable, "-m", "mypy", 
        path,
        "--ignore-missing-imports",
        "--show-error-codes", 
        "--explicit-package-bases"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="backend")
        errors = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return result.returncode, errors
    except Exception as e:
        return 1, [f"Error running MyPy: {e}"]

def categorize_errors(errors: List[str]) -> Dict[str, List[str]]:
    """Categorize errors by type."""
    categories = {
        'syntax': [],
        'missing_return_type': [],
        'missing_type_annotation': [],
        'import_issues': [],
        'type_mismatch': [],
        'other': []
    }
    
    for error in errors:
        if 'syntax' in error.lower():
            categories['syntax'].append(error)
        elif 'no-untyped-def' in error:
            categories['missing_return_type'].append(error)
        elif 'var-annotated' in error or 'type-arg' in error:
            categories['missing_type_annotation'].append(error)
        elif 'implicitly relative' in error or 'no module named' in error:
            categories['import_issues'].append(error)
        elif 'assignment' in error or 'arg-type' in error:
            categories['type_mismatch'].append(error)
        else:
            categories['other'].append(error)
    
    return categories

def fix_missing_return_types(file_path: str) -> int:
    """Fix missing return type annotations in a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Pattern to find function definitions without return type
        pattern = r'^(\s*)def\s+(\w+)\s*\([^)]*\)\s*:$'
        
        lines = content.split('\n')
        fixes = 0
        
        for i, line in enumerate(lines):
            if re.match(pattern, line) and '->' not in line:
                # Check if it's a test function (should return None)
                if 'test_' in line or line.strip().startswith('def test_'):
                    indent = len(line) - len(line.lstrip())
                    lines[i] = line.rstrip() + ' -> None:'
                    fixes += 1
                # Check if function has return statements
                elif i + 1 < len(lines):
                    # Simple heuristic: if no obvious return, assume None
                    if not any('return' in lines[j] for j in range(i+1, min(i+10, len(lines)))):
                        indent = len(line) - len(line.lstrip())
                        lines[i] = line.rstrip() + ' -> None:'
                        fixes += 1
        
        if fixes > 0:
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            print(f"Fixed {fixes} return type annotations in {file_path}")
        
        return fixes
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return 0

def main():
    """Main function to systematically fix type errors."""
    print("🔧 Starting systematic MyPy error fixes...")
    
    # Check overall status
    returncode, errors = run_mypy_check("backend/")
    print(f"📊 Current error count: {len(errors)}")
    
    # Categorize errors
    categories = categorize_errors(errors)
    for category, error_list in categories.items():
        if error_list:
            print(f"  {category}: {len(error_list)} errors")
    
    # Focus on critical files first
    critical_files = [
        "backend/app/security/integration.py",
        "backend/app/services/websocket.py", 
        "backend/app/services/multi_search_service.py",
        "backend/app/services/content_intelligence_service.py"
    ]
    
    # Fix missing return types in test files first
    test_files = list(Path("backend").glob("**/test_*.py"))
    print(f"\n🧪 Fixing {len(test_files)} test files...")
    
    total_fixes = 0
    for test_file in test_files:
        fixes = fix_missing_return_types(str(test_file))
        total_fixes += fixes
    
    print(f"✅ Fixed {total_fixes} return type annotations in test files")
    
    # Re-check
    returncode, errors = run_mypy_check("backend/")
    print(f"\n📊 Updated error count: {len(errors)}")
    
    if len(errors) < 100:
        print("\n🎉 Progress made! Error count reduced significantly.")
        categories = categorize_errors(errors)
        for category, error_list in categories.items():
            if error_list:
                print(f"  {category}: {len(error_list)} errors")
    else:
        print("\n⚠️  Still many errors remaining. Need more focused fixes.")

if __name__ == "__main__":
    main()