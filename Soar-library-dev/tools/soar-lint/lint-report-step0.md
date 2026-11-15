# soar_lint report

Static reading of the .soar and datamap files only. Commented-out rules are not counted as active. Load order assumed: simple, selection-world, selection-optimal, selection-iterative-deepening, agent-world, thor-soar.

## 1. Inventory

| project | active rules | :default | commented-out rules | .soar files | files with rules | unsourced files |
|---|---|---|---|---|---|---|
| simple | 8 | 8 | 0 | 1 | 1 | 0 |
| selection-world | 86 | 83 | 7 | 29 | 10 | 0 |
| selection-optimal | 10 | 10 | 3 | 18 | 4 | 0 |
| selection-iterative-deepening | 86 | 86 | 4 | 37 | 22 | 0 |
| agent-world | 313 | 307 | 69 | 65 | 40 | 1 |
| thor-soar | 834 | 20 | 89 | 170 | 118 | 0 |
| **total** | 1337 |  | 172 |  |  |  |

Backup (~) files and directories: 156. Sourcing problems: 1. Generator productions (gp, each expands to several rules at load time): 1 (thor-soar/elaborations/random-operator-selection.soar).

- missing-file: `../agent/thor-soar-semantic-memory.soar` sourced from `thor-soar/_firstload.soar` does not exist in the zip

## 2. Rules defined more than once (same name)

| scope | rule | definitions (project:file:line, in load order) | last loaded (wins) | bodies identical |
|---|---|---|---|---|
| cross-project | `apply*operator*external*argument2*no-handle1*no-handle2` | agent-world:external-operator-application.soar:178; thor-soar:external-operator-application.soar:94 | thor-soar | no |
| cross-project | `default*select*reject*conflict` | simple:simple.soar:88; selection-world:elaborations.soar:5 | selection-world | no |
| cross-project | `selection*compare*same-symbolic-evaluations-are-indifferent` | selection-world:elaborations.soar:175; selection-optimal:elaborations.soar:48 | selection-optimal | no |
| cross-project | `selection*compare*success-evaluation-better-than-partial-success` | selection-world:elaborations.soar:249; selection-optimal:elaborations.soar:8 | selection-optimal | no |
| cross-project | `selection*select*success-evaluation-becomes-best-preference` | selection-world:elaborations.soar:293; selection-optimal:elaborations.soar:79 | selection-optimal | no |
| same-file | `elaborate*thor-soar*desired*put-potato-in-cabinet-then-close-cabinet-then-get-potato` | thor-soar:desireds-sequence.soar:45; thor-soar:desireds-sequence.soar:77 | thor-soar | no |
| same-project | `thor-soar*compare*anchor-info-existing-object*distance` | thor-soar:search-control.soar:180; thor-soar:anchor-info-existing-object.soar:489 | thor-soar | no |

## 3. excise commands

| project | file | line | target | state | target defined in |
|---|---|---|---|---|---|
| agent-world | goal-completed.soar | 1 | `top-goal*halt*success` | commented | selection-world |
| agent-world | elaborations.soar | 35 | `evaluate-operator*elaborate*state*desired` | commented | not defined anywhere |

## 4. Rule-name prefixes

Rules whose name starts with another project's prefix:

| in project | prefix | rule |
|---|---|---|
| thor-soar | agent-world | `agent-world*compare*find-object*worse*operator-grounded2` |
| thor-soar | agent-world | `agent-world*compare*find-object*controlled-by` |
| thor-soar | agent-world | `agent-world*compare*find-object*on-in*prefer*arg2` |
| thor-soar | agent-world | `agent-world*compare*find-object*worse2` |
| thor-soar | agent-world | `agent-world*reject*twin*sliced-object*argument1` |
| thor-soar | agent-world | `agent-world*reject*twin*sliced-object*argument2` |
| agent-world | thor-soar | `thor-soar*elaborate*operator*desired-count0*achieved-0` |

Distinct first name elements per project: simple 3, selection-world 6, selection-optimal 3, selection-iterative-deepening 6, agent-world 21, thor-soar 21

## 5. Flags (^flags.*)

