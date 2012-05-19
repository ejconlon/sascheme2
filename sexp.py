#!/usr/bin/env python

from pprint import pprint, pformat

def is_open(c): return c in '(['
def is_close(c): return c in ')]'

def tokenize(stream):
    in_comment = False
    last = []
    for c in stream:
        if in_comment:
            if c == "\n":
                in_comment = False
                if len(last) > 0:
                    yield "".join(last)
                    last = []
        elif c == ";":
            in_comment = True
        elif c == " " or c == "\t" or c == "\n":
            if len(last) > 0:
                yield "".join(last)
                last = []
        elif is_open(c) or is_close(c):
            if len(last) > 0: 
                yield "".join(last)
                last = []
            yield c
        else:
            last.append(c)
    if len(last) > 0:
        yield "".join(last)

def nest_inner(tokens):
    tokens = iter(tokens)
    cur = []
    while True:
        try:
            next = tokens.next()
            #print "TOKEN", next
            if is_open(next):
                child, tokens = nest_inner(tokens)
                cur.append(child)
            elif is_close(next):
                return cur, tokens
            else:
                cur.append(next)
        except StopIteration:
            return cur, tokens
            
def nest(tokens):
    cur, tokens = nest_inner(tokens)
    try:
        next = tokens.next()
        raise Exception("not a single sexp")
    except StopIteration:
        pass
    assert len(cur) == 1
    return cur[0]

class Nodes:
    NUM = 'NumNode'
    BOOL = 'BoolNode'
    LET = 'LetNode'
    IDENT = 'IdentNode'
    FUNC = 'FuncNode'

class Types:
    NUM = 'NumType'
    BOOL = 'BoolType'
    INVALID = 'InvalidType'

def num_node(value):
    return {'ntype': Nodes.NUM, 'value': value}
def bool_node(value):
    return {'ntype': Nodes.BOOL, 'value': value}
def func_node(func, args):
    return {'ntype': Nodes.FUNC, 'func': func, 'args': args}
def ident_node(value):
    return {'ntype': Nodes.IDENT, 'value': value}
def let_node(bindings, expr):
    return {'ntype': Nodes.LET, 'bindings': bindings, 'expr': expr}


def op_add(args): 
    return num_node(args[0].value + args[1].value)
def op_sub(args): 
    return num_node(args[0].value - args[1].value)
def op_mul(args): 
    return num_node(args[0].value * args[1].value)
def op_div(args): 
    return num_node(args[0].value / args[1].value)
def op_mod(args): 
    return num_node(args[0].value % args[1].value)
def op_neg(args):    
    return num_node(-args[0].value)
def op_not(args):    
    return bool_node(not args[0].value)
def op_and(args): 
    return bool_node(args[0].value and args[1].value)
def op_or(args):  
    return bool_node(args[0].value or args[1].value)
def op_xor(args):  
    return bool_node(args[0].value ^ args[1].value)
def op_gt(args):  
    return bool_node(args[0].value > args[1].value)
def op_lt(args):  
    return bool_node(args[0].value < args[1].value)
def op_eq(args):  
    return bool_node(args[0].value == args[1].value)
def op_gte(args): 
    return bool_node(args[0].value >= args[1].value)
def op_lte(args): 
    return bool_node(args[0].value <= args[1].value)
def op_neq(args): 
    return bool_node(args[0].value != args[1].value)

def nary(op, n, intype, outtype = None):
    if outtype is None: outtype = intype
    return { 'intypes': [intype for i in xrange(n)], 'outtype': intype, 'op': op }

FUNCDEFS = {
    'add' : nary(op_add, 2, Types.NUM),
    'sub' : nary(op_sub, 2, Types.NUM),
    'mul' : nary(op_mul, 2, Types.NUM),
    'div' : nary(op_div, 2, Types.NUM),
    'mod' : nary(op_mod, 2, Types.NUM),
    'neg' : nary(op_neg, 1, Types.NUM),
    'not' : nary(op_not, 1, Types.BOOL),
    'and' : nary(op_and, 2, Types.BOOL),
    'or'  : nary(op_or,  2, Types.BOOL),
    'xor' : nary(op_xor, 2, Types.BOOL),
    'gt'  : nary(op_gt,  2, Types.NUM, Types.BOOL),
    'lt'  : nary(op_lt,  2, Types.NUM, Types.BOOL),
    'eq'  : nary(op_eq,  2, Types.NUM, Types.BOOL),
    'gte' : nary(op_gte, 2, Types.NUM, Types.BOOL),
    'lte' : nary(op_lte, 2, Types.NUM, Types.BOOL),
    'neq' : nary(op_neq, 2, Types.NUM, Types.BOOL)
}

