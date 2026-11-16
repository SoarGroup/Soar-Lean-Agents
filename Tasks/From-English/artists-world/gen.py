import os
import sys, itertools
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
STEP = sys.argv[2] if len(sys.argv) > 2 else 'tie-impasse'   # or: operator
DESC = """## Artists and managers river crossing, written to the world conventions
## (agent-world, selection-world, selection-iterative-deepening; no-environment mode, lib/world2).
##
## Description (as given):
##   The Setup: A certain number of artists (often three) and their respective personal managers
##   need to cross a river using a small boat.
##   The Constraints:
##   * The boat can only hold a maximum of two people at a time.
##   * A boat cannot cross empty; someone must row it back and forth.
##   * The Twist: The managers are fiercely protective and competitive. If an artist is left on
##     either side of the riverbank with other managers, their own manager must also be present.
##     If an artist is left with other managers without their own manager to protect them, the
##     other managers will immediately try to poach or mistreat that artist.
##   The Goal: Figure out a sequential order of boat trips to get all artists and all managers
##   safely across the river without ever leaving an artist unprotected.
##
## Choices where the description is open:
##   - The constraint is checked on both banks after every crossing (the boat's occupants are
##     counted on the bank they arrive at); the boat itself is not constrained.
##   - Look-ahead does not return to a situation already visited on the simulated path. A real
##     crossing back to a situation already visited for real is only a last resort (worst
##     preference), so the agent prefers progress but can still back out of a dead end.
##   - Number of pairs: %d (regenerate with: python3 gen.py <n>).
##
## World: banks left/right; boat (^side; ^visited labels in look-ahead); artist-i
## (^manager-handle manager-i) and manager-i, each with ^side. Goal: one desired, the left bank ^empty true.
## Task operator cross: ^moves = 1 or 2 people on the boat's side (argument1, argument2).
## A crossing is rejected if it leaves an artist with another manager and without their own,
## or, in look-ahead, if it returns to a situation already on the simulated path. Ties are
## settled by look-ahead (iterative deepening, limit raised to 4N-1 tie levels).
## No external environment: the top state has ^environment none and crossings update ^world
## as they are applied.
""" % N
MAXD = int(__import__('os').environ.get('MAXD', max(7, 4 * N - 1)))
RAISE = f"""## The shortest crossing sequence (11 crossings for three pairs) is longer than the library's
## default look-ahead limit of 7 tie levels, so this task raises the limit for its top-level
## selection to 4N-1.
sp {{artists*propose*raise-max-evaluation-depth
   (state <s> ^name selection ^top-selection true ^superstate.name artists ^max-evaluation-depth 7)
-->
   (<s> ^operator <o> + >)
   (<o> ^name raise-max-evaluation-depth)
}}

sp {{artists*prefer*raise-max-evaluation-depth
   (state <s> ^name selection ^operator <o> + ^operator {{ <x> <> <o> }} +)
   (<o> ^name raise-max-evaluation-depth)
-->
   (<s> ^operator <o> > <x>)
}}

sp {{artists*apply*raise-max-evaluation-depth
   (state <s> ^operator.name raise-max-evaluation-depth ^max-evaluation-depth 7)
-->
   (<s> ^max-evaluation-depth 7 - {MAXD})
}}

"""
people = [f'artist-{i}' for i in range(1, N + 1)] + [f'manager-{i}' for i in range(1, N + 1)]
start_label = '.'.join(['left'] * len(people)) + '-left'
R = [DESC]
objs = ['<left>', '<right>', '<boat>'] + [f'<{p}>' for p in people]
init = [f"   (<left> ^object-handle left ^anchored true ^type bank)",
        f"   (<right> ^object-handle right ^anchored true ^type bank)",
        f"   (<boat> ^object-handle boat ^anchored true ^type boat ^side left)"]
for k, p in enumerate(people, 1):
    if p.startswith('artist'):
        init.append(f"   (<{p}> ^object-handle {p} ^anchored true ^type person ^role artist ^number {k} ^side left ^manager-handle manager-{p.split('-')[1]})")
    else:
        init.append(f"   (<{p}> ^object-handle {p} ^anchored true ^type person ^role manager ^number {k} ^side left)")
