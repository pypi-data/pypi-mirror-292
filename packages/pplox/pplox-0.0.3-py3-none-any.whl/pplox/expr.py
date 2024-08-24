
class Visitor:
    def visit_literal(self, expr):
        ...    

class Expr:
    def accept(self, visitor):
        ...
    
class Literal(Expr):
    def __init__(self, value, ):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal(self)
        
