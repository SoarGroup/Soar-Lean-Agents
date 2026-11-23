(define (problem p03-o3) (:domain briefcase)
  (:objects o1 o2 o3 - portable l0 l1 l2 l3 - location)
  (:init (is-at l3) (at o1 l0) (at o2 l1) (at o3 l2))
  (:goal (and (at o1 l2) (at o2 l3) (at o3 l1) (is-at l0))))
