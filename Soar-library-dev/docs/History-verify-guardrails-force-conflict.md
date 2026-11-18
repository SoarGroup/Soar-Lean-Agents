# Removed in library v2.38: verify, guardrails and force-conflict

Removed 16 November 2026 (library v2.38) to simplify the library. These were experiments; this file keeps their rule text so they can be reintroduced. The text is exactly as it stood in v2.37.

## What the pieces did

- **verify** (selection-world flag, default false). When true, the top selection started iterative deepening at depth 10 instead of 1 (the maximum stayed 12), and `agent-world*elaborate*desired-verify` copied the flag value to `^desireds.verify` on the top state.
- **force-conflict** (agent-world, 12 rules; agent-world tie impasse, 3 rules; thor-soar, 2 rules). When `^desireds.verify` was true (from the verify flag, the input sentence "Be careful.", a desired with `^action be-careful` or `^safety ensure`), a force-conflict task operator was proposed at the top state. It was always worse than real task operators, so it was only chosen when nothing else could be, and its application reported a constraint failure (`^report-test-result.result failure`). With `^desireds.verify external-action`, force-conflict was made both better and worse than each external-action operator, forcing an operator conflict before every external action. Applying a task operator removed `^desireds.verify` and set `^verify-done true`. In look-ahead, evaluating force-conflict gave a failure and the evaluate-operator for it was made worse.
- **guardrails** (selection-world flag, default false). When true, the agent's `^self.pose` was copied into a deep-copied look-ahead world, which let thor-soar compute `^expected-distance` for go-to in look-ahead and detect the "running with knives" constraint failure (holding a non-plastic knife on a go-to longer than 10).

No test in test set v1.31 set either flag or gave a be-careful or safety desired; removing them changed no decision or trace in the 384 library tests (only firing and WME counts). thor-soar set both flags to false in flags-initialization.soar.

## Also removed

- Datamap entries: `^flags.verify`, `^flags.guardrails`, `^flag-override.verify`, `^flag-override.guardrails`, `^desireds.verify`, `^desireds.verify-done`, `^desired.safety`, `^desireds.action be-careful`, and the operator name `force-conflict`.
- Source lines: `source force-conflict.soar` in agent-world/agent-world_source.soar and thor-soar/from-agent-world/from-agent-world_source.soar; the Visual Soar entries for both files.
- thor-soar/elaborations/flags-initialization.soar: the lines `^guardrails false` and `^verify false  # true external-action`.
- In init-current-evaluation-depth.soar, the test `-^flags.verify true` was removed from the three top-selection proposals and from `selection-world*apply*init-current-evaluation-depth*max`.

## Rule text (v2.37), by file

### selection-world/_flags.soar
```
## Elaborate flags default verify -> sets verify.
## true: verify look-ahead evaluations: the top selection starts at depth 10 (the maximum depth stays 12).
sp {selection-world*elaborate*flags*default*verify
   :default
   (state <s> ^superstate nil
              ^flags <f>
             -^flag-override.verify <any>)
-->
   (<f> ^verify false)
}
```

### selection-world/_flags.soar
```
## Elaborate flags default guardrails -> sets guardrails.
## true: the agent's pose (^self.pose) is copied into a deep-copied look-ahead world. No other rule reads this flag.
sp {selection-world*elaborate*flags*default*guardrails
   :default
   (state <s> ^superstate nil
              ^flags <f>
             -^flag-override.guardrails <any>)
-->
   (<f> ^guardrails false)
}
```

### selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar
```
## Propose init-current-evaluation-depth.
sp {selection-world*propose*selection*init-current-evaluation-depth*top-selection*verify
   :default
   (state <s> ^name selection
              ^flags.verify true
             # ^top-selection true
             -^current-evaluation-depth)
-->
   (<s> ^operator <operator> + =, >)
   (<operator> ^name init-current-evaluation-depth
               ^value 10)
}
```

### selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/init-current-evaluation-depth.soar
```
## Apply init-current-evaluation-depth -> sets max-evaluation-dep.
sp {selection-world*apply*init-current-evaluation-depth*max*verify
   :default
   (state <s> ^top-selection true
              ^flags.verify true
              ^flags.max-evaluation-depth <max>
              ^operator <operator>)
   (<operator> ^name init-current-evaluation-depth)
-->
   (<s> ^max-evaluation-depth <max>)
   #was 7, 9, 10 (raised to 12)
}
```

### selection-world/Operator_Tie/evaluate-operator/elaborations.soar
```
## Elaborate evaluate-operator default-state-copy-self io pose.
sp {selection-world*elaborate*evaluate-operator*default-state-copy-self*io*pose
   :default
   (state <s> ^deep-copy-world true
              ^flags.guardrails true
              ^selection-superstate.top-state.io.input-link.self.pose <pose>
              ^world <new-world>)
   (<new-world> ^self <new-self>)
-->
   (<new-self> ^pose <pose>)
}
```

