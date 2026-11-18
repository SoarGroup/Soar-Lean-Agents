# World conventions for Soar programs: reference specification v7

Generated 18 November 2026, 15:03 by `gen_spec.py` from `World-Conventions-v6.xlsx` (552 rows). Do not edit by hand: change the workbook and rebuild. Rows are ordered by level, then by topic in development order, then by ID.

## Levels

| Level | Rows | Meaning |
|---|---|---|
| [L0 Definitional](#l0-definitional) | 113 | Describes what Soar is or does: definitions, syntax and architectural mechanisms. A program cannot violate it. |
| [L1 Architectural](#l1-architectural) | 24 | Tells the programmer what to do or avoid, where the architecture makes a violation fail. |
| [L2 Universal practice](#l2-universal-practice) | 14 | Adopted in essentially every Soar program. |
| [L3 Guidance](#l3-guidance) | 98 | Guidance from the Soar manual and tutorial that the library material supports. |
| [L4 Default rules](#l4-default-rules) | 6 | Conventions set by the default rules of soar-base (loaded with the shared library). |
| [L5 Selection space (classic)](#l5-selection-space-classic) | 9 | Conventions of the classic selection space that selection-world keeps. |
| [L6 Program organization](#l6-program-organization) | 9 | Library conventions for naming, files, flags and constants. |
| [L7 World state](#l7-world-state) | 16 | The world representation every agent-world program shares: ^world, objects and relations. |
| [L8 Desireds](#l8-desireds) | 25 | How goals are represented as desireds, and the library's bookkeeping for them. |
| [L9 Operators](#l9-operators) | 25 | Task, composite and non-task operators. |
| [L10 Application and output](#l10-application-and-output) | 16 | Internal and external operator application, output commands and events. |
| [L11 Learning](#l11-learning) | 6 | Chunking conventions for agent-world programs. |
| [L12 Scene and attention](#l12-scene-and-attention) | 4 | Holds when attention (attend/remove) over the scene is in use. |
| [L13 Grounding](#l13-grounding) | 14 | Holds when grounding (object-world) is in use. |
| [L14 Selection space](#l14-selection-space) | 48 | Holds when the selection-world selection space is in use. |
| [L15 Substates, search and look-ahead](#l15-substates-search-and-look-ahead) | 23 | Substates and search control in general, and look-ahead with its cost when in use. |
| [L16 Iterative deepening](#l16-iterative-deepening) | 39 | Holds when the iterative-deepening strategy is in use. |
| [L17 MEA operator subgoaling](#l17-mea-operator-subgoaling) | 4 | Holds when means-ends (MEA) operator subgoaling is in use. |
| [L18 Time and future events](#l18-time-and-future-events) | 12 | Holds when time, future events or idle waiting are in use. |
| [L19 Goal completion and memory storage](#l19-goal-completion-and-memory-storage) | 6 | Holds when goal completion or semantic-memory storage is in use. |
| [L20 Thor-Soar](#l20-thor-soar) | 41 | Applies only to Thor-Soar (the Thor-specific sheet). |

## L0 Definitional

Describes what Soar is or does: definitions, syntax and architectural mechanisms. A program cannot violate it.

### Rule syntax/naming

**L0-001** — A production never contains a literal identifier (S1, O22). Every identifier is matched by a variable; conditions are linked by shared variables.

*Rationale:* Identifiers are created at runtime and cannot be known when the rule is written.

*If violated:* Rule can never match the intended object.

*Example:*

```
(<s> ^ontop <on>) (<on> ^top-block <b>)
```

*Source:* Manual §2.2, p.15; §2.3.1.1, p.17; §3.3.5.2, p.53; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L0-002** — The first condition of every rule begins with the keyword state and matches a state. Every other condition and every action is linked to that state, directly or through other conditions.

*Rationale:* Matching is rooted in states; unlinked actions make the rule fail to load.

*If violated:* Warning and rule not stored in production memory.

*Example:*

```
sp {x (state <s> ^thing <t>) (<t> ^clear yes) --> ...}
```

*Source:* Manual §2.3.1, p.17-18; §3.3.5.1, p.52; Manual §3.3.1; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details; Tutorial Part 2, 2.2.2 Soar Version; Tutorial Part 2, 2.5.1 Syntax Errors

**L0-003** — A rule must have at least one positive condition that references a state; a rule whose conditions are all negated fails to load. The first condition as written must be that positive test of the state, for example (state <s> ...) (L0-002). After it, negated conditions may be written in any order: the reorderer places each one after the positive conditions that bind its variables.

*Rationale:* Matching starts from a positively matched state; negated conditions can only test the absence of structure relative to bound variables.

*If violated:* Rule fails to load ("no positive conditions that reference a goal state").

*Example:*

```
(state <s> ^superstate nil -^name)
```

*See:* related L0-002; L0-019

*Source:* Manual §3.3.5.6, p.57-58; Soar kernel: production_reorder.cpp (vars requiring bindings), output_errors.cpp reorder_failed_no_roots; Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator

**L0-004** — A production consists of sp {name ["doc"] [:type] conditions --> actions}; the name, conditions and actions are required, the documentation string and type optional.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
sp {task*propose*op (state <s> ...) --> (<s> ^operator <o> +)}
```

*Source:* Manual §3.3, p.49

**L0-005** — A production name must contain no whitespace and must not have the form of an identifier (one letter followed by digits). Symbolic constants must not have that form either.

*Rationale:* Whitespace ends the name; letter-digit names are confusable with identifiers.

*If violated:* Parse error, or constants printed as |G37| and confused with identifiers.

*Source:* Manual §3.1.1, p.44; §3.3.1, p.50; Tutorial Part 1, 1.2.4 Loading and Running Hello-World

**L0-006** — Everything after a # on a line is a comment, up to the end of that line. When commenting out conditions or actions, keep the parentheses balanced in the text that remains.

*Rationale:* A # comment ends at the end of its line, so a multi-line comment needs a # on each line.

*If violated:* Parse error.

*Example:* # (<ontop> ^top-block <t>)

*Source:* Manual §3.3.4, p.51

**L0-007** — Variables are written <name> with at least one non-pipe character; predicates <>, <=>, <, <=, >=, > precede a single value, and LTI predicates @, !@, @+, @- test long-term identifier links.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
(<c> ^color <> rust)
```

*Source:* Manual §3.3.5.2-3.3.5.3, p.53-54

**L0-008** — Disjunctive tests << ... >> may contain only constants (no variables or predicates) and need spaces inside the brackets; disjunctions of whole conditions are not allowed, so write separate rules instead.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
(<t> ^color << red blue >>)
```

*Source:* Manual §3.3.5.4, p.55

**L0-009** — A conjunctive test {...} must not equate two variables (e.g. { <a> <b> }); use one variable throughout instead.

*Rationale:* Illegal syntax.

*If violated:* Parse error.

*Source:* Manual §3.3.5.5, p.56

**L0-010** — A negated condition -(...) matches when no WME satisfies it under the current bindings. A negated conjunction -{...} matches when no single set of bindings satisfies all of its conditions together.

*Rationale:* Defined semantics.

*If violated:* Misread negation scope, e.g. negating only the last condition instead of the group.

*Example:* -{(<s> ^ontop <on>) (<on> ^bottom-object.type table)}

*Source:* Manual §3.3.5.6-3.3.5.7, p.56-58

**L0-011** — A negation in front of an attribute with multiple values negates their conjunction (it matches if any one is absent), not each value separately.

*Rationale:* Defined expansion to a negated conjunction.

*If violated:* Rule matches when only one of the values is absent.

*Example:*

```
(<p> -^child oprah uma)
```

*Source:* Manual §3.3.5.8, p.59

**L0-012** — A WME is identified by its timetag; a rule instantiation fires only once per set of matched timetags, so removing and recreating an identical WME lets the rule fire again.

*Rationale:* Instantiations are determined by timetags, not triples.

*If violated:* Unexpected refiring after delete/re-create.

*Source:* Manual §3.1.3, p.45

**L0-013** — Attributes that will be used in attribute-path notation must not begin with a digit (^foo.3.bar parses .3 as a float).

*Rationale:* Parser ambiguity with floating-point numbers.

*If violated:* Mis-parsed condition.

*Source:* Manual §3.3.5.11, p.65; §3.3.6.2, p.68

**L0-014** — Structured-value notation (^attr (^a v ...)) may be used in conditions only, never in actions.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:* ^ontop (^top-block <t> ^bottom-block <b>)

*Source:* Manual §3.3.5.12, p.67; §3.3.6.5, p.70

**L0-015** — A variable that appears only in a rule's actions is bound to a new, unique identifier, shared by all of its occurrences in that firing; use this to create new objects.

*Rationale:* Unbound RHS variables generate fresh identifiers.

*If violated:* Unintended creation of new objects through typos in variable names.

*Example:* --> (<s> ^operator <o> +) (<o> ^name wait)

*Source:* Manual §3.3.6.1, p.67-68

**L0-016** — Operator preferences on the RHS use the forms + ! ~ - > < = with an optional second value or number for binary forms; identifier and value are always variables, and predicates cannot be used on the RHS. = followed by a number creates a numeric-indifferent preference, (<s> ^operator <o> = 0.5); this is the form RL rules use, with a constant number (L0-100).

*Rationale:* Defined syntax; RHS creates, conditions restrict.

*If violated:* Parse error, or a predicate mistaken for a preference.

*Example:*

```
(<s> ^operator <o1> > <o2>)
(<s> ^operator <o> = 0.5)
```

*See:* related L0-100

*Source:* Manual §3.3.6.4, p.69

**L0-017** — In RHS preference lists, > < = followed by a value are read as binary; use a comma (or ^, ) or another preference) after a unary > < = to keep it unary.

*Rationale:* Defined disambiguation rule.

*If violated:* A unary best/worst/indifferent silently read as binary.

*Example:*

```
(<s> ^operator <o1> <o2> >, <o3>)
```

*Source:* Manual §3.3.6.5, p.70

**L0-018** — LTI names such as @6 may not appear in rule actions; use the LTI predicates (@, !@, @+, @-) in conditions to test LTI links.

*Rationale:* LTI labels are runtime artefacts.

*If violated:* Rule fails to load or is task-specific.

*Example:* { @ <orig> <retrieved> }

*Source:* Manual §6.2.1.2, p.145; §3.3.5.3, p.54

**L0-019** — The order of conditions does not matter to Soar except that the first must test the state; Soar reorders conditions internally for matching efficiency.

*Rationale:* The Rete matcher reorders conditions.

*If violated:* Expecting printed rules to keep source condition order.

*Source:* Manual §2.3.1, p.17

**L0-020** — Every variable used in an action must be bound in the conditions or be a new variable linked into working memory by another action in the same rule.

*Rationale:* Unlinked action variables create disconnected structure.

*If violated:* Syntax error (disconnected RHS action variable)

*Source:* Tutorial Part 2, 2.5.1 Syntax Errors

**L0-021** — Actions may call right-hand-side functions, written (name args ...); a function's value can be the value of a created WME. They are: stopping and pausing (halt, interrupt, wait); text output (write, crlf, log); mathematics (+ - * /, div, mod, abs, atan2, sqrt, sin, cos, min, max, the set- functions, int, float, ifeq); generating and manipulating symbols (capitalize-symbol, compute-heading, compute-range, concat, dc, deep-copy, @, link-stm-to-ltm, make-constant-symbol, rand-float, rand-int, round-off, round-off-heading, size, strlen, timestamp, trim); and interface calls (exec for registered user functions, cmd for Soar commands).

*Rationale:* These are the only computations a rule can perform; everything else is matching and WME creation.

*If violated:* Unknown function names fail to load; computation attempted in conditions (L1-003).

*Example:*

```
(<s> ^sum (+ <a> <b>))
(write (crlf) |Done|)
(halt)
```

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 3.3.7.6 Right-hand side Functions

### State representation

**L0-022** — The top state has ^superstate nil and ^io with ^input-link and ^output-link; it is the only state with ^superstate nil.

*Rationale:* Architecture-created.

*See:* related L0-058 (overlap)

*Source:* Manual §3.1, §3.5

**L0-023** — Working memory is a set: no two WMEs share the same identifier-attribute-value triple, but one identifier and attribute may have several values (a multi-valued attribute).

*Rationale:* The architecture prevents duplicate triples.

*If violated:* Expecting duplicate WMEs to count separately.

*Example:*

```
(<s> ^thing <b1> ^thing <b2>)
```

*Source:* Manual §2.2, p.14-15; §3.1.2, p.45

**L0-024** — Every WME must be linked directly or indirectly to a state; when a WME is removed, all structure that thereby becomes unlinked is removed automatically and recursively.

*Rationale:* Working memory is a graph rooted in the states.

*If violated:* Structures vanish when their link to a state is removed.

*Source:* Manual §2.2, p.14-15; §3.1.5, p.46-47; Manual §3.3.6.3, p.69

### Operator WM representation

**L0-025** — An operator is an identifier that is the value of ^operator on a state. Only the decision procedure creates the selected-operator WME (<s> ^operator <o>); a rule action written (<s> ^operator <o>) with no preference creates an acceptable preference.

*Rationale:* Only the decision procedure selects operators.

*If violated:* Rule cannot create (<s> ^operator <o>) directly

*Source:* Manual §2.4, §3.2; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L0-026** — A state has at most one selected operator. It may have any number of proposed (acceptable) operators.

*Rationale:* The decision procedure selects a single value for each state's operator slot.

*If violated:* Rules confuse candidates with the selected operator.

*Source:* Manual §2.1.4, p.8; §2.4.1, p.19; Manual §2.4

**L0-027** — Testing (<s> ^operator <o> +) matches a candidate operator, whereas (<s> ^operator <o>) matches only the selected operator; selection rules test the former and application rules the latter.

*Rationale:* Acceptable preferences and the selected-operator WME are distinct WMEs.

*If violated:* Comparison rules that fire only after selection, or application rules that fire on mere candidates.

*Source:* Manual §3.3.5.9, p.59-60

### Rule: state elaboration

**L0-028** — A state elaboration tests state structure only (no selected operator, no acceptable preference) and adds structure to that state. Its WMEs are i-supported: they are removed when the rule no longer matches and no other instantiation (of the same or a different rule) supports them. A rule flagged :i-support is i-supported whatever its conditions test.

*Rationale:* Definition; elaborations compute entailments of the current state.

*If violated:* If it tests ^operator it is not an elaboration

*Source:* Manual §2.3, §3.3; Manual §2.1.1, p.6; §2.1.9, p.12; §2.3.3, p.18; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 1, 1.4.4 Persistence of Working Memory Elements; Manual §2.7.4, p.31 (fn. 4)

### Rule: operator proposal

**L0-029** — An operator proposal tests a state (not its selected operator) and creates an acceptable preference (^operator <o> +) for a new operator object, and may add attributes to that object. The preference and the attributes are i-supported: they are removed when the proposal no longer matches. That an operator has a ^name is a practice (L2-006), not part of the definition.

*Rationale:* Definition of proposal.

*Example:*

```
(state <s> ^name blocks)
--> (<s> ^operator <o> +)
(<o> ^name move-block)
```

*See:* related L2-006 (name is practice)

*Source:* Manual §2.4, §3.3; Manual §2.1.5, p.9; §2.3.3, p.18; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

### Rule: operator elaboration

**L0-030** — An operator elaboration tests an operator (proposed or selected) and adds attributes to that operator object only. Its WMEs are i-supported, also when it tests the selected operator (L0-042).

*Rationale:* Definition; computes derived features of operators used by evaluation or application.

*Example:*

```
(state <s> ^operator <o> +)
(<o> ^name move ^to <t>)
(<t> ^clear yes)
--> (<o> ^target-clear yes)
```

*See:* related L1-011 (overlap); L0-042

*Source:* Manual §3.3; Tutorial Part 2, 2.3.2 Operator Application: Persistence; Tutorial Part 2, 2.8.5 Jump and Move Operator Selection

### Rule: operator evaluation/selection

**L0-031** — An operator evaluation (selection) rule tests a state and the acceptable preferences of proposed operators, and creates only preferences (=, >, <, !, ~, -, numeric) for those operators. It creates no operator and no other structure. Its preferences are i-supported. Preferences are not created by rules that test the selected operator: such a rule's preferences are o-supported and persist.

*Rationale:* Definition of selection knowledge.

*Example:*

```
(state <s> ^operator <o1> + <o2> +)
(<o1> ^name pour)
--> (<s> ^operator <o1> > <o2>)
```

*See:* related L0-029; L0-042

*Source:* Manual §2.4, §3.3.6; Manual §2.1.6, p.9; §2.3.3, p.18; Tutorial Part 1, 1.4.11 Search Control; Tutorial Part 2, 2.6.3 Move Operator Selection; Manual §3.3.6.4, p.69

**L0-032** — Of all preferences, only acceptable operator preferences appear in working memory, so they are the only preferences that conditions can test (written (<s> ^operator <o> +)).

*Rationale:* Preference memory is separate and not matchable except for acceptable operator preferences.

*If violated:* Conditions testing other preference types are invalid or never match.

*Example:*

```
(state <s> ^operator <o1> + <o2> +)
```

*Source:* Manual §2.2, p.16; §3.1.4, p.46; §3.3.5.9, p.59

**L0-033** — An operator is selectable only if it has an acceptable (+) or require (!) preference.

*Rationale:* AcceptableCollect builds candidates from acceptable preferences; require short-circuits.

*If violated:* Preferences for an unproposed operator have no effect.

*Source:* Manual §2.4, p.19; §2.4.1, p.20

**L0-034** — Preferences are not transitive: indifference or betterness between A-B and B-C implies nothing about A-C unless stated.

*Rationale:* Preference semantics evaluate only the preferences that exist.

*If violated:* Unexpected tie or conflict impasses.

*Source:* Manual §2.4.1, p.20

**L0-035** — When every remaining candidate is indifferent to every other (unary =, numeric =, or pairwise binary =), the indifferent-selection policy chooses one. If any pair of candidates is not indifferent, a tie impasse results.

*Rationale:* IndifferentFilter is the last step of preference resolution.

*If violated:* Unintended tie impasses.

*Example:*

```
(<s> ^operator <o> =)
```

*Source:* Manual §2.4.1, p.20; §2.4.2, p.24

**L0-036** — Numeric-indifferent preferences (= number) bias selection among indifferent candidates via the exploration policy; multiple numeric values for one operator are summed or averaged per numeric-indifferent-mode.

*Rationale:* Numeric values are combined before the exploration policy is applied.

*Example:*

```
(<s> ^operator <o> = 0.5)
```

*Source:* Manual §2.4.1, p.20-21

**L0-037** — Two candidates that both have best (or both worst) preferences tie unless further preferences distinguish them.

*Rationale:* BestFilter leaves all best candidates in the set.

*If violated:* Tie impasse among best operators.

*Source:* Manual §2.4.1, p.20; §2.7.1, p.28

**L0-038** — Preferences are resolved in this order: require, acceptable, prohibit, reject, better/worse, best, worst, indifferent.

*Rationale:* Fixed decision procedure; later filters see only survivors of earlier ones.

*Source:* Manual §2.4.2, p.21-24, Fig. 2.8

**L0-039** — Preference memory is not a set: several instantiations may create identical preferences, which coexist.

*Rationale:* Each preference is tied to its creating instantiation.

*Source:* Manual §3.2, p.48

**L0-040** — Only acceptable and reject preferences have meaning for non-operator attributes; all other preference types apply only to ^operator.

*Rationale:* Definition of preference semantics.

*If violated:* Preference ignored

*Source:* Consolidation review (gap); Manual §2.4

### Rule: operator application

**L0-041** — An operator application rule tests a state and that state's selected operator (^operator <o>, without +), normally by ^name, and changes that state or structure linked to it, but not the operator object (L0-042). Its changes are o-supported: they persist after the rule or the operator is removed.

*Rationale:* Definition of operator application.

*If violated:* Not an application rule (changes get i-support)

*Example:*

```
(state <s> ^operator <o>)
(<o> ^name move)
--> (<s> ^done yes)
```

*See:* related L0-042 (overlap)

*Source:* Manual §2.3, §3.3.x (o-support); Manual §2.1.8, p.11; §2.3.3, p.18-19; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version; Tutorial Part 1, 1.4.4 Persistence of Working Memory Elements; Tutorial Part 2, 2.3.2 Operator Application: Persistence

**L0-042** — A rule's actions are o-supported if and only if its RHS proposes no operator, its LHS tests the selected operator of the most recent (deepest) state the rule matches, and no action adds to that operator object; otherwise they are i-supported. A rule that tests the selected operator and adds to the operator object is an operator elaboration (L0-030): all of its actions are i-supported, including any that change the state. A :o-support or :i-support flag on the rule overrides this test. Persistent changes to a state are therefore made only by operator application rules or by rules that carry the flag.

*Rationale:* Since 9.6 the single support mode is computed per instantiation from rule structure. In Soar 9.6, o-support comes only from testing the selected operator unless the rule carries :o-support; other rules' results retract.

*If violated:* Intended persistent changes silently get i-support, or vice versa; structure disappears unexpectedly.

*Example:*

```
(state <s> ^operator <o>) --> (<s> ^count 2)
```

*See:* related L0-041 (overlap); L0-043 (overlap); L0-046 (overlap); L10-008 (overlap); L12-003 (overlap); L12-004 (overlap); L0-030; L1-011

*Source:* Manual §2.7.6, p.32-33; Manual §3.3.x (o-support)

**L0-043** — All actions of one rule instantiation receive the same support; a rule cannot give o-support to some actions and i-support to others.

*Rationale:* Support is assigned per instantiation, not per action.

*See:* related L0-042 (overlap)

*Source:* Manual §2.7.6, p.33

**L0-044** — O-supported WMEs remain until removed explicitly by a reject action in an operator application rule, or until they become unlinked or their state is removed.

*Rationale:* Persistence means the architecture never retracts them on its own.

*If violated:* Stale persistent structures accumulate unless explicitly removed.

*Example:*

```
(<s> ^ontop <old> -)
```

*Source:* Manual §2.2, p.15; §2.3.3, p.19

**L0-045** — When the preferences that selected the current operator change so that it would no longer be chosen (for example its proposal retracts), the selected-operator WME is removed at once and the application phase ends. The next operator is chosen at the next decision.

*Rationale:* Selection is continuously monitored against current preferences.

*If violated:* Application rules that expect to keep firing after the operator's proposal is falsified.

*Source:* Manual §2.5, p.25

**L0-046** — A decision cycle runs five phases in order: input, proposal, decision, application, output. Within a phase, rules fire in waves; all instantiations in one wave fire in parallel. The proposal phase fires only i-supported instantiations and retractions, wave after wave, until quiescence; o-supported matches wait for the application phase. The application phase alternates two kinds of wave and never mixes them: i-waves (i-supported instantiations plus all retractions) repeat until minor quiescence (none of these left), then one o-wave fires the o-supported instantiations (operator application rules); this repeats until neither kind is ready. With substates, each wave is at the highest goal with activity. Monitor rules (rules that test the selected operator and whose actions are only RHS functions such as write, with no WME actions) are classed with i-supported rules, so they fire in i-waves, in the first wave after the operator is selected and before any application rule, not in waves of their own.

*Rationale:* Fixed architectural cycle.

*See:* related L0-042 (overlap)

*Source:* Manual §2.5, p.24-25; Fig. 2.10, p.27; Soar kernel: rete.cpp p_node_left_addition (IE_PRODS/PE_PRODS classification), consistency.cpp active_production_type_at_goal and minor_quiescence_at_goal, run_soar.cpp apply loop

### Rule: monitoring/output

**L0-047** — A monitoring rule tests the state, the selected operator, or both, and has only printing actions (write, crlf, log). It changes no working memory.

*Rationale:* Monitoring must not affect behaviour.

*If violated:* Hidden behavioural effects

*Example:*

```
sp {blocks-world*monitor*move-block ... --> (write ...)}
```

*Source:* Tutorial Part 1; Manual §3.3.5.11, p.62

### Rule: impasse/substate handling

**L0-048** — A substate rule that tests the superstate's selected operator but writes only to the substate gets i-support, because the operator tested is not on the deepest matched state.

*Rationale:* O-support requires testing the operator of the lowest state matched.

*If violated:* Expecting persistent substate WMEs from rules that elaborate from the superoperator.

*Example:*

```
(state <s> ^superstate <ss>) (<ss> ^operator <o>)
--> (<s> ^name <n>)
```

*See:* related L0-061 (overlap)

*Source:* Manual §2.7.6, p.33

**L0-049** — A tie impasse arises when acceptable candidates are not distinguished by preferences; it is resolved by preferences that pick one (better, best, require), eliminate others (worse, worst, reject, prohibit), or make all indifferent. It can also be resolved when the substate creates an acceptable preference for a new candidate together with other preferences that make the new candidate the choice (for example best, or better than each tied candidate).

*Rationale:* Defined by the preference scheme.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34

**L0-050** — A conflict impasse arises from contradictory better/worse preferences (A>B and B>A). Among the existing candidates it can be resolved only by require, reject or prohibit preferences. It can also be resolved when the substate creates an acceptable preference for a new candidate together with other preferences that make the new candidate the choice (for example better than each conflicting candidate).

*Rationale:* Additional better/worse preferences cannot undo a cycle.

*If violated:* Trying to resolve a conflict with more better/worse preferences among the existing candidates.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34

**L0-051** — A state no-change impasse arises when a state has no selectable operator: none is proposed, or every proposed operator is rejected or prohibited. It is resolved when a rule creates an acceptable or require preference for an operator that is not rejected or prohibited, or when a reject or prohibit preference on a proposed operator retracts.

*Rationale:* Defined by the decision procedure.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.35

**L0-052** — An operator no-change impasse arises when the selected operator stays selected across a decision: no rule changed the state so that its proposal retracts, and no other operator displaced it. It is resolved by applying the operator, by changing the state so that the proposal retracts, or by preferences that select another operator.

*Rationale:* Defined by the decision procedure; substate processing is how complex operators are implemented.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.35

**L0-053** — Rules can match at every level of the goal stack, but they fire one level at a time: within each phase, each wave fires at the oldest (highest) state with activity before any newer state, so higher-level changes may remove lower states before their rules fire.

*Rationale:* Ensures lower-level activity is consistent with higher levels.

*If violated:* Substate rules that assume they fire before superstate changes.

*See:* related L0-046

*Source:* Manual §2.7.2, p.29; §2.7.8, p.36

**L0-054** — If a superstate WME that was tested (directly or via local i-supported WMEs) in creating a local o-supported substate WME changes, the substate is regenerated (removed and recreated) by the goal dependency set.

*Rationale:* GDS keeps persistent substate structures consistent with their context.

*If violated:* Unexpected substate removal and restarts.

*See:* related L0-055 (overlap)

*Source:* Manual §2.7.7, p.35-36; §2.7.9.2, p.38-40

**L0-055** — Only local o-supported WMEs add to the goal dependency set; local i-supported WMEs and o-supported results do not.

*Rationale:* GDS tracks only dependencies of persistent local structures.

*See:* related L0-054 (overlap)

*Source:* Manual §2.7.7, p.36; §2.7.9.2, p.39-40

**L0-056** — An impasse can be eliminated without being resolved: its substate is removed when a higher-level impasse is resolved, eliminated or regenerated, or when input changes working memory so that an operator can be selected. A regenerated substate (L0-054) is likewise removed and recreated. Elimination and regeneration produce no results, so nothing is learned from them; only results created before the substate was removed are learned from (L0-085).

*Rationale:* Substate processing becomes irrelevant when the situation above it changes.

*If violated:* Expecting results or learning from substate work that was abandoned.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 2.7.7 Removal of Substates: Impasse Resolution (Eliminating Impasses; Regenerating Impasses)

### Substate representation

**L0-057** — Only one impasse can exist at a given level; when a tie or conflict coexists with a constraint failure, only the constraint-failure impasse is created.

*Rationale:* Architectural precedence.

*Source:* Manual §2.7.1, p.28

**L0-058** — Each state has exactly one superstate (the top state has ^superstate nil) and at most one substate, forming a goal stack.

*Rationale:* Impasses create substates one level at a time.

*Example:*

```
(state <s> ^superstate nil)  # top state
```

*See:* related L0-022 (overlap)

*Source:* Manual §2.7.2, p.29

**L0-059** — When a substate is removed, all WMEs and preferences in it are removed. Results are not removed with it: they are WMEs of a superstate and persist according to their own support.

*Rationale:* They are no longer linked to the goal stack.

*If violated:* Relying on substate structures after the impasse resolves.

*Source:* Manual §2.7.7, p.36

**L0-060** — Only an impasse creates a substate. Each substate has ^type state, ^superstate, ^impasse (tie, conflict, constraint-failure, no-change), ^choices (multiple, constraint-failure, none), ^attribute (operator or state) and ^quiescence t. Tie, conflict and constraint-failure substates also have ^item and ^item-count; tie substates also have ^non-numeric and ^non-numeric-count. Every state has ^reward-link, ^smem and ^epmem. The kind of impasse is identified by ^impasse together with ^attribute (operator no-change: ^impasse no-change ^attribute operator; state no-change: ^impasse no-change ^attribute state).

*Rationale:* Created by the architecture to describe the impasse.

*If violated:* Rules testing non-existent impasse attributes.

*Example:*

```
(state <s> ^impasse tie ^attribute operator ^item <o>)
```

*Source:* Manual §3.4.1, p.84-86; Manual §2.7, §3.4; Tutorial Part 3, 4.9 Wait Operator; Tutorial Part 5, 1. The Water Jug Problem

### Rule: results

**L0-061** — A result's lasting support is set by its justification, not by how the substate rule created it: the result is o-supported if the justification tests the superstate and the superstate's selected operator (for example through the substate's ^name), and i-supported otherwise.

*Rationale:* The rule is an operator application in the substate whose actions are linked to the superstate.

*Example:*

```
(state <s> ^superstate <ss> ^operator <o>)
--> (<ss> ^sub-operator-name <n>)
```

*See:* related L0-048 (overlap); L0-063 (overlap)

*Source:* Manual §2.7.6, p.33

**L0-062** — A result is a WME or preference created in a substate that is linked, directly or indirectly, to a superstate (rules reach the superstate through ^superstate); a WME counts as created in the most recent (lowest) state that its rule tested.

*Rationale:* Results survive substate removal because they remain linked to a superstate.

*If violated:* Intended results lost when substate is removed, or unintended results leaking upward.

*Example:*

```
(state <s> ^superstate <ss>) ... --> (<ss> ^answer <a>)
```

*Source:* Manual §2.7.3, p.29; Tutorial Part 3, 3.2 Impasses and State Creation; Tutorial Part 3, 5.2 Remove-sound Operator

**L0-063** — A justification's conditions are the superstate WMEs tested, through the chain of substate firings, in producing the result; an i-supported result retracts when those conditions no longer match and no other support exists.

*Rationale:* Justifications are the instantiated summaries of substate reasoning.

*If violated:* i-supported results disappearing unexpectedly when tested superstate structure changes.

*See:* related L0-061 (overlap)

*Source:* Manual §2.7.4, p.31-32

**L0-064** — If substate reasoning tests no superstate knowledge, no chunk or justification is built, and the results lose all support and are removed when the substate is removed.

*Rationale:* No rule exists in the superstate to support the results.

*If violated:* Results disappear after the substate goes away.

*Example:*

```
sp {sub*mark-superstate
   (state <s> ^superstate <ss>)
-->
   (<ss> ^done true)}
(^superstate is a substate WME, so no superstate WME is tested)
```

*Source:* Manual §4.6.17, p.118

**L0-065** — A justification is built for a result whenever no chunk is learned for it: when learning is off, and also when learning is on but a chunk is not learned (for example, the reasoning tested ^quiescence t). Justifications contain only literal values and no value constraints, and are removed as soon as their conditions stop matching; they exist to determine result support.

*Rationale:* They are a limited form of chunking used for support calculation.

*Source:* Manual §4.6.1, p.108

### Semantic memory

**L0-066** — Every state receives architecture-created ^smem structures (<s> ^smem <m>) (<m> ^command <c> ^result <r>); semantic memory commands are written under ^smem.command of a state and results appear under that state's ^smem.result.

*Rationale:* Created by the architecture for each new state.

*If violated:* Commands placed elsewhere are ignored.

*Example:*

```
(state <s> ^smem.command <cmd>) --> (<cmd> ^query <q>)
```

*See:* related L0-076 (overlap)

*Source:* Manual §6.1, p.143

**L0-067** — Store a WM object in semantic memory with (<cmd> ^store <id>); only the object's direct attributes are stored, so deeper substructure needs further store commands, and success is reported as ^result.success <id>.

*Rationale:* Agent storage is not recursive.

*If violated:* Only the top level of a structure saved.

*Example:*

```
(<s> ^smem.command.store <id>)
```

*Source:* Manual §6.3.1, p.145-146; Tutorial Part 7, 3. Agent Storage and Modification

**L0-068** — Storing an identifier already linked to an LTI overwrites that LTI's attributes with the current ones; use ^store-new to always create a new LTI.

*Rationale:* Defined store semantics.

*If violated:* Loss of previously stored augmentations.

*Example:*

```
(<cmd> ^store-new <id>)
```

*Source:* Manual §6.3.1-6.3.2, p.146

**L0-069** — LTIs never appear in working memory; each retrieval creates a new short-term identifier linked to the LTI, and changes to it do not affect semantic memory until stored.

*Rationale:* Since 9.6, LTIs exist only in semantic memory.

*If violated:* Expecting WM edits to update long-term knowledge.

*Source:* Manual §6.2, p.144; §6.2.1.1, p.145

**L0-070** — Semantic memory supports only constant attributes; do not store objects whose attributes are identifiers.

*Rationale:* Representation restriction.

*If violated:* Unsupported storage.

*Source:* Manual §6.2, p.144

**L0-071** — A state issues at most one semantic-memory retrieval (^retrieve or ^query, with optional modifiers) per decision cycle; retrievals are processed in the output phase. A malformed command, or more than one retrieval, gives ^result.bad-cmd. Any number of ^store commands may be issued together. The limit is per memory: an episodic-memory retrieval can be issued on the same state in the same decision cycle.

*Rationale:* Defined command processing.

*If violated:* bad-cmd error.

*Source:* Manual §6.4, p.147-148; Tutorial Part 7, 4. Non-Cue-Based Retrieval; Tutorial Part 7, 5. Cue-Based Retrieval

**L0-072** — A non-cue-based retrieval uses ^retrieve <lti-linked-id> and yields ^result.success and ^result.retrieved; a non-LTI value yields ^result.failure.

*Rationale:* Defined command format.

*If violated:* failure result.

*Example:*

```
(<cmd> ^retrieve <id>)
```

*Source:* Manual §6.4.1, p.148

**L0-073** — A cue-based query uses ^query <cue>: constant values must match exactly, LTI-linked identifier values must match that LTI, and short-term identifier values match any value; results appear as ^result.success <cue> and ^result.retrieved <new-sti>, or ^result.failure <cue>. When several LTIs match, the one with the highest activation is retrieved; by default activation is recency (the most recently stored or retrieved).

*Rationale:* Defined query semantics.

*If violated:* Unexpected failures from over-specified cues.

*Example:*

```
(<cmd> ^query <q>) (<q> ^name <any> ^age 25)
```

*Source:* Manual §6.4.2, p.148-149; Soar manual (online, soargroup.github.io, 6 Oct 2026): 6.4.2.1 Activation

**L0-074** — A processed smem or epmem command is ignored until its command structure changes. A new retrieval is issued by changing or replacing the command WMEs, which also clears the result.

*Rationale:* Commands are processed only on change.

*If violated:* Repeated queries silently not re-executed.

*Source:* Manual §6.4, p.148; §7.3, p.157

**L0-075** — In a cue, a value that must match exactly is a constant or a long-term identifier; a value that only requires the attribute to be present is a new short-term identifier.

*Rationale:* Cue values are hard constraints, except short-term identifiers, which match any value.

*If violated:* Over- or under-constrained queries

*Example:*

```
(<cue> ^name <any-name> ^friend <lti>)
```

*Source:* Tutorial Part 7, 5. Cue-Based Retrieval

### Episodic memory

**L0-076** — Every state receives architecture-created ^epmem structures with ^command, ^result and ^present-id; episodic commands go under the state's ^epmem.command and results appear under ^epmem.result.

*Rationale:* Created by the architecture for each new state.

*If violated:* Commands placed elsewhere are ignored.

*Example:*

```
(state <s> ^epmem.command <ec>)
```

*See:* related L0-066 (overlap)

*Source:* Manual §7.1, p.155

**L0-077** — By default an episode is recorded when a new attribute is added to the output-link; set the epmem trigger to dc to record every decision.

*Rationale:* Default trigger is output.

*If violated:* Agents without output record no episodes.

*Example:* epmem --set trigger dc

*Source:* Manual §7.2, p.156

**L0-078** — An episode captures the whole top state except structure under excluded attributes; ^epmem and ^smem are excluded by default. What is stored is controlled by excluding specific attributes (epmem --set exclusions <attribute>): keep information that should be recorded episodically on the top state, and exclude attributes not worth recording. WMEs with identifier attributes are not supported.

*Rationale:* Episodic storage captures only the top state, minus excluded attributes.

*If violated:* Needed information missing from episodes; bloated episodes; undefined behaviour for identifier attributes.

*Example:* epmem --set exclusions <attribute>

*Source:* Manual §7.2.1, p.156; Tutorial Part 8, 2. Episodic Storage

**L0-079** — A cue-based episodic retrieval requires exactly one ^query cue and optionally one ^neg-query cue, with optional ^before, ^after and repeatable ^prohibit time modifiers; only one retrieval type per state per decision.

*Rationale:* Defined command format.

*If violated:* ^result.status bad-cmd.

*Example:*

```
(<ec> ^query <q>) (<q> ^io.input-link.foo <bar>)
```

*Source:* Manual §7.3, p.157; §7.3.1, p.158-159

**L0-080** — Absolute retrieval uses ^retrieve <time>; relative retrieval uses ^next or ^previous with an arbitrary identifier value.

*Rationale:* Defined command format.

*If violated:* Error result.

*Example:*

```
(<ec> ^next <n>)
```

*Source:* Manual §7.3.2-7.3.3, p.159-160

**L0-081** — Retrieved episodes are recreated under ^result.retrieved, with acceptable operator preferences renamed ^operator*; rules must test ^operator* to see past candidate operators.

*Rationale:* Avoids creating real acceptable preferences from memories.

*If violated:* Rules that never match retrieved operators.

*Example:*

```
(<r> ^operator* <o>)
```

*Source:* Manual §7.3, p.157; §7.3.4, p.160

**L0-082** — In episodic cues, short-term identifiers match any structurally consistent identifier, while LTI-linked identifiers are treated as constants matching only the same LTI.

*Rationale:* Defined cue semantics.

*If violated:* Unexpected match failures.

*Source:* Manual §7.3.1, p.159

**L0-083** — Episodic-memory commands (^query, ^retrieve, ^next, ^previous) are created under the state's ^epmem.command, at most one per state per decision; results are read under ^epmem.result.

*Rationale:* The architecture processes one command per state per decision, in the output phase by default.

*If violated:* Commands ignored or errors

*Example:*

```
(<cmd> ^query <n1>) (<n1> ^feature value ^id <n2>)
```

*Source:* Tutorial Part 8, 3. Agent Interaction; Tutorial Part 8, 4. Cue-Based Retrieval; Tutorial Part 8, 5. Temporal Progression

**L0-084** — A cue-based retrieval returns the episode that best matches the cue: the most recent episode with the greatest match score (by default the number of cue leaf elements matched, the cardinality; with graph-match on, an episode whose identifiers bind consistently is preferred). The result carries metadata such as ^match-score, ^normalized-match-score, ^match-cardinality, ^memory-id and, with graph-match, ^graph-match.

*Rationale:* Retrieval is a partial match: the best match may not contain every cue element.

*If violated:* Rules that assume a retrieved episode matches the whole cue.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 7.3.1 Cue-Based Retrievals; 7.3.4 Retrieval Metadata

### Learning: chunking

**L0-085** — A chunk or justification is built at the moment a substate rule creates a result, whether or not the result resolves the impasse (L0-065). Its conditions are the superstate-linked WMEs tested on the path to the result; its actions are the results. A substate that is removed or regenerated before it creates a result produces no chunk or justification.

*Rationale:* Chunks and justifications summarise the substate processing that produced each result.

*If violated:* Expecting chunks or justifications from substates that were removed before creating a result.

*See:* related L0-065

*Source:* Manual §2.7.7, p.34-35

**L0-086** — The dont-learn and force-learn RHS actions are development tools that work only with chunk except or chunk only respectively (dont-learn in except mode, force-learn in only mode); they control chunking for a given state.

*Rationale:* Each action only has effect under the matching chunk setting.

*If violated:* Action silently has no effect.

*Example:*

```
(dont-learn <s>)
```

*Source:* Manual §3.3.6.7, p.82

**L0-087** — Some elements of a chunk stay constants instead of becoming variables: (1) a constant that a substate rule tests in its conditions; (2) a value that one substate rule creates as a constant in its actions and a later substate rule tests; (3) a value that a substate rule creates from a variable in its actions when a later substate rule tests it against a specific constant.

*Rationale:* Explanation-based chunking variablizes an element only when the substate rules that tested or created it matched it with variables throughout; if any rule in that chain fixes it as a constant, it gets the NULL identity and the chunk keeps it as a constant.

*If violated:* Chunks are more specific than expected.

*Source:* Manual §4.3.1, p.96-97; §4.5.2.2, p.104-105

**L0-088** — Conditions that test the same superstate WME are merged into one chunk condition when that WME matches a singleton pattern: an architectural singleton (such as ^superstate), a user singleton (chunk singleton <type> <attribute> <type>), or one Soar creates automatically for string attributes (chunk automatically-create-singletons, on by default). A pattern stops applying when it is removed (chunk singleton -r), when automatic singletons are turned off (automatically-create-singletons off), or when user singletons are turned off (user-singletons off). Conditions on a WME that matches no singleton pattern each become their own chunk condition.

*Rationale:* A singleton WME can have only one value in a state, so conditions that match it are given the same identity and merge; otherwise EBC keeps the reasoning of each original condition.

*If violated:* Chunks with seemingly duplicate conditions.

*See:* related L0-089 (overlap)

*Source:* Manual §4.4.1, p.100; §4.5.2.1, p.103-104; §4.7.3.2, p.120; Soar CLI reference: chunk command (singleton, automatically-create-singletons, user-singletons)

**L0-089** — The local ^superstate WME is an architectural singleton: all conditions testing (<s> ^superstate <ss>) share one identity during chunking.

*Rationale:* A state can have only one superstate.

*See:* related L0-088 (overlap)

*Source:* Manual §4.4.1, p.100

**L0-090** — Architectural WMEs such as a tie impasse's ^item are explained by architectural instantiations: each ^item <o> is backtraced to the superstate's acceptable preference for that operator, (<ss> ^operator <o> +), so a chunk whose reasoning tests ^item has a condition on that acceptable preference.

*Rationale:* The architecture creates ^item <o> because the superstate has an acceptable preference for <o>; that preference is what the item depends on.

*Source:* Manual §4.2, p.93

**L0-091** — Negated conditions are included in a chunk only when they test the absence of WMEs on superstate-linked identifiers; negations of local substate structures are dropped.

*Rationale:* Chunking cannot describe why a local WME was not produced.

*If violated:* Over-general chunk.

*Source:* Manual §4.5.2.1, p.104; §4.6.10, p.112

**L0-092** — Constraints (e.g. <> <x>, >= 0) that a condition on local substate structure places on a value that came from the superstate are carried into the chunk as tests on that superstate value.

*Rationale:* Constraint tracking prevents over-generality.

*Example:*

```
Rule 1: (state <s> ^superstate <ss>) (<ss> ^count <c>) --> (<s> ^copy <c>)
Rule 2: (state <s> ^copy {<c> > 0} ^superstate <ss>) --> (<ss> ^positive true)
Chunk condition: (<ss> ^count {<c> > 0})
```

*Source:* Manual §4.5.2.3, p.105; §4.5.3.2, p.106

**L0-093** — Intermediate RHS functions (math etc.) used in substate reasoning cause their argument identities and any tests of their outputs to be literalized in the chunk; only a RHS function in the result-creating rule is generalised.

*Rationale:* Constraints on intermediate RHS outputs cannot be expressed in a single rule's conditions.

*If violated:* Over-specialised chunks.

*Example:*

```
(<s> ^sum (+ <x> <y>))
```

*Source:* Manual §4.6.16, p.116

**L0-094** — No chunk is learned when any of these holds: chunking is off for the state; the chunk duplicates an existing rule; a correctness filter rejects it; bottom-only is on and a lower chunk exists; the reasoning tested ^quiescence t; the reasoning tested the absence of local substate structure (a negated condition on a substate WME) and chunk allow-local-negations is off; no superstate WME was tested.

*Rationale:* Enumerated architectural conditions.

*If violated:* Expected chunk missing.

*See:* related L0-091; L3-062

*Source:* Manual §4.6.17, p.117-118

**L0-095** — A newly learned chunk is inhibited from firing on the exact WMEs that created it, but it may fire immediately on other matching WMEs.

*Rationale:* Prevents duplication of the original result.

*Source:* Manual §4.6.2, p.108-109

**L0-096** — With multi-level substates a single result can yield bottom-up chunks at each level until a chunk creates WMEs only in the state it matches; bottom-only restricts learning to the lowest level.

*Rationale:* Chunks in higher spaces are learned from implicit matches of lower chunks.

*Example:* chunk bottom-only on

*Source:* Manual §4.6.3, p.109; §4.6.17, p.117

**L0-097** — chunk add-osk is off by default. When it is on, the operator selection knowledge relevant to choosing the substate operators that led to a result (the preferences that selected them) is backtraced, and its conditions are added to the chunk.

*Rationale:* Without it, a chunk can leave out conditions that the substate's choice of operators depended on.

*If violated:* Over-general chunks when the substate's operator choices mattered.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.4.1 Operator Selection Knowledge Analysis; 4.6.8 Missing Operator Selection Knowledge

**L0-098** — A previous result is a WME created locally in a substate that later became a result. When substate rules then test or add to it through a path from the local substate, the chunk has unconnected conditions; chunking repairs it by adding grounding conditions along the shortest path it finds in working memory, which can make the chunk over-specialized. chunk stats reports repaired rules (L3-063).

*Rationale:* The explanation does not say where in the superstate the previous result lies.

*If violated:* Chunks that match only when the previous result is found on the same path.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.5.3.6 Rule Validation and Repair; 4.6.7 Previous Results and Rule Repair

**L0-099** — When several substate rule instantiations that test different superstate structures create the same substate WME, the WME exists once and a result that tests it is created once; but the chunk learned from that result matches once for each of those superstate structures and creates a separate result for each (disjunctive context conflation), so it does not reproduce the substate's behaviour.

*Rationale:* A chunk cannot express a disjunction of the superstate conditions that each produced the collapsed WME.

*If violated:* Chunks that create several results where the substate created one.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.6.12 Disjunctive Context Conflation

### Learning: RL

**L0-100** — A rule is an RL rule if and only if its LHS tests a proposed operator (^operator <o> +), it is not a :template rule, and its RHS has exactly one action: a numeric-indifferent preference with a constant value for that operator, (<s> ^operator <o> = <number>). Any other action (another preference, an RHS function, a variable value) makes the rule a non-RL rule; put such actions in separate rules.

*Rationale:* RL rules are identified purely by syntax; the format permits exactly one constant numeric-indifferent action.

*If violated:* Intended RL rule silently not updated by RL.

*Example:*

```
sp {rl*3*12*left (state <s> ^x 3 ^operator <o> +) (<o> ^name move)
--> (<s> ^operator <o> = 1.5)}
```

*Source:* Manual §5.1, p.131-132; Tutorial Part 6, 2.1 RL Rules

**L0-101** — Reward is given via the state's architecture-created ^reward-link as (<rl> ^reward <r>) (<r> ^value number); structures not matching this pattern are ignored, and multiple valid rewards are summed.

*Rationale:* Defined reward representation; the intermediate identifier allows equal-valued rewards and annotations.

*If violated:* Reward never seen by RL.

*Example:*

```
(<rl> ^reward <r>) (<r> ^value 1.0 ^source env)
```

*Source:* Manual §5.2, p.133-134

**L0-102** — Every state (including substates) has its own reward-link; rewards for an operator are read only from the reward-link of the state where it was selected.

*Rationale:* RL treats each state independently.

*If violated:* Rewards placed on the wrong state's link.

*Source:* Manual §5.2, p.133; §5.3.2, p.137

**L0-103** — RL updates occur when an RL operator is selected, using the reward collected and the next RL operator's Q-value (Sarsa) or the maximum over proposed RL operators (Q-learning), per rl learning-policy.

*Rationale:* Defined temporal-difference update.

*Example:* rl --set learning-policy q-learning

*Source:* Manual §5.3, p.134-135

**L0-104** — Decisions in which no RL operator is selected (e.g. maintenance operators such as cleaning output-link) form gaps that are bridged by temporal-extension; disabling it updates pre-gap rules with zero future value.

*Rationale:* Defined gap-propagation behaviour.

*If violated:* Value of operators before maintenance steps under-estimated if temporal-extension is off.

*Example:* rl --set temporal-extension off

*Source:* Manual §5.3.1, p.136

**L0-105** — An RL operator that leads to an operator no-change impasse remains selected while its substate works; its update discounts superstate rewards over that period only when hrl-discount is on (default off).

*Rationale:* Defined hierarchical RL behaviour.

*Source:* Manual §5.3.2, p.137; Manual rl parameter table (hrl-discount default off)

**L0-106** — A rule template is marked :template and otherwise follows the RL rule format, except that its numeric value may be a variable; it generates rules named rl*<template>*<n> for each novel combination of matched constants.

*Rationale:* Defined template mechanism.

*If violated:* Template not recognised.

*Example:*

```
sp {t :template (state <s> ^operator <o> + ^value <v>) --> (<s> ^operator <o> = <v>)}
```

*Source:* Manual §5.4.2, p.140-141

**L0-107** — The default indifferent-selection policy is softmax. epsilon-greedy and boltzmann are the policies designed for RL; one of them is set when RL is enabled (L3-088).

*Rationale:* The default is kept for backward compatibility, not for RL.

*If violated:* RL exploration that does not follow the intended policy.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 5.3.3.1 Exploration

**L0-108** — Eligibility traces are off by default (rl eligibility-trace-decay-rate 0). With a positive decay rate, Sarsa becomes Sarsa(lambda) and Q-learning becomes Watkins Q(lambda); eligibility-trace-tolerance is the smallest trace value not treated as 0.

*Rationale:* Traces update RL rules across several sequential steps, speeding credit assignment.

*If violated:* Expecting multi-step credit assignment without enabling traces.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 5.3.3 Eligibility Traces

### Input/output link

**L0-109** — Input functions add and remove WMEs at the start of each decision cycle, and output functions process the output-link commands at the end of each cycle. The environment may apply the action then or together with the next input (as in a gym step).

*Rationale:* I/O is synchronised with the decision cycle.

*If violated:* Expecting environment feedback within the same cycle the command was issued.

*Source:* Manual §2.6, p.26; §2.5, p.25

**L0-110** — Input and output through the I/O system is represented as substructure of the top state's ^io attribute: ^io.input-link for perception and ^io.output-link for motor commands, both created by the architecture. Input can also come through SVS (the spatial visual system), whose scene graph the environment updates and the agent reaches through the state's ^svs structure.

*Rationale:* Apart from SVS, I/O occurs only through the top state's io attribute.

*If violated:* Commands placed elsewhere are never seen by output functions.

*Example:*

```
(state <s> ^io.output-link <out>)
```

*Source:* Manual §3.5.1-3.5.2, p.87-89

**L0-111** — A WME on the input-link stays until the input function removes it and supports matching rules meanwhile; a rule does not refire on unchanged input, only when the input is removed and re-added.

*Rationale:* Instantiations are tied to WME timetags.

*If violated:* Expecting repeated firing on persistent input.

*Source:* Manual §3.5.2, p.89-90

**L0-112** — Rules that interpret input test attributes and values under ^io.input-link; rules that produce output create structure under ^io.output-link.

*Rationale:* I/O rule roles as defined.

*Example:*

```
sp {blocks-world*elaborate*input (state <s> ^io.input-link <in>) ...}
```

*Source:* Manual §3.5.3, p.90

### Settings/commands

**L0-113** — Chunking is off by default. It is enabled with chunk always, or selectively with chunk only (plus force-learn) or chunk except (plus dont-learn).

*Rationale:* Default chunk setting is never.

*If violated:* Expecting chunks with learning disabled.

*Example:* chunk always

*Source:* Manual §4.1, p.91; §4.7.2, p.119

## L1 Architectural

Tells the programmer what to do or avoid, where the architecture makes a violation fail.

### Rule syntax/naming

**L1-001** — Different variables may bind to the same symbol; when two conditions must bind distinct objects or values (e.g. two jugs, two values of a multi-valued attribute), add an explicit test that excludes equality: not-equal (<j2> <> <j1>), or > or < ({<j2> > <j1>}). > and < work on numbers, strings and identifiers and give a canonical ordering, so the rule matches each pair only once instead of in both orders.

*Rationale:* Variable bindings are not unique unless forced.

*If violated:* Rule matches the same object twice.

*Example:*

```
(<p> ^child <c1> {<> <c1> <c2>})
```

*Source:* Manual §3.3.5.2, p.53; §3.3.5.8, p.59; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L1-002** — In rule conditions, attribute-path notation (^a.b.c) introduces a new variable for each step. Two paths through a multi-valued attribute therefore need not bind the same intermediate object; where the same object is meant, bind it with an explicit variable.

*Rationale:* In conditions, each dotted path expands into its own conditions with new variables.

*If violated:* Conditions match different ontop relations than intended.

*Example:* ^ontop.top-block <b1> ^ontop.bottom-block <b2> # two different ontops

*Source:* Manual §3.3.5.11, p.62-64

**L1-003** — Conditions contain no arithmetic. A derived value is computed in the action of an elaboration, and conditions test the elaborated attribute.

*Rationale:* Soar allows math functions only in actions.

*If violated:* Rule cannot be written / syntax error

*Example:*

```
(<j> ^empty (- <v> <c>))
```

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 1, 1.4.5 Water Jug State Elaboration

**L1-004** — An attribute or constant written unquoted as a letter followed by digits (d1, c11) is read as the upper-case symbol (D1, C11). Where it must match smem, epmem or input content stored in lower case, write it between vertical bars: ^|d1|, |c11|. Check every such attribute in conditions, in actions and in the text of smem --add commands.

*Rationale:* Soar upper-cases an unquoted symbol that is a letter followed by digits, so ^d1 never equals the string |d1| stored in smem. Nothing is reported.

*If violated:* Silent mismatch: the smem or epmem query returns nothing or fails and the rule never fires (^d1 against facts stored as |d1|).

*Example:*

```
(<s> ^|d1| <d1>)   # matches the attribute stored as |d1|
(<s> ^d1 <d1>)    # reads ^D1
```

*See:* related L0-008

*Source:* Found 17 Nov 2026 in arithmetic-smem world-v6 (Tasks/Families README-v6.md)

### State representation

**L1-005** — An object is defined by its attributes and values, not by its identifier; programs must not depend on particular identifier names, which differ between runs.

*Rationale:* Identifiers are runtime-generated labels.

*If violated:* Behaviour that depends on identifier spelling is not reproducible.

*Source:* Manual §2.2, p.15; §3.1.1, p.44

**L1-006** — Rules must not create, remove or change the state attributes the architecture creates (^type, ^superstate, ^impasse, ^attribute, ^choices, ^item, ^item-count, ^quiescence, ^io, ^reward-link, ^smem, ^epmem) or the selected-operator WME.

*Rationale:* These WMEs are owned by the decision procedure.

*If violated:* Rule is rejected or architecture state is corrupted.

*Source:* Manual §2.2, p.16; §3.4, p.84

### Operator WM representation

**L1-007** — An operator proposal must not test the acceptable preference of the operator it proposes.

*Rationale:* A proposal that tests its own preference never fires.

*If violated:* Operator never proposed

*Source:* Manual §2.4

### Rule: state elaboration

**L1-008** — Elaboration, proposal and comparison rules must reach quiescence before the decision phase: no cycle of rules that keeps adding and retracting (e.g. a rule that tests the absence of what it creates).

*Rationale:* Elaboration runs to quiescence before each decision.

*If violated:* max-elaborations reached; oscillation

*Source:* Manual §2.5, p.24-25

**L1-009** — Within one elaboration cycle all matched rules fire and all unmatched instantiations retract in parallel. A rule's correctness must not depend on the order of firing.

*Rationale:* Soar has no conflict resolution among matched rules; order is functionally parallel.

*If violated:* Order-dependent behaviour that differs between runs or versions.

*Source:* Manual §2.3.3, p.19; §2.5, p.25

**L1-010** — An i-supported rule must not test the absence of the WME it creates: the rule would fire and retract without end.

*Rationale:* The action falsifies the rule's own condition, which retracts the action, which re-enables the rule.

*If violated:* Infinite fire/retract loop; no quiescence.

*Example:*

```
(state <s> ^car <c> -^road)
--> (<s> ^road route-66)  # loops
```

*Source:* Manual §3.3.5.6, p.57; Manual §2.5

### Rule: operator elaboration

**L1-011** — Operator attributes are i-supported. A rule that tests the selected operator does not add both operator attributes and state attributes: every action of such a rule is i-supported (L0-042), so the state change would not persist. Exception: a rule flagged :o-support may add a persistent bookkeeping link to an operator (for example ^evaluation on evaluate-operator, L14-020).

*Rationale:* Operator augmentations define the operator and must track it; mixing them with state changes defeats o-support, and o-supported operator elaborations would add GDS dependencies.

*If violated:* State change unexpectedly i-supported; runtime warning.

*Example:*

```
(<o> ^new aug) (<s> ^new aug)  # bad: same rule
```

*See:* related L0-030 (overlap); L14-020 (overlap)

*Source:* Manual §2.7.6, p.33-34; §2.7.9.2, p.40

### Rule: operator application

**L1-012** — A reject action (^attr value -) that is meant to remove a WME permanently must be in an o-supported rule; with i-support the WME returns when the rejecting instantiation retracts.

*Rationale:* Removal under i-support is not persistent.

*If violated:* Removed WME reappears.

*Example:*

```
(state <s> ^operator <o>) ... --> (<s> ^block <b> -)
```

*See:* related L8-021 (overlap)

*Source:* Manual §3.3.6.3, p.68-69; Tutorial Part 2, 2.3.2 Operator Application: Persistence

**L1-013** — Operator preferences are created only by rules whose actions are i-supported (proposal and evaluation rules), never by operator application rules. Preferences are never removed by rules: they retract when the rule that created them no longer matches.

*Rationale:* A rule that creates an operator preference while testing the selected operator gets i-support for all its actions (L0-042), so a state change in the same rule does not persist; preferences are meant to track the current situation.

*If violated:* State changes made in the same rule disappear; preferences that do not track the situation.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 3.3.7.4 The syntax of preferences

### Rule: impasse/substate handling

**L1-014** — The ^item set of a tie or conflict substate can change during the impasse without ending it. Substate rules must not assume that the set of candidates is fixed.

*Rationale:* The architecture adds and removes ^item WMEs in place.

*If violated:* Stale evaluations of candidates that have left the tie.

*Source:* Manual §3.4.1, p.85

**L1-015** — At most one operator has a require (!) preference at a time, and no operator has both require and prohibit. Otherwise a constraint-failure impasse results, which no further preference resolves; one of the conflicting preferences must retract.

*Rationale:* Require and prohibit are hard constraints.

*If violated:* Unresolvable impasse.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34; Manual §2.4.1, p.21; §2.7.1, p.28

### Semantic memory

**L1-016** — Rules must not remove attributes of the ^smem.result (or ^epmem.result) structure; the memory system maintains them.

*Rationale:* The memory module adds and clears result WMEs itself.

*If violated:* Inconsistent result structure.

*Source:* Manual §6.1, p.143; §7.1, p.155

**L1-017** — Semantic-memory commands are created under the state's ^smem.command by operator application rules, and exactly one smem command is on the command link at a time. The agent removes the previous command before it issues the next (for example ^retrieve replaced by ^query).

*Rationale:* smem reads the command link and does not clear it; an operator application rule (o-support) keeps the command in place until the agent removes it, so the agent is responsible for maintaining the command link.

*If violated:* smem finds more than one command and returns an error status instead of running the new command.

*Example:*

```
(<cmd> ^retrieve <lti> - ^query <cue>)
```

*Source:* Tutorial Part 7, 3. Agent Storage and Modification; Tutorial Part 7, 5. Cue-Based Retrieval

### Learning: RL

**L1-018** — A reward WME exists for exactly the decision cycles it applies to: make reward rules i-supported, or remove the reward after it is collected. Soar never clears the reward-link, and a reward that persists is counted again in every cycle.

*Rationale:* Reward collection scans the link every decision phase without bookkeeping.

*If violated:* Reward counted multiple times.

*Example:*

```
sp {elaborate*reward (state <s> ^name left-right ^reward-link <r> ...) --> (<r> ^reward.value <d-reward>)}
```

*See:* related L0-101

*Source:* Manual §5.2, p.134; Tutorial Part 6, 2.2 Reward Rules

### Input/output link

**L1-019** — Rules must reach the io, input-link and output-link objects through variables bound by ^io.input-link and ^io.output-link; their identifiers are assigned at run time.

*Rationale:* Identifiers differ across runs.

*Example:*

```
(state <s> ^io.input-link <in>)
```

*Source:* Manual §3.5.2, p.87; Tutorial Part 2, 2.3.3 Running and Tracing

**L1-020** — Rules never create, remove or change structure under ^io.input-link; the environment owns it.

*Rationale:* Input changes are made by the I/O system each input phase.

*If violated:* Input overwritten or inconsistent

*Source:* Manual §3.5

**L1-021** — A rule that copies an input-link object onto the state uses a new variable for the copy on the RHS, so that a new identifier is created. Reusing the input-link variable links the state to the input structure and copies nothing: when the environment changes or removes that structure on the input-link, what the state reaches through the link changes or is removed with it.

*Rationale:* Unbound RHS variables create new objects; bound ones create links.

*If violated:* State structure aliases input that the environment may remove.

*Example:*

```
(<in> ^block <ib>) --> (<s> ^block <b>) (<b> ^x <x>)
```

*Source:* Manual §3.5.3, p.90

**L1-022** — Every external action is issued as a command structure under ^io.output-link. The attribute used for the command is set by the environment interface: the tutorial environments use the command name itself (^move.direction north), many systems use ^command, and Thor-Soar (agent-world) uses ^perform-action with ^name <action-handle> and ^argument1, ^argument2, on which the environment reports ^status success, error or failure.

*Rationale:* The output-link is the only channel for motor commands.

*If violated:* Environment never sees the action

*Example:*

```
(state <s> ^io.output-link <out>) --> (<out> ^move.direction north)
(<out> ^perform-action <p>) (<p> ^name <action-handle> ^argument1 <handle>)   # Thor-Soar
```

*Source:* Tutorial Part 2, 2.2.1 English Version; Tutorial Part 2, 2.2.2 Soar Version; agent-world/external-operator-application.soar; thor-soar/external-operator-application.soar

### Settings/commands

**L1-023** — Semantic memory is enabled (smem --enable) before an agent uses it.

*Rationale:* Memory mechanisms are disabled by default.

*If violated:* Commands silently not processed

*Example:* smem --enable

*Source:* Tutorial Part 7, 2. Agent Interaction

**L1-024** — Episodic memory is enabled (epmem --set learning on) and its storage trigger chosen (output, the default, or dc for every decision) before an agent depends on it.

*Rationale:* Episodic memory is disabled by default; the trigger determines which moments are recorded.

*If violated:* No episodes recorded

*Example:*

```
epmem --set learning on
epmem --set trigger dc
```

*Source:* Tutorial Part 8, 2. Episodic Storage

## L2 Universal practice

Adopted in essentially every Soar program.

### Project/file organization

**L2-001** — Files follow the operator hierarchy (the VisualSoar layout): one file per operator, named after it, holding its proposal and application rules; general rules under elaborations/; operators usable in any substate under all/; a substate that implements an operator is a folder with the operator's name that holds its suboperators.

*Rationale:* VisualSoar organization; the layout mirrors the problem-space hierarchy.

*Source:* VisualSoar templates; Tutorial Part 3, 3. Wander Operator - Subgoals; Tutorial Part 3, 3.4 General Rule Summary; Tutorial Part 3, 4.9 Wait Operator; Tutorial Part 3, 5. Improving Sound Detection

**L2-002** — A project uses one copy of the shared library, loaded from its shared folder (Soar/soar-library); it does not keep edited local copies.

*Rationale:* The corpus has at least five versions (default-1-24-17, default-2019, default-2019-x, default with Impasse__ folders, plus astar/iterative-deepening/epmem/RL variants), and local copies with changed rules.

*If violated:* Silent behavioural differences between agents

*Source:* Corpus survey (6 Nov 2026)

### Rule syntax/naming

**L2-003** — A rule name has asterisk-separated fields: <task-or-state>*<function>*<operator-or-feature>[*detail]. The function is one of propose, apply, elaborate, compare (or select), monitor, detect, evaluate. Library rules follow L6-006.

*Rationale:* Readable traces; VisualSoar and tools rely on it; a checker can compare the declared type with the classified type.

*Example:* water-jug*apply*pour*case1

*Source:* Tutorial Part 1; Manual §3.3.1, p.50; Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator; Tutorial Part 1, 1.4.9 State and Operator Monitoring; Tutorial Part 1, 1.4.10 Desired State Recognition; Tutorial Part 1, 1.4.11 Search Control

**L2-004** — The state variable is <s> and the operator variable is <o> (or <op>); other variable names say what they bind.

*Rationale:* Uniform variable names make rules quicker to read.

*If violated:* Reduced readability only

*Example:*

```
(state <s> ^operator <o>)
```

*Source:* Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details

### State representation

**L2-005** — Every state that rules reason about has ^name. The top state gets the task name from its initialization operator; a substate gets the name of the superstate's selected operator from the default elaboration (L4-008) or from a rule specific to that substate.

*Rationale:* Every rule then tests (state <s> ^name X), which scopes it to one problem space.

*If violated:* Rules fire in unintended states

*Example:*

```
(<s> ^name water-jug)
```

*Source:* Tutorial Part 1, Part 3; Tutorial Part 1, 1.4.2 State Representation; Tutorial Part 3, 2. Simple Wandering Tank

### Operator WM representation

**L2-006** — Every operator has exactly one ^name, set by its proposal rule; every proposal, evaluation and application rule for the operator tests that name.

*Rationale:* Universal; default rules (substate naming, selection space) depend on it.

*If violated:* Default rules do not work

*Example:*

```
(<o> ^name pour)
```

*See:* related L0-029 (name is practice)

*Source:* Tutorial Part 1; default soar-base*elaborate*state*name; Tutorial Part 1, 1.3 Building a Simple Hello-World Agent Using an Operator; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L2-007** — Operator parameters are attributes of the operator object, created by the proposal rule; their values are the objects or constants the operator acts on. Parameters are not encoded in the operator's name.

*Rationale:* Applications and evaluations bind the objects through the operator.

*Example:*

```
(<o> ^name pour ^from <j1> ^to <j2>)
```

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

### Rule: operator proposal

**L2-008** — Every proposed operator needs an acceptable preference, including when the same rule also creates other preferences for it (indifferent, best).

*Rationale:* Operators without an acceptable preference are never selected.

*If violated:* Operator never selected

*Example:*

```
(<s> ^operator <o> + =)
```

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 2, 2.4.1 English Version

**L2-009** — Every operator that can be proposed has an implementation: application rules that test its ^name in the state where it is proposed, or rules that apply it in its operator no-change substate.

*Rationale:* Otherwise selecting it produces an unintended operator no-change impasse.

*If violated:* Operator no-change impasse; agent stalls

*Source:* Consolidation review (gap)

### Rule: operator application

**L2-010** — An application rule that changes the value of a single-valued attribute adds the new value and removes the old one in the same rule (^attr <new> ^attr <old> -). A WME cannot be changed in place.

*Rationale:* Otherwise the attribute becomes multi-valued.

*If violated:* Attribute has two values

*Example:*

```
(<j> ^contents <new> ^contents <old> -)
```

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 4, 5. Operator Application

**L2-011** — An operator that acts on an external environment changes the state indirectly: it issues a motor command and the state changes through perception. If the agent keeps an internal model of the world, the operator also updates the model.

*Rationale:* External changes arrive only via input; an internal model diverges unless updated by the operator.

*If violated:* Internal model inconsistent with the world.

*Source:* Manual §2.1.8, p.11

**L2-012** — Structure that must outlive a substate (a remembered situation, a cached computation, a task memory) is created on a superstate that persists as long as it is needed (the top state when it must last for the whole run), not in the substate.

*Rationale:* Local o-supported memories would be removed whenever the substate is regenerated.

*If violated:* Remembered information lost on substate regeneration.

*Example:*

```
(<ss> ^remembered <x>)
```

*Source:* Manual §2.7.9.2, p.40-41; Tutorial Part 3, 5.1 Record-sound Operator; Tutorial Part 3, 6.1 The Map Data Structure and Initialization

### Learning: RL

**L2-013** — An RL rule tests the proposed operator (^operator <op> +) together with the state features that define the state-action pair whose value is learned.

*Rationale:* Each RL rule stands for one state-action value.

*If violated:* Values shared across distinct situations

*Example:*

```
(state <s> ^name water-jug ^operator <op> + ^jug <j1> <j2>) (<op> ^name empty ^empty-jug.volume 3) ...
```

*Source:* Tutorial Part 6, 2.1 RL Rules

### Input/output link

**L2-014** — An output command is one attribute under the output-link that names the command; its value is an identifier that carries the command's parameters.

*Rationale:* The environment defines its commands this way and adds feedback such as ^status to the command object.

*If violated:* Malformed command ignored by the environment

*Example:*

```
(<out> ^move <m>) (<m> ^direction north)
```

*Source:* Tutorial Part 2, 2.2.1 English Version; Tutorial Part 2, 2.10. Top-state Structure; Tutorial Part 3, 1.7 Summary of Input-link and Output-link

## L3 Guidance

Guidance from the Soar manual and tutorial that the library material supports.

### Project/file organization

**L3-001** — Use VisualSoar (or another syntax-checking editor) and its datamap to check rules for syntax errors and misspelled attributes before loading them.

*Rationale:* Typos in attribute names (e.g. contant for content) produce rules that load but never match.

*If violated:* Silent non-matching rules

*Source:* Tutorial Part 1, 1.2.5 Working Memory; Tutorial Part 2, 2.5.1 Syntax Errors; Tutorial Part 2, 2.5.4 Semantic Errors

**L3-002** — Formulate each task by writing, in order: state representation, initial-state creation, state elaborations, operator proposals, operator applications, monitoring rules, desired-state recognition, failure recognition (if any) and search control.

*Rationale:* A systematic formulation covers every kind of knowledge the problem needs.

*If violated:* Missing knowledge (e.g. no goal test)

*Source:* Tutorial Part 1, 1.4.13 Summary of Problem Formulation in Soar; Tutorial Part 4, 1. Missionaries and Cannibals Definition; Tutorial Part 5, 1. The Water Jug Problem

### Rule syntax/naming

**L3-003** — Every production plays exactly one role, fixed by what it tests and what it creates: state elaboration, operator proposal, operator evaluation, operator elaboration, operator application, or monitoring. One combination is allowed: a proposal rule may also create unary preferences (best, worst, indifferent) for the operator it proposes. Soar warns about one mix of roles: when a rule that tests the selected operator both elaborates the operator and changes the state, it prints "Operator elaborations mixed with operator applications" when the rule fires and gives all its actions i-support (L0-042, L1-011).

*Rationale:* The rule types are what the other conventions are stated over; a checker classifies every rule first.

*If violated:* Rule cannot be classified; conventions cannot be checked

*See:* related L0-042; L1-011

*Source:* Manual §3.3; Tutorial Part 1; Manual §2.1.1, p.6; §2.3.2, p.18

**L3-004** — An action must not use dot notation to create several attributes of one new object: each dotted path creates a separate object. Create the object with a variable and add the attributes to that variable.

*Rationale:* Each dotted action path makes a new identifier.

*If violated:* Multiple command objects each with one attribute (e.g. two ^move commands)

*Example:*

```
(<out> ^move <m>)
(<m> ^direction north ^speed fast)
```

*Source:* Tutorial Part 2, 2.2.3 Shortcuts

**L3-005** — Every non-default rule tests, in its first condition, the name of the state it matches or of the problem space that state belongs to. This includes rules that fire in every state that holds a world (world and desired elaborations, internal operator applications). The exceptions are the rules that create a state's name or problem space: initialization (which tests ^superstate nil or the initialization operator) and the elaborations that give an operator no-change substate its problem space (which test the superstate's problem space).

*Rationale:* Scopes rules to their problem space; prevents firing in look-ahead copies or unrelated substates by accident.

*If violated:* Rules fire in the wrong states

*Example:*

```
(state <s> ^name water-jug ...)
```

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 3, 2.1 Move Operator

**L3-006** — Format productions with the name right after sp {, conditions aligned under it, an object's attributes aligned, the arrow aligned with conditions, and the closing brace after the last action.

*Rationale:* Improves readability; not required by syntax.

*Source:* Manual §3.3, p.49-50

**L3-007** — Avoid the production type flags :o-support, :i-support, :default and :chunk in user rules. Get persistence by testing a selected operator rather than with :o-support; use any of these flags only with caution. Exception: a rule that records the effect of an external action once the environment reports the output command complete (an environment-effect rule) tests no selected operator and may be flagged :o-support. It may be better to make such rules part of the operator's application.

*Rationale:* Support and rule origin should follow from rule structure and source; the flags are easy to overuse and hide the real source of persistence.

*If violated:* Support that contradicts rule structure; unexpected persistent structures; confusing traces.

*Example:*

```
sp {map*record-object :o-support ...}
```

*Source:* Manual §3.3.3, p.50; Tutorial Part 3, 6.2 Updating the Map

**L3-008** — Use attribute-path notation to avoid intermediate linking variables where the path is single-valued.

*Rationale:* Shorter rules that are easier to read and less error prone.

*Example:* ^moving-block.name <n>

*Source:* Manual §3.3.5.11, p.62

**L3-009** — Do not combine negation, attribute-path notation and multi-valued attributes in one test; write one negated path per value instead.

*Rationale:* The expansion tests a single object with all values, which is rarely intended.

*If violated:* Negation tests the wrong condition.

*Example:*

```
-^ontop.bottom-object.name table
-^ontop.bottom-object.name A
```

*Source:* Manual §3.3.5.11, p.64-65

**L3-010** — Soar symbols are case sensitive (red, Red and RED differ); write all constants in a single case. Use lower case, for consistency across projects; use another case only where needed to match an environment, smem, epmem or input, quoting such names as in L1-004.

*Rationale:* Mixed case leads to silent mismatches.

*If violated:* Rules that never match because of case differences.

*Source:* Manual §3.3.6.2, p.68

**L3-011** — For rules that implement an operator in a substate, use the substate's name (the superoperator name) as the first field of the rule name.

*Rationale:* Keeps track of which substate a rule belongs to.

*If violated:* Rules from different substates indistinguishable by name

*Example:*

```
sp {wander*propose*move ...}
```

*Source:* Tutorial Part 3, 3.3 Wander Operator Suboperators

**L3-012** — Precede each rule, or each group of rules for the same operator or purpose, with a #-comment giving an English version of its conditions and actions, written before the Soar version.

*Rationale:* The English version is documentation and helps design the rule.

*If violated:* Undocumented rules; harder debugging

*Example:*

```
# water-jug*propose*fill
# If the task is water-jug and there is a jug that is not full, propose filling it.
```

*Source:* Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator; Tutorial Part 3, 2.1 Move Operator

**L3-013** — A variable in attribute position is usually restricted with a disjunction of the attributes it may match.

*Rationale:* An unrestricted attribute variable can bind to any attribute of the object, including unrelated ones.

*If violated:* Spurious matches (e.g. matching ^boat or ^other-bank)

*Example:*

```
(<bank> ^{ << cannibals missionaries >> <type> } > 0)
```

*Source:* Tutorial Part 4, 4. Operator Proposal

### State representation

**L3-014** — Attribute and value names have no meaning to the architecture (apart from architecture-created WMEs); choose task labels deliberately and use them consistently across all rules.

*Rationale:* Matching is purely symbolic, so a misspelled or inconsistent label silently fails to match.

*If violated:* Rules that never fire because of inconsistent attribute names.

*Source:* Manual §2.2, p.15

**L3-015** — A domain entity is an object (an identifier with attributes such as ^volume and ^contents). Entity and property are not packed into one attribute name such as ^five-gallon-jug-contents.

*Rationale:* Rules cannot match parts of an attribute name, so structured objects allow general rules with variables.

*If violated:* Separate rules needed for each entity

*Example:*

```
(<s> ^jug <j1>)
(<j1> ^volume 5 ^contents 0)
```

*Source:* Tutorial Part 1, 1.4.2 State Representation; Tutorial Part 4, 2. State Representation

**L3-016** — A set of similar objects is a multi-valued attribute (^jug <j1> ^jug <j2>).

*Rationale:* One set of rules can then process every member of the set.

*If violated:* Member-specific rules

*Example:*

```
(<s> ^jug <j1> <j2>)
```

*Source:* Tutorial Part 1, 1.4.2 State Representation

**L3-017** — A fixed lookup table (for example each direction and its opposite) is working-memory structure created either by an elaboration that tests only that the state exists, or by the initialize-<task-name> operator and then copied into substates.

*Rationale:* General rules can then match relations directly instead of having one rule per case.

*If violated:* Proliferation of case-specific rules

*Example:*

```
(<ss> ^directions <n>)
(<n> ^value north ^opposite south)
```

*Source:* Tutorial Part 2, 2.7.1 Initialization: Opposite Directions; Tutorial Part 3, 5.1 Record-sound Operator

**L3-018** — Encode a decision-relevant classification (e.g. low missiles or energy) once as an abstract state elaboration and have proposals test that elaboration, rather than repeating thresholds in each proposal.

*Rationale:* The threshold lives in one place and multiple rules creating the same WME collapse to one element.

*If violated:* Inconsistent thresholds across operators

*Example:*

```
(<s> ^missiles-energy low)
```

*Source:* Tutorial Part 3, 4.1 Chase Operator Proposal

**L3-019** — Where ^io is copied into substates, a rule meant only for the top state tests ^superstate nil, not just the presence of ^io.

*Rationale:* Otherwise the elaboration fires again in every new substate.

*If violated:* Duplicate elaborations in every substate

*Example:*

```
(state <s> ^name tanksoar ^io.input-link.missiles 0)
```

*Source:* Tutorial Part 3, 4.1 Chase Operator Proposal; default soar-base/simple.soar soar-base*elaborate*default*state*io

**L3-020** — Copy or derive input-link values needed by a substate onto that substate with an elaboration (e.g. ^sound-direction), or copy the whole ^io structure down to the substate, and have the substate's rules test the local copy.

*Rationale:* If the source of the value later changes (e.g. to a remembered value), only the elaboration has to change.

*If violated:* Many rules to edit when the representation changes

*Example:*

```
sp {chase*elaborate*state*sound-direction (state <s> ^name chase ^io.input-link.sound <d>) --> (<s> ^sound-direction <d>)}
```

*Source:* Tutorial Part 3, 4.2 Chase Operator Application; Tutorial Part 3, 5.1 Record-sound Operator

**L3-021** — To remember the previous operator, an application rule copies what later rules need (its name and the parameters that identify it, e.g. ^name pour ^fill-jug <fj> ^empty-jug <ej>) into a state structure ^last-operator, rather than keeping a pointer to the operator identifier. Maintenance is L4-005; uses are L3-047.

*Rationale:* The selected operator and its substructure go away once its proposal retracts, so a pointer to it ends up empty. The parameters are needed to tell what the operator did, not just its name.

*If violated:* Record vanishes or becomes empty; an undo cannot be identified from the name alone

*Example:*

```
(<s> ^last-operator <lo>)
(<lo> ^name pour ^fill-jug <fj> ^empty-jug <ej>)
```

*Source:* Tutorial Part 1, 1.4.11 Search Control

**L3-022** — Exception to L2-010: remove an incorrect value in its own application rule only when the current value is known to be incorrect but a correct value is not yet available; add the correct value later when it is.

*Rationale:* A single rule cannot handle both the initial case (no old value) and the update case.

*If violated:* Accumulating stale values, or missing initial value

*Example:*

```
(<s> ^last-direction <d> -)
```

*Source:* Tutorial Part 2, 2.7.2 Advanced Move Operator Application; Tutorial Part 1, 1.4.11 Search Control

**L3-023** — Attributes that link task objects to each other and never change (for example ^other-bank) are left out of duplicate-state tests and RL templates.

*Rationale:* Identifiers differ between a state and its look-ahead copies, so comparing links never matches.

*If violated:* Duplicates never detected; RL features never match

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Goal/desired representation

**L3-024** — The goal is a structure on the state, created at initialization, and success is recognized by comparing it with the current state; the goal is not hard-coded in a rule.

*Rationale:* New problems can be posed by changing working memory, and the desired state can guide search.

*If violated:* Goal changes require editing rules

*Example:*

```
(<s> ^desired.jug <k>)
(<k> ^volume 3 ^contents 1)
```

*Source:* Tutorial Part 1, 1.4.10 Desired State Recognition; Tutorial Part 4, 3. Initial State Creation: Initialize-mac

**L3-025** — A losing or failure state is recognized by a separate i-supported rule that marks the state (^failure <desireds>). Operator proposals may also encode failure avoidance when that knowledge is available, but it rarely is, so the failure mark is the general mechanism.

*Rationale:* An i-supported mark retracts automatically when the state is no longer a failure. Failure knowledge in a proposal is correct only where it is known in advance, and it moves problem knowledge into the problem space.

*If violated:* Failures that are not recognized, or problem-space legality mixed with failure knowledge

*Example:*

```
(<bank> ^missionaries { <n> > 0 } ^cannibals > <n>) --> (<s> ^failure <d>)
```

*Source:* Tutorial Part 4, 1. Missionaries and Cannibals Definition; Tutorial Part 4, 9. Search Control: Undoing the Last Operator

### Operator WM representation

**L3-026** — Put on the operator any information that later selection rules need to compare it (e.g. the content of the target cell), so search control need not re-derive it.

*Rationale:* Simpler selection rules that test only the proposed operators.

*If violated:* Complex selection rules that rematch the state

*Example:*

```
(<o> ^name move ^direction <dir> ^content <content>)
```

*Source:* Tutorial Part 2, 2.6.1 Move Operator Proposal

**L3-027** — Where practical, make the operator representation describe the change it makes (e.g. entity type as attribute and count as value) so that a single general application rule can apply all instances.

*Rationale:* General application rules replace many operator-specific ones.

*If violated:* Many near-duplicate application rules

*Example:*

```
(<o> ^name move-mac-boat ^bank <b> ^cannibals 1 ^boat 1 ^types 1)
```

*Source:* Tutorial Part 1, 1.3 Building a Simple Hello-World Agent Using an Operator; Tutorial Part 4, 4. Operator Proposal; Tutorial Part 4, 5. Operator Application

**L3-028** — For operators that perform external actions, place the output commands on the operator under an ^actions object (^actions.<command>.<param> <value>), so generic rules can copy them to the output-link.

*Rationale:* A single generic rule then performs output for every operator without copying unrelated operator augmentations.

*If violated:* Need for per-operator output rules

*Example:*

```
(<o> ^name jump ^actions.jump.direction <dir>)
```

*Source:* Tutorial Part 2, 2.8.3 Simplified Operators; Tutorial Part 3, 2. Simple Wandering Tank

**L3-029** — Each action in the world is performed by a new operator instance. One selected operator must not be expected to perform repeated actions.

*Rationale:* Each instance is selected and applied once; repetition comes from re-proposal.

*If violated:* Agent acts once and then reaches an impasse

*Source:* Tutorial Part 2, 2.3.1 Operator Selection: Multiple Instances

**L3-030** — A parameter that ranges over a small set of constants (for example move 1 or 2 missionaries) gets one proposal rule per value, with the value as a constant on the operator; application rules read it from the operator.

*Rationale:* Operator instances are distinguishable for preferences, chunking and RL.

*If violated:* Instances indistinguishable

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Rule: state elaboration

**L3-031** — A feature that is entailed by core state features (a block is clear, a jug's free space) may be an i-supported elaboration, so that operator applications change only the core features, provided that both its presence and its absence are computed by rules and those rules use no local negations (negations over structure in a substate such as a look-ahead state). A feature that cannot be computed that way is maintained by the operator applications that change it.

*Rationale:* Elaborations retract and re-derive automatically, which simplifies operator encoding. A rule that tests the absence of structure leaves a local negation out of any chunk built from it, so the chunk is over-general.

*If violated:* Application rules that must maintain every derived feature by hand; or chunks that are over-general because a derived feature is computed with a local negation.

*Source:* Manual §2.1.9, p.12; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 1, 1.4.13 Summary of Problem Formulation in Soar; JL review 18 Nov 2026

### Rule: operator proposal

**L3-032** — An operator that is carried out by suboperators which change what its proposal tests is proposed through a relevance elaboration (^<op>-relevant), so that the same operator stays selected while its substate works. The relevance elaboration is an i-supported rule on the state that tests the situations in which the operator is relevant, including the intermediate situations its suboperators create (for example, the jug is not full, or is full and still held), and creates ^<op>-relevant with the object the operator applies to; the proposal rule tests ^<op>-relevant in place of the conditions the suboperators change.

*Rationale:* Otherwise each result retracts the proposal, a new operator is made, and the substate ends and is rebuilt.

*If violated:* Hierarchical operator re-proposed after every sub-operator result

*Source:* Small families (agentgen, 6 Nov 2026)

**L3-033** — An operator proposal should test WMEs that the operator's application (or its effect on input) changes, so that the proposal retracts after the application and a new decision follows.

*Rationale:* An operator stays selected while its acceptable preference remains and no better candidate appears.

*If violated:* Operator no-change impasse after the operator has effectively applied.

*Example:*

```
(state <s> ^io.input-link.eater <e>) (<e> ^x <x> ^y <y>)
```

*Source:* Manual §2.5, p.25; §2.7.1, p.28; §2.7.7, p.35; Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 2, 2.3.1 Operator Selection: Multiple Instances; Tutorial Part 4, 5. Operator Application

**L3-034** — An operator whose application would leave the state unchanged (for example filling a full jug) must not be proposed.

*Rationale:* If application changes nothing, the proposal never retracts and the operator never terminates.

*If violated:* Operator no-change impasse / stuck operator

*Example:*

```
(<j> ^empty > 0)
```

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L3-035** — To exclude an option, a proposal does not test the absence of a record (-^last-direction <dir>): the negated test is dropped from chunks learned in a substate, such as a look-ahead, and the chunk is over-general (L3-062). The record always exists (it is initialized, for example ^last-direction none) and the proposal tests the presence of a record with a different value (^last-direction <> <dir>).

*Rationale:* A negated test on state structure is a local negation in a substate and is left out of the chunk. A presence test is a positive condition that chunking keeps, but it fails when no record exists yet, so the record must exist from the first decision.

*If violated:* Over-general chunks from look-ahead; or, if the record is not initialized, the operator is never proposed in the initial situation.

*Example:*

```
(state <s> ^directions <d> ^last-direction <> <o-dir>) (<d> ^value <dir> ^opposite <o-dir>)
# initialization: (<s> ^last-direction none)
```

*Source:* Tutorial Part 2, 2.7.3 Advanced Move Operator Proposal

**L3-036** — A proposal's conditions state when the operator is relevant to the situation. Relevance is a design decision and may come from the goal, so an operator can be proposed before its preconditions hold.

*Rationale:* Soar programs are organised implicitly by problem spaces via proposal conditions.

*If violated:* Irrelevant operators proposed, causing ties.

*Example:*

```
(state <s> ^problem-space blocks)
```

*Source:* Manual §2.1.10, p.12

**L3-037** — Always write the + for acceptable preferences in actions, even though it is implicit when no other preference is given for that operator.

*Rationale:* Makes the semantics explicit; a non-acceptable preference alone does not imply acceptable.

*If violated:* An operator given only (> ) is never selected.

*Example:*

```
(<s> ^operator <o> + >)
```

*Source:* Manual §3.3.6.4-3.3.6.5, p.69-70

**L3-038** — Precondition style: an operator is proposed if and only if its preconditions are satisfied; whether it should be chosen is left to selection knowledge. This is not the means-ends analysis (MEA) style, in which an operator is proposed when it is relevant to the goal even if its preconditions are not satisfied, and an operator no-change impasse sets up subgoals to achieve them.

*Rationale:* Separating problem-space knowledge from search control is a design goal of Soar.

*If violated:* Proposal rules tangled with heuristics

*Source:* Tutorial Part 1, 1.4.1. Water Jug; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L3-039** — Add an indifferent preference (+ =) to proposals only when the order in which the competing operators are chosen does not matter, for example when the operators are monotonic (each only adds to the state and none blocks or undoes another, so every order reaches the same result); not as a default way to avoid ties. Agents converted to RL leave it out (L3-083).

*Rationale:* Indifference asserts knowledge that the options are equivalent; ties are the signal that more problem solving (e.g. look-ahead) is needed.

*If violated:* Random choices where deliberation was needed; planning never invoked

*Example:*

```
(<s> ^operator <o> + =)
```

*Source:* Tutorial Part 5, 1. The Water Jug Problem; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 2, 2.4 Move-To-Food Operator

**L3-040** — Do not propose two operators in a single rule. Exception: one rule may propose a fixed set of operators that differ only in a constant parameter (for example move with direction -1 and move with direction 1).

*Rationale:* One operator per proposal rule keeps rules separate and easy to debug.

*If violated:* Coupled operators; hard debugging

*Source:* Tutorial Part 3, 7.2 Final Thoughts

**L3-041** — Means-ends style: an operator is proposed when it can achieve part of the desired state, whether or not its preconditions hold. Unmet preconditions are achieved in its operator no-change substate before it applies.

*Rationale:* Means-ends analysis: the goal, not the current state alone, determines relevance.

*Source:* Decided 6 Nov 2026 (JL)

**L3-042** — In either style, proposals may be further restricted by heuristic conditions that exclude operators that are applicable or goal-relevant but not useful in the situation.

*Rationale:* Efficiency; heuristic knowledge in proposals.

*Source:* Decided 6 Nov 2026 (JL)

### Rule: operator elaboration

**L3-043** — Issue reflex-like commands (e.g. shields on/off) by adding them to the ^actions of whatever operator is selected, not by writing directly to the output-link from a non-operator rule.

*Rationale:* Direct writes produce output early and can preempt other output in environments that run the agent until output appears.

*If violated:* Output generated before the real action is ready

*Example:*

```
sp {elaborate*shields-on (state <s> ^operator.actions <a> ^io.input-link <il>) (<il> ^incoming.<dir> yes ^shield-status off) --> (<a> ^shields.switch on)}
```

*Source:* Tutorial Part 3, 4.8 Shield Control Rules

### Rule: operator evaluation/selection

**L3-044** — Use require (!) rather than best (>) when an operator must be selected, because a candidate that is better than a best candidate wins over it.

*Rationale:* BetterWorseFilter runs before BestFilter.

*If violated:* A best operator unexpectedly loses to a better preference.

*Source:* Manual §2.4.1, p.20

**L3-045** — Use a worst (<) preference as a default: a worst operator is chosen only when there are no non-worst alternatives.

*Rationale:* WorstFilter removes worst candidates unless all are worst.

*Example:*

```
(<s> ^operator <o> <)
```

*Source:* Manual §2.4.1, p.20

**L3-046** — Use a reject preference when an operator must not be selected in the current situation even if nothing else is available; use a worst preference when it may be selected but only if nothing better exists.

*Rationale:* Reject removes the option entirely, while worst only orders it last.

*If violated:* Agent stuck (reject) or does pointless actions (worst)

*Example:*

```
(<s> ^operator <o> -)  vs  (<s> ^operator <o> <)
```

*Source:* Tutorial Part 2, 2.7.4 Advanced Move Operator Selection; Tutorial Part 2, 2.6.4 Summary of Preferences

**L3-047** — Use a worst preference to avoid immediately undoing the previous operator (matching the proposed operator against ^last-operator, L3-021).

*Rationale:* A cheap heuristic that shortens undirected search.

*If violated:* Wasted inverse operator applications

*Example:*

```
(<o> ^name fill ^fill-jug <i>) (<lo> ^name empty ^empty-jug <i>) --> (<s> ^operator <o> <)
```

*Source:* Tutorial Part 1, 1.4.11 Search Control; Tutorial Part 4, 9. Search Control: Undoing the Last Operator

**L3-048** — In look-ahead, reject an operator that undoes the previous operator (matching the proposed operator against ^last-operator, L3-021).

*Rationale:* An operator that undoes the previous one returns to the previous state, so evaluating it adds nothing; a reject removes it from the look-ahead search.

*If violated:* Look-ahead spends decisions evaluating operators that return to the previous state

*Source:* Tutorial Part 5, 2.1.6 Remove last-operator rules; Tutorial Part 5, 1.4.4 Evaluating the result

### Rule: operator application

**L3-049** — Prefer modifying the attributes of existing state objects in application rules over deleting and recreating whole objects.

*Rationale:* Fewer working-memory changes and a more natural model (the jug is the same jug); two-level state copying supports look-ahead.

*If violated:* More WM churn; unnatural representation

*Source:* Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 5, 1.4.1 Creating the Initial State

**L3-050** — When several application rules are needed for one operator (e.g. different situations for pour), make their conditions mutually exclusive.

*Rationale:* Only the rule matching the situation should fire.

*If violated:* Conflicting changes applied together

*Example:* ^contents { <= <jempty> <icon> } vs ^contents { <icon> > <jempty> }

*Source:* Tutorial Part 1, 1.4.8 Operator Application

**L3-051** — An attribute should be maintained either by elaborations (i-support) or by operator applications (o-support), not both.

*Rationale:* Mixed support makes values reappear or vanish unexpectedly.

*If violated:* Values reappear after removal, or disappear

*See:* related L3-031; L1-012; L14-043

*Source:* Consolidation review (gap); Manual §2.3.3

**L3-052** — When an operator may apply to an attribute that has no current value, provide a separate application rule that adds the value only when none exists (tests -^attr); the rule of L2-010 changes the value when one exists. Together they cover both cases. It is preferred that the attribute is initialized when its object is created, so that this rule is not needed.

*Rationale:* L2-010's rule needs an old value to match; without one it does not fire.

*If violated:* Attribute never set when it starts with no value

*Example:*

```
(state <s> ^operator <o>) (<o> ^name set ^value <v>)
-(<s> ^attr)
--> (<s> ^attr <v>)
```

*Source:* Decided 6 Nov 2026 (JL)

### Rule: monitoring/output

**L3-053** — (halt) is used only when the run must end for good; (interrupt) is used for debugging, to stop the run so that the program can be examined and resumed.

*Rationale:* Halt terminates the run irreversibly.

*If violated:* Agent cannot be continued.

*Source:* Manual §3.3.6.6, p.71

**L3-054** — Avoid the (wait) RHS function.

*Rationale:* The manual discourages it; it sleeps the Soar thread.

*If violated:* Slow or stalled agent.

*Source:* Manual §3.3.6.6, p.72

**L3-055** — write, crlf and log are for simple text output; extensive text input and output goes through SML.

*Rationale:* RHS text functions are minimal debugging output.

*Example:*

```
(write (crlf) |Moving | <n>)
```

*Source:* Manual §3.3.6.6, p.72

**L3-056** — Monitoring rules are separate from problem-solving rules: they test the state or the selected operator and only print. They fire in parallel with application and do not affect it.

*Rationale:* Printing the operator and state makes problem solving easy to follow without interfering with it.

*If violated:* Monitoring mixed into functional rules

*Example:*

```
sp {water-jug*monitor*operator-application*fill (state <s> ^name water-jug ^operator <o>) (<o> ^name fill ^fill-jug.volume <v>) --> (write | FILL(| <v> |)|)}
```

*Source:* Tutorial Part 1, 1.4.9 State and Operator Monitoring; Tutorial Part 2, 2.4.3 Shortcuts and Extensions

### Rule: impasse/substate handling

**L3-057** — An operator whose substate creates local o-supported structure should be implemented so that it is re-entrant: it resumes correctly after the goal dependency set regenerates its substate (L0-054). Soar does not guarantee this; it depends on how the substate is written.

*Rationale:* The GDS may remove and recreate the substate at any time.

*If violated:* Partial work repeated or corrupted after regeneration.

*Source:* Manual §2.7.9.2, p.40

**L3-058** — Impasses are a normal way to decompose problems and deliberate about selection, not necessarily a program error; impasses are required for chunking to learn.

*Rationale:* Substates are Soar's mechanism for hierarchical decomposition and learning.

*Source:* Manual §2.7.7, p.34

**L3-059** — Use (or adapt) the default productions for handling impasses rather than writing ad-hoc impasse handling from scratch.

*Rationale:* The default rules provide standard ways of resolving common impasses.

*Source:* Manual §3.4.1, p.85

**L3-060** — When a state no-change should mean waiting rather than impassing (e.g. expert models waiting on the world), enable soar wait-snc so no substate is created.

*Rationale:* A wait state repeats the decision cycle without creating a substate.

*If violated:* Spurious substates while waiting.

*Example:* soar wait-snc on

*Source:* Manual §9.1.1 soar wait-snc, p.190

### Substate representation

**L3-061** — Store features locally in the substate for local non-monotonic reasoning about the context (e.g. counting, projection/planning), accepting that the substate is removed when its context changes.

*Rationale:* Such reasoning is only valid relative to the current context.

*Source:* Manual §2.7.9.2, p.41

### Rule: results

**L3-062** — A rule on the path to a result should not test the absence of local substate structure: the negation is dropped from the chunk or justification, which is then over-general (L0-091). Remedies: hold the tested data in the superstate, make it a result, or set chunk allow-local-negations off to reject such chunks.

*Rationale:* Only negated conditions on superstate WMEs are carried into justifications.

*If violated:* Over-general justification or chunk.

*Example:* -(<s> ^tried <x>) # local negation, dropped

*Source:* Manual §2.7.4, p.32; §4.5.2.1, p.104; §4.6.10, p.112; Manual §4 (EBC: local negations)

**L3-063** — A previous result is tested or changed through a path from the superstate, not through a path local to the substate. Otherwise explanation-based chunking repairs the chunk with grounding conditions that can over-specialize it.

*Rationale:* EBC cannot know where in the superstate a result lives when it is reached via a local path.

*If violated:* Repaired, over-specialised chunks (shown in chunk stats).

*Source:* Manual §4.6.7, p.110-111; §4.5.3.6, p.107

**L3-064** — When a result depends on the impasse itself, that is, on there being nothing more to come (for example a state no-change after every operator is exhausted), the rule that creates it tests ^quiescence t. The test signals that what is computed depends on the impasse having occurred; as a consequence no chunk is learned for that result (L0-094).

*Rationale:* Without the test, the chunk would leave out its dependence on the impasse and could fire where no impasse would have occurred.

*If violated:* Over-general chunk that fires in situations without the impasse.

*Example:*

```
(state <s> ^quiescence t)
```

*See:* related L0-094

*Source:* Manual §4.6.11, p.112-113; §4.6.17, p.118; Manual §3.4.1, p.85; §4.6.11, p.112

**L3-065** — Semantic or episodic knowledge needed for a result should be retrieved in a higher state, not in the substate where learning occurs. Soar does not trace back to the cue of a semantic or episodic retrieval: conditions on knowledge recalled in the substate are local and are dropped from the chunk.

*Rationale:* There is no backtracing to the cue, so recalled knowledge is treated as local and its retrieval reasons are opaque.

*If violated:* Over-general chunks.

*Source:* Manual §4.6.13, p.113-114

**L3-066** — Substate structures become results indirectly when their identifier becomes linked to a superstate through another result. This gives an approach for creating all of a result at once instead of incrementally: build the structure locally in the substate, then link it to the superstate last (e.g., build an operator's structure locally, then create its acceptable preference in the superstate).

*Rationale:* Linking makes the entire substructure results at once.

*If violated:* Superstate sees a partially constructed operator.

*Example:*

```
(<ss> ^operator <o> +)  # after <o> is complete
```

*Source:* Manual §2.7.3, p.31

### Semantic memory

**L3-067** — Keep the semantic store in memory for most runs; if using a file database, leave lazy-commit on and set path and append before initialisation (changes take effect after --init).

*Rationale:* Disk-based stores are costly; storage parameters apply only after init.

*If violated:* Slow runs, or settings with no effect.

*Example:* smem --set database memory

*Source:* Manual §6.3.4, p.147; §6.5.2, p.153

**L3-068** — A rule that uses a semantic-memory retrieval tests ^result.success or ^result.failure, and the retrieved structure, before it acts on ^result.retrieved.

*Rationale:* Retrieval may fail and results arrive only after the command is processed.

*If violated:* Rules acting on missing or stale results.

*Example:*

```
(<s> ^smem.result.retrieved <r>)
```

*Source:* Manual §6.4.1-6.4.2, p.148-149; Tutorial Part 7, 4. Non-Cue-Based Retrieval; Tutorial Part 7, 5. Cue-Based Retrieval

**L3-069** — Use ^prohibit <lti> modifiers (repeatable) to exclude already-retrieved LTIs and iterate over all matches; use ^neg-query and ^math-query to constrain the cue.

*Rationale:* Ties among matching LTIs go to the most activated LTI.

*If violated:* Repeated retrieval of the same LTI.

*Example:*

```
(<cmd> ^query <q> ^prohibit <old>)
```

*Source:* Manual §6.4.2, p.149-150

**L3-070** — Use ^depth <n> with a retrieval only when necessary, since deep retrievals can be costly.

*Rationale:* Retrieves children recursively.

*If violated:* Slow retrievals.

*Example:*

```
(<cmd> ^query <q> ^depth 2)
```

*Source:* Manual §6.4.3, p.152-153

### Episodic memory

**L3-071** — Keep episodic cues small and avoid cues that relate to every episode or include multi-valued identifiers needing graph matching, since retrieval can be linear in episodes or combinatorial in literals.

*Rationale:* Cue-based search and graph match are the unbounded costs.

*If violated:* Very slow retrievals.

*Source:* Manual §7.4, p.161-162

**L3-072** — Propose an episodic query operator only when the command link is empty (-^epmem.command.<cmd>), and replace the previous command when issuing the next one (e.g. ^query with ^next).

*Rationale:* One command at a time; the agent maintains the command link.

*If violated:* Repeated or conflicting commands

*Example:*

```
(state <s> ^name epmem -^epmem.command.<cmd>)
```

*Source:* Tutorial Part 8, 4. Cue-Based Retrieval; Tutorial Part 8, 5. Temporal Progression

### Learning: chunking

**L3-073** — Learning should be off in a substate whose result depends on a probabilistic choice among indifferent or numeric-indifferent operators: no chunk summarizes that reasoning correctly.

*Rationale:* A different random choice could produce a different result.

*If violated:* Incorrect chunks.

*Example:*

```
(dont-learn <s>) with chunk except
```

*Source:* Manual §4.6.9, p.111

**L3-074** — Substate rules should test only what is needed to produce the result: a chunk's conditions are exactly what the substate rules tested.

*Rationale:* Unneeded tests carry over into the learned rule.

*If violated:* Overly specific chunks

*Source:* Tutorial Part 5, 1.4.5 Chunking

**L3-075** — Application rules test every operator attribute that distinguishes one operator instance from another, so that chunks learned from evaluations include those distinctions.

*Rationale:* Chunking picks up only what the rules tested; untested distinguishing features yield overgeneral rejections.

*If violated:* Overgeneral chunk rejects an operator on the solution path

*Example:*

```
(<o> ^name move-mac-boat ^{ << missionaries cannibals boat >> <type> } <num> ^bank <bank> ^types <types>)
```

*Source:* Tutorial Part 5, 2.2 Subtle chunking problem

**L3-076** — With chunking, exact evaluations (success, failure) are preferred to heuristic numeric evaluations that are only partly correct: a chunk captures the heuristic's errors too.

*Rationale:* Chunking is only as good as the problem solving it summarizes.

*If violated:* Learned rules embody heuristic mistakes; worse performance

*Source:* Tutorial Part 5, 2.3 Numeric Evaluations

**L3-077** — When several superstate structures can each produce the same local substate WME that a result depends on, put that WME on the superstate (make it a result) instead of in the substate, so that the learned rule creates one result (L0-099).

*Rationale:* The rule learned then produces one result regardless of how many rules create the WME.

*If violated:* Incorrect chunks from disjunctive context conflation.

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.6.12 Disjunctive Context Conflation

**L3-078** — Do not declare chunking singletons by hand: Soar 9.6.5 creates them automatically for string attributes (chunk automatically-create-singletons, on by default). Declare one with chunk singleton only where the automatic ones do not apply.

*Rationale:* Removes unnecessary generality and redundant conditions in chunks.

*If violated:* Redundant, over-general conditions in learned rules.

*Example:* chunk singleton state gripper identifier

*Source:* Manual §4.4.1, p.100; §4.7.3.2, p.120; §9.4.1, p.232; Soar online CLI reference, chunk (automatically-create-singletons); Soar 9.6.5 build 9.6.50

**L3-079** — Use chunk stats and the explain mechanism (rather than backtracing traces) to diagnose repaired rules, local negations, and LTM-dependent chunks.

*Rationale:* Stats report potential generality and correctness issues directly.

*Example:* chunk stats

*Source:* Manual §4.7.3.1, p.120; §4.7.4, p.120-122

**L3-080** — If chunking hits max-chunks, stop execution and investigate rather than continuing.

*Rationale:* The manual warns Soar cannot then guarantee consistency of its internal structures.

*If violated:* Inconsistent agent state.

*Source:* Manual §9.4.1.4 chunk max-chunks, p.235

### Learning: RL

**L3-081** — For table-based RL write one RL rule per state-operator pair; more generally RL rules act as binary features of a linear Q-function approximation (e.g. tile coding), with the update divided equally among contributing rules.

*Rationale:* Rules matching an operator jointly define its Q-value.

*Source:* Manual §5.1, p.132-133; §5.3, p.135

**L3-082** — RL rules can also be learned by chunking when the state is relational and cannot be enumerated; a chunk is an RL rule when it has RL rule form.

*Rationale:* RL rules are ordinary productions.

*Source:* Manual §5.4.3, p.141

**L3-083** — When converting an agent to RL, take the indifferent preference out of the proposal rules, leaving only the acceptable preference, and supply values through separate RL rules.

*Rationale:* Keeps proposal (legality) separate from learned value.

*If violated:* Static indifference competes with learned values

*Example:*

```
(<s> ^operator <o> +)
```

*Source:* Tutorial Part 6, 2.1 RL Rules

**L3-084** — Generate RL rules for an enumerable state-action space with gp (or scripting) rather than by hand or with rule templates; use rule templates only when rules cannot be enumerated in advance, since template-instance checking can become expensive in long runs.

*Rationale:* Full state-action coverage can require many rules.

*If violated:* Incomplete or error-prone hand enumeration

*Example:* gp {rl*water-jug*empty ... (<op> ^name empty ^empty-jug.volume [3 5]) ... --> (<s> ^operator <op> = 0)}

*Source:* Tutorial Part 6, 2.1 RL Rules; Manual §5.4.1, p.139; Manual §5.4.2, p.141

**L3-085** — Numeric-indifferent preferences from non-RL rules (rules outside the L0-100 format, such as a proposal that also creates = 0.5, or a rule with a computed value) should not be mixed with RL rules for the same operators unless that is intended: all numeric-indifferent values for an operator are combined, and only RL rules are updated.

*Rationale:* Fixed values bias or mask learned ones.

*If violated:* Learning appears not to work

*See:* related L0-100

*Source:* Consolidation review (gap); Manual §5.1

**L3-086** — With RL, numeric-indifferent-mode should be left at sum (the default): an operator's Q-value is then the sum of the numeric-indifferent values of all RL rules that match it. Soar does not enforce this.

*Rationale:* RL updates assume the summed value.

*If violated:* Incorrect Q-values and updates.

*Example:* decide numeric-indifferent-mode --sum

*Source:* Manual §5.1, p.133 (fn. 2); §2.4.1, p.21

**L3-087** — With GQ(lambda) learning policies, set the rl step-size-parameter small (e.g. 0.01).

*Rationale:* Secondary weights must change slowly to converge.

*If violated:* Poor convergence.

*Example:* rl --set step-size-parameter 0.01

*Source:* Manual §5.3.4, p.139

**L3-088** — Enable RL with rl --set learning on and choose an exploration policy (e.g. indifferent-selection --epsilon-greedy), for instance in the project's load file.

*Rationale:* RL is off by default.

*If violated:* No learning

*Example:*

```
rl --set learning on
indifferent-selection --epsilon-greedy
```

*Source:* Tutorial Part 6, 1.2 Running the Left-Right Agent; Tutorial Part 6, 3. Further Exploration

### Input/output link

**L3-089** — Copy environment reward from the input-link to the reward-link with rules; the reward-link is not part of io and is not written by the environment.

*Rationale:* The environment writes only to the input-link.

*If violated:* No reward reaches RL.

*Example:*

```
(state <s> ^io.input-link.reward <v> ^reward-link <rl>) --> (<rl> ^reward.value <v>)
```

*Source:* Manual §5.2, p.134

**L3-090** — Output commands are created by operator application rules, so that each command is an o-supported, deliberate action. Output functions run at the end of a cycle only if structure under the output-link changed.

*Rationale:* Actions are deliberate commitments made by operators.

*If violated:* Commands issued without deliberation, or retracted early

*Example:*

```
sp {apply*move-north (state <s> ^operator.name move-north ^io.output-link <out>) --> (<out> ^move.direction north)}
```

*Source:* Tutorial Part 2, 2.2.2 Soar Version; Tutorial Part 2, 2.3.2 Operator Application: Persistence; Manual §3.5.1, p.87; §3.5.2, p.88-89; §3.5.3, p.90

**L3-091** — One generic application rule copies the selected operator's command to the output-link and another removes each command, by rejecting its link on the output-link, after the environment marks it ^status complete, so that an operator with an external action needs only a proposal rule.

*Rationale:* Removes duplicated per-operator output rules.

*If violated:* Many duplicated output rules

*Example:*

```
sp {io*elaborate*operator*remove-command (state <s> ^operator.actions ^io.output-link <out>) (<out> ^<att> <v>) (<v> ^status complete) --> (<out> ^<att> <v> -)}
```

*Source:* Tutorial Part 2, 2.8.3 Simplified Operators; Tutorial Part 3, 3.4 General Rule Summary

**L3-092** — Interpreted input lands on the task state: elaborations that test ^io.input-link copy what the task needs onto the state (constants as they are, objects with fresh identifiers, L1-021). All other task rules test the state, never the input-link.

*Rationale:* One place holds the mapping; look-ahead and chunking see state structure, not the environment's.

*If violated:* Task rules tied to the environment's names; input aliasing; the task cannot be simulated in look-ahead.

*Example:*

```
(state <s> ^name io-guess ^io.input-link.turn <t>) --> (<s> ^turn <t>)
```

*Source:* Soar-Lean-Agents issue 5; Tasks/Reference/io-guess (15 Nov 2026)

**L3-093** — An agent in an environment halts on the environment's input-link signal that the task instance has ended (for example ^game-over true), by an operator application; the agent's own goal is not the end of the task instance unless the environment says so.

*Rationale:* The environment owns the task instance. In the task language Goal is terminal, so a goal reached before the environment's signal stops the agent too early.

*If violated:* The agent halts while the environment is mid-task-instance, or runs on after it ended.

*Example:*

```
(state <s> ^operator <o>) (<o> ^name stop) --> (halt)   with stop proposed on ^game-over true
```

*Source:* Soar-Lean-Agents issue 5; Tasks/Reference/io-guess (15 Nov 2026)

### Settings/commands

**L3-094** — With RL, the exploration policy is set explicitly (indifferent-selection: epsilon-greedy or boltzmann) and not left at the default softmax.

*Rationale:* Those policies are designed for RL; softmax is default only for backward compatibility.

*If violated:* Unsuitable exploration.

*Example:* decide indifferent-selection --epsilon-greedy

*Source:* Manual §5.3.3.1, p.138-139

**L3-095** — An attribute that usually has many values at once is declared with production optimize-attribute before the productions are loaded, to help condition ordering.

*Rationale:* Gives the reorderer hints about multi-attributes; has no effect if issued after rules are loaded.

*If violated:* Slower matching in problematic cases.

*Example:* production optimize-attribute thing 20

*Source:* Manual §9.2.3.8, p.213

**L3-096** — A max-elaborations warning is treated as a sign of a fire-and-retract loop. The limit is raised only for a program that really needs that many elaboration cycles.

*Rationale:* When the limit is hit, Soar moves to the next phase without quiescence.

*If violated:* Decisions made before quiescence.

*Example:* soar max-elaborations 200

*Source:* Manual §9.1.1 soar max-elaborations, p.188

**L3-097** — Substate depth is bounded with soar max-goal-depth. Unbounded depth usually comes from a defect that repeats state no-change impasses.

*Rationale:* Prevents infinite recursive subgoaling.

*If violated:* Runaway goal stack.

*Example:* soar max-goal-depth 100

*Source:* Manual §9.1.1 soar max-goal-depth, p.188

**L3-098** — Debug with trace and inspection commands: run a full trace (watch 5) viewed collapsed, and use matches, preferences --names/--wmes, print --depth and print-stack to find why rules did or did not fire.

*Rationale:* These commands show what is about to fire, what created a preference, and why a condition failed.

*If violated:* Slow, guess-based debugging

*Example:*

```
matches propose*move-to-food
preferences I3 move --names
```

*Source:* Tutorial Part 1, 1.3.1 Hello World Operator: English Version; Tutorial Part 2, 2.5.3 Runtime Debugging Commands; Tutorial Part 3, 3.2 Impasses and State Creation

## L4 Default rules

Conventions set by the default rules of soar-base (loaded with the shared library).

### Rule syntax/naming

**L4-002** — Task rules do not reuse the names the default rules rely on: the operator name wait, the state attribute ^top-state, and the assignment of a substate's ^name from the superoperator.

*Rationale:* Collisions change default behaviour.

*If violated:* Default rules misfire

*Source:* Consolidation review (gap); default soar-base/simple.soar, elaborations/_all.soar

### State representation

**L4-003** — Every state has ^top-state, which points to the top state. Rules reach top-level structure through ^top-state, not through a chain of ^superstate. In a look-ahead state ^top-state is the look-ahead state itself (L7-009).

*Rationale:* Uniform access from any depth.

*If violated:* Long ^superstate chains

*Example:*

```
(state <s> ^top-state <ts>)
```

*Source:* Default: elaborations/top-state.soar; selection/elaborations/top-state.soar

### Rule: operator evaluation/selection

**L4-005** — ^last-operator is maintained by one application rule that, whenever an operator is applied, adds the new record and removes the previous one (L2-010), and is initialized (for example by the init-<task-name> operator) with an empty ^last-operator so that rules testing it match from the first decision.

*Rationale:* Without removal the state accumulates several records and comparisons match stale ones; without initialization rules that test it cannot match on the first decision.

*If violated:* Several ^last-operator values at once; rules that test it do not fire at the start

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Rule: impasse/substate handling

**L4-006** — A wait operator is proposed with a worst preference in a state no-change substate (^attribute state ^choices none) when no wait is already selected, except, as planned, in look-ahead for agent-world (L9-025), so that an idle agent waits in one substate and does not stack impasses. soar-base and agent-world (L9-025) each provide one.

*Rationale:* Prevents runaway substate creation.

*Example:*

```
sp {top-state*propose*wait (state <s> ^attribute state ^choices none -^operator.name wait) --> (<s> ^operator <o> +) (<o> ^name wait)}
```

*Source:* Default: soar-base/simple.soar soar-base*propose*top-ps*wait; Tutorial Part 3, 4.9 Wait Operator

### Substate representation

**L4-008** — A substate created by an operator no-change impasse gets ^name equal to the ^name of the superstate's selected operator.

*Rationale:* Lets the operator's implementation be written as rules testing (state <s> ^name <operator-name>).

*If violated:* Rules for the operator's implementation never match

*Example:*

```
(state <s> ^superstate.operator.name <n>) --> (<s> ^name <n>)
```

*Source:* Default: elaborations/_all.soar soar-base*elaborate*state*name; Tutorial Part 3, 3.3 Wander Operator Suboperators; Tutorial Part 3, 3.4 General Rule Summary

### Input/output link

**L4-009** — A substate that issues input or output needs ^io. soar-base copies the superstate's ^io into no-change substates; agent-world copies it into every substate except selection states and states under evaluate-operator (L15-007).

*Rationale:* Operator implementations in substates can act directly.

*Example:*

```
sp {elaborate*state*io (state <s> ^superstate.io <io>) --> (<s> ^io <io>)}
```

*Source:* Default: soar-base/simple.soar soar-base*elaborate*default*state*io; Tutorial Part 3, 3.3 Wander Operator Suboperators; Tutorial Part 3, 3.4 General Rule Summary

## L5 Selection space (classic)

Conventions of the classic selection space that selection-world keeps.

### State representation

**L5-004** — A derived (i-supported) attribute is excluded from state copying, so that the copy derives it again and does not hold a stale value. Under the world conventions the exclusion list is ^dont-copy-object-attribute on the problem space (L14-026).

*Rationale:* Copied derived values would be o-supported-like stale facts in the copy.

*If violated:* Stale derived values in look-ahead

*Example:*

```
(<p> ^dont-copy free)
```

*Source:* Water Jug originals; default selection copy rules

### Goal/desired representation

**L5-008** — A state signals achievement of its goal with an elaboration (<s> ^success <ds>), or ^required-success or ^partial-success, where <ds> is the state's ^desireds. It signals failure with ^failure, ^partial-failure or ^prohibit-failure <ds>. In look-ahead these replace halting. L14-027 lists every evaluation value.

*Rationale:* The library turns these state attributes into evaluations and preferences.

*If violated:* Look-ahead never sees success

*Example:*

```
(state <s> ^desired <d> ...) --> (<s> ^success <d>)
```

*Source:* Default selection: selection-world*apply*evaluate-operator*symbolic-evaluation*from-subgoal; Tutorial Part 5, 1.4.4 Evaluating the result; Tutorial Part 5, 2.1.3 Modify goal detection; Tutorial Part 5, 2.1.4 Modify failure detection

### Rule: state elaboration

**L5-013** — Rules that evaluate a look-ahead state (success, failure, duplicate tests) test ^tried-tied-operator, so that they apply only after the evaluated operator has been applied in the evaluation state. This does not work for an operator applied by a sequence of rule firings.

*Rationale:* Before that, the copy equals its parent and would be judged a duplicate.

*If violated:* Every look-ahead fails immediately

*Example:*

```
(state <s> ^tried-tied-operator <o> ...)
```

*Source:* Default selection: evaluate-operator*elaborate*state*tried-tied-operator; Water Jug originals; Tutorial Part 5, 1.4.4 Evaluating the result; Tutorial Part 5, 2.3 Numeric Evaluations

### Rule: operator proposal

**L5-014** — To have look-ahead decide among task operators, their proposals create only the acceptable preference: no indifferent or other preference that settles the choice. The operators then tie, and the tie impasse creates the selection substate.

*Rationale:* The selection space is entered only through a tie impasse.

*If violated:* Random selection; planning never invoked

*Example:*

```
(<s> ^operator <o> +)
```

*Source:* Tutorial Part 5, 1. The Water Jug Problem; Tutorial Part 5, 2.1 Conversion to Planning and Learning

**L5-015** — In a selection state, evaluate-operator is proposed for each tied ^item that has no evaluation with ^value true, with ^super-operator <item>. It stays selected until its evaluation has a value.

*Rationale:* Exactly one evaluation is made per tied operator, and its order rarely matters.

*If violated:* Repeated or missing evaluations

*Example:*

```
(state <s> ^name selection ^item <i>) -{(<s> ^evaluation <e>) (<e> ^super-operator <i> ^value true)}
```

*See:* related L14-020

*Source:* Tutorial Part 5, 1.3 Selection Operator Proposal; selection-world/Operator_Tie/evaluate-operator.soar (selection*propose*evaluate-operator)

### Rule: operator application

**L5-017** — An operator whose real effect comes from an external environment also has an internal application rule that applies it in the evaluation state, so that look-ahead can predict its effect (L10-007).

*Rationale:* In the look-ahead copy, nothing from the world changes the state.

*If violated:* Look-ahead state never changes; operator no-change

*Source:* Tutorial Part 5, 1.4.3 Applying the selected operator

### Rule: impasse/substate handling

**L5-018** — In look-ahead, an evaluation state in which no operator can be selected, or in which a constraint-failure impasse arises, counts as a failure of the evaluated operator (L14-037, L14-039). Tasks do not add their own handlers for these cases.

*Rationale:* The library already turns them into failure evaluations.

*If violated:* Double handling

*Source:* Default selection: selection-world*apply*evaluate-operator*evaluation*failure*no-operators, *constraint-failure

### Substate representation

**L5-019** — A tie or conflict substate (^choices multiple) is named selection by a default rule. Its ^item values are the candidate operators. Selection-space rules test ^name selection, not the impasse type.

*Rationale:* All selection rules test ^name selection.

*Example:*

```
(state <s> ^name selection ^item <i>)
```

*Source:* Default selection: selection-world*elaborate*selection*name*selection; Tutorial Part 5, 1.2 Selection Initial State Creation

### Learning: chunking

**L5-021** — When look-ahead results are to be learned, chunking is enabled explicitly: chunk always, chunk only with force-learn on the selection states, or chunk all-except with dont-learn on the states that must not learn.

*Rationale:* Without chunking each result is used only locally and forgotten.

*If violated:* Excessive decisions; repeated search

*Example:*

```
chunk always
# or: chunk only, with force-learn on the selection states
# or: chunk all-except, with dont-learn on the other states
```

*Source:* Tutorial Part 5, 1.4.5 Chunking

## L6 Program organization

Library conventions for naming, files, flags and constants.

### Naming and files

**L6-001** — A program loads the shared library by sourcing soar-library.soar from the library folder (pushd, source, popd), then its task rules. soar-library.soar loads soar-base, selection-world, agent-world and object-world, in that order; Thor-Soar agents also source thor.soar.

*Rationale:* The conventions are implemented by the library, not by each task.

*If violated:* none of the bookkeeping (world, desireds counts, preconditions) exists

*Library rules:* all agent-world rules

*Source:* agent-world/_readme.soar; agent-world_source.soar

**L6-002** — Every library rule is flagged :default; task rules are not.

*Rationale:* Distinguishes library from task knowledge (chunking treats :default rules specially, and traces can hide library rules).

*If violated:* library/task boundary unclear

*Source:* agent-world/elaborations/*.soar (all rules flagged :default except three)

**L6-003** — Rules that belong to a problem space test ^problem-space.name, not the state's ^name.

*Rationale:* Problem space determines which operators are available in a state.

*If violated:* no operators proposed

*Task supplies:* yes

*Library rules:* elaborations/problem-space.soar (requires ^problem-space)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Problem-space"

**L6-004** — An operator attribute must not have the name of a state attribute the library uses (^world, ^io, ^flags, ^real, ^problem-space, ^top-state, ^scene, ^type, ^success, ^failure, ^path-cost and the like): every operator attribute is copied onto the operator's no-change substate (L15-009).

*Rationale:* elaborate*substate*super-operator*attributes copies all operator attributes blindly.

*If violated:* substate gets spurious multi-valued state attributes and library rules mis-match

*Task supplies:* yes

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*substate*super-operator*attributes

**L6-005** — Task rules must not use the operator names agent-world and object-world reserve: wait, skip-wait, dispatch-agent-event-idle, goal-completed, clean-up-topstate, initialize-agent-world, next-desireds, find-object, find-object-direct, failed-grounding, assume-successful-grounding, cutoff-search, finish-future-event.

*Rationale:* Library rules key on these names.

*If violated:* library rules fire on task operators

*Task supplies:* yes

*Source:* all files of this assignment

**L6-006** — A library rule is named <library>*<function>*<state-or-operator>[*detail], with the library name (soar-base, selection-world, agent-world, object-world) as prefix and function one of propose, apply, compare, elaborate.

*Source:* all files of this assignment

### Flags and constants

**L6-007** — Flags read by agent-world: mea-operator-selection, desired-preferences, gps-desired-ordering, cost-metric (none, unit, time), min-step-cost, cost-weight, heuristic-weight, rl, smem-store, explore, agent-mode (testing), desireds-source (language, elaboration).

*Task supplies:* yes

*Library rules:* agent-world*elaborate*substate*flags

*Source:* agent-world/force-conflict.soar; agent-world/goal-completed.soar; agent-world/goal-completed/clean-up-topstate.soar; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar; elaborations/_all.soar:agent-world*elaborate*substate*flags; Thor-Soar Agent Documentation (thor.txt) 'Flags'

**L6-008** — The library creates ^flags on the top state and fills it with each project's defaults (:default rules in the _flags.soar files). A task changes a flag only by putting it under ^flag-override on the top state; it never writes ^flags. The same ^flags identifier is shared with every substate, including evaluate-operator states, and is never changed there.

*Rationale:* All ID mode switches are read as ^flags.<x> on selection and evaluate-operator states.

*If violated:* no depth initialised and no depth elaborated: search unbounded

*Task supplies:* yes

*Library rules:* agent-world*elaborate*substate*flags

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*flags ('the flags should not be changed in substates')

### Other

**L6-009** — agent-world sets Soar parameters for the whole agent: max-goal-depth 50, max-elaborations 100, max-nil-output-cycles 100, srand 1, epsilon-greedy indifferent selection, working-memory activation off, and production optimize-attribute hints for multi-valued attributes (object, on, in, attend, desired and others).

*Rationale:* Search depth, determinism and matching efficiency assumptions of the library.

*If violated:* task overriding these changes look-ahead depth or reproducibility

*Source:* agent-world/_flags.soar

## L7 World state

The world representation every agent-world program shares: ^world, objects and relations.

### World/state

**L7-001** — The library proposes initialize-agent-world (acceptable and best) on the top state while the top state has no ^world (the proposal tests -^world). It carries ^task-operator false.

*Rationale:* The library's initialization must run first to create the world/scene/attends skeleton.

*If violated:* library structures never created, or both init operators tie

*Library rules:* agent-world*propose*initialize-agent-world

*Source:* agent-world/initialize-agent-world.soar:agent-world*propose*initialize-agent-world

**L7-002** — The application of initialize-agent-world creates on the top state: ^top-state and ^external-top-state (the state itself), ^real true, ^world (with ^objects, ^real true, ^self, ^anchored-world true), ^scene.objects, ^attends, ^super-desireds, ^smem-storage-structure.initial-in-relations and ^quiescence t.

*Rationale:* Fixed skeleton other library rules rely on.

*If violated:* library rules fail to match

*Library rules:* agent-world*apply*init-agent-world

*Source:* agent-world/initialize-agent-world.soar:agent-world*apply*init-agent-world

**L7-003** — Every substate shares its superstate's ^world identifier (the same object, not a copy), except selection states, states named no-task-operator, and states under evaluate-operator. An operator no-change substate therefore acts on the same world as its superstate.

*Rationale:* Operator subgoaling works on the real world; only look-ahead copies it.

*Library rules:* agent-world*elaborate*substate*world

*See:* related L15-007 (overlap)

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*world

**L7-004** — ^real true marks a state that deals with the real situation: the top state and its substates, except states named selection or evaluate-operator. A look-ahead state has ^real false. Rules that must act only on the real situation (goal-completed, skip-wait, constraint-failure messages) test ^real true.

*Rationale:* Distinguish real from hypothetical reasoning; overlaps ^external-top-state.

*Library rules:* agent-world*elaborate*real

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*real

**L7-005** — A world is the value of ^world on a state. It holds only the task situation: objects (^objects.object), relation objects, and a few other attributes (^time, ^future-event, ^abstract-property, ^info, ^path-cost). State-control structure is not part of the world.

*Rationale:* The world is the problem-space state that look-ahead copies and evaluates.

*If violated:* control info copied or lost in look-ahead

*Task supplies:* yes

*Source:* agent-world/initialize-agent-world.soar; Thor-Soar Agent Documentation (thor.txt) 'World'

**L7-006** — A world's kind is given by ^real and ^anchored-world: the real world (^real true ^anchored-world true), a look-ahead copy (^anchored-world true, no ^real true), and a world-context world (^anchored-world false).

*Rationale:* Rules must know whether a world is the real one, hypothetical, or a set of grounding constraints.

*If violated:* rules ground desireds against constraint worlds or act on hypothetical worlds

*Library rules:* agent-world*apply*init-agent-world; object-world*elaborate*world-context*anchored-false

*Source:* agent-world/initialize-agent-world.soar; elaborations/world-context.soar; Thor-Soar Agent Documentation (thor.txt) 'World'

**L7-007** — A rule that grounds a desired in the world, or acts on the world, tests ^anchored-world true: a state can have several ^world values (the anchored world and world-context worlds).

*Rationale:* Multiple ^world augmentations coexist on a state.

*If violated:* matches against ungrounded constraint objects

*Task supplies:* yes

*Library rules:* object-world*elaborate*world-from-scene*attended-object

*Source:* agent-world/elaborations/world-context.soar; world-from-scene.soar; Thor-Soar Agent Documentation (thor.txt) clean-object proposal

**L7-008** — Every state in which task operators are proposed or applied has ^problem-space with ^name. The task supplies it for the top state, for MEA substates and for look-ahead states (L15-017); the library creates it only for operator-implementation substates (L9-022).

*Rationale:* find-object, future-event locking and the derivation of ^internal-actions all depend on ^problem-space.

*If violated:* these capacities silently do not fire

*Example:*

```
(<s> ^problem-space <ps>) (<ps> ^name thor-world ^agent-world true)
```

*Task supplies:* yes

*See:* related L9-022 (overlap)

*Source:* agent-world/_readme.soar; object-world (find-object); agent-world/events/elaborations/future-event.soar; agent-world/generic-operator/elaborations.soar

**L7-009** — ^top-state of the top state, and of each look-ahead (evaluate-operator) state, is the state itself. Every other substate copies ^top-state from its superstate. ^external-top-state always points to the real top state, in look-ahead states too.

*Rationale:* Rules that should run only on 'the world being modelled' test ^top-state <s>.

*Example:*

```
(state <s> ^world <w> ^top-state <s>)
```

*Library rules:* elaborate*substate*top-state, agent-world*elaborate*substate*external-top-state

*See:* related L15-006 (overlap)

*Source:* initialize-agent-world.soar; elaborations/_all.soar; problem-space.soar:selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*evaluate-operator*external-top-state

**L7-010** — The task supplies an operator initialize-<task>, proposed (acceptable and best) on the top state once ^world exists and the state has no ^name. Its application creates the top state's ^name, the task's ^desireds, and the world's objects and relations; adding ^name retracts its proposal. The order of selection is therefore initialize-agent-world, then initialize-<task>. It carries ^task-operator false.

*Rationale:* Sequences library initialization before task initialization so the world, scene and attends skeleton exists when the task fills it.

*If violated:* task structures built on a missing world, or the two initialization operators tie

*Example:*

```
sp {thor-soar*propose*initialize-thor-soar (state <s> ^superstate nil ^world <world> -^name thor-soar) --> (<s> ^operator <op> + >) (<op> ^name initialize-thor-soar)}  sp {apply*initialize-thor-soar*thor-soar (state <s> ^operator.name initialize-thor-soar ^io.input-link <input> ^scene <scene>) (<input> ^room-name <room-name> ^scene-name <scene-name>) --> (<s> ^name thor-soar) (<scene> ^room-name <room-name> ^scene-name <scene-name>)}
```

*Task supplies:* yes

*See:* related L7-001 (sequence)

*Source:* JEL, 12 Nov 2026; Thor-Soar propose*initialize-thor-soar and apply*initialize-thor-soar*thor-soar; agent-world/initialize-agent-world.soar

**L7-011** — A task states whether it has an external environment. A task with none (every operator applied internally, nothing written to the output-link) puts ^environment none on the top state in initialize-<task>. A task with an external environment does not create ^environment.

*Rationale:* Lets the library decide internal versus external application of task operators from one declared fact.

*If violated:* a no-environment task never applies internally on its top state (operator no-change after the first task operator)

*Example:*

```
(<s> ^name zebra ^environment none)
```

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026; zebra and kenken (direct-world) programs

### Objects

**L7-012** — Every object in an anchored world has ^anchored true and ^object-handle; the library's achievement tests match only such objects.

*Rationale:* Operator-desired achievement rules match only world objects with ^anchored true.

*If violated:* operator preconditions never satisfied

*Task supplies:* yes

*Library rules:* agent-world*apply*operator*acheived-desired*handle; ...*anchored-only

*Source:* agent-world/elaborations/achieved-desired-operators.soar:agent-world*apply*operator*acheived-desired*handle; achieved-desireds.soar:unachieved rules

**L7-013** — ^object-handle is the unique constant that names an object. Desireds, attends, world-context and output commands refer to objects only by handle, never by identifier; objects, relations and desireds are matched between the real world and its copies by handle.

*Rationale:* Desireds and look-ahead copies have different identifiers than world objects.

*If violated:* desireds cannot be grounded

*Task supplies:* yes

*Library rules:* all achievement rules

*Source:* Thor-Soar Agent Documentation (thor.txt) "Objects.object" and "Desireds"; agent-world/achieved-desired-operators.soar

**L7-014** — An object derived from another (for example a slice) has ^origin-object-handle naming the original. Rules that match a desired's handle to a world object therefore test ^<< object-handle origin-object-handle >>.

*Rationale:* A desired may name an object that will only exist after transformation.

*If violated:* desireds on derived objects never achieved

*Task supplies:* yes

*Library rules:* agent-world*elaborate*state*unachieved-desired-origin

*Source:* Thor-Soar Agent Documentation (thor.txt) "Objects.object", clean-object proposal; agent-world/achieved-desireds.soar:agent-world*elaborate*state*unachieved-desired-origin

**L7-015** — Every attribute of a world object has a constant value (a symbol or a number), never an identifier. A structured value is flattened into constant attributes or held as a separate world object referred to by handle. This does not apply to relation objects, ^holding-object, ^future-event or ^self, which the library copies and re-links by handle.

*Rationale:* The look-ahead copy copies attribute values unchanged, so an identifier value in the copy points into the real world.

*If violated:* look-ahead reads or changes real-world structure through the link; wrong evaluations

*Example:*

```
(<c> ^object-handle c11 ^cand v111) not (<c> ^cand <cand-object>)
```

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (decision on LF-21); selection-world selection-world*elaborate*evaluate-operator*default-state-copy-object-attributes; kenken direct-world NOTES

### Relations

**L7-016** — A relation is a relation object on the world: (<w> ^<relation> <r>) with (<r> ^argument1 <object> ^argument2 <object>), one object per fact; a one-argument relation has only ^argument1. In a look-ahead copy the relation object also has ^duplicate-of. A relation is never represented as an attribute of one object that points to the other.

*Rationale:* Uniform relation representation for MEA and look-ahead copying. A relation is an explicit object that points to its arguments, so chunks and RL rules test the relation object and the objects it points to and generalize over which objects are related; a numeric code for an argument or a fixed link would make learned rules specific to values.

*If violated:* relation desireds never matched

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "World"

## L8 Desireds

How goals are represented as desireds, and the library's bookkeeping for them.

### Desireds

**L8-001** — A state's goal is ^desireds <ds>: one or more ^desired structures, all of which must be achieved (a conjunction), with ^desired-count. Success and failure are signalled on the state as ^success <ds>, ^failure <ds> and the like, where <ds> is the state's own ^desireds.

*Rationale:* Uniform goal representation used by MEA, look-ahead and halting.

*If violated:* no goal detection

*Task supplies:* yes

*Library rules:* achieved-desireds.soar count rules

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds"

**L8-002** — The task creates the top state's ^desireds (from interaction with the outside world, or in Thor by elaborations chosen by ^flags.desired-selection).

*Rationale:* The library never creates task goals.

*If violated:* agent has nothing to do

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds"; agent-world/initialize-agent-world.soar (creates none)

**L8-003** — Every desireds structure has ^desired-count equal to its number of ^desired, set when the structure is created. The library never computes it.

*Rationale:* Count rules compare achieved counts to desired-count.

*If violated:* success/preconditions never detected or detected early

*Example:*

```
(<desireds> ^desired <d1> <d2> ^desired-count 2)
```

*Task supplies:* yes

*Library rules:* all desired-count rules

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^desired-count; agent-world/achieved-desireds.soar, achieved-desired-operators.soar

**L8-004** — A desireds structure has at most 6 ^desired: the library's counting rules cover ^desired-count 0 to 6, and for 6 only the case in which all are achieved.

*Rationale:* Counting is done by enumerated rules, not arithmetic.

*If violated:* no counts, no success, no pre-conditions-satisfied

*Task supplies:* yes

*Library rules:* count rules

*Source:* agent-world/elaborations/achieved-desireds.soar; achieved-desired-operators.soar

**L8-005** — Each ^desired states exactly one relation or one property of one object. Several properties are never combined in one desired.

*Rationale:* Library achievement rules mark a desired achieved when any one non-handle attribute matches, so multiple properties behave as a disjunction.

*If violated:* desired reported achieved when only one property holds

*Task supplies:* yes

*Library rules:* agent-world*apply*operator*acheived-desired*handle

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^desired, ^object; agent-world/achieved-desired-operators.soar:...*acheived-desired*handle

**L8-006** — An object desired, (<d> ^object <o>), is a partial description: ^object-handle and the one property to achieve (for example ^sliced true). <o> is never the identifier of a world object.

*Rationale:* Desireds describe changes and link to world by handle.

*If violated:* goal structures confused with state; look-ahead copies break

*Example:*

```
(<d> ^object <o>) (<o> ^object-handle Potato50 ^sliced true)
```

*Task supplies:* yes

*Library rules:* agent-world*apply*operator*acheived-desired*handle

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^object; clean-object proposal discussion

**L8-007** — In a desired object the attributes object-handle, duplicate-of, anchored and origin-object-handle are bookkeeping; every other attribute is the property to achieve.

*Rationale:* Achievement rules use a variable attribute excluding these.

*If violated:* bookkeeping attributes treated as goal properties

*Library rules:* achievement rules

*Source:* agent-world/elaborations/achieved-desireds.soar, achieved-desired-operators.soar

**L8-008** — A desired object with only ^object-handle and ^anchored true means that the object must be grounded; it is achieved when an anchored world object has that handle.

*Rationale:* Expresses grounding preconditions.

*Library rules:* same

*See:* related L13-006 (overlap)

*Source:* agent-world/elaborations/achieved-desired-operators.soar:agent-world*apply*operator*acheived-desired*handle*anchored-only

**L8-009** — A relation desired, (<d> ^<relation> <r>), has only ^argument1.object-handle and ^argument2.object-handle. Further constraints on the arguments go in separate object desireds with the same handle, or in ^world-context.

*Rationale:* Relation desireds are matched by handle against world relations.

*If violated:* relation desireds cannot be achieved/grounded

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^in/on

**L8-010** — When the specific object is not known, a desired uses a placeholder object-handle, and ^desireds.world-context (shaped like a world: ^objects.object with the same placeholder handle and the constraining properties) constrains how the placeholder is grounded.

*Rationale:* Delay grounding until needed.

*If violated:* ungroundable desireds

*Example:*

```
(<desireds> ^desired.holding-object.object-handle |unanchored-object-egg-handle| ^world-context.objects.object <e>)(<e> ^class egg ^object-handle |unanchored-object-egg-handle| ^anchored false)
```

*Task supplies:* yes

*Library rules:* object-world*elaborate*world-context*world

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^world-context

**L8-011** — When a state's ^desireds, or its selected operator's ^desireds, has ^world-context <wc>, the library adds (<s> ^world <wc>) and marks <wc> ^anchored-world false, so that rules can match the ungrounded structure.

*Rationale:* World-context is treated as a constraint world.

*Library rules:* object-world*elaborate*create-world-from*desired-world-context; object-world*elaborate*world-context*world; ...*anchored-false

*Source:* agent-world/elaborations/world-context.soar (all 4 rules)

**L8-012** — Two desireds are alternatives (a disjunction) when each has ^disjunction pointing to the other. When one is achieved the library marks the other achieved.

*Rationale:* Either alternative satisfies the conjunction.

*Task supplies:* yes

*Library rules:* agent-world*elaborate*state*achieved-desired*disjunction

*Source:* Thor-Soar Agent Documentation (thor.txt) "Disjunction"; agent-world/achieved-desireds.soar:agent-world*elaborate*state*achieved-desired*disjunction

**L8-013** — ^next-desireds <ds2> on a desireds structure names the goal set to pursue after every current desired is achieved (strict sequence).

*Rationale:* Represents step-by-step procedures.

*Task supplies:* yes

*Library rules:* Thor next-desireds operator; agent-world*elaborate*operator*acheived-all-next-desireds

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^next-desireds; cCTO section

**L8-014** — Other desired kinds handled by the library: ^info.unanchored-object.object-handle (achieved when world.info has the same unanchored-object and an ^anchored-object), ^learn task-goal ^task (achieved by ^events.learning-event of that type/task), and ^executed-action.action-handle (achieved by ^events.executed-action with that handle).

*Rationale:* Knowledge, learning and action goals.

*Library rules:* listed rules

*Source:* agent-world/elaborations/achieved-desireds.soar (info, learn, executed-action rules); achieved-desired-operators.soar:...*info

**L8-015** — ^super-desireds on a state accumulates every ^desired of that state's ^desireds and of all superstates' ^super-desireds; it is created in operator substates (^attribute operator, i.e. ties and no-changes) except under evaluate-operator.

*Rationale:* Lets substates know all goals being pursued above.

*Library rules:* agent-world*elaborate*super-desireds*substate*super-desireds*desired; agent-world*elaborate*super-desireds*substate*desired

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*super-desireds; super-desireds.soar

**L8-016** — A desired uses only the forms the look-ahead copy preserves: ^object, ^holding-object, a relation with ^argument1.object-handle and ^argument2.object-handle, ^selection-value, ^learn, ^executed-action, ^info and ^disjunction. Any other desired attribute is absent from look-ahead desireds.

*Rationale:* Only these are copied into the look-ahead desireds.

*If violated:* look-ahead evaluates against a different goal than the real one

*Task supplies:* yes

*See:* related L15-015 (overlap)

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*copy-desired*

### Desireds bookkeeping

**L8-017** — ^world.abstract-property <attr> declares an object attribute that is abstracted away: a state desired whose object specifies <attr> counts as achieved, and <attr> is ignored when unachieved desireds are computed.

*Rationale:* Supports abstraction (usually reachable) to shorten planning.

*Task supplies:* yes

*Library rules:* same

*Source:* agent-world/elaborations/achieved-desireds.soar:agent-world*elaborate*state*achieved-desired*abstract-property, ...*unachieved-desired*abstract-property

**L8-018** — The library does not compute whether object-property and relation desireds of a state are achieved. The task supplies i-supported elaborations that add (<desireds> ^achieved <d>) and (<desireds> ^unachieved <d>); the library computes the counts and ^success from them (L8-023, L8-025).

*Rationale:* Library only handles operator object-property desireds, disjunction, abstract properties, origin handles, info/learn/action desireds.

*If violated:* goals never achieved; MEA proposes nothing

*Task supplies:* yes

*Source:* agent-world/elaborations/achieved-desireds.soar (no general rule); Thor-Soar Agent Documentation (thor.txt) 'Other Innate Task Knowledge'

**L8-019** — ^achieved <d> and ^unachieved <d> on a desireds structure are i-supported, and every desired is in exactly one of the two at any time.

*Rationale:* Counts and MEA proposals depend on them.

*If violated:* wrong counts; operators proposed for achieved desireds

*Task supplies:* yes

*Library rules:* achieved-desireds.soar; achieved-desired-operators.soar

*See:* related L8-021 (overlap)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^achieved

**L8-020** — ^unachieved is a positive WME, so that proposals and chunks test ^unachieved <d> and not a negation.

*Rationale:* Avoid negated conditions in chunks.

*If violated:* overgeneral chunks

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^unachieved

**L8-021** — For an operator's desireds, the library's achieved rules also create an i-supported reject of ^unachieved <d>, which suppresses a task-created ^unachieved while the achieved condition holds.

*Rationale:* Prevents simultaneous achieved/unachieved on operator preconditions.

*Library rules:* agent-world*apply*operator*acheived-desired*handle etc.

*See:* related L1-012 (overlap); L8-019 (overlap)

*Source:* agent-world/elaborations/achieved-desired-operators.soar (all achieved rules); verified in Soar 9.6.5 that an i-supported reject suppresses an i-supported WME

**L8-022** — An object-property desired of an operator is achieved when an anchored world object with the same handle has the same attribute and value. If partial counts are needed, the task supplies the operator's ^unachieved.

*Rationale:* Library gives achieved; counts with unachieved need ^unachieved.

*If violated:* missing ^unachieved-desireds-count for partially satisfied operators

*Task supplies:* yes

*Library rules:* agent-world*apply*operator*acheived-desired*handle

*Source:* agent-world/elaborations/achieved-desired-operators.soar

**L8-023** — The library computes ^achieved-desireds-count and ^unachieved-desireds-count on every desireds structure (of a state or of a proposed operator) from ^achieved, ^unachieved and ^desired-count.

*Rationale:* Used for success and precondition tests.

*Library rules:* count rules

*Source:* agent-world/elaborations/achieved-desireds.soar, achieved-desired-operators.soar count rules

**L8-024** — A state's desireds structure has ^unachieved-desireds true while any ^unachieved exists.

*Rationale:* Simple flag for 'goal not met'.

*Library rules:* same

*Source:* agent-world/elaborations/achieved-desireds.soar:agent-world*elaborate*unachieved-desireds-true

**L8-025** — When every desired of a state's ^desireds is achieved, the library adds (<s> ^success <desireds>) to that state. This holds for the top state, operator substates and look-ahead states.

*Rationale:* Uniform success signal: halts at top, ends look-ahead, signals preconditions in operator substates.

*Library rules:* count rules

*Source:* agent-world/elaborations/achieved-desireds.soar:...*desired-count<N>*achieved-<N>; Thor-Soar Agent Documentation (thor.txt) 'Desireds'

## L9 Operators

Task, composite and non-task operators.

### Task operators

**L9-001** — Every operator has ^task-operator true or ^task-operator false. Task operators (those that change the task situation and that look-ahead compares) have true; initialization and other internal operators have false. A few library operators carry neither (L13-002).

*Rationale:* Library search control prefers non-task operators over task operators and look-ahead treats task operators specially.

*If violated:* internal operators compete with task operators; ties

*Task supplies:* yes

*Library rules:* agent-world*compare*task-operator-non-task-operator

*See:* related L9-023 (overlap)

*Source:* agent-world/elaborations/search-control.soar:agent-world*compare*task-operator-non-task-operator; initialize-agent-world.soar

**L9-002** — When every desired of an operator's ^desireds is achieved and the structure has ^next-desireds, the library replaces the operator's ^desireds with the next set.

*Rationale:* Sequential preconditions.

*Library rules:* same

*See:* related L9-024 (overlap)

*Source:* agent-world/elaborations/achieved-desired-operators.soar:agent-world*elaborate*operator*acheived-all-next-desireds, *pre-conditions-satisfied

**L9-003** — ^avoid-desired, ^preferred-desired and the related desired preferences affect an operator only if the operator records the desired it serves as ^super-desired, with the same identifier.

*Rationale:* Library search control joins on ^super-desired identity.

*If violated:* preferences silently not created

*Task supplies:* yes

*Library rules:* search-control rules

*Source:* agent-world/elaborations/search-control.soar; Thor-Soar Agent Documentation (thor.txt) '^super-desired'

**L9-004** — A task-action operator (TAO) is proposed as an operator object with ^name, ^task-operator true, ^action-handle <command name>, ^argument1 to ^argumentN (world objects), ^argument-count N, and ^desireds (its preconditions, a desireds structure with ^desired-count). If the proposal's conditions test a desired, the operator records that desired as ^super-desired; a proposal that tests no desired creates no ^super-desired.

*Rationale:* Uniform structure lets generic rules track preconditions, issue output and apply look-ahead bookkeeping.

*If violated:* generic rules cannot apply/monitor the operator

*Example:*

```
(<o> ^name clean-object ^task-operator true ^action-handle clean ^super-desired <d> ^argument1 <obj> ^argument-count 1 ^desireds <p>)(<p> ^desired-count 1 ^desired.object <po>)(<po> ^reachable true ^object-handle <h>)
```

*Task supplies:* yes

*Library rules:* external-operator-application; achieved-desired-operators; monitor-operator

*Source:* Thor-Soar Agent Documentation (thor.txt) "Task Action Operator Working Memory Structure"

**L9-005** — Operator arguments are world objects, each with ^object-handle; an operator has at most 3. An object the action needs but the agent already holds (the knife in slice-object) is a precondition, not an argument. The output command carries each argument's handle, not its identifier.

*Rationale:* Arguments are what the action is applied to.

*Task supplies:* yes

*Library rules:* monitor-operator rules

*Source:* Thor-Soar Agent Documentation (thor.txt) "^argument1"

**L9-006** — An operator's precondition desireds are evaluated while the operator is only proposed (the rules match ^operator <o> +); each is achieved or unachieved at any time and can change back.

*Rationale:* Preconditions known before selection.

*Library rules:* count rules

*Source:* agent-world/elaborations/achieved-desired-operators.soar (all count rules test ^operator <operator> +)

**L9-007** — A proposed operator gets ^pre-conditions-satisfied true (i-supported) when its desireds' achieved count equals ^desired-count, the unachieved count is 0, and the desireds have no ^next-desireds. The generic external application and every internal application rule test it.

*Rationale:* Operators selected via MEA wait (in a substate) until preconditions hold.

*If violated:* action applied before preconditions

*Library rules:* agent-world*elaborate*operator*pre-conditions-satisfied; external-operator-application

*Source:* agent-world/elaborations/achieved-desired-operators.soar:agent-world*elaborate*operator*pre-conditions-satisfied; Thor-Soar Agent Documentation (thor.txt)

**L9-008** — An operator whose ^desireds has ^desired-count 0 gets achieved and unachieved counts of 0, and so has ^pre-conditions-satisfied true at once.

*Rationale:* Allows operators with no preconditions (e.g. only effect-desireds).

*Library rules:* same

*Source:* agent-world/elaborations/achieved-desired-operators.soar:agent-world*elaborate*operator*desired-count0*achieved-0

**L9-009** — A means-ends (MEA) proposal of a task-action operator tests: ^problem-space.name; ^flags.mea-operator-selection true; the anchored world (^anchored-world true) and the object or objects whose handle (or origin handle) the desired names; and (<ds> ^desired <d> ^unachieved <d>) for a desired the operator achieves. Because it tests <d>, it records <d> on the operator as ^super-desired (L9-004).

*Rationale:* Operators are proposed only for unachieved differences.

*If violated:* operators proposed for achieved goals or ungrounded objects

*Example:*

```
(state <s> ^problem-space.name thor-world ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)(<w> ^anchored-world true ^objects.object <obj>)(<ds> ^desired <d> ^unachieved <d>)
```

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Clean-object" proposal and MEA selection notes

**L9-010** — ^argument-count equals the number of ^argument1..^argumentN attributes on the operator. The generic external application rules dispatch on it (0, 1, 2 or 3).

*Rationale:* Each external-application rule tests a literal ^argument-count and the matching ^argumentN attributes.

*If violated:* no external rule matches, so no perform-action is created and the operator stalls

*Example:* ^argument-count 2 ^argument1 <a> ^argument2 <b>

*Task supplies:* yes

*Library rules:* apply*operator*external*argument*

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument0..argument3*no-handle2; Thor-Soar Agent Documentation (thor.txt) '^argument-count'

**L9-011** — Every task-action operator has ^desireds with ^desired-count, also when it has no preconditions (^desired-count 0): ^pre-conditions-satisfied is computed only from that structure.

*Rationale:* Without ^desireds no ^pre-conditions-satisfied is produced and neither external nor internal application fires.

*If violated:* operator is selected but never applied (operator no-change)

*Example:*

```
(<operator> ^desireds <d2>) (<d2> ^desired-count 0)
```

*Task supplies:* yes

*Library rules:* agent-world*elaborate*operator*pre-conditions-satisfied

*Source:* elaborations/achieved-desired-operators.soar:agent-world*elaborate*operator*pre-conditions-satisfied, agent-world*elaborate*operator*desired-count0*achieved-0; Thor-Soar Agent Documentation (thor.txt) '^desireds'

**L9-012** — For each task-action operator the task supplies a proposal and an internal application rule (used in look-ahead, and for every application when ^environment is none). External application is generic and needs no task rule. A second, non-MEA proposal (proposed when the preconditions hold) is allowed but untested.

*Rationale:* This keeps TAOs to two rules; the uniform structure lets agent-world issue the action.

*If violated:* operator cannot be simulated in look-ahead or never proposed

*Example:*

```
sp {apply*clean-object*internal (state <s> ^operator <o> ^internal-actions true) (<o> ^name clean-object ^argument1 <obj> ^pre-conditions-satisfied true) (<obj> ^dirty true) --> (<obj> ^dirty true - false)}
```

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'Innate Task-Action Operators', 'Task Operator Rules', 'Internal Application'

**L9-013** — A means-ends task-action operator ends when its ^super-desired becomes achieved: its proposal tests ^unachieved <d> and retracts. For a real action this happens when perception updates the world.

*Rationale:* Selection persists across MEA substates until the purpose of the operator is achieved.

*Source:* Thor-Soar Agent Documentation (thor.txt) 'MEA selection' (^unachieved bullet); agent-world/external-operator-application.soar

**L9-014** — A task-action operator's proposal creates only the acceptable preference. Selection among task operators is left to the library's search control and to look-ahead.

*Rationale:* Ties between task operators are what trigger look-ahead planning.

*If violated:* look-ahead never runs, or the task hard-codes choices

*Example:*

```
(<s> ^operator <operator> +)
```

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) clean-object proposal

**L9-015** — A task-action operator has ^action-handle or ^actions, never both: each has its own output rule, and two perform-action commands would be issued.

*Rationale:* Both apply*operator*create-action-command and apply*operator*external* match a task operator.

*If violated:* duplicate commands to the environment

*Task supplies:* yes

*Source:* agent-world/elaborations/output.soar:apply*operator*create-action-command; agent-world/external-operator-application.soar

### Composite operators

**L9-016** — A simple composite task operator (sCTO) is a proposal only: its ^desireds preconditions are achieved by other operators through means-ends subgoaling. It has no output action and no internal application rule.

*Rationale:* Composition entirely through preconditions; achieving them is what implements the operator (e.g. discard, store); learnable by ITL.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Simple Composite Task Operators"

**L9-017** — A complex composite task operator (cCTO) has the structure of an sCTO plus ^effect-desireds <ed>, a desireds structure (^desired, ^desired-count, optionally ^next-desireds and disjunctions). When every precondition is satisfied, <ed> becomes the ^desireds of the operator-implementation substate, where task-action and composite operators achieve it.

*Rationale:* Separates preconditions from effects; supports sequencing, disjunction and temporal extent.

*If violated:* cCTO never implemented

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Complex Composite Task Operators"

**L9-018** — A composite operator needs no internal application rule for look-ahead: its implementation ends in task-action operators, which have them.

*Rationale:* Look-ahead expands them via substates.

*Source:* Thor-Soar Agent Documentation (thor.txt) "Complex Composite Task Operators"

**L9-019** — The problem space agent-world creates for an operator-implementation substate has only ^name <operator-name>. It needs nothing more for find-object or future-event locking inside that substate: no library rule tests ^problem-space.agent-world true (deprecated, P-006).

*Rationale:* Earlier versions tested ^problem-space.agent-world true; since P-006 grounding and locking apply in every state that has the world structure.

*If violated:* A task that adds ^agent-world true to the substate's problem space adds an attribute nothing reads.

*Task supplies:* no

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*operator-implementation-substate*super-operator-problem-space

**L9-020** — An sCTO has no application, so its precondition desireds must together entail its ^super-desired: the proposal then retracts as soon as the preconditions are satisfied.

*Rationale:* Otherwise, once ^pre-conditions-satisfied true holds nothing changes the state.

*If violated:* operator no-change impasse after the preconditions are achieved

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'sCTO' (inferred from 'do not have internal implementation rules')

**L9-021** — In the operator-implementation substate of an operator with ^pre-conditions-satisfied true and ^effect-desireds <ed>, agent-world makes <ed> itself (the same identifier) the substate's ^desireds and adds ^better lower to it.

*Rationale:* Reuses all desireds machinery for the effects; ^better lower makes look-ahead minimise time.

*Example:*

```
(<s> ^desireds <effect-desireds>) (<effect-desireds> ^better lower)
```

*Library rules:* agent-world*elaborate*operator-implementation-substate*super-operator-desireds

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*operator-implementation-substate*super-operator-desireds

**L9-022** — In an operator-implementation substate agent-world creates ^problem-space.name <operator-name>; implementation operators are proposed by testing that problem-space name.

*Rationale:* Gives the substate its own operator space.

*If violated:* implementation operators leak into other substates

*Example:*

```
(state <s> ^problem-space.name cook-microwave ...)
```

*Task supplies:* yes

*Library rules:* agent-world*elaborate*operator-implementation-substate*super-operator-problem-space

*See:* related L7-008 (overlap)

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*operator-implementation-substate*super-operator-problem-space

### Non-task operators

**L9-023** — An internal (non-task) operator performs internal reasoning only, issues no output command, and has ^task-operator false. Examples: initialize-<task>, next-desireds, attend-object.

*Rationale:* Internal bookkeeping operators are preferred over task operators.

*Task supplies:* yes

*Library rules:* agent-world*compare*task-operator-non-task-operator

*See:* related L9-001; L15-001

*Source:* Thor-Soar Agent Documentation (thor.txt) "Non-Task Operators"; agent-world/search-control.soar

**L9-024** — When a state's desireds have ^success and ^next-desireds, the operator next-desireds makes the next set the state's current desireds.

*Rationale:* Sequenced goals.

*See:* related L9-002 (overlap)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Next-desireds"

**L9-025** — In a state no-change substate (^attribute state ^choices none) agent-world proposes wait with a worst preference, and proposes it again after each selection (the proposal tests -^operator.name wait); every other operator is better than wait. Planned exception (not in library v2.41, which still proposes wait there): no wait or other idle operator is proposed in a state no-change below an evaluate-operator substate (look-ahead), where the state no-change means the evaluated operator fails (L14-039).

*Rationale:* An idle agent waits in one substate instead of stacking impasses.

*Example:*

```
(<s> ^operator <o> + <) (<o> ^name wait)
```

*Library rules:* agent-world*propose*state-no-change*wait, agent-world*compare*prefer*other*over*wait

*Source:* agent-world/Impasse__State_No-Change/wait.soar:agent-world*propose*state-no-change*wait, agent-world*compare*prefer*other*over*wait

## L10 Application and output

Internal and external operator application, output commands and events.

### Operator application (internal/external)

**L10-001** — Every operator application writes a log line, (log 1 ...): under means-ends subgoaling an operator may apply many decisions after it was selected.

*Rationale:* Traceability.

*If violated:* hard to debug

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Internal Application" actions

**L10-002** — External application is generic. When a task operator with ^action-handle is selected, has ^pre-conditions-satisfied true, and the state has ^internal-actions false (not every rule tests it, L10-006), library rules create (<output-link> ^perform-action <p>) with ^name <action-handle> and the argument handles. Task operators need no external application rules (in Thor, go-to, turn-on, turn-off and look-at are exceptions).

*Rationale:* Uniform output.

*Library rules:* external-operator-application.soar

*Source:* Thor-Soar Agent Documentation (thor.txt) "Task Operator Rules", "Go-to"; agent-world/_readme.soar; external-operator-application.soar

**L10-003** — The library elaborates ^internal-actions on every state: true in evaluate-operator states and in every state below a state that has it true, and false elsewhere (but see L10-009). External application rules test ^internal-actions false; internal application rules test ^internal-actions true.

*Rationale:* Selects between simulated and real application.

*Library rules:* agent-world*elaborate*problem-space*internal, *internal*evaluate-operator, *internal*true, *internal*state

*See:* related L10-009 (overlap)

*Source:* agent-world/elaborations/problem-space.soar (all 4 rules)

**L10-004** — An operator argument without ^object-handle (a time or another non-object parameter) is passed to the output command unchanged.

*Rationale:* Lets actions take non-object parameters through the same generic rules.

*Example:*

```
(<perform> ^name <action-handle> ^argument1 <argument1>) where (<argument1> -^object-handle)
```

*Library rules:* apply*operator*external*argument*no-handle*

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument1*no-handle, *argument2*no-handle1, *no-handle2, *no-handle1*no-handle2

**L10-005** — External application rules test ^quiescence t on the state. The top state gets it from initialize-agent-world and impasse substates have it architecturally, so a command is issued only at quiescence and no chunk is built from creating an output command.

*Rationale:* Output created in a substate is a result; testing ^quiescence t stops chunking of actions and waits for elaborations to settle.

*If violated:* without ^quiescence t on the top state no external action fires there

*Example:*

```
(state <s> ^operator <o> ^quiescence t ^internal-actions false ^io.output-link <out>)
```

*Library rules:* agent-world*apply*init-agent-world

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument0 etc.; initialize-agent-world.soar:agent-world*apply*init-agent-world

**L10-006** — Not every external application rule tests ^internal-actions false (the one-argument rules and the turn-on and turn-off rules do not); they rely on look-ahead states having no ^io.

*Rationale:* ^io is not copied below the selection state (elaborate*substate*io excludes selection and evaluate-operator superstates).

*Library rules:* agent-world*elaborate*substate*io

*Source:* agent-world/external-operator-application.soar; elaborations/_all.soar:agent-world*elaborate*substate*io

**L10-007** — The internal application rule of a task-action operator tests ^internal-actions true on the state, the operator's ^name and arguments, and ^pre-conditions-satisfied true. It changes the world model directly (objects and relation objects, replacing old values) to the action's effect.

*Rationale:* Look-ahead must predict the action's effect; MEA operators apply only once preconditions are satisfied.

*If violated:* look-ahead never changes the world (no-change impasses) or applies before preconditions hold

*Example:*

```
(state <s> ^operator <o> ^internal-actions true) (<o> ^name clean-object ^argument1 <obj> ^pre-conditions-satisfied true)
```

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'Internal Application' (applyclean-objectinternal)

**L10-008** — Some library rules are flagged :o-support and test no selected operator: output cleanup, future-event completion and smem storage.

*Rationale:* Persistent bookkeeping independent of the current operator.

*See:* related L0-042 (overlap)

*Source:* agent-world/elaborations/output.soar; agent-world/elaborations/future-event.soar; agent-world/force-conflict.soar; agent-world/elaborations/smem*.soar

**L10-009** — When ^top-state.environment is none, every state has ^internal-actions true. Otherwise real states have ^internal-actions false, and evaluate-operator states and the states below them have ^internal-actions true.

*Rationale:* Internal application on all states for tasks with no environment.

*If violated:* internal apply rules do not fire

*Library rules:* agent-world*elaborate*state*internal-actions*no-environment, agent-world*elaborate*state*internal-actions*false

*See:* related L10-003 (overlap)

*Source:* JEL, 12 Nov 2026

### Output and events

**L10-010** — Library log output uses (log <level> ...); levels 0 to 9 are reserved for the agent. Operator selection and application traces, and key events, are at level 1.

*Rationale:* Lets trace verbosity be controlled by log level.

*If violated:* noisy or missing traces

*Library rules:* agent-world*apply*operator*one-argument*monitor etc.

*Source:* agent-world/_readme.soar lines 6-7; elaborations/monitor-operator.soar

**L10-011** — The library's operator monitor logs 'Select <name>: <handles>' from ^argument-count and the arguments' object handles; operators therefore supply ^argument-count and arguments with handles.

*Rationale:* Uniform trace.

*If violated:* no selection trace

*Task supplies:* yes

*Library rules:* agent-world*apply*operator*one-argument*monitor; agent-world*apply*operator*two-argument*monitor; *no-handle*

*Source:* agent-world/elaborations/monitor-operator.soar

**L10-012** — The real-world output of a task-action operator is (<output-link> ^perform-action <p>) (<p> ^name <action-handle> ^argument1 <handle> [^argument2 <handle>]), created by agent-world and not by task rules.

*Rationale:* Generic rules translate the uniform operator structure into the environment command.

*Example:*

```
(<ol> ^perform-action <p>) (<p> ^name put-in ^argument1 Apple1 ^argument2 Fridge40)
```

*Library rules:* agent-world*apply*operator*external*argument0/1/2 (+ variants)

*Source:* agent-world/external-operator-application.soar; Thor-Soar Agent Documentation (thor.txt) 'Innate Task-Action Operators' (generic operator-independent rules)

**L10-013** — Second output path: when a selected operator has ^task-operator true and ^actions <cmd>, <cmd> is linked to the output-link as ^perform-action <cmd>. This rule tests none of ^pre-conditions-satisfied, ^internal-actions and ^quiescence.

*Rationale:* Lets an operator build its own command structure.

*Example:*

```
(<o> ^task-operator true ^actions <a>) --> (<ol> ^perform-action <a>)
```

*Library rules:* apply*operator*create-action-command

*Source:* agent-world/elaborations/output.soar:apply*operator*create-action-command

**L10-014** — agent-world removes a ^perform-action command from the output-link once its ^status is interrupted, complete or success. A command with ^status error stays, and its ^error-info is logged.

*Rationale:* Keeps the output-link clean without per-operator removal rules.

*Example:*

```
(<ol> ^perform-action <v>) (<v> ^status complete) --> (<ol> ^perform-action <v> -)
```

*Library rules:* agent-world*elaborate*operator*remove-command

*Source:* agent-world/elaborations/output.soar:agent-world*elaborate*operator*remove-command, agent-world*elaborate*operator*error

**L10-015** — ^agent-event structures on the output-link are removed once the environment marks them ^status complete.

*Rationale:* Same output protocol as perform-action.

*Library rules:* agent-world*elaborate*top-state*any*remove*completed*agent-event

*Source:* agent-world/elaborations/output.soar:agent-world*elaborate*top-state*any*remove*completed*agent-event

**L10-016** — When the perform-action of the selected operator returns ^status success during an active interaction segment, agent-world adds ^events.executed-action.action-handle <h>; on ^status error or failure it adds ^events.failed-action.action-handle <h> and interrupts.

*Rationale:* Reports action outcomes to the interaction/learning layer.

*Example:*

```
(<events> ^executed-action <a>) (<a> ^action-handle put-in)
```

*Task supplies:* yes

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*report*action-event*success, *report*failed-action*event

## L11 Learning

Chunking conventions for agent-world programs.

### Learning: chunking

**L11-001** — The library's chunking-control rules (force-learn in real-world states or in single-desired substates) are present but commented out.

*Rationale:* Control what chunks are learned.

*Source:* agent-world/elaborations/chunking-control.soar; Thor-Soar Agent Documentation (thor.txt) 'Learning'

**L11-002** — The rules that copy an operator's desireds into a substate test ^desired-count with $, so that a chunk is specific to the count.

*Rationale:* Chunk generality control.

*If violated:* overgeneral chunks

*Library rules:* agent-world*elaborate*substate*operator*desireds

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*operator*desireds (comment)

**L11-003** — A rule whose result can reach a chunk does not test the absence of structure in a substate, such as a look-ahead world (L3-062). A concept that tests absence and decides operator legality (clear, empty, opposite) is therefore a maintained relation: created and removed by the operator applications that change it, and tested with positive conditions.

*Rationale:* Chunking leaves negations over substate structure out of the chunk (allow-local-negations on), so the chunk is over-general; with allow-local-negations off Soar learns almost nothing.

*If violated:* Over-general chunks: with chunking on, look-ahead prefers longer or blocked paths (Hanoi 2 discs: 4 moves on 2 of 6 seeds).

*Example:*

```
(<w> ^clear <cd> - <nc>) (<nc> ^argument1 <old>) in the move application, instead of an elaboration that tests -{(<w> ^on <r>) (<r> ^argument2 <o>)}
```

*Task supplies:* yes

*Library rules:* gen_hanoi.py, gen_blocks.py (test set v1.26); library v2.29 copies one-argument declared relations

*Source:* FINDING-chunking-overgeneral.md; World-Conventions-Spec-v5 section 3

**L11-004** — Status of chunking in look-ahead (15 Nov 2026, library v2.30): with iterative-step tie-impasse, a cost metric and ^optimize true, and with L11-003 and L11-005 followed in the task rules, chunking gave optimal solutions on every tested water jug, Hanoi and blocks-world seed, also when chunks from an earlier run were reused. With the operator step some water jug seeds were longer than optimal. Open: chunks do not transfer between differently named objects.

*Rationale:* Learning in look-ahead is wanted; the current default gives up its speed-up.

*If violated:* n/a (records an open problem)

*Example:* Hanoi with maintained clear: the chunk tests that the destination is clear and that the goal peg is clear, but not that they differ, so it also prefers moving the small disc onto the goal peg.

*Library rules:* library v2.30 (lower-bound.soar; value writers test ^lower-bound $; success returned with its cost; failure-cutoff preference names the holder)

*Source:* FINDING-chunking-overgeneral.md (update of 15 Nov 2026); World-Conventions-Spec-v6

**L11-005** — Task rules test object handles with $: ^object-handle $ <h> (and ^argument1.object-handle $ <h>), so that a chunk keeps the handle as a constant. Until the Soar 9.6.50 defects are fixed: no $ inside a negated condition, and none inside a { } test that also holds a relational test.

*Rationale:* Chunking turns handles into variables and adds no inequality between them, so a chunk learned for one object can fire for another. Cost: chunks transfer only to the same named objects.

*If violated:* Over-general chunks: Hanoi 2 discs takes 4 moves on 2 of 6 seeds when it reuses its chunks (operator step: 3 to 8 moves). With $ in the excepted places: Soar reports "bad test type in hash_test ... cannot recover" (negated condition) or crashes when the rule loads ({ <> <x> $ <h> }).

*Example:*

```
(<b> ^object-handle $ <bh>) (<d> ^object-handle { <> <bh> <dh> }) in a blocks-world proposal
```

*Task supplies:* yes

*Library rules:* worldgen v18 wg.literalize_handles (default Task(literal_handles=True)); test set v1.27 gen__* rules

*Source:* FINDING-chunking-overgeneral.md (update of 15 Nov 2026); World-Conventions-Spec-v6 section 2; soar-dollar-bugs.zip (bug report)

### Learning: RL

**L11-006** — With ^flags.rl true, a state that has a ^reward-link and whose ^success is its ^desireds gets reward 1.0 on its reward-link. RL is otherwise unsupported by the library.

*Rationale:* Placeholder RL support.

*Library rules:* agent-world*elaborate*state*reward

*Source:* agent-world/elaborations/reward.soar; Thor-Soar Agent Documentation (thor.txt) 'Flags' ^rl

## L12 Scene and attention

Holds when attention (attend/remove) over the scene is in use.

### World/state

**L12-001** (capacity: attention (attend/remove)) — The top state has ^scene; its ^objects.object structures (and, in Thor, ^in and ^on relations and ^holding-object) describe what the agent currently perceives. The task's input processing creates each ^scene.objects.object with an ^object-handle.

*Rationale:* The world is built from the scene.

*If violated:* no objects enter the world

*Task supplies:* yes

*Library rules:* object-world*elaborate*world-from-scene*attended-object

*Source:* agent-world/initialize-agent-world.soar (creates empty ^scene.objects); Thor-Soar Agent Documentation (thor.txt) 'Scene'

**L12-002** (capacity: attention (attend/remove)) — The top state's ^attends has one ^attend <object-handle> for each scene object that is to be in the world. The task creates them.

*Rationale:* Keeps the world small; only attended objects are reasoned about.

*If violated:* objects never copied to world

*Task supplies:* yes

*Library rules:* object-world*elaborate*world-from-scene*attended-object

*Source:* agent-world/initialize-agent-world.soar; Thor-Soar Agent Documentation (thor.txt) 'Attends.attend'

**L12-003** (capacity: attention (attend/remove)) — For each attended handle the library adds the scene object itself (the same identifier, not a copy) to the anchored world's ^objects, with o-support, on the top state only, when no world object has that handle.

*Rationale:* World and scene share object identifiers.

*Library rules:* object-world*elaborate*world-from-scene*attended-object

*See:* related L0-042 (overlap); L12-004 (overlap)

*Source:* agent-world/elaborations/world-from-scene.soar:object-world*elaborate*world-from-scene*attended-object

**L12-004** (capacity: attention (attend/remove)) — The rule that adds attended scene objects to the world is flagged :o-support and tests no selected operator, so a world object persists after its attend is removed. The library does not remove unattended objects.

*Rationale:* World is a memory of attended objects, not a reflection of input.

*If violated:* stale objects remain

*Library rules:* object-world*elaborate*world-from-scene*attended-object

*See:* related L0-042 (overlap); L12-003 (overlap)

*Source:* agent-world/elaborations/world-from-scene.soar

## L13 Grounding

Holds when grounding (object-world) is in use.

### Naming and files

**L13-001** (capacity: grounding) — A task's problem space carries no ^agent-world marker, including when the task uses grounding (find-object) or future-event locking: ^problem-space.agent-world true is deprecated (P-006) and no library rule tests it.

*Rationale:* Before P-006 some library rules fired only for agent-world problem spaces; the marker is now unused.

*If violated:* No effect on behavior; the attribute is dead weight and misleads readers.

*Example:*

```
(<ps> ^name thor-world)
```

*Task supplies:* no

*Library rules:* none (agent-world*elaborate*state*reward and the find-object-direct proposals do not test it)

*Source:* Library P-006 (v2.14); agent-world/elaborations/reward.soar:agent-world*elaborate*state*reward; object-world/find-object.soar

### Non-task operators

**L13-002** (capacity: grounding) — The library operators find-object, find-object-direct, wait, goal-completed and cutoff-search carry no ^task-operator, so the preference of L15-001 does not apply to them. failed-grounding and assume-successful-grounding have ^task-operator true.

*Source:* agent-world/find-object.soar; agent-world/find-object-direct.soar; agent-world/Impasse__Operator_Tie/evaluate-operator/failed-grounding.soar; agent-world/find-object/assume-successful-grounding.soar; agent-world/force-conflict.soar

### Search control

**L13-003** (capacity: grounding) — With ^flags.desired-preferences true, ^failed-grounding-desired <d> on a desireds structure rejects a find-object operator for <d> whenever an operator other than find-object is also proposed.

*Rationale:* Avoid repeated failed grounding.

*Library rules:* same

*Source:* agent-world/elaborations/search-control.soar:agent-world*compare*avoid-desired*search-control*failed-grounding

**L13-004** (capacity: grounding, time and future events) — Search control for find-object: mode a is better than mode b; find-objects are mutually indifferent; operators with an unanchored argument2 are worse than find-object; operators whose arguments are all anchored, or that use an anchored object with find-object's handle, are better; find-object for an object locked by a future event is rejected.

*Source:* agent-world/find-object.soar:object-world*compare*find-object*, object-world*compare*reject*find-object*future-event

### Grounding

**L13-005** (capacity: grounding) — A desired object refers to a world object only by ^object-handle. When the handle is a placeholder for an object described in ^world-context (^anchored false), the object must be grounded (its handle replaced by a real world handle) by find-object or find-object-direct before a task operator can act on it.

*Rationale:* Delays grounding until needed; desired and world are connected only by shared handles.

*Example:*

```
(<desireds> ^desired.holding-object.object-handle |unanchored-object-egg-handle| ^world-context.objects.object <egg>) (<egg> ^class egg ^object-handle |unanchored-object-egg-handle| ^anchored false)
```

*Source:* Thor-Soar Agent Documentation (thor.txt) Desireds '^world-context'; agent-world/find-object.soar; agent-world/find-object-direct.soar

**L13-006** (capacity: grounding) — find-object is proposed (acceptable only), in a state with ^desireds, when an unachieved desired's ^object or ^holding-object names a handle that is not grounded in the anchored world: (a) no world object has the handle; (b) only a derived object has it as ^origin-object-handle; (c) the object is in a world-context world; or (d) the world object with the handle has ^anchored false.

*Rationale:* Grounding is an MEA-style operator triggered by the goal.

*Library rules:* object-world*propose*find-object*

*See:* related L8-008 (overlap)

*Source:* object-world/find-object.soar:object-world*propose*find-object*

**L13-007** (capacity: grounding) — A find-object operator has ^name find-object, ^super-desired, ^argument1 <the desired object>, optionally ^argument2 <a world object>, ^argument-count, and ^desireds with one desired, ^info.unanchored-object <obj> (optionally ^info.anchored-object), and ^desired-count 1. It has no ^task-operator.

*Source:* agent-world/find-object.soar

**L13-008** (capacity: grounding) — find-object's precondition is satisfied when the world has ^info <i> with ^unanchored-object (the same object-handle) and ^anchored-object <a real object>. The grounding operators in find-object's substate (a task-supplied search, an smem retrieval, or assume-successful-grounding) must create exactly this ^world.info structure.

*Rationale:* agent-world's info special case of achieved-desired turns it into ^pre-conditions-satisfied.

*If violated:* find-object never applies

*Example:*

```
(<world> ^info <i>) (<i> ^unanchored-object <u> ^anchored-object <a>) (<a> ^object-handle Egg12 ^anchored true)
```

*Task supplies:* yes

*Source:* agent-world/find-object.soar apply rules; elaborations/achieved-desired-operators.soar:agent-world*apply*operator*acheived-desired*info

**L13-009** (capacity: grounding) — When find-object applies, the placeholder ^object-handle on the desired object (and on matching super-desireds objects and the superoperator's ^argument1) is replaced by the anchored object's handle, ^anchored false becomes true, the world's ^info is removed and ^processed true is added to the world.

*Library rules:* object-world*apply*find-object*object-found*

*Source:* agent-world/find-object.soar:object-world*apply*find-object*object-found, *-arg1, *imaginary, *super-desireds*object, *super-desireds*object*argument1

**L13-010** (capacity: grounding) — find-object's ^argument1 is elaborated with every other desired object (in the state's desireds or the superoperator's effect-desireds) that has the handle of argument2, so one grounding rewrites them all; ^argument1 can be multi-valued.

*Source:* agent-world/find-object.soar:object-world*elaborate*find-object*object*mea, *object*effect-desired

**L13-011** (capacity: grounding) — find-object-direct grounds immediately (no substate, ^pre-conditions-satisfied true at proposal, best+indifferent so a random candidate is picked) when a world-context object is constrained only by ^class (or ^class plus one feature) and an anchored world object of that class (and feature) exists; variants pair both arguments of desired in/on relations and the stoveburner/stoveknob pair of a controlled-by desired.

*Rationale:* Grounding is trivial when the class alone determines the candidate set.

*Library rules:* agent-world*propose*find-object-direct*

*Source:* agent-world/find-object-direct.soar:agent-world*propose*find-object-direct*

**L13-012** (capacity: grounding) — A world-context object is constrained by at most ^class and one other feature (apart from ^anchored, ^object-handle, ^accessible and ^duplicate-of). An object with more constraints is not grounded by find-object-direct and is left to find-object.

*Rationale:* find-object-direct tests the absence of any other attribute.

*If violated:* slow grounding via search

*Task supplies:* yes

*Source:* agent-world/find-object-direct.soar:*class-only-one, *class-plus-one; Thor-Soar Agent Documentation (thor.txt) Desireds '^object' (limited to two features)

**L13-013** (capacity: grounding) — find-object-direct applies by rewriting the matching placeholder handle (and ^anchored false -> true) wherever it occurs: the desired object, the world-context object, desired holding-object, super-desireds, the superoperator's argument1/argument2, relation arguments in desireds, and the superoperator's effect-desireds; *34 rules do the same for argument3/argument4.

*Library rules:* apply*find-object-direct*

*Source:* agent-world/find-object-direct.soar:apply*find-object-direct*

**L13-014** (capacity: grounding) — A desired object marked ^failed-grounding true is not proposed for find-object again.

*Source:* agent-world/find-object.soar (-^failed-grounding true in all proposals)

## L14 Selection space

Holds when the selection-world selection space is in use.

### Naming and files

**L14-001** (capacity: selection-world) — The classic selection space (selection.soar) is not loaded with the shared library: selection-world replaces it and uses different attribute names.

*Rationale:* The libraries share rule names but differ in representation (^superoperator vs ^super-operator, ^desired vs ^desireds).

*If violated:* mixed, inconsistent selection rules

*Task supplies:* yes

*Source:* selection.soar, selection-world.soar; both Operator_Tie/evaluate-operator.soar

**L14-002** (capacity: selection-world) — Task rules must not use the state name selection or the operator names evaluate-operator and cutoff-search.

*Rationale:* Library rules key on these names.

*If violated:* library rules fire in task states or on task operators

*Source:* selection/Operator_Tie/evaluate-operator.soar, evaluate-operator/*.soar; selection-world/Operator_Tie/*.soar

### Flags and constants

**L14-003** (capacity: selection-world) — The task state being evaluated has ^problem-space with ^name, and the evaluation state must have a problem space with the same name: agent-world compares the evaluation state's ^problem-space.name with the evaluate-operator's ^super-problem-space.name.

*Rationale:* The look-ahead operator is installed only when the names match.

*If violated:* no look-ahead operator; evaluation substate stalls

*Example:*

```
(<s> ^problem-space <p>) (<p> ^name my-task)
```

*Task supplies:* yes

*Source:* selection/Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy/*no-copy; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy

**L14-004** (capacity: selection-world) — ^no-local-negations on the problem space switches selection-world to rules that avoid local negations (for chunking).

*Rationale:* Lets chunks be built over the copy rules.

*If violated:* copy rules mix the two modes

*Task supplies:* yes

*Source:* _firstload.soar 'Changes May 2007 (SBW)' (both); *nln rules

### World/state

**L14-005** (capacity: selection-world) — The top state must have ^name: the library rules that interrupt on success or failure test it.

*Rationale:* The rules bind and print the name.

*If violated:* agent never halts on success

*Task supplies:* yes

*Source:* selection-world*apply*top-goal*halt*success, selection-world*apply*top-goal*halt*failure (both)

**L14-006** (capacity: selection-world) — A task rule that reaches the top state through ^top-state also works in look-ahead, because the evaluation state is its own ^top-state.

*Rationale:* Keeps hypothetical reasoning off the real top state.

*If violated:* look-ahead reads or writes the real top state

*Task supplies:* yes

*Source:* selection-world selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions; agent-world/elaborations/_all.soar:elaborate*substate*top-state, agent-world*elaborate*substate*external-top-state

### Relations

**L14-007** (capacity: selection-world) — The look-ahead world copy copies the relations ^on, ^in and ^above, every relation named by ^copy-relation on the task's problem space, ^holding-object, ^future-event, and ^controlled-by (shared, not copied). A relation object is copied when its arguments are copied objects. Any other world relation is absent from the look-ahead world.

*Rationale:* The copy rules are written per relation.

*If violated:* task relations missing in look-ahead

*Task supplies:* yes

*Source:* selection-world/.../elaborations.soar:selection-world*elaborate*evaluate-operator*default-state-copy-relation*in-container*above-location/on-location/in-location, *controlled-by, *holding, *holding*none

### Desireds

**L14-008** (capacity: selection-world) — Whether higher or lower numeric evaluations are better is declared on the goal set: ^desireds.better higher or lower.

*Rationale:* The comparison rules read the direction from the goal.

*If violated:* numeric values produce no better/worse preferences

*Example:*

```
(<ds> ^better lower)
```

*Task supplies:* yes

*Source:* selection-world*compare*selection*higher-evaluation-better, selection-world*compare*selection*prefer-lower-evaluation (both)

**L14-009** (capacity: selection-world) — Two operators with equal numeric evaluations are made indifferent unless a desired of the goal set has ^equal not-indifferent.

*Rationale:* Allows treating ties in value as real ties.

*Source:* selection-world*compare*selection*equal-evaluation-indifferent (both)

### Desireds bookkeeping

**L14-010** (capacity: selection-world) — Each evaluation carries the goal it is computed for: a new ^desireds <nd> with ^duplicate-of <the task state's desireds>, the same ^desired pointers and the same ^desired-count.

*Rationale:* Preferences are created only when the evaluation's goal matches the task state's goal.

*If violated:* no preferences are created

*Source:* selection/Operator_Tie/elaborations.soar:selection*elaborate*evaluation*desired; selection-world/Operator_Tie/elaborations.soar:selection-world*elaborate*selection*evaluation*desireds, *desireds*desired, *desireds*count

**L14-011** (capacity: selection-world) — In an evaluation substate, ^success, ^failure and the other outcome attributes are put on the substate's own ^desireds (the copy that has ^duplicate-of), never on the original. The return rules match that copy's ^duplicate-of against the evaluation's ^desireds.

*Rationale:* Each evaluation and substate has its own desireds copy, so achieved flags stay local to the look-ahead.

*If violated:* success is not passed back

*Library rules:* agent-world achieved-desireds rules

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:evaluate-operator*elaborate*symbolic-evaluation*from-subgoal*success*no*better

**L14-012** (capacity: selection-world) — The evaluation substate gets a new ^desireds with ^duplicate-of <the evaluation's desireds> and the same ^desired-count; agent-world copies each ^desired into it, each with ^duplicate-of.

*Rationale:* The look-ahead marks desireds achieved locally.

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*state*desireds, *desired*nln; agent-world .../agent-world*elaborate*evaluate-operator*copy-desired

### Task operators

**L14-013** (capacity: selection-world) — The general rule makes two tied operators with the same symbolic evaluation indifferent only when both have ^task-operator true and the desireds have no ^better, and never for success, exhaustion-failure, depth-exceeded or depth-exhaustion. Two success evaluations (both closed, desireds without ^better, selection without ^remaining-operators) and two exhaustion-failure evaluations (at quiescence) are made indifferent by their own rules. Iterative deepening adds the rules of L16-014.

*Rationale:* Keeps non-task operators out of indifference.

*If violated:* equal-valued operators stay tied (new tie impasse)

*Example:*

```
(<o> ^name move ^task-operator true)
```

*Task supplies:* yes

*See:* related L16-014

*Source:* selection-world/Operator_Tie/elaborations.soar:selection-world*compare*selection*same-symbolic-evaluations-are-indifferent

**L14-014** (capacity: selection-world) — The look-ahead operator is a shallow copy of the evaluated operator (L14-044): its attribute values are those of the original, so they still point into the real world. Its parameters must therefore refer to world objects in a way that survives the world copy: by ^object-handle, or by a description matched in the copied world, not by the identifier of a real-world object.

*Rationale:* The copied world has new object identifiers.

*If violated:* the look-ahead operator modifies or tests real-world objects

*Task supplies:* yes

*Source:* inferred from selection-world copy rules and agent-world look-ahead-operator*copy

**L14-015** (capacity: selection-world) — Every tied operator has ^name: library rules that return and print evaluations test ^super-operator.name.

*Rationale:* Rules bind the operator name.

*If violated:* pass-back and cutoff rules do not fire

*Task supplies:* yes

*Source:* selection-world/Operator_Tie/evaluate-operator/Operator_Tie/elaborations.soar:selection-world*elaborate*selection*pass-back-success; selection/... same rule (^superoperator.name)

### Search control

**L14-016** (capacity: selection-world) — evaluate-operator operators are mutually indifferent unless the selection state has ^operator-selection not-indifferent. A task that orders the evaluations elaborates that attribute on the selection state and supplies its own preferences among the evaluate-operator operators.

*Rationale:* Lets task knowledge order which candidate is looked at first.

*If violated:* without own preferences the evaluate-operator operators tie again

*Example:*

```
(<sel> ^operator-selection not-indifferent)
```

*Library rules:* selection-world*compare*selection*select*evaluate-operator*indifferent

*Source:* selection-world*compare*selection*select*evaluate-operator*indifferent (both libraries)

### Substates (general)

**L14-017** (capacity: selection-world) — selection-world relies on the soar-base rule that names a substate after its superoperator: the evaluation substate has ^name evaluate-operator only because of it.

*Rationale:* Proposal rules such as evaluate-operator*propose*copy-task-state and evaluate-operator*elaborate*evaluate-operator*internal-actions test ^name evaluate-operator.

*If violated:* evaluation substate does nothing

*Library rules:* simple.soar:soar-base*elaborate*state*name

*Source:* soar-base/simple.soar:soar-base*elaborate*state*name; selection/Operator_Tie/evaluate-operator/copy-task-state.soar; selection-world/Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions

### Selection space

**L14-018** (capacity: selection-world) — A conflict impasse is handled like a tie: its substate is named selection, so the conflicting operators are evaluated by look-ahead.

*Rationale:* Contradictory better and worse preferences are settled by look-ahead.

*Source:* agent-world/Impasse__Operator_Conflict/elaborations.soar; selection-world (selection naming rule)

**L14-019** (capacity: selection-world) — selection-world depends on agent-world for: the copy of the evaluated operator (^look-ahead-operator, L14-044), copying each ^desired into the evaluation state, creating ^success <desireds>, and turning constraint-failure evaluations into rejects.

*Rationale:* selection-world leaves these steps to agent-world.

*If violated:* the look-ahead never gets an evaluated operator or a success

*Library rules:* agent-world rules listed in source

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy, agent-world*elaborate*evaluate-operator*copy-desired; agent-world/elaborations/achieved-desireds.soar; agent-world/Impasse__Operator_Tie/elaborations.soar:agent-world*compare*selection*select*constraint-failure-becomes-reject

**L14-020** (capacity: selection-world) — When evaluate-operator is selected and no evaluation exists for its item, an ^evaluation object with ^super-operator <item> is created on the selection state, and the operator is linked to it (^evaluation <e>, o-supported).

*Rationale:* The evaluation holds the result for that candidate.

*If violated:* selection: duplicate evaluations for one item if evaluate-operator is reselected

*Library rules:* selection-world*apply*selection*state*evaluation

*See:* related L1-011 (overlap); L5-015 (overlap)

*Source:* selection-world*apply*selection*state*evaluation, selection-world*apply*selection*evaluate-operator*evaluation (both libraries)

**L14-021** (capacity: selection-world) — evaluate-operator is elaborated with ^superstate <the tied state> and ^super-problem-space <that state's ^problem-space>; the tied state therefore needs a ^problem-space.

*Rationale:* The evaluation substate finds the task state and problem space through the operator.

*If violated:* look-ahead-operator is never created

*Source:* selection*elaborate*evaluate-operator*superproblem-space / *super-problem-space, selection-world*apply*selection*evaluate-operator*superstate

**L14-022** (capacity: selection-world) — An evaluation gets ^value true as soon as it has ^numeric-value, ^symbolic-value or ^expected-value (any value, including novalue). evaluate-operator is then no longer proposed for that item.

*Rationale:* Marks the item as evaluated.

*Library rules:* selection-world*elaborate*selection*evaluation*value

*Source:* selection-world*elaborate*selection*evaluation*value; selection-world*propose*selection*evaluate-operator

**L14-023** (capacity: selection-world) — The selection state has ^not-all-operators-evaluated true while some proposed evaluate-operator has no evaluation with ^value true, and ^found-value true once an evaluation has a value other than novalue.

*Rationale:* Used to tell when all candidates have been evaluated with no useful value.

*Source:* selection-world*elaborate*selection*state*all-objects-evaluated, selection-world*elaborate*selection*state*found-value-true (both)

**L14-024** (capacity: selection-world) — Every substate below a selection state has ^selection-superstate <the nearest enclosing selection state>, copied down through non-selection states. A selection state that has none is a top selection and has ^top-selection true.

*Rationale:* Lets rules find the evaluation being computed at any depth, and the outermost search.

*Source:* selection-world/.../evaluate-operator/elaborations.soar:selection-world*elaborate*selection*selection-substate, *copy; Operator_Tie/elaborations.soar:selection-world*elaborate*selection*top-selection

**L14-025** (capacity: selection-world) — When the substate of a conflict impasse reaches a state no-change (^choices none), each conflicting item is rejected in the conflicted state.

*Rationale:* An unresolved conflict means none of those operators is acceptable.

*Source:* selection-world/Operator_Tie/Impasse__State_No-Change/elaborations.soar:selection-world*compare*default*select*reject*conflict

**L14-026** (capacity: selection-world) — The look-ahead world copy copies every attribute of every world object except ^object-handle, ^duplicate-of and ^anchored (which it sets itself) and the attributes listed as ^dont-copy-object-attribute on the state's problem space. The task lists there every derived (i-supported) object attribute, on both problem-space rules (task state and MEA substate), so that the copy derives them again and holds no stale value.

*Rationale:* A computed property copied from the real world may disagree with the copied properties it is derived from.

*If violated:* stale computed properties in look-ahead copies give wrong evaluations

*Example:*

```
(<ps> ^dont-copy-object-attribute accessible)
```

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (decision on LF-19); selection-world/Operator_Tie/evaluate-operator/elaborations.soar: selection-world*elaborate*evaluate-operator*default-state-copy-object-attributes

### Look-ahead / evaluation

**L14-027** (capacity: selection-world) — The symbolic evaluation values are required-success, success, partial-success, indifferent, partial-failure, failure, prohibit-failure, exhaustion-failure, constraint-failure, failed-grounding, depth-exceeded and depth-exhaustion. lose is accepted as failure by the preference rules but is not returned from a substate.

*Rationale:* Only these values are translated into preferences.

*If violated:* other values are ignored

*See:* related L14-028 (overlap)

*Source:* selection-world*apply*evaluate-operator*symbolic-evaluation*from-subgoal; selection*select* rules

**L14-028** (capacity: selection-world) — Evaluations become preferences in the tied state as follows. required-success: require. success and partial-success: best, when the desireds have no ^better. indifferent: indifferent. failure and lose: reject. constraint-failure: reject. prohibit-failure: prohibit. partial-failure: worst. exhaustion-failure: worst, at quiescence. Pairwise: success is better than partial-success, failure and partial-failure; partial-failure and exhaustion-failure are better than failure.

*Rationale:* A failed operator can still be chosen if nothing else is left.

*See:* related L14-027 (overlap)

*Source:* selection-world/Operator_Tie/elaborations.soar:selection-world*compare*selection*select*failure-evaluation-becomes-reject-preference (creates <), selection-world*compare*selection*select*exhaustion-failure-evaluation-becomes-worst-preference, selection-world*compare*selection*success-evaluation-better-than-failure, selection-world*compare*selection*exhaustion-evaluation-better-than-failure, selection-world*compare*selection*success-evaluation-equal-failure; agent-world/Impasse__Operator_Tie/elaborations.soar:agent-world*compare*selection*select*constraint-failure-becomes-reject

**L14-029** (capacity: selection-world) — Preferences from evaluations are created for the operators of the tied state (the selection state's superstate), and only when the evaluation's goal (^desireds.duplicate-of) is that state's ^desireds.

*Rationale:* Results are scoped to the goal they were computed for.

*Source:* all selection*select* and selection*compare* rules

**L14-030** (capacity: selection-world) — A nested look-ahead that reaches required-success passes back partial-success to the operator being evaluated one selection level up.

*Rationale:* Lets a deeper success support the higher-level choice; the comment calls it dangerous because it can learn a non-optimal path.

*Library rules:* selection-world*elaborate*selection*pass-back-success

*Source:* selection/Operator_Tie/evaluate-operator/Operator_Tie/elaborations.soar:selection-world*elaborate*selection*pass-back-success; selection-world same file

**L14-031** (capacity: selection-world) — When, at quiescence, every operator of a nested selection has been evaluated without any value (no ^found-value), the enclosing evaluation gets ^numeric-value novalue. A novalue evaluation is worse than any numeric value.

*Rationale:* Propagates that nothing useful was found.

*Source:* selection*elaborate*evaluate-operator*all-operators-novalue; selection*compare*novalue-evaluation-always-worse

**L14-032** (capacity: selection-world) — For a numeric evaluation the task elaborates ^numeric-value <n> on the evaluation state (the state with the copied ^desireds); the library copies it to the evaluation.

*Rationale:* Numeric values let operators be ranked rather than accepted or rejected.

*If violated:* no numeric preferences

*Task supplies:* yes

*Source:* selection-world*apply*evaluate-operator*numeric-evaluation*from-subgoal (both)

**L14-033** (capacity: selection-world) — When the desireds have ^better lower and ^best 0, an operator whose numeric evaluation is 0 gets a best preference.

*Rationale:* 0 is known to be optimal (e.g. zero remaining cost).

*Source:* selection-world/Operator_Tie/elaborations.soar:selection-world*compare*selection*prefer-lower-evaluation*0

**L14-034** (capacity: selection-world) — When the desireds have ^better, a success is returned only with a numeric value: the state must have both ^success <ds2> and ^numeric-value <n>. Success then creates no best preference; operators are ranked by numeric value.

*Rationale:* With a quality measure, all successes are compared by cost.

*If violated:* success not returned

*Task supplies:* yes

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:evaluate-operator*elaborate*symbolic-evaluation*from-subgoal*success*better; Operator_Tie/elaborations.soar:selection-world*compare*selection*select*success-evaluation-becomes-best-preference

**L14-035** (capacity: selection-world) — ^expected-value <v> elaborated on the evaluation state is copied to the evaluation and becomes a numeric-indifferent preference for the tied operator, for probabilistic or RL-style selection.

*Rationale:* Expected values bias selection rather than rank strictly.

*Source:* selection-world*apply*evaluate-operator*expected-evaluation*from-subgoal, selection-world*compare*selection*evaluation*expected-values (both)

**L14-036** (capacity: selection-world) — selection-world creates no reward and does not use ^reward-link; its only numeric preference comes from ^expected-value. (agent-world has a reward rule for ^flags.rl true, L11-006.)

*Rationale:* No reward conventions are defined by these libraries.

*Source:* selection/*, selection-world/* (absence); agent-world/elaborations/reward.soar

**L14-037** (capacity: selection-world) — A constraint-failure impasse anywhere below the selection state (found through ^selection-superstate) counts as exhaustion-failure for the operator being evaluated.

*Rationale:* No operator can be chosen, so the path is a dead end.

*Source:* Operator_Constraint-Failure/elaborations.soar:selection-world*apply*evaluate-operator*evaluation*failure*constraint-failure (both)

**L14-038** (capacity: selection-world) — Two stacked state no-change impasses under the evaluation substate give exhaustion-failure for the operator being evaluated.

*Rationale:* Nothing more can be done from that state.

*Source:* State_No-Change/State_No-Change/elaborations.soar:selection-world*apply*evaluate-operator*evaluation*failure*no-operators (both)

**L14-039** (capacity: selection-world) — A state no-change directly under the evaluate-operator substate, with no ^world.future-event pending, gives the evaluation ^symbolic-value failure (not exhaustion-failure). Planned: no wait is proposed there (L9-025); library v2.41 still proposes it.

*Rationale:* A look-ahead state with nothing to do and no pending event is a dead end; a future event means time can still pass.

*If violated:* look-ahead never terminates

*Source:* selection-world/Operator_Tie/evaluate-operator/State_No-Change/elaborations.soar:selection-world*apply*state-no-change*selected*failure*during*evaluation*reject-operator; soar-base/simple.soar:soar-base*propose*top-ps*wait excludes evaluate-operator

**L14-040** (capacity: selection-world) — The library does not detect a state that repeats an earlier state. ^duplicate-of only maps a copied object, operator or desired to its original.

*Rationale:* Repeated-state detection is left to the task (Thor-Soar has domain-specific rules).

*If violated:* look-ahead may loop through repeated states

*Task supplies:* yes

*Source:* selection-world/_firstload.soar (commented superstate-set rules); agent-world look-ahead elaborations (comment on duplicate-look-ahead-operator)

**L14-041** (capacity: selection-world) — The classic problem-space copy flags (default-state-copy and the like) are not used: every evaluate-operator substate is marked ^deep-copy-world true and fixed elaboration rules copy the world.

*Rationale:* The world has a fixed structure (objects with handles, binary relations), so one generic copy works.

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions, selection-world*apply*evaluate-operator*state*world-copy

**L14-042** (capacity: selection-world) — The evaluate-operator substate is a hypothetical top state: ^top-state <itself>, ^real false, ^internal-actions true, ^deep-copy-world true.

*Rationale:* The look-ahead runs the task's own rules on the copied world.

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions, selection-world*elaborate*evaluate-operator*state*name

**L14-043** (capacity: selection-world) — The copied world is built by elaborations (i-supported), not by an operator; look-ahead operators then change it with o-supported actions. (Tested in Soar 9.6.5: an o-supported removal of an i-supported value takes effect.)

*Rationale:* Copy follows the original while the substate exists.

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar

**L14-044** (capacity: selection-world) — The evaluated operator is selected first in the evaluation substate through a require preference on the operator that is both ^look-ahead-operator and ^untried-tied-operator. agent-world makes ^look-ahead-operator a shallow copy of the tied operator: a new object with ^copied-from <the original> and every attribute of the original except ^evaluation and ^super-operator, with the same values.

*Rationale:* The look-ahead should start with the operator being evaluated.

*Source:* selection-world/Operator_Tie/evaluate-operator/task-operator.soar:selection-world*compare*evaluate-operator*look-ahead; agent-world/.../elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy

### Learning: chunking

**L14-045** (capacity: selection-world) — exhaustion-failure is created only at quiescence (its rules test ^quiescence t), and so are its preferences; no chunk is learned from it.

*Rationale:* Exhaustion depends on the absence of knowledge, which chunking must not capture.

*If violated:* overgeneral chunks

*Source:* _firstload.soar 'Change made for Soar 9.0' (both); selection*select*exhaustion-failure-evaluation-becomes-*

**L14-046** (capacity: selection-world) — The evaluate-operator substate calls force-learn, so evaluation results are chunked also when learning is restricted to selected states (chunk only).

*Rationale:* Look-ahead results should be learned.

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*evaluate-operator*internal-actions

**L14-047** (capacity: selection-world) — selection-world sets multi-attributes evaluation 5 (a matching hint for the multi-valued ^evaluation attribute).

*Rationale:* Improves rete ordering.

*Source:* selection-world/_firstload.soar

### Other

**L14-048** (capacity: selection-world) — selection-world logs (level 1) the name of the operator being evaluated each time evaluate-operator applies, and logs exhaustion and cut-off failures.

*Rationale:* Tracing.

*Source:* selection-world/Operator_Tie/evaluate-operator.soar:selection-world*apply*evaluate-operator*print; State_No-Change/elaborations.soar

## L15 Substates, search and look-ahead

Substates and search control in general, and look-ahead with its cost when in use.

### Search control

**L15-001** — When an operator with ^task-operator false and one with ^task-operator true are both proposed, the library makes the first better than the second.

*Rationale:* Internal bookkeeping (grounding, init, desireds management) runs before world actions.

*Library rules:* agent-world*compare*task-operator-non-task-operator

*See:* related L9-023 (overlap)

*Source:* agent-world/elaborations/search-control.soar:agent-world*compare*task-operator-non-task-operator

**L15-002** — With ^flags.desired-preferences true, preferences among desireds are stated on the desireds structure: ^preferred-desired <d> gives best to operators with ^super-desired <d>; ^avoid-desired <d> gives worst; ^preferred-indifferent <d> gives indifferent; ^super-preferred-desired <d1> with ^preferred-desired <d2> makes the operator for <d1> better than the one for <d2>.

*Rationale:* Declarative ordering of which desired to pursue.

*Task supplies:* yes

*Library rules:* agent-world*compare*preferred-desired*search-control; *avoid-desired*; *preferred-indifferent*; *superpreferred-desired*

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^avoid-desired etc.; agent-world/elaborations/search-control.soar

**L15-003** — ^required-desired <d> on a desireds structure makes every operator that serves an unachieved required desired better than every task operator that does not. No flag is needed.

*Rationale:* Force pursuit of required desireds first.

*Library rules:* same

*Source:* agent-world/elaborations/search-control.soar:agent-world*compare*required-desired*ordering*relations*better

**L15-004** — With ^flags.gps-desired-ordering true, each entry of ^constants.desired-orderings.desired-ordering (^relation <attr> or ^object-property <attr>, with ^value <n>) gives each matching desired ^selection-value <n>. Between two task operators, the one whose ^super-desired has the higher value is worse; equal values (without a disjunction) are indifferent.

*Rationale:* Table-of-connections ordering of differences.

*Task supplies:* yes

*Library rules:* agent-world*apply*desired-selection-value*relation/object-property; agent-world*compare*gps-desired-ordering*ordering*relations*same/better

*Source:* Thor-Soar Agent Documentation (thor.txt) "Constants" desired-ordering, "Flags" gps-desired-ordering; agent-world/elaborations/search-control.soar (selection-value and gps rules)

**L15-005** — On every operator conflict impasse the library logs '***Conflict Impasse***' and interrupts.

*Rationale:* Conflicts are treated as a debugging stop point.

*Library rules:* agent-world*apply*operator-conflict*state

*Source:* agent-world/Impasse__Operator_Conflict/elaborations.soar:agent-world*apply*operator-conflict*state

### Substates (general)

**L15-006** — A rule that must reach the real top state from a look-ahead state uses ^external-top-state, not ^top-state.

*Rationale:* ^top-state is a copy during look-ahead.

*If violated:* look-ahead reads hypothetical instead of real top state or vice versa

*Library rules:* agent-world*elaborate*substate*external-top-state

*See:* related L7-009 (overlap)

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*external-top-state

**L15-007** — ^io is copied to every substate except selection states and states under evaluate-operator. A look-ahead state therefore has no ^io.

*Rationale:* Hypothetical states must not issue output.

*If violated:* look-ahead could write to output-link

*Library rules:* agent-world*elaborate*substate*io

*See:* related L7-003 (overlap)

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*io

**L15-008** — An operator no-change substate is an operator-implementation substate when the superoperator has ^pre-conditions-satisfied true. Otherwise it is an MEA subgoal, and its ^desireds is a duplicate (^duplicate-of) of the superoperator's ^desireds.

*Rationale:* The same impasse type serves two roles: achieving preconditions and implementing a composite.

*Library rules:* agent-world*elaborate*substate*operator*desireds, agent-world*elaborate*operator-implementation-substate*super-operator-problem-space

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*operator-implementation-substate*super-operator-problem-space; elaborations/_all.soar:agent-world*elaborate*substate*operator*desireds

**L15-009** — An operator no-change substate receives every attribute of the superstate's selected operator as a state attribute, except ^desireds, ^superstate and ^current-evaluation-depth. This includes ^name, the arguments, ^task-operator, ^pre-conditions-satisfied and ^effect-desireds.

*Rationale:* Substate rules can test operator parameters directly on the state; it also gives the substate its ^name.

*Example:*

```
(state <s> ^impasse no-change ^attribute operator ^superstate.operator.<attr> <v>) --> (<s> ^<attr> <v>)
```

*Library rules:* agent-world*elaborate*substate*super-operator*attributes

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*substate*super-operator*attributes

### Look-ahead / evaluation

**L15-010** (capacity: look-ahead (agent-world)) — In a look-ahead copy, every world, object, relation object and desired has ^duplicate-of pointing to its original.

*Rationale:* Trace back to originals; separate bookkeeping.

*Library rules:* selection-world copy rules (outside A1)

*Source:* Thor-Soar Agent Documentation (thor.txt) "World" ^duplicate-of, "Desireds" ^duplicate-of, "Objects" ^duplicate-of

**L15-011** (capacity: look-ahead (agent-world)) — The look-ahead (evaluate-operator) state has two ^name values: evaluate-operator (from the superoperator) and the task state's name. Task proposal and evaluation rules that test the task ^name therefore fire in it.

*Rationale:* Rules for look-ahead test ^name evaluate-operator; task rules test the task name.

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*substate*super-operator*attributes; selection-world selection-world*elaborate*evaluate-operator*state*name; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar (tests ^name evaluate-operator)

**L15-012** (capacity: look-ahead (agent-world)) — Look-ahead time is relative. In an evaluation state directly under the top selection the copied anchored world starts at ^time 0; a deeper evaluation copies ^time from the world of the selection's superstate. A numeric evaluation under cost-metric time is therefore time from the start of the top-level look-ahead.

*Rationale:* The evaluated plan duration is the elapsed time.

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*time*copy*lock-in, *time*copy, *time*copy-not-from-super-state

**L15-013** (capacity: look-ahead (agent-world)) — With ^flags.cost-metric unit or time, a look-ahead state that reaches ^success <its desireds> returns ^symbolic-value success together with ^numeric-value equal to the look-ahead world's ^path-cost (L15-021), so cheaper plans are preferred.

*Rationale:* Optimises for temporally shortest plans.

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*apply*evaluate-operator*numeric-evaluation-return*path-cost; Thor-Soar Agent Documentation (thor.txt) Flags ^cost-metric (was ^use-timers)

**L15-014** (capacity: look-ahead (agent-world)) — cutoff-search: in a look-ahead state whose world ^path-cost exceeds the selection state's ^minimum-numeric-value (the best plan so far), when the current evaluation is not that best one, cutoff-search is proposed (best, and better than task operators and find-object). It gives the evaluation ^failure-cutoff true ^value true. It tests ^quiescence t, so no chunk is learned from it.

*Rationale:* Branch-and-bound pruning of longer plans (comment: 'Did not really help').

*Library rules:* agent-world*propose*evaluate-operator*cutoff-search, agent-world*apply*cutoff-search

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/cutoff-search.soar

**L15-015** (capacity: look-ahead (agent-world)) — The desireds are deep-copied for look-ahead: each desired gets a new desired with ^duplicate-of, and only these parts are copied: ^selection-value, ^object (handle and attributes), ^holding-object, relations (argument handles only), ^learn with ^task, ^executed-action, ^info and ^disjunction.

*Rationale:* Grounding (find-object) rewrites object-handles in desireds; changes must be local to the look-ahead.

*Library rules:* agent-world*elaborate*evaluate-operator*copy-desired, *-selection-value, *-object, *-holding-object, *-relation, *-learn*task, *-executed-action, *-info

*See:* related L8-016 (overlap)

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*copy-desired*

**L15-016** (capacity: look-ahead (agent-world)) — The look-ahead state gets ^look-ahead-operator <a shallow copy of the evaluated operator, L14-044> when its ^problem-space.name equals the evaluate-operator's ^super-problem-space.name, and ^external-top-state from the selection's superstate.

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy, *evaluate-operator*external-top-state

**L15-017** (capacity: look-ahead (agent-world)) — The task gives the look-ahead state a ^problem-space whose ^name equals the task state's problem-space name; agent-world does not create it.

*Rationale:* look-ahead-operator, internal-actions and task proposals depend on it.

*If violated:* no task operators proposed in look-ahead; no ^look-ahead-operator

*Task supplies:* yes

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*state*look-ahead-operator*copy; elaborations/problem-space.soar

**L15-018** (capacity: look-ahead (agent-world)) — A look-ahead state marked ^constraint-failure <desireds> with ^failure-string gives its evaluation ^symbolic-value constraint-failure. agent-world then rejects the evaluated operator in the tied state and, at a real state, sends the failure string as a say-sentence message.

*Rationale:* Lets task knowledge veto an operator (e.g. unsafe) and explain why.

*Library rules:* agent-world*compare*selection*select*constraint-failure-becomes-reject

*Source:* agent-world/Impasse__Operator_Tie/elaborations.soar:agent-world*compare*selection*select*constraint-failure-becomes-reject, *constraint-failure-print-out; selection-world selection-world*apply*evaluate-operator*symbolic-evaluation*from-subgoal*constraint-failure

**L15-019** (capacity: look-ahead (agent-world)) — A task rule vetoes an operator in look-ahead by adding ^constraint-failure <the state's desireds> and ^failure-string <text> to the look-ahead state.

*Rationale:* The library turns it into a reject preference and a spoken explanation.

*Example:*

```
(<s> ^constraint-failure <desireds> ^failure-string |would burn the toast|)
```

*Task supplies:* yes

*Source:* agent-world/Impasse__Operator_Tie/elaborations.soar

### Cost

**L15-020** (capacity: cost (look-ahead)) — ^flags.cost-metric (default none) selects the cost of a look-ahead path: none (no cost), unit (each task operator costs its ^step-cost, default 1) or time (elapsed look-ahead time). A task sets it through ^flag-override. The flag use-timers is retired.

*Rationale:* One definition of cost for all search modes.

*If violated:* With none, evaluations carry only the task state value.

*Task supplies:* yes

*Library rules:* agent-world/_flags.soar:agent-world*elaborate*flags*default*cost-metric

*Source:* agent-world/elaborations/cost.soar; soar-library CHANGES.md (cost metric, v2.2x); World-Conventions-Spec-v6 section 6

**L15-021** (capacity: cost (look-ahead)) — The look-ahead world carries ^path-cost, the cost of the operators applied so far: 0 at the top selection, copied down like ^time, and increased by ^step-cost for each task operator applied (unit) or equal to the look-ahead ^time (time).

*Rationale:* The numeric value an evaluation passes back is the path cost; lower is better.

*If violated:* Evaluations pass back no cost.

*Task supplies:* yes

*Library rules:* agent-world/elaborations/cost.soar:agent-world*elaborate*evaluate-operator*path-cost*copy*lock-in, ...copy, ...copy-not-from-super-state, ...time; agent-world*apply*operator*step-cost

*Source:* agent-world/elaborations/cost.soar; soar-library CHANGES.md (cost metric, v2.2x); World-Conventions-Spec-v6 section 6

**L15-022** (capacity: cost (look-ahead)) — Only task operators accrue cost under cost-metric unit; internal operators (evaluate-operator, cutoff-search, finish-future-event) do not. Under cost-metric time the task supplies ^action-time on operators and advances the look-ahead ^time.

*Rationale:* Avoids double counting of composite operators and keeps unit cost a count of task steps.

*If violated:* Costs are wrong or counted twice.

*Task supplies:* yes

*Library rules:* agent-world/elaborations/cost.soar:agent-world*elaborate*operator*step-cost*default

*Source:* agent-world/elaborations/cost.soar; soar-library CHANGES.md (cost metric, v2.2x); World-Conventions-Spec-v6 section 6

**L15-023** (capacity: cost (look-ahead)) — Under a cost metric the library adds ^better lower to the top state's desireds unless the task has stated ^better. The rule is o-supported because it tests that ^better is absent.

*Rationale:* A cost is minimized by default.

*If violated:* The selection compares costs the wrong way.

*Task supplies:* yes

*Library rules:* agent-world/elaborations/cost.soar:agent-world*elaborate*desireds*better*lower*cost-metric

*Source:* agent-world/elaborations/cost.soar; soar-library CHANGES.md (cost metric, v2.2x); World-Conventions-Spec-v6 section 6

## L16 Iterative deepening

Holds when the iterative-deepening strategy is in use.

### Naming and files

**L16-001** (capacity: iterative deepening) — Iterative deepening is a strategy inside selection-world (selection-world/strategies/iterative-deepening), chosen in strategies_source.soar and loaded with the library; it is not loaded separately.

*Rationale:* Its rules test structures created only by selection-world (^top-selection, ^selection-superstate, ^evaluation with ^value true and ^desireds.duplicate-of, evaluate-operator proposal/evaluation creation), agent-world (^flags copy, ^success, ^pre-conditions-satisfied, ^unachieved-desireds-count) and simple.soar (state ^name from superoperator).

*If violated:* no evaluations, depth or flags are ever seen; the library's rules never match

*Task supplies:* yes

*Library rules:* selection-world: selection-world*elaborate*selection*top-selection, selection-world*elaborate*selection*selection-substate(*copy), selection-world*propose*selection*evaluate-operator, selection-world*apply*selection*state*evaluation; agent-world: agent-world*elaborate*substate*flags

*Source:* default-world/soar-base/simple.soar (pushd agent-world/selection/selection-world); selection-iterative-deepening.soar

**L16-002** (capacity: iterative deepening) — Task rules must not use the names iterative deepening reserves. Operator names: exceed-depth, achieved-max-depth, init-current-evaluation-depth, init-remaining-operators, increment-current-evaluation-depth, decrement-remaining-operators, remove-evaluation, all-evaluations-failed and initialize-failure-evaluation. Attributes: current-evaluation-depth, max-evaluation-depth, remaining-operators, item-no-evaluation, minimum-numeric-value, applied-lookahead and depth-exceeded.

*Rationale:* Library rules match these operator names in any state, and the attributes drive the library's control logic.

*If violated:* library rules fire on task structures or vice versa; corrupted depth control

*Source:* selection-world/strategies/iterative-deepening/(all proposals); selection-world/strategies/iterative-deepening/

### Flags and constants

**L16-003** (capacity: iterative deepening) — ^flags.iterative-step selects what one step of the depth bound is: operator (one step per task-operator application in look-ahead; the default), tie-impasse (one step per nested tie: each evaluate-operator state's depth is the evaluated operator's depth minus 1) or cost (the bound is a cap on ^path-cost; it implies cost-metric unit when the task states no metric). A task sets it through ^flag-override. The flag controls how far the search goes, not how solutions are compared (L16-034).

*Rationale:* All depth-decrement and depth-cutoff rules are split by this flag, and they test its exact values. It separates search control from solution cost.

*If violated:* with no valid value no evaluate-operator state gets a ^current-evaluation-depth and depth is never cut off; search control and cost conflated

*Example:*

```
(<flags> ^iterative-step tie-impasse)
```

*Task supplies:* yes

*Library rules:* selection-world*elaborate*evaluate-operator*current-evaluate-depth, selection-world*elaborate*evaluate-operator*current-evaluate-depth*tie-impasse, selection-world*apply*operator*internal*iterative-deepening

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*current-evaluate-depth(*tie-impasse); selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/exceed-depth.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/exceed-depth.soar; JEL, 12 Nov 2026 (LF-22); selection-iterative-deepening; agent-world evaluate-operator elaborations (numeric-value from time); selection-world/strategies/iterative-deepening/(grep ^flags.)

**L16-004** (capacity: iterative deepening) — ^flags.init-evaluation-depth selects the starting depth: one (depth 1; the default) or unachieved-desireds (the number of unachieved desireds of the tied state, and 2 when there are 2 or fewer).

*Rationale:* init-current-evaluation-depth is proposed only for these two values (unless ^flags.verify true).

*If violated:* the top selection never gets ^current-evaluation-depth; evaluate-operator is never given a depth and deepening never starts

*Example:*

```
(<flags> ^init-evaluation-depth unachieved-desireds)
```

*Task supplies:* yes

*Library rules:* selection-world*apply*init-current-evaluation-depth

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar: selection-world*propose*selection*init-current-evaluation-depth*top-selection*one, *top-selection, *top-selection*1

### World/state

**L16-005** (capacity: iterative deepening) — The real world is marked ^world.real true (initialize-agent-world does this). Look-ahead rules under ^iterative-step tie-impasse recognize a hypothetical state by -^world.real true.

*Rationale:* Separates look-ahead from real execution.

*If violated:* best preferences for applicable operators would also be given in the real task state

*Library rules:* agent-world initialize

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar; agent-world/initialize-agent-world.soar

### Desireds bookkeeping

**L16-006** (capacity: iterative deepening) — Desireds are copied into each evaluate-operator state (desired objects are created again, with ^duplicate-of) because grounding can change object handles in look-ahead. The search uses ^desireds.duplicate-of to tie each result to its evaluation.

*Rationale:* Look-ahead changes must stay local.

*If violated:* n/a

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:agent-world*elaborate*evaluate-operator*copy-desired*

**L16-007** (capacity: iterative deepening) — The desireds of the state above the top selection must have ^unachieved-desireds-count (agent-world computes it): the depth initialization tests it, also when ^flags.init-evaluation-depth is one.

*Rationale:* Initial depth heuristic = number of unachieved goals.

*If violated:* no depth initialisation

*Library rules:* agent-world/elaborations/achieved-desireds.soar

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar

### Task operators

**L16-008** (capacity: iterative deepening) — A task operator must have ^pre-conditions-satisfied true when it is applicable (agent-world adds it when the operator's ^desireds are all achieved): the depth decrement and the tie-impasse bookkeeping test it.

*Rationale:* Distinguishes applying an operator from subgoaling on its preconditions (MEA).

*If violated:* operator mode never decrements depth: unbounded look-ahead

*Task supplies:* yes

*Library rules:* agent-world*elaborate*operator*pre-conditions-satisfied

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar; agent-world/elaborations/achieved-desired-operators.soar:agent-world*elaborate*operator*pre-conditions-satisfied

### Output and events

**L16-009** (capacity: iterative deepening) — The depth monitor writes 'Depth: <ced>: <value> remaining, <n>' whenever the top selection's depth or remaining count changes.

*Rationale:* Trace of deepening progress.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/elaborations.soar:selection-world*elaborate*selection*monitor*depth

### Substates (general)

**L16-010** (capacity: iterative deepening) — soar max-goal-depth allows the nesting of look-ahead and MEA substates at the maximum search depth; agent-world sets 50.

*Rationale:* Each depth unit can add a selection, evaluate-operator and MEA substates.

*If violated:* goal-stack overflow

*Source:* agent-world/_flags.soar (max-goal-depth 50)

### Selection space

**L16-011** (capacity: iterative deepening) — Iterative deepening works on the selection-world selection space: the selection state has ^name selection; an evaluation is (<s> ^evaluation <e>) with (<e> ^super-operator <item> ^desireds <d2>), <d2> ^duplicate-of the tied state's desireds, and ^value true once it has any value.

*Rationale:* ID rules test exactly these selection-world structures.

*If violated:* ID rules never match evaluations

*Library rules:* selection-world*apply*selection*state*evaluation, selection-world*elaborate*selection*evaluation*desireds

*Source:* selection-world/Operator_Tie/elaborations.soar: selection-world*elaborate*selection*evaluation*value, selection-world*elaborate*selection*evaluation*desireds; ID elaborations.soar

**L16-012** (capacity: iterative deepening) — Iterative deepening reads the architectural ^item-count of the tie substate (the number of tied operators) for ^remaining-operators and for all-evaluations-failed.

*Rationale:* Architecture provides it.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-remaining-operators.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/Impasse__Operator_Tie/all-evaluations-failed.soar

**L16-013** (capacity: iterative deepening) — An evaluation whose ^super-operator is no longer a tied ^item is removed by the operator remove-evaluation (best, and better than decrement-remaining-operators and init-current-evaluation-depth).

*Rationale:* The ^item set can change during an impasse.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/remove-evaluation.soar

**L16-014** (capacity: iterative deepening) — Under iterative deepening, when the selection has ^remaining-operators 0, two tied operators with the same symbolic evaluation are made indifferent (the second must have ^task-operator true), except for success, partial-success, depth-exceeded, exhaustion-failure and depth-exhaustion; two closed success evaluations are made indifferent when the desireds have no ^better. With ^remaining-operators 1 and no ^item-no-evaluation the first rule also applies, and it includes success. The general rules are in L14-013; the maximum depth is handled by achieved-max-depth (L16-031).

*Rationale:* Breaks ties among equally good options only after the pass is complete.

*If violated:* n/a

*See:* related L14-013

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/elaborations.soar:selection-world*compare*selection*same-symbolic-evaluations-are-indifferent*task-operators, *success*no-better, *no-eval

### Look-ahead / evaluation

**L16-015** (capacity: iterative deepening) — depth-exceeded and depth-exhaustion evaluations are excluded from the indifference rules and create no preference by themselves; only achieved-max-depth turns them into worst preferences.

*Rationale:* They are provisional until the deepest iteration.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/elaborations.soar; selection-world/Operator_Tie/elaborations.soar:selection-world*compare*selection*same-symbolic-evaluations-are-indifferent; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/achieved-max-depth.soar

**L16-016** (capacity: iterative deepening) — A look-ahead state with ^success <d2>, where <d2> has ^duplicate-of the evaluation's ^desireds, gives the evaluation ^symbolic-value success; success becomes a best preference for the tied operator (but see L14-034 and L16-036).

*Rationale:* Standard selection-world flow, unchanged by ID.

*If violated:* n/a

*Library rules:* agent-world achieved-desireds (^success <desireds>)

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar:evaluate-operator*elaborate*symbolic-evaluation*from-subgoal*success*no*better; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:evaluate-operator*elaborate*numeric-evaluation-return*time; selection-world selection-world*compare*selection*select*success-evaluation-becomes-best-preference

**L16-017** (capacity: iterative deepening) — Success is not passed back from a nested selection to its parent evaluation directly (the pass-back rules are commented out because they broke chunking); the parent evaluation succeeds only when its own evaluate-operator state reaches ^success after the nested tie is resolved.

*Rationale:* Avoids chunking problems with iterative deepening.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/Impasse__Operator_Tie/elaborations.soar (commented selection*pass-back-success*iterative, *iterative2)

**L16-018** (capacity: iterative deepening) — Failure is passed up from a nested selection only when it is not the top selection, has ^remaining-operators 0 and ^item-count from 2 to 10 (2 to 6 before library v2.40), and every one of its evaluations has ^symbolic-value failure; then all-evaluations-failed marks the parent evaluation ^symbolic-value failure. A tie of more than 10 operators only prints a warning.

*Rationale:* A state whose every option fails is itself a failure.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/Impasse__Operator_Tie/all-evaluations-failed.soar

**L16-019** (capacity: iterative deepening) — A state no-change in look-ahead, with no ^world.future-event pending, proposes initialize-failure-evaluation. At quiescence it marks the evaluation of the nearest selection's selected evaluate-operator as failure, or as depth-exhaustion if some evaluation in that selection is depth-exceeded or depth-exhaustion. If that selection has no selected evaluate-operator, the next selection up is used.

*Rationale:* A dead end is a real failure only if no sibling evaluation was depth-limited.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/initialize-failure-count.soar

**L16-020** (capacity: iterative deepening) — Each selection keeps ^minimum-numeric-value, the smallest ^numeric-value (other than novalue) of its evaluations; a nested selection inherits its parent's minimum. Larger or out-of-date values are removed (o-support).

*Rationale:* Branch-and-bound on time-to-goal across look-ahead levels.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/elaborations.soar:selection-world*elaborate*selection*minimum*numeric-value(*pass-down, *remove-invalid-*)

**L16-021** (capacity: iterative deepening) — The ^duplicate-look-ahead-operator gets a require preference while depth remains: under iterative-step operator while ^current-evaluation-depth.value > 0, under tie-impasse while it is >= 0. Once depth is used up, exceed-depth is selected.

*Rationale:* Ensures the evaluated operator is applied first.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar:selection-world*compare*evaluate-operator*select*duplicate-look-ahead(*tie-impasse); selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/exceed-depth.soar:selection-world*compare*evaluate-operator*exceed-depth*duplicate

**L16-022** (capacity: iterative deepening) — The failure-evaluation counting operators (count-object, count-relation, count-desired-object, count-desired-relation, count-name-finish) apply only in a state named failure-evaluation that has ^feature-count. No library rule creates such a state, so they are inactive unless a task supplies it. count-name-finish also requires ^world.self and optionally ^world.last-moved-object-handle, which no shared-library rule creates.

*Rationale:* Remnant of a domain-specific feature-count heuristic evaluation.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/count-*.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/elaborations.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/count-name-finish.soar

### Iterative deepening

**L16-023** (capacity: iterative deepening) — Several iterative-deepening searches can be active at once, one for each top selection (a tie that is not below a selection state).

*Rationale:* Top-selection is defined per tie, so ties in different MEA substates each run their own deepening.

*If violated:* n/a

*Library rules:* selection-world*elaborate*selection*top-selection

*Source:* selection-world/Operator_Tie/evaluate-operator/elaborations.soar comment 'Can have multiple active iterative deepening going for different intermediate goals/states'

**L16-024** (capacity: iterative deepening) — The top selection holds the current depth as an object, (<sel> ^current-evaluation-depth <ced>) (<ced> ^value <n>), created with o-support by the operator init-current-evaluation-depth. A nested selection state shares the ^current-evaluation-depth identifier of its superstate (an i-supported copy of the pointer), so it does not run init-current-evaluation-depth. Because the depth state is held on the top selection substate, it is lost when the tie is resolved: the next tie starts again from the initial depth.

*Rationale:* An object (not a constant) lets the value be shared and changed in place by lower states. Depth remaining is inherited from the evaluate-operator (or MEA) state containing the nested tie. Substate WMEs are removed with the impasse.

*If violated:* n/a

*Example:*

```
(S5 ^current-evaluation-depth C1) (C1 ^value 3)
```

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar:selection-world*apply*init-current-evaluation-depth; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/elaborations.soar:selection-world*elaborate*selection*current-evaluate-depth; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar

**L16-025** (capacity: iterative deepening) — Each evaluate-operator operator is elaborated with ^current-evaluation-depth.value <v> and ^remaining-operators <r> from the selection state, unless an evaluation already has a value at this depth for the same item or for the same remaining count. When evaluate-operator is selected, its evaluation is stamped (o-support) with the same two values.

*Rationale:* Tags each evaluation with the depth and slot it was computed for; decrement-remaining-operators matches evaluations by depth and remaining count.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator.soar:selection-world*elaborate*selection*evaluate-operator*current-evaluation-depth; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator.soar:selection-world*apply*selection*evaluate-operator*remaining-operators*current-evaluation-depth, *2

**L16-026** (capacity: iterative deepening) — How depth is charged. Under iterative-step operator: the evaluate-operator state gets a new ^current-evaluation-depth object with the same value as the evaluate-operator's; applying a selected operator with ^pre-conditions-satisfied true in a state that has ^current-evaluation-depth decrements that object's ^value by 1 and marks the state ^applied-lookahead true, at most once per state. The decrement removes an i-supported ^value (created by an elaboration) with an o-supported reject, leaving the depth object with an o-supported value (confirmed with a 3-rule test agent in Soar 9.6.5). Under iterative-step tie-impasse: the evaluate-operator state gets its own ^current-evaluation-depth object whose ^value is the evaluate-operator's value minus 1; in a state whose world is not real, a proposed operator with ^pre-conditions-satisfied true gets a best preference, and applying it marks the state ^applied-lookahead true.

*Rationale:* Operator mode charges one depth unit per applied look-ahead operator, with a once-per-state guard against repeated decrements. Tie mode charges one unit per look-ahead level and prefers directly applicable operators over operators needing MEA subgoaling. Mixed support on the depth object is fragile if the elaboration re-fires.

*If violated:* a second operator applied in the same state is not charged

*Example:*

```
(<ced> ^value <v> - (- <v> 1))
```

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:selection-world*elaborate*evaluate-operator*current-evaluate-depth, *tie-impasse; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar:selection-world*apply*operator*internal*iterative-deepening; runtime check (this extraction) of the pattern in selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar:selection-world*apply*operator*internal*iterative-deepening; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar:selection-world*compare*operator*maintain-operator*preconditions-satisfied, selection-world*apply*operator*internal*iterative-deepening*tie-impasse-step

**L16-027** (capacity: iterative deepening) — The top selection's ^remaining-operators counts the tied items still to be evaluated at the current depth. init-remaining-operators (best) sets it to ^item-count; it is decremented once for each evaluation that gets a value at this depth, and reset to ^item-count on each depth increment.

*Rationale:* Detects when a full pass over the tied operators at this depth is complete.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-remaining-operators.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/decrement-remaining-operators.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar:selection-world*apply*increment-current-evaluation-depth

**L16-028** (capacity: iterative deepening) — decrement-remaining-operators (best, and better than the depth increment) applies when an evaluation stamped with the current depth and remaining count has ^value true, or when a success evaluation from this or a shallower depth matches the remaining count.

*Rationale:* Counts evaluations completed in this pass.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/decrement-remaining-operators.soar

**L16-029** (capacity: iterative deepening) — When the top selection has ^remaining-operators 0, or every tied item has an evaluation with ^value true, increment-current-evaluation-depth (best) adds 1 to ^current-evaluation-depth.value and resets ^remaining-operators to ^item-count. The second condition is needed because a chunk learned at a shallower depth can resolve a tie without decrementing ^remaining-operators.

*Rationale:* One iteration of iterative deepening per pass over all tied operators; keeps deepening progressing when chunks short-circuit evaluation.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar comment 'Can arise from chunks applying without a decrement of remaining-operators'

**L16-030** (capacity: iterative deepening) — On a depth increment, every evaluation with ^value true is removed unless its symbolic value is failure, exhaustion-failure or success, or it has a ^numeric-value. depth-exceeded, depth-exhaustion, partial-success, failed-grounding and failure-cutoff evaluations (^failure-cutoff true is set by cutoff-search, L15-014) are therefore computed again at the new depth. Also, when evaluate-operator is selected for an item, an older evaluation of that item that was computed at another depth and has neither success nor a numeric value is removed, so that a new evaluation is created.

*Rationale:* Only depth-independent results are kept between iterations, and stale depth-limited values must not block re-evaluation.

*If violated:* n/a

*Library rules:* selection-world*apply*selection*state*evaluation

*See:* related L20-018 (overlap)

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar:selection-world*apply*increment-current-evalaution*clean-up-evaluations; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator.soar:selection-world*apply*evaluate-operator*clean-up-evaluations; agent-world/Impasse__Operator_Tie/evaluate-operator/cutoff-search.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar

**L16-031** (capacity: iterative deepening) — The depth bound stops at ^flags.max-evaluation-depth (default 12). When ^current-evaluation-depth.value reaches it, achieved-max-depth is proposed (worse than evaluate-operator); applied, it gives best to tied operators with success evaluations, and worst to operators with depth-exceeded, depth-exhaustion or exhaustion-failure evaluations and to unevaluated items.

*Rationale:* Bounds the deepening and commits to the best known choice.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/achieved-max-depth.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar

**L16-032** (capacity: iterative deepening) — When the depth is used up, exceed-depth ends the branch. Under iterative-step tie-impasse: in a selection state (^impasse tie, ^quiescence t) whose ^current-evaluation-depth.value is <= 0 and that has no ^depth-exceeded, exceed-depth is proposed with a best preference; applying it puts ^depth-exceeded <d> on the selection state, where <d> is the parent evaluation's ^desireds, and the parent evaluation (the one on the selection-superstate's selected evaluate-operator, with ^desireds <d>) gets ^symbolic-value depth-exceeded. Under iterative-step operator: in an evaluate-operator state whose ^current-evaluation-depth.value is <= 0, exceed-depth is proposed best and better than every other proposed operator; applying it puts ^depth-exceeded <desireds> on that state, and the evaluation whose ^desireds is <desireds>.duplicate-of gets ^symbolic-value depth-exceeded.

*Rationale:* A tie at zero remaining depth, or a look-ahead whose operator budget is spent, ends that branch and returns 'not decided at this depth' plus an optional lower-bound time.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/exceed-depth.soar:selection-world*propose*selection*exceed-depth*tie-impasse, selection-world*apply*exceed-depth*tie-impasse; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/exceed-depth.soar:selection-world*apply*evaluate-operator*symbolic-evaluation*from-tie-subgoal*depth-exceeded(*numeric); selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/exceed-depth.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/elaborations.soar:selection-world*apply*evaluate-operator*symbolic-evaluation*from-subgoal*depth-exceeded

**L16-033** (capacity: iterative deepening) — Iterative deepening returns a solution with the fewest steps (of the kind selected by ^iterative-step) when ^cost-metric is none. It gives no bound on the number of states searched, with or without chunking.

*Rationale:* Iterative deepening explores depth d fully before d+1.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/_firstload.soar header

**L16-034** (capacity: iterative deepening) — Solutions are compared by a task-defined cost. A task operator may carry ^step-cost (a positive number); under cost-metric unit the library uses 1 when it has none (^effective-step-cost), so the default cost is the number of task operators. With cost-metric none (the default, L15-020) no cost is computed. In Thor-Soar an operator's step-cost is its internal time estimate.

*Rationale:* One general cost for any task: operator count, time, or anything else.

*If violated:* all tasks compare by time (zero when none passes), so shortest plans are not found

*Example:*

```
(<op> ^step-cost 1)
```

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (LF-22); selection-iterative-deepening; agent-world evaluate-operator elaborations (numeric-value from time)

**L16-035** (capacity: iterative deepening) — Under a cost metric the library keeps ^path-cost on the look-ahead world (0 at the top selection, copied down like ^time). Under unit it adds the ^step-cost of each task operator applied; under time it equals the look-ahead ^time, which includes waits (L15-021). ^step-cost must be positive: a zero-cost operator can keep a cut-off branch below the solution's cost at every depth, and the search need not end.

*Rationale:* Gives every look-ahead a cost without task-written arithmetic.

*If violated:* numeric values missing or time-only

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (LF-22); selection-iterative-deepening; agent-world evaluate-operator elaborations (numeric-value from time)

**L16-036** (capacity: iterative deepening) — A success of path-cost c is accepted (best preference) only when every depth-exceeded branch at the current bound has a path-cost of at least c at its cut-off; otherwise the bound is incremented and the search continues. With unit costs this is the first success at a depth; with unequal costs it gives the cheapest solution.

*Rationale:* Deepening by tie depth finds the cheapest solution only if cutoff branches cannot be cheaper.

*If violated:* a solution within the depth bound can cost more than an unfinished cutoff branch

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (LF-22); selection-iterative-deepening; agent-world evaluate-operator elaborations (numeric-value from time)

**L16-037** (capacity: iterative deepening) — ^step-cost (an operator attribute) and ^path-cost (a world attribute) are reserved names. ^path-cost must not be an operator attribute: every operator attribute is copied onto the operator's no-change substate.

*Rationale:* Avoids collision between operator and state attributes (L6-004).

*If violated:* path-cost on a substate overwritten by the operator copy

*Task supplies:* yes

*Source:* JEL, 12 Nov 2026 (LF-22); selection-iterative-deepening; agent-world evaluate-operator elaborations (numeric-value from time)

### MEA operator subgoaling

**L16-038** (capacity: iterative deepening) — A substate whose ^problem-space.name equals its superstate's (an MEA subgoal) shares the superstate's ^current-evaluation-depth identifier; an MEA subgoal therefore keeps the ^problem-space.name of the state that created it. An operator-implementation substate has the operator's name as problem-space name and does not share it.

*Rationale:* Depth spent inside MEA subgoals during look-ahead is charged to the same counter as the evaluate-operator state; the copy rule requires equal problem-space names.

*If violated:* MEA substates in look-ahead would have no depth bound

*Library rules:* agent-world problem-space elaborations

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/elaborations.soar:selection-world*elaborate*task*current-evaluation*depth; agent-world/generic-operator/elaborations.soar:agent-world*elaborate*operator-implementation-substate*super-operator-problem-space

### Learning: chunking

**L16-039** (capacity: iterative deepening) — Depth-limited outcomes (exceed-depth in a tie, initialize-failure-evaluation) are computed only at ^quiescence t, so no chunk is learned from them.

*Rationale:* A depth-limited result is not a property of the task and must not be cached.

*If violated:* chunks would encode depth-cutoff results as real evaluations

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/exceed-depth.soar:selection-world*propose*selection*exceed-depth*tie-impasse; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/initialize-failure-count.soar

## L17 MEA operator subgoaling

Holds when means-ends (MEA) operator subgoaling is in use.

### MEA operator subgoaling

**L17-001** (capacity: MEA operator subgoaling) — In an operator no-change substate whose superoperator has ^desireds and no ^pre-conditions-satisfied true, the library creates a local ^desireds with ^duplicate-of <the operator's desireds>, the same ^desired-count, the same ^desired identifiers, and ^world-context. ^preferred-desired and ^avoid-desired are copied only when ^flags.desired-preferences is true.

*Rationale:* The substate's goal is the superoperator's preconditions; achieved marks stay local (no o-supported results on the operator).

*Library rules:* same

*Source:* agent-world/elaborations/_all.soar:agent-world*elaborate*substate*operator*desireds, ...*desired, ...*world-context, ...*preferred-desired, ...*avoid-desired

**L17-002** (capacity: MEA operator subgoaling) — An operator selected while its preconditions are unsatisfied has no application; the resulting operator no-change substate has those preconditions as its desireds (means-ends operator subgoaling).

*Rationale:* Achieves preconditions recursively.

*Library rules:* agent-world*elaborate*substate*operator*desireds

*Source:* Thor-Soar Agent Documentation (thor.txt) "Simple Composite Task Operators", "Task Action Operator"; agent-world/elaborations/_all.soar:agent-world*elaborate*substate*operator*desireds

**L17-003** (capacity: MEA operator subgoaling) — In a chain of operator no-change substates with the same ^problem-space.name, ^failure <desireds> on a substate (for its own ^desireds) is passed up as ^failure <the superstate's desireds>.

*Rationale:* Lets a failure deep in an MEA stack reach the look-ahead state, where selection-world turns ^failure into an evaluation.

*Library rules:* pass-back-failure-mea-subgoaling*

*Source:* agent-world/generic-operator/failure.soar:pass-back-failure-mea-subgoaling, pass-back-failure-mea-subgoaling2

**L17-004** (capacity: MEA operator subgoaling) — A task rule that detects a dead end in means-ends subgoaling marks the substate with ^failure <its desireds>; agent-world passes it up.

*Rationale:* The failure is then turned into a look-ahead evaluation.

*Example:*

```
(<s> ^failure <desireds>)
```

*Task supplies:* yes

*Library rules:* pass-back-failure-mea-subgoaling*

*Source:* agent-world/generic-operator/failure.soar

## L18 Time and future events

Holds when time, future events or idle waiting are in use.

### Desireds bookkeeping

**L18-001** (capacity: time and future events) — A future event may carry ^new-desired <d>. At completion <d> is added to the top state's desireds as ^desired and ^required-desired, and ^desired-count is incremented (one per decision).

*Rationale:* Lets a process create a follow-up goal (e.g. remove the food when cooked).

*Task supplies:* yes

*Source:* agent-world/elaborations/future-event.soar:agent-world*apply*complete*future-event*add-desired*external-not-visible

### Output and events

**L18-002** (capacity: idle (wait)) — dispatch-agent-event-idle: in a state no-change directly under the external top state, when the top state has no ^desireds, dispatch-agent-event-idle is proposed (worst, and better than wait). It applies at quiescence by adding ^agent-event.name idle to the output-link, and is not proposed again while that event is present.

*Rationale:* Tells the environment/interaction layer that the agent is idle.

*Example:*

```
(<out> ^agent-event.name idle)
```

*Library rules:* agent-world*propose*top*state-no-change*propose*dispatch-agent-event-idle, agent-world*apply*top*state-no-change*apply*wait*dispatch*agent-event*idle

*Source:* agent-world/Impasse__State_No-Change/dispatch-agent-event-idle.soar

### Time and future events

**L18-003** (capacity: time and future events) — The real world's ^time is an i-supported copy of ^io.input-link.time.ms. In look-ahead, time is computed from models of operator durations.

*Rationale:* Time-based planning needs a current time.

*Library rules:* agent-world*elaborate*state*time

*Source:* agent-world/elaborations/time.soar:agent-world*elaborate*state*time; Thor-Soar Agent Documentation (thor.txt) 'World'

**L18-004** (capacity: time and future events) — The environment must supply ^io.input-link.time.ms (milliseconds).

*Rationale:* Source of world time.

*If violated:* world has no time; timed look-ahead breaks

*Task supplies:* yes

*Library rules:* agent-world*elaborate*state*time

*Source:* agent-world/elaborations/time.soar

**L18-005** (capacity: time and future events) — A future event is (<world> ^future-event <e>) with (<e> ^type <t> ^completion-time <ms> ^property-change <pc> [^primary-property-change <pc>] [^new-desired <d>] [^argument1 <obj>] [^argument2 <obj>]) and (<pc> ^object <obj> ^property-handle <attr> ^original-property-value <v> or no-value ^new-property-value <v2>).

*Rationale:* agent-world completes events generically from this structure.

*If violated:* events never complete, or complete with wrong values

*Example:*

```
(<e> ^type cook ^completion-time 15950 ^argument1 <microwave> ^property-change <pc>) (<pc> ^object <potato> ^property-handle cook-state ^original-property-value raw ^new-property-value cooked)
```

*Task supplies:* yes

*Library rules:* agent-world*apply*complete*future-event*change-property*

*Source:* agent-world/elaborations/future-event.soar; agent-world/Impasse__Operator_Tie/evaluate-operator/finish-future-event.soar; Thor-Soar Agent Documentation (thor.txt) 'Turn-on', 'cCTO' (future-event)

**L18-006** (capacity: time and future events) — ^property-change.object is the identifier of the world object (in look-ahead, of the copied object) and ^property-handle is the attribute name. ^original-property-value no-value means the attribute is absent now and the change only adds the new value.

*Rationale:* Completion rules match (<object> ^<property-handle> <original-property-value>) by identity.

*If violated:* the change is never applied

*Task supplies:* yes

*Source:* agent-world/elaborations/future-event.soar:agent-world*apply*complete*future-event*change-property*external-not-visible*no-value; *look-ahead*no-value

**L18-007** (capacity: time and future events) — The objects a pending future event locks are its ^argument1 and ^argument2. An operator with such an object as an argument is marked ^future-event-disruption true (except go-to) and made worst; a task operator that uses one is rejected when ^problem-space.agent-world is true.

*Rationale:* Objects in an ongoing process (e.g. a potato cooking in the microwave) are unavailable until it ends.

*Source:* agent-world/elaborations/future-event.soar:agent-world*reject*operators*disturbing*future-event, *future-event2, agent-world*compare*future-event, *future-event2

**L18-008** (capacity: time and future events) — On a state that is its own ^top-state, a ^future-event whose completion-time is not later than the world's ^time is removed (except events of type broken-egg).

*Library rules:* agent-world*apply*clear*future-event

*Source:* agent-world/elaborations/future-event.soar:agent-world*apply*clear*future-event

**L18-009** (capacity: time and future events) — In the real world, agent-world applies a completed future event's property change only to objects that are not visible (-^derived-from-input.visible true); perception updates visible objects.

*Rationale:* Predicts changes to objects the agent cannot see (e.g. inside a closed microwave).

*Source:* agent-world/elaborations/future-event.soar:agent-world*apply*complete*future-event*change-property*external-not-visible (+ *property-not-exist, *no-value)

**L18-010** (capacity: time and future events) — If an event's ^primary-property-change already holds in the world before its completion-time, the completion-time is reset to the current time.

*Rationale:* Handles processes that finished earlier than predicted.

*Source:* agent-world/elaborations/future-event.soar:agent-world*elaborate*future-event*unexpected-completion

**L18-011** (capacity: time and future events) — In look-ahead (^internal-actions true) a completed future event's property change is applied to any object, visible or not.

*Source:* agent-world/elaborations/future-event.soar:agent-world*elaborate*complete*future-event*change-property*look-ahead, *look-ahead*no-value

**L18-012** (capacity: grounding, time and future events) — For time-based evaluation, internal application rules (or the time model) advance the world's ^time in look-ahead; an operator may state its duration as ^action-time (in ms).

*Rationale:* The numeric evaluation is the world time at success.

*If violated:* all plans evaluate to the same time

*Example:* ^action-time 2000

*Task supplies:* yes

*Source:* agent-world/find-object/assume-successful-grounding.soar; Thor-Soar Agent Documentation (thor.txt) Constants ^action-time; World ^time

## L19 Goal completion and memory storage

Holds when goal completion or semantic-memory storage is in use.

### Desireds bookkeeping

**L19-001** (capacity: goal completion) — goal-completed is proposed at the top state (worst, indifferent) when the state has ^success or ^required-success <desireds>, the desireds have no ^next-desireds, and the world is real and anchored. The operator carries ^completed-desireds <desireds>.

*Rationale:* Ends a task in the real world.

*Library rules:* agent-world*propose*goal-completed

*Source:* agent-world/goal-completed.soar:agent-world*propose*goal-completed

**L19-002** (capacity: goal completion, smem storage) — When goal-completed is selected the library logs 'Task achieved' with the input-link time; with ^flags.agent-mode testing it outputs ^report-test-result.result success; with ^flags.smem-store true it stores the scene and the smem-storage-structure in semantic memory.

*Source:* agent-world/goal-completed.soar:agent-world*apply*goal-completed*log*achievement, *report-test-result, *store-smem*

**L19-003** (capacity: goal completion) — goal-completed is implemented in a substate by clean-up-topstate (best, indifferent). With ^flags.desireds-source language it removes the completed desireds from the top state; it marks the interaction's top segment satisfied when its satisfaction is achieved-desireds, and removes the task-goal learning events and all executed-action and failed-action events.

*Library rules:* agent-world*propose*goal-completed*clean-up-topstate, goal-completed*apply*clean-up-topstate*

*Source:* agent-world/goal-completed/clean-up-topstate.soar

**L19-004** (capacity: goal completion) — With ^flags.desireds-source elaboration, a wait selected in a state whose super-superstate has goal-completed selected causes (interrupt).

*Source:* agent-world/goal-completed.soar:agent-world*apply*goal-completed*interrupt

### Search control

**L19-005** (capacity: smem storage) — An operator named smem-query is better than every task operator.

*Rationale:* Retrieve knowledge before acting.

*Library rules:* agent-world*compare*task-operator-smem-query

*Source:* agent-world/elaborations/search-control.soar:agent-world*compare*task-operator-smem-query

### Other

**L19-006** (capacity: smem storage) — agent-world cleans the smem command link: a ^retrieve or ^query command is removed once ^smem.result has success or failure, and a ^store <id> once ^result.success <id> appears. It never changes the ^result structure.

*Rationale:* Lets the next command be issued without per-task cleanup.

*Library rules:* smem*apply*clean-up*

*Source:* agent-world/elaborations/smem.soar:object-world*elaborate*smem*clean-up*retrieve, *query, *store

## L20 Thor-Soar

Applies only to Thor-Soar (the Thor-specific sheet).

### Flags and constants

**L20-001** — ^constants on the top state holds values used in reasoning, not switches: ^action-time, ^decision-time, ^food-cook-time (ms), ^desired-object-states, ^desired-orderings.

*Rationale:* Separate parameters from processing switches.

*Task supplies:* yes

*Library rules:* agent-world*desired-selection-value* rules

*Source:* Thor-Soar Agent Documentation (thor.txt) "Constants"

**L20-002** — Thor flags also include clean-up-on-success, desireds-source, desired-selection, mea-operator-selection and cost-metric (which replaced use-timers).

*Rationale:* Experiment configuration.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Flags"

**L20-003** (capacity: selection-world) — With ^flags.hierarchical-properties true, each ^constants.property-abstraction-hierarchy.object-property is added to the copied world as ^abstract-property.

*Rationale:* Supports abstracted look-ahead.

*Source:* selection-world/.../elaborations.soar:selection-world*elaborate*evaluate-operator*state*hierarchical-properties*true

### World/state

**L20-004** (capacity: attention (attend/remove)) — Which handles to attend is task knowledge (in Thor: objects named in desireds, cooking machines, knives for slicing, containers of attended objects, receptacles, sinks and faucets, slices of sliced objects).

*Rationale:* Attention is domain-specific.

*If violated:* needed objects missing from world

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'Attends.attend' (elaborations/attend-objects in Thor)

**L20-005** (capacity: selection-world) — Of the world's ^self, the world copy copies only ^mobile.

*Rationale:* Only those self properties matter in look-ahead.

*Source:* selection-world/.../elaborations.soar:selection-world*elaborate*evaluate-operator*default-state-copy-self, *self*io*pose, *self*pose

### Objects

**L20-006** — Object capability properties (activable, breakable, cookable, cooks, dirtyable, fillable, graspable, openable, reachable, sliceable, toggleable) usually exist only when true; state properties (activated, broken, contains-liquid, dirty, open, reachable, sliced, toggle, cook-state raw/cooked/burnt, liquid empty/coffee/water/wine) hold the current value.

*Rationale:* Thor's object vocabulary derived from input by task elaborations.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Objects.object"

**L20-007** — Objects may also have ^class, ^type (location/container), ^receptable, ^material, ^mass, ^temperature, ^ms-remaining (ms an activated object stays on), ^derived-from-input (debug link to input object) and ^duplicate-of (original in look-ahead).

*Rationale:* Descriptive object attributes.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Objects.object"

### Relations

**L20-008** — ^holding-object on the scene and on the world is the identifier of the held object, or an object with ^object-handle none.

*Rationale:* Single-valued gripper state.

*Task supplies:* yes

*See:* related L20-009 (overlap)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Scene", "World"

### Desireds

**L20-009** — A holding desired is ^desired.holding-object.object-handle <h>, or none for an empty hand.

*Rationale:* Gripper goals.

*Task supplies:* yes

*See:* related L20-008 (overlap)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Desireds" ^holding-object

### Task operators

**L20-010** — An operator may have several MEA proposal rules when it achieves different kinds of desireds (for example toggle on and off, or fill with a named liquid or any liquid).

*Rationale:* Different differences reduced by the same action.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Task Operator Rules", Fill-object, Toggle-object

**L20-011** — A task-action operator has no operator-implementation substate. An operator that needs special external handling (go-to, break) omits ^action-handle, or is excluded by name from the generic rules, and supplies its own external application rules.

*Rationale:* The generic rules only cover the action-handle/argument scheme.

*If violated:* the generic and custom rules both issue commands, or none do

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'Go-to', 'Break'; agent-world/external-operator-application.soar header comment ('Will not work for operators not in the constant-map')

**L20-012** — The set of task operators named in the doc is: break-object, clean-object, close-container, cook-microwave, dirty-object, empty-object, fill-object, get-object, go-to, look-at, open-container, put-in, put-on, slice-object, turn-on, turn-off (and toggle-object).

*Rationale:* Defines the innate Thor action vocabulary.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'Innate Task-Action Operators'

### Composite operators

**L20-013** — For the current cCTOs (cook-microwave, toast, make-coffee, cook-stove) the effect desired is that the machine is ^activated true, achieved by the single implementation operator turn-on.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) 'cCTO'

### Non-task operators

**L20-014** — detect-illegal-desired adds <desireds> ^illegal-desired <d> for unachievable desireds (e.g. in a surface, not cookable) and interrupts.

*Rationale:* Catch impossible goals.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) "Detect-illegal-desired"

**L20-015** (capacity: goal completion) — With ^flags.clean-up-on-success true, after the desireds succeed create-object-state-desired creates new desireds from ^constants.desired-object-states (close open containers, deactivate objects except lights).

*Rationale:* Tidy world after tasks.

*Task supplies:* yes

*Library rules:* goal-completed (outside A1)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Create-object-state-desired", "Constants", "Flags"

### Search control

**L20-016** (capacity: grounding) — While a find-object without ^argument1.origin-object-handle is proposed, most other task operators without ^argument2 are rejected (except slice-object, toast, turn-off, find-object-direct), unless a failed-grounding desired exists; while world ^info.unanchored-object names a handle, all non-grounding operators are rejected in favour of a find-object for that handle.

*Rationale:* Forces grounding before acting.

*Source:* agent-world/find-object.soar:agent-world*compare*find-object*worse2 (### BUG), *reject-other

**L20-017** (capacity: grounding) — find-object-direct search control: smem-query is better than it; all other operators are worse (select immediately); candidates with the same argument2 are indifferent; reachable, accessible and (in the real world) nearer candidates (expected-distance from io.input-link.self.pose) are better.

*Source:* agent-world/find-object-direct.soar:agent-world*compare*find-object-direct*, agent-world*elaborations*compute-distances*find-object-direct

**L20-018** (capacity: selection-world) — An evaluation with ^failure-cutoff true and no numeric value gives its operator a worst preference.

*Rationale:* Prunes branches that are already worse than the best found.

*See:* related L16-030 (overlap)

*Source:* selection-world/Operator_Tie/elaborations.soar:selection-world*compare*selection*worse*failure-cutoff-numeric-value2; agent-world/.../cutoff-search.soar

### Operator application (internal/external)

**L20-019** — turn-on is special: with one object argument it is sent by agent-world*apply*operator*external*argument1*turn-on; with ^argument-count 2 and ^argument2 <time> (not a stoveknob) the time is sent as argument2; other generic rules exclude turn-on.

*Rationale:* Turn-on initiates timed machine dynamics.

*Example:*

```
(<perform> ^name turn-on ^argument1 Microwave47 ^argument2 15000)
```

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument1*turn-on, *turn-on*time; Thor-Soar Agent Documentation (thor.txt) 'Turn-on'

**L20-020** — turn-off has its own external rule; look-at is excluded from the generic one-argument rule and must be applied by task rules.

*Task supplies:* yes

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument1, *argument1*turn-off

**L20-021** — Operators with ^argument-count 3 are sent only with argument1 (handle) and argument2 (no handle); argument3 is dropped, and cook-microwave, make-coffee and toast are excluded by name.

*Rationale:* Special case for turning on the microwave.

*Source:* agent-world/external-operator-application.soar:agent-world*apply*operator*external*argument3*no-handle2 (marked ## BUG)

**L20-022** (capacity: iterative deepening) — The task (or the Thor rules) supplies the look-ahead application of task operators. The search only adds depth bookkeeping to an application that tests ^operator.pre-conditions-satisfied true.

*Rationale:* agent-world has only external application rules; the internal ones are 'in thor-soar for now'.

*If violated:* look-ahead never changes the world; evaluations never succeed

*Task supplies:* yes

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar comment 'See in files in thor-soar for now. Tied to internal operator application rules'

### Substates (general)

**L20-023** — Operator no-change substates also get the superstate's ^scene.

*Library rules:* agent-world*elaborate*substate*scene

*Source:* agent-world/generic-operator/elaborations.soar:agent-world*elaborate*substate*scene

### Look-ahead / evaluation

**L20-024** (capacity: look-ahead (agent-world)) — The Thor problem space turns off the classic selection-space copying (^default-state-copy no ^default-operator-copy no ^default-desired-copy no ^dont-copy top-state): dedicated rules copy the world and the desireds.

*Rationale:* Custom deep copy of world/desireds.

*If violated:* default copy shares world objects with real state

*Task supplies:* yes

*Library rules:* selection-world (outside A1)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Problem-space" (P508 example)

**L20-025** (capacity: iterative deepening) — The look-ahead operator in the evaluate-operator state is the task's own duplicate of the evaluated operator, which the task marks with (<eval-state> ^duplicate-look-ahead-operator <op>); the shared library does not create it (Thor-Soar does, by domain-specific rules).

*Rationale:* ID must know which proposed operator is the one being evaluated in order to force it.

*If violated:* the evaluated operator is not forced; the look-ahead may apply a different operator first

*Task supplies:* yes

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator.soar; agent-world/Impasse__Operator_Tie/evaluate-operator/elaborations.soar comment 'see thor-soar-agent for domain-specific duplicate-look-ahead-operator detection'

### Grounding

**L20-026** (capacity: grounding) — Grounding treats stoveknob and stoveburner specially: they are excluded from class-only grounding and grounded together through an existing world ^controlled-by relation.

*Source:* agent-world/find-object-direct.soar:*controlled-by

**L20-027** (capacity: grounding) — failed-grounding: when a grounding desired (^info.unanchored-object of class C) has no anchored object of class C in the external scene and is not in an in/on relation, failed-grounding (task-operator true, worst) is proposed; in look-ahead it sets the evaluation ^symbolic-value failed-grounding ^failed-grounding-info <info>, otherwise it marks find-object's argument1 ^failed-grounding true and adds ^failed-grounding-desired to the superstate desireds.

*Rationale:* Pushes the need to find the object to the top level, which can lead to exploration.

*Library rules:* object-world*propose*failed-grounding, apply*failed-grounding*

*See:* related L20-029 (overlap)

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/failed-grounding.soar

**L20-028** (capacity: grounding) — assume-successful-grounding: in look-ahead (thor-world, world anchored, not real, a copy), if an object cannot be grounded it is assumed found: a fake anchored object (handle '<handle>-fake', ^fake true, optimistic reachable/accessible/openable/open, room-temp; sliced variants use constants.transformations) replaces it and world ^info is created; ^action-time 2000. If the operator being evaluated is itself find-object, the evaluation fails instead.

*Rationale:* Lets planning continue with an assumed grounding.

*Library rules:* evaluate-operator*propose*assume-successful-grounding*, apply*assume-successful-grounding*

*Source:* agent-world/find-object/assume-successful-grounding.soar

**L20-029** (capacity: selection-world) — selection-world: an evaluation with symbolic-value failed-grounding and ^failed-grounding-info <info> adds a new ^desired (with ^info <info>) to the original task desireds and marks it ^preferred-desired.

*Rationale:* A failed grounding becomes a sub-goal (e.g. explore closed receptacles).

*See:* related L20-027 (overlap)

*Source:* selection-world/Operator_Tie/elaborations.soar:selection-world*elaborate*selection*super-desired*explore-closed-receptacles*failed-grounding; agent-world/.../failed-grounding.soar

**L20-030** (capacity: iterative deepening) — agent-world uses ^duplicate-look-ahead-operator to detect that find-object itself is being evaluated, and then returns ^failure: find-object is not evaluated by look-ahead.

*Rationale:* Grounding can't be simulated in look-ahead.

*If violated:* n/a

*Source:* agent-world/find-object/assume-successful-grounding.soar:object-world*apply*assume-successful-grounding*failue-if-would-assume-ground

**L20-031** (capacity: iterative deepening) — agent-world failed-grounding: in an anchored look-ahead where a desired refers to an unanchored object class not present in the scene, failed-grounding (worst, task-operator) gives the evaluation ^symbolic-value failed-grounding; selection-world then adds a ^preferred-desired to the superstate desireds. ID's depth-increment cleanup removes such evaluations.

*Rationale:* Pushes the need to find an object up to the top level.

*If violated:* n/a

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/failed-grounding.soar; selection-world/Operator_Tie/elaborations.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/increment-current-evaluation-depth.soar

### Time and future events

**L20-032** (capacity: time and future events) — A temporally extended action creates a ^future-event on the world only in the implementation of the operator that starts it (in Thor, turn-on). A composite operator learned by instruction needs to know only that the machine must be activated.

*Rationale:* Keeps timing knowledge out of learned operators.

*Task supplies:* yes

*Library rules:* elaborations/future-event.soar (outside A1)

*Source:* Thor-Soar Agent Documentation (thor.txt) "Complex Composite...", "Turn-on"

**L20-033** (capacity: time and future events, idle (wait)) — skip-wait: in a state no-change in the real world with a ^future-event pending, skip-wait is proposed (worst, indifferent, the soonest completion preferred, better than wait). It puts ^manipulate-time (^command advance-time ^ms <completion time minus now plus 200>) on the output-link.

*Rationale:* Fast-forwards the simulator instead of idling until a machine finishes.

*Example:*

```
(<output> ^manipulate-time <mt>) (<mt> ^command advance-time ^ms 15200)
```

*Library rules:* agent-world*propose*state-no-change*skip-wait, agent-world*apply*skip-wait

*Source:* agent-world/Impasse__State_No-Change/skip-wait.soar

**L20-034** (capacity: time and future events) — In look-ahead, while a future event exists, finish-future-event is proposed (worst, indifferent, the soonest completion first). It removes the event, sets the world's ^time to the completion time and applies the property change.

*Rationale:* Lets look-ahead simulate waiting for a temporally extended action.

*Library rules:* agent-world*propose*evaluate-operator*finish-future-event, apply*finish-future-event*future-event*

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/finish-future-event.soar

**L20-035** (capacity: selection-world) — The world copy copies a ^future-event that has ^argument1 and ^argument2 (both copied objects), ^completion-time, ^type and ^property-change-count, with its ^property-change items (objects mapped by handle), ^primary-property-change and ^new-desired. Future events of any other shape are not copied.

*Rationale:* Pending events must finish in look-ahead so desireds are marked achieved at the right time.

*If violated:* events missing in look-ahead

*Source:* selection-world/.../elaborations.soar:selection-world*elaborate*evaluate-operator*default-state-copy-relation*future-event, *property-change, *primary-property-change, *new-desired

**L20-036** (capacity: selection-world) — The copied world gets ^anchored-world from the old world (false if absent).

*Rationale:* Look-ahead time starts from a fixed reference.

*Source:* selection-world/.../elaborations.soar:selection-world*elaborate*evaluate-operator*time*anchored-world, *anchored-world*false, *initialize-room*false; agent-world/.../elaborations.soar:agent-world*elaborate*evaluate-operator*time*copy*lock-in, *time*copy

**L20-037** (capacity: iterative deepening) — While the look-ahead world has a ^future-event, initialize-failure-evaluation is not proposed: finish-future-event advances time instead.

*Rationale:* Waiting for a pending event is not a dead end.

*If violated:* n/a

*Source:* selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/initialize-failure-count.soar; agent-world/Impasse__Operator_Tie/evaluate-operator/finish-future-event.soar

### Other

**L20-038** (capacity: attention (attend/remove)) — Shortcomings acknowledged in the Thor-Soar documentation: task knowledge (achievement elaborations, attention rules) is spread over elaborations; navigation may leave the agent not facing an object; reachability after go-to may miss unattended objects.

*Rationale:* Known limitations.

*Task supplies:* yes

*Source:* Thor-Soar Agent Documentation (thor.txt) intro, "Go-to", "Attends"

**L20-039** (capacity: smem storage) — With ^flags.smem-store true, every top-state scene object and every scene ^in relation whose argument1 is a scene object is stored in smem once (marked ^smem-stored true), and every identifier child of a stored structure is stored recursively except via ^duplicate-of, ^info, ^future-event and ^derived-from-input.

*Rationale:* Builds a semantic memory of the environment for later retrieval.

*Library rules:* object-world*elaborate*smem-store-object, object-world*elaborate*smem-store-object*in-location*first-time, object-world*elaborate*store-scene*smem*recur

*Source:* agent-world/elaborations/smem-store-object.soar, smem-store-in.soar, smem-store-scene.soar:object-world*elaborate*store-scene*smem*recur

**L20-040** (capacity: goal completion, smem storage) — goal-completed's smem storage needs smem enabled and ^smem-storage-structure.initial-in-relations on the top state (initialize-agent-world creates it); with ^flags.explore false the scene's ^in relations are added to it.

*Source:* agent-world/goal-completed.soar:agent-world*apply*goal-completed*store-smem*; initialize-agent-world.soar

**L20-041** (capacity: iterative deepening) — Some look-ahead rules contain Thor names: finish-future-event requires ^problem-space.name thor-world, and the failure-evaluation counting rules test the relations on, in, above and under.

*Rationale:* Library not yet generalised.

*If violated:* non-Thor tasks with future events never advance time in look-ahead

*Source:* agent-world/Impasse__Operator_Tie/evaluate-operator/finish-future-event.soar; selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/count-desired-relation.soar
