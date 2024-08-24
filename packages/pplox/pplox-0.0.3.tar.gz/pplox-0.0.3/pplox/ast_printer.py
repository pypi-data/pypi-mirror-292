from .expr import Visitor

class AstPrinter(Visitor):
    def print (self, expr):
        return expr.accept(self)
    
    def visit_literal(self, expr):
        if expr.value is None:
            return 'nil'
        if isinstance(expr.value, bool):
            if expr.value:
                return 'true'
            return 'false'
        