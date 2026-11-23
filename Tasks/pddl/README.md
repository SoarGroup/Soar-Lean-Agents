# PDDL tasks: classic planning domains as input to the Soar pipeline (23 November 2026)

**Status (23 November 2026, evening): ten domains converted and run in Soar; the other four (tyreworld and the three ADL domains) are refused by the converter, reasons below.** Not runnable as delivered for actions with three or more arguments: the library sends no output command for them (see "Library gap"). With an experimental output rule, 3 of the 6 domains solve their smallest problems with valid plans. Earlier status line, kept: PDDL input only. All 13 domains (14 folders: Blocksworld comes in two versions) and their 308 problems parse, and the three smallest problems of each were solved by an external planner (Fast Downward, through unified-planning), so every set used for a first conversion has a known solution.

These are the earliest and most widely taught PDDL domains: the domains of the first International Planning Competition (AIPS-1998), the AIPS-2000 Blocksworld, and the older benchmarks of the IPP domain collection that the FF domain collection documents. They are a second, formal front end to the same pipeline as `Tasks/From-English` and `Tasks/webtasks`: PDDL to WorldSpec to world-convention Soar rules. Because PDDL is already formal, there is no English to interpret and no assumption ledger is expected; the open questions are about what WorldSpec and the conventions can express.

Each folder holds `domain.pddl` (the input, as `english-input.txt` is for the From-English tasks), `problems/`, and a `README.md` giving the origin, source, PDDL features, overlap with existing tasks, and notes for conversion. Files added at conversion follow `Tasks/webtasks/classic-ai`: `<task>-spec.py`, `<Name>.lean`, `<task>-worldspec.json`, `*.world`, `<task>-rules.soar`, `<task>.soar`, `run-seed*.json`.

## The domains

Rows are in the proposed order of conversion. Round 1 is classical STRIPS; round 2 needs features WorldSpec does not yet have.

| Folder | Domain | Origin | PDDL | Problems | Smallest solved (actions) | Round |
|---|---|---|---|---|---|---|
| `movie/` | Movie | Corin Anderson, AIPS-1998 | Untyped STRIPS | 30 | 8 | 1 (smoke test) |
| `blocksworld-4ops/` | Blocksworld, robot arm | Winograd, Sussman lineage; AIPS-2000 | Untyped STRIPS | 102 | 6 | 1 |
| `hanoi/` | Towers of Hanoi | IPP collection | Untyped STRIPS | 6 (3 to 8 discs) | 7 | 1 |
| `gripper/` | Gripper | Jana Koehler, AIPS-1998 | Untyped STRIPS | 20 | 11 | 1 |
| `ferry/` | Ferry | IPP collection | Untyped STRIPS | 3 (written here) | 3 | 1 |
| `tyreworld/` | Tyreworld | Stuart Russell; Jana Koehler | Typed STRIPS, constants | 3 (written here) | 25 | 1 |
| `logistics/` | Logistics | Manuela Veloso; Selman and Kautz, AIPS-1998 | Untyped STRIPS | 35 | 27 | 1 |
| `grid/` | Grid | Drew McDermott, AIPS-1998 | Untyped STRIPS | 5 | 14 | 1 |
| `mystery/` | Mystery | Drew McDermott, AIPS-1998 | Untyped STRIPS | 30 | 5 | 1 |
| `blocksworld-3ops/` | Blocksworld, no arm | Winograd, Sussman lineage; IPP collection | STRIPS with an inequality | 3 (written here) | 3 | 2 (inequality) |
| `mprime/` | Mystery Prime | Drew McDermott, AIPS-1998 | STRIPS with an inequality | 35 | 5 | 2 (inequality) |
| `briefcaseworld/` | Briefcaseworld | Edwin Pednault; IPP collection | ADL: conditional effect, negative precondition | 3 (written here) | 4 | 2 |
| `fridge/` | Fridge | Tony Barrett; IPP collection | ADL: quantified, negative, implied preconditions | 3 (written here) | 8 | 2 |
| `assembly/` | Assembly | Drew McDermott, AIPS-1998 | ADL: quantified and conditional | 30 | 28 | 2 (last) |

## Conversion and runs (23 November 2026)

**Converter.** `tools/pddl2ws.py` translates the STRIPS subset literally into a WorldSpec description (`<task>-spec.py`), a Rosie world file and a loader: PDDL types become object categories (`object` when untyped), every predicate of arity 1 or more becomes a relation (unary type predicates included), action parameters become operator parameters, `(not (= ?x ?y))` becomes `distinct`, effects become `del` then `add`, and the goal becomes a conjunction of ground relations. Rules are then written by the path B back end (`spec_backend.py` of `SoarLean-2026-11-21b-release.zip`). Agents are in `<domain>/soar/<problem>/`.

