# Soar program conventions — initial list (draft for review)

Generated 21 November 2026, 14:18 by `gen_spec.py` from `Soar-Conventions.xlsx` (302 rows). Do not edit by hand: change the workbook and rebuild. Rows are ordered by level, then by topic in development order, then by ID.

## Levels

| Level | Rows | Meaning |
|---|---|---|
| [L0 Definitional](#l0-definitional) | 113 | Describes what Soar is or does: definitions, syntax and architectural mechanisms. A program cannot violate it. |
| [L1 Architectural](#l1-architectural) | 24 | Tells the programmer what to do or avoid, where the architecture makes a violation fail. |
| [L2 Universal practice](#l2-universal-practice) | 14 | Adopted in essentially every Soar program. |
| [L3 Guidance](#l3-guidance) | 103 | Guidance from the Soar manual and tutorial that the library material supports. |
| [L3S Guidance (Soar only)](#l3s-guidance-soar-only) | 4 | L3 guidance for Soar programs in general that World-Conventions-v6 does not include, because a more specific world convention replaces it. The World-Conventions column gives the reason. |
| [L4 Default rules](#l4-default-rules) | 9 | Provided or assumed by Soar's general default rules (e.g. an operator no-change substate gets ^name of the operator; ^top-state). |
| [L5 Selection space (classic)](#l5-selection-space-classic) | 21 | Conventions of the default selection / look-ahead library (^desired, ^success, ^problem-space copy controls, evaluation values). |
| [L6P Project (constrained)](#l6p-project-constrained) | 14 | This project's stricter conventions for generated agents (plan of 5 Nov 2026; Water Jug DSL v0). |

## L0 Definitional

Describes what Soar is or does: definitions, syntax and architectural mechanisms. A program cannot violate it.

### Rule syntax/naming

**L0-001** (Definition, Must, convention, shared with World-Conventions, formerly SYN-002) — A production never contains a literal identifier (S1, O22). Every identifier is matched by a variable; conditions are linked by shared variables.

*Rationale:* Identifiers are created at runtime and cannot be known when the rule is written.

*If violated:* Rule can never match the intended object.

*Example:*

```
(<s> ^ontop <on>) (<on> ^top-block <b>)
```

*See:* parent L1-005

*Source:* Manual §2.2, p.15; §2.3.1.1, p.17; §3.3.5.2, p.53; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L0-002** (Definition, Must, fact, shared with World-Conventions, formerly SYN-003) — The first condition of every rule begins with the keyword state and matches a state. Every other condition and every action is linked to that state, directly or through other conditions.

*Rationale:* Matching is rooted in states; unlinked actions make the rule fail to load.

*If violated:* Warning and rule not stored in production memory.

*Example:*

```
sp {x (state <s> ^thing <t>) (<t> ^clear yes) --> ...}
```

*Source:* Manual §2.3.1, p.17-18; §3.3.5.1, p.52; Manual §3.3.1; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details; Tutorial Part 2, 2.2.2 Soar Version; Tutorial Part 2, 2.5.1 Syntax Errors

**L0-003** (Definition, Must, fact, shared with World-Conventions, formerly SYN-004) — A rule must have at least one positive condition that references a state; a rule whose conditions are all negated fails to load. The first condition as written must be that positive test of the state, for example (state <s> ...) (L0-002). After it, negated conditions may be written in any order: the reorderer places each one after the positive conditions that bind its variables.

*Rationale:* Matching starts from a positively matched state; negated conditions can only test the absence of structure relative to bound variables.

*If violated:* Rule fails to load ("no positive conditions that reference a goal state").

*Example:*

```
(state <s> ^superstate nil -^name)
```

*See:* parent L0-002

*Source:* Manual §3.3.5.6, p.57-58

**L0-004** (Definition, Must, fact, shared with World-Conventions, formerly SYN-005) — A production consists of sp {name ["doc"] [:type] conditions --> actions}; the name, conditions and actions are required, the documentation string and type optional.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
sp {task*propose*op (state <s> ...) --> (<s> ^operator <o> +)}
```

*Source:* Manual §3.3, p.49

**L0-005** (Definition, Must, convention, shared with World-Conventions, formerly SYN-006) — A production name must contain no whitespace and must not have the form of an identifier (one letter followed by digits). Symbolic constants must not have that form either.

*Rationale:* Whitespace ends the name; letter-digit names are confusable with identifiers.

*If violated:* Parse error, or constants printed as |G37| and confused with identifiers.

*See:* parent L0-004

*Source:* Manual §3.1.1, p.44; §3.3.1, p.50; Tutorial Part 1, 1.2.4 Loading and Running Hello-World

**L0-006** (Definition, Must, convention, shared with World-Conventions, formerly SYN-007) — Everything after a # on a line is a comment, up to the end of that line. When commenting out conditions or actions, keep the parentheses balanced in the text that remains.

*Rationale:* A # comment ends at the end of its line, so a multi-line comment needs a # on each line.

*If violated:* Parse error.

*Example:* # (<ontop> ^top-block <t>)

*See:* parent L0-004

*Source:* Manual §3.3.4, p.51

**L0-007** (Definition, Must, fact, shared with World-Conventions, formerly SYN-008) — Variables are written <name> with at least one non-pipe character; predicates <>, <=>, <, <=, >=, > precede a single value, and LTI predicates @, !@, @+, @- test long-term identifier links.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
(<c> ^color <> rust)
```

*See:* parent L0-004

*Source:* Manual §3.3.5.2-3.3.5.3, p.53-54

**L0-008** (Definition, Must, fact, shared with World-Conventions, formerly SYN-009) — Disjunctive tests << ... >> may contain only constants (no variables or predicates) and need spaces inside the brackets; disjunctions of whole conditions are not allowed, so write separate rules instead.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:*

```
(<t> ^color << red blue >>)
```

*See:* parent L0-004

*Source:* Manual §3.3.5.4, p.55

**L0-009** (Definition, Must, fact, shared with World-Conventions, formerly SYN-010) — A conjunctive test {...} must not equate two variables (e.g. { <a> <b> }); use one variable throughout instead.

*Rationale:* Illegal syntax.

*If violated:* Parse error.

*See:* parent L0-004

*Source:* Manual §3.3.5.5, p.56

**L0-010** (Definition, Must, fact, shared with World-Conventions, formerly SYN-011) — A negated condition -(...) matches when no WME satisfies it under the current bindings. A negated conjunction -{...} matches when no single set of bindings satisfies all of its conditions together.

*Rationale:* Defined semantics.

*If violated:* Misread negation scope, e.g. negating only the last condition instead of the group.

*Example:* -{(<s> ^ontop <on>) (<on> ^bottom-object.type table)}

*See:* parent L0-004

*Source:* Manual §3.3.5.6-3.3.5.7, p.56-58

**L0-011** (Definition, Must, fact, shared with World-Conventions, formerly SYN-012) — A negation in front of an attribute with multiple values negates their conjunction (it matches if any one is absent), not each value separately.

*Rationale:* Defined expansion to a negated conjunction.

*If violated:* Rule matches when only one of the values is absent.

*Example:*

```
(<p> -^child oprah uma)
```

*See:* parent L0-010

*Source:* Manual §3.3.5.8, p.59

**L0-012** (Definition, Must, fact, shared with World-Conventions, formerly SYN-013) — A WME is identified by its timetag; a rule instantiation fires only once per set of matched timetags, so removing and recreating an identical WME lets the rule fire again.

*Rationale:* Instantiations are determined by timetags, not triples.

*If violated:* Unexpected refiring after delete/re-create.

*Source:* Manual §3.1.3, p.45

**L0-013** (Definition, Must, convention, shared with World-Conventions, formerly SYN-014) — Attributes that will be used in attribute-path notation must not begin with a digit (^foo.3.bar parses .3 as a float).

*Rationale:* Parser ambiguity with floating-point numbers.

*If violated:* Mis-parsed condition.

*Exceptions:* Digit-initial attributes are allowed outside path notation.

*See:* parent L1-002

*Source:* Manual §3.3.5.11, p.65; §3.3.6.2, p.68

**L0-014** (Definition, Must, fact, shared with World-Conventions, formerly SYN-015) — Structured-value notation (^attr (^a v ...)) may be used in conditions only, never in actions.

*Rationale:* Defined syntax.

*If violated:* Parse error.

*Example:* ^ontop (^top-block <t> ^bottom-block <b>)

*See:* parent L0-004

*Source:* Manual §3.3.5.12, p.67; §3.3.6.5, p.70

**L0-015** (Definition, Must, fact, shared with World-Conventions, formerly SYN-016) — A variable that appears only in a rule's actions is bound to a new, unique identifier, shared by all of its occurrences in that firing; use this to create new objects.

*Rationale:* Unbound RHS variables generate fresh identifiers.

*If violated:* Unintended creation of new objects through typos in variable names.

*Example:* --> (<s> ^operator <o> +) (<o> ^name wait)

*See:* parent L0-004

*Source:* Manual §3.3.6.1, p.67-68

**L0-016** (Definition, Must, fact, shared with World-Conventions, formerly SYN-017) — Operator preferences on the RHS use the forms + ! ~ - > < = with an optional second value or number for binary forms; identifier and value are always variables, and predicates cannot be used on the RHS. = followed by a number creates a numeric-indifferent preference, (<s> ^operator <o> = 0.5); this is the form RL rules use, with a constant number (L0-100).

*Rationale:* Defined syntax; RHS creates, conditions restrict.

*If violated:* Parse error, or a predicate mistaken for a preference.

*Example:*

```
(<s> ^operator <o1> > <o2>)
(<s> ^operator <o> = 0.5)
```

*See:* parent L0-004

*Source:* Manual §3.3.6.4, p.69

**L0-017** (Definition, Must, fact, shared with World-Conventions, formerly SYN-018) — In RHS preference lists, > < = followed by a value are read as binary; use a comma (or ^, ) or another preference) after a unary > < = to keep it unary.

*Rationale:* Defined disambiguation rule.

*If violated:* A unary best/worst/indifferent silently read as binary.

*Example:*

```
(<s> ^operator <o1> <o2> >, <o3>)
```

*See:* parent L0-016

*Source:* Manual §3.3.6.5, p.70

**L0-018** (Definition, Must, fact, shared with World-Conventions, formerly SYN-019) — LTI names such as @6 may not appear in rule actions; use the LTI predicates (@, !@, @+, @-) in conditions to test LTI links.

*Rationale:* LTI labels are runtime artefacts.

*If violated:* Rule fails to load or is task-specific.

*Exceptions:* smem --add may use hard-coded LTI ids.

*Example:* { @ <orig> <retrieved> }

*See:* parent L0-007

*Source:* Manual §6.2.1.2, p.145; §3.3.5.3, p.54

**L0-019** (Definition, Must, fact, shared with World-Conventions, formerly SYN-020) — The order of conditions does not matter to Soar except that the first must test the state; Soar reorders conditions internally for matching efficiency.

*Rationale:* The Rete matcher reorders conditions.

*If violated:* Expecting printed rules to keep source condition order.

*See:* parent L0-002

*Source:* Manual §2.3.1, p.17

**L0-020** (Definition, Must, fact, shared with World-Conventions, formerly SYN-021) — Every variable used in an action must be bound in the conditions or be a new variable linked into working memory by another action in the same rule.

*Rationale:* Unlinked action variables create disconnected structure.

*If violated:* Syntax error (disconnected RHS action variable)

*See:* parent L0-015

*Source:* Tutorial Part 2, 2.5.1 Syntax Errors

**L0-021** (Definition, Must, fact, shared with World-Conventions, formerly SYN-051) — Actions may call right-hand-side functions, written (name args ...); a function's value can be the value of a created WME. They are: stopping and pausing (halt, interrupt, wait); text output (write, crlf, log); mathematics (+ - * /, div, mod, abs, atan2, sqrt, sin, cos, min, max, the set- functions, int, float, ifeq); generating and manipulating symbols (capitalize-symbol, compute-heading, compute-range, concat, dc, deep-copy, @, link-stm-to-ltm, make-constant-symbol, rand-float, rand-int, round-off, round-off-heading, size, strlen, timestamp, trim); and interface calls (exec for registered user functions, cmd for Soar commands).

*Rationale:* These are the only computations a rule can perform; everything else is matching and WME creation.

*If violated:* Unknown function names fail to load; computation attempted in conditions (L1-003).

*Example:*

```
(<s> ^sum (+ <a> <b>))
(write (crlf) |Done|)
(halt)
```

*See:* parent L0-004

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 3.3.7.6 Right-hand side Functions

### State representation

**L0-022** (Definition, Must, fact, shared with World-Conventions, formerly STA-001) — The top state has ^superstate nil and ^io with ^input-link and ^output-link; it is the only state with ^superstate nil.

*Rationale:* Architecture-created.

*Source:* Manual §3.1, §3.5

**L0-023** (Definition, Must, fact, shared with World-Conventions, formerly STA-002) — Working memory is a set: no two WMEs share the same identifier-attribute-value triple, but one identifier and attribute may have several values (a multi-valued attribute).

*Rationale:* The architecture prevents duplicate triples.

*If violated:* Expecting duplicate WMEs to count separately.

*Example:*

```
(<s> ^thing <b1> ^thing <b2>)
```

*Source:* Manual §2.2, p.14-15; §3.1.2, p.45

**L0-024** (Definition, Must, fact, shared with World-Conventions, formerly STA-003) — Every WME must be linked directly or indirectly to a state; when a WME is removed, all structure that thereby becomes unlinked is removed automatically and recursively.

*Rationale:* Working memory is a graph rooted in the states.

*If violated:* Structures vanish when their link to a state is removed.

*Source:* Manual §2.2, p.14-15; §3.1.5, p.46-47; Manual §3.3.6.3, p.69

### Operator WM representation

**L0-025** (Definition, Must, convention, shared with World-Conventions, formerly OPR-001) — An operator is an identifier that is the value of ^operator on a state. Only the decision procedure creates the selected-operator WME (<s> ^operator <o>); a rule action written (<s> ^operator <o>) with no preference creates an acceptable preference.

*Rationale:* Only the decision procedure selects operators.

*If violated:* Rule cannot create (<s> ^operator <o>) directly

*Source:* Manual §2.4, §3.2; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L0-026** (Definition, Must, fact, shared with World-Conventions, formerly OPR-002) — A state has at most one selected operator. It may have any number of proposed (acceptable) operators.

*Rationale:* The decision procedure selects a single value for each state's operator slot.

*If violated:* Rules confuse candidates with the selected operator.

*See:* parent L0-025

*Source:* Manual §2.1.4, p.8; §2.4.1, p.19; Manual §2.4

**L0-027** (Definition, Must, fact, shared with World-Conventions, formerly OPR-003) — Testing (<s> ^operator <o> +) matches a candidate operator, whereas (<s> ^operator <o>) matches only the selected operator; selection rules test the former and application rules the latter.

*Rationale:* Acceptable preferences and the selected-operator WME are distinct WMEs.

*If violated:* Comparison rules that fire only after selection, or application rules that fire on mere candidates.

*See:* parent L0-032

*Source:* Manual §3.3.5.9, p.59-60

### Rule: state elaboration

**L0-028** (Definition, Must, convention, shared with World-Conventions, formerly ELB-001) — A state elaboration tests state structure only (no selected operator, no acceptable preference) and adds structure to that state. Its WMEs are i-supported: they are removed when the rule no longer matches and no other instantiation (of the same or a different rule) supports them. A rule flagged :i-support is i-supported whatever its conditions test.

*Rationale:* Definition; elaborations compute entailments of the current state.

*If violated:* If it tests ^operator it is not an elaboration

*See:* parent L3-003

*Source:* Manual §2.3, §3.3; Manual §2.1.1, p.6; §2.1.9, p.12; §2.3.3, p.18; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 1, 1.4.4 Persistence of Working Memory Elements

### Rule: operator proposal

**L0-029** (Definition, Must, convention, shared with World-Conventions, formerly PRO-001) — An operator proposal tests a state (not its selected operator) and creates an acceptable preference (^operator <o> +) for a new operator object, and may add attributes to that object. The preference and the attributes are i-supported: they are removed when the proposal no longer matches. That an operator has a ^name is a practice (L2-006), not part of the definition.

*Rationale:* Definition of proposal.

*Example:*

```
(state <s> ^name blocks)
--> (<s> ^operator <o> +)
(<o> ^name move-block)
```

*See:* parent L3-003

*Source:* Manual §2.4, §3.3; Manual §2.1.5, p.9; §2.3.3, p.18; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

### Rule: operator elaboration

**L0-030** (Definition, Must, convention, shared with World-Conventions, formerly OEL-001) — An operator elaboration tests an operator (proposed or selected) and adds attributes to that operator object only. Its WMEs are i-supported, also when it tests the selected operator (L0-042).

*Rationale:* Definition; computes derived features of operators used by evaluation or application.

*Example:*

```
(state <s> ^operator <o> +)
(<o> ^name move ^to <t>)
(<t> ^clear yes)
--> (<o> ^target-clear yes)
```

*See:* parent L3-003

*Source:* Manual §3.3; Tutorial Part 2, 2.3.2 Operator Application: Persistence; Tutorial Part 2, 2.8.5 Jump and Move Operator Selection

### Rule: operator evaluation/selection

**L0-031** (Definition, Must, convention, shared with World-Conventions, formerly EVA-001) — An operator evaluation (selection) rule tests a state and the acceptable preferences of proposed operators, and creates only preferences (=, >, <, !, ~, -, numeric) for those operators. It creates no operator and no other structure. Its preferences are i-supported. Preferences are not created by rules that test the selected operator: such a rule's preferences are o-supported and persist.

*Rationale:* Definition of selection knowledge.

*Example:*

```
(state <s> ^operator <o1> + <o2> +)
(<o1> ^name pour)
--> (<s> ^operator <o1> > <o2>)
```

*See:* parent L3-003

*Source:* Manual §2.4, §3.3.6; Manual §2.1.6, p.9; §2.3.3, p.18; Tutorial Part 1, 1.4.11 Search Control; Tutorial Part 2, 2.6.3 Move Operator Selection

**L0-032** (Definition, Must, fact, shared with World-Conventions, formerly EVA-002) — Of all preferences, only acceptable operator preferences appear in working memory, so they are the only preferences that conditions can test (written (<s> ^operator <o> +)).

*Rationale:* Preference memory is separate and not matchable except for acceptable operator preferences.

*If violated:* Conditions testing other preference types are invalid or never match.

*Example:*

```
(state <s> ^operator <o1> + <o2> +)
```

*Source:* Manual §2.2, p.16; §3.1.4, p.46; §3.3.5.9, p.59

**L0-033** (Definition, Must, fact, shared with World-Conventions, formerly EVA-003) — An operator is selectable only if it has an acceptable (+) or require (!) preference.

*Rationale:* AcceptableCollect builds candidates from acceptable preferences; require short-circuits.

*If violated:* Preferences for an unproposed operator have no effect.

*See:* parent L0-038

*Source:* Manual §2.4, p.19; §2.4.1, p.20

**L0-034** (Definition, Must, fact, shared with World-Conventions, formerly EVA-004) — Preferences are not transitive: indifference or betterness between A-B and B-C implies nothing about A-C unless stated.

*Rationale:* Preference semantics evaluate only the preferences that exist.

*If violated:* Unexpected tie or conflict impasses.

*See:* parent L0-038

*Source:* Manual §2.4.1, p.20

**L0-035** (Definition, Must, fact, shared with World-Conventions, formerly EVA-005) — When every remaining candidate is indifferent to every other (unary =, numeric =, or pairwise binary =), the indifferent-selection policy chooses one. If any pair of candidates is not indifferent, a tie impasse results.

*Rationale:* IndifferentFilter is the last step of preference resolution.

*If violated:* Unintended tie impasses.

*Example:*

```
(<s> ^operator <o> =)
```

*See:* parent L0-038

*Source:* Manual §2.4.1, p.20; §2.4.2, p.24

**L0-036** (Definition, Must, fact, shared with World-Conventions, formerly EVA-006) — Numeric-indifferent preferences (= number) bias selection among indifferent candidates via the exploration policy; multiple numeric values for one operator are summed or averaged per numeric-indifferent-mode.

*Rationale:* Numeric values are combined before the exploration policy is applied.

*Example:*

```
(<s> ^operator <o> = 0.5)
```

*See:* parent L0-035

*Source:* Manual §2.4.1, p.20-21

**L0-037** (Definition, Must, fact, shared with World-Conventions, formerly EVA-007) — Two candidates that both have best (or both worst) preferences tie unless further preferences distinguish them.

*Rationale:* BestFilter leaves all best candidates in the set.

*If violated:* Tie impasse among best operators.

*See:* parent L0-038

*Source:* Manual §2.4.1, p.20; §2.7.1, p.28

**L0-038** (Definition, Must, fact, shared with World-Conventions, formerly EVA-008) — Preferences are resolved in this order: require, acceptable, prohibit, reject, better/worse, best, worst, indifferent.

*Rationale:* Fixed decision procedure; later filters see only survivors of earlier ones.

*Source:* Manual §2.4.2, p.21-24, Fig. 2.8

**L0-039** (Definition, Must, fact, shared with World-Conventions, formerly EVA-009) — Preference memory is not a set: several instantiations may create identical preferences, which coexist.

*Rationale:* Each preference is tied to its creating instantiation.

*Source:* Manual §3.2, p.48

**L0-040** (Definition, Must, fact, shared with World-Conventions, formerly EVA-010) — Only acceptable and reject preferences have meaning for non-operator attributes; all other preference types apply only to ^operator.

*Rationale:* Definition of preference semantics.

*If violated:* Preference ignored

*Source:* Consolidation review (gap); Manual §2.4

### Rule: operator application

**L0-041** (Definition, Must, convention, shared with World-Conventions, formerly APP-001) — An operator application rule tests a state and that state's selected operator (^operator <o>, without +), normally by ^name, and changes that state or structure linked to it, but not the operator object (L0-042). Its changes are o-supported: they persist after the rule or the operator is removed.

*Rationale:* Definition of operator application.

*If violated:* Not an application rule (changes get i-support)

*Example:*

```
(state <s> ^operator <o>)
(<o> ^name move)
--> (<s> ^done yes)
```

*See:* parent L3-003

*Source:* Manual §2.3, §3.3.x (o-support); Manual §2.1.8, p.11; §2.3.3, p.18-19; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version; Tutorial Part 1, 1.4.4 Persistence of Working Memory Elements; Tutorial Part 2, 2.3.2 Operator Application: Persistence

**L0-042** (Definition, Must, fact, shared with World-Conventions, formerly APP-002) — A rule's actions are o-supported if and only if its RHS proposes no operator, its LHS tests the selected operator of the most recent (deepest) state the rule matches, and no action adds to that operator object; otherwise they are i-supported. A rule that tests the selected operator and adds to the operator object is an operator elaboration (L0-030): all of its actions are i-supported, including any that change the state. A :o-support or :i-support flag on the rule overrides this test. Persistent changes to a state are therefore made only by operator application rules or by rules that carry the flag.

*Rationale:* Since 9.6 the single support mode is computed per instantiation from rule structure. In Soar 9.6, o-support comes only from testing the selected operator unless the rule carries :o-support; other rules' results retract.

*If violated:* Intended persistent changes silently get i-support, or vice versa; structure disappears unexpectedly.

*Example:*

```
(state <s> ^operator <o>) --> (<s> ^count 2)
```

*Source:* Manual §2.7.6, p.32-33

**L0-043** (Definition, Must, fact, shared with World-Conventions, formerly APP-003) — All actions of one rule instantiation receive the same support; a rule cannot give o-support to some actions and i-support to others.

*Rationale:* Support is assigned per instantiation, not per action.

*See:* parent L0-042

*Source:* Manual §2.7.6, p.33

**L0-044** (Definition, Must, fact, shared with World-Conventions, formerly APP-004) — O-supported WMEs remain until removed explicitly by a reject action in an operator application rule, or until they become unlinked or their state is removed.

*Rationale:* Persistence means the architecture never retracts them on its own.

*If violated:* Stale persistent structures accumulate unless explicitly removed.

*Example:*

```
(<s> ^ontop <old> -)
```

*See:* parent L0-042

*Source:* Manual §2.2, p.15; §2.3.3, p.19

**L0-045** (Definition, Must, fact, shared with World-Conventions, formerly APP-005) — When the preferences that selected the current operator change so that it would no longer be chosen (for example its proposal retracts), the selected-operator WME is removed at once and the application phase ends. The next operator is chosen at the next decision.

*Rationale:* Selection is continuously monitored against current preferences.

*If violated:* Application rules that expect to keep firing after the operator's proposal is falsified.

*See:* parent L0-046

*Source:* Manual §2.5, p.25

**L0-046** (Definition, Must, fact, shared with World-Conventions, formerly APP-006) — A decision cycle runs five phases in order: input, proposal, decision, application, output. Within a phase, rules fire in waves; all instantiations in one wave fire in parallel. The proposal phase fires only i-supported instantiations and retractions, wave after wave, until quiescence; o-supported matches wait for the application phase. The application phase alternates two kinds of wave and never mixes them: i-waves (i-supported instantiations plus all retractions) repeat until minor quiescence (none of these left), then one o-wave fires the o-supported instantiations (operator application rules); this repeats until neither kind is ready. With substates, each wave is at the highest goal with activity. Monitor rules (rules that test the selected operator and whose actions are only RHS functions such as write, with no WME actions) are classed with i-supported rules, so they fire in i-waves, in the first wave after the operator is selected and before any application rule, not in waves of their own.

*Rationale:* Fixed architectural cycle.

*Source:* Manual §2.5, p.24-25; Fig. 2.10, p.27

### Rule: monitoring/output

**L0-047** (Definition, Must, convention, shared with World-Conventions, formerly MON-001) — A monitoring rule tests the state, the selected operator, or both, and has only printing actions (write, crlf, log). It changes no working memory.

*Rationale:* Monitoring must not affect behaviour.

*If violated:* Hidden behavioural effects

*Example:*

```
sp {blocks-world*monitor*move-block ... --> (write ...)}
```

*See:* parent L3-003

*Source:* Tutorial Part 1; Manual §3.3.5.11, p.62

### Rule: impasse/substate handling

**L0-048** (Definition, Must, fact, shared with World-Conventions, formerly IMP-001) — A substate rule that tests the superstate's selected operator but writes only to the substate gets i-support, because the operator tested is not on the deepest matched state.

*Rationale:* O-support requires testing the operator of the lowest state matched.

*If violated:* Expecting persistent substate WMEs from rules that elaborate from the superoperator.

*Example:*

```
(state <s> ^superstate <ss>) (<ss> ^operator <o>)
--> (<s> ^name <n>)
```

*See:* parent L0-042

*Source:* Manual §2.7.6, p.33

**L0-049** (Definition, Must, fact, shared with World-Conventions, formerly IMP-002) — A tie impasse arises when acceptable candidates are not distinguished by preferences; it is resolved by preferences that pick one (better, best, require), eliminate others (worse, worst, reject, prohibit), or make all indifferent. It can also be resolved when the substate creates an acceptable preference for a new candidate together with other preferences that make the new candidate the choice (for example best, or better than each tied candidate).

*Rationale:* Defined by the preference scheme.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34

**L0-050** (Definition, Must, fact, shared with World-Conventions, formerly IMP-003) — A conflict impasse arises from contradictory better/worse preferences (A>B and B>A). Among the existing candidates it can be resolved only by require, reject or prohibit preferences. It can also be resolved when the substate creates an acceptable preference for a new candidate together with other preferences that make the new candidate the choice (for example better than each conflicting candidate).

*Rationale:* Additional better/worse preferences cannot undo a cycle.

*If violated:* Trying to resolve a conflict with more better/worse preferences among the existing candidates.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34

**L0-051** (Definition, Must, fact, shared with World-Conventions, formerly IMP-004) — A state no-change impasse arises when a state has no selectable operator: none is proposed, or every proposed operator is rejected or prohibited. It is resolved when a rule creates an acceptable or require preference for an operator that is not rejected or prohibited, or when a reject or prohibit preference on a proposed operator retracts.

*Rationale:* Defined by the decision procedure.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.35

**L0-052** (Definition, Must, fact, shared with World-Conventions, formerly IMP-005) — An operator no-change impasse arises when the selected operator stays selected across a decision: no rule changed the state so that its proposal retracts, and no other operator displaced it. It is resolved by applying the operator, by changing the state so that the proposal retracts, or by preferences that select another operator.

*Rationale:* Defined by the decision procedure; substate processing is how complex operators are implemented.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.35

**L0-053** (Definition, Must, fact, shared with World-Conventions, formerly IMP-006) — Rules can match at every level of the goal stack, but they fire one level at a time: within each phase, each wave fires at the oldest (highest) state with activity before any newer state, so higher-level changes may remove lower states before their rules fire.

*Rationale:* Ensures lower-level activity is consistent with higher levels.

*If violated:* Substate rules that assume they fire before superstate changes.

*Source:* Manual §2.7.2, p.29; §2.7.8, p.36

**L0-054** (Definition, Must, fact, shared with World-Conventions, formerly IMP-007) — If a superstate WME that was tested (directly or via local i-supported WMEs) in creating a local o-supported substate WME changes, the substate is regenerated (removed and recreated) by the goal dependency set.

*Rationale:* GDS keeps persistent substate structures consistent with their context.

*If violated:* Unexpected substate removal and restarts.

*Source:* Manual §2.7.7, p.35-36; §2.7.9.2, p.38-40

**L0-055** (Definition, Must, fact, shared with World-Conventions, formerly IMP-008) — Only local o-supported WMEs add to the goal dependency set; local i-supported WMEs and o-supported results do not.

*Rationale:* GDS tracks only dependencies of persistent local structures.

*See:* parent L0-054

*Source:* Manual §2.7.7, p.36; §2.7.9.2, p.39-40

**L0-056** (Definition, Must, fact, shared with World-Conventions, formerly IMP-022) — An impasse can be eliminated without being resolved: its substate is removed when a higher-level impasse is resolved, eliminated or regenerated, or when input changes working memory so that an operator can be selected. A regenerated substate (L0-054) is likewise removed and recreated. Elimination and regeneration produce no results, so nothing is learned from them; only results created before the substate was removed are learned from (L0-085).

*Rationale:* Substate processing becomes irrelevant when the situation above it changes.

*If violated:* Expecting results or learning from substate work that was abandoned.

*See:* parent L0-054

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 2.7.7 Removal of Substates: Impasse Resolution (Eliminating Impasses; Regenerating Impasses)

### Substate representation

**L0-057** (Definition, Must, fact, shared with World-Conventions, formerly SUB-001) — Only one impasse can exist at a given level; when a tie or conflict coexists with a constraint failure, only the constraint-failure impasse is created.

*Rationale:* Architectural precedence.

*Source:* Manual §2.7.1, p.28

**L0-058** (Definition, Must, fact, shared with World-Conventions, formerly SUB-002) — Each state has exactly one superstate (the top state has ^superstate nil) and at most one substate, forming a goal stack.

*Rationale:* Impasses create substates one level at a time.

*Example:*

```
(state <s> ^superstate nil)  # top state
```

*Source:* Manual §2.7.2, p.29

**L0-059** (Definition, Must, fact, shared with World-Conventions, formerly SUB-003) — When a substate is removed, all WMEs and preferences in it are removed. Results are not removed with it: they are WMEs of a superstate and persist according to their own support.

*Rationale:* They are no longer linked to the goal stack.

*If violated:* Relying on substate structures after the impasse resolves.

*Source:* Manual §2.7.7, p.36

**L0-060** (Definition, Must, fact, shared with World-Conventions, formerly SUB-004) — Only an impasse creates a substate. Each substate has ^type state, ^superstate, ^impasse (tie, conflict, constraint-failure, no-change), ^choices (multiple, constraint-failure, none), ^attribute (operator or state) and ^quiescence t. Tie, conflict and constraint-failure substates also have ^item and ^item-count; tie substates also have ^non-numeric and ^non-numeric-count. Every state has ^reward-link, ^smem and ^epmem. The kind of impasse is identified by ^impasse together with ^attribute (operator no-change: ^impasse no-change ^attribute operator; state no-change: ^impasse no-change ^attribute state).

*Rationale:* Created by the architecture to describe the impasse.

*If violated:* Rules testing non-existent impasse attributes.

*Example:*

```
(state <s> ^impasse tie ^attribute operator ^item <o>)
```

*Source:* Manual §3.4.1, p.84-85; Manual §2.7, §3.4

### Rule: results

**L0-061** (Definition, Must, fact, shared with World-Conventions, formerly RES-001) — A result's lasting support is set by its justification, not by how the substate rule created it: the result is o-supported if the justification tests the superstate and the superstate's selected operator (for example through the substate's ^name), and i-supported otherwise.

*Rationale:* The rule is an operator application in the substate whose actions are linked to the superstate.

*Exceptions:* Result support is finally decided by the justification's role in the superstate.

*Example:*

```
(state <s> ^superstate <ss> ^operator <o>)
--> (<ss> ^sub-operator-name <n>)
```

*See:* parent L0-062

*Source:* Manual §2.7.6, p.33

**L0-062** (Definition, Must, fact, shared with World-Conventions, formerly RES-002) — A result is a WME or preference created in a substate that is linked, directly or indirectly, to a superstate (rules reach the superstate through ^superstate); a WME counts as created in the most recent (lowest) state that its rule tested.

*Rationale:* Results survive substate removal because they remain linked to a superstate.

*If violated:* Intended results lost when substate is removed, or unintended results leaking upward.

*Example:*

```
(state <s> ^superstate <ss>) ... --> (<ss> ^answer <a>)
```

*Source:* Manual §2.7.3, p.29; Tutorial Part 3, 3.2 Impasses and State Creation; Tutorial Part 3, 5.2 Remove-sound Operator

**L0-063** (Definition, Must, fact, shared with World-Conventions, formerly RES-003) — A justification's conditions are the superstate WMEs tested, through the chain of substate firings, in producing the result; an i-supported result retracts when those conditions no longer match and no other support exists.

*Rationale:* Justifications are the instantiated summaries of substate reasoning.

*If violated:* i-supported results disappearing unexpectedly when tested superstate structure changes.

*See:* parent L0-061

*Source:* Manual §2.7.4, p.31-32

**L0-064** (Definition, Must, fact, shared with World-Conventions, formerly RES-004) — If substate reasoning tests no superstate knowledge, no chunk or justification is built, and the results lose all support and are removed when the substate is removed.

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

*See:* parent L0-063

*Source:* Manual §4.6.17, p.118

**L0-065** (Definition, Must, fact, shared with World-Conventions, formerly RES-005) — A justification is built for a result whenever no chunk is learned for it: when learning is off, and also when learning is on but a chunk is not learned (for example, the reasoning tested ^quiescence t). Justifications contain only literal values and no value constraints, and are removed as soon as their conditions stop matching; they exist to determine result support.

*Rationale:* They are a limited form of chunking used for support calculation.

*See:* parent L0-063

*Source:* Manual §4.6.1, p.108

### Semantic memory

**L0-066** (Definition, Must, fact, shared with World-Conventions, formerly SMM-001) — Every state receives architecture-created ^smem structures (<s> ^smem <m>) (<m> ^command <c> ^result <r>); semantic memory commands are written under ^smem.command of a state and results appear under that state's ^smem.result.

*Rationale:* Created by the architecture for each new state.

*If violated:* Commands placed elsewhere are ignored.

*Example:*

```
(state <s> ^smem.command <cmd>) --> (<cmd> ^query <q>)
```

*Source:* Manual §6.1, p.143

**L0-067** (Definition, Must, convention, shared with World-Conventions, formerly SMM-002) — Store a WM object in semantic memory with (<cmd> ^store <id>); only the object's direct attributes are stored, so deeper substructure needs further store commands, and success is reported as ^result.success <id>.

*Rationale:* Agent storage is not recursive.

*If violated:* Only the top level of a structure saved.

*Exceptions:* smem --add from the command line is recursive.

*Example:*

```
(<s> ^smem.command.store <id>)
```

*See:* parent L1-017

*Source:* Manual §6.3.1, p.145-146; Tutorial Part 7, 3. Agent Storage and Modification

**L0-068** (Definition, Must, fact, shared with World-Conventions, formerly SMM-003) — Storing an identifier already linked to an LTI overwrites that LTI's attributes with the current ones; use ^store-new to always create a new LTI.

*Rationale:* Defined store semantics.

*If violated:* Loss of previously stored augmentations.

*Example:*

```
(<cmd> ^store-new <id>)
```

*See:* parent L0-067

*Source:* Manual §6.3.1-6.3.2, p.146

**L0-069** (Definition, Must, fact, shared with World-Conventions, formerly SMM-004) — LTIs never appear in working memory; each retrieval creates a new short-term identifier linked to the LTI, and changes to it do not affect semantic memory until stored.

*Rationale:* Since 9.6, LTIs exist only in semantic memory.

*If violated:* Expecting WM edits to update long-term knowledge.

*Source:* Manual §6.2, p.144; §6.2.1.1, p.145

**L0-070** (Definition, Must, convention, shared with World-Conventions, formerly SMM-005) — Semantic memory supports only constant attributes; do not store objects whose attributes are identifiers.

*Rationale:* Representation restriction.

*If violated:* Unsupported storage.

*See:* parent L0-067

*Source:* Manual §6.2, p.144

**L0-071** (Definition, Must, convention, shared with World-Conventions, formerly SMM-006) — A state issues at most one semantic-memory retrieval (^retrieve or ^query, with optional modifiers) per decision cycle; retrievals are processed in the output phase. A malformed command, or more than one retrieval, gives ^result.bad-cmd. Any number of ^store commands may be issued together. The limit is per memory: an episodic-memory retrieval can be issued on the same state in the same decision cycle.

*Rationale:* Defined command processing.

*If violated:* bad-cmd error.

*Exceptions:* Several store commands may be issued at once.

*See:* parent L1-017

*Source:* Manual §6.4, p.147-148; Tutorial Part 7, 4. Non-Cue-Based Retrieval; Tutorial Part 7, 5. Cue-Based Retrieval

**L0-072** (Definition, Must, fact, shared with World-Conventions, formerly SMM-007) — A non-cue-based retrieval uses ^retrieve <lti-linked-id> and yields ^result.success and ^result.retrieved; a non-LTI value yields ^result.failure.

*Rationale:* Defined command format.

*If violated:* failure result.

*Example:*

```
(<cmd> ^retrieve <id>)
```

*See:* parent L0-071

*Source:* Manual §6.4.1, p.148

**L0-073** (Definition, Must, fact, shared with World-Conventions, formerly SMM-008) — A cue-based query uses ^query <cue>: constant values must match exactly, LTI-linked identifier values must match that LTI, and short-term identifier values match any value; results appear as ^result.success <cue> and ^result.retrieved <new-sti>, or ^result.failure <cue>. When several LTIs match, the one with the highest activation is retrieved; by default activation is recency (the most recently stored or retrieved).

*Rationale:* Defined query semantics.

*If violated:* Unexpected failures from over-specified cues.

*Example:*

```
(<cmd> ^query <q>) (<q> ^name <any> ^age 25)
```

*See:* parent L0-071

*Source:* Manual §6.4.2, p.148-149; Soar manual (online, soargroup.github.io, 6 Oct 2026): 6.4.2.1 Activation

**L0-074** (Definition, Must, convention, shared with World-Conventions, formerly SMM-009) — A processed smem or epmem command is ignored until its command structure changes. A new retrieval is issued by changing or replacing the command WMEs, which also clears the result.

*Rationale:* Commands are processed only on change.

*If violated:* Repeated queries silently not re-executed.

*See:* parent L1-017

*Source:* Manual §6.4, p.148; §7.3, p.157

**L0-075** (Definition, Should, convention, shared with World-Conventions, formerly SMM-010) — In a cue, a value that must match exactly is a constant or a long-term identifier; a value that only requires the attribute to be present is a new short-term identifier.

*Rationale:* Cue values are hard constraints, except short-term identifiers, which match any value.

*If violated:* Over- or under-constrained queries

*Example:*

```
(<cue> ^name <any-name> ^friend <lti>)
```

*See:* parent L0-073

*Source:* Tutorial Part 7, 5. Cue-Based Retrieval

### Episodic memory

**L0-076** (Definition, Must, fact, shared with World-Conventions, formerly EPM-001) — Every state receives architecture-created ^epmem structures with ^command, ^result and ^present-id; episodic commands go under the state's ^epmem.command and results appear under ^epmem.result.

*Rationale:* Created by the architecture for each new state.

*If violated:* Commands placed elsewhere are ignored.

*Example:*

```
(state <s> ^epmem.command <ec>)
```

*Source:* Manual §7.1, p.155

**L0-077** (Definition, Must, fact, shared with World-Conventions, formerly EPM-002) — By default an episode is recorded when a new attribute is added to the output-link; set the epmem trigger to dc to record every decision.

*Rationale:* Default trigger is output.

*If violated:* Agents without output record no episodes.

*Example:* epmem --set trigger dc

*Source:* Manual §7.2, p.156

**L0-078** (Definition, Must, fact, shared with World-Conventions, formerly EPM-003) — An episode captures the whole top state except structure under excluded attributes; ^epmem and ^smem are excluded by default. What is stored is controlled by excluding specific attributes (epmem --set exclusions <attribute>): keep information that should be recorded episodically on the top state, and exclude attributes not worth recording. WMEs with identifier attributes are not supported.

*Rationale:* Episodic storage captures only the top state, minus excluded attributes.

*If violated:* Needed information missing from episodes; bloated episodes; undefined behaviour for identifier attributes.

*Example:* epmem --set exclusions <attribute>

*Source:* Manual §7.2.1, p.156

**L0-079** (Definition, Must, convention, shared with World-Conventions, formerly EPM-004) — A cue-based episodic retrieval requires exactly one ^query cue and optionally one ^neg-query cue, with optional ^before, ^after and repeatable ^prohibit time modifiers; only one retrieval type per state per decision.

*Rationale:* Defined command format.

*If violated:* ^result.status bad-cmd.

*Example:*

```
(<ec> ^query <q>) (<q> ^io.input-link.foo <bar>)
```

*See:* parent L0-083

*Source:* Manual §7.3, p.157; §7.3.1, p.158-159

**L0-080** (Definition, Must, fact, shared with World-Conventions, formerly EPM-005) — Absolute retrieval uses ^retrieve <time>; relative retrieval uses ^next or ^previous with an arbitrary identifier value.

*Rationale:* Defined command format.

*If violated:* Error result.

*Example:*

```
(<ec> ^next <n>)
```

*See:* parent L0-083

*Source:* Manual §7.3.2-7.3.3, p.159-160

**L0-081** (Definition, Must, fact, shared with World-Conventions, formerly EPM-006) — Retrieved episodes are recreated under ^result.retrieved, with acceptable operator preferences renamed ^operator*; rules must test ^operator* to see past candidate operators.

*Rationale:* Avoids creating real acceptable preferences from memories.

*If violated:* Rules that never match retrieved operators.

*Example:*

```
(<r> ^operator* <o>)
```

*See:* parent L0-083

*Source:* Manual §7.3, p.157; §7.3.4, p.160

**L0-082** (Definition, Must, fact, shared with World-Conventions, formerly EPM-007) — In episodic cues, short-term identifiers match any structurally consistent identifier, while LTI-linked identifiers are treated as constants matching only the same LTI.

*Rationale:* Defined cue semantics.

*If violated:* Unexpected match failures.

*See:* parent L0-079

*Source:* Manual §7.3.1, p.159

**L0-083** (Definition, Must, convention, shared with World-Conventions, formerly EPM-008) — Episodic-memory commands (^query, ^retrieve, ^next, ^previous) are created under the state's ^epmem.command, at most one per state per decision; results are read under ^epmem.result.

*Rationale:* The architecture processes one command per state per decision, in the output phase by default.

*If violated:* Commands ignored or errors

*Example:*

```
(<cmd> ^query <n1>) (<n1> ^feature value ^id <n2>)
```

*See:* parent L0-076

*Source:* Tutorial Part 8, 3. Agent Interaction; Tutorial Part 8, 4. Cue-Based Retrieval; Tutorial Part 8, 5. Temporal Progression

**L0-084** (Definition, Must, fact, shared with World-Conventions, formerly EPM-012) — A cue-based retrieval returns the episode that best matches the cue: the most recent episode with the greatest match score (by default the number of cue leaf elements matched, the cardinality; with graph-match on, an episode whose identifiers bind consistently is preferred). The result carries metadata such as ^match-score, ^normalized-match-score, ^match-cardinality, ^memory-id and, with graph-match, ^graph-match.

*Rationale:* Retrieval is a partial match: the best match may not contain every cue element.

*If violated:* Rules that assume a retrieved episode matches the whole cue.

*See:* parent L0-079

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 7.3.1 Cue-Based Retrievals; 7.3.4 Retrieval Metadata

### Learning: chunking

**L0-085** (Definition, Must, fact, shared with World-Conventions, formerly CHK-001) — A chunk or justification is built at the moment a substate rule creates a result, whether or not the result resolves the impasse (L0-065). Its conditions are the superstate-linked WMEs tested on the path to the result; its actions are the results. A substate that is removed or regenerated before it creates a result produces no chunk or justification.

*Rationale:* Chunks and justifications summarise the substate processing that produced each result.

*If violated:* Expecting chunks or justifications from substates that were removed before creating a result.

*Source:* Manual §2.7.7, p.34-35

**L0-086** (Definition, Must, fact, shared with World-Conventions, formerly CHK-002) — The dont-learn and force-learn RHS actions are development tools that work only with chunk except or chunk only respectively (dont-learn in except mode, force-learn in only mode); they control chunking for a given state.

*Rationale:* Each action only has effect under the matching chunk setting.

*If violated:* Action silently has no effect.

*Example:*

```
(dont-learn <s>)
```

*See:* parent L0-113

*Source:* Manual §3.3.6.7, p.82

**L0-087** (Definition, Must, fact, shared with World-Conventions, formerly CHK-003) — Some elements of a chunk stay constants instead of becoming variables: (1) a constant that a substate rule tests in its conditions; (2) a value that one substate rule creates as a constant in its actions and a later substate rule tests; (3) a value that a substate rule creates from a variable in its actions when a later substate rule tests it against a specific constant.

*Rationale:* Explanation-based chunking variablizes an element only when the substate rules that tested or created it matched it with variables throughout; if any rule in that chain fixes it as a constant, it gets the NULL identity and the chunk keeps it as a constant.

*If violated:* Chunks are more specific than expected.

*See:* parent L0-085

*Source:* Manual §4.3.1, p.96-97; §4.5.2.2, p.104-105

**L0-088** (Definition, Must, fact, shared with World-Conventions, formerly CHK-004) — Conditions that test the same superstate WME are merged into one chunk condition when that WME matches a singleton pattern: an architectural singleton (such as ^superstate), a user singleton (chunk singleton <type> <attribute> <type>), or one Soar creates automatically for string attributes (chunk automatically-create-singletons, on by default). A pattern stops applying when it is removed (chunk singleton -r), when automatic singletons are turned off (automatically-create-singletons off), or when user singletons are turned off (user-singletons off). Conditions on a WME that matches no singleton pattern each become their own chunk condition.

*Rationale:* A singleton WME can have only one value in a state, so conditions that match it are given the same identity and merge; otherwise EBC keeps the reasoning of each original condition.

*If violated:* Chunks with seemingly duplicate conditions.

*See:* parent L0-085

*Source:* Manual §4.4.1, p.100; §4.5.2.1, p.103-104; §4.7.3.2, p.120

**L0-089** (Definition, Must, fact, shared with World-Conventions, formerly CHK-005) — The local ^superstate WME is an architectural singleton: all conditions testing (<s> ^superstate <ss>) share one identity during chunking.

*Rationale:* A state can have only one superstate.

*See:* parent L0-088

*Source:* Manual §4.4.1, p.100

**L0-090** (Definition, Must, fact, shared with World-Conventions, formerly CHK-006) — Architectural WMEs such as a tie impasse's ^item are explained by architectural instantiations: each ^item <o> is backtraced to the superstate's acceptable preference for that operator, (<ss> ^operator <o> +), so a chunk whose reasoning tests ^item has a condition on that acceptable preference.

*Rationale:* The architecture creates ^item <o> because the superstate has an acceptable preference for <o>; that preference is what the item depends on.

*See:* parent L0-085

*Source:* Manual §4.2, p.93

**L0-091** (Definition, Must, fact, shared with World-Conventions, formerly CHK-007) — Negated conditions are included in a chunk only when they test the absence of WMEs on superstate-linked identifiers; negations of local substate structures are dropped.

*Rationale:* Chunking cannot describe why a local WME was not produced.

*If violated:* Over-general chunk.

*See:* parent L0-085

*Source:* Manual §4.5.2.1, p.104; §4.6.10, p.112

**L0-092** (Definition, Must, fact, shared with World-Conventions, formerly CHK-008) — Constraints (e.g. <> <x>, >= 0) that a condition on local substate structure places on a value that came from the superstate are carried into the chunk as tests on that superstate value.

*Rationale:* Constraint tracking prevents over-generality.

*Example:*

```
Rule 1: (state <s> ^superstate <ss>) (<ss> ^count <c>) --> (<s> ^copy <c>)
Rule 2: (state <s> ^copy {<c> > 0} ^superstate <ss>) --> (<ss> ^positive true)
Chunk condition: (<ss> ^count {<c> > 0})
```

*See:* parent L0-085

*Source:* Manual §4.5.2.3, p.105; §4.5.3.2, p.106

**L0-093** (Definition, Must, fact, shared with World-Conventions, formerly CHK-009) — Intermediate RHS functions (math etc.) used in substate reasoning cause their argument identities and any tests of their outputs to be literalized in the chunk; only a RHS function in the result-creating rule is generalised.

*Rationale:* Constraints on intermediate RHS outputs cannot be expressed in a single rule's conditions.

*If violated:* Over-specialised chunks.

*Example:*

```
(<s> ^sum (+ <x> <y>))
```

*See:* parent L0-087

*Source:* Manual §4.6.16, p.116

**L0-094** (Definition, Must, fact, shared with World-Conventions, formerly CHK-010) — No chunk is learned when any of these holds: chunking is off for the state; the chunk duplicates an existing rule; a correctness filter rejects it; bottom-only is on and a lower chunk exists; the reasoning tested ^quiescence t; the reasoning tested the absence of local substate structure (a negated condition on a substate WME) and chunk allow-local-negations is off; no superstate WME was tested.

*Rationale:* Enumerated architectural conditions.

*If violated:* Expected chunk missing.

*See:* parent L0-085

*Source:* Manual §4.6.17, p.117-118

**L0-095** (Definition, Must, fact, shared with World-Conventions, formerly CHK-011) — A newly learned chunk is inhibited from firing on the exact WMEs that created it, but it may fire immediately on other matching WMEs.

*Rationale:* Prevents duplication of the original result.

*See:* parent L0-085

*Source:* Manual §4.6.2, p.108-109

**L0-096** (Definition, Must, fact, shared with World-Conventions, formerly CHK-012) — With multi-level substates a single result can yield bottom-up chunks at each level until a chunk creates WMEs only in the state it matches; bottom-only restricts learning to the lowest level.

*Rationale:* Chunks in higher spaces are learned from implicit matches of lower chunks.

*Example:* chunk bottom-only on

*See:* parent L0-085

*Source:* Manual §4.6.3, p.109; §4.6.17, p.117

**L0-097** (Definition, Must, fact, shared with World-Conventions, formerly CHK-023) — chunk add-osk is off by default. When it is on, the operator selection knowledge relevant to choosing the substate operators that led to a result (the preferences that selected them) is backtraced, and its conditions are added to the chunk.

*Rationale:* Without it, a chunk can leave out conditions that the substate's choice of operators depended on.

*If violated:* Over-general chunks when the substate's operator choices mattered.

*See:* parent L0-085

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.4.1 Operator Selection Knowledge Analysis; 4.6.8 Missing Operator Selection Knowledge

**L0-098** (Definition, Must, fact, shared with World-Conventions, formerly CHK-024) — A previous result is a WME created locally in a substate that later became a result. When substate rules then test or add to it through a path from the local substate, the chunk has unconnected conditions; chunking repairs it by adding grounding conditions along the shortest path it finds in working memory, which can make the chunk over-specialized. chunk stats reports repaired rules (L3-063).

*Rationale:* The explanation does not say where in the superstate the previous result lies.

*If violated:* Chunks that match only when the previous result is found on the same path.

*See:* parent L0-085

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.5.3.6 Rule Validation and Repair; 4.6.7 Previous Results and Rule Repair

**L0-099** (Definition, Must, fact, shared with World-Conventions, formerly CHK-025) — When several substate rule instantiations that test different superstate structures create the same substate WME, the WME exists once and a result that tests it is created once; but the chunk learned from that result matches once for each of those superstate structures and creates a separate result for each (disjunctive context conflation), so it does not reproduce the substate's behaviour.

*Rationale:* A chunk cannot express a disjunction of the superstate conditions that each produced the collapsed WME.

*If violated:* Chunks that create several results where the substate created one.

*See:* parent L0-085

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.6.12 Disjunctive Context Conflation

### Learning: RL

**L0-100** (Definition, Must, fact, shared with World-Conventions, formerly RL-001) — A rule is an RL rule if and only if its LHS tests a proposed operator (^operator <o> +), it is not a :template rule, and its RHS has exactly one action: a numeric-indifferent preference with a constant value for that operator, (<s> ^operator <o> = <number>). Any other action (another preference, an RHS function, a variable value) makes the rule a non-RL rule; put such actions in separate rules.

*Rationale:* RL rules are identified purely by syntax; the format permits exactly one constant numeric-indifferent action.

*If violated:* Intended RL rule silently not updated by RL.

*Example:*

```
sp {rl*3*12*left (state <s> ^x 3 ^operator <o> +) (<o> ^name move)
--> (<s> ^operator <o> = 1.5)}
```

*See:* parent L0-031

*Source:* Manual §5.1, p.131-132; Manual §5.1

**L0-101** (Definition, Must, fact, shared with World-Conventions, formerly RL-002) — Reward is given via the state's architecture-created ^reward-link as (<rl> ^reward <r>) (<r> ^value number); structures not matching this pattern are ignored, and multiple valid rewards are summed.

*Rationale:* Defined reward representation; the intermediate identifier allows equal-valued rewards and annotations.

*If violated:* Reward never seen by RL.

*Example:*

```
(<rl> ^reward <r>) (<r> ^value 1.0 ^source env)
```

*Source:* Manual §5.2, p.133-134

**L0-102** (Definition, Must, fact, shared with World-Conventions, formerly RL-003) — Every state (including substates) has its own reward-link; rewards for an operator are read only from the reward-link of the state where it was selected.

*Rationale:* RL treats each state independently.

*If violated:* Rewards placed on the wrong state's link.

*Exceptions:* Operator no-change impasses span decisions as described in §5.3.2.

*See:* parent L0-101

*Source:* Manual §5.2, p.133; §5.3.2, p.137

**L0-103** (Definition, Must, fact, shared with World-Conventions, formerly RL-004) — RL updates occur when an RL operator is selected, using the reward collected and the next RL operator's Q-value (Sarsa) or the maximum over proposed RL operators (Q-learning), per rl learning-policy.

*Rationale:* Defined temporal-difference update.

*Example:* rl --set learning-policy q-learning

*Source:* Manual §5.3, p.134-135

**L0-104** (Definition, Must, fact, shared with World-Conventions, formerly RL-005) — Decisions in which no RL operator is selected (e.g. maintenance operators such as cleaning output-link) form gaps that are bridged by temporal-extension; disabling it updates pre-gap rules with zero future value.

*Rationale:* Defined gap-propagation behaviour.

*If violated:* Value of operators before maintenance steps under-estimated if temporal-extension is off.

*Example:* rl --set temporal-extension off

*See:* parent L0-103

*Source:* Manual §5.3.1, p.136

**L0-105** (Definition, Must, fact, shared with World-Conventions, formerly RL-006) — An RL operator that leads to an operator no-change impasse remains selected while its substate works; its update discounts superstate rewards over that period only when hrl-discount is on (default off).

*Rationale:* Defined hierarchical RL behaviour.

*See:* parent L0-103

*Source:* Manual §5.3.2, p.137; Manual rl parameter table (hrl-discount default off)

**L0-106** (Definition, Must, fact, shared with World-Conventions, formerly RL-007) — A rule template is marked :template and otherwise follows the RL rule format, except that its numeric value may be a variable; it generates rules named rl*<template>*<n> for each novel combination of matched constants.

*Rationale:* Defined template mechanism.

*If violated:* Template not recognised.

*Example:*

```
sp {t :template (state <s> ^operator <o> + ^value <v>) --> (<s> ^operator <o> = <v>)}
```

*See:* parent L0-100

*Source:* Manual §5.4.2, p.140-141

**L0-107** (Definition, Must, fact, shared with World-Conventions, formerly RL-022) — The default indifferent-selection policy is softmax. epsilon-greedy and boltzmann are the policies designed for RL; one of them is set when RL is enabled (L3-088).

*Rationale:* The default is kept for backward compatibility, not for RL.

*If violated:* RL exploration that does not follow the intended policy.

*See:* parent L0-036

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 5.3.3.1 Exploration

**L0-108** (Definition, Must, fact, shared with World-Conventions, formerly RL-023) — Eligibility traces are off by default (rl eligibility-trace-decay-rate 0). With a positive decay rate, Sarsa becomes Sarsa(lambda) and Q-learning becomes Watkins Q(lambda); eligibility-trace-tolerance is the smallest trace value not treated as 0.

*Rationale:* Traces update RL rules across several sequential steps, speeding credit assignment.

*If violated:* Expecting multi-step credit assignment without enabling traces.

*See:* parent L0-103

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 5.3.3 Eligibility Traces

### Input/output link

**L0-109** (Definition, Must, fact, shared with World-Conventions, formerly IO-001) — Input functions add and remove WMEs at the start of each decision cycle, and output functions process the output-link commands at the end of each cycle. The environment may apply the action then or together with the next input (as in a gym step).

*Rationale:* I/O is synchronised with the decision cycle.

*If violated:* Expecting environment feedback within the same cycle the command was issued.

*See:* parent L0-046

*Source:* Manual §2.6, p.26; §2.5, p.25

**L0-110** (Definition, Must, fact, shared with World-Conventions, formerly IO-002) — Input and output through the I/O system is represented as substructure of the top state's ^io attribute: ^io.input-link for perception and ^io.output-link for motor commands, both created by the architecture. Input can also come through SVS (the spatial visual system), whose scene graph the environment updates and the agent reaches through the state's ^svs structure.

*Rationale:* Apart from SVS, I/O occurs only through the top state's io attribute.

*If violated:* Commands placed elsewhere are never seen by output functions.

*Exceptions:* Systems may add extra, descriptively named input or output links under ^io.

*Example:*

```
(state <s> ^io.output-link <out>)
```

*See:* parent L0-022

*Source:* Manual §3.5.1-3.5.2, p.87-89

**L0-111** (Definition, Must, fact, shared with World-Conventions, formerly IO-003) — A WME on the input-link stays until the input function removes it and supports matching rules meanwhile; a rule does not refire on unchanged input, only when the input is removed and re-added.

*Rationale:* Instantiations are tied to WME timetags.

*If violated:* Expecting repeated firing on persistent input.

*See:* parent L0-110

*Source:* Manual §3.5.2, p.89-90

**L0-112** (Definition, Must, fact, shared with World-Conventions, formerly IO-004) — Rules that interpret input test attributes and values under ^io.input-link; rules that produce output create structure under ^io.output-link.

*Rationale:* I/O rule roles as defined.

*Example:*

```
sp {blocks-world*elaborate*input (state <s> ^io.input-link <in>) ...}
```

*See:* parent L0-110

*Source:* Manual §3.5.3, p.90

### Settings/commands

**L0-113** (Definition, Must, fact, shared with World-Conventions, formerly SET-001) — Chunking is off by default. It is enabled with chunk always, or selectively with chunk only (plus force-learn) or chunk except (plus dont-learn).

*Rationale:* Default chunk setting is never.

*If violated:* Expecting chunks with learning disabled.

*Example:* chunk always

*Source:* Manual §4.1, p.91; §4.7.2, p.119

## L1 Architectural

Tells the programmer what to do or avoid, where the architecture makes a violation fail.

### Rule syntax/naming

**L1-001** (Definition, Must, convention, shared with World-Conventions, formerly SYN-022) — Different variables may bind to the same symbol; when two conditions must bind distinct objects or values (e.g. two jugs, two values of a multi-valued attribute), add an explicit test that excludes equality: not-equal (<j2> <> <j1>), or > or < ({<j2> > <j1>}). > and < work on numbers, strings and identifiers and give a canonical ordering, so the rule matches each pair only once instead of in both orders.

*Rationale:* Variable bindings are not unique unless forced.

*If violated:* Rule matches the same object twice.

*Example:*

```
(<p> ^child <c1> {<> <c1> <c2>})
```

*See:* parent L0-001

*Source:* Manual §3.3.5.2, p.53; §3.3.5.8, p.59; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L1-002** (Definition, Must, convention, shared with World-Conventions, formerly SYN-023) — In rule conditions, attribute-path notation (^a.b.c) introduces a new variable for each step. Two paths through a multi-valued attribute therefore need not bind the same intermediate object; where the same object is meant, bind it with an explicit variable.

*Rationale:* In conditions, each dotted path expands into its own conditions with new variables.

*If violated:* Conditions match different ontop relations than intended.

*Example:* ^ontop.top-block <b1> ^ontop.bottom-block <b2> # two different ontops

*Source:* Manual §3.3.5.11, p.62-64

**L1-003** (Definition, Must, convention, shared with World-Conventions, formerly SYN-024) — Conditions contain no arithmetic. A derived value is computed in the action of an elaboration, and conditions test the elaborated attribute.

*Rationale:* Soar allows math functions only in actions.

*If violated:* Rule cannot be written / syntax error

*Example:*

```
(<j> ^empty (- <v> <c>))
```

*See:* parent L3-031

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 1, 1.4.5 Water Jug State Elaboration

**L1-004** (Definition, Must, convention, shared with World-Conventions, formerly SYN-050) — An attribute or constant written unquoted as a letter followed by digits (d1, c11) is read as the upper-case symbol (D1, C11). Where it must match smem, epmem or input content stored in lower case, write it between vertical bars: ^|d1|, |c11|. Check every such attribute in conditions, in actions and in the text of smem --add commands.

*Rationale:* Soar upper-cases an unquoted symbol that is a letter followed by digits, so ^d1 never equals the string |d1| stored in smem. Nothing is reported.

*If violated:* Silent mismatch: the smem or epmem query returns nothing or fails and the rule never fires (^d1 against facts stored as |d1|).

*Exceptions:* Names that are meant to be identifiers (D1 in the Hanoi disc handles).

*Example:*

```
(<s> ^|d1| <d1>)   # matches the attribute stored as |d1|
(<s> ^d1 <d1>)    # reads ^D1
```

*See:* parent L0-008

*Source:* Found 17 Nov 2026 in arithmetic-smem world-v6 (Tasks/Families README-v6.md)

### State representation

**L1-005** (Definition, Must, convention, shared with World-Conventions, formerly STA-004) — An object is defined by its attributes and values, not by its identifier; programs must not depend on particular identifier names, which differ between runs.

*Rationale:* Identifiers are runtime-generated labels.

*If violated:* Behaviour that depends on identifier spelling is not reproducible.

*Source:* Manual §2.2, p.15; §3.1.1, p.44

**L1-006** (Definition, Must, convention, shared with World-Conventions, formerly STA-005) — Rules must not create, remove or change the state attributes the architecture creates (^type, ^superstate, ^impasse, ^attribute, ^choices, ^item, ^item-count, ^quiescence, ^io, ^reward-link, ^smem, ^epmem) or the selected-operator WME.

*Rationale:* These WMEs are owned by the decision procedure.

*If violated:* Rule is rejected or architecture state is corrupted.

*Exceptions:* The operator slot is influenced only indirectly, through preferences.

*Source:* Manual §2.2, p.16; §3.4, p.84

### Operator WM representation

**L1-007** (Definition, Must, convention, shared with World-Conventions, formerly OPR-004) — An operator proposal must not test the acceptable preference of the operator it proposes.

*Rationale:* A proposal that tests its own preference never fires.

*If violated:* Operator never proposed

*See:* parent L0-029

*Source:* Manual §2.4

### Rule: state elaboration

**L1-008** (Definition, Must, convention, shared with World-Conventions, formerly ELB-002) — Elaboration, proposal and comparison rules must reach quiescence before the decision phase: no cycle of rules that keeps adding and retracting (e.g. a rule that tests the absence of what it creates).

*Rationale:* Elaboration runs to quiescence before each decision.

*If violated:* max-elaborations reached; oscillation

*Source:* Manual §2.5; Manual §2.5, p.24-25

**L1-009** (Definition, Must, convention, shared with World-Conventions, formerly ELB-003) — Within one elaboration cycle all matched rules fire and all unmatched instantiations retract in parallel. A rule's correctness must not depend on the order of firing.

*Rationale:* Soar has no conflict resolution among matched rules; order is functionally parallel.

*If violated:* Order-dependent behaviour that differs between runs or versions.

*Source:* Manual §2.3.3, p.19; §2.5, p.25

**L1-010** (Definition, Must, convention, shared with World-Conventions, formerly ELB-004) — An i-supported rule must not test the absence of the WME it creates: the rule would fire and retract without end.

*Rationale:* The action falsifies the rule's own condition, which retracts the action, which re-enables the rule.

*If violated:* Infinite fire/retract loop; no quiescence.

*Exceptions:* Operator application rules (o-support) may legitimately test for absence of what they create.

*Example:*

```
(state <s> ^car <c> -^road)
--> (<s> ^road route-66)  # loops
```

*See:* parent L1-008

*Source:* Manual §3.3.5.6, p.57; Manual §2.5

### Rule: operator elaboration

**L1-011** (Definition, Should, convention, shared with World-Conventions, formerly OEL-002) — Operator attributes are i-supported. A rule that tests the selected operator does not add both operator attributes and state attributes: every action of such a rule is i-supported (L0-042), so the state change would not persist. Exception: a rule flagged :o-support may add a persistent bookkeeping link to an operator (for example ^evaluation on evaluate-operator, L14-020).

*Rationale:* Operator augmentations define the operator and must track it; mixing them with state changes defeats o-support, and o-supported operator elaborations would add GDS dependencies.

*If violated:* State change unexpectedly i-supported; runtime warning.

*Example:*

```
(<o> ^new aug) (<s> ^new aug)  # bad: same rule
```

*See:* parent L0-030

*Source:* Manual §2.7.6, p.33-34; §2.7.9.2, p.40

### Rule: operator application

**L1-012** (Definition, Must, convention, shared with World-Conventions, formerly APP-007) — A reject action (^attr value -) that is meant to remove a WME permanently must be in an o-supported rule; with i-support the WME returns when the rejecting instantiation retracts.

*Rationale:* Removal under i-support is not persistent.

*If violated:* Removed WME reappears.

*Example:*

```
(state <s> ^operator <o>) ... --> (<s> ^block <b> -)
```

*See:* parent L0-042

*Source:* Manual §3.3.6.3, p.68-69; Tutorial Part 2, 2.3.2 Operator Application: Persistence

**L1-013** (Definition, Must, convention, shared with World-Conventions, formerly APP-027) — Operator preferences are created only by rules whose actions are i-supported (proposal and evaluation rules), never by operator application rules. Preferences are never removed by rules: they retract when the rule that created them no longer matches.

*Rationale:* A rule that creates an operator preference while testing the selected operator gets i-support for all its actions (L0-042), so a state change in the same rule does not persist; preferences are meant to track the current situation.

*If violated:* State changes made in the same rule disappear; preferences that do not track the situation.

*See:* parent L0-042

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 3.3.7.4 The syntax of preferences

### Rule: impasse/substate handling

**L1-014** (Definition, Must, convention, shared with World-Conventions, formerly IMP-009) — The ^item set of a tie or conflict substate can change during the impasse without ending it. Substate rules must not assume that the set of candidates is fixed.

*Rationale:* The architecture adds and removes ^item WMEs in place.

*If violated:* Stale evaluations of candidates that have left the tie.

*See:* parent L5-019

*Source:* Manual §3.4.1, p.85

**L1-015** (Definition, Must, convention, shared with World-Conventions, formerly IMP-010) — At most one operator has a require (!) preference at a time, and no operator has both require and prohibit. Otherwise a constraint-failure impasse results, which no further preference resolves; one of the conflicting preferences must retract.

*Rationale:* Require and prohibit are hard constraints.

*If violated:* Unresolvable impasse.

*Source:* Manual §2.7.1, p.28; §2.7.7, p.34; Manual §2.4.1, p.21; §2.7.1, p.28

### Semantic memory

**L1-016** (Definition, Must, convention, shared with World-Conventions, formerly SMM-012) — Rules must not remove attributes of the ^smem.result (or ^epmem.result) structure; the memory system maintains them.

*Rationale:* The memory module adds and clears result WMEs itself.

*If violated:* Inconsistent result structure.

*See:* parent L0-066

*Source:* Manual §6.1, p.143; §7.1, p.155

**L1-017** (Definition, Should, convention, shared with World-Conventions, formerly SMM-019) — Semantic-memory commands are created under the state's ^smem.command by operator application rules, and exactly one smem command is on the command link at a time. The agent removes the previous command before it issues the next (for example ^retrieve replaced by ^query).

*Rationale:* smem reads the command link and does not clear it; an operator application rule (o-support) keeps the command in place until the agent removes it, so the agent is responsible for maintaining the command link.

*If violated:* smem finds more than one command and returns an error status instead of running the new command.

*Example:*

```
(<cmd> ^retrieve <lti> - ^query <cue>)
```

*See:* parent L0-074

*Source:* Tutorial Part 7, 3. Agent Storage and Modification; Tutorial Part 7, 5. Cue-Based Retrieval

### Learning: RL

**L1-018** (Definition, Should, convention, shared with World-Conventions, formerly RL-008) — A reward WME exists for exactly the decision cycles it applies to: make reward rules i-supported, or remove the reward after it is collected. Soar never clears the reward-link, and a reward that persists is counted again in every cycle.

*Rationale:* Reward collection scans the link every decision phase without bookkeeping.

*If violated:* Reward counted multiple times.

*Exceptions:* Rewards intended to be received every cycle.

*Example:*

```
sp {elaborate*reward (state <s> ^name left-right ^reward-link <r> ...) --> (<r> ^reward.value <d-reward>)}
```

*See:* parent L0-101

*Source:* Manual §5.2, p.134; Tutorial Part 6, 2.2 Reward Rules

### Input/output link

**L1-019** (Definition, Must, convention, shared with World-Conventions, formerly IO-005) — Rules must reach the io, input-link and output-link objects through variables bound by ^io.input-link and ^io.output-link; their identifiers are assigned at run time.

*Rationale:* Identifiers differ across runs.

*Example:*

```
(state <s> ^io.input-link <in>)
```

*See:* parent L1-005

*Source:* Manual §3.5.2, p.87; Tutorial Part 2, 2.3.3 Running and Tracing

**L1-020** (Definition, Must, convention, shared with World-Conventions, formerly IO-006) — Rules never create, remove or change structure under ^io.input-link; the environment owns it.

*Rationale:* Input changes are made by the I/O system each input phase.

*If violated:* Input overwritten or inconsistent

*See:* parent L0-110

*Source:* Manual §3.5

**L1-021** (Definition, Should, convention, shared with World-Conventions, formerly IO-007) — A rule that copies an input-link object onto the state uses a new variable for the copy on the RHS, so that a new identifier is created. Reusing the input-link variable links the state to the input structure and copies nothing: when the environment changes or removes that structure on the input-link, what the state reaches through the link changes or is removed with it.

*Rationale:* Unbound RHS variables create new objects; bound ones create links.

*If violated:* State structure aliases input that the environment may remove.

*Exceptions:* Linking may be intended when no copy is needed.

*Example:*

```
(<in> ^block <ib>) --> (<s> ^block <b>) (<b> ^x <x>)
```

*See:* parent L0-112

*Source:* Manual §3.5.3, p.90

**L1-022** (Definition, Must, convention, shared with World-Conventions, formerly IO-008) — Every external action is issued as a command structure under ^io.output-link. The attribute used for the command is set by the environment interface: the tutorial environments use the command name itself (^move.direction north), many systems use ^command, and Thor-Soar (agent-world) uses ^perform-action with ^name <action-handle> and ^argument1, ^argument2, on which the environment reports ^status success, error or failure.

*Rationale:* The output-link is the only channel for motor commands.

*If violated:* Environment never sees the action

*Example:*

```
(state <s> ^io.output-link <out>) --> (<out> ^move.direction north)
(<out> ^perform-action <p>) (<p> ^name <action-handle> ^argument1 <handle>)   # Thor-Soar
```

*See:* parent L0-110

*Source:* Tutorial Part 2, 2.2.1 English Version; Tutorial Part 2, 2.2.2 Soar Version

### Settings/commands

**L1-023** (Definition, Must, convention, shared with World-Conventions, formerly SET-003) — Semantic memory is enabled (smem --enable) before an agent uses it.

*Rationale:* Memory mechanisms are disabled by default.

*If violated:* Commands silently not processed

*Example:* smem --enable

*Source:* Tutorial Part 7, 2. Agent Interaction

**L1-024** (Definition, Must, convention, shared with World-Conventions, formerly SET-004) — Episodic memory is enabled (epmem --set learning on) and its storage trigger chosen (output, the default, or dc for every decision) before an agent depends on it.

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

**L2-001** (Requirement, Should, convention, shared with World-Conventions, formerly ORG-001) — Files follow the operator hierarchy (the VisualSoar layout): one file per operator, named after it, holding its proposal and application rules; general rules under elaborations/; operators usable in any substate under all/; a substate that implements an operator is a folder with the operator's name that holds its suboperators.

*Rationale:* VisualSoar organization; the layout mirrors the problem-space hierarchy.

*Source:* VisualSoar templates; Tutorial Part 3, 3. Wander Operator - Subgoals; Tutorial Part 3, 3.4 General Rule Summary; Tutorial Part 3, 4.9 Wait Operator; Tutorial Part 3, 5. Improving Sound Detection

**L2-002** (Requirement, Should, convention, shared with World-Conventions, formerly ORG-002) — A project uses one copy of the shared library, loaded from its shared folder (Soar/soar-library); it does not keep edited local copies.

*Rationale:* The corpus has at least five versions (default-1-24-17, default-2019, default-2019-x, default with Impasse__ folders, plus astar/iterative-deepening/epmem/RL variants), and local copies with changed rules.

*If violated:* Silent behavioural differences between agents

*Exceptions:* Deliberate alternative search libraries (selection-astar, selection-iterative-deepening, selection-RL, selection-epmem)

*See:* parent L5-001

*Source:* Corpus survey (6 Nov 2026)

### Rule syntax/naming

**L2-003** (Requirement, Should, convention, shared with World-Conventions, formerly SYN-025) — A rule name has asterisk-separated fields: <task-or-state>*<function>*<operator-or-feature>[*detail]. The function is one of propose, apply, elaborate, compare (or select), monitor, detect, evaluate. Library rules follow L6-006.

*Rationale:* Readable traces; VisualSoar and tools rely on it; a checker can compare the declared type with the classified type.

*Exceptions:* Very early examples (hello-world) and generic rules omit the task field.

*Example:* water-jug*apply*pour*case1

*Source:* Tutorial Part 1; Manual §3.3.1, p.50; Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator; Tutorial Part 1, 1.4.9 State and Operator Monitoring; Tutorial Part 1, 1.4.10 Desired State Recognition; Tutorial Part 1, 1.4.11 Search Control

**L2-004** (Requirement, Should, convention, shared with World-Conventions, formerly SYN-026) — The state variable is <s> and the operator variable is <o> (or <op>); other variable names say what they bind.

*Rationale:* Uniform variable names make rules quicker to read.

*If violated:* Reduced readability only

*Exceptions:* Substate rules often use <ss> for the superstate.

*Example:*

```
(state <s> ^operator <o>)
```

*Source:* Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version; Tutorial Part 1, 1.2.6 Hello-World Rule: Soar Details

### State representation

**L2-005** (Requirement, Should, convention, shared with World-Conventions, formerly STA-006) — Every state that rules reason about has ^name. The top state gets the task name from its initialization operator; a substate gets the name of the superstate's selected operator from the default elaboration (L4-008) or from a rule specific to that substate.

*Rationale:* Every rule then tests (state <s> ^name X), which scopes it to one problem space.

*If violated:* Rules fire in unintended states

*Exceptions:* Environments that start from input-link data may skip initialization, but the tutorial's TankSoar default agent still names the top state.

*Example:*

```
(<s> ^name water-jug)
```

*Source:* Tutorial Part 1, Part 3; Tutorial Part 1, 1.4.2 State Representation; Tutorial Part 3, 2. Simple Wandering Tank

### Operator WM representation

**L2-006** (Requirement, Should, convention, shared with World-Conventions, formerly OPR-005) — Every operator has exactly one ^name, set by its proposal rule; every proposal, evaluation and application rule for the operator tests that name.

*Rationale:* Universal; default rules (substate naming, selection space) depend on it.

*If violated:* Default rules do not work

*Example:*

```
(<o> ^name pour)
```

*Source:* Tutorial Part 1; default elaborate*state*name; Tutorial Part 1, 1.3 Building a Simple Hello-World Agent Using an Operator; Tutorial Part 1, 1.3.2 Hello-World Operator: Soar Version

**L2-007** (Requirement, Should, convention, shared with World-Conventions, formerly OPR-006) — Operator parameters are attributes of the operator object, created by the proposal rule; their values are the objects or constants the operator acts on. Parameters are not encoded in the operator's name.

*Rationale:* Applications and evaluations bind the objects through the operator.

*Example:*

```
(<o> ^name pour ^from <j1> ^to <j2>)
```

*See:* parent L2-006

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

### Rule: operator proposal

**L2-008** (Requirement, Must, convention, shared with World-Conventions, formerly PRO-002) — Every proposed operator needs an acceptable preference, including when the same rule also creates other preferences for it (indifferent, best).

*Rationale:* Operators without an acceptable preference are never selected.

*If violated:* Operator never selected

*Example:*

```
(<s> ^operator <o> + =)
```

*See:* parent L0-029

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 2, 2.4.1 English Version

**L2-009** (Requirement, Must, convention, shared with World-Conventions, formerly PRO-003) — Every operator that can be proposed has an implementation: application rules that test its ^name in the state where it is proposed, or rules that apply it in its operator no-change substate.

*Rationale:* Otherwise selecting it produces an unintended operator no-change impasse.

*If violated:* Operator no-change impasse; agent stalls

*Exceptions:* Operators deliberately implemented in a substate

*Source:* Consolidation review (gap)

### Rule: operator application

**L2-010** (Requirement, Should, convention, shared with World-Conventions, formerly APP-008) — An application rule that changes the value of a single-valued attribute adds the new value and removes the old one in the same rule (^attr <new> ^attr <old> -). A WME cannot be changed in place.

*Rationale:* Otherwise the attribute becomes multi-valued.

*If violated:* Attribute has two values

*Exceptions:* See L3-022: a separate removal rule when the current value is known to be incorrect but the correct value is not yet available.

*Example:*

```
(<j> ^contents <new> ^contents <old> -)
```

*See:* parent L0-042

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 4, 5. Operator Application

**L2-011** (Requirement, Should, convention, shared with World-Conventions, formerly APP-009) — An operator that acts on an external environment changes the state indirectly: it issues a motor command and the state changes through perception. If the agent keeps an internal model of the world, the operator also updates the model.

*Rationale:* External changes arrive only via input; an internal model diverges unless updated by the operator.

*If violated:* Internal model inconsistent with the world.

*See:* parent L1-022

*Source:* Manual §2.1.8, p.11

**L2-012** (Requirement, Should, convention, shared with World-Conventions, formerly APP-010) — Structure that must outlive a substate (a remembered situation, a cached computation, a task memory) is created on a superstate that persists as long as it is needed (the top state when it must last for the whole run), not in the substate.

*Rationale:* Local o-supported memories would be removed whenever the substate is regenerated.

*If violated:* Remembered information lost on substate regeneration.

*Example:*

```
(<ss> ^remembered <x>)
```

*See:* parent L0-042

*Source:* Manual §2.7.9.2, p.40-41; Tutorial Part 3, 5.1 Record-sound Operator; Tutorial Part 3, 6.1 The Map Data Structure and Initialization

### Learning: RL

**L2-013** (Requirement, Should, convention, shared with World-Conventions, formerly RL-009) — An RL rule tests the proposed operator (^operator <op> +) together with the state features that define the state-action pair whose value is learned.

*Rationale:* Each RL rule stands for one state-action value.

*If violated:* Values shared across distinct situations

*Example:*

```
(state <s> ^name water-jug ^operator <op> + ^jug <j1> <j2>) (<op> ^name empty ^empty-jug.volume 3) ...
```

*See:* parent L0-100

*Source:* Tutorial Part 6, 2.1 RL Rules

### Input/output link

**L2-014** (Requirement, Should, convention, shared with World-Conventions, formerly IO-010) — An output command is one attribute under the output-link that names the command; its value is an identifier that carries the command's parameters.

*Rationale:* The environment defines its commands this way and adds feedback such as ^status to the command object.

*If violated:* Malformed command ignored by the environment

*Example:*

```
(<out> ^move <m>) (<m> ^direction north)
```

*See:* parent L1-022

*Source:* Tutorial Part 2, 2.2.1 English Version; Tutorial Part 2, 2.10. Top-state Structure; Tutorial Part 3, 1.7 Summary of Input-link and Output-link

## L3 Guidance

Guidance from the Soar manual and tutorial that the library material supports.

### Project/file organization

**L3-001** (Requirement, Should, convention, formerly ORG-004) — Use VisualSoar (or another syntax-checking editor) and its datamap to check rules for syntax errors and misspelled attributes before loading them.

*Rationale:* Typos in attribute names (e.g. contant for content) produce rules that load but never match.

*If violated:* Silent non-matching rules

*Source:* Tutorial Part 1, 1.2.5 Working Memory; Tutorial Part 2, 2.5.1 Syntax Errors; Tutorial Part 2, 2.5.4 Semantic Errors

**L3-002** (Requirement, Should, convention, formerly ORG-006) — Formulate each task by writing, in order: state representation, initial-state creation, state elaborations, operator proposals, operator applications, monitoring rules, desired-state recognition, failure recognition (if any) and search control.

*Rationale:* A systematic formulation covers every kind of knowledge the problem needs.

*If violated:* Missing knowledge (e.g. no goal test)

*Source:* Tutorial Part 1, 1.4.13 Summary of Problem Formulation in Soar; Tutorial Part 4, 1. Missionaries and Cannibals Definition; Tutorial Part 5, 1. The Water Jug Problem

### Rule syntax/naming

**L3-003** (Requirement, Must, convention, shared with World-Conventions, formerly SYN-001) — Every production plays exactly one role, fixed by what it tests and what it creates: state elaboration, operator proposal, operator evaluation, operator elaboration, operator application, or monitoring. One combination is allowed: a proposal rule may also create unary preferences (best, worst, indifferent) for the operator it proposes. Soar warns about one mix of roles: when a rule that tests the selected operator both elaborates the operator and changes the state, it prints "Operator elaborations mixed with operator applications" when the rule fires and gives all its actions i-support (L0-042, L1-011).

*Rationale:* The rule types are what the other conventions are stated over; a checker classifies every rule first.

*If violated:* Rule cannot be classified; conventions cannot be checked

*Exceptions:* Escape-hatch (raw) rules

*Source:* Manual §3.3; Tutorial Part 1; Manual §2.1.1, p.6; §2.3.2, p.18

**L3-004** (Requirement, Must, convention, shared with World-Conventions, formerly SYN-030) — An action must not use dot notation to create several attributes of one new object: each dotted path creates a separate object. Create the object with a variable and add the attributes to that variable.

*Rationale:* Each dotted action path makes a new identifier.

*If violated:* Multiple command objects each with one attribute (e.g. two ^move commands)

*Example:*

```
(<out> ^move <m>)
(<m> ^direction north ^speed fast)
```

*See:* parent L1-002

*Source:* Tutorial Part 2, 2.2.3 Shortcuts

**L3-005** (Requirement, Should, convention, formerly SYN-033) — Every non-default rule tests, in its first condition, the name of the state it matches or of the problem space that state belongs to. This includes rules that fire in every state that holds a world (world and desired elaborations, internal operator applications). The exceptions are the rules that create a state's name or problem space: initialization (which tests ^superstate nil or the initialization operator) and the elaborations that give an operator no-change substate its problem space (which test the superstate's problem space).

*Rationale:* Scopes rules to their problem space; prevents firing in look-ahead copies or unrelated substates by accident.

*If violated:* Rules fire in the wrong states

*Exceptions:* Rules intended for all states (e.g. top-state links)

*Example:*

```
(state <s> ^name water-jug ...)
```

*See:* parent L2-005

*Source:* Tutorial Part 1; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 3, 2.1 Move Operator

**L3-006** (Requirement, May, convention, formerly SYN-040) — Format productions with the name right after sp {, conditions aligned under it, an object's attributes aligned, the arrow aligned with conditions, and the closing brace after the last action.

*Rationale:* Improves readability; not required by syntax.

*See:* parent L0-004

*Source:* Manual §3.3, p.49-50

**L3-007** (Requirement, Should, convention, formerly SYN-041) — Avoid the production type flags :o-support, :i-support, :default and :chunk in user rules. Get persistence by testing a selected operator rather than with :o-support; use any of these flags only with caution. Exception: a rule that records the effect of an external action once the environment reports the output command complete (an environment-effect rule) tests no selected operator and may be flagged :o-support. It may be better to make such rules part of the operator's application.

*Rationale:* Support and rule origin should follow from rule structure and source; the flags are easy to overuse and hide the real source of persistence.

*If violated:* Support that contradicts rule structure; unexpected persistent structures; confusing traces.

*Exceptions:* Default-rule files use :default. The tutorial uses :o-support only to illustrate map updating. Environment-effect rules may use :o-support (see Convention).

*Example:*

```
sp {map*record-object :o-support ...}
```

*Source:* Manual §3.3.3, p.50; Tutorial Part 3, 6.2 Updating the Map

**L3-008** (Requirement, May, convention, formerly SYN-042) — Use attribute-path notation to avoid intermediate linking variables where the path is single-valued.

*Rationale:* Shorter rules that are easier to read and less error prone.

*Exceptions:* Multi-valued intermediate attributes (see the preceding row).

*Example:* ^moving-block.name <n>

*See:* parent L1-002

*Source:* Manual §3.3.5.11, p.62

**L3-009** (Requirement, Should, convention, formerly SYN-043) — Do not combine negation, attribute-path notation and multi-valued attributes in one test; write one negated path per value instead.

*Rationale:* The expansion tests a single object with all values, which is rarely intended.

*If violated:* Negation tests the wrong condition.

*Example:*

```
-^ontop.bottom-object.name table
-^ontop.bottom-object.name A
```

*See:* parent L1-002

*Source:* Manual §3.3.5.11, p.64-65

**L3-010** (Requirement, Should, convention, formerly SYN-044) — Soar symbols are case sensitive (red, Red and RED differ); write all constants in a single case. Use lower case, for consistency across projects; use another case only where needed to match an environment, smem, epmem or input, quoting such names as in L1-004.

*Rationale:* Mixed case leads to silent mismatches.

*If violated:* Rules that never match because of case differences.

*Source:* Manual §3.3.6.2, p.68

**L3-011** (Requirement, Should, convention, formerly SYN-047) — For rules that implement an operator in a substate, use the substate's name (the superoperator name) as the first field of the rule name.

*Rationale:* Keeps track of which substate a rule belongs to.

*If violated:* Rules from different substates indistinguishable by name

*Exceptions:* Rules for operators shared by all substates use a prefix such as all.

*Example:*

```
sp {wander*propose*move ...}
```

*See:* parent L2-003

*Source:* Tutorial Part 3, 3.3 Wander Operator Suboperators

**L3-012** (Requirement, Should, convention, formerly SYN-048) — Precede each rule, or each group of rules for the same operator or purpose, with a #-comment giving an English version of its conditions and actions, written before the Soar version.

*Rationale:* The English version is documentation and helps design the rule.

*If violated:* Undocumented rules; harder debugging

*Example:*

```
# water-jug*propose*fill
# If the task is water-jug and there is a jug that is not full, propose filling it.
```

*Source:* Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator; Tutorial Part 3, 2.1 Move Operator

**L3-013** (Requirement, Should, convention, shared with World-Conventions, formerly SYN-049) — A variable in attribute position is usually restricted with a disjunction of the attributes it may match.

*Rationale:* An unrestricted attribute variable can bind to any attribute of the object, including unrelated ones.

*If violated:* Spurious matches (e.g. matching ^boat or ^other-bank)

*Example:*

```
(<bank> ^{ << cannibals missionaries >> <type> } > 0)
```

*See:* parent L0-008

*Source:* Tutorial Part 4, 4. Operator Proposal

### State representation

**L3-014** (Requirement, Should, convention, formerly STA-016) — Attribute and value names have no meaning to the architecture (apart from architecture-created WMEs); choose task labels deliberately and use them consistently across all rules.

*Rationale:* Matching is purely symbolic, so a misspelled or inconsistent label silently fails to match.

*If violated:* Rules that never fire because of inconsistent attribute names.

*Source:* Manual §2.2, p.15

**L3-015** (Requirement, Should, convention, shared with World-Conventions, formerly STA-017) — A domain entity is an object (an identifier with attributes such as ^volume and ^contents). Entity and property are not packed into one attribute name such as ^five-gallon-jug-contents.

*Rationale:* Rules cannot match parts of an attribute name, so structured objects allow general rules with variables.

*If violated:* Separate rules needed for each entity

*Example:*

```
(<s> ^jug <j1>)
(<j1> ^volume 5 ^contents 0)
```

*See:* parent L3-014

*Source:* Tutorial Part 1, 1.4.2 State Representation; Tutorial Part 4, 2. State Representation

**L3-016** (Requirement, Should, convention, shared with World-Conventions, formerly STA-018) — A set of similar objects is a multi-valued attribute (^jug <j1> ^jug <j2>).

*Rationale:* One set of rules can then process every member of the set.

*If violated:* Member-specific rules

*Example:*

```
(<s> ^jug <j1> <j2>)
```

*See:* parent L3-015

*Source:* Tutorial Part 1, 1.4.2 State Representation

**L3-017** (Requirement, Should, convention, shared with World-Conventions, formerly STA-020) — A fixed lookup table (for example each direction and its opposite) is working-memory structure created either by an elaboration that tests only that the state exists, or by the initialize-<task-name> operator and then copied into substates.

*Rationale:* General rules can then match relations directly instead of having one rule per case.

*If violated:* Proliferation of case-specific rules

*Example:*

```
(<ss> ^directions <n>)
(<n> ^value north ^opposite south)
```

*See:* parent L0-028

*Source:* Tutorial Part 2, 2.7.1 Initialization: Opposite Directions; Tutorial Part 3, 5.1 Record-sound Operator

**L3-018** (Requirement, Should, convention, formerly STA-021) — Encode a decision-relevant classification (e.g. low missiles or energy) once as an abstract state elaboration and have proposals test that elaboration, rather than repeating thresholds in each proposal.

*Rationale:* The threshold lives in one place and multiple rules creating the same WME collapse to one element.

*If violated:* Inconsistent thresholds across operators

*Example:*

```
(<s> ^missiles-energy low)
```

*See:* parent L3-031

*Source:* Tutorial Part 3, 4.1 Chase Operator Proposal

**L3-019** (Requirement, Should, convention, shared with World-Conventions, formerly STA-022) — Where ^io is copied into substates, a rule meant only for the top state tests ^superstate nil, not just the presence of ^io.

*Rationale:* Otherwise the elaboration fires again in every new substate.

*If violated:* Duplicate elaborations in every substate

*Example:*

```
(state <s> ^name tanksoar ^io.input-link.missiles 0)
```

*See:* parent L4-009

*Source:* Tutorial Part 3, 4.1 Chase Operator Proposal; default simple.soar default*elaborate*state*io

**L3-020** (Requirement, Should, convention, formerly STA-023) — Copy or derive input-link values needed by a substate onto that substate with an elaboration (e.g. ^sound-direction), or copy the whole ^io structure down to the substate, and have the substate's rules test the local copy.

*Rationale:* If the source of the value later changes (e.g. to a remembered value), only the elaboration has to change.

*If violated:* Many rules to edit when the representation changes

*Example:*

```
sp {chase*elaborate*state*sound-direction (state <s> ^name chase ^io.input-link.sound <d>) --> (<s> ^sound-direction <d>)}
```

*See:* parent L0-112

*Source:* Tutorial Part 3, 4.2 Chase Operator Application; Tutorial Part 3, 5.1 Record-sound Operator

**L3-021** (Requirement, Should, convention, formerly STA-025) — To remember the previous operator, an application rule copies what later rules need (its name and the parameters that identify it, e.g. ^name pour ^fill-jug <fj> ^empty-jug <ej>) into a state structure ^last-operator, rather than keeping a pointer to the operator identifier. Maintenance is L4-005; uses are L3-047.

*Rationale:* The selected operator and its substructure go away once its proposal retracts, so a pointer to it ends up empty. The parameters are needed to tell what the operator did, not just its name.

*If violated:* Record vanishes or becomes empty; an undo cannot be identified from the name alone

*Example:*

```
(<s> ^last-operator <lo>)
(<lo> ^name pour ^fill-jug <fj> ^empty-jug <ej>)
```

*See:* parent L2-012

*Source:* Tutorial Part 1, 1.4.11 Search Control

**L3-022** (Requirement, May, convention, formerly STA-026) — Exception to L2-010: remove an incorrect value in its own application rule only when the current value is known to be incorrect but a correct value is not yet available; add the correct value later when it is.

*Rationale:* A single rule cannot handle both the initial case (no old value) and the update case.

*If violated:* Accumulating stale values, or missing initial value

*Exceptions:* Structures that never change can be created by an elaboration that tests only the state.

*Example:*

```
(<s> ^last-direction <d> -)
```

*See:* parent L2-010

*Source:* Tutorial Part 2, 2.7.2 Advanced Move Operator Application; Tutorial Part 1, 1.4.11 Search Control

**L3-023** (Requirement, Should, convention, shared with World-Conventions, formerly STA-029) — Attributes that link task objects to each other and never change (for example ^other-bank) are left out of duplicate-state tests and RL templates.

*Rationale:* Identifiers differ between a state and its look-ahead copies, so comparing links never matches.

*If violated:* Duplicates never detected; RL features never match

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Goal/desired representation

**L3-024** (Requirement, Should, convention, shared with World-Conventions, formerly GOL-012) — The goal is a structure on the state, created at initialization, and success is recognized by comparing it with the current state; the goal is not hard-coded in a rule.

*Rationale:* New problems can be posed by changing working memory, and the desired state can guide search.

*If violated:* Goal changes require editing rules

*Exceptions:* Simple first agents hard-code the goal test.

*Example:*

```
(<s> ^desired.jug <k>)
(<k> ^volume 3 ^contents 1)
```

*See:* parent L3S-002

*Source:* Tutorial Part 1, 1.4.10 Desired State Recognition; Tutorial Part 4, 3. Initial State Creation: Initialize-mac

**L3-025** (Requirement, Should, convention, shared with World-Conventions, formerly GOL-015) — A losing or failure state is recognized by a separate i-supported rule that marks the state (^failure <desireds>). Operator proposals may also encode failure avoidance when that knowledge is available, but it rarely is, so the failure mark is the general mechanism.

*Rationale:* An i-supported mark retracts automatically when the state is no longer a failure. Failure knowledge in a proposal is correct only where it is known in advance, and it moves problem knowledge into the problem space.

*If violated:* Failures that are not recognized, or problem-space legality mixed with failure knowledge

*Example:*

```
(<bank> ^missionaries { <n> > 0 } ^cannibals > <n>) --> (<s> ^failure <d>)
```

*See:* parent L5-008

*Source:* Tutorial Part 4, 1. Missionaries and Cannibals Definition; Tutorial Part 4, 9. Search Control: Undoing the Last Operator

### Operator WM representation

**L3-026** (Requirement, Should, convention, formerly OPR-012) — Put on the operator any information that later selection rules need to compare it (e.g. the content of the target cell), so search control need not re-derive it.

*Rationale:* Simpler selection rules that test only the proposed operators.

*If violated:* Complex selection rules that rematch the state

*Example:*

```
(<o> ^name move ^direction <dir> ^content <content>)
```

*See:* parent L2-007

*Source:* Tutorial Part 2, 2.6.1 Move Operator Proposal

**L3-027** (Requirement, Should, convention, formerly OPR-013) — Where practical, make the operator representation describe the change it makes (e.g. entity type as attribute and count as value) so that a single general application rule can apply all instances.

*Rationale:* General application rules replace many operator-specific ones.

*If violated:* Many near-duplicate application rules

*Example:*

```
(<o> ^name move-mac-boat ^bank <b> ^cannibals 1 ^boat 1 ^types 1)
```

*See:* parent L2-007

*Source:* Tutorial Part 1, 1.3 Building a Simple Hello-World Agent Using an Operator; Tutorial Part 4, 4. Operator Proposal; Tutorial Part 4, 5. Operator Application

**L3-028** (Requirement, Should, convention, formerly OPR-014) — For operators that perform external actions, place the output commands on the operator under an ^actions object (^actions.<command>.<param> <value>), so generic rules can copy them to the output-link.

*Rationale:* A single generic rule then performs output for every operator without copying unrelated operator augmentations.

*If violated:* Need for per-operator output rules

*Exceptions:* Operators whose action has internal effects too still need their own application rules.

*Example:*

```
(<o> ^name jump ^actions.jump.direction <dir>)
```

*See:* parent L1-022

*Source:* Tutorial Part 2, 2.8.3 Simplified Operators; Tutorial Part 3, 2. Simple Wandering Tank

**L3-029** (Requirement, Must, convention, shared with World-Conventions, formerly OPR-015) — Each action in the world is performed by a new operator instance. One selected operator must not be expected to perform repeated actions.

*Rationale:* Each instance is selected and applied once; repetition comes from re-proposal.

*If violated:* Agent acts once and then reaches an impasse

*See:* parent L0-052

*Source:* Tutorial Part 2, 2.3.1 Operator Selection: Multiple Instances

**L3-030** (Requirement, Should, convention, shared with World-Conventions, formerly OPR-016) — A parameter that ranges over a small set of constants (for example move 1 or 2 missionaries) gets one proposal rule per value, with the value as a constant on the operator; application rules read it from the operator.

*Rationale:* Operator instances are distinguishable for preferences, chunking and RL.

*If violated:* Instances indistinguishable

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Rule: state elaboration

**L3-031** (Requirement, Should, convention, shared with World-Conventions, formerly ELB-011) — A feature that is entailed by core state features (a block is clear, a jug's free space) may be an i-supported elaboration, so that operator applications change only the core features, provided that both its presence and its absence are computed by rules and those rules use no local negations (negations over structure in a substate such as a look-ahead state). A feature that cannot be computed that way is maintained by the operator applications that change it.

*Rationale:* Elaborations retract and re-derive automatically, which simplifies operator encoding. A rule that tests the absence of structure leaves a local negation out of any chunk built from it, so the chunk is over-general.

*If violated:* Application rules that must maintain every derived feature by hand; or chunks that are over-general because a derived feature is computed with a local negation.

*See:* parent L0-028

*Source:* Manual §2.1.9, p.12; Tutorial Part 1, 1.4.5 Water Jug State Elaboration; Tutorial Part 1, 1.4.13 Summary of Problem Formulation in Soar

### Rule: operator proposal

**L3-032** (Requirement, Must, convention, shared with World-Conventions, formerly OPR-017) — An operator that is carried out by suboperators which change what its proposal tests is proposed through a relevance elaboration (^<op>-relevant), so that the same operator stays selected while its substate works. The relevance elaboration is an i-supported rule on the state that tests the situations in which the operator is relevant, including the intermediate situations its suboperators create (for example, the jug is not full, or is full and still held), and creates ^<op>-relevant with the object the operator applies to; the proposal rule tests ^<op>-relevant in place of the conditions the suboperators change.

*Rationale:* Otherwise each result retracts the proposal, a new operator is made, and the substate ends and is rebuilt.

*If violated:* Hierarchical operator re-proposed after every sub-operator result

*Source:* Small families (agentgen, 6 Nov 2026)

**L3-033** (Requirement, Should, convention, shared with World-Conventions, formerly PRO-004) — An operator proposal should test WMEs that the operator's application (or its effect on input) changes, so that the proposal retracts after the application and a new decision follows.

*Rationale:* An operator stays selected while its acceptable preference remains and no better candidate appears.

*If violated:* Operator no-change impasse after the operator has effectively applied.

*Exceptions:* Operators intentionally left selected to wait on the external world.

*Example:*

```
(state <s> ^io.input-link.eater <e>) (<e> ^x <x> ^y <y>)
```

*See:* parent L0-052

*Source:* Manual §2.5, p.25; §2.7.1, p.28; §2.7.7, p.35; Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 2, 2.3.1 Operator Selection: Multiple Instances; Tutorial Part 4, 5. Operator Application

**L3-034** (Requirement, Must, convention, shared with World-Conventions, formerly PRO-007) — An operator whose application would leave the state unchanged (for example filling a full jug) must not be proposed.

*Rationale:* If application changes nothing, the proposal never retracts and the operator never terminates.

*If violated:* Operator no-change impasse / stuck operator

*Example:*

```
(<j> ^empty > 0)
```

*See:* parent L3-033

*Source:* Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L3-035** (Requirement, Must, convention, shared with World-Conventions, formerly PRO-010) — To exclude an option, a proposal does not test the absence of a record (-^last-direction <dir>): the negated test is dropped from chunks learned in a substate, such as a look-ahead, and the chunk is over-general (L3-062). The record always exists (it is initialized, for example ^last-direction none) and the proposal tests the presence of a record with a different value (^last-direction <> <dir>).

*Rationale:* A negated test on state structure is a local negation in a substate and is left out of the chunk. A presence test is a positive condition that chunking keeps, but it fails when no record exists yet, so the record must exist from the first decision.

*If violated:* Over-general chunks from look-ahead; or, if the record is not initialized, the operator is never proposed in the initial situation.

*Example:*

```
(state <s> ^directions <d> ^last-direction <> <o-dir>) (<d> ^value <dir> ^opposite <o-dir>)
# initialization: (<s> ^last-direction none)
```

*See:* parent L0-010

*Source:* Tutorial Part 2, 2.7.3 Advanced Move Operator Proposal

**L3-036** (Requirement, Should, convention, shared with World-Conventions, formerly PRO-015) — A proposal's conditions state when the operator is relevant to the situation. Relevance is a design decision and may come from the goal, so an operator can be proposed before its preconditions hold.

*Rationale:* Soar programs are organised implicitly by problem spaces via proposal conditions.

*If violated:* Irrelevant operators proposed, causing ties.

*Example:*

```
(state <s> ^problem-space blocks)
```

*See:* parent L0-029

*Source:* Manual §2.1.10, p.12

**L3-037** (Requirement, Should, convention, formerly PRO-016) — Always write the + for acceptable preferences in actions, even though it is implicit when no other preference is given for that operator.

*Rationale:* Makes the semantics explicit; a non-acceptable preference alone does not imply acceptable.

*If violated:* An operator given only (> ) is never selected.

*Example:*

```
(<s> ^operator <o> + >)
```

*See:* parent L2-008

*Source:* Manual §3.3.6.4-3.3.6.5, p.69-70

**L3-038** (Requirement, Should, convention, formerly PRO-017) — Precondition style: an operator is proposed if and only if its preconditions are satisfied; whether it should be chosen is left to selection knowledge. This is not the means-ends analysis (MEA) style, in which an operator is proposed when it is relevant to the goal even if its preconditions are not satisfied, and an operator no-change impasse sets up subgoals to achieve them.

*Rationale:* Separating problem-space knowledge from search control is a design goal of Soar.

*If violated:* Proposal rules tangled with heuristics

*See:* parent L3-036

*Source:* Tutorial Part 1, 1.4.1. Water Jug; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals

**L3-039** (Requirement, Should, convention, formerly PRO-019) — Add an indifferent preference (+ =) to proposals only when the order in which the competing operators are chosen does not matter, for example when the operators are monotonic (each only adds to the state and none blocks or undoes another, so every order reaches the same result); not as a default way to avoid ties. Agents converted to RL leave it out (L3-083).

*Rationale:* Indifference asserts knowledge that the options are equivalent; ties are the signal that more problem solving (e.g. look-ahead) is needed.

*If violated:* Random choices where deliberation was needed; planning never invoked

*Exceptions:* Early agents use + = for random search on purpose.

*Example:*

```
(<s> ^operator <o> + =)
```

*See:* parent L3-038

*Source:* Tutorial Part 5, 1. The Water Jug Problem; Tutorial Part 1, 1.4.7 Water Jug Operator Proposals; Tutorial Part 2, 2.4 Move-To-Food Operator

**L3-040** (Requirement, Should, convention, formerly PRO-020) — Do not propose two operators in a single rule. Exception: one rule may propose a fixed set of operators that differ only in a constant parameter (for example move with direction -1 and move with direction 1).

*Rationale:* One operator per proposal rule keeps rules separate and easy to debug.

*If violated:* Coupled operators; hard debugging

*See:* parent L3-003

*Source:* Tutorial Part 3, 7.2 Final Thoughts

**L3-041** (Requirement, May, convention, shared with World-Conventions, formerly PRO-023) — Means-ends style: an operator is proposed when it can achieve part of the desired state, whether or not its preconditions hold. Unmet preconditions are achieved in its operator no-change substate before it applies.

*Rationale:* Means-ends analysis: the goal, not the current state alone, determines relevance.

*See:* parent L3-036

*Source:* Decided 6 Nov 2026 (JL)

**L3-042** (Requirement, May, convention, formerly PRO-024) — In either style, proposals may be further restricted by heuristic conditions that exclude operators that are applicable or goal-relevant but not useful in the situation.

*Rationale:* Efficiency; heuristic knowledge in proposals.

*See:* parent L3-036

*Source:* Decided 6 Nov 2026 (JL)

### Rule: operator elaboration

**L3-043** (Requirement, Should, convention, formerly OEL-004) — Issue reflex-like commands (e.g. shields on/off) by adding them to the ^actions of whatever operator is selected, not by writing directly to the output-link from a non-operator rule.

*Rationale:* Direct writes produce output early and can preempt other output in environments that run the agent until output appears.

*If violated:* Output generated before the real action is ready

*Example:*

```
sp {elaborate*shields-on (state <s> ^operator.actions <a> ^io.input-link <il>) (<il> ^incoming.<dir> yes ^shield-status off) --> (<a> ^shields.switch on)}
```

*See:* parent L3-028

*Source:* Tutorial Part 3, 4.8 Shield Control Rules

### Rule: operator evaluation/selection

**L3-044** (Requirement, Should, convention, formerly EVA-016) — Use require (!) rather than best (>) when an operator must be selected, because a candidate that is better than a best candidate wins over it.

*Rationale:* BetterWorseFilter runs before BestFilter.

*If violated:* A best operator unexpectedly loses to a better preference.

*See:* parent L0-031

*Source:* Manual §2.4.1, p.20

**L3-045** (Requirement, May, convention, formerly EVA-017) — Use a worst (<) preference as a default: a worst operator is chosen only when there are no non-worst alternatives.

*Rationale:* WorstFilter removes worst candidates unless all are worst.

*Example:*

```
(<s> ^operator <o> <)
```

*See:* parent L3-046

*Source:* Manual §2.4.1, p.20

**L3-046** (Requirement, Should, convention, formerly EVA-018) — Use a reject preference when an operator must not be selected in the current situation even if nothing else is available; use a worst preference when it may be selected but only if nothing better exists.

*Rationale:* Reject removes the option entirely, while worst only orders it last.

*If violated:* Agent stuck (reject) or does pointless actions (worst)

*Example:*

```
(<s> ^operator <o> -)  vs  (<s> ^operator <o> <)
```

*See:* parent L0-031

*Source:* Tutorial Part 2, 2.7.4 Advanced Move Operator Selection; Tutorial Part 2, 2.6.4 Summary of Preferences

**L3-047** (Requirement, May, convention, formerly EVA-019) — Use a worst preference to avoid immediately undoing the previous operator (matching the proposed operator against ^last-operator, L3-021).

*Rationale:* A cheap heuristic that shortens undirected search.

*If violated:* Wasted inverse operator applications

*Exceptions:* Superseded by duplicate-state detection when look-ahead is used.

*Example:*

```
(<o> ^name fill ^fill-jug <i>) (<lo> ^name empty ^empty-jug <i>) --> (<s> ^operator <o> <)
```

*See:* parent L3-045

*Source:* Tutorial Part 1, 1.4.11 Search Control; Tutorial Part 4, 9. Search Control: Undoing the Last Operator

**L3-048** (Requirement, Should, convention, formerly EVA-021) — In look-ahead, reject an operator that undoes the previous operator (matching the proposed operator against ^last-operator, L3-021).

*Rationale:* An operator that undoes the previous one returns to the previous state, so evaluating it adds nothing; a reject removes it from the look-ahead search.

*If violated:* Look-ahead spends decisions evaluating operators that return to the previous state

*See:* parent L5-011

*Source:* Tutorial Part 5, 2.1.6 Remove last-operator rules; Tutorial Part 5, 1.4.4 Evaluating the result

**L3-102** (Choice, Should, convention, shared with World-Conventions) — Set the policy for choosing among indifferent operators explicitly with decide indifferent-selection and the policy's name (--epsilon-greedy, --boltzmann, --softmax, --first, --last); the default is softmax. A one-letter option with no value only reports a setting: decide indifferent-selection -e prints epsilon and leaves the policy unchanged. Use epsilon-greedy or Boltzmann with a low temperature when numeric preferences (expected values, RL values) should steer the choice.

*Rationale:* Under softmax, numeric preferences that differ by small amounts give nearly equal probabilities, so learned or estimated values hardly change the choice.

*If violated:* The agent chooses almost at random among operators whose values differ (eight-puzzle-expected-value solved only by luck until library v2.45).

*Example:* decide indifferent-selection --epsilon-greedy (epsilon 0.1 by default; decide indifferent-selection --epsilon 0.05 changes it)

*Source:* Soar 9.6 decide command; Soar-library CHANGES.md v2.45; to-do row 2 (20 Nov 2026)

### Rule: operator application

**L3-049** (Requirement, Should, convention, formerly APP-021) — Prefer modifying the attributes of existing state objects in application rules over deleting and recreating whole objects.

*Rationale:* Fewer working-memory changes and a more natural model (the jug is the same jug); two-level state copying supports look-ahead.

*If violated:* More WM churn; unnatural representation

*Exceptions:* Replacing objects can reduce copying in look-ahead.

*See:* parent L0-042

*Source:* Tutorial Part 1, 1.4.8 Operator Application; Tutorial Part 5, 1.4.1 Creating the Initial State

**L3-050** (Requirement, Should, convention, formerly APP-022) — When several application rules are needed for one operator (e.g. different situations for pour), make their conditions mutually exclusive.

*Rationale:* Only the rule matching the situation should fire.

*If violated:* Conflicting changes applied together

*Exceptions:* Rules that perform independent parts of one application may fire together.

*Example:* ^contents { <= <jempty> <icon> } vs ^contents { <icon> > <jempty> }

*See:* parent L0-041

*Source:* Tutorial Part 1, 1.4.8 Operator Application

**L3-051** (Requirement, Should, convention, formerly APP-025) — An attribute should be maintained either by elaborations (i-support) or by operator applications (o-support), not both.

*Rationale:* Mixed support makes values reappear or vanish unexpectedly.

*If violated:* Values reappear after removal, or disappear

*Source:* Consolidation review (gap); Manual §2.3.3

**L3-052** (Requirement, Should, convention, formerly APP-026) — When an operator may apply to an attribute that has no current value, provide a separate application rule that adds the value only when none exists (tests -^attr); the rule of L2-010 changes the value when one exists. Together they cover both cases. It is preferred that the attribute is initialized when its object is created, so that this rule is not needed.

*Rationale:* L2-010's rule needs an old value to match; without one it does not fire.

*If violated:* Attribute never set when it starts with no value

*Exceptions:* Attributes always created by initialization

*Example:*

```
(state <s> ^operator <o>) (<o> ^name set ^value <v>)
-(<s> ^attr)
--> (<s> ^attr <v>)
```

*See:* parent L2-010

*Source:* Decided 6 Nov 2026 (JL)

### Rule: monitoring/output

**L3-053** (Requirement, Should, convention, shared with World-Conventions, formerly MON-002) — (halt) is used only when the run must end for good; (interrupt) is used for debugging, to stop the run so that the program can be examined and resumed.

*Rationale:* Halt terminates the run irreversibly.

*If violated:* Agent cannot be continued.

*Source:* Manual §3.3.6.6, p.71

**L3-054** (Requirement, Should, convention, formerly MON-003) — Avoid the (wait) RHS function.

*Rationale:* The manual discourages it; it sleeps the Soar thread.

*If violated:* Slow or stalled agent.

*Source:* Manual §3.3.6.6, p.72

**L3-055** (Requirement, Should, convention, shared with World-Conventions, formerly MON-004) — write, crlf and log are for simple text output; extensive text input and output goes through SML.

*Rationale:* RHS text functions are minimal debugging output.

*Example:*

```
(write (crlf) |Moving | <n>)
```

*See:* parent L0-047

*Source:* Manual §3.3.6.6, p.72

**L3-056** (Requirement, Should, convention, shared with World-Conventions, formerly MON-006) — Monitoring rules are separate from problem-solving rules: they test the state or the selected operator and only print. They fire in parallel with application and do not affect it.

*Rationale:* Printing the operator and state makes problem solving easy to follow without interfering with it.

*If violated:* Monitoring mixed into functional rules

*Example:*

```
sp {water-jug*monitor*operator-application*fill (state <s> ^name water-jug ^operator <o>) (<o> ^name fill ^fill-jug.volume <v>) --> (write | FILL(| <v> |)|)}
```

*See:* parent L0-047

*Source:* Tutorial Part 1, 1.4.9 State and Operator Monitoring; Tutorial Part 2, 2.4.3 Shortcuts and Extensions

### Rule: impasse/substate handling

**L3-057** (Requirement, Should, convention, shared with World-Conventions, formerly IMP-013) — An operator whose substate creates local o-supported structure should be implemented so that it is re-entrant: it resumes correctly after the goal dependency set regenerates its substate (L0-054). Soar does not guarantee this; it depends on how the substate is written.

*Rationale:* The GDS may remove and recreate the substate at any time.

*If violated:* Partial work repeated or corrupted after regeneration.

*See:* parent L0-054

*Source:* Manual §2.7.9.2, p.40

**L3-058** (Requirement, May, convention, formerly IMP-020) — Impasses are a normal way to decompose problems and deliberate about selection, not necessarily a program error; impasses are required for chunking to learn.

*Rationale:* Substates are Soar's mechanism for hierarchical decomposition and learning.

*Source:* Manual §2.7.7, p.34

**L3-059** (Requirement, May, convention, formerly IMP-021) — Use (or adapt) the default productions for handling impasses rather than writing ad-hoc impasse handling from scratch.

*Rationale:* The default rules provide standard ways of resolving common impasses.

*Source:* Manual §3.4.1, p.85

**L3-060** (Requirement, May, convention, formerly SET-014) — When a state no-change should mean waiting rather than impassing (e.g. expert models waiting on the world), enable soar wait-snc so no substate is created.

*Rationale:* A wait state repeats the decision cycle without creating a substate.

*If violated:* Spurious substates while waiting.

*Example:* soar wait-snc on

*See:* parent L0-051

*Source:* Manual §9.1.1 soar wait-snc, p.190

### Substate representation

**L3-061** (Requirement, Should, convention, formerly SUB-012) — Store features locally in the substate for local non-monotonic reasoning about the context (e.g. counting, projection/planning), accepting that the substate is removed when its context changes.

*Rationale:* Such reasoning is only valid relative to the current context.

*See:* parent L0-059

*Source:* Manual §2.7.9.2, p.41

### Rule: results

**L3-062** (Requirement, Should, convention, shared with World-Conventions, formerly RES-011) — A rule on the path to a result should not test the absence of local substate structure: the negation is dropped from the chunk or justification, which is then over-general (L0-091). Remedies: hold the tested data in the superstate, make it a result, or set chunk allow-local-negations off to reject such chunks.

*Rationale:* Only negated conditions on superstate WMEs are carried into justifications.

*If violated:* Over-general justification or chunk.

*Example:* -(<s> ^tried <x>) # local negation, dropped

*See:* parent L0-091

*Source:* Manual §2.7.4, p.32; §4.5.2.1, p.104; §4.6.10, p.112; Manual §4 (EBC: local negations)

**L3-063** (Requirement, Should, convention, shared with World-Conventions, formerly RES-012) — A previous result is tested or changed through a path from the superstate, not through a path local to the substate. Otherwise explanation-based chunking repairs the chunk with grounding conditions that can over-specialize it.

*Rationale:* EBC cannot know where in the superstate a result lives when it is reached via a local path.

*If violated:* Repaired, over-specialised chunks (shown in chunk stats).

*Exceptions:* If the repaired path always exists, the repaired rule is as general.

*Source:* Manual §4.6.7, p.110-111; §4.5.3.6, p.107

**L3-064** (Requirement, Should, convention, shared with World-Conventions, formerly RES-013) — When a result depends on the impasse itself, that is, on there being nothing more to come (for example a state no-change after every operator is exhausted), the rule that creates it tests ^quiescence t. The test signals that what is computed depends on the impasse having occurred; as a consequence no chunk is learned for that result (L0-094).

*Rationale:* Without the test, the chunk would leave out its dependence on the impasse and could fire where no impasse would have occurred.

*If violated:* Over-general chunk that fires in situations without the impasse.

*Exceptions:* Can be ignored when learning is off.

*Example:*

```
(state <s> ^quiescence t)
```

*Source:* Manual §4.6.11, p.112-113; §4.6.17, p.118; Manual §3.4.1, p.85; §4.6.11, p.112

**L3-065** (Requirement, Should, convention, shared with World-Conventions, formerly RES-015) — Semantic or episodic knowledge needed for a result should be retrieved in a higher state, not in the substate where learning occurs. Soar does not trace back to the cue of a semantic or episodic retrieval: conditions on knowledge recalled in the substate are local and are dropped from the chunk.

*Rationale:* There is no backtracing to the cue, so recalled knowledge is treated as local and its retrieval reasons are opaque.

*If violated:* Over-general chunks.

*Exceptions:* Learning-from-instruction designs that intentionally exclude recalled instructions.

*Source:* Manual §4.6.13, p.113-114

**L3-066** (Requirement, May, convention, formerly RES-018) — Substate structures become results indirectly when their identifier becomes linked to a superstate through another result. This gives an approach for creating all of a result at once instead of incrementally: build the structure locally in the substate, then link it to the superstate last (e.g., build an operator's structure locally, then create its acceptable preference in the superstate).

*Rationale:* Linking makes the entire substructure results at once.

*If violated:* Superstate sees a partially constructed operator.

*Example:*

```
(<ss> ^operator <o> +)  # after <o> is complete
```

*See:* parent L0-062

*Source:* Manual §2.7.3, p.31

### Semantic memory

**L3-067** (Requirement, Should, convention, formerly SET-010) — Keep the semantic store in memory for most runs; if using a file database, leave lazy-commit on and set path and append before initialisation (changes take effect after --init).

*Rationale:* Disk-based stores are costly; storage parameters apply only after init.

*If violated:* Slow runs, or settings with no effect.

*Example:* smem --set database memory

*See:* parent L1-023

*Source:* Manual §6.3.4, p.147; §6.5.2, p.153

**L3-068** (Requirement, Should, convention, shared with World-Conventions, formerly SMM-011) — A rule that uses a semantic-memory retrieval tests ^result.success or ^result.failure, and the retrieved structure, before it acts on ^result.retrieved.

*Rationale:* Retrieval may fail and results arrive only after the command is processed.

*If violated:* Rules acting on missing or stale results.

*Example:*

```
(<s> ^smem.result.retrieved <r>)
```

*See:* parent L0-071

*Source:* Manual §6.4.1-6.4.2, p.148-149; Tutorial Part 7, 4. Non-Cue-Based Retrieval; Tutorial Part 7, 5. Cue-Based Retrieval

**L3-069** (Requirement, May, convention, formerly SMM-017) — Use ^prohibit <lti> modifiers (repeatable) to exclude already-retrieved LTIs and iterate over all matches; use ^neg-query and ^math-query to constrain the cue.

*Rationale:* Ties among matching LTIs go to the most activated LTI.

*If violated:* Repeated retrieval of the same LTI.

*Example:*

```
(<cmd> ^query <q> ^prohibit <old>)
```

*See:* parent L0-073

*Source:* Manual §6.4.2, p.149-150

**L3-070** (Requirement, Should, convention, formerly SMM-018) — Use ^depth <n> with a retrieval only when necessary, since deep retrievals can be costly.

*Rationale:* Retrieves children recursively.

*If violated:* Slow retrievals.

*Example:*

```
(<cmd> ^query <q> ^depth 2)
```

*See:* parent L0-071

*Source:* Manual §6.4.3, p.152-153

### Episodic memory

**L3-071** (Requirement, Should, convention, formerly EPM-010) — Keep episodic cues small and avoid cues that relate to every episode or include multi-valued identifiers needing graph matching, since retrieval can be linear in episodes or combinatorial in literals.

*Rationale:* Cue-based search and graph match are the unbounded costs.

*If violated:* Very slow retrievals.

*See:* parent L0-079

*Source:* Manual §7.4, p.161-162

**L3-072** (Requirement, Should, convention, formerly EPM-011) — Propose an episodic query operator only when the command link is empty (-^epmem.command.<cmd>), and replace the previous command when issuing the next one (e.g. ^query with ^next).

*Rationale:* One command at a time; the agent maintains the command link.

*If violated:* Repeated or conflicting commands

*Example:*

```
(state <s> ^name epmem -^epmem.command.<cmd>)
```

*See:* parent L0-074

*Source:* Tutorial Part 8, 4. Cue-Based Retrieval; Tutorial Part 8, 5. Temporal Progression

### Learning: chunking

**L3-073** (Requirement, Should, convention, shared with World-Conventions, formerly CHK-018) — Learning should be off in a substate whose result depends on a probabilistic choice among indifferent or numeric-indifferent operators: no chunk summarizes that reasoning correctly.

*Rationale:* A different random choice could produce a different result.

*If violated:* Incorrect chunks.

*Example:*

```
(dont-learn <s>) with chunk except
```

*Source:* Manual §4.6.9, p.111

**L3-074** (Requirement, Should, convention, shared with World-Conventions, formerly CHK-019) — Substate rules should test only what is needed to produce the result: a chunk's conditions are exactly what the substate rules tested.

*Rationale:* Unneeded tests carry over into the learned rule.

*If violated:* Overly specific chunks

*See:* parent L0-085

*Source:* Tutorial Part 5, 1.4.5 Chunking

**L3-075** (Requirement, Should, convention, shared with World-Conventions, formerly CHK-021) — Application rules test every operator attribute that distinguishes one operator instance from another, so that chunks learned from evaluations include those distinctions.

*Rationale:* Chunking picks up only what the rules tested; untested distinguishing features yield overgeneral rejections.

*If violated:* Overgeneral chunk rejects an operator on the solution path

*Example:*

```
(<o> ^name move-mac-boat ^{ << missionaries cannibals boat >> <type> } <num> ^bank <bank> ^types <types>)
```

*See:* parent L3-074

*Source:* Tutorial Part 5, 2.2 Subtle chunking problem

**L3-076** (Requirement, Should, convention, shared with World-Conventions, formerly CHK-022) — With chunking, exact evaluations (success, failure) are preferred to heuristic numeric evaluations that are only partly correct: a chunk captures the heuristic's errors too.

*Rationale:* Chunking is only as good as the problem solving it summarizes.

*If violated:* Learned rules embody heuristic mistakes; worse performance

*Exceptions:* Heuristics may still help when chunking is off.

*Source:* Tutorial Part 5, 2.3 Numeric Evaluations

**L3-077** (Requirement, Should, convention, shared with World-Conventions, formerly CHK-026) — When several superstate structures can each produce the same local substate WME that a result depends on, put that WME on the superstate (make it a result) instead of in the substate, so that the learned rule creates one result (L0-099).

*Rationale:* The rule learned then produces one result regardless of how many rules create the WME.

*If violated:* Incorrect chunks from disjunctive context conflation.

*See:* parent L0-099

*Source:* Soar manual (online, soargroup.github.io, 6 Oct 2026): 4.6.12 Disjunctive Context Conflation

**L3-078** (Requirement, May, convention, formerly SET-005) — Do not declare chunking singletons by hand: Soar 9.6.5 creates them automatically for string attributes (chunk automatically-create-singletons, on by default). Declare one with chunk singleton only where the automatic ones do not apply.

*Rationale:* Removes unnecessary generality and redundant conditions in chunks.

*If violated:* Redundant, over-general conditions in learned rules.

*Exceptions:* Attributes the automatic singletons do not cover

*Example:* chunk singleton state gripper identifier

*See:* parent L0-088

*Source:* Manual §4.4.1, p.100; §4.7.3.2, p.120; §9.4.1, p.232; Soar online CLI reference, chunk (automatically-create-singletons); Soar 9.6.5 build 9.6.50

**L3-079** (Requirement, Should, convention, formerly SET-007) — Use chunk stats and the explain mechanism (rather than backtracing traces) to diagnose repaired rules, local negations, and LTM-dependent chunks.

*Rationale:* Stats report potential generality and correctness issues directly.

*Example:* chunk stats

*Source:* Manual §4.7.3.1, p.120; §4.7.4, p.120-122

**L3-080** (Requirement, Should, convention, formerly SET-015) — If chunking hits max-chunks, stop execution and investigate rather than continuing.

*Rationale:* The manual warns Soar cannot then guarantee consistency of its internal structures.

*If violated:* Inconsistent agent state.

*Source:* Manual §9.4.1.4 chunk max-chunks, p.235

**L3-099** (Requirement, Should, convention, shared with World-Conventions) — A rule whose result can reach a chunk tests with $ (^attr $ <v>) a value that must stay a constant in the chunk, such as an object's name or handle, so that the chunk does not transfer to other objects. Until the Soar 9.6.50 defects are fixed: no $ inside a negated condition, and none inside a { } test that also holds a relational test.

*Rationale:* Chunking turns such values into variables and adds no inequality between them, so a chunk learned for one object can fire for another. Cost: chunks transfer only to the same named objects.

*If violated:* Over-general chunks. With $ in the excepted places, Soar reports "bad test type in hash_test ... cannot recover" (negated condition) or crashes when the rule loads ({ <> <x> $ <h> }).

*Example:*

```
(<b> ^object-handle $ <bh>) (<d> ^object-handle { <> <bh> <dh> })
```

*See:* parent L0-087

*Source:* Generalized from World-Conventions L11-005 (20 Nov 2026); FINDING-chunking-overgeneral.md; soar-dollar-bugs.zip

**L3-100** (Requirement, Should, convention, shared with World-Conventions) — A concept defined by the absence of structure (a block is clear, a container is empty) that a rule on the path to a chunk tests is kept as a maintained attribute or relation: created and removed by the operator applications that change it, and tested with positive conditions.

*Rationale:* A negation over substate structure is left out of the chunk (L0-091, L3-062), so the chunk is over-general; a maintained positive structure is kept.

*If violated:* Over-general chunks: with chunking on, look-ahead prefers longer or blocked paths.

*Example:*

```
(<w> ^clear <cd> - <nc>) in the move application, instead of an elaboration that tests -{(<w> ^on <r>) (<r> ^argument2 <o>)}
```

*See:* parent L3-062

*Source:* Generalized from World-Conventions L11-003 (20 Nov 2026); FINDING-chunking-overgeneral.md

**L3-103** (Requirement, Should, convention, shared with World-Conventions) — A state evaluation computed in look-ahead (an expected value, a numeric or symbolic value of the look-ahead state) whose result can be chunked tests structure that the evaluated operator creates or changes, not only structure the operator leaves as it was. Testing the whole relevant situation (for example where every block is) does this.

*Rationale:* Structure the operator leaves unchanged is copied from the state where the tie arose, so a chunk built only on it tests nothing about the operator and gives the same value to every tied operator; that the operator did not change the structure is not in the chunk.

*If violated:* Over-general chunks give unevaluated operators a value, the tie dissolves before they are evaluated, and the agent picks poor moves (blocks-world-look-ahead-state-eval world version: 25, 21 and 109 moves instead of 3, until 21 Nov 2026).

*Example:* Blocks world: 'C is not on the table, value 0' is true after B -> C only because C was already on A; the chunk fired for C -> table too. With tests of where A, B and C are, the moved block's new ^on is in the chunk.

*See:* parent L3-100

*Source:* blocks-world-look-ahead-state-eval (world-lean), 21 Nov 2026; Soar – To-do row 4

### Learning: RL

**L3-081** (Requirement, May, convention, formerly RL-015) — For table-based RL write one RL rule per state-operator pair; more generally RL rules act as binary features of a linear Q-function approximation (e.g. tile coding), with the update divided equally among contributing rules.

*Rationale:* Rules matching an operator jointly define its Q-value.

*See:* parent L0-100

*Source:* Manual §5.1, p.132-133; §5.3, p.135

**L3-082** (Requirement, May, fact, formerly RL-018) — RL rules can also be learned by chunking when the state is relational and cannot be enumerated; a chunk is an RL rule when it has RL rule form.

*Rationale:* RL rules are ordinary productions.

*See:* parent L0-100

*Source:* Manual §5.4.3, p.141

**L3-083** (Requirement, Should, convention, formerly RL-019) — When converting an agent to RL, take the indifferent preference out of the proposal rules, leaving only the acceptable preference, and supply values through separate RL rules.

*Rationale:* Keeps proposal (legality) separate from learned value.

*If violated:* Static indifference competes with learned values

*Example:*

```
(<s> ^operator <o> +)
```

*See:* parent L0-100

*Source:* Tutorial Part 6, 2.1 RL Rules

**L3-084** (Requirement, May, convention, formerly RL-020) — Generate RL rules for an enumerable state-action space with gp (or scripting) rather than by hand or with rule templates; use rule templates only when rules cannot be enumerated in advance, since template-instance checking can become expensive in long runs.

*Rationale:* Full state-action coverage can require many rules.

*If violated:* Incomplete or error-prone hand enumeration

*Exceptions:* Small spaces can be enumerated by hand.

*Example:* gp {rl*water-jug*empty ... (<op> ^name empty ^empty-jug.volume [3 5]) ... --> (<s> ^operator <op> = 0)}

*See:* parent L3-081

*Source:* Tutorial Part 6, 2.1 RL Rules; Manual §5.4.1, p.139; Manual §5.4.2, p.141

**L3-085** (Requirement, Should, convention, shared with World-Conventions, formerly RL-021) — Numeric-indifferent preferences from non-RL rules (rules outside the L0-100 format, such as a proposal that also creates = 0.5, or a rule with a computed value) should not be mixed with RL rules for the same operators unless that is intended: all numeric-indifferent values for an operator are combined, and only RL rules are updated.

*Rationale:* Fixed values bias or mask learned ones.

*If violated:* Learning appears not to work

*Exceptions:* Deliberate prior knowledge

*Source:* Consolidation review (gap); Manual §5.1

**L3-086** (Requirement, Must, convention, shared with World-Conventions, formerly SET-002) — With RL, numeric-indifferent-mode should be left at sum (the default): an operator's Q-value is then the sum of the numeric-indifferent values of all RL rules that match it. Soar does not enforce this.

*Rationale:* RL updates assume the summed value.

*If violated:* Incorrect Q-values and updates.

*Example:* decide numeric-indifferent-mode --sum

*See:* parent L0-036

*Source:* Manual §5.1, p.133 (fn. 2); §2.4.1, p.21

**L3-087** (Requirement, Should, convention, formerly SET-009) — With GQ(lambda) learning policies, set the rl step-size-parameter small (e.g. 0.01).

*Rationale:* Secondary weights must change slowly to converge.

*If violated:* Poor convergence.

*Example:* rl --set step-size-parameter 0.01

*See:* parent L3-088

*Source:* Manual §5.3.4, p.139

**L3-088** (Requirement, Should, convention, formerly SET-017) — Enable RL with rl --set learning on and choose an exploration policy (e.g. indifferent-selection --epsilon-greedy), for instance in the project's load file.

*Rationale:* RL is off by default.

*If violated:* No learning

*Example:*

```
rl --set learning on
indifferent-selection --epsilon-greedy
```

*Source:* Tutorial Part 6, 1.2 Running the Left-Right Agent; Tutorial Part 6, 3. Further Exploration

**L3-101** (Choice, May, convention, shared with World-Conventions) — Use reinforcement learning only for tasks run over repeated episodes, where values learned in one episode help the next.

*Rationale:* RL learns across episodes; within a single problem it only adds rules and updates.

*If violated:* Extra cost with no benefit.

*Source:* Generalized from World-Conventions L11-007 (20 Nov 2026)

### Input/output link

**L3-089** (Requirement, Must, convention, shared with World-Conventions, formerly IO-009) — Copy environment reward from the input-link to the reward-link with rules; the reward-link is not part of io and is not written by the environment.

*Rationale:* The environment writes only to the input-link.

*If violated:* No reward reaches RL.

*Example:*

```
(state <s> ^io.input-link.reward <v> ^reward-link <rl>) --> (<rl> ^reward.value <v>)
```

*See:* parent L0-101

*Source:* Manual §5.2, p.134

**L3-090** (Requirement, Should, convention, shared with World-Conventions, formerly IO-012) — Output commands are created by operator application rules, so that each command is an o-supported, deliberate action. Output functions run at the end of a cycle only if structure under the output-link changed.

*Rationale:* Actions are deliberate commitments made by operators.

*If violated:* Commands issued without deliberation, or retracted early

*Example:*

```
sp {apply*move-north (state <s> ^operator.name move-north ^io.output-link <out>) --> (<out> ^move.direction north)}
```

*See:* parent L1-022

*Source:* Tutorial Part 2, 2.2.2 Soar Version; Tutorial Part 2, 2.3.2 Operator Application: Persistence; Manual §3.5.1, p.87; §3.5.2, p.88-89; §3.5.3, p.90

**L3-091** (Requirement, Should, convention, shared with World-Conventions, formerly IO-016) — One generic application rule copies the selected operator's command to the output-link and another removes each command, by rejecting its link on the output-link, after the environment marks it ^status complete, so that an operator with an external action needs only a proposal rule.

*Rationale:* Removes duplicated per-operator output rules.

*If violated:* Many duplicated output rules

*Exceptions:* Generic rules impose conventions (e.g. ^status complete is always removed and cannot be tested by other rules).

*Example:*

```
sp {io*elaborate*operator*remove-command (state <s> ^operator.actions ^io.output-link <out>) (<out> ^<att> <v>) (<v> ^status complete) --> (<out> ^<att> <v> -)}
```

*See:* parent L3-028

*Source:* Tutorial Part 2, 2.8.3 Simplified Operators; Tutorial Part 3, 3.4 General Rule Summary

**L3-092** (Requirement, Must, convention, formerly IO-019) — Interpreted input lands on the task state: elaborations that test ^io.input-link copy what the task needs onto the state (constants as they are, objects with fresh identifiers, L1-021). All other task rules test the state, never the input-link.

*Rationale:* One place holds the mapping; look-ahead and chunking see state structure, not the environment's.

*If violated:* Task rules tied to the environment's names; input aliasing; the task cannot be simulated in look-ahead.

*Example:*

```
(state <s> ^name io-guess ^io.input-link.turn <t>) --> (<s> ^turn <t>)
```

*See:* parent L0-112

*Source:* Soar-Lean-Agents issue 5; Tasks/Reference/io-guess (15 Nov 2026)

**L3-093** (Requirement, Must, convention, formerly IO-022) — An agent in an environment halts on the environment's input-link signal that the task instance has ended (for example ^game-over true), by an operator application; the agent's own goal is not the end of the task instance unless the environment says so.

*Rationale:* The environment owns the task instance. In the task language Goal is terminal, so a goal reached before the environment's signal stops the agent too early.

*If violated:* The agent halts while the environment is mid-task-instance, or runs on after it ended.

*Example:*

```
(state <s> ^operator <o>) (<o> ^name stop) --> (halt)   with stop proposed on ^game-over true
```

*See:* parent L6P-013

*Source:* Soar-Lean-Agents issue 5; Tasks/Reference/io-guess (15 Nov 2026)

### Settings/commands

**L3-094** (Requirement, Should, convention, shared with World-Conventions, formerly SET-008) — With RL, the exploration policy is set explicitly (indifferent-selection: epsilon-greedy or boltzmann) and not left at the default softmax.

*Rationale:* Those policies are designed for RL; softmax is default only for backward compatibility.

*If violated:* Unsuitable exploration.

*Example:* decide indifferent-selection --epsilon-greedy

*See:* parent L3-088

*Source:* Manual §5.3.3.1, p.138-139

**L3-095** (Requirement, May, convention, shared with World-Conventions, formerly SET-011) — An attribute that usually has many values at once is declared with production optimize-attribute before the productions are loaded, to help condition ordering.

*Rationale:* Gives the reorderer hints about multi-attributes; has no effect if issued after rules are loaded.

*If violated:* Slower matching in problematic cases.

*Example:* production optimize-attribute thing 20

*Source:* Manual §9.2.3.8, p.213

**L3-096** (Requirement, Should, convention, shared with World-Conventions, formerly SET-012) — A max-elaborations warning is treated as a sign of a fire-and-retract loop. The limit is raised only for a program that really needs that many elaboration cycles.

*Rationale:* When the limit is hit, Soar moves to the next phase without quiescence.

*If violated:* Decisions made before quiescence.

*Exceptions:* Programs designed for many elaboration cycles.

*Example:* soar max-elaborations 200

*See:* parent L1-008

*Source:* Manual §9.1.1 soar max-elaborations, p.188

**L3-097** (Requirement, May, convention, shared with World-Conventions, formerly SET-013) — Substate depth is bounded with soar max-goal-depth. Unbounded depth usually comes from a defect that repeats state no-change impasses.

*Rationale:* Prevents infinite recursive subgoaling.

*If violated:* Runaway goal stack.

*Example:* soar max-goal-depth 100

*See:* parent L0-051

*Source:* Manual §9.1.1 soar max-goal-depth, p.188

**L3-098** (Requirement, Should, convention, formerly SET-018) — Debug with trace and inspection commands: run a full trace (watch 5) viewed collapsed, and use matches, preferences --names/--wmes, print --depth and print-stack to find why rules did or did not fire.

*Rationale:* These commands show what is about to fire, what created a preference, and why a condition failed.

*If violated:* Slow, guess-based debugging

*Example:*

```
matches propose*move-to-food
preferences I3 move --names
```

*Source:* Tutorial Part 1, 1.3.1 Hello World Operator: English Version; Tutorial Part 2, 2.5.3 Runtime Debugging Commands; Tutorial Part 3, 3.2 Impasses and State Creation

## L3S Guidance (Soar only)

L3 guidance for Soar programs in general that World-Conventions-v6 does not include, because a more specific world convention replaces it. The World-Conventions column gives the reason.

### State representation

**L3S-001** (Requirement, Should, convention, formerly STA-030) — A relation that operators change is represented explicitly on the state, as an object (or attribute) that points to its arguments' identifiers, not as a numeric code for an argument or a fixed link. World-Conventions gives one way to do this: a relation object on the world with ^argument1 ... (L7-016).

*Rationale:* Learning generalizes over identifiers: rules learned over pointers apply to other objects in the same relation, while numeric codes tie them to particular values.

*If violated:* An operator-changed relation stored as an integer code (e.g. a tile's cell number) or as a static link.

*Example:* Eight puzzle: ^binding objects (^cell <c> ^tile <t>) on the state; move-tile changes a binding's ^tile. Not tile ^cell 23.

*Source:* Eight puzzle review (agentgen, 7 Nov 2026)

### Goal/desired representation

**L3S-002** (Choice, May, convention, formerly GOL-011) — Goals may be represented explicitly as state substructure tested by general goal-recognition rules, or implicitly in goal-specific rules that test for completion; explicit representation is preferred where feasible.

*Rationale:* Explicit goals can focus problem solving and be compared generally.

*If violated:* Goal knowledge buried in task-specific rules.

*Exceptions:* Goals that are hard to represent explicitly.

*Source:* Manual §2.1.4, p.8-9

**L3S-003** (Requirement, Should, convention, formerly GOL-013) — Give the desired structure the same attributes as the state objects it describes, so the goal test can share variables between ^desired and the state.

*Rationale:* A general goal-test rule can then compare the desired and current structures directly.

*If violated:* Goal test needs special-case rules

*Example:*

```
(<dj> ^volume <v> ^contents <c>) (<j> ^volume <v> ^contents <c>)
```

*See:* parent L3-024

*Source:* Tutorial Part 1, 1.4.10 Desired State Recognition; Tutorial Part 4, 7. Desired State Recognition

### Rule: operator proposal

**L3S-004** (Requirement, Should, convention, formerly PRO-011) — Create the initial task state with an operator initialize-<task>, proposed when (state <s> ^superstate nil -^name), whose application creates ^name and the initial task structure, rather than with an unconditional rule.

*Rationale:* Initial structure is then o-supported and the start is explicit.

*If violated:* Initial structure i-supported (cannot be changed by operators)

*Exceptions:* Environment-driven agents may begin from input-link data instead.

*Example:*

```
(state <s> ^superstate nil -^name) --> (<s> ^operator <o> +) (<o> ^name initialize-water-jug)
```

*See:* parent L2-005

*Source:* Tutorial Part 1; default initialize-selection; Tutorial Part 1, 1.4.3 Initial State Creation: The initialize-water-jug Operator; Tutorial Part 4, 3. Initial State Creation: Initialize-mac; Tutorial Part 6, 1.1 The Left-Right Agent

## L4 Default rules

Provided or assumed by Soar's general default rules (e.g. an operator no-change substate gets ^name of the operator; ^top-state).

### Rule syntax/naming

**L4-001** (Requirement, Should, convention, shared with World-Conventions, formerly SYN-027) — Library (default) rules carry the :default flag; task rules do not.

*Rationale:* Distinguishes library from task knowledge (chunking treats :default rules specially, and traces can hide library rules).

*Example:*

```
sp {selection*... :default ...}
```

*Source:* Default rules (all files); Tutorial Part 5, 1.2 Selection Initial State Creation

**L4-002** (Requirement, Must, convention, shared with World-Conventions, formerly SYN-028) — Task rules do not reuse the names the default rules rely on: the operator name wait, the state attribute ^top-state, and the assignment of a substate's ^name from the superoperator.

*Rationale:* Collisions change default behaviour.

*If violated:* Default rules misfire

*Source:* Consolidation review (gap); default simple.soar, elaborations/_all.soar

### State representation

**L4-003** (Requirement, Should, convention, shared with World-Conventions, formerly STA-007) — Every state has ^top-state, which points to the top state. Rules reach top-level structure through ^top-state, not through a chain of ^superstate. In a look-ahead state ^top-state is the look-ahead state itself (L7-009).

*Rationale:* Uniform access from any depth.

*If violated:* Long ^superstate chains

*Exceptions:* In look-ahead (evaluate-operator) substates the selection version does not propagate ^top-state, so look-ahead copies do not see the real top state

*Example:*

```
(state <s> ^top-state <ts>)
```

*Source:* Default: elaborations/top-state.soar; selection/elaborations/top-state.soar

### Rule: operator evaluation/selection

**L4-004** (Library definition, May, fact, shared with World-Conventions, formerly EVA-011) — With the default rules (simple.soar), an operator whose tie substate reaches a state no-change with nothing proposed gets indifferent and worst preferences; one whose conflict substate does gets rejected.

*Rationale:* Breaks ties and conflicts the agent has no knowledge for.

*See:* parent L0-049

*Source:* Default: simple.soar default*select*indifferent-and-worst*tied, default*select*reject*conflict (world library: soar-base*compare*default*select*indifferent-and-worst*tied, selection-world*compare*default*select*reject*conflict)

**L4-005** (Choice, Should, convention, formerly EVA-012) — ^last-operator is not always maintained; this applies if an agent uses it. It is used most often to avoid undoing the last operator in look-ahead (L3-047, L3-048). When it is used, it is maintained by one application rule that, whenever an operator is applied, adds the new record and removes the previous one (L2-010), and is initialized (for example by the init-<task-name> operator) with an empty ^last-operator so that rules testing it match from the first decision.

*Rationale:* Without removal the state accumulates several records and comparisons match stale ones; without initialization rules that test it cannot match on the first decision.

*If violated:* Several ^last-operator values at once; rules that test it do not fire at the start

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Rule: impasse/substate handling

**L4-006** (Library definition, May, convention, shared with World-Conventions, formerly IMP-011) — A wait operator is proposed with a worst preference in a state no-change substate (^attribute state ^choices none) when no wait is already selected, so that an idle agent waits in one substate and does not stack impasses. soar-base and agent-world (L9-025) each provide one. soar-base's proposal is not made in a state no-change directly below an evaluate-operator state (-^superstate.name evaluate-operator); agent-world's has no such exception yet (planned, L9-025).

*Rationale:* Prevents runaway substate creation.

*Example:*

```
sp {top-state*propose*wait (state <s> ^attribute state ^choices none -^operator.name wait) --> (<s> ^operator <o> +) (<o> ^name wait)}
```

*See:* parent L0-051

*Source:* Default: simple.soar top-ps*propose*wait; Tutorial Part 3, 4.9 Wait Operator

**L4-007** (Library definition, May, fact, shared with World-Conventions, formerly IMP-012) — With the default rules (simple.soar), a constraint failure directly under the top state halts the agent.

*Rationale:* An unresolvable conflict at the top is fatal.

*See:* parent L1-015

*Source:* Default: simple.soar default*top-goal*halt*operator*failure (world library: soar-base*apply*default*top-goal*halt*operator*failure)

### Substate representation

**L4-008** (Library definition, Should, fact, shared with World-Conventions, formerly SUB-005) — A substate created by an operator no-change impasse gets ^name equal to the ^name of the superstate's selected operator.

*Rationale:* Lets the operator's implementation be written as rules testing (state <s> ^name <operator-name>).

*If violated:* Rules for the operator's implementation never match

*Exceptions:* Selection space: ^name selection; evaluate-operator copies the superstate name

*Example:*

```
(state <s> ^superstate.operator.name <n>) --> (<s> ^name <n>)
```

*See:* parent L2-005

*Source:* Default: elaborations/_all.soar elaborate*state*name; Tutorial Part 3, 3.3 Wander Operator Suboperators; Tutorial Part 3, 3.4 General Rule Summary

### Input/output link

**L4-009** (Library definition, May, convention, shared with World-Conventions, formerly IO-011) — A substate that issues input or output needs ^io. soar-base copies the superstate's ^io into no-change substates; agent-world copies it into every substate except selection states and states under evaluate-operator (L15-007).

*Rationale:* Operator implementations in substates can act directly.

*Exceptions:* Not loaded unless simple.soar is sourced

*Example:*

```
sp {elaborate*state*io (state <s> ^superstate.io <io>) --> (<s> ^io <io>)}
```

*See:* parent L0-110

*Source:* Default: simple.soar default*elaborate*state*io; Tutorial Part 3, 3.3 Wander Operator Suboperators; Tutorial Part 3, 3.4 General Rule Summary

## L5 Selection space (classic)

Conventions of the default selection / look-ahead library (^desired, ^success, ^problem-space copy controls, evaluation values).

### Project/file organization

**L5-001** (Requirement, Must, convention, formerly ORG-003) — Load the default selection rules (default/selection.soar) together with the task rules when using look-ahead.

*Rationale:* They provide the domain-independent evaluate-operator, state-copy and preference-conversion rules.

*If violated:* Tie impasses are not processed

*Example:*

```
pushd ../default
source selection.soar
popd
```

*Source:* Tutorial Part 5, 1. The Water Jug Problem; Tutorial Part 5, 2.1.1 Add selection rules

### Rule syntax/naming

**L5-002** (Reserved, Must, convention, formerly SYN-029) — Task rules do not use the selection library's reserved names and attributes: operator names evaluate-operator; state names selection; attributes evaluation, superoperator, look-ahead-operator, tried-tied-operator, duplicate-of, duplicates, desired (except as the goal), success/failure values.

*Rationale:* Collisions change library behaviour.

*If violated:* Library misfires

*Source:* Default selection (all files)

### State representation

**L5-003** (Requirement, Should, convention, formerly STA-008) — A task that uses look-ahead declares a ^problem-space on its state with ^name and copy controls: ^default-state-copy yes|no, ^default-operator-copy yes|no, ^one-level-attributes, ^two-level-attributes, ^all-attributes-at-level one|two, ^dont-copy, ^dont-copy-anything.

*Rationale:* Controls how evaluate-operator copies the state; without it everything is copied one level deep.

*If violated:* Copies share mutable objects with the real state; look-ahead corrupts the task state

*Example:*

```
(<p> ^name water-jug ^default-state-copy yes ^two-level-attributes jug ^dont-copy free)
```

*Source:* Default selection: evaluate-operator*elaborate*state*… copy rules; Tutorial Part 5, 1.4 Selection Operator Application; Tutorial Part 5, 1.4.1 Creating the Initial State; Tutorial Part 5, 2.1.2 Add problem space and state copying information

**L5-004** (Library definition, Should, convention, shared with World-Conventions, formerly STA-009) — A derived (i-supported) attribute is excluded from state copying, so that the copy derives it again and does not hold a stale value. Nothing in working memory identifies an attribute as i-supported to the rules, so the copy rules cannot find derived attributes themselves: the task must list them. Under the world conventions the exclusion list is ^dont-copy-object-attribute on the problem space (L14-026). A derived i-supported structure is avoided when testing for its absence would require local negated tests in the substate (L3-031, L3-035, L3-062).

*Rationale:* Copied derived values would be o-supported-like stale facts in the copy.

*If violated:* Stale derived values in look-ahead

*Example:*

```
(<p> ^dont-copy free)
```

*See:* parent L5-003

*Source:* Water Jug originals; default selection copy rules

**L5-005** (Requirement, Should, convention, formerly STA-010) — List exactly the state attributes to be copied for evaluation (^one-level-attributes / ^two-level-attributes) rather than using all-attributes-at-level two.

*Rationale:* Copying only what is needed keeps evaluation states small and explicit.

*If violated:* Unnecessary copying

*Exceptions:* Default without directives is all-attributes-at-level one.

*Example:* ^two-level-attributes right-bank left-bank

*See:* parent L5-003

*Source:* Tutorial Part 5, 1.4.1 Creating the Initial State

**L5-006** (Requirement, Must, convention, formerly STA-011) — Declare as ^two-level-attributes every state attribute whose objects (e.g. jugs, blocks) are modified by operator application, so look-ahead copies the objects; one-level copying shares the objects with the original state.

*Rationale:* With shared objects, applying the operator in the evaluation state also modifies the real state.

*If violated:* Look-ahead corrupts the actual task state

*Exceptions:* Not needed if application replaces whole objects instead of modifying them.

*See:* parent L5-003

*Source:* Tutorial Part 5, 1.4.1 Creating the Initial State; Tutorial Part 5, 2.1.2 Add problem space and state copying information; Default selection: evaluate-operator*elaborate*state*add-duplicate-to-state

### Goal/desired representation

**L5-007** (Requirement, Must, convention, formerly GOL-001) — A task that uses the selection space represents its goal as ^desired <d> on the task state; evaluations are tied to that desired (^evaluation.desired <d>) and success/failure are reported against it.

*Rationale:* Every selection compare/select rule joins on the superstate's ^desired.

*If violated:* Evaluations never turn into preferences

*Example:*

```
(<s> ^desired <d>) (<d> ^jug <dj>)
```

*See:* parent L3-024

*Source:* Default selection: selection*elaborate*evaluation*desired and all compare rules

**L5-008** (Requirement, Must, convention, shared with World-Conventions, formerly GOL-002) — A state signals achievement of its goal with an elaboration (<s> ^success <ds>), or ^required-success or ^partial-success, where <ds> is the state's ^desireds. It signals failure with ^failure, ^partial-failure or ^prohibit-failure <ds>. In look-ahead these replace halting. L14-027 lists every evaluation value.

*Rationale:* The library turns these state attributes into evaluations and preferences.

*If violated:* Look-ahead never sees success

*Example:*

```
(state <s> ^desired <d> ...) --> (<s> ^success <d>)
```

*See:* parent L5-007

*Source:* Default selection: evaluate-operator*elaborate*symbolic-evaluation*from-subgoal; Tutorial Part 5, 1.4.4 Evaluating the result; Tutorial Part 5, 2.1.3 Modify goal detection; Tutorial Part 5, 2.1.4 Modify failure detection

**L5-009** (Library definition, Should, fact, formerly GOL-003) — At the top state, ^success (or required-success) on the ^desired halts the agent; ^failure or ^prohibit-failure halts with failure (top-goal*halt*success/failure).

*Rationale:* The same success rule serves look-ahead (evaluation) and the real task (halt).

*If violated:* Agent continues after reaching the goal (seen in water-jug-look-ahead-RL)

*See:* parent L5-008

*Source:* Default selection: elaborations/top-state.soar

**L5-010** (Requirement, Should, convention, formerly GOL-004) — A task using numeric evaluations creates ^numeric-value on the evaluated state and declares on its desired whether higher or lower values are better (^desired.better higher|lower); ^equal not-indifferent turns off indifference between equal values.

*Rationale:* Compare rules need it to order operators.

*If violated:* Numeric evaluations never ordered

*Example:*

```
(<d> ^better higher)
```

*See:* parent L5-016

*Source:* Default selection: selection*compare*higher-evaluation-better, prefer-lower-evaluation; Tutorial Part 5, 2.3 Numeric Evaluations

**L5-011** (Choice, Should, convention, formerly GOL-005) — In look-ahead, evaluate a state as failure if it duplicates a state higher in the state stack, using an elaborated ^superstate-set (each state's superstate plus that superstate's superstate-set).

*Rationale:* Avoids loops and, as a side effect, undoing the last operator.

*If violated:* Deep recursive search revisiting the same states

*Example:*

```
sp {...elaborate*superstate-set (state <s> ^superstate <ss>) --> (<s> ^superstate-set <ss>)}
```

*See:* parent L5-008

*Source:* Tutorial Part 5, 1.4.4 Evaluating the result; Tutorial Part 5, 2.1.5 Add duplicate state detection rule

### Operator WM representation

**L5-012** (Requirement, Should, convention, formerly OPR-007) — Operators evaluated by look-ahead must be copyable: all their parameters are attributes of the operator object, and the selection rules copy the evaluated operator (replacing copied state identifiers) unless the problem space sets ^default-operator-copy no.

*Rationale:* The look-ahead applies a copy of the operator to the copied state.

*If violated:* Copied operator refers to real-state objects

*Example:*

```
(<p> ^default-operator-copy no)
```

*See:* parent L2-007

*Source:* Default selection: evaluate-operator*elaborate*operator*add-*-to-duplicate-operator; Tutorial Part 5, 1.4.2 Selecting the operator being evaluated

### Rule: state elaboration

**L5-013** (Requirement, Should, convention, shared with World-Conventions, formerly ELB-005) — Rules that evaluate a look-ahead state (success, failure, duplicate tests) test ^tried-tied-operator, so that they apply only after the evaluated operator has been applied in the evaluation state. For an operator applied by a sequence of rule firings, ^tried-tied-operator alone does not show that the application is complete; this is not a problem if a separate rule tests that the operator's preconditions are satisfied (^pre-conditions-satisfied, L9-007).

*Rationale:* Before that, the copy equals its parent and would be judged a duplicate.

*If violated:* Every look-ahead fails immediately

*Exceptions:* Does not work for operators applied by a sequence of rules.

*Example:*

```
(state <s> ^tried-tied-operator <o> ...)
```

*See:* parent L5-008

*Source:* Default selection: evaluate-operator*elaborate*state*tried-tied-operator; Water Jug originals; Tutorial Part 5, 1.4.4 Evaluating the result; Tutorial Part 5, 2.3 Numeric Evaluations

### Rule: operator proposal

**L5-014** (Requirement, Must, convention, shared with World-Conventions, formerly PRO-005) — To have look-ahead decide among task operators, their proposals create only the acceptable preference: no indifferent or other preference that settles the choice. The operators then tie, and the tie impasse creates the selection substate.

*Rationale:* The selection space is entered only through a tie impasse.

*If violated:* Random selection; planning never invoked

*Example:*

```
(<s> ^operator <o> +)
```

*See:* parent L3-039

*Source:* Tutorial Part 5, 1. The Water Jug Problem; Tutorial Part 5, 2.1 Conversion to Planning and Learning

**L5-015** (Library definition, Must, fact, shared with World-Conventions, formerly PRO-006) — In a selection state, evaluate-operator is proposed for each tied ^item that has no evaluation with ^value true, with ^super-operator <item>. It stays selected until its evaluation has a value.

*Rationale:* Exactly one evaluation is made per tied operator, and its order rarely matters.

*If violated:* Repeated or missing evaluations

*Exceptions:* Search control may order evaluations when task knowledge allows.

*Example:*

```
(state <s> ^name selection ^item <i>) -{(<s> ^evaluation <e>) (<e> ^super-operator <i> ^value true)}
```

*See:* parent L5-020

*Source:* Tutorial Part 5, 1.3 Selection Operator Proposal

### Rule: operator evaluation/selection

**L5-016** (Requirement, Must, convention, formerly EVA-013) — Use only the standard symbolic evaluations required-success, success, partial-success, indifferent, partial-failure, failure, prohibit-failure (lose = failure); the selection rules map them to !, >, >, =, <, -, ~ respectively (success is also better than partial-success). Numeric evaluations (^numeric-value) are compared using ^desired.better higher|lower.

*Rationale:* Fixed vocabulary of the library.

*If violated:* Evaluation ignored

*Example:*

```
(<s> ^success <d>)
```

*See:* parent L5-020

*Source:* Default selection: selection*select*… and selection*compare*…; Tutorial Part 5, 1.4.4 Evaluating the result

### Rule: operator application

**L5-017** (Requirement, Should, convention, shared with World-Conventions, formerly APP-011) — An operator whose real effect comes from an external environment also has an internal application rule that applies it in the evaluation state, so that look-ahead can predict its effect (L10-007).

*Rationale:* In the look-ahead copy, nothing from the world changes the state.

*If violated:* Look-ahead state never changes; operator no-change

*See:* parent L2-011

*Source:* Tutorial Part 5, 1.4.3 Applying the selected operator

### Rule: impasse/substate handling

**L5-018** (Library definition, Should, convention, shared with World-Conventions, formerly IMP-014) — In look-ahead, an evaluation state in which no operator can be selected, or in which a constraint-failure impasse arises, counts as a failure of the evaluated operator (L14-037, L14-039). Tasks do not add their own handlers for these cases.

*Rationale:* The library already turns them into failure evaluations.

*If violated:* Double handling

*See:* parent L5-008

*Source:* Default selection: evaluate-operator*elaborate*evaluation*failure*no-operators, *constraint-failure

### Substate representation

**L5-019** (Library definition, Must, fact, shared with World-Conventions, formerly SUB-006) — A tie or conflict substate (^choices multiple) is named selection by a default rule. Its ^item values are the candidate operators. Selection-space rules test ^name selection, not the impasse type.

*Rationale:* All selection rules test ^name selection.

*Example:*

```
(state <s> ^name selection ^item <i>)
```

*See:* parent L2-005

*Source:* Default selection: selection*elaborate*name*selection; Tutorial Part 5, 1.2 Selection Initial State Creation

**L5-020** (Library definition, Must, convention, formerly SUB-007) — In the selection space, record evaluations as ^evaluation objects on the selection state, each with ^operator (the tied operator) and, once known, ^symbolic-value or ^numeric-value, ^value true and ^desired.

*Rationale:* Evaluations must name the operator they refer to, and placing them on the state means they are removed when the impasse is resolved.

*If violated:* Evaluations not processed into preferences

*Example:*

```
(<e> ^operator <i> ^symbolic-value success ^value true ^desired <d>)
```

*See:* parent L5-019

*Source:* Tutorial Part 5, 1.1 Selection State Representation

### Learning: chunking

**L5-021** (Choice, Should, convention, shared with World-Conventions, formerly SET-016) — When look-ahead results are to be learned, chunking is enabled explicitly: chunk always, chunk only with force-learn on the selection states, or chunk all-except with dont-learn on the states that must not learn.

*Rationale:* Without chunking each result is used only locally and forgotten.

*If violated:* Excessive decisions; repeated search

*Example:*

```
chunk always
# or: chunk only, with force-learn on the selection states
# or: chunk all-except, with dont-learn on the other states
```

*See:* parent L0-113

*Source:* Tutorial Part 5, 1.4.5 Chunking

## L6P Project (constrained)

This project's stricter conventions for generated agents (plan of 5 Nov 2026; Water Jug DSL v0).

### Project/file organization

**L6P-001** (Requirement, Must, convention, formerly ORG-005) — Rules outside these conventions live only in designated escape-hatch files, each with a stated reason, which the generator never overwrites and the checker does not verify.

*Rationale:* Guarantees are scoped explicitly rather than quietly broken.

*Source:* Plan: escape hatch

### State representation

**L6P-002** (Requirement, Must, convention, formerly STA-012) — All state and object attributes are declared in a schema (type, single- or multi-valued, derived or not); rules test and create only declared attributes.

*Rationale:* Removes attribute-path errors; makes the datamap complete; enables Lean type checking.

*If violated:* Undeclared attribute

*Exceptions:* Escape-hatch rules

*Source:* Plan (5 Nov 2026): declared state schema

**L6P-003** (Requirement, Should, convention, formerly STA-013) — Object types compared across states (e.g. for duplicate detection) declare a key attribute whose values are unique and never changed by operators.

*Rationale:* Duplicate detection and chunking rely on it.

*See:* parent L6P-002

*Source:* Water Jug DSL v0 check

### Goal/desired representation

**L6P-004** (Requirement, Must, convention, formerly GOL-006) — Every task declares its goal as a ^desired structure plus one success rule, and the agent halts when the goal holds at the top state, whatever the selection method.

*Rationale:* Uniform goal handling across variants; reachability can be checked.

*If violated:* Agent never halts

*See:* parent L3-024

*Source:* Plan: explicit goals

### Rule: state elaboration

**L6P-005** (Requirement, Must, convention, formerly ELB-006) — Derived attributes are computed only by elaborations, only from non-derived attributes (stratified), and never set by operator application.

*Rationale:* Unique fixed point; no support conflicts.

*See:* parent L6P-002

*Source:* Plan: stratified elaborations; Water Jug DSL v0

**L6P-006** (Requirement, Must, convention, formerly ELB-007) — Failure states are declared once: one elaboration tests features of the task state and marks the state (^failure <desired>); every method (random, look-ahead, RL) uses that mark.

*Rationale:* Methods cannot disagree about what a failure is.

*If violated:* Inconsistent failure handling across methods

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

**L6P-007** (Requirement, Must, convention, formerly ELB-008) — A failure state violates a task constraint. Moves into it are still proposed (the constraint is not built into the proposals); entering a failure state at the top state is a task failure and halts. In a look-ahead substate it is a failure evaluation; with RL it is a terminal (negative) reward.

*Rationale:* Building the constraint into the proposals gives the agent too much knowledge; treating the state as recoverable (undo) misstates the task.

*If violated:* Proposals that exclude failure states; recovery (undo) after a failure state at the top

*Exceptions:* Not an undo: abandoning a path in a forward search (e.g. the knight's tour's backup returns to an earlier choice point and tries another move; there is no operator that reverses a move) is allowed (JL, 7 Nov 2026).

*See:* parent L6P-006

*Source:* Missionaries & Cannibals family (agentgen, 6 Nov 2026)

### Rule: operator proposal

**L6P-008** (Requirement, Must, convention, formerly PRO-008) — Each operator is given by one template: name, typed parameters, proposal conditions, preference policy, and application cases (guard + effects) that are exhaustive and disjoint.

*Rationale:* Uniform structure the generator and checker understand.

*Exceptions:* Escape-hatch rules

*See:* parent L2-006

*Source:* Plan: one operator template; Water Jug DSL v0

**L6P-009** (Requirement, Should, convention, formerly PRO-009) — Each operator declares its proposal style (precondition, L3-038; goal, L3-041), and heuristic restrictions (L3-042) are marked separately from precondition or goal-relevance conditions, so a reviewer and the checker can tell them apart.

*Rationale:* Lets checks such as reachability use the right conditions, and makes the heuristics reviewable.

*See:* parent L3-036

*Source:* Suggested 6 Nov 2026 (not yet decided)

### Rule: operator evaluation/selection

**L6P-010** (Requirement, Must, convention, formerly EVA-014) — A heuristic tie evaluation is total and single-valued: exactly one value for every (context, candidate) pair.

*Rationale:* Otherwise evaluate-operator stalls or conflicts.

*If violated:* Operator no-change on evaluate-operator

*Source:* Water Jug DSL v0 check

### Substate representation

**L6P-011** (Requirement, Should, convention, formerly SUB-008) — In nested operator no-change substates, every substate below the first gets ^task-state (the state whose operator began the hierarchy, copied down from its parent). Sub-operators read the task through ^task-state; a nested sub-operator's results are changes to its parent substate's own attributes (^superstate); only first-level sub-operators change the task state.

*Rationale:* Each level works on its parent's local data, so its results are local to the parent and are removed with it; ^task-state makes the task objects (facts, problem) reachable at any depth without a ^top-state chain, and stays right when the hierarchy starts below the top state (look-ahead, operator subgoaling).

*If violated:* A nested sub-operator changing the task state directly, or reaching task objects through ^superstate chains.

*Example:* process-column > get-digit2 > increment-digit2 (arithmetic): increment-digit2 reads an inc-fact through ^task-state and changes process-column's ^d2 and ^adj.

*Source:* Arithmetic family (agentgen, 7 Nov 2026)

### Learning: chunking

**L6P-012** (Requirement, Should, convention, formerly CHK-013) — When a substate test compares the current state with an ancestor state (e.g. duplicate detection), write it with positive conditions over a known number of objects, not with nested negations over the ancestor.

*Rationale:* Water Jug pilot (6 Nov 2026): a nested-negation duplicate test made chunking learn "every operator is a partial failure".

*If violated:* Over-general chunks; look-ahead degenerates to random choice

*See:* parent L3-062

*Source:* Project finding (Water Jug pilot)

### Input/output link

**L6P-013** (Requirement, Must, convention, formerly IO-013) — Output commands follow one protocol: create the command on ^output-link, wait for ^status, remove the command; input-link structure is declared in the schema and read-only.

*Rationale:* Uniform interaction with environments.

*See:* parent L1-020

*Source:* Plan: fixed I/O protocol

**L6P-014** (Requirement, Must, convention, formerly IO-014) — In a generated agent, hand-written I/O rules are ordinary task rules, kept in files named for their role (input.soar, output.soar), not in _escape-* files. Escape files are for deviations from the conventions (L6P-001, VS-FIL-006).

*Rationale:* I/O is first-class Soar; a reviewer skips escape files by the project's own convention.

*If violated:* I/O rules nobody reads; an agent that passes check and cannot play.

*See:* parent L6P-001

*Source:* Soar-Lean-Agents issue 5; Tasks/Reference/io-guess (15 Nov 2026)
