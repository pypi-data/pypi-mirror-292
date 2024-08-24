#!/usr/bin/env python
import sys
from pplox.scanner import Scanner
from pplox.error_reporter import ErrorReporter
from pplox.parser import Parser
from pplox.ast_printer import AstPrinter

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh [tokenize, parse] <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize" and command != "parse":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()
    if command == "tokenize":
        for token in tokens:
            print(token.to_string())
    
    if command == "parse":
        parser = Parser(tokens)
        expr = parser.parse()
        print(AstPrinter().print(expr))

    if ErrorReporter.had_error:
        exit(65)

if __name__ == "__main__":
    main()