**Propositions (no-argument predicates).** Decided by John, 23 November 2026, now World-Conventions L7-027 and L3-104 (spec: World-Conventions-Spec-v8.md): a proposition is a property of an object in the world, `(<objs> ^object <o>) (<o> ^object-handle hand ^empty true)`, never on the world identifier or the task object. A property that is tested for `true` also carries `false`, so that no rule tests for absence (compare L3-035): every proposition is initialized to `true` or `false` and maintained by operators (WorldSpec `update` effects); a negated proposition in a precondition becomes a test for `false`. The object and property for each proposition are listed per domain in `PROPOSITIONS` in `tools/pddl2ws.py`: `handempty` -> `hand ^empty`, `empty-ferry` -> `ferry ^empty`, `arm-empty` -> `arm ^empty`, movie's `movie-rewound` -> `movie ^rewound`, its three counter propositions -> `counter ^at-zero`, `^at-two-hours`, `^at-other-than-two-hours`, and its five `have-` propositions -> `viewer ^have-chips` and so on.

Two naming details found while testing: the Rosie world-file reader drops one trailing `1` from every name (a word-sense marker), so the converter writes each name with a `1` appended; and a name of one letter and digits (`d1`) reads in Soar as an identifier (it came back on the output link as `D1`), so such names get a hyphen (`d-1`).

**Translation check.** For every converted problem checked, a Fast Downward plan for the original PDDL was replayed in the WorldSpec semantics (`tools/check_translation.py`): every plan replays and reaches the goal (Hanoi 3/4/5, Blocksworld-3ops 1-3, Gripper 1, Mystery 1, Mprime 1, Logistics 1, Movie 1, Ferry 1 and 3, Blocksworld-4ops 1, Grid 1).