| flag | read by (rules) | set by (rules) | issues |
|---|---|---|---|
| above-computed | thor-soar 1 | thor-soar 1 |  |
| agent-mode | agent-world 1 | thor-soar 1 | read-below-initializer |
| attend-all | agent-world 1 | thor-soar 1 | read-below-initializer |
| clean-up-on-success | thor-soar 1 | thor-soar 1 |  |
| desired-preferences | thor-soar 1, agent-world 7 | thor-soar 1 | read-below-initializer |
| desired-selection | thor-soar 161 | thor-soar 2 |  |
| desireds-source | thor-soar 4, agent-world 1 | thor-soar 1 | read-below-initializer |
| epmem-retrieve | thor-soar 1 | thor-soar 1 |  |
| explore | thor-soar 8, agent-world 1 | thor-soar 3 | read-below-initializer |
| explore-receptacles | thor-soar 6 | thor-soar 3 |  |
| forget-unattended | agent-world 2 | thor-soar 1 | read-below-initializer |
| gps-desired-ordering | agent-world 6 | thor-soar 1 | read-below-initializer |
| guardrails | thor-soar 2, selection-world 2 | thor-soar 1 | read-below-initializer |
| hide-in-container-objects | thor-soar 12 | thor-soar 1 |  |
| hierarchical-properties | selection-world 1 | thor-soar 1 | read-below-initializer |
| init-evaluation-depth | selection-iterative-deepening 3 | thor-soar 1 | read-below-initializer |
| initialize-scene-with-smem | thor-soar 4 | thor-soar 2 |  |
| iterative-step | selection-iterative-deepening 9 | thor-soar 1 | read-below-initializer |
| look-ahead-planning | thor-soar 1 | thor-soar 1 |  |
| mea-operator-selection | thor-soar 65 | thor-soar 1 |  |
| profile | thor-soar 1 | - | read-never-initialized |
| rl | agent-world 1 | thor-soar 1 | read-below-initializer |
| scan-room | - | thor-soar 1 | initialized-never-read |
| smem-retrieve | thor-soar 11 | thor-soar 1 |  |
| smem-store | agent-world 9 | thor-soar 1 | read-below-initializer |
| task-search-control | thor-soar 20 | thor-soar 1 |  |
| use-timers | thor-soar 5, agent-world 1 | thor-soar 1 | read-below-initializer |
| verify | agent-world 1, selection-iterative-deepening 6 | thor-soar 1 | read-below-initializer |
| view-frustum | thor-soar 21 | thor-soar 1 |  |

## 6. Problem-space gating

| project | rules | test a problem-space attribute | mention problem-space | most common gates |
|---|---|---|---|---|
| simple | 8 | 0 | 0 |  |
| selection-world | 86 | 2 | 4 | no-local-negations 2 |
| selection-optimal | 10 | 0 | 0 |  |
| selection-iterative-deepening | 86 | 1 | 1 | name=<name> 1 |
| agent-world | 313 | 36 | 40 | agent-world 31; internal-actions 2; name=thor-world 2; name=<problem-space> 2 |
| thor-soar | 834 | 117 | 122 | name=thor-world 105; name=<< 11; name=clean-dishwasher 1 |

## 7. Domain vocabulary in library projects

Words: turn-on, turn-off, go-to, accessible, reachable, visible, sliced, cook-state, cookable, broken, egg, coffee, toast, cook-microwave, scan-room, thor-world (whole-word match in rule name or body).

**agent-world: 35 rules**

