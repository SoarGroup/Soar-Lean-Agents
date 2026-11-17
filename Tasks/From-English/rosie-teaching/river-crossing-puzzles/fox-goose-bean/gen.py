"""Fox, goose and beans (goose-fox-beans) from the Rosie teaching script (english-input.txt), world conventions.
usage: python3 gen.py [WORLD]   WORLD defaults to init-fox.world; another world writes the same rules with that state as the
initial world, for the state checks (out: goose-fox-beans-rules-<world>.soar)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import rosie_gen as R
os.chdir(os.path.dirname(os.path.abspath(__file__)))
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-fox.world'

DESC = """## Fox, goose and beans (goose-fox-beans), generated from the Rosie teaching script (english-input.txt) under the world conventions.
##
## Instructor statements used (numbers as in english-input.txt):
##   4. The name of an action is ferry-one.
##   5. You can move the boat and a block on the current bank onto the opposite bank.
##   6. If an object is below a boat then it is current.
##   7. If a location is not below a boat then it is opposite.
##   8. You can move a boat onto the opposite bank.
##  10. If a red block is on an opposite bank and a yellow block is on the opposite bank then you lose.
##  13. If a green block is on an opposite bank and a yellow block is on the opposite bank then you lose.
##  18. The goal is that all the blocks are on a destination bank.
## World: init-fox.world (bank-1; bank-2 named destination; red, yellow and green blocks and the boat, all on bank-1).
##
## Translation (rosie-language.md gives the general reading; the assumption ledger is in README.md):
##   - Operators ferry-one (statement 5; argument1 = the block, argument2 = the opposite bank) and cross (statement 8, not
##     named in the dialog; argument1 = the boat, argument2 = the opposite bank). Moving an object onto a bank replaces its
##     on and below relations; the block and the boat both move in ferry-one.
##   - current (statement 6) is expanded in place: a bank is current when it is below the boat.
##   - opposite (statement 7) tests absence and decides legality, so it is a maintained one-argument relation: each crossing
##     moves opposite from the destination bank to the bank the boat left.
##   - The two losing conditions (statements 10, 13) mark the state with ^failure; look-ahead returns it as a failure.
##   - The goal (statement 18) is ^goal-met true on the task object when no block is on a bank other than the destination
##     bank (A-F3: the boat is a block).
"""

def handle(i, a):
    if a['category'] == 'location': return f"bank-{i}"
    return a.get('shape', a.get('color')) + f"-{i}"   # boat-6; red-3, yellow-4, green-5

def concept(name, objs, rels):
    if name == 'opposite':   # statement 7: a location not below a boat
        boats = {i for i, a in objs.items() if a.get('shape') == 'boat'}
        under_boat = {a for a, b in rels.get('below', []) if b in boats}
        return {i for i, a in objs.items() if a['category'] == 'location' and i not in under_boat}
    raise KeyError(name)

GOAL_T = """## Goal (statement 18): all the blocks are on a destination bank. "All the blocks" is expanded over the blocks of the world
## file (A-F4), so the test is positive: each block's on relation names the bank called destination.
sp {goose-fox-beans*elaborate*goal*all-crossed
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <dest> %OBJS%)
   (<t> ^type task)
   (<dest> ^type location ^name destination)
