from .token_type import TokenType
from .expr import Literal

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        return self.primary()

    # def expression(self):
    #     return self.primary()   

    # def equality(self):
    #     expr = self.comparison()
    #     while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
    #         operator = self.previous()
    #         right = self.comparison()
    #         expr = self.expr()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        
    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
        
    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
