(define (problem bw3-5blocks) (:domain blocksworld-3ops)
  (:objects a b c d e)
  (:init (on-table a) (on b a) (on-table c) (on d c) (on e d) (clear b) (clear e))
  (:goal (and (on e a) (on a c) (on c b) (on b d))))
