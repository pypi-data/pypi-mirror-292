class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    def to_string(self):
        if self.literal is None:
            literal = "null"
        else:
            literal = self.literal
        return str(self.type.value) + " " + self.lexeme + " " + str(literal)
         