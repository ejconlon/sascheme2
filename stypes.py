class Nodes:
    NUM = 'NumNode'
    BOOL = 'BoolNode'
    LET = 'LetNode'
    IDENT = 'IdentNode'
    DEFINE = 'DefineNode'
    FUNC = 'FuncNode'
    INVALID = 'InvalidNode'

class Types:
    NUM = 'NumType'
    BOOL = 'BoolType'
    VOID = 'VoidType'
    INVALID = 'InvalidType'

def num_node(value):
    return {'ntype': Nodes.NUM, 'value': int(value)}
def bool_node(value):
    return {'ntype': Nodes.BOOL, 'value': bool(value)}
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
