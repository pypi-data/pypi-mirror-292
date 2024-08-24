from pplox.parser import Parser 
from pplox.scanner import Scanner
from pplox.expr import Literal

def parse(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()

def test_boolean_nil():
    assert parse('true').value == Literal(True).value
    assert parse('false').value== Literal(False).value
    assert parse('nil').value == Literal(None).value