# CLAUDE.md: working in Soar-Lean-Agents

Read `README.md` for the layout and `RESUME.md` for where things stand. `Soar/lean-spec/SOAR-LEAN-CONTEXT.md` is the Lean specification's own CLAUDE.md (a different project); this file is the one for this repository.

## Where the specification is silent: stop and surface (issue 6)

Where the Soar conventions and the Lean specification are silent on a decision the work requires, **stop and surface it to the user.** Do not choose a default, and do not record the choice as an accepted assumption. The assumption ledger is for places where the user's English was open, not for gaps in the specification. Surface the gap at the stage it is hit: a question during formalization costs one exchange; the same question found at run time costs a day.

This applies to every stage: formalization (a representation the conventions do not fix), generation (which selection library to pair with), review and back-translation (presenting an invented choice as a design decision), diagnosis (reasoning about a run before establishing what the build can do), and the convention and library work itself (saying a convention settles a question when the row cited is weaker than claimed).

| Situation | Action |
|---|---|
| The English is ambiguous | Assumption-ledger entry; proceed; flag at review |
| The specification is silent (no convention row, nothing in the Lean spec) | Stop and ask. Do not proceed |
| The specification is clear but the tooling cannot do it | Record a named gap; if load-bearing, say so first |

Do not enter a specification gap in the assumption ledger as an accepted assumption: it then looks like a statement of what the user meant.

## Reporting

- **Lead with runnability.** A handover opens with "runnable" or "skeleton: cannot run until these N files are written", not with file and production counts.
- **Verify before diagnosing.** Before analysing a reported run, establish that the build on disk can produce the behaviour described (for example, that no hand-written file is still empty).
- Use the user's design hints. A hint in the description that the output does not realise is a gap to report, not an item to drop.

## Not yet enforced

The check that fails on an open `gap` assumption (an assumption `kind`: intent, gap, tooling) needs a Lean change to `Agent.Assumption` and `check` (issue 6). Until then this file is the control.
