import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'rosie-teaching', 'tools'))
import convpass   # 18 Nov 2026 conventions: problem-space test (L3-005), group comments (L3-012)
import os
LOADS=[("cross-1m",1,0),("cross-2m",2,0),("cross-1c",0,1),("cross-2c",0,2),("cross-1m1c",1,1)]
DESC="""## Missionaries and cannibals, written to the world conventions (agent-world,
## selection-world, selection-iterative-deepening).
## Written from the English description only.
##
## Description:
##   Three missionaries and three cannibals are on one bank of a river. They
##   have a boat that holds at most two people, and it cannot cross empty. Get
##   all six people to the other bank. If at any time the cannibals on either
##   bank outnumber the missionaries on that bank, the cannibals will eat those
##   missionaries; cannibals alone on a bank, with no missionaries there, are
##   harmless. How can everyone cross safely?
##
## World: objects left and right (^type bank, ^missionaries, ^cannibals) and
## boat (^type boat, ^side <bank handle>, ^visited <situation label>*).
## A situation label is <from>-<m>-<c>-<to>-<m>-<c>-<boat side> after a crossing.
## Goal: one desired, the left bank is empty (^empty true).
## Task operators: one per boat load (cross-1m, cross-2m, cross-1c, cross-2c,
## cross-1m1c), ^argument1 = bank the boat leaves, ^argument2 = bank it reaches.
## Loads that are impossible, leave missionaries outnumbered, or return to a
## situation already visited are rejected. Look-ahead (iterative deepening) chooses among the rest.
"""
R=[DESC,"""
sp {missionaries-cannibals*propose*initialize-missionaries-cannibals
   (state <s> ^superstate nil ^world <w> -^name)
-->
   (<s> ^operator <o> + >)
   (<o> ^name initialize-missionaries-cannibals ^task-operator false)
}

sp {missionaries-cannibals*apply*initialize-missionaries-cannibals
   (state <s> ^operator.name initialize-missionaries-cannibals ^world <w>)
   (<w> ^objects <objs>)
-->
   (<s> ^name missionaries-cannibals ^desireds <ds> ^load-table <lt>)
   (<objs> ^object <left> <right> <boat>)
   (<left> ^object-handle left ^anchored true ^type bank ^missionaries 3 ^cannibals 3)
   (<right> ^object-handle right ^anchored true ^type bank ^missionaries 0 ^cannibals 0)
   (<boat> ^object-handle boat ^anchored true ^type boat ^side left ^visited |right-0-0-left-3-3-left|)
   (<ds> ^desired-count 1 ^desired <d1>)
   (<d1> ^object <d1-o>)
   (<d1-o> ^object-handle left ^empty true)
""" + "".join(f"   (<lt> ^load <l-{n}>)\n   (<l-{n}> ^name {n} ^missionaries {m} ^cannibals {c})\n" for n,m,c in LOADS) + """   (log 1 (crlf) |Initialize missionaries-cannibals.|)
}

sp {missionaries-cannibals*elaborate*problem-space
   (state <s> ^name missionaries-cannibals)
-->
   (<s> ^problem-space <p>)
   (<p> ^name missionaries-cannibals ^agent-world true ^default-state-copy no ^default-operator-copy no ^default-desired-copy no ^dont-copy top-state)
}

sp {missionaries-cannibals*elaborate*problem-space*mea-substate
   (state <s> ^impasse no-change ^attribute operator ^superstate <ss>)
   (<ss> ^problem-space.name missionaries-cannibals ^operator <so>)
   (<so> ^task-operator true -^pre-conditions-satisfied true)
-->
   (<s> ^problem-space <p>)
   (<p> ^name missionaries-cannibals ^agent-world true)
}

## Search setting measured with probe_settings.py (16 Nov 2026, library v2.34): tie-impasse 367 decisions against 1,451 with operator depth (seeds 1-3), same 11 crossings.
sp {missionaries-cannibals*elaborate*flags
   (state <s> ^superstate nil ^name missionaries-cannibals)
-->
   (<s> ^flag-override <f>)
   (<f> ^mea-operator-selection true ^iterative-step tie-impasse)
}

## World elaboration: a bank with no one on it is empty.
sp {missionaries-cannibals*elaborate*world*empty
   (state <s> ^world <w>)
   (<w> ^objects.object <b>)
   (<b> ^type bank ^missionaries 0 ^cannibals 0)
-->
   (<b> ^empty true)
}

## Achievement of object-property desireds (supplied by the task).
sp {missionaries-cannibals*elaborate*state*achieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{ <> object-handle <a> } <v>)
   (<w> ^anchored-world true ^objects.object <ob>)
   (<ob> ^object-handle <h> ^<a> <v>)
-->
   (<ds> ^achieved <d>)
}

sp {missionaries-cannibals*elaborate*state*unachieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{ <> object-handle <a> } <v>)
   (<w> ^anchored-world true)
  -{(<w> ^objects.object <ob>)
    (<ob> ^object-handle <h> ^<a> <v>)}
-->
   (<ds> ^unachieved <d>)
}
"""]
for n,m,c in LOADS:
    R.append(f"""
sp {{missionaries-cannibals*propose*{n}*mea
   (state <s> ^problem-space.name missionaries-cannibals ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <from> <to>)
   (<boat> ^type boat ^side <fh>)
   (<from> ^type bank ^object-handle <fh> ^missionaries <fm> ^cannibals <fc>)
   (<to> ^type bank ^object-handle {{ <th> <> <fh> }} ^missionaries <tm> ^cannibals <tc>)
   (<ds> ^desired <sd> ^unachieved <sd>)
-->
   (<s> ^operator <op> +)
   (<op> ^name {n} ^task-operator true ^action-handle {n} ^super-desired <sd> ^argument1 <from> ^argument2 <to> ^argument-count 2 ^desireds <pre>
         ^m-load {m} ^c-load {c}
         ^from-m (- <fm> {m}) ^from-c (- <fc> {c}) ^to-m (+ <tm> {m}) ^to-c (+ <tc> {c})
         ^result (concat <fh> |-| (- <fm> {m}) |-| (- <fc> {c}) |-| <th> |-| (+ <tm> {m}) |-| (+ <tc> {c}) |-| <th>))
   (<pre> ^desired-count 0)
}}
""")
R.append("""
## Reject loads that are impossible, unsafe, or return to a visited situation.
sp {missionaries-cannibals*reject*crossing*not-enough-people
   (state <s> ^problem-space.name missionaries-cannibals ^operator <op> +)
   (<op> ^task-operator true ^<< from-m from-c >> < 0)
-->
   (<s> ^operator <op> -)
}

sp {missionaries-cannibals*reject*crossing*unsafe-from-bank
   (state <s> ^problem-space.name missionaries-cannibals ^operator <op> +)
   (<op> ^task-operator true ^from-m { <m> > 0 } ^from-c > <m>)
-->
   (<s> ^operator <op> -)
}

sp {missionaries-cannibals*reject*crossing*unsafe-to-bank
   (state <s> ^problem-space.name missionaries-cannibals ^operator <op> +)
   (<op> ^task-operator true ^to-m { <m> > 0 } ^to-c > <m>)
-->
   (<s> ^operator <op> -)
}

sp {missionaries-cannibals*reject*crossing*already-visited
   (state <s> ^problem-space.name missionaries-cannibals ^operator <op> + ^world <w>)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^visited <l>)
   (<op> ^task-operator true ^result <l>)
-->
   (<s> ^operator <op> -)
}

## Internal application (look-ahead).
sp {missionaries-cannibals*apply*crossing*internal
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name <n> ^pre-conditions-satisfied true ^m-load <dm> ^c-load <dc> ^result <r>
         ^argument1.object-handle <fh> ^argument2.object-handle <th>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <from> <to> <boat>)
   (<from> ^object-handle <fh> ^missionaries <fm> ^cannibals <fc>)
   (<to> ^object-handle <th> ^missionaries <tm> ^cannibals <tc>)
   (<boat> ^type boat ^side <fh>)
-->
   (log 1 (crlf) |Apply | <n> | internal.|)
   (<from> ^missionaries <fm> - (- <fm> <dm>) ^cannibals <fc> - (- <fc> <dc>))
   (<to> ^missionaries <tm> - (+ <tm> <dm>) ^cannibals <tc> - (+ <tc> <dc>))
   (<boat> ^side <fh> - <th> ^visited <r>)
}

## Effect of a completed external crossing on the real world (once per command).
sp {missionaries-cannibals*apply*crossing*environment-effect
   :o-support
   (state <s> ^superstate nil ^world <w> ^load-table.load <l> ^io.output-link.perform-action <pa>)
   (<pa> ^name <n> ^status complete ^argument1 <fh> ^argument2 <th> -^effect-applied true)
   (<l> ^name <n> ^missionaries <dm> ^cannibals <dc>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <from> <to> <boat>)
   (<from> ^object-handle <fh> ^missionaries <fm> ^cannibals <fc>)
   (<to> ^object-handle <th> ^missionaries <tm> ^cannibals <tc>)
   (<boat> ^type boat ^side <fh>)
-->
   (<from> ^missionaries <fm> - (- <fm> <dm>) ^cannibals <fc> - (- <fc> <dc>))
   (<to> ^missionaries <tm> - (+ <tm> <dm>) ^cannibals <tc> - (+ <tc> <dc>))
   (<boat> ^side <fh> - <th> ^visited (concat <fh> |-| (- <fm> <dm>) |-| (- <fc> <dc>) |-| <th> |-| (+ <tm> <dm>) |-| (+ <tc> <dc>) |-| <th>))
   (<pa> ^effect-applied true)
   (write |Crossing: | <n> | from | <fh> | to | <th> |.   | <fh> | bank now | (- <fm> <dm>) |M | (- <fc> <dc>) |C, | <th> | bank now | (+ <tm> <dm>) |M | (+ <tc> <dc>) |C| (crlf))
}
""")
open("missionaries-cannibals-rules.soar","w").write(convpass.apply("".join(R)))
open("missionaries-cannibals.soar","w").write("""# Loads the shared Soar library from the repository (Soar/soar-library), then the task rules.
# The path assumes this folder is unpacked in its place in Soar-Lean-Agents; set SOAR_LIBRARY
# when running gen.py to write another path.
pushd "%s"
source soar-library.soar
popd
source missionaries-cannibals-rules.soar
""" % os.environ.get("SOAR_LIBRARY", "../../../Soar/soar-library"))