### selection-world/Operator_Tie/evaluate-operator/elaborations.soar
```
## Elaborate evaluate-operator default-state-copy-self pose.
sp {selection-world*elaborate*evaluate-operator*default-state-copy-self*pose
   :default
   (state <s> ^deep-copy-world true
              ^flags.guardrails true
              ^world <new-world>)
   (<new-world> ^duplicate-of.self.pose <pose>
                ^self <new-self>)
-->
   (<new-self> ^pose <pose>)
}
```

### agent-world/force-conflict.soar (whole file)
```
## force-conflict.soar -- agent-world: 4 elaborations, 2 proposals, 3 compares, 3 applications.

## ---- elaborations ----

## Elaborate desired-verify -> sets verify.
sp {agent-world*elaborate*desired-verify
   :default
   (state <s>
              ^real true
              ^superstate nil
              ^flags.verify { <> false <verify> }
              ^desireds <desireds>)
   (<desireds> -^object-state-desireds true
               -^verify-done true)
-->
   (<desireds> ^verify <verify>)}

## Elaborate desired-verify be-careful -> sets verify.
sp {agent-world*elaborate*desired-verify*be-careful
   :default
   :o-support
   (state <s>
              ^real true
              ^superstate nil
              ^io.input-link.language.sentence.complete-sentence |Be careful.|
              ^desireds <desireds>)
-->
   (<desireds> ^verify true)
}

## Elaborate desired-verify be-careful desired -> sets verify, desireds.
sp {agent-world*elaborate*desired-verify*be-careful*desired
   :default
   :o-support
   (state <s>
              ^real true
              ^superstate nil
              ^desireds <desireds> { <> <desireds> <desireds2> })
   (<desireds2> ^desired.action be-careful)
-->
   (<desireds> ^verify true)
   (<s> ^desireds <desireds2> -)
}

## Elaborate desired-verify be-careful safety -> sets verify, desireds.
sp {agent-world*elaborate*desired-verify*be-careful*safety
   :default
   :o-support
   (state <s>
              ^real true
              ^superstate nil
              ^desireds <desireds> { <> <desireds> <desireds2> })
   (<desireds2> ^desired.safety ensure)
-->
   (<desireds> ^verify true)
   (<s> ^desireds <desireds2> -)
}

## ---- operator proposal ----

## Propose force-conflict.
sp {agent-world*propose*force-conflict
   :default
   (state <s> ^superstate nil
              ^real true
              ^desireds.verify true)
-->
   (<s> ^operator <op> +)
   (<op> ^name force-conflict
         ^task-operator true)
}

## Propose force-conflict.
sp {agent-world*propose*force-conflict*external-action
   :default
   (state <s>
              ^quiescence t
              ^real true
              ^desireds.verify external-action)
-->
   (<s> ^operator <op> +, <)
   (<op> ^name force-conflict
         ^task-operator true)
}

## ---- evaluate / compare ----

## Preference for force-conflict next-desireds.
sp {agent-world*compare*force-conflict*next-desireds
   :default
   (state <s> ^operator <op1> +
                        { <> <op1> <op2> }  +)
   (<op1> ^name next-desireds)
   (<op2> ^name force-conflict)
-->
   (<s> ^operator <op1> > <op2>)
}

## Preference for force-conflict external-action.
sp {agent-world*compare*force-conflict*external-action
   :default
   (state <s>
              ^desireds.verify external-action
              ^operator <op1> +
                        { <> <op1> <op2> }  +)
   (<op1> ^name force-conflict)
   (<op2> ^name <> force-conflict
          ^task-operator true
          ^action-handle)
-->
   (<s> ^operator <op1> < <op2>
        ^operator <op1> > <op2>)
}

## Preference for force-conflict not-external-action.
sp {agent-world*compare*force-conflict*not-external-action
   :default
   (state <s>
              ^desireds.verify external-action
              ^operator <op1> +
                        { <> <op1> <op2> }  +)
   (<op1> ^name force-conflict)
   (<op2> ^name <> force-conflict
          ^task-operator true
         -^action-handle)
-->
   (<s> ^operator <op1> < <op2>)
}

## ---- operator application ----

## Apply task-operator remove force-conflict -> sets verify-done, verify.
sp {agent-world*apply*task-operator*remove*force-conflict
   :default
   (state <s>
              ^quiescence t
              ^real true
              ^desireds <desireds>
              ^operator <operator>)
   (<desireds> ^verify <verify>)
   (<operator> ^pre-conditions-satisfied true
               ^task-operator true)
-->
   (<desireds> ^verify-done true
               ^verify <verify> -)}

## Apply force-conflict -> sets report-test-result.
## If this operator ever gets selected and applied, something has gone wrong and there is a constraint failure
sp {agent-world*apply*force-conflict*interrupt
   :default
   (state <s>
              ^real true
              ^io.output-link <output-link>
              ^desireds.verify true
              ^operator.name force-conflict)
-->
   (<output-link> ^report-test-result.result failure)
   (log 1 | Constraint Failure.|)
}

## Apply force-conflict -> sets verify.
sp {agent-world*apply*force-conflict*remove*force-conflict
   :default
   (state <s>
              ^quiescence t
              ^real true
              ^desireds <desireds>
              ^operator <operator>)
   (<desireds> ^verify <verify>)
   (<operator> ^name force-conflict)
-->
   (<desireds> ^verify <verify> -)
}
```

