# Proposal: ^static attributes on world objects (library changes)

Version 1, 19 November 2026. Against library v2.43. Conventions: World-Conventions-v6.xlsx rows L7-017 to L7-020 (new), L7-015, L8-022 and L14-026 (revised).

## The convention in brief

- A world object may have `^static <st>`, a structure that holds the attributes no task operator changes (L7-017). Which attributes are static is the task's decision, relative to its operators.
- Nothing ever writes under `^static` after the object is created, in the real world or in look-ahead (L7-018).
- The look-ahead copy shares the `^static` link, so a copied object costs one WME for its static attributes instead of one per attribute.
- Rules reach a static attribute as `^static.<attr>`. Desireds, attends, world-context and find-object descriptions name it flat (`^class mug`); a desired object never has `^static`. The library's achievement, unachieved and grounding rules match either form (L7-019).
- A derived object (a slice) gets its own `^static` (L7-020).

## What already works with no change

- **World copy.** `selection-world*elaborate*evaluate-operator*default-state-copy-object-attributes` copies every attribute value unchanged, so it already copies the `^static` identifier as a shared link. The only requirement is that no task lists `static` as `^dont-copy-object-attribute` (now stated in L14-026).
- **Iterative-deepening ground-state** (`.../Impasse__State_No-Change/ground-state.soar`) copies attributes generically and also copies the link.
- **Rules that test only the handle**, such as `agent-world*apply*operator*acheived-desired*handle*anchored-only` and the relation, holding, container and self rules, are unaffected.
- **Abstract-property achievement** ignores the attribute, so it is unaffected.

## Proposed changes

### S-1 agent-world: achievement and unachieved rules (needed for L7-019)

| Rule (file) | Change |
|---|---|
| `agent-world*apply*operator*acheived-desired*handle` (elaborations/achieved-desired-operators.soar) | Add a companion rule `...*handle*static` that matches the desired's flat attribute against `(<object> ^static.<attr> <value>)`. |
| `agent-world*elaborate*state*unachieved-desired-origin` (elaborations/achieved-desireds.soar) | Add a second negated conjunction: no anchored object with the handle has `^static.<attr> <value>`. Otherwise a desired on a static attribute is always unachieved. |
| `agent-world*elaborate*state*unachieved-desired*abstract-property` (same file) | Same added negation. |

### S-2 thor-soar: achievement and unachieved rules (elaborations/achieved-desireds-operators.soar, achieved-desireds.soar)

- `thor-soar*elaborate*operator*acheived-desired*handle2`: add a `*static` companion, as in S-1.
- `...*unacheived-desired`, `...*unacheived-desired-origin`, `...*unacheived-desired*abstract-property` and `...*unacheived-desired-origin*abstract-property`: add the second negated conjunction, as in S-1.
- `thor-soar*elaborate*state*achieved-desired*handle*object*class` (achieved-desireds.soar): test `^static.class` once class is static (see S-5).

No new negations on local structure are introduced beyond those the rules already have. The added conjunction tests the shared `^static` structure, which belongs to the real world.

### S-3 thor-soar: grounding

- `find-object-direct.soar` (4 rules): the "no other attributes to constrain grounding" negations and the feature match at line 112 compare a world-context description, which stays flat, with an anchored object. Add the `^static.<feature>` path to the match, and make the negation ignore `^static`.
- `anchor-info-existing-object.soar` (3 proposals): `^class` and the `^{ <> class <attribute> }` match on the anchored scene object need the `^static` path for static attributes. The dynamic list in these rules (cook-state, dirty, open, broken, temperature, activated, liquid-contents, reachable, sliced) is a ready-made list of the attributes that are not static in Thor.

### S-4 thor-soar: perception, memory retrieval and storage

