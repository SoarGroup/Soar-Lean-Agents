import os
"""Generate zebra-rules.soar: the five-houses logic puzzle under the world conventions
(lib/world2, no-environment mode).  The clues are data; the rules are generic."""

DESC = r"""## The five-houses puzzle (world conventions, lib/world2, no environment)
##
## Original English:
##   There are five houses in a row, numbered 1 to 5 from left to right. Each house is painted a
##   different color. In each house lives a person of a different nationality. Each of the five
##   owners drinks a certain beverage, smokes a certain brand of cigar, and keeps a certain pet.
##   No two owners have the same pet, smoke the same cigar, drink the same beverage, or share a
##   nationality. Questions: 1. Who drinks water? 2. Who owns the zebra?
##   Clues: 1 There are exactly five houses. 2 The Englishman lives in the red house. 3 The Swede
##   keeps dogs as pets. 4 The Dane drinks tea. 5 The green house is immediately to the left of
##   the white house. 6 The green house's owner drinks coffee. 7 The person who smokes Pall Mall
##   rears birds. 8 The owner of the yellow house smokes Dunhill. 9 The man living in the center
##   house (House 3) drinks milk. 10 The Norwegian lives in the first house (House 1). 11 The man
##   who smokes Blends lives next to the one who keeps cats. 12 The man who keeps horses lives
##   next to the man who smokes Dunhill. 13 The owner who smokes BlueMaster drinks beer. 14 The
##   German smokes Prince. 15 The Norwegian lives next to the blue house.
##   Show the elimination matrix or deductions; answer who drinks water and who owns the zebra.
##
## Encoding:
##   World: house-1..5 (^position, ^left/^right neighbour handles, ^candidate for every value
##   still possible), the 25 values (^group: their category; selection-world's look-ahead copy
##   does not copy an attribute named ^category), the 5 categories, the clues as data
##   (relation same | position | left-of | next-to), and the puzzle (desired: ^solved true).
##   Reasoning is candidate elimination (the elimination matrix). Task operator eliminate removes
##   one candidate for a stated reason: a clue, a naked single (a house has one value left in a
##   category) or a hidden single (a value has one house left). When no elimination applies, the
##   agent prints the matrix and branches on the first open cell (task operator assign); the
##   branches tie and look-ahead (selection-world, iterative deepening) settles the tie: a branch
##   that empties a cell or a value is a failure, one that solves the puzzle a success.
##   Clue 1 is the structure itself (five houses).
"""

CATS = [('color', ['red', 'green', 'white', 'yellow', 'blue']),
        ('nationality', ['English', 'Swede', 'Dane', 'Norwegian', 'German']),
        ('drink', ['tea', 'coffee', 'milk', 'beer', 'water']),
        ('smoke', ['PallMall', 'Dunhill', 'Blends', 'BlueMaster', 'Prince']),
        ('pet', ['dogs', 'birds', 'cats', 'horses', 'zebra'])]
LABEL = {'English': 'Englishman', 'Swede': 'Swede', 'Dane': 'Dane',
         'Norwegian': 'Norwegian', 'German': 'German'}
# (number, relation, x, y-or-position, text)
CLUES = [(2, 'same', 'English', 'red', 'The Englishman lives in the red house'),
         (3, 'same', 'Swede', 'dogs', 'The Swede keeps dogs'),
         (4, 'same', 'Dane', 'tea', 'The Dane drinks tea'),
         (5, 'left-of', 'green', 'white', 'The green house is immediately to the left of the white house'),
         (6, 'same', 'green', 'coffee', 'The green house owner drinks coffee'),
         (7, 'same', 'PallMall', 'birds', 'The Pall Mall smoker rears birds'),
         (8, 'same', 'yellow', 'Dunhill', 'The yellow house owner smokes Dunhill'),
         (9, 'position', 'milk', 3, 'The man in house 3 drinks milk'),
         (10, 'position', 'Norwegian', 1, 'The Norwegian lives in house 1'),
         (11, 'next-to', 'Blends', 'cats', 'The Blends smoker lives next to the cat keeper'),
         (12, 'next-to', 'horses', 'Dunhill', 'The horse keeper lives next to the Dunhill smoker'),
         (13, 'same', 'BlueMaster', 'beer', 'The BlueMaster smoker drinks beer'),
         (14, 'same', 'German', 'Prince', 'The German smokes Prince'),
         (15, 'next-to', 'Norwegian', 'blue', 'The Norwegian lives next to the blue house')]
VALUES = [(v, c) for c, vs in CATS for v in vs]

