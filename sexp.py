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
def is_bool(x): return is_blah(x, bool)

def astify(nested):
    pprint(nested)
    if type(nested) == list:
        return func_node(nested[0], [astify(arg) for arg in nested[1:]])
    else:
        if is_int(nested):
            return num_node(nested)
        elif is_bool(nested):
            return bool_node(nested)
    raise Exception("Cannot type: "+pformat(nested))

def dappend(din, dout):
    for a, b in din.iteritems():
        if a not in dout:
            dout[a] = b
    return dout

def vtype(ast, funcdefs):
    if ast['ntype'] == Nodes.NUM:
        return dappend(ast, {'vtype': Types.NUM})
    elif ast['ntype'] == Nodes.BOOL:
        return dappend(ast, {'vtype': Types.BOOL})
    elif ast['ntype'] == Nodes.FUNC:
        args = [vtype(arg, funcdefs) for arg in ast['args']]
        intypes = [arg['vtype'] for arg in args]
        funcdef = funcdefs[ast['func']]
        if intypes != funcdef['intypes']:
            raise Exception("Cannot match intypes "+pformat(intypes)+" against funcdef "+pformat(funcdef))
        return dappend(ast, {'vtype': funcdef['outtype'], 'args': args})
    else:
        raise Exception("Unkown node type "+pformat(ast))
    return ast
        
def interpret(vtyped):
    pprint(vtyped)
    pass

def execute(prog_str):
    tokens = tokenize(prog_str)
    nested = nest(tokens)
    ast = astify(nested)
    vtyped = vtype(ast, FUNCDEFS)
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
    ret_node = execute(program)
    print "==="
    print ret_node
