
import stypes

class Matcher:
    VERBOSE = False

    def __init__(self, name, matchf):
        self.name = name
        self.matchf = matchf
    def _return(self, val):
        if self.VERBOSE:
            result = "SUCCEEDED" if val else "FAILED"
            print "MATCH "+result+":", self.name
        return val
    def matches(self, other):
        try:
            if self.VERBOSE: print "MATCH TRYING:", self.name
            return self._return(self.matchf(other))
        except Exception:
            return self._return(False)
    def __eq__(self, other):
        return self.matches(other)
    def __and__(self, second):
        return Matcher("("+self.name+" and "+second.name+")", lambda o: self.matches(o) and second.matches(o))
    def __or__(self, second):
        return Matcher("("+self.name+" or "+second.name+")", lambda o: self.matches(o) or second.matches(o))
    def __invert__(self):
        return Matcher("(not "+self.name+")", lambda o: not self.matches(o))


has_ = lambda x: Matcher("has "+x, lambda o: x in o)
equals_ = lambda x, y: Matcher("equals "+x+" "+str(y), lambda o: o[x] == y)
matches_ = lambda x, m: Matcher("matches "+x, lambda o: m.matches(o[x]))
typed_ = lambda x, t: Matcher("typed "+x, lambda o: type(o[x]) == t)
all_ = lambda x, m: Matcher("all "+x, lambda o: all(m.matches(c) for c in o[x]))
any_ = lambda x, m: Matcher("any "+x, lambda o: any(m.matches(c) for c in o[x]))

class ASTMatchers:
    # basic matches
    ntyped = has_('ntype')
    primitive = ntyped & has_('value')
    num = primitive & equals_('ntype', stypes.Nodes.NUM) & typed_('value', int)
    mbool = primitive & equals_('ntype', stypes.Nodes.BOOL) & typed_('value', bool)
    ident = primitive & equals_('ntype', stypes.Nodes.IDENT) & typed_('value', str)
    func = ~primitive & equals_('ntype', stypes.Nodes.FUNC) & all_('args', ntyped) & matches_('func', ident)
    let = ~primitive & equals_('ntype', stypes.Nodes.LET) & all_('bindings', lambda x: ident.matches(x[0]) and ntyped.matches(x[1])) and matches_('expr', ntyped)
    define = ~primitive & equals_('ntype', stypes.Nodes.DEFINE) & all_('params', ident) & matches_('func', ident) & matches_('expr', ntyped)
    invalid_base = has_('error') & typed_('error', str) & typed_('children', list)
    invalid_ntype = invalid_base & equals_('ntype', stypes.Nodes.INVALID) 
    invalid_vtype = invalid_base & equals_('vtype', stypes.Types.INVALID)
    invalid = invalid_ntype | invalid_vtype
    void = equals_('vtype', stypes.Types.VOID)
    vtyped_basic = has_('vtype')

    # pass matchers
    astified = num | mbool | ident | func | let | define
    vtyped = astified & vtyped_basic
    interpreted = vtyped & (invalid | primitive | void)


