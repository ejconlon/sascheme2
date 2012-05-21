#!/usr/bin/env python

from pprint import pprint, pformat
from stypes import *
import matcher

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
                child, tokens, more = nest_inner(tokens)
                cur.append(child)
            elif is_close(next):
                return cur, tokens, True
            else:
                cur.append(next)
        except StopIteration:
            return cur, tokens, False
            
def nest(tokens):
    while True:
        try:
            cur, tokens, more = nest_inner(tokens)
            for c in cur:
                yield c
            if not more:
                break
        except StopIteration:
            break

def op_add(args): 
    return num_node(args[0]['value'] + args[1]['value'])
def op_sub(args): 
    return num_node(args[0]['value'] - args[1]['value'])
def op_mul(args): 
    return num_node(args[0]['value'] * args[1]['value'])
def op_div(args): 
    return num_node(args[0]['value'] / args[1]['value'])
def op_mod(args): 
    return num_node(args[0]['value'] % args[1]['value'])
def op_neg(args):    
    return num_node(-args[0]['value'])
def op_not(args):    
    return bool_node(not args[0]['value'])
def op_and(args): 
    return bool_node(args[0]['value'] and args[1]['value'])
def op_or(args):  
    return bool_node(args[0]['value'] or args[1]['value'])
def op_xor(args):  
    return bool_node(args[0]['value'] ^ args[1]['value'])
def op_gt(args):  
    return bool_node(args[0]['value'] > args[1]['value'])
def op_lt(args):  
    return bool_node(args[0]['value'] < args[1]['value'])
def op_eq(args):  
    return bool_node(args[0]['value'] == args[1]['value'])
def op_gte(args): 
    return bool_node(args[0]['value'] >= args[1]['value'])
def op_lte(args): 
    return bool_node(args[0]['value'] <= args[1]['value'])
def op_neq(args): 
    return bool_node(args[0]['value'] != args[1]['value'])
def op_idnum(args):
    return num_node(args[0]['value'])
def op_idbool(args):
    return bool_node(args[0]['value'])
def op_id(args):
    vtype = args[0]['vtype']
    if vtype == type_node(Types.BOOL):
        return bool_node(args[0]['value'])
    else:
        return num_node(args[0]['value'])
def op_nil(args):
    return list_node(None, None)
def op_cons(args):
    return list_node(args[0], args[1])
def op_sum(args):
    s = 0
    a = args[0]
    while a['current'] is not None:
        s += a['current']['value']
        a = a['next']
    return num_node(s)

def nary(op, n, intype, outtype = None):
    if outtype is None: outtype = intype
    return { 'intypes': [type_node(intype) for i in xrange(n)], 'outtype': type_node(outtype), 'op': op }

BUILTINS = {
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
    'neq' : nary(op_neq, 2, Types.NUM, Types.BOOL),
    'idnum': nary(op_idnum, 1, Types.NUM),
    'idbool': nary(op_idbool, 1, Types.BOOL),
    'id': nary(op_id, 1, Types.T(1)),
    'nil': nary(op_nil, 0, Types.T(1)),
    'cons': { 'op': op_cons, 'outtype': type_node(Types.LIST, Types.T(1)),
              'intypes': [type_node(Types.T(1)), type_node(Types.LIST, Types.T(1))] },
    'sum': { 'op': op_sum, 'outtype': type_node(Types.NUM),
             'intypes': [type_node(Types.LIST, Types.NUM)] }
}

def alias_builtin(a, b):
    BUILTINS[a] = BUILTINS[b]

alias_builtin('+', 'add')
alias_builtin('-', 'sub')
alias_builtin('*', 'mul')
alias_builtin('/', 'div')
alias_builtin('%', 'mod')
alias_builtin('!', 'not')
alias_builtin('&&', 'and')
alias_builtin('||', 'or')
alias_builtin('^', 'xor')
alias_builtin('>', 'gt')
alias_builtin('<', 'lt')
alias_builtin('==', 'eq')
alias_builtin('>=', 'gte')
alias_builtin('<=', 'lte')
alias_builtin('!=', 'neq')

