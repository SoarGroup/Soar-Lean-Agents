(define (problem p01-l2-c1) (:domain ferry)
  (:objects l0 l1 c0)
  (:init (location l0) (location l1) (car c0) (not-eq l0 l1) (not-eq l1 l0) (empty-ferry) (at-ferry l0) (at c0 l0))
  (:goal (and (at c0 l1))))
