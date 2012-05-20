#!/usr/bin/env python

import unittest
import sexp
import matcher
import stypes

M = matcher.ASTMatchers

class TestSexp(unittest.TestCase):

    def typed_num(value):
        return M.num & M.vtyped_basic & matcher.equals_('value', value)

    CASES = [
        ["(+ (* 1 2) (/ 12 4))", [typed_num(5)]],
        ["(+ 1 2)(+ 3 4)", [typed_num(3), typed_num(7)]],
        ["(let ((n 8)) (add 3 n))", [typed_num(11)]],
        ["(define (double n) (mul 2 n)) (double 3)", [M.void, typed_num(6)]]
    ]

    def test_cases(self):
        for case in self.CASES:
            program, expected = case
            actual = [res for res, _ in sexp.execute(program)]
            self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
