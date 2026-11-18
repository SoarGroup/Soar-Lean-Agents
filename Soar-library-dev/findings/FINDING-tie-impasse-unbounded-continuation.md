# FINDING: tie-impasse look-ahead can continue without bound when every step ties (16 Nov 2026, library v2.33)

## Observed
water-jug-look-ahead (step 6 family, world variant) under `^iterative-step tie-impasse`: seed 1 did not solve within 3,000 decisions;
from decision 2,500 on, one evaluation state alternated fill and empty with no tie and no depth charge. Eight-puzzle (gen tests)
fails the same way. Generated water jug solves but returns 6 to 12 moves instead of 4.

## Mechanism (trace, seed 1)
1. In an evaluation state (S85) the next choice ties; the nested selection (S86) evaluates its three items and all come back
   `depth-exceeded`.
2. S86's `^remaining-operators` stays at 3: `decrement-remaining-operators` needs `^current-evaluation-depth` on each evaluation,
   and `selection-world*apply*selection*evaluate-operator*remaining-operators*current-evaluation-depth` requires an
   evaluate-operator operator without the current depth, which never exists. (In the top selection the depth advances through
   `increment-current-evaluation-depth*all-evals-have-values`, so this rule is dead there too.)
3. `selection-world*apply*no-more-evaluations` exists but nothing proposes it, so S86 reaches a state no-change.
4. soar-base `default*select*indifferent-and-worst*tied*OpNoChange` makes the tied operators indifferent and worst; one is picked
   at random and the look-ahead continues below the depth bound. Depth in tie-impasse mode is charged only by ties.

## Fix tried and not adopted
A rule that tags evaluations in nested selections with the current depth (so the count reaches 0) and a proposal of
`no-more-evaluations` (nested selection, `^remaining-operators 0`, a `depth-exceeded` evaluation; positive tests only).
The look-ahead then stays within the bound and iterative deepening steps properly, but:
- water-jug-look-ahead still does not solve (depth 4 after 3,000 decisions; not solved at 30,000): every nested level runs a full
  iterative deepening.
- artists-2 (tie-impasse) went from 165-282 to 2,160-4,226 decisions; operator-mode tasks changed slightly (water jug 303-374,
  blocks world 411-540, mc 469-504).
v2.30 deliberately continues after a nested tie is broken (lower-bound.soar header): the value comes from one path whose nested
choices were made on partial information. The fix removes that and costs too much where tie-impasse works well.

## Consequence
Tie-impasse is not a safe default. Tasks where every step is a real choice keep operator depth (the default); tie-impasse is set
per task where the probe shows it wins (Search-Settings-Intake-Checklist-v1.md, probe P6).

## Open
A bounded continuation: charge depth for steps taken after a nested tie was broken at a depth cut-off, or cap such continuations,
so that the v2.30 behaviour is kept where it helps and cannot run away. Not prototyped.
