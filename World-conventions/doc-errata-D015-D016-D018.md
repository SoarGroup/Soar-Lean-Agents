# Thor-Soar documentation: corrected passages (D-015, D-016, D-018)

Each section names the passage to replace and gives the new text.

---

## D-015: World section, the kinds of world and the `^anchored` entry

**Replace** the paragraph "A world structure can be: …" with:

> A world structure can be:
> - a direct reflection of what the agent knows about the current state of the external world,
>   derived from the ^scene (`<world> ^real true ^anchored-world true`);
> - a copy of the external world used for look-ahead search
>   (`<world> ^real false ^anchored-world true`);
> - a description of objects and relations that need to be grounded to objects and relations in
>   the scene (`<world> ^real false ^anchored-world false`).

**Replace** the `^anchored [true/false]` entry with:

> `^anchored-world [true/false]` Distinguishes worlds that model the real world (true: the real
> world derived from the scene, or copies of it in look-ahead search) from worlds that describe
> constraints on desired objects (false: built from ^world-context; see ^desireds).

**Add** to the description of objects (`^objects.object`):

> `^anchored [true/false]` On an object: true when the object is grounded in the scene (or is a
> look-ahead copy of a grounded object); false for an object in a ^world-context that still
> has to be grounded (see the unanchored egg example under ^desireds). Achievement of
> desireds and operator preconditions tests only anchored objects.

**In the two examples**, change `^anchored true` to `^anchored-world true` (W1) and
`^anchored false` to `^anchored-world false` (W3).

---

## D-016: Desireds section, count attributes and desired preferences

**Replace** the entries for the counts with:

> `^desired-count [integer]` The number of ^desired structures. It must be included when the
> desireds structure is created; it is not computed. agent-world counts at most 6 desired per
> desireds structure; a larger count is an error (a message is printed and the agent
> interrupts).
>
> `^achieved-desireds-count [integer]` The number of desired that are achieved. Computed in
> elaborations/achieved-desireds.soar (state desireds) and
> elaborations/achieved-desired-operators.soar (operator preconditions).
>
> `^unachieved-desireds-count [integer]` The number of desired that are not achieved.
> Computed in the same files. Iterative deepening uses it for its initial depth
> (^flags.init-evaluation-depth unachieved-desireds).
>
> `^unachieved-desireds [true]` Present when some desired is not achieved.

**Replace** the passage on desired preferences (Task Action Operators, "Not shown is that
^preferred-desired, ^avoid-desired, or indifferent-desired can be …") with:

> Not shown is that ^preferred-desired and ^avoid-desired can be added to a desireds
> structure. When ^flags.desired-preferences is true and an operator is proposed for a
> desired marked ^preferred-desired (or ^avoid-desired), a corresponding preference (> or <)
> is created for that operator. (^indifferent-desired is not supported.)

---

## D-018: Flags section

**Replace** the opening sentence ("These determine the specific processing. In
elaborations/flags-initialization.soar. Defaults are in bold.") with:

> These determine the specific processing. agent-world does not create ^flags: the task must
> create the ^flags structure on the top state (agent-world copies it to substates). A flag
> that is missing switches its behaviour off. Below, each flag lists the part of the system
> that reads it.

**Annotate or add** the following entries (the flags read by the libraries, as of 9 Nov 2026):

| Flag | Values | Read by |
|---|---|---|
| ^attend-all | true/false | agent-world |
| ^desired-preferences | true/false | agent-world (search control) |
| ^desireds-source | elaboration, language, … | agent-world (goal-completed). The attribute is ^desireds-source, not ^desired-source. |
| ^forget-unattended | true/false | agent-world |
| ^gps-desired-ordering | true/false | agent-world (search control) |
| ^use-timers | true/false | agent-world (look-ahead time as numeric evaluation) |
| ^rl | true/false | agent-world (not supported) |
| ^verify | true | agent-world (force-conflict), iterative deepening (maximum depth 10 instead of 7) |
| ^smem-store | true | agent-world (smem storage) |
| ^explore | false | agent-world |
| ^agent-mode | testing | agent-world |
| ^iterative-step | tie-impasse / operator | iterative deepening: what uses up evaluation depth |
| ^init-evaluation-depth | one / unachieved-desireds | iterative deepening: starting depth |
| ^guardrails | true | selection-world |
| ^hierarchical-properties | true | selection-world |
| ^mea-operator-selection | true/false | task rules (MEA proposals test it); not read by the libraries |
| ^look-ahead-planning | true/false | task rules; not read by the libraries |
| ^internal-simulation, ^clean-up-on-success, ^desired-selection, ^user | | Thor-Soar task code only; not read by agent-world or the selection libraries |
