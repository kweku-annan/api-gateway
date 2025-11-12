#!/usr/bin/env python3
"""
Validation script to verify Docker container fixes are properly implemented.
Run this before committing to ensure all issues are resolved.
"""

import os
import sys
import re
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if filepath.exists():
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description} not found: {filepath}")
        return False

def check_file_content(filepath, pattern, description):
    """Check if file contains expected pattern"""
    try:
        content = filepath.read_text()
        if re.search(pattern, content, re.MULTILINE):
            print(f"{GREEN}✓{RESET} {description}")
            return True
        else:
            print(f"{RED}✗{RESET} {description} - pattern not found")
            return False
    except Exception as e:
        print(f"{RED}✗{RESET} Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Docker Container Fix Validation")
    print("=" * 60)
    print()
    
    # Base directory
    base_dir = Path(__file__).parent
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: run.py exists
    checks_total += 1
    run_py = base_dir / "run.py"
    if check_file_exists(run_py, "run.py file"):
        checks_passed += 1
    
    # Check 2: run.py exports app at module level
    checks_total += 1
    if check_file_content(
        run_py,
        r'^app\s*=\s*create_app\(',
        "run.py exports 'app' at module level"
    ):
        checks_passed += 1
    
    # Check 3: run.py uses FLASK_ENV
    checks_total += 1
    if check_file_content(
        run_py,
        r"os\.getenv\(['\"]FLASK_ENV['\"]",
        "run.py uses FLASK_ENV environment variable"
    ):
        checks_passed += 1
    
    # Check 4: run.py has startup logging
    checks_total += 1
    if check_file_content(
        run_py,
        r"print.*API Gateway Starting",
        "run.py has startup logging"
    ):
        checks_passed += 1
    
    # Check 5: api/main.py exists
    checks_total += 1
    main_py = base_dir / "api" / "main.py"
    if check_file_exists(main_py, "api/main.py file"):
        checks_passed += 1
    
    # Check 6: create_app uses FLASK_ENV
    checks_total += 1
    if check_file_content(
        main_py,
        r"os\.getenv\(['\"]FLASK_ENV['\"]",
        "create_app() uses FLASK_ENV"
    ):
        checks_passed += 1
    
    # Check 7: Dockerfile exists
    checks_total += 1
    dockerfile = base_dir / "docker" / "Dockerfile"
    if check_file_exists(dockerfile, "Dockerfile"):
        checks_passed += 1
    
    # Check 8: Dockerfile doesn't have invalid healthcheck
    checks_total += 1
    dockerfile_content = dockerfile.read_text()
    if "import requests" not in dockerfile_content:
        print(f"{GREEN}✓{RESET} Dockerfile doesn't have invalid healthcheck with 'requests'")
        checks_passed += 1
    else:
        print(f"{RED}✗{RESET} Dockerfile still has invalid healthcheck requiring 'requests'")
    
    # Check 9: Dockerfile has CMD with gunicorn
    checks_total += 1
    if check_file_content(
        dockerfile,
        r'CMD.*gunicorn.*run:app',
        "Dockerfile CMD uses 'gunicorn run:app'"
    ):
        checks_passed += 1
    
    # Check 10: requirements.txt has gunicorn
    checks_total += 1
    requirements = base_dir / "requirements.txt"
    if check_file_content(
        requirements,
        r'^gunicorn',
        "requirements.txt includes gunicorn"
    ):
        checks_passed += 1
    
    # Check 11: Config uses environment variables
    checks_total += 1
    config_py = base_dir / "api" / "config.py"
    if check_file_content(
        config_py,
        r"os\.getenv\(['\"]RABBITMQ_HOST['\"]",
        "config.py uses environment variables"
    ):
        checks_passed += 1
    
    # Check 12: Health endpoint exists
    checks_total += 1
    health_py = base_dir / "api" / "routes" / "health.py"
    if check_file_exists(health_py, "health.py endpoint"):
        checks_passed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print(f"{GREEN}✓ All validation checks passed!{RESET}")
        print()
        print("Next steps:")
        print("1. Run: chmod +x test_startup.sh")
        print("2. Run: ./test_startup.sh")
        print("3. Commit and push changes")
        return 0
    else:
        print(f"{RED}✗ Some validation checks failed{RESET}")
        print(f"{YELLOW}Please review the issues above before proceeding{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

