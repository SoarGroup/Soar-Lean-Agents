(define (problem fridge-f2-s3) (:domain fridge-domain)
  (:objects s1-1 s1-2 s1-3 s2-1 s2-2 s2-3 - screw b1 b2 - backplane c1-old c1-new c2-old c2-new - compressor f1 f2 - fridge)
  (:init (attached c1-old f1) (fridge-on f1) (screwed s1-1) (fits s1-1 c1-old) (fits s1-1 c1-new) (screwed s1-2) (fits s1-2 c1-old) (fits s1-2 c1-new) (screwed s1-3) (fits s1-3 c1-old) (fits s1-3 c1-new) (attached c2-old f2) (fridge-on f2) (screwed s2-1) (fits s2-1 c2-old) (fits s2-1 c2-new) (screwed s2-2) (fits s2-2 c2-old) (fits s2-2 c2-new) (screwed s2-3) (fits s2-3 c2-old) (fits s2-3 c2-new))
  (:goal (and (attached c1-new f1) (fridge-on f1) (screwed s1-1) (screwed s1-2) (screwed s1-3) (attached c2-new f2) (fridge-on f2) (screwed s2-1) (screwed s2-2) (screwed s2-3))))