| file | rule | words |
|---|---|---|
| external-operator-application.soar | `apply*operator*external*argument0` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument1` | turn-off, turn-on |
| external-operator-application.soar | `apply*operator*external*argument1*turn-on` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument1*turn-on*time` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument1*turn-off` | turn-off |
| external-operator-application.soar | `apply*operator*external*argument1*no-handle` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument2*no-handle1` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument2*no-handle2` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument2*no-handle1*no-handle2` | turn-on |
| external-operator-application.soar | `apply*operator*external*argument3*no-handle2` | coffee, cook-microwave, toast |
| find-object-direct.soar | `agent-world*propose*find-object-direct*object-handle*class-only-one` | accessible |
| find-object-direct.soar | `agent-world*propose*find-object-direct*object-handle*in*argument1` | accessible |
| find-object-direct.soar | `agent-world*propose*find-object-direct*object-handle*in*argument2` | accessible |
| find-object-direct.soar | `agent-world*propose*find-object-direct*object-handle*class-plus-one` | accessible |
| find-object-direct.soar | `agent-world*compare*find-object-direct*anchored-reachable` | reachable |
| find-object-direct.soar | `agent-world*compare*find-object-direct*accessible` | accessible, reachable |
| find-object-direct.soar | `agent-world*elaborations*compute-distances*find-object-direct` | reachable |
| find-object-direct.soar | `agent-world*compare*find-object-direct*distance` | accessible, reachable |
| find-object.soar | `agent-world*compare*find-object*better-if-ready` | accessible |
| force-conflict.soar | `agent-world*compare*force-conflict` | turn-off |
| force-conflict.soar | `agent-world*compare*force-conflict*reject*only-one-option` | turn-off |
| remove-object.soar | `agent-world*propose*remove-object*not-desired*hack` | visible |
| finish-future-event.soar | `agent-world*compare*go-to*finish-future` | go-to |
| assume-successful-grounding.soar | `evaluate-operator*propose*assume-successful-grounding` | thor-world |
| assume-successful-grounding.soar | `evaluate-operator*propose*assume-successful-grounding*in-on` | thor-world |
| assume-successful-grounding.soar | `apply*assume-successful-grounding*not-sliced` | accessible, reachable, sliced |
| assume-successful-grounding.soar | `apply*assume-successful-grounding*sliced` | accessible, cook-state, cookable, reachable, sliced |
| future-event.soar | `agent-world*apply*clear*future-event` | broken, egg |
| future-event.soar | `agent-world*apply*complete*future-event*change-property*external-not-visible` | visible |
| future-event.soar | `agent-world*apply*complete*future-event*change-property*external-not-visible*property-not-exist` | visible |
| future-event.soar | `agent-world*apply*complete*future-event*change-property*external-not-visible*no-value` | visible |
| future-event.soar | `agent-world*apply*complete*future-event*add-desired*external-not-visible` | visible |
| future-event.soar | `agent-world*reject*operators*disturbing*future-event` | go-to |
| future-event.soar | `agent-world*compare*future-event2` | go-to |
| skip-wait.soar | `Impasse__State_No-Change*compare*skip-wait*soonest-wait` | scan-room |

## 8. Identical rule bodies under different names

- simple `elaborate*state*top-state`; agent-world `elaborate*substate*top-state`

## 9. Commented-out rules

| project | commented-out | with no active rule of the same name | files with most |
|---|---|---|---|
| simple | 0 | 0 |  |
| selection-world | 7 | 6 | elaborations.soar 5; elaborations.soar 1; elaborations.soar 1 |
| selection-optimal | 3 | 3 | _chunks.soar 3 |
| selection-iterative-deepening | 4 | 3 | elaborations.soar 3; task-operator.soar 1 |
| agent-world | 69 | 31 | achieved-desireds.soar 45; monitor-desireds.soar 8; monitor-state.soar 3 |
| thor-soar | 89 | 75 | update-scene-smem-object-visible.soar 10; achieved-desireds.soar 10; detect-illegal-desired.soar 9 |

## 10. Top-level commands other than source/pushd/popd (settings in the loaded files)

- **thor-soar**: epmem 28, chunk 4, rl 2, svs 2, decide 1, soar 1, w 1, wma 1, smem 1

- **selection-world**: multi-attributes 1

- **agent-world**: production 36, alias 4, max-nil-output-cycles 1, max-goal-depth 1, max-elaborations 1, srand 1, decide 1, wma 1

## 11. Datamaps against rules (attribute names only)

| project | datamap format | vertices | unreachable from any state root |
|---|---|---|---|
| simple | none |  | n/a |
| selection-world | vsa.json | 162 | 0 |
| selection-optimal | dm | 31 | n/a |
| selection-iterative-deepening | vsa.json | 170 | 3 |
| agent-world | vsa.json | 389 | 39 |
| thor-soar | vsa.json | 1383 | 349 |

| project | attribute names used by its rules | declared only by a higher layer | declared nowhere |
|---|---|---|---|
| simple | 10 | 10 | 0 |
| selection-world | 88 | 0 | 0 |
| selection-optimal | 11 | 0 | 0 |
| selection-iterative-deepening | 55 | 0 | 0 |
| agent-world | 174 | 0 | 0 |
| thor-soar | 297 | 0 | 0 |

| project | attribute names declared (reachable) but used by no rule in any project |
|---|---|
| selection-world | 18 |
| selection-optimal | 0 |
| selection-iterative-deepening | 9 |
| agent-world | 3 |
| thor-soar | 99 |

| library datamap | attribute names missing from thor-soar datamap | examples |
|---|---|---|
| selection-world | 20 | all-attributes-at-level, copied-structure, dont-copy-anything, dont-copy-object-atttribute, duplicates, exhaustion-failure, expected-value, found-value |
| selection-optimal | 3 | partial-failure, success-depth, superoperator |
| selection-iterative-deepening | 18 | count, counted-desired-handle, counted-desired-relation, counted-object-handle, counted-relation, feature-count, indifferent, item |
| agent-world | 5 | achieved-desireds, copied-from, environment, mode, verify-done |
