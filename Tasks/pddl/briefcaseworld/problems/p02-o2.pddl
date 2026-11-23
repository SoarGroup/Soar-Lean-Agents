(define (problem p02-o2) (:domain briefcase)
  (:objects o1 o2 - portable l0 l1 l2 - location)
  (:init (is-at l0) (at o1 l1) (at o2 l2))
  (:goal (and (at o1 l2) (at o2 l0) (is-at l1))))