R.append(f"""
sp {{artists*propose*initialize-artists
   (state <s> ^superstate nil ^world <w> -^name)
-->
   (<s> ^operator <o> + >)
   (<o> ^name initialize-artists ^task-operator false)
}}

## propose*initialize-agent-world tests only -^name, so it stays proposed after it has built
## ^world and ties with initialize-artists; a look-ahead can then apply it a second time and
## give the top state two worlds. Once ^world exists it is rejected here (library finding).
sp {{artists*reject*initialize-agent-world*world-exists
   (state <s> ^superstate nil ^world <w> ^operator <o> +)
   (<o> ^name initialize-agent-world)
-->
   (<s> ^operator <o> -)
}}

sp {{artists*apply*initialize-artists
   (state <s> ^operator.name initialize-artists ^world <w>)
   (<w> ^objects <objs>)
-->
   (<s> ^name artists ^desireds <ds>)
   (<objs> ^object {' '.join(objs)})
""" + "\n".join(init) + f"""
   (<ds> ^desired-count 1 ^desired <d1>)
   (<d1> ^object <d1-o>)
   (<d1-o> ^object-handle left ^empty true)
   (write |{N} artists and {N} managers on the left bank; the boat holds two.| (crlf))
}}

sp {{artists*elaborate*top-state*environment-none
   (state <s> ^superstate nil ^name artists)
-->
   (<s> ^environment none)
}}

sp {{artists*elaborate*problem-space
   (state <s> ^name artists)
-->
   (<s> ^problem-space <p>)
   (<p> ^name artists ^agent-world true ^default-state-copy no ^default-operator-copy no ^default-desired-copy no ^dont-copy top-state
        ^dont-copy-object-attribute empty ^ground-object-attribute side)
}}

sp {{artists*elaborate*flags
   (state <s> ^superstate nil ^name artists)
-->
   (<s> ^flag-override <f>)
   (<f> ^mea-operator-selection true ^iterative-step {STEP})
}}

## A bank with nobody on it is empty.
sp {{artists*elaborate*world*bank*empty
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <b>)
   (<b> ^type bank ^object-handle <h>)
  -{{(<objs> ^object <p>)
    (<p> ^type person ^side <h>)}}
-->
   (<b> ^empty true)
}}

## Achievement of object-property desireds (supplied by the task).
sp {{artists*elaborate*state*achieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{{ <> object-handle <a> }} <v>)
   (<w> ^anchored-world true ^objects.object <ob>)
   (<ob> ^object-handle <h> ^<a> <v>)
-->
   (<ds> ^achieved <d>)
}}

sp {{artists*elaborate*state*unachieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{{ <> object-handle <a> }} <v>)
   (<w> ^anchored-world true)
  -{{(<w> ^objects.object <ob>)
    (<ob> ^object-handle <h> ^<a> <v>)}}
-->
   (<ds> ^unachieved <d>)
}}

### cross: one or two people on the boat's side row to the other bank

sp {{artists*propose*cross*one*mea
   (state <s> ^problem-space.name artists ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <p> <to>)
   (<boat> ^type boat ^side <fh>)
   (<p> ^type person ^side <fh> ^object-handle <ph>)
   (<to> ^type bank ^object-handle {{ <th> <> <fh> }})
   (<ds> ^desired <sd> ^unachieved <sd>)
-->
   (<s> ^operator <op> +)
   (<op> ^name cross ^task-operator true ^action-handle cross ^super-desired <sd> ^argument1 <p> ^argument-count 1
         ^moves <p> ^from <fh> ^to <th> ^text <ph> ^desireds <pre>)
   (<pre> ^desired-count 0)
}}

sp {{artists*propose*cross*two*mea
   (state <s> ^problem-space.name artists ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <p1> <p2> <to>)
   (<boat> ^type boat ^side <fh>)
   (<p1> ^type person ^side <fh> ^number <n1> ^object-handle <h1>)
   (<p2> ^type person ^side <fh> ^number > <n1> ^object-handle <h2>)
   (<to> ^type bank ^object-handle {{ <th> <> <fh> }})
   (<ds> ^desired <sd> ^unachieved <sd>)
-->
   (<s> ^operator <op> +)
   (<op> ^name cross ^task-operator true ^action-handle cross ^super-desired <sd> ^argument1 <p1> ^argument2 <p2> ^argument-count 2
         ^moves <p1> <p2> ^from <fh> ^to <th> ^text (concat <h1> | and | <h2>) ^desireds <pre>)
   (<pre> ^desired-count 0)
}}

## Where each person would be after the crossing. The predictions are kept on the state, not on
## the operator: in look-ahead the same operator is acceptable both at the real state and in the
## evaluation copy, whose worlds differ, and structure built on a superstate's operator from a
## substate becomes a result of the substate.
sp {{artists*elaborate*operator*prediction
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^name cross)
-->
   (<s> ^prediction <pr>)
   (<pr> ^operator <op>)
}}

sp {{artists*elaborate*operator*result*moved
   (state <s> ^operator <op> + ^prediction <pr>)
   (<pr> ^operator <op>)
   (<op> ^name cross ^to <th> ^moves.object-handle <h>)
-->
   (<pr> ^result <r>)
   (<r> ^handle <h> ^side <th>)
}}

sp {{artists*elaborate*operator*result*stays
   (state <s> ^operator <op> + ^prediction <pr> ^world <w>)
   (<pr> ^operator <op>)
   (<op> ^name cross)
   (<w> ^anchored-world true ^objects.object <p>)
   (<p> ^type person ^object-handle <h> ^side <side>)
  -(<op> ^moves.object-handle <h>)
-->
   (<pr> ^result <r>)
   (<r> ^handle <h> ^side <side>)
}}

sp {{artists*elaborate*operator*result-label
   (state <s> ^operator <op> + ^prediction <pr>)
   (<op> ^name cross ^to <th>)
   (<pr> ^operator <op>
""" + "\n".join(f"         ^result <r{k}>" for k in range(len(people))) + ")\n" +
"\n".join(f"   (<r{k}> ^handle {p} ^side <s{k}>)" for k, p in enumerate(people)) + f"""
-->
   (<pr> ^label (concat """ + " |.| ".join(f"<s{k}>" for k in range(len(people))) + f""" |-| <th>))
}}

## Reject a crossing that leaves an artist with another manager and without their own.
sp {{artists*reject*cross*artist-unprotected
   (state <s> ^operator <op> + ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <a>)
   (<a> ^role artist ^object-handle <ah> ^manager-handle <own>)
   (<op> ^name cross)
   (<s> ^prediction <pr>)
   (<pr> ^operator <op> ^result <ra> <rm> <ro>)
   (<ra> ^handle <ah> ^side <bank>)
   (<rm> ^handle {{ <mh> <> <own> }} ^side <bank>)
   (<ro> ^handle <own> ^side <> <bank>)
   (<objs> ^object <m>)
   (<m> ^role manager ^object-handle <mh>)
-->
   (<s> ^operator <op> -)
}}

## In look-ahead, reject a crossing that returns to a situation already visited on the simulated
## path.
sp {{artists*reject*cross*visited
   (state <s> ^operator <op> + ^world <w> -^superstate nil)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^visited <l>)
   (<op> ^name cross)
   (<s> ^prediction <pr>)
   (<pr> ^operator <op> ^label <l>)
-->
   (<s> ^operator <op> -)
}}

## Application (internal; with ^environment none it also applies at the top state).
sp {{artists*apply*cross*person
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^name cross ^pre-conditions-satisfied true ^from <fh> ^to <th> ^moves.object-handle <h>)
   (<w> ^anchored-world true ^objects.object <p>)
   (<p> ^object-handle <h> ^side <fh>)
-->
   (<p> ^side <fh> - <th>)
}}

## The label of the situation as it stands; recorded as visited when it is left.
sp {{artists*elaborate*state*situation-label
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat>)
   (<boat> ^type boat ^side <b>)
""" + "\n".join(f"   (<objs> ^object <q{k}>)\n   (<q{k}> ^object-handle {p} ^side <s{k}>)" for k, p in enumerate(people)) + f"""
-->
   (<s> ^situation-label (concat """ + " |.| ".join(f"<s{k}>" for k in range(len(people))) + f""" |-| <b>))
}}

sp {{artists*apply*cross*boat
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^name cross ^pre-conditions-satisfied true ^from <fh> ^to <th>)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^side <fh>)
-->
   (<boat> ^side <fh> - <th>)
}}

sp {{artists*apply*cross*record-visited*look-ahead
   (state <s> ^operator <op> ^internal-actions true ^world <w> ^situation-label <l> -^superstate nil)
   (<op> ^name cross ^pre-conditions-satisfied true ^from <fh>)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^side <fh>)
-->
   (<boat> ^visited <l>)
}}

sp {{artists*apply*cross*record-visited*real
   (state <s> ^operator <op> ^world <w> ^situation-label <l> ^superstate nil)
   (<op> ^name cross ^pre-conditions-satisfied true ^from <fh>)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^side <fh>)
-->
   (<s> ^real-visited <l>)
}}

## For real crossings, returning to a situation already visited is a last resort.
sp {{artists*prefer*cross*real-visited*worst
   (state <s> ^superstate nil ^operator <op> + ^real-visited <l> ^prediction <pr>)
   (<op> ^name cross)
   (<pr> ^operator <op> ^label <l>)
-->
   (<s> ^operator <op> <)
}}

""" + (RAISE if MAXD > 7 else "") + f"""## Report real crossings only (the top state); look-ahead crossings are not printed.
sp {{artists*apply*cross*report
   (state <s> ^superstate nil ^operator <op> ^world <w>)
   (<op> ^name cross ^pre-conditions-satisfied true ^from <fh> ^to <th> ^text <t>)
   (<w> ^anchored-world true ^objects.object <boat>)
   (<boat> ^type boat ^side <fh>)
-->
   (write |Crossing: | <t> | row from the | <fh> | bank to the | <th> | bank.| (crlf))
}}

## Done: everyone is across.
sp {{artists*elaborate*top-state*done
   (state <s> ^superstate nil ^name artists ^world <w>)
   (<w> ^anchored-world true ^objects.object <left>)
   (<left> ^object-handle left ^empty true)
-->
   (write |Everyone is across; no artist was ever left unprotected.| (crlf) |TASK-RESULT: success| (crlf))
   (halt)
}}
""")
open('artists-rules.soar', 'w').write(''.join(R))
open('artists.soar', 'w').write("""# Loads the shared Soar library from the repository (Soar/soar-library), then the task rules.
# The path assumes this folder is unpacked in its place in Soar-Lean-Agents; set SOAR_LIBRARY
# when running gen.py to write another path.
pushd "%s"
source soar-library.soar
popd
source artists-rules.soar
""" % os.environ.get('SOAR_LIBRARY', '../../../Soar/soar-library'))
