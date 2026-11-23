(define (problem bw3-4blocks) (:domain blocksworld-3ops)
  (:objects a b c d)
  (:init (on-table a) (on b a) (on c b) (on-table d) (clear c) (clear d))
  (:goal (and (on a b) (on b c) (on c d))))
