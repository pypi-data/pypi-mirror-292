import sys

class ErrorReporter:
    had_error = False
    @classmethod
    def error(cls, line, message):
        cls.report(line, "", message)
    @classmethod
    def report(cls, line, where, message):
        print("[line " + str(line) + "] Error" + where + ": " + message, file=sys.stderr)
        cls.had_error = True
    
