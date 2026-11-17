"""Tic-tac-toe from the Rosie teaching script (english-input.txt), world conventions. The environment (run.py) plays blue.
usage: python3 gen.py [WORLD]   WORLD defaults to init-tictactoerc.world; another world writes the same rules with that state
as the initial world, for the state checks (out: tic-tac-toe-rules-<world>.soar)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import rosie_gen as R
os.chdir(os.path.dirname(os.path.abspath(__file__)))
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-tictactoerc.world'

DESC = """## Tic-tac-toe, generated from the Rosie teaching script (english-input.txt) under the world conventions.
##
## Instructor statements used (numbers as in english-input.txt):
##   4. You can move a clear available red block onto a clear location.
##   5. If a block is not on a location then it is available.
##   6. If a location is not below an object then it is clear.
##  10. The name of the goal is three-in-row.
##  12. The goal is that three of the captured locations are in a line.
##  13. If a location is below a red block then it is captured.
##  14. If the locations are linear then they are in a line.
##  16. The name of the failure is opponent-three.
##  18. If three of the occupied locations are in a line then you lose.
##  19. If a location is below a blue block then it is occupied.
## World: init-tictactoerc.world (9 locations with row and column; 3 red and 3 blue blocks in two stacks off the board;
## the predicate-set linear lists the 8 lines).
##
## Translation (rosie-language.md gives the general reading; the assumption ledger is in README.md):
##   - Operator move (statement 4; argument1 = the red block, argument2 = the location). Only red moves are taught.
##   - available (statement 5) and clear (statement 6) test absence and decide legality, so both are maintained one-argument
##     relations, changed by every move (red's own and blue's).
##   - captured (13), occupied (19) and in a line (14) are expanded in place in the goal and failure tests. Each line of the
##     predicate-set linear is a world object of type line with a member relation to each of its three locations.
##   - The goal (12) is ^goal-met true on the task object; the failure (18) marks the state with ^failure.
##   - Opponent (decided by JL, 16 Nov 2026): the environment plays blue. Blue's moves arrive on the input-link
##     (^opponent-move with ^block, ^location, ^number; ^turn; ^blue-moves); input.soar-style rules copy them onto the state
##     (IO-019) and apply them to the world. The agent proposes a move only when the environment says it is red's turn and
##     it has applied every blue move reported (IO-021). Look-ahead covers red's own moves only.
"""

def handle(i, a):
    if a['category'] == 'location': return f"loc-{a['row']}-{a['column']}"
    return f"{a['color']}-{i}"

def concept(name, objs, rels):
    on_loc = {a for a, b in rels.get('on', []) if objs[b]['category'] == 'location'}
    below_first = {a for a, b in rels.get('below', [])}
    if name == 'available':   # statement 5: a block not on a location
        return {i for i, a in objs.items() if a['category'] == 'block' and i not in on_loc}
    if name == 'clear':       # statement 6: not below an object
        return {i for i in objs if i not in below_first}
    raise KeyError(name)

t = R.RosieTask('tic-tac-toe', DESC, WORLD, handle, maintained=['available', 'clear'], concept=concept,
                member_sets=[('linear', 'line')], task_props={'blue-moves-applied': 0})
# (the task object counts the blue moves applied: bookkeeping on a world object, W-SPEC section 2)

t.add(t.t.propose('move', '''   (<objs> ^object <b> <l>)
   (<b> ^type block ^color red ^object-handle <bh>)
   (<l> ^type location ^object-handle <lh>)
   (<w> ^clear <cb> <cl> ^available <ab>)
   (<cb> ^argument1 <b>)
   (<cl> ^argument1 <l>)
   (<ab> ^argument1 <b>)''', ['<b>', '<l>']))

# Moving block B onto location L: B now on L, L below B; L is no longer clear; B is no longer available. If B was on
# another block, that block is clear again; if B was on nothing (the bottom of its stack), a new on relation is made.
BASE = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <l>)
   (<b> ^object-handle <bh>)
   (<l> ^object-handle <lh>)
   (<w> ^clear <cl> ^available <ab>)
   (<cl> ^argument1 <l>)
   (<ab> ^argument1 <b>)'''
FROM_BLOCK = '''   (<w> ^on <r> ^below <bl>)
   (<r> ^argument1 <b> ^argument2 <old>)
   (<bl> ^argument1 <old> ^argument2 <b>)'''
FROM_NOTHING = '''  -{(<w> ^on <r>)
    (<r> ^argument1 <b>)}'''
RHS_COMMON = '''(<w> ^clear <cl> - ^available <ab> -)'''
RHS_FROM_BLOCK = '''(<r> ^argument2 <old> - <l>)
   (<bl> ^argument1 <old> - <l>)
   (<w> ^clear <nc>)
   (<nc> ^argument1 <old>)'''
RHS_FROM_NOTHING = '''(<w> ^on <nr> ^below <nb>)
   (<nr> ^argument1 <b> ^argument2 <l>)
   (<nb> ^argument1 <l> ^argument2 <b>)'''

def effect_rules(tag, trigger, extra_rhs, cond_trigger):
    out = ''
    for case, cond, rhs in (('from-block', FROM_BLOCK, RHS_FROM_BLOCK), ('from-nothing', FROM_NOTHING, RHS_FROM_NOTHING)):
        out += f'''
sp {{tic-tac-toe*apply*{tag}*{case}
{trigger}
{BASE}
{cond}{cond_trigger}
-->
   {RHS_COMMON}
   {rhs}{extra_rhs}
}}
'''
    return out

t.add('## Effect of red\'s move in look-ahead.' + effect_rules('move*internal',
    '''   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name move ^pre-conditions-satisfied true ^argument1.object-handle <bh> ^argument2.object-handle <lh>)''',
    '', ''))
t.add('## Effect of a completed red move on the real world (once per command).' + effect_rules('move*environment-effect',
    '''   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name move ^status complete ^argument1 <bh> ^argument2 <lh> -^effect-applied true)''',
    '''
   (<pa> ^effect-applied true)
   (write |Place | <bh> | on | <lh> (crlf))''', ''))
t.add('''## Input (IO-019): the environment's turn signal and blue's last move, copied onto the top state.
sp {tic-tac-toe*elaborate*input*turn
   (state <s> ^superstate nil ^io.input-link <il>)
   (<il> ^turn <c> ^blue-moves <n>)
-->
   (<s> ^env-turn <c> ^env-blue-moves <n>)
}

sp {tic-tac-toe*elaborate*input*opponent-move
   (state <s> ^superstate nil ^io.input-link.opponent-move <m>)
   (<m> ^block <bh> ^location <lh> ^number <n>)
-->
   (<s> ^opponent-move <om>)
   (<om> ^block <bh> ^location <lh> ^number <n>)
}

sp {tic-tac-toe*elaborate*input*game-over
   (state <s> ^superstate nil ^io.input-link.game-over <r>)
-->
   (<s> ^env-game-over <r>)
}

## Red may act only when the environment says it is red's turn and every blue move reported has been applied (IO-021).
sp {tic-tac-toe*elaborate*my-turn
   (state <s> ^superstate nil ^env-turn red ^env-blue-moves <n> ^world <w>)
   (<w> ^objects.object <t>)
   (<t> ^type task ^blue-moves-applied <n>)
-->
   (<s> ^my-turn true)
}

sp {tic-tac-toe*reject*move*not-my-turn
   (state <s> ^superstate nil ^operator <op> + -^my-turn true)
   (<op> ^task-operator true)
-->
   (<s> ^operator <op> -)
}

## The environment's end-of-episode signal ends the run (IO-022), once every blue move reported has been applied.
sp {tic-tac-toe*propose*game-over
   (state <s> ^superstate nil ^env-game-over <r> ^env-blue-moves <n> ^world <w>)
   (<w> ^objects.object <t>)
   (<t> ^type task ^blue-moves-applied <n>)
-->
   (<s> ^operator <o> + >)
   (<o> ^name game-over ^result <r>)
}

sp {tic-tac-toe*apply*game-over
   (state <s> ^operator <o>)
   (<o> ^name game-over ^result <r>)
-->
   (write |Game over: | <r> (crlf))
   (halt)
}
''')
t.add('## Effect of blue\'s move (reported by the environment) on the real world, once per move number.' + effect_rules(
    'opponent-move',
    '''   :o-support
   (state <s> ^superstate nil ^world <w> ^opponent-move <om>)
   (<om> ^block <bh> ^location <lh> ^number <n>)''',
    '''
   (<t> ^blue-moves-applied <k> - <n>)
   (write |Opponent places | <bh> | on | <lh> (crlf))''',
    '''
   (<objs> ^object <t>)
   (<t> ^type task ^blue-moves-applied { <k> < <n> })'''))
t.add('''## Goal (statements 12-14): three different captured locations (each below a red block) are members of one line.
sp {tic-tac-toe*elaborate*goal*three-in-row
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^member <m1> <m2> <m3> ^below <b1> <b2> <b3>)
   (<objs> ^object <t> <line>)
   (<t> ^type task)
   (<line> ^type line)
   (<m1> ^argument1 <line> ^argument2 <l1>)
   (<m2> ^argument1 <line> ^argument2 { <> <l1> <l2> })
   (<m3> ^argument1 <line> ^argument2 { <> <l1> <> <l2> <l3> })
   (<b1> ^argument1 <l1> ^argument2 <r1>)
   (<b2> ^argument1 <l2> ^argument2 <r2>)
   (<b3> ^argument1 <l3> ^argument2 <r3>)
   (<r1> ^type block ^color red)
   (<r2> ^type block ^color red)
   (<r3> ^type block ^color red)
-->
   (<t> ^goal-met true)
}

## Failure (statements 18-19): three different occupied locations (each below a blue block) are members of one line.
sp {tic-tac-toe*elaborate*failure*opponent-three
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^member <m1> <m2> <m3> ^below <b1> <b2> <b3>)
   (<objs> ^object <line>)
   (<line> ^type line)
   (<m1> ^argument1 <line> ^argument2 <l1>)
   (<m2> ^argument1 <line> ^argument2 { <> <l1> <l2> })
   (<m3> ^argument1 <line> ^argument2 { <> <l1> <> <l2> <l3> })
   (<b1> ^argument1 <l1> ^argument2 <r1>)
   (<b2> ^argument1 <l2> ^argument2 <r2>)
   (<b3> ^argument1 <l3> ^argument2 <r3>)
   (<r1> ^type block ^color blue)
   (<r2> ^type block ^color blue)
   (<r3> ^type block ^color blue)
-->
   (<s> ^failure <ds>)
}
''')

out = 'tic-tac-toe-rules.soar' if WORLD == 'init-tictactoerc.world' else f'tic-tac-toe-rules-{WORLD[:-6]}.soar'
t.write(out)
open('tic-tac-toe.soar', 'w').write(R.loader('tic-tac-toe.soar', 'tic-tac-toe-rules.soar', 5))
print('wrote', out)
