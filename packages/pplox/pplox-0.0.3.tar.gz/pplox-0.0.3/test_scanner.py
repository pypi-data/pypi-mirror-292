from pplox.scanner import Scanner
from pplox.error_reporter import ErrorReporter

def test_parens():
    scanner = Scanner("(()")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 4
    assert tokens[0].to_string() == "LEFT_PAREN ( null"
    assert tokens[1].to_string() == "LEFT_PAREN ( null"
    assert tokens[2].to_string() == "RIGHT_PAREN ) null"
    assert tokens[3].to_string() == "EOF  null"

def test_braces():
    scanner = Scanner("{{}}")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 5
    assert tokens[0].to_string() == "LEFT_BRACE { null"
    assert tokens[1].to_string() == "LEFT_BRACE { null"
    assert tokens[2].to_string() == "RIGHT_BRACE } null"
    assert tokens[3].to_string() == "RIGHT_BRACE } null"
    assert tokens[4].to_string() == "EOF  null"

def test_single_characters():
    scanner = Scanner("({*.,+*})")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 10
    assert tokens[0].to_string() == "LEFT_PAREN ( null"
    assert tokens[1].to_string() == "LEFT_BRACE { null"
    assert tokens[2].to_string() == "STAR * null"
    assert tokens[3].to_string() == "DOT . null"
    assert tokens[4].to_string() == "COMMA , null"
    assert tokens[5].to_string() == "PLUS + null"
    assert tokens[6].to_string() == "STAR * null"
    assert tokens[7].to_string() == "RIGHT_BRACE } null"
    assert tokens[8].to_string() == "RIGHT_PAREN ) null"
    assert tokens[9].to_string() == "EOF  null"

def test_equals():
    scanner = Scanner("={===}")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 6
    assert tokens[0].to_string() == "EQUAL = null"
    assert tokens[1].to_string() == "LEFT_BRACE { null"
    assert tokens[2].to_string() == "EQUAL_EQUAL == null"
    assert tokens[3].to_string() == "EQUAL = null"
    assert tokens[4].to_string() == "RIGHT_BRACE } null"
    assert tokens[5].to_string() == "EOF  null"

def test_bang_equals():
    scanner = Scanner("!!===")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 4
    assert tokens[0].to_string() == "BANG ! null"
    assert tokens[1].to_string() == "BANG_EQUAL != null"
    assert tokens[2].to_string() == "EQUAL_EQUAL == null"
    assert tokens[3].to_string() == "EOF  null"

def test_relational_operators():
    scanner = Scanner("<<=>>=")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 5
    assert tokens[0].to_string() == "LESS < null"
    assert tokens[1].to_string() == "LESS_EQUAL <= null"
    assert tokens[2].to_string() == "GREATER > null"
    assert tokens[3].to_string() == "GREATER_EQUAL >= null"
    assert tokens[4].to_string() == "EOF  null"

def test_comment():
    scanner = Scanner("// Comment")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].to_string() == "EOF  null"

def test_division():
    scanner = Scanner("/")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].to_string() == "SLASH / null"
    assert tokens[1].to_string() == "EOF  null"

def test_whitespace():
    scanner = Scanner("(\t\n )")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 3
    assert tokens[0].to_string() == "LEFT_PAREN ( null"
    assert tokens[1].to_string() == "RIGHT_PAREN ) null"
    assert tokens[2].to_string() == "EOF  null"

def test_string():
    scanner = Scanner("\"foo baz\"")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].to_string() == "STRING \"foo baz\" foo baz"
    assert tokens[1].to_string() == "EOF  null"

def test_numbers():
    scanner = Scanner("1234.1234")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].to_string() == "NUMBER 1234.1234 1234.1234"
    assert tokens[1].to_string() == "EOF  null"

def test_identifiers():
    scanner = Scanner("foo bar _hello")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 4
    assert tokens[0].to_string() == "IDENTIFIER foo null"
    assert tokens[1].to_string() == "IDENTIFIER bar null"
    assert tokens[2].to_string() == "IDENTIFIER _hello null"
    assert tokens[3].to_string() == "EOF  null"

def test_keywords():
    scanner = Scanner("and")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 2
    assert tokens[0].to_string() == "AND and null"
    assert tokens[1].to_string() == "EOF  null"

def test_empty_file():
    scanner = Scanner("")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].to_string() == "EOF  null"
    assert not ErrorReporter.had_error

# Place tests with errors here due to global had_error
# Ensure you set had_error to False after each test
def test_unterminated_string():
    scanner = Scanner("\"bar")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 1
    assert ErrorReporter.had_error
    assert tokens[0].to_string() == "EOF  null"
    ErrorReporter.had_error = False

def test_bad_token():
    scanner = Scanner("#")
    tokens = scanner.scan_tokens()
    assert len(tokens) == 1
    assert tokens[0].to_string() == "EOF  null"
    assert ErrorReporter.had_error
    ErrorReporter.had_error = False