def is_blah(x, blah):
    try:
        y = blah(x)
        return True
    except Exception:
        return False

def is_int(x): return is_blah(x, int)
def is_bool(x): return x == "#t" or x == "#f"
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
                #print "BINDING", binding
                assert len(binding) == 2 
                assert is_ident(binding[0])
                bindings.append((ident_node(binding[0]), astify(binding[1])))                
            return let_node(bindings, astify(nested[2]))
        elif nested[0] == 'define':
            assert len(nested) == 3
            assert len(nested[1]) > 0
            assert type(nested[1]) == list
            for x in nested[1]:
                assert is_ident(x)
            idents = [ident_node(x) for x in nested[1]]
            return define_node(idents[0], idents[1:], astify(nested[2]))
        elif nested[0] == 'if':
            assert len(nested) == 4
            return if_node(astify(nested[1]), astify(nested[2]), astify(nested[3]))
        elif type(nested[0]) != list and is_ident(nested[0]):
            return func_node(ident_node(nested[0]), [astify(arg) for arg in nested[1:]])
    else:
        if is_int(nested):
            return num_node(nested)
        elif is_bool(nested):
            return bool_node(nested)
        elif is_ident(nested):
            return ident_node(nested)
    return invalid_node(nested, 'cannot type')

def dappend(din, dout):
    for a, b in din.iteritems():
        if a not in dout:
            dout[a] = b
    return dout

class FuncStack(object):
    def __init__(self, builtins):
        self.builtins = builtins
        self.scoped = [{}]
    def push(self):
        self.scoped.append({})
    def pop(self):
        self.scoped.pop()
    def define(self, x, y):
        self.scoped[-1][x] = y
    def depth(self):
        return len(self.scoped)
    def __getitem__(self, item):
        for i in reversed(xrange(len(self.scoped))):
            if item in self.scoped[i]:
                return self.scoped[i][item]
        return self.builtins[item]
    def __contains__(self, item):
        if item in self.builtins:
            return True
        for i in xrange(len(self.scoped)):
            if item in self.scoped[i]:
                return True
        return False
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return pformat({'builtins': '...', 'scoped': self.scoped})