**Runs.** (Made on library v2.45. Main now has v2.46, whose default is chunk only; these runs set chunk never explicitly, and v2.46's new search-control rules act only on operators marked ^evaluate-first, ^evaluate-last or ^monotonic, which the PDDL agents do not set. Not rerun on v2.46.) Soar kernel 9.6.50 built from SoarGroup source (development branch of 30 Oct 2026; it has `$`), library v2.45, `chunk never` (no chunks were learned in any run), default flags, cap 60,000 decisions, seeds 1-3. Each plan was checked against the PDDL by an independent validator (unified-planning). `tools/run_pddl.py`; results in `soar/<problem>/run-seed*.json`.

| Domain, problem | Library as is | With the experimental output rule |
|---|---|---|
| Blocksworld-3ops, Sussman anomaly | success, 3 actions, valid (609 / 717 / 794 decisions) | same |
| Blocksworld-3ops, 4 blocks | no action: the plan's first action has 3 arguments | success, 3 actions, valid (283 / 366 / 288) |
| Blocksworld-3ops, 5 blocks | cap | cap |
| Hanoi, 3 discs | no action (3-argument move) | success on seeds 1 and 3 (12 and 11 moves, valid, 53,692 and 41,176 decisions); seed 2 cap after 1 move |
| Hanoi, 4 and 5 discs | no action | cap |
| Gripper, instance 1 (4 balls) | cap | cap |
| Mystery, instance 1 | no action (4 to 7 arguments) | success, 6 actions, valid (3,676 / 3,585 / 3,554); the planner's plan has 5 |
| Mprime, instance 1 | cap | cap |
| Logistics, instance 1 | cap | cap |
| Blocksworld-4ops, instances 1 and 3 | success, 6 actions (shortest), valid; 34,375 / 25,338 / 50,357 and 22,240 / 31,369 / 23,969 decisions | (no action has 3 arguments) |
| Blocksworld-4ops, instance 2 | cap after 1 action | |
| Ferry, 2 locations 1 car | success, valid, 15 / 15 / 13 actions (the shortest plan has 3; the agent wanders, L4-004 random continuation) | (no action has 3 arguments) |
| Ferry, 3 locations 2 and 3 cars | cap | |
| Movie, instance 1 | cap (seed 1 to 3); instances 2 and 3 not run | (no action has 3 arguments) |
| Grid, instance 1 | cap after 1 action (seed 1, with the experimental rule; `unlock` has 4 arguments) | |

Where the cap is reached with no action, the agent's search (look-ahead, operator-depth deepening, default flags) has not committed to a first action; these are search-strategy questions, the subject of the strategy plan, not translation errors.

## Library gap: no output command for three or more object arguments

`agent-world/external-operator-application.soar` sends `perform-action` for task operators with 0, 1 or 2 arguments; the only 3-argument rule is the Thor microwave case (argument 2 not an object). A selected task operator with 3 or more object arguments therefore gets no output command, the top state reaches an operator no-change, and the agent waits forever (found on Hanoi: `move` selected at decision 60,000, `wait` in a state no-change below it). It affects every converted domain here (Hanoi move; Blocksworld-3ops move-b-to-b; Gripper pick and drop; every Mystery, Mprime and Logistics load or unload action), and any WorldSpec task with operators of three or more parameters.

Proposed rule text, for John to apply or change (the experiment sourced rules of this form for counts 3 to 7 after the task rules; `/home/claude/build/exp-argN.soar` in the session, not added to the library):

```
sp {agent-world*apply*operator*external*argument3*all-handles
   :default
   (state <s> ^operator <operator> ^quiescence t ^internal-actions false ^io.output-link <output>)
   (<operator> ^action-handle <action-handle> ^pre-conditions-satisfied true ^argument-count 3
               ^argument1.object-handle <a1> ^argument2.object-handle <a2> ^argument3.object-handle <a3>)
-->
   (<output> ^perform-action <perform>)
   (<perform> ^name <action-handle> ^argument1 <a1> ^argument2 <a2> ^argument3 <a3>)
}
```

One such rule per count (Mystery needs up to 7), or a general mechanism; which is a library design choice. The run harness `run_agent.py` also records only `argument1` and `argument2`; `tools/run_pddl.py` records all arguments.

## Questions to settle before conversion

These are places where the conventions or WorldSpec are silent or exclude what the PDDL uses. Per `CLAUDE.md`, each is surfaced, not decided by default.

1. **Inequality**: settled. WorldSpec has `distinct x y`, so blocksworld-3ops and mprime convert.
1a. **Nullary predicates**: settled by John (see "Propositions" above); blocksworld-4ops, ferry, grid and movie now convert.
1b. **Type hierarchies** (tyreworld: `fetch ?x - obj`, where `obj` has subtypes tool, wheel and nut). WorldSpec matches an operator parameter's type exactly; subtypes are not represented. Not converted.
2. **Negative preconditions** (`(not (in ?x))` in briefcaseworld; `(not (screwed ?x))` and others in fridge). Same convention.
3. **Conditional effects over all objects** (briefcaseworld `move`). WorldSpec's `each` effect looks close but is restricted to positive conditions.
4. **Quantified and implied preconditions** (fridge, assembly). Not in WorldSpec.
5. **Types.** Typed domains declare types; untyped ones use unary predicates (`ball`, `room`, `truck`) for the same purpose. The converter keeps both literally (category from the PDDL type, unary predicates as relations); whether to fold static unary predicates into categories is open.
6. **Large instances.** Grid's five instances are large (14 to 80 actions for the first three); smaller grid problems may need to be written for first runs.

## Sources

- AIPS-1998 and AIPS-2000 problems and domains: [potassco/pddl-instances](https://github.com/potassco/pddl-instances), which keeps the original competition files with their original names (`SOURCE-README.md` in each folder). The 1998 files are also at the [CSU Planning Repository](https://www.cs.colostate.edu/meps/repository/aips98.html).
- IPP-collection domains (Blocksworld 3ops, Tyreworld, Ferry, Briefcaseworld, Fridge): [AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators), following Hoffmann's [FF domain collection](https://fai.cs.uni-saarland.de/hoffmann/ff-domains.html). The repository has generators but no instances. Running downloaded generator code was not done; the problems marked "written here" were written for this collection following each generator's documented scheme, and each was solved by the planner check.
- Hanoi: [SoarGroup/Domains-Planning-Domain-Definition-Language](https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language), SoarGroup's earlier PDDL 1.2 to Soar translator (Java, ANTLR), which also holds versions of Blocksworld, Gripper, Logistics, Mystery and others. It is prior work to compare with when conversion starts.
- One source file was changed: in `tyreworld/domain.pddl` the `(:constants ...)` line was moved before `(:predicates ...)`, as the PDDL grammar requires.
- `fridge/domain.pddl` carries a 1993-94 University of Washington notice that permits non-commercial research use only; it must stay with the file. The other sources state no licence.

## Related material in this repository

`Tasks/hps-tasks.zip` holds PDDL task sets derived for replicating Langley, Barley and Meadows (2018): blocks world, five puzzle, kinship and logistics, 52 problems.

## How the check was run

`tools/check_pddl.py` parses every domain and problem pair with the unified-planning PDDL reader and runs Fast Downward on the three smallest problems of each domain, with a 60-second limit. Results: all 308 problems parse; all 42 planner runs solved. It needs `pip install unified-planning up-fast-downward`. `tools/build_pddl.py` assembled this folder from local clones of the three source repositories and holds the hand-written problems.
