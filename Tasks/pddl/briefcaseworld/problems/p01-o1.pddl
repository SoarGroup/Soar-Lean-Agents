(define (problem p01-o1) (:domain briefcase)
  (:objects o1 - portable l0 l1 - location)
  (:init (is-at l0) (at o1 l0))
  (:goal (and (at o1 l1) (is-at l0))))
