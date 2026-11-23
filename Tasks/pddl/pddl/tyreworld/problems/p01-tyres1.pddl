(define (problem tyreworld-1) (:domain tyreworld)
  (:objects w1 r1 - wheel nuts1 - nut the-hub1 - hub boot - container)
  (:init (in jack boot) (in pump boot) (in wrench boot) (unlocked boot) (closed boot) (intact r1) (in r1 boot) (not-inflated r1) (on w1 the-hub1) (on-ground the-hub1) (tight nuts1 the-hub1) (fastened the-hub1))
  (:goal (and (on r1 the-hub1) (inflated r1) (tight nuts1 the-hub1) (in w1 boot) (in wrench boot) (in jack boot) (in pump boot) (closed boot))))