R = [DESC]
# ---------------------------------------------------------------- initialization
objs, init = ['<puzzle>'], ["   (<puzzle> ^object-handle puzzle ^anchored true ^type puzzle)"]
for k in range(1, 6):
    nb = (f" ^left house-{k-1}" if k > 1 else "") + (f" ^right house-{k+1}" if k < 5 else "")
    cands = ' '.join(f'|{v}|' for v, _ in VALUES)
    objs.append(f'<h{k}>')
    init.append(f"   (<h{k}> ^object-handle house-{k} ^anchored true ^type house ^position {k}{nb}\n           ^candidate {cands})")
for i, (c, vs) in enumerate(CATS, 1):
    objs.append(f'<c-{c}>')
    init.append(f"   (<c-{c}> ^object-handle category-{c} ^anchored true ^type category ^name {c} ^order {i})")
    for v in vs:
        objs.append(f'<v-{v}>')
        lab = f" ^label |{LABEL[v]}|" if v in LABEL else ""
        init.append(f"   (<v-{v}> ^object-handle value-{v} ^anchored true ^type value ^name |{v}| ^group {c}{lab})")
for n, rel, x, y, t in CLUES:
    objs.append(f'<k{n}>')
    yy = f"^position {y}" if rel == 'position' else f"^y |{y}|"
    init.append(f"   (<k{n}> ^object-handle clue-{n} ^anchored true ^type clue ^number {n} ^relation {rel} ^x |{x}| {yy} ^text |{t}|)")

R.append(f"""
sp {{zebra*propose*initialize-zebra
   (state <s> ^superstate nil ^world <w> -^name)
-->
   (<s> ^operator <o> + >)
   (<o> ^name initialize-zebra ^task-operator false)
}}

## propose*initialize-agent-world tests only -^name, so it stays proposed after it has built
## ^world; reject it once ^world exists (library finding).
sp {{zebra*reject*initialize-agent-world*world-exists
   (state <s> ^superstate nil ^world <w> ^operator <o> +)
   (<o> ^name initialize-agent-world)
-->
   (<s> ^operator <o> -)
}}

sp {{zebra*apply*initialize-zebra
   (state <s> ^operator.name initialize-zebra ^world <w>)
   (<w> ^objects <objs>)
-->
   (<s> ^name zebra ^desireds <ds>)
   (<objs> ^object {' '.join(objs)})
""" + "\n".join(init) + """
   (<ds> ^desired-count 1 ^desired <d1>)
   (<d1> ^object <d1-o>)
   (<d1-o> ^object-handle puzzle ^solved true)
   (write |Five houses; every house starts with all 25 values as candidates.| (crlf) |Deductions:| (crlf))
}

sp {zebra*elaborate*top-state*environment-none
   (state <s> ^superstate nil ^name zebra)
-->
   (<s> ^environment none)
}

sp {zebra*elaborate*problem-space
   (state <s> ^name zebra)
-->
   (<s> ^problem-space <p>)
   (<p> ^name zebra ^agent-world true ^default-state-copy no ^default-operator-copy no ^default-desired-copy no ^dont-copy top-state)
}

sp {zebra*elaborate*flags
   (state <s> ^superstate nil ^name zebra)
-->
   (<s> ^flag-override <f>)
   (<f> ^mea-operator-selection true ^iterative-step tie-impasse)
}

## Achievement of object-property desireds (supplied by the task).
sp {zebra*elaborate*state*achieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{ <> object-handle <a> } <v>)
   (<w> ^anchored-world true ^objects.object <ob>)
   (<ob> ^object-handle <h> ^<a> <v>)
-->
   (<ds> ^achieved <d>)
}

sp {zebra*elaborate*state*unachieved*object-property
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

########################################################################
## The matrix: derived facts on the state (re-derived in every look-ahead copy)
########################################################################

## A house has exactly one value left in a category.
sp {zebra*elaborate*single
   (state <s> ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <vo>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <v>)
   (<vo> ^type value ^name <v> ^group <c>)
  -{(<h> ^candidate { <v2> <> <v> })
    (<objs> ^object <vo2>)
    (<vo2> ^type value ^name <v2> ^group <c>)}
-->
   (<s> ^single <x>)
   (<x> ^house-handle <hh> ^position <p> ^group <c> ^value <v>)
}

## A cell (house, category) not yet down to one value.
sp {zebra*elaborate*open-cell
   (state <s> ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <co>)
   (<h> ^type house ^object-handle <hh> ^position <p>)
   (<co> ^type category ^name <c> ^order <k>)
  -{(<s> ^single <x>)
    (<x> ^house-handle <hh> ^group <c>)}
-->
   (<s> ^open <o>)
   (<o> ^house-handle <hh> ^position <p> ^group <c> ^rank (+ (* <p> 10) <k>))
}

## The puzzle is solved when no cell holds two values of one category, no cell is empty, and no
## clue still eliminates anything (a full assignment that breaks a clue still has an elimination
## proposed, which would empty a cell).
sp {zebra*elaborate*puzzle*solved
   (state <s> ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <pz>)
   (<pz> ^type puzzle)
  -{(<s> ^operator <x> +)
    (<x> ^name eliminate)}
  -{(<objs> ^object <h> <a> <b>)
    (<h> ^type house ^candidate <v1> { <v2> <> <v1> })
    (<a> ^type value ^name <v1> ^group <c>)
    (<b> ^type value ^name <v2> ^group <c>)}
  -{(<objs> ^object <h2> <co>)
    (<h2> ^type house)
    (<co> ^type category ^name <c2>)
    -{(<h2> ^candidate <v3>)
      (<objs> ^object <vo3>)
      (<vo3> ^type value ^name <v3> ^group <c2>)}}
-->
   (<pz> ^solved true)
}

## Failure (a contradiction): a cell with no value left, or a value with no house left.
sp {zebra*elaborate*failure*empty-cell
   (state <s> ^name zebra ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <co>)
   (<h> ^type house)
   (<co> ^type category ^name <c>)
  -{(<h> ^candidate <v>)
    (<objs> ^object <vo>)
    (<vo> ^type value ^name <v> ^group <c>)}
-->
   (<s> ^failure <ds>)
}

sp {zebra*elaborate*failure*value-without-house
   (state <s> ^name zebra ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <vo>)
   (<vo> ^type value ^name <v>)
  -{(<objs> ^object <h>)
    (<h> ^type house ^candidate <v>)}
-->
   (<s> ^failure <ds>)
}

########################################################################
## eliminate: remove one candidate, for a stated reason (best and indifferent: deductions
## are taken before any branching, in any order)
########################################################################
""")

