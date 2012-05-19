(define (fact n)
  (cond [(zero? n) 1]
        [else (* n (fact (- n 1)))]))