# return ast typed with 'vtype' (a new copy of it - use dappend)
# btypes are the types of bound symbols in lets
# funcstack may be modified with top-level defs
def vtype(ast, funcstack, btypes=None, propagated_btypes=None, propagated_template_assignment=None):
    if btypes is None: btypes = {}
    #print "BTYPES", pformat(btypes)
    if ast['ntype'] == Nodes.NUM:
        return dappend(ast, {'vtype': type_node(Types.NUM)})
    elif ast['ntype'] == Nodes.BOOL:
        return dappend(ast, {'vtype': type_node(Types.BOOL)})
    elif ast['ntype'] == Nodes.FUNC:
        if ast['func']['value'] not in funcstack:
            return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'unknown func' })
        funcdef = funcstack[ast['func']['value']]
        if len(ast['args']) != len(funcdef['intypes']):
            return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'arity mismatch' })

        # allow same-level defines in func args to allow for seq
        funcstack.push()
        args = []
        template_assignment = {}
        for arg in ast['args']:
            dvt = funcdef['intypes'][len(args)]
            if propagated_btypes != None and arg['ntype'] == Nodes.IDENT and arg['value'] not in btypes:
                arg = dappend(arg, {'vtype': dvt})
                assert arg['value'] not in propagated_btypes or propagated_btypes[arg['value']] == dvt
                propagated_btypes[arg['value']] = dvt
            else:
                is_t = Types.node_is_T(dvt)
                prop_ta = None
                if is_t:
                    et = dvt['etypes']
                    parts = [[x, x] for x in Types.split_T(et)]
                    for i in xrange(len(parts)):
                        if parts[i][0] in template_assignment:
                            parts[i][1] = template_assignment[parts[i][0]]['etypes']
                    prop_ta = type_node(Types.join_T((x[1] for x in parts)))
                arg = vtype(arg, funcstack, btypes, propagated_template_assignment=prop_ta)
                if is_t:
                    et = dvt['etypes']
                    if et not in template_assignment:
                        template_assignment[et] = arg['vtype']
                    if arg['vtype'] != template_assignment[et]:
                        return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 't type mismatch' })
                    # Check template assignment parts for contradictions
                    for k, v in template_assignment.iteritems():
                        k_parts = Types.split_T(k)
                        v_parts = Types.split_T(v['etypes'])
                        assert len(k_parts) == len(v_parts)
                        for i in xrange(len(k_parts)):
                            if Types.is_T(k_parts[i]):
                                if k_parts[i] in template_assignment and v_parts[i] != template_assignment[k_parts[i]]['etypes']:
                                    return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'sub t type mismatch' })
                elif arg['vtype'] != dvt:
                    return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'non-t type mismatch' })
            args.append(arg)
        funcstack.pop()

        if Types.node_is_T(funcdef['outtype']):
            ot = funcdef['outtype']['etypes']
            parts = [[x, x] for x in Types.split_T(ot)]
            for i in xrange(len(parts)):
                if parts[i][0] in template_assignment:
                    parts[i][1] = template_assignment[parts[i][0]]['etypes']
                elif Types.is_T(parts[i][0]):
                    # Got an unassigned template part.  Use the propagated assignment if present, otherwise error
                    if propagated_template_assignment is not None:
                        return dappend(ast, {'vtype': propagated_template_assignment, 'args': args})                        
                    else:
                        return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'unassignable template: '+parts[i][0] })
            ta = type_node(Types.join_T((x[1] for x in parts)))
            return dappend(ast, {'vtype': ta, 'args': args})                
        else:
            return dappend(ast, {'vtype': funcdef['outtype'], 'args': args})                
    elif ast['ntype'] == Nodes.IDENT:
        if ast['value'] not in btypes:
            return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'unknown identifier'})
        else:
            return dappend(ast, {'vtype': btypes[ast['value']]})
    elif ast['ntype'] == Nodes.LET:
        newbtypes = dappend(btypes, {})
        for binding in ast['bindings']:
            # do not allow effective defines in lets. create a new scope and pop it immediately
            funcstack.push()
            vtyped = vtype(binding[1], funcstack, newbtypes)
            funcstack.pop()
            newbtypes = dappend(newbtypes, {binding[0]['value']: vtyped['vtype']})
        expr = vtype(ast['expr'], funcstack, newbtypes)
        return dappend(ast, {'vtype': expr['vtype'], 'expr': expr})
    elif ast['ntype'] == Nodes.DEFINE:
        vt = Types.VOID
        if not propagated_btypes:
            propagated_btypes = {}
        typedexpr = vtype(ast['expr'], funcstack, btypes, propagated_btypes)
        intypes = []
        for param in ast['params']:
            if param['value'] in propagated_btypes:
                intypes.append(propagated_btypes[param['value']])
            else:
                intypes.append(Types.INVALID)
                vt = Types.INVALID
        outtype = typedexpr['vtype']
        op = None
        newast = dappend(ast, {'intypes': intypes, 'outtype': outtype, 'op': op, 'expr': typedexpr, 'vtype': type_node(vt)})
        funcstack.define(ast['func']['value'], newast) 
        return newast
    elif ast['ntype'] == Nodes.IF:
        typedtest  = vtype(ast['testexpr'], funcstack, btypes)
        typedtrue  = vtype(ast['trueexpr'], funcstack, btypes)
        typedfalse = vtype(ast['falseexpr'], funcstack, btypes)
        if typedtest['vtype'] != type_node(Types.BOOL):
            return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'test not boolean', 'testexpr': typedtest, 'trueexpr': typedtrue, 'falseexpr': typedfalse})
        elif typedtrue['vtype'] != typedfalse['vtype']:
            return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'test not boolean', 'testexpr': typedtest, 'trueexpr': typedtrue, 'falseexpr': typedfalse})
        else:
            return dappend(ast, {'vtype': typedtrue['vtype'], 'testexpr': typedtest, 'trueexpr': typedtrue, 'falseexpr': typedfalse})
    return dappend(ast, {'vtype': type_node(Types.INVALID), 'error': 'unknown node type'})

