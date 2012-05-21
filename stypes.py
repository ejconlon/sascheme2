class Nodes:
    NUM = 'NumNode'
    BOOL = 'BoolNode'
    LET = 'LetNode'
    IDENT = 'IdentNode'
    DEFINE = 'DefineNode'
    IF = 'IfNode'
    FUNC = 'FuncNode'
    INVALID = 'InvalidNode'
    TYPE = 'TypeNode'

class Types:
    NUM = 'NumType'
    BOOL = 'BoolType'
    LIST = 'ListType'
    VOID = 'VoidType'
    INVALID = 'InvalidType'

def type_node(*etypes):
    return {'ntype': Nodes.TYPE, 'etypes': etypes }
def num_node(value):
    return {'ntype': Nodes.NUM, 'value': int(value)}
def bool_node(value):
    return {'ntype': Nodes.BOOL, 'value': value == "#t" or value == True}
def func_node(func, args):
    return {'ntype': Nodes.FUNC, 'func': func, 'args': args}
def ident_node(value):
    return {'ntype': Nodes.IDENT, 'value': value}
def let_node(bindings, expr):
    return {'ntype': Nodes.LET, 'bindings': bindings, 'expr': expr}
def invalid_node(children, error):
    return {'ntype': Nodes.INVALID, 'children': children, 'error': error}
def define_node(func, params, expr):
    return {'ntype': Nodes.DEFINE, 'func': func, 'params': params, 'expr': expr}
def if_node(testexpr, trueexpr, falseexpr):
    return {'ntype': Nodes.IF, 'testexpr': testexpr, 'trueexpr': trueexpr, 'falseexpr': falseexpr}

