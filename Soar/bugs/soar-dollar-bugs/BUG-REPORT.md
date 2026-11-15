# Two defects in the `$` (constant-match) test: an unrecoverable error in negated conditions, and a crash in `{ … }` tests

**Soar version:** 9.6.50 (kernel), built 6 November 2026 (SoarSuite 9.6.6). Linux x86-64, embedded kernel through SML (Python).
**Source examined:** SoarGroup/Soar, commit 94a15d6 (30 October 2026). File and line numbers below refer to that commit, under `Core/SoarKernel/src/`.
**Found in:** generated agents that use the agent-world and selection-world libraries, where every object-handle test was written with `$` so that chunks keep handles as constants.

Both defects are independent of the learning setting: they occur with `chunk never` as well as `chunk always`.

---

## Bug 1: `$` inside a negated condition makes Soar report an unrecoverable error

### Reproduce

`bug1-negated-dollar.soar` (attached):

```
sp {result*ncc-dollar
   (state <ss> ^superstate <s>)
   (<s> ^target.handle $ <h>)
  -{(<s> ^objects.object <ob>)
    (<ob> ^handle $ <h>)}
-->
   (<s> ^target-is-new true)}
```

The rest of the file creates a tie impasse, so this rule fires in a substate and returns a result. Then run:

```
source bug1-negated-dollar.soar
chunk never        # same with chunk always
run 10
```

### Observed

```
     1:    O: O1 (initialize)
     2:    ==>S: S2 (operator tie)production.c: Error: bad test type in hash_test
Soar cannot recover from this error.
Data is still available for inspection, but may be corrupt.
You will have to restart Soar to run an agent.
Bug 1 rule fired
System halted.
```

The run continues after the message. In larger agents the message repeats every time a result is built from such a rule, about 30 to 110 times per run in Hanoi and water jug tasks. One blocks-world agent stopped making progress.

The same error occurs with `$` inside a single negated condition, `-(<ob> ^handle $ <h>)`.

### Expected

No error. A `$` test inside a negated condition should behave like the same test without `$` during matching. When a chunk is built, the variable should be literalized consistently with its positive occurrences.

### Cause

`$ <x>` is parsed (`parsing/parser.cpp`, `case DOLLAR_LEXEME`, line 420) into the conjunctive test `{ <x> $$ <x> }`, where `$$` is a `CONSTANT_MATCH_TEST`.

When EBC builds a justification or chunk, every negated condition (a negation or NCC) met during backtracing goes into the negated-conditions set through `make_chunk_cond_for_negated_condition` (`explanation_based_chunking/ebc_build.cpp`, line 302). That function calls `hash_condition`, which calls `hash_test` on each field.

`hash_test` (`soar_representation/test.cpp`, the switch around lines 547–592) handles `EQUALITY_TEST`, the goal and impasse tests, the disjunction and conjunctive tests, and the relational tests. It has no case for `CONSTANT_MATCH_TEST`. The `default:` branch calls `abort_with_fatal_error("production.c: Error: bad test type in hash_test")`.

Positive conditions never reach `hash_test`, which is why `$` in positive conditions works.

### Suggested fix

In `hash_test`, treat `CONSTANT_MATCH_TEST` like the other tests that carry a referent:

```cpp
        case NOT_EQUAL_TEST:
        case LESS_TEST:
        case GREATER_TEST:
        case LESS_OR_EQUAL_TEST:
        case GREATER_OR_EQUAL_TEST:
        case SAME_TYPE_TEST:
        case SMEM_LINK_TEST:
        case SMEM_LINK_NOT_TEST:
        case CONSTANT_MATCH_TEST:          // added
            return (t->type << 24) + t->data.referent->hash_id;
```

After the fix, two things should be checked:
- Chunks built over such a rule should print with the negated condition intact, and should literalize the variable if it is also tested with `$` positively. EBC's literalization (`check_for_constant_match_literalization`, `ebc_unify.cpp` line 178) is applied only to ground and local conditions, not to negated ones.
- Other switches over test types should be audited for the new type. `reverse_direction_of_relational_test` (`soar_representation/production_reorder.cpp`, line 438) also has no `CONSTANT_MATCH_TEST` case and aborts in its `default:` branch. I did not find an input that reaches it.

