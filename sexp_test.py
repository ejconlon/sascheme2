#!/usr/bin/env python

import unittest
import sexp
import matcher
import stypes

M = matcher.ASTMatchers

class TestSexp(unittest.TestCase):

    def mnum(value):
        return M.num & M.vtyped_basic & matcher.equals_('value', value)

    def mbool(value):
        return M.mbool & M.vtyped_basic & matcher.equals_('value', value)

    CASES = [
        ["(+ (* 1 2) (/ 12 4))", [mnum(5)]],
        ["(+ 1 2)(+ 3 4)", [mnum(3), mnum(7)]],
        ["(let ((n 8)) (add 3 n))", [mnum(11)]],
        ["(define (double n) (mul 2 n)) (double 3)", [M.void, mnum(6)]],
        ["(idnum 3)", [mnum(3)]],
        ["(idbool #t)", [mbool(True)]],
        ["(idbool #f)", [mbool(False)]],
        ["(if (idbool #t) (idnum 3) (idnum 4))", [mnum(3)]],
        ["(if (idbool #f) (idnum 3) (idnum 4))", [mnum(4)]],
        ["(cond ((idbool #t) (idnum 1)) (idnum 2))", [mnum(1)]],
        ["(cond ((idbool #f) (idnum 1)) (idnum 2))", [mnum(2)]]
    ]

    def test_cases(self):
        for case in self.CASES:
            program, expected = case
            actual = [res for res, _ in sexp.execute(program)]
            self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