%CONDS%
-->
   (<t> ^goal-met true)
}
"""
t = R.RosieTask('goose-fox-beans', DESC, WORLD, handle, maintained=['opposite'], concept=concept)

blocks = [h for i, a in sorted(t.objs.items()) for h in [t.h[i]] if a['category'] == 'block']
GOAL = GOAL_T.replace('%OBJS%', ' '.join(f'<b-{h}>' for h in blocks)).replace('%CONDS%', '\n'.join(
    f'   (<b-{h}> ^object-handle {h})\n   (<w> ^on <on-{h}>)\n   (<on-{h}> ^argument1 <b-{h}> ^argument2 <dest>)' for h in blocks))

# Statement 5: the boat and a block on the current bank onto the opposite bank (A-F1: the block is not the boat).
t.add(t.t.propose('ferry-one', '''   (<objs> ^object <boat> <x> <cur> <opp>)
   (<boat> ^type block ^shape boat ^object-handle <bh>)
   (<x> ^type block ^object-handle { <> <bh> <xh> })
   (<cur> ^type location)
   (<opp> ^type location ^object-handle <oh>)
   (<w> ^below <bb> ^on <xo> ^opposite <op-r>)
   (<bb> ^argument1 <cur> ^argument2 <boat>)
   (<xo> ^argument1 <x> ^argument2 <cur>)
   (<op-r> ^argument1 <opp>)''', ['<x>', '<opp>']))
# Statement 8: a boat onto the opposite bank.
t.add(t.t.propose('cross', '''   (<objs> ^object <boat> <opp>)
   (<boat> ^type block ^shape boat ^object-handle <bh>)
   (<opp> ^type location ^object-handle <oh>)
   (<w> ^opposite <op-r>)
   (<op-r> ^argument1 <opp>)''', ['<boat>', '<opp>']))

# Effects. Moving object X onto bank D: X's on relation and the bank's below relation now name D. The boat always moves,
# so opposite moves from D to the bank the boat left.
BOAT = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <d>)
   (<boat> ^type block ^shape boat)
   (<d> ^object-handle <dh>)
   (<w> ^on <rb> ^below <bb> ^opposite <od>)
   (<rb> ^argument1 <boat> ^argument2 <old>)
   (<bb> ^argument1 <old> ^argument2 <boat>)
   (<od> ^argument1 <d>)'''
BOAT_RHS = '''(<rb> ^argument2 <old> - <d>)
   (<bb> ^argument1 <old> - <d>)
   (<w> ^opposite <od> - <no>)
   (<no> ^argument1 <old>)'''
BLOCK = '''   (<objs> ^object <x>)
   (<x> ^object-handle <xh>)
   (<w> ^on <rx> ^below <bx>)
   (<rx> ^argument1 <x> ^argument2 <old>)
   (<bx> ^argument1 <old> ^argument2 <x>)'''
BLOCK_RHS = '''(<rx> ^argument2 <old> - <d>)
   (<bx> ^argument1 <old> - <d>)'''
t.add(f'''
## Effect of ferry-one (look-ahead): the boat and the block are now on the destination bank.
sp {{goose-fox-beans*apply*ferry-one*internal
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name ferry-one ^pre-conditions-satisfied true ^argument1.object-handle <xh> ^argument2.object-handle <dh>)
{BOAT}
{BLOCK}
-->
   {BOAT_RHS}
   {BLOCK_RHS}
}}

sp {{goose-fox-beans*apply*ferry-one*environment-effect
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name ferry-one ^status complete ^argument1 <xh> ^argument2 <dh> -^effect-applied true)
{BOAT}
{BLOCK}
-->
   {BOAT_RHS}
   {BLOCK_RHS}
   (<pa> ^effect-applied true)
   (write |Ferry boat and | <xh> | onto | <dh> (crlf))
}}

## Effect of cross (look-ahead): the boat alone is now on the destination bank.
sp {{goose-fox-beans*apply*cross*internal
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name cross ^pre-conditions-satisfied true ^argument2.object-handle <dh>)
{BOAT}
-->
   {BOAT_RHS}
}}

sp {{goose-fox-beans*apply*cross*environment-effect
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name cross ^status complete ^argument2 <dh> -^effect-applied true)
{BOAT}
-->
   {BOAT_RHS}
   (<pa> ^effect-applied true)
   (write |Cross with the boat alone onto | <dh> (crlf))
}}

## Failure (statements 10 and 13): a red and a yellow block, or a green and a yellow block, are on the opposite bank.
sp {{goose-fox-beans*elaborate*failure*red-and-yellow-on-opposite-bank
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^opposite <or> ^on <r1> <r2>)
   (<objs> ^object <b1> <b2>)
   (<b1> ^type block ^color red)
   (<b2> ^type block ^color yellow)
   (<or> ^argument1 <bank>)
   (<r1> ^argument1 <b1> ^argument2 <bank>)
   (<r2> ^argument1 <b2> ^argument2 <bank>)
-->
   (<s> ^failure <ds>)
}}

sp {{goose-fox-beans*elaborate*failure*green-and-yellow-on-opposite-bank
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^opposite <or> ^on <r1> <r2>)
   (<objs> ^object <b1> <b2>)
   (<b1> ^type block ^color green)
   (<b2> ^type block ^color yellow)
   (<or> ^argument1 <bank>)
   (<r1> ^argument1 <b1> ^argument2 <bank>)
   (<r2> ^argument1 <b2> ^argument2 <bank>)
-->
   (<s> ^failure <ds>)
}}

''' + GOAL + '''
''')

out = 'goose-fox-beans-rules.soar' if WORLD == 'init-fox.world' else f'goose-fox-beans-rules-{WORLD[:-6]}.soar'
t.write(out)
open('goose-fox-beans.soar', 'w').write(R.loader('goose-fox-beans.soar', 'goose-fox-beans-rules.soar', 5))
print('wrote', out)
