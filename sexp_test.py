#!/usr/bin/env python

import unittest
import sexp

class Matcher:
    def __init__(self, matchf):
        self.matchf = matchf
    def __eq__(self, other):
        return self.matchf(other)

class TestSexp(unittest.TestCase):

    CASES = [
        ["(+ (* 1 2) (/ 12 4))", [sexp.num_node(5)]],
        ["(+ 1 2)(+ 3 4)", [sexp.num_node(3), sexp.num_node(7)]],
        ["(let ((n 8)) (add 3 n))", [sexp.num_node(11)]],
        ["(define (double n) (mul 2 n)) (double 3)", [Matcher(lambda o: o['vtype'] == sexp.Types.VOID), sexp.num_node(6)]]
    ]

    def test_cases(self):
        for case in self.CASES:
            program, expected = case
            actual = [res for res, _ in sexp.execute(program)]
            self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
