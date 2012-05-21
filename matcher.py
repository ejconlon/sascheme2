
import stypes

class Matcher:
    VERBOSE = False

    def __init__(self, name, matchf):
        self.name = name
        self.matchf = matchf
    def _return(self, val, depth=0):
        if self.VERBOSE:
            result = "SUCCEEDED" if val else "FAILED"
            print "-"*depth+"MATCH "+result+":", self.name
        return val
    def matches(self, other, depth):
        try:
            if self.VERBOSE: print "-"*depth+"MATCH TRYING:", self.name
            return self._return(self.matchf(other, depth), depth)
        except Exception:
            return self._return(False, depth)
    def __eq__(self, other):
        return self.matches(other, 0)
    def __and__(self, second):
        return Matcher("("+self.name+" and "+second.name+")", lambda o, d: self.matches(o, d+1) and second.matches(o, d+1))
    def __or__(self, second):
        return Matcher("("+self.name+" or "+second.name+")", lambda o, d: self.matches(o, d+1) or second.matches(o, d+1))
    def __invert__(self):
        return Matcher("(not "+self.name+")", lambda o, d: not self.matches(o, d+1))


has_ = lambda x: Matcher("has "+x, lambda o, d: x in o)
equals_ = lambda x, y: Matcher("equals "+x+" "+str(y), lambda o, d: o[x] == y)
matches_ = lambda x, m: Matcher("matches "+x, lambda o, d: m.matches(o[x], d+1))
typed_ = lambda x, t: Matcher("typed "+x, lambda o, d: type(o[x]) == t)
all_ = lambda x, m: Matcher("all "+x, lambda o, d: all(m.matches(c, d+1) for c in o[x]))
any_ = lambda x, m: Matcher("any "+x, lambda o, d: any(m.matches(c, d+1) for c in o[x]))

class ASTMatchers:
    # basic matches
    ntyped = has_('ntype')
    primitive = ntyped & has_('value')
    num = primitive & equals_('ntype', stypes.Nodes.NUM) & typed_('value', int)
    mbool = primitive & equals_('ntype', stypes.Nodes.BOOL) & typed_('value', bool)
    ident = primitive & equals_('ntype', stypes.Nodes.IDENT) & typed_('value', str)
    func = ~primitive & equals_('ntype', stypes.Nodes.FUNC) & all_('args', ntyped) & matches_('func', ident)
    let = ~primitive & equals_('ntype', stypes.Nodes.LET) & all_('bindings', lambda o, d: ident.matches(o[0], d+1) and ntyped.matches(o[1], d+1)) and matches_('expr', ntyped)
    define = ~primitive & equals_('ntype', stypes.Nodes.DEFINE) & all_('params', ident) & matches_('func', ident) & matches_('expr', ntyped)
    mif = ~primitive & equals_('ntype', stypes.Nodes.IF) & matches_('testexpr', ntyped) & matches_('trueexpr', ntyped) & matches_('falseexpr', ntyped)
    mlist = ~primitive & equals_('ntype', stypes.Nodes.LIST) & has_('next') & has_('current')
    invalid_base = has_('error') & typed_('error', str)
    invalid_ntype = invalid_base & equals_('ntype', stypes.Nodes.INVALID) 
    invalid_vtype = invalid_base & equals_('vtype', stypes.type_node(stypes.Types.INVALID))
    invalid = invalid_ntype | invalid_vtype
    void = equals_('vtype', stypes.type_node(stypes.Types.VOID))
    vtyped_basic = has_('vtype') and matches_('vtype', ntyped) and matches_('vtype', Matcher('etypes', lambda o, d: len(o['etypes']) > 0))

    # pass matchers
    astified = num | mbool | ident | func | let | define | mif | mlist
    vtyped = astified & vtyped_basic
    interpreted = vtyped & (invalid | primitive | void | mlist)


