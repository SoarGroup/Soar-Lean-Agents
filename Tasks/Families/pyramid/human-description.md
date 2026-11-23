# Pyramid problems

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

A pyramid problem adds a run of consecutive numbers counting down from a base: the base gives the first term and the
height says how many terms to add, each one less than the last. For example, base 5 with height 3 is 5 + 4 + 3 = 12.

Goal: compute the sum.

## This instance

The agents add one term per step while the remaining height is zero or more, so height h gives h + 1 terms.
pyramid and pyramid-hierarchical: base 5, height 10, i.e. 5 + 4 + ... + (-5) = 0 (eleven terms, running below zero);
pyramid-anderson: base 5, height 2, i.e. 5 + 4 + 3 = 12. Pyramid problems were used by John Anderson's group with ACT-R models
and fMRI studies of mathematical problem solving.

## Note

The sources describe pyramid problems as a research task; the base-and-height wording above is how the agents use it.

## Sources

- [Pyramid problems research grant (NSF DRL-1007945, ACT-R)](https://grantome.com/grant/NSF/DRL-1007945)
- [Anderson et al., fMRI study of extended mental calculation (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5480097)