def is_blah(x, blah):
    try:
        y = blah(x)
        return True
    except Exception:
        return False

def is_int(x): return is_blah(x, int)
def is_bool(x): return x.lower() in ['true', 'false']
def is_ident(x):
    return len(x) > 0 and not is_int(x) and not is_bool(x)

def astify(nested):
    if type(nested) == list:
        if nested[0] == 'let':
            assert len(nested) == 3
            assert len(nested[1]) == 1
            assert type(nested[1]) == list
            bindings = []
            for binding in nested[1]:
                print "BINDING", binding
                assert len(binding) == 2 
                assert is_ident(binding[0])
                bindings.append((ident_node(binding[0]), astify(binding[1])))                
            return let_node(bindings, astify(nested[2]))
        else:
            return func_node(nested[0], [astify(arg) for arg in nested[1:]])
    else:
        if is_int(nested):
            return num_node(nested)
        elif is_bool(nested):
            return bool_node(nested)
        elif is_ident(nested):
            return ident_node(nested)
    raise Exception("Cannot type: "+pformat(nested))

def dappend(din, dout):
    for a, b in din.iteritems():
        if a not in dout:
            dout[a] = b
    return dout

def vtype_inner(ast, funcdefs, btypes={}):
    print "BTYPES", pformat(btypes)
    if ast['ntype'] == Nodes.NUM:
        return dappend(ast, {'vtype': Types.NUM}), btypes
    elif ast['ntype'] == Nodes.BOOL:
        return dappend(ast, {'vtype': Types.BOOL}), btypes
    elif ast['ntype'] == Nodes.FUNC:
        args = [vtype_inner(arg, funcdefs, btypes)[0] for arg in ast['args']]
        intypes = [arg['vtype'] for arg in args]
        if ast['func'] not in funcdefs:
            return dappend(ast, {'vtype': Types.INVALID, 'error': 'unknown func' })
        funcdef = funcdefs[ast['func']]
        if intypes != funcdef['intypes']:
            return dappend(ast, {'vtype': Types.INVALID, 'error': 'type mismatch' })
        return dappend(ast, {'vtype': funcdef['outtype'], 'args': args}), btypes
    elif ast['ntype'] == Nodes.IDENT:
        if ast['value'] not in btypes:
            return dappend(ast, {'vtype': Types.INVALID, 'error': 'unknown identifier'})
        else:
            return dappend(ast, {'vtype': btypes[ast['value']]}), btypes
    elif ast['ntype'] == Nodes.LET:
        for binding in ast['bindings']:
            vtyped, _ = vtype_inner(binding[1], funcdefs, btypes)
            btypes = dappend(btypes, {binding[0]['value']: vtyped['vtype']})
        typed_arg, _ = vtype_inner(ast['expr'], funcdefs, btypes)
        return dappend(ast, {'vtype': typed_arg['vtype']}), btypes
    return dappend(ast, {'vtype': Types.INVALID, 'error': 'unkown node type'})

def vtype(ast, funcdefs):
    ast, _ = vtype_inner(ast, funcdefs)
    return ast
        
def interpret(vtyped):
    return vtyped

def execute(prog_str):
    tokens = tokenize(prog_str)
    nested = nest(tokens)
    print "\nNESTED\n", pformat(nested)
    ast = astify(nested)
    print "\nAST\n", pformat(ast)
    vtyped = vtype(ast, FUNCDEFS)
    print "\nVTYPED\n", pformat(vtyped)
    return interpret(vtyped)

if __name__ == "__main__":
    import sys
    use_string = "USE: sexp.py (-f file | -c string)" 
    if len(sys.argv) < 3:
        print use_string
        sys.exit(-1)
    flag = sys.argv[1]
    arg = sys.argv[2]
    program = ""

    if flag == "-f":
        with open(arg, "r") as f:
            program = f.read()
    elif flag == "-c":
        program = arg
    else:
        print use_string
        sys.exit(-1)

    program = program.strip()
    interpreted = execute(program)
    print "\nINTERPRETED\n", pformat(interpreted)    