def interpret(ast, funcstack, bindings={}):
    #print "ASTB", ast, bindings
    if ast['ntype'] == Nodes.INVALID or ast['vtype'] == type_node(Types.INVALID):
        return ast
    elif ast['ntype'] in [Nodes.NUM, Nodes.BOOL]:
        return ast
    elif ast['ntype'] == Nodes.IDENT:
        return bindings[ast['value']]
    elif ast['ntype'] == Nodes.LET:
        newbindings = dappend(bindings, {})
        for bpair in ast['bindings']:
            newbindings[bpair[0]['value']] = bpair[1]
        return interpret(ast['expr'], funcstack, newbindings)
    elif ast['ntype'] == Nodes.FUNC:
        newargs = [interpret(arg, funcstack, bindings) for arg in ast['args']]
        funcdef = funcstack[ast['func']['value']]
        newast = funcdef['op'](newargs)
        newast['vtype'] = ast['vtype']
        return newast
    elif ast['ntype'] == Nodes.DEFINE:
        funcdef = funcstack[ast['func']['value']]
        def op(args):
            newbindings = dappend(bindings, {})
            for i in xrange(len(ast['params'])):
                pname = ast['params'][i]['value']
                arg = args[i]
                newbindings[pname] = interpret(arg, funcstack, newbindings)
            return interpret(ast['expr'], funcstack, newbindings)
        funcdef['op'] = op
        return ast
    elif ast['ntype'] == Nodes.IF:
        tested = interpret(ast['testexpr'], funcstack, bindings)
        if tested['value']:
            return interpret(ast['trueexpr'], funcstack, bindings)
        else:
            return interpret(ast['falseexpr'], funcstack, bindings)
    raise Exception("Should handle all node types")

def condexpand(ast, _):
    if ast['ntype'] != Nodes.FUNC or ast['func']['value'] != 'cond':
        return ast
    else:
        # example
        # (cond ((zero? n) (idnum 1)) (* n (fact (- n 1))))
        args = ast['args']
        assert len(args) > 1
        newast = args[-1]
        for i in reversed(xrange(len(args)-1)):
            test_expr, true_expr = args[i]['children']
            newast = if_node(astify(test_expr), astify(true_expr), newast)
        return newast

PASSES = [
    # passes on the untyped tree
    # expand cond to ifs
    ["COND", condexpand, matcher.ASTMatchers.astified],
    # type the tree
    ["VTYPE", vtype, matcher.ASTMatchers.vtyped],
    # passes on the typed tree
    # final pass
    ["INTERPRET", interpret, matcher.ASTMatchers.interpreted],
]


def execute(prog_str):
    tokens = tokenize(prog_str)
    nested = list(nest(tokens))
    funcstack = FuncStack(BUILTINS)
    for sexp in nested:
        ast = astify(sexp)
        print "INITIAL", pformat(ast)
        matched = matcher.ASTMatchers.astified.matches(ast, 0)
        print "MATCHED?", matched
        assert matched
        for p in PASSES:
            name, func, m = p
            print "STARTING", name
            ast = func(ast, funcstack)
            print "FINISHED", name, pformat(ast)
            matched = m.matches(ast, 0)
            print "MATCHED?", matched
            assert matched
        yield ast, funcstack

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
    for interpreted, funcstack in execute(program):
        pass

