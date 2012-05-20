#!/usr/bin/env python

import unittest
import sexp
import matcher
import stypes

M = matcher.ASTMatchers

class TestSexp(unittest.TestCase):

    CASES = [
        [stypes.num_node(4), M.num],
        [stypes.ident_node('foo'), M.ident],
        [stypes.bool_node(False), M.mbool],
        [stypes.func_node(stypes.ident_node('x'), [stypes.num_node(3)]), M.func],
        [stypes.let_node([(stypes.ident_node('a'), stypes.bool_node(True))], stypes.num_node(2)), M.let],
        [stypes.define_node(stypes.ident_node('y'), [stypes.ident_node('z')], stypes.num_node(4)), M.define],
        [stypes.invalid_node([1,2,3], 'erp'), M.invalid],
        [stypes.num_node(4), M.num | M.func],
        [stypes.num_node(4), M.func | M.num]
    ]

    def test_cases(self):
        for case in self.CASES:
            actual, expected = case
            self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