### Workaround

Do not use `$` inside negated conditions. Write the `$` on a positive condition that binds the same variable.

---

## Bug 2: `$` after another test inside `{ … }` crashes Soar when the rule is loaded

### Reproduce

`bug2-conjunctive-dollar.soar` (attached) contains:

```
sp {result*conjunctive-relational-dollar
   (state <ss> ^superstate <s>)
   (<s> ^objects <os>)
   (<os> ^object <a> <b>)
   (<a> ^handle <ha>)
   (<b> ^handle { <> <ha> $ <hb> })
-->
   (<s> ^pair <p>)
   (<p> ^first <ha> ^second <hb>)}
```

```
source bug2-conjunctive-dollar.soar
```

### Observed

Segmentation fault during `source`, before the agent runs. Backtrace (gdb):

```
#0  simplify_test(agent_struct*, test_struct**, saved_test_struct*)
#1  simplify_condition_list(agent_struct*, condition_struct*)
#2  reorder_condition_list(...)
#3  reorder_lhs(...)
#4  parse_production(agent_struct*, char const*, unsigned char*)
#5  cli::CommandLineInterface::DoSP(...)
```

### Expected

The rule loads and behaves like `{ <> <ha> <hb> }`, with `<hb>` literalized in chunks.

### Cause

1. In `parse_test` (`parsing/parser.cpp`, line 585), each element of `{ … }` is parsed by `parse_simple_test` and added with `add_test(thisAgent, &t, temp)` (line 627). For `$ <hb>`, `parse_simple_test` returns the conjunctive test `{ <hb> $$ <hb> }`.
2. When `$ <hb>` follows another test, `add_test` (`soar_representation/test.cpp`, line 280) nests that conjunctive test inside the outer one instead of merging it. The outer test becomes `{ <> <ha> { <hb> $$ <hb> } }`. Its `eq_test` points into the nested test (line 317), and the outer list itself holds no equality test.
3. `simplify_test` (`soar_representation/production_reorder.cpp`, line 290) moves every non-equality conjunct out of the outer list into the saved-test list. That includes the nested conjunctive test, so the list becomes empty.
4. The code then reads `ct->data.conjunct_list->rest` (line 379), dereferencing NULL.

When `$ <hb>` comes first, as in `{ $ <hb> <> <ha> }`, `add_test` starts from the conjunctive test itself and appends to it, so the result is flat and loads correctly. The libraries' `{ $ <count> > 2 }` is of this form and works.

### Suggested fix

Flatten conjunctive tests when they are added to a test, in `add_test`:

```cpp
    /* new: splice the conjuncts of a conjunctive new_test instead of nesting it */
    if (new_test->type == CONJUNCTIVE_TEST)
    {
        for (cons* c2 = new_test->data.conjunct_list; c2; c2 = c2->rest)
            add_test(thisAgent, dest_test_address, static_cast<test>(c2->first), merge_disjunctions);
        /* free the now-empty wrapper (its conjunct list and the test struct, not the sub-tests) */
        ...
        return true;
    }
```

The same could be done in `parse_test` only, or in the `DOLLAR_LEXEME` case by returning the two tests to be added separately. Fixing `add_test` also covers other callers that combine tests.

`simplify_test` should also be made robust:
- Guard against an empty conjunct list after the non-equality tests are removed.
- The `if (!sym)` branch (around line 325) assigns `c->first` and `c->rest` with `c` uninitialized; it needs `allocate_cons(thisAgent, &c)` first. That branch is reached only when a conjunctive test has no equality test, which the parser normally prevents, but nested conjunctive tests break that assumption.

### Workaround

Put `$ <x>` first inside the braces, `{ $ <hb> <> <ha> }`, or test the variable with `$` in a separate condition. `bug2-workaround.soar` (attached) loads and runs without error with chunking on.

---

## Notes

- The proposed fixes have not been compiled or tested against the Soar source; the causes were found by reading the source and confirmed with the backtrace and the reproduction files.
- Attached: `bug1-negated-dollar.soar`, `bug2-conjunctive-dollar.soar`, `bug2-workaround.soar`, `run.py` (a minimal SML runner: `python3 run.py <file.soar> "chunk never"`).