### agent-world/Impasse__Operator_Tie/evaluate-operator.soar
```
## Preference for evaluate-operator force-conflict2.
sp {agent-world*compare*evaluate-operator*force-conflict2
   :default
   (state <s> ^operator <op>
              ^quiescence t
              ^superstate <superstate>)
   (<op> ^name evaluate-operator
         ^super-operator <super-operator>)
   (<super-operator> ^name force-conflict)
   (<superstate> ^operator <operator> +)
   (<operator> ^name force-conflict)
-->
   (<superstate> ^operator <operator> -)
}
```

### agent-world/Impasse__Operator_Tie/evaluate-operator.soar
```
## Apply evaluate-operator -> sets evaluation, symbolic-value, super-operator.
sp {agent-world*apply*evaluate-operator*force-conflict
   :default
   (state <s> ^operator <op>)
   (<op> ^name evaluate-operator
         ^super-operator <super-operator>)
   (<super-operator> ^name force-conflict)
   (<e> ^lower-bound $ <lower-bound>)   # v2.30: the chunk tests this bound literally (none: no cut-off below)
-->
   (<s> ^evaluation <e>)
   (<e> ^symbolic-value failure
        ^super-operator <super-operator>)
}
```

### agent-world/Impasse__Operator_Tie/elaborations.soar
```
## Preference for selection evaluate force-conflict worse.
sp {agent-world*compare*selection*evaluate*force-conflict*worse
   :default
   (state <s> ^name selection
              ^operator <o> +)
   (<o> ^name evaluate-operator
        ^super-operator.name force-conflict)
-->
   (<s> ^operator <o> < )}
```

### thor-soar/from-agent-world/force-conflict.soar (whole file)
```
## force-conflict.soar -- thor-soar: 2 compares.

## Preference for force-conflict.
sp {agent-world*compare*force-conflict
   :default
   (state <s>
              ^desireds.verify true
              ^operator <op1> +
                        { <> <op1> <op2> }  +)
   (<op1> ^name force-conflict)
   (<op2> ^name <> force-conflict <> turn-off
          ^task-operator true)
-->
   (<s> ^operator <op1> < <op2>
        ^operator <op1> > <op2>)
}

## Preference for force-conflict reject only-one-option.
sp {agent-world*compare*force-conflict*reject*only-one-option
   :default
   (state <s>
              ^operator <op1> +)
  -{(<s> ^operator { <> <op1> <op2> }  +)
   (<op2> ^name <> force-conflict <> turn-off
          ^task-operator true)}
   (<op1> ^name force-conflict)
-->
   (<s> ^operator <op1> -)
}
```

### thor-soar/Impasse__Operator_Tie/evaluate-operator/detect-constraint-failure.soar
```
## Apply go-to -> sets constraint-failure, failure-string.
## Could just reject it..
sp {evaluate-operator*elaborate*state*detect-constraint-failure*running-with-knives
   :default
   (state <s>  ^real false
              ^flags.guardrails true
              ^desireds <desireds>
              ^world.holding-object <knife-object>
              ^operator <operator>)
   (<knife-object> ^class knife
                  -^material plastic)
   (<operator> ^name go-to
               ^expected-distance > 10)
-->
   (log 1 (crlf) | ** Constraint Failure ** running with knife **|)
   (<s> ^constraint-failure <desireds>
        ^failure-string | ** Constraint Failure ** running with knife **|)}
```

### thor-soar/elaborations/search-control.soar
```
## Elaborate compute-distances single-destination-operators goto guardrails -> sets expected-distance.
sp {thor-soar*elaborations*compute-distances*single-destination-operators*goto*guardrails
    :default
   (state <s> ^operator <op1> +
              ^flags.guardrails true
              ^world.self.pose <pos>)
   (<op1> ^name go-to
          ^argument1 <arg1>)
   (<pos> ^x <x> ^y <y>)
   (<arg1> ^x <x1> ^y <y1>)
-->
   (<op1> ^expected-distance (+ (compute-range (* 100.0 <x>) (* 100.0 <y>) (* 100.0 <x1>) (* 100.0 <y1>))))
}
```

