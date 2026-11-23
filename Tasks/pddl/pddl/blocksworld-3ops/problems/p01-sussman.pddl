; Sussman anomaly: C on A; A and B on the table. Goal: A on B on C.
(define (problem bw3-sussman) (:domain blocksworld-3ops)
  (:objects a b c)
  (:init (on-table a) (on-table b) (on c a) (clear c) (clear b))
  (:goal (and (on a b) (on b c))))
