#!/usr/bin/env python
"""
Test runner for Golf League Manager backend API tests.
This script runs the pytest suite for the backend API.
"""

import os
import sys
import subprocess
import argparse

def main():
    """Run the test suite."""
    parser = argparse.ArgumentParser(description='Run Golf League Manager API tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--test-file', '-f', help='Run specific test file')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')
    args = parser.parse_args()

    # Set up the command
    cmd = ['pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    if args.coverage:
        cmd.extend(['--cov=../lambda/resolvers', '--cov-report=term', '--cov-report=html'])
    
    if args.test_file:
        cmd.append(args.test_file)
    
    # Run the tests
    print(f"Running tests with command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
