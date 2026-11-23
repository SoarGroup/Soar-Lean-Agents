(define (problem fridge-f1-s4) (:domain fridge-domain)
  (:objects s1-1 s1-2 s1-3 s1-4 - screw b1 - backplane c1-old c1-new - compressor f1 - fridge)
  (:init (attached c1-old f1) (fridge-on f1) (screwed s1-1) (fits s1-1 c1-old) (fits s1-1 c1-new) (screwed s1-2) (fits s1-2 c1-old) (fits s1-2 c1-new) (screwed s1-3) (fits s1-3 c1-old) (fits s1-3 c1-new) (screwed s1-4) (fits s1-4 c1-old) (fits s1-4 c1-new))
  (:goal (and (attached c1-new f1) (fridge-on f1) (screwed s1-1) (screwed s1-2) (screwed s1-3) (screwed s1-4))))