- **Scene creation** (`scene-creation.soar`): `apply*scene-creation*hidden` and `*not-hidden` create `^static` with the new object. `apply*scene-creation*scene-attribute-value` puts a property under `^static` when it is declared static, and on the object otherwise. Declaring the set: a list on the problem space (`^static-object-attribute <attr>`), mirroring `^dont-copy-object-attribute`.
- **smem and epmem retrieval** (`anchor-epmem-retrieve.soar`, `anchor-smem-object-retrieve.soar`, `smem-copy-retrieved-object.soar`, `smem-copy-retrieved-in.soar`, `init-scene-smem.soar`): these copy a retrieved object attribute by attribute. A retrieved `^static` must be copied into a new `^static`, not shared. A retrieval structure disappears when the retrieval is cleared (epmem) or is long-term-memory structure (smem). Sharing it would also break L7-018.
- **smem storage** (`object-world/elaborations/smem-store-scene.soar`): stores `^static` as substructure. No change is needed, but retrieval then depends on the copying above.

### S-5 Thor-Soar: which attributes become static

Candidates from the Thor input properties: `class`, `openable`, `graspable`, `sliceable`, `cookable`, `breakable`, `fillable`, `dirtyable`, `activatable`, `recyclable`, `material`, `mass`. They are tested in these numbers of library and Thor task files:

| Attribute | Files | Occurrences |
|---|---|---|
| class | 74 | 461 |
| openable | 13 | 22 |
| graspable | 12 | 25 |
| cookable | 9 | 21 |
| activatable | 6 | 11 |
| fillable | 5 | 9 |
| dirtyable | 4 | 9 |
| material | 3 | 7 |
| breakable | 3 | 3 |
| sliceable | 2 | 2 |
| mass, recyclable | 0 | 0 |

Not every occurrence is a test of a world object: some are on scene, input-link, desired or info objects. `class` carries most of the saving and most of the editing. Suggested order: move the capability flags first (about 110 occurrences), and `class` second.

Precedent: Thor world objects already hold an identifier link that is shared and not copied by value, `^derived-from-input` (the input-link object). L7-015 does not list it. It should be added to L7-015's exceptions or removed from world objects; this is a separate decision.

### S-6 Checks (worldcheck / soar-lint)

1. Flag any action whose target identifier is reached through a `^static` condition. This enforces L7-018. The allowed exception is the rule that creates the object and its `^static` in the same action.
2. Flag a desired object, attend or world-context object that has `^static`.
3. Flag `static` listed as `^dont-copy-object-attribute`.
4. Flag an identifier value under `^static`, since L7-017 requires constants there.

### S-7 Datamaps

Add `^static` (an identifier with the static attributes) under the world object in the agent-world, object-world, thor-soar and thor-tasks `.vsa.json` files and in `library-datamap.json`. Move the static Thor attributes under it when S-5 is done.

### S-8 Tests and measurement

- The current test set does not use `^static`, so S-1 to S-3 should leave all results unchanged. Run the full test set to confirm.
- New test: a Water Jug variant with `^static.volume` (jug capacity never changes), run under look-ahead. Compare WMEs created by the copy and decisions against the flat version; the plans must be identical.
- Thor-Soar, after S-5: count the WMEs created per look-ahead state before and after, on one kitchen task.

## Measured on KenKen (19 November 2026)

The 16 KenKen world programs were rewritten to the ^static layout with `tools/staticize/staticize.py`, which computes the static set as L7-022 describes. No library change was needed. All 96 runs (two layouts, seeds 1-3) reach the same correct grids. The copy rule fires 76% less on kenken-6-2. Over all runs, firings fall by 12.7% and WME changes by 8.4% (6x6 puzzles: -18% and -13.5%). Time per decision does not change, because KenKen's cost lies in a pairwise preference rule and per-state index rebuilding, not in the copy. Details: `studies/KenKen-static-layout-results.md`.

## Suggested order

1. S-1 and S-8 (Water Jug variant): the library supports `^static` and the saving is measured. This becomes release v2.44.
2. S-6 checks, before any task depends on `^static`.
3. S-2, S-3 and S-4 with the S-7 datamaps, with the capability flags moved first (S-5).
4. `class` moved under `^static` (S-5).

Assisted by Claude.
