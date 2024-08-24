#!/usr/bin/env python
import sys
import argparse
from .scanner import Scanner

def main():
    parser = argparse.ArgumentParser(
        prog='pplox',
        description='A Lox interpreter',
    )
    parser.add_argument('filename')           
    parser.add_argument('-t', '--tokenize', action='store_true')
    args = parser.parse_args()

    with open(args.filename) as file:
        file_contents = file.read()
    
    if args.tokenize:
        scanner = Scanner(file_contents)
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token.to_string())
    else:
        print("Interpreter not yet implemented", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