def elim(name, conds, reason):
    return f"""
sp {{zebra*propose*eliminate*{name}
   (state <s> ^problem-space.name zebra ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)
   (<ds> ^desired <sd> ^unachieved <sd>)
   (<w> ^anchored-world true ^objects <objs>)
{conds}
-->
   (<s> ^operator <op> + = >)
   (<op> ^name eliminate ^task-operator true ^action-handle eliminate ^super-desired <sd>
         ^argument1 <e> ^argument-count 1 ^house-handle <hh> ^value <e>
         ^reason (concat {reason}) ^desireds <pre>)
   (<pre> ^desired-count 0)
}}
"""

R.append(elim('position', """   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation position ^number <n> ^x <e> ^position <q> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position { <p> <> <q> } ^candidate <e>)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |).|"))
R.append(elim('same*x', """   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation same ^number <n> ^x <x> ^y <e> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> -^candidate <x>)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and house | <p> | cannot be | <x> |.|"))
R.append(elim('same*y', """   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation same ^number <n> ^x <e> ^y <y> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> -^candidate <y>)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and house | <p> | cannot be | <y> |.|"))
R.append(elim('left-of*x', """   (<objs> ^object <k> <h> <r>)
   (<k> ^type clue ^relation left-of ^number <n> ^x <e> ^y <y> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> ^right <rh>)
   (<r> ^object-handle <rh> -^candidate <y>)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and the house to its right cannot be | <y> |.|"))
R.append(elim('left-of*x*edge', """   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation left-of ^number <n> ^x <e> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> -^right)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and it has no house to its right.|"))
R.append(elim('left-of*y', """   (<objs> ^object <k> <h> <l>)
   (<k> ^type clue ^relation left-of ^number <n> ^x <x> ^y <e> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> ^left <lh>)
   (<l> ^object-handle <lh> -^candidate <x>)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and the house to its left cannot be | <x> |.|"))
R.append(elim('left-of*y*edge', """   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation left-of ^number <n> ^y <e> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e> -^left)""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and it has no house to its left.|"))
for side, own, other in (('x', 'x', 'y'), ('y', 'y', 'x')):
    R.append(elim(f'next-to*{side}', f"""   (<objs> ^object <k> <h>)
   (<k> ^type clue ^relation next-to ^number <n> ^{own} <e> ^{other} <o> ^text <t>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <e>)
  -{{(<h> ^<< left right >> <nh>)
    (<objs> ^object <nb>)
    (<nb> ^object-handle <nh> ^candidate <o>)}}""",
 "|House | <p> | is not | <e> |: clue | <n> | (| <t> |) and no neighbour of house | <p> | can be | <o> |.|"))
R.append(elim('naked-single', """   (<s> ^single <x>)
   (<x> ^value <e> ^position <q>)
   (<objs> ^object <h>)
   (<h> ^type house ^object-handle <hh> ^position { <p> <> <q> } ^candidate <e>)""",
 "|House | <p> | is not | <e> |: house | <q> | can only be | <e> |.|"))
R.append(elim('hidden-single', """   (<objs> ^object <h> <vo> <vo2>)
   (<h> ^type house ^object-handle <hh> ^position <p> ^candidate <v> { <e> <> <v> })
   (<vo> ^type value ^name <v> ^group <c>)
   (<vo2> ^type value ^name <e> ^group <c>)
  -{(<objs> ^object { <h2> <> <h> })
    (<h2> ^type house ^candidate <v>)}""",
 "|House | <p> | is not | <e> |: only house | <p> | can be | <v> |.|"))

R.append("""
sp {zebra*apply*eliminate
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^name eliminate ^pre-conditions-satisfied true ^house-handle <hh> ^value <e>)
   (<w> ^anchored-world true ^objects.object <h>)
   (<h> ^object-handle <hh> ^candidate <e>)
-->
   (<h> ^candidate <e> -)
}

## Real deductions are printed; look-ahead deductions are not.
sp {zebra*apply*eliminate*report
   (state <s> ^superstate nil ^operator <op> ^world <w>)
   (<op> ^name eliminate ^pre-conditions-satisfied true ^house-handle <hh> ^value <e> ^reason <r>)
   (<w> ^anchored-world true ^objects.object <h>)
   (<h> ^object-handle <hh> ^candidate <e>)
-->
   (write |  | <r> (crlf))
}

########################################################################
## assign: branch on the first open cell when no deduction applies (tie -> look-ahead).
## Proposed only while no eliminate is proposed: in look-ahead the library's
## apply*operator*maintain-operator*preconditions-satisfied makes every operator best, so the
## best preference on eliminate does not hold assign back there.
########################################################################

sp {zebra*propose*assign
   (state <s> ^problem-space.name zebra ^flags.mea-operator-selection true ^world <w> ^desireds <ds> ^open <o>)
   (<ds> ^desired <sd> ^unachieved <sd>)
   (<o> ^house-handle <hh> ^position <p> ^group <c> ^rank <r>)
  -{(<s> ^open <o2>)
    (<o2> ^rank < <r>)}
  -{(<s> ^operator <x> +)
    (<x> ^name eliminate)}
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <vo>)
   (<h> ^object-handle <hh> ^candidate <v>)
   (<vo> ^type value ^name <v> ^group <c>)
-->
   (<s> ^operator <op> +)
   (<op> ^name assign ^task-operator true ^action-handle assign ^super-desired <sd>
         ^argument1 <v> ^argument-count 1 ^house-handle <hh> ^position <p> ^group <c> ^value <v> ^desireds <pre>)
   (<pre> ^desired-count 0)
}

sp {zebra*apply*assign
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^name assign ^pre-conditions-satisfied true ^house-handle <hh> ^group <c> ^value <v>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <vo>)
   (<h> ^object-handle <hh> ^candidate <v> { <e> <> <v> })
   (<vo> ^type value ^name <e> ^group <c>)
-->
   (<h> ^candidate <e> -)
}

sp {zebra*apply*assign*report
   (state <s> ^superstate nil ^operator <op> ^world <w>)
   (<op> ^name assign ^pre-conditions-satisfied true ^house-handle <hh> ^position <p> ^group <c> ^value <v>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <h> <vo>)
   (<h> ^object-handle <hh> ^candidate <v> { <e> <> <v> })
   (<vo> ^type value ^name <e> ^group <c>)
-->
   (write (crlf) |  Branch: house | <p> |, | <c> | = | <v> |. Look-ahead found that this choice leads to a complete solution.| (crlf))
}

########################################################################
## The elimination matrix as text (top state only), printed when deduction stalls and at the end
########################################################################
""")
# mark rules: the text of each candidate slot
for v, c in VALUES:
    R.append(f"""
sp {{zebra*elaborate*mark*{v}*present
   (state <s> ^superstate nil ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects.object <h>)
   (<h> ^type house ^object-handle <hh> ^candidate |{v}|)
-->
   (<s> ^mark <m>)
   (<m> ^house-handle <hh> ^value |{v}| ^text |{v} |)
}}

sp {{zebra*elaborate*mark*{v}*absent
   (state <s> ^superstate nil ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects.object <h>)
   (<h> ^type house ^object-handle <hh> -^candidate |{v}|)
-->
   (<s> ^mark <m>)
   (<m> ^house-handle <hh> ^value |{v}| ^text ||)
}}
""")
conds, parts = [], []
for ci, (c, vs) in enumerate(CATS):
    parts.append(f"|{c:<12}|")
    for k in range(1, 6):
        parts.append(f"| {k}: |")
        for vi, v in enumerate(vs):
            var = f"<t{ci}{k}{vi}>"
            conds.append(f"   (<s> ^mark <m{ci}{k}{vi}>)\n   (<m{ci}{k}{vi}> ^house-handle house-{k} ^value |{v}| ^text {var})")
            parts.append(var)
        parts.append("|; |" if k < 5 else "")
    parts.append("|\n|")
R.append("""
sp {zebra*elaborate*matrix-text
   (state <s> ^superstate nil ^name zebra)
""" + "\n".join(conds) + """
-->
   (<s> ^matrix-text (concat """ + ' '.join(p for p in parts if p) + """))
}

sp {zebra*elaborate*has-open
   (state <s> ^superstate nil ^name zebra ^open <o>)
-->
   (<s> ^has-open true)
}

## Printed once, when no deduction is left. (agent-world makes non-task operators better than
## task operators, so the proposal itself waits until no eliminate is proposed.)
sp {zebra*propose*print-matrix
   (state <s> ^superstate nil ^name zebra ^matrix-text <m> -^matrix-printed true ^has-open true)
  -{(<s> ^operator <x> +)
    (<x> ^name eliminate)}
-->
   (<s> ^operator <op> +)
   (<op> ^name print-matrix ^task-operator false)
}

sp {zebra*prefer*print-matrix*over*assign
   (state <s> ^operator <p> + ^operator <a> +)
   (<p> ^name print-matrix)
   (<a> ^name assign)
-->
   (<s> ^operator <p> > <a>)
}

sp {zebra*apply*print-matrix
   (state <s> ^operator.name print-matrix ^matrix-text <m>)
-->
   (write (crlf) |No clue or single eliminates anything more. Elimination matrix (remaining candidates):| (crlf) <m> (crlf))
   (<s> ^matrix-printed true)
}

########################################################################
## Done: print the solved matrix and the answers
########################################################################

## Report once the puzzle is solved (an operator, so the matrix text has settled).
sp {zebra*propose*report-solution
   (state <s> ^superstate nil ^name zebra ^world <w>)
   (<w> ^anchored-world true ^objects.object <pz>)
   (<pz> ^type puzzle ^solved true)
-->
   (<s> ^operator <op> + >)
   (<op> ^name report-solution ^task-operator false)
}

sp {zebra*prefer*report-solution
   (state <s> ^operator <r> + ^operator { <x> <> <r> } +)
   (<r> ^name report-solution)
-->
   (<s> ^operator <r> > <x>)
}

sp {zebra*apply*report-solution
   (state <s> ^operator.name report-solution ^matrix-text <m> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <pz> <hw> <hz> <nw> <nz>)
   (<pz> ^type puzzle ^solved true)
   (<hw> ^type house ^candidate |water| <nwn> ^position <pw>)
   (<nw> ^type value ^group nationality ^name <nwn> ^label <lw>)
   (<hz> ^type house ^candidate |zebra| <nzn> ^position <pzz>)
   (<nz> ^type value ^group nationality ^name <nzn> ^label <lz>)
-->
   (write (crlf) |Solved. Final matrix:| (crlf) <m> (crlf)
          |1. Who drinks water? The | <lw> | (house | <pw> |).| (crlf)
          |2. Who owns the zebra? The | <lz> | (house | <pzz> |).| (crlf) (crlf)
          |Final answer: the | <lw> | drinks water; the | <lz> | owns the zebra.| (crlf)
          |TASK-RESULT: success| (crlf))
   (halt)
}
""")
open('zebra-rules.soar', 'w').write(''.join(R))
open('zebra.soar', 'w').write("""# Loads the shared Soar library from the repository (Soar/soar-library), then the task rules.
# The path assumes this folder is unpacked in its place in Soar-Lean-Agents; set SOAR_LIBRARY
# when running gen.py to write another path.
pushd "%s"
source soar-library.soar
popd
source zebra-rules.soar
""" % os.environ.get('SOAR_LIBRARY', '../../../Soar/soar-library'))
print('ok')
