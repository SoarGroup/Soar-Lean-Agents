"""Generate three-mens-morris.soar: Three Men's Morris with the default selection space.

Rules of the game (the English specification followed):
 * 3x3 points, numbered 0..8 row by row; X moves first, players alternate.
 * Placement phase: each player places 3 pieces on empty points (one per turn).
 * Movement phase (a player with no piece left to place): move one of your pieces to an
   adjacent empty point; points are adjacent along the board's lines (rows, columns, and the
   two diagonals, which pass through the centre).
 * Three of your pieces in a line (row, column or diagonal) wins at once, in either phase.
 * A player who has no legal move in the movement phase loses.
 * Draw if no one has won after 30 plies (the movement phase can repeat forever).
"""
L=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
orth=[(a,b) for a in range(9) for b in range(9) if (abs(a-b)==1 and a//3==b//3) or abs(a-b)==3]
adj=set(orth)|{(4,x) for x in range(9) if x!=4}|{(x,4) for x in range(9) if x!=4}
adj=sorted(adj)
OPP={'X':'O','O':'X'}
MAXPLY=30
import sys
# optional start position: gen.py OUTFILE BOARD TURN REMX REMO PLIES  (BOARD like "XX.OO....")
ARGS=sys.argv[1:]
OUTF=ARGS[0] if ARGS else 'three-mens-morris.soar'
BOARD=ARGS[1] if len(ARGS)>1 else '.'*9
TURN=ARGS[2] if len(ARGS)>2 else 'X'
REMX,REMO,PLIES=(ARGS[3:6] if len(ARGS)>5 else (3,3,0))
out=[]
def sp(name,body): out.append("sp {%s\n%s\n}\n"%(name,body))
def P(n): return str(n)

sp("morris*propose*initialize","""    (state <s> ^superstate nil -^name <n>)
    -->
    (<s> ^operator <o> +)
    (<o> ^name initialize-morris +)""")
sp("morris*apply*initialize","""    (state <s> ^operator <o>)
    (<o> ^name initialize-morris)
    -->
    (<s> ^name three-mens-morris + ^board <b> + ^turn %s + ^remaining-X %s + ^remaining-O %s + ^plies %s + ^desired <d> +)
    (<d> ^name win + ^better higher +)
    (<b> """%(TURN,REMX,REMO,PLIES)+" ".join("^c%d %s +"%(i,{'.':'empty'}.get(BOARD[i],BOARD[i])) for i in range(9))+" )")
sp("morris*elaborate*problem-space","""    (state <s> ^name three-mens-morris)
    -->
    (<s> ^problem-space <p> +)
    (<p> ^name three-mens-morris + ^default-state-copy yes + ^all-attributes-at-level one + ^two-level-attributes board +
         ^dont-copy winner + ^dont-copy threat + ^dont-copy draw + ^dont-copy stage1 + ^dont-copy stage2 +)""")

# ---- derived facts (i-supported): winner, mobile, threat, draw
for p in 'XO':
    for (a,b,c) in L:
        sp("morris*elaborate*winner*%s*%d%d%d"%(p,a,b,c),"""    (state <s> ^name three-mens-morris ^board <b>)
    (<b> ^c%d %s ^c%d %s ^c%d %s)
    -->
    (<s> ^winner %s +)"""%(a,p,b,p,c,p,p))
for p in 'XO':
    neg="\n".join("    -{ (<b> ^c%d %s ^c%d empty) }"%(a,p,b) for (a,b) in adj)
    sp("morris*elaborate*winner*blocked*%s"%p,"""    (state <s> ^name three-mens-morris ^turn %s ^remaining-%s 0 ^board <b>)
"""%(p,p)+neg+"""
    -->
    (<s> ^winner %s +)"""%OPP[p])
sp("morris*elaborate*draw","""    (state <s> ^name three-mens-morris ^plies >= %d -^winner <w>)
    -->
    (<s> ^draw yes +)"""%MAXPLY)
# threat: the player to move can complete a line next move
for p in 'XO':
    for (a,b,c) in L:
        for (x,y,t) in [(a,b,c),(a,c,b),(b,c,a)]:
            sp("morris*elaborate*threat*place*%s*%d%d%d-%d"%(p,a,b,c,t),"""    (state <s> ^name three-mens-morris ^turn %s ^remaining-%s > 0 ^board <b>)
    (<b> ^c%d %s ^c%d %s ^c%d empty)
    -->
    (<s> ^threat %s +)"""%(p,p,x,p,y,p,t,p))
            for z in range(9):
                if z in (x,y,t) or (z,t) not in adj: continue
                sp("morris*elaborate*threat*move*%s*%d%d%d-%d-from%d"%(p,a,b,c,t,z),"""    (state <s> ^name three-mens-morris ^turn %s ^remaining-%s 0 ^board <b>)
    (<b> ^c%d %s ^c%d %s ^c%d empty ^c%d %s)
    -->
    (<s> ^threat %s +)"""%(p,p,x,p,y,p,t,z,p,p))

# ---- operators
for p in 'XO':
    for n in range(9):
        sp("morris*propose*place*%s*%d"%(p,n),"""    (state <s> ^name three-mens-morris ^turn %s ^remaining-%s > 0 ^board <b> -^winner <w> -^draw yes -^tried-tied-operator <t>)
    (<b> ^c%d empty)
    -->
    (<s> ^operator <o> +)
    (<o> ^name place + ^player %s + ^cell %d +)"""%(p,p,n,p,n))
    for (a,b) in adj:
        sp("morris*propose*move*%s*%d-%d"%(p,a,b),"""    (state <s> ^name three-mens-morris ^turn %s ^remaining-%s 0 ^board <b> -^winner <w> -^draw yes -^tried-tied-operator <t>)
    (<b> ^c%d %s ^c%d empty)
    -->
    (<s> ^operator <o> +)
    (<o> ^name move + ^player %s + ^from %d + ^to %d +)"""%(p,p,a,p,b,p,a,b))
for n in range(9):
    sp("morris*apply*place*cell*%d"%n,"""    (state <s> ^name three-mens-morris ^operator <o> ^board <b>)
    (<o> ^name place ^player <p> ^cell %d)
    (<b> ^c%d empty)
    -->
    (<b> ^c%d <p> + ^c%d empty -)"""%(n,n,n,n))
for (a,b) in adj:
    sp("morris*apply*move*cell*%d-%d"%(a,b),"""    (state <s> ^name three-mens-morris ^operator <o> ^board <b>)
    (<o> ^name move ^player <p> ^from %d ^to %d)
    (<b> ^c%d <p> ^c%d empty)
    -->
    (<b> ^c%d <p> + ^c%d <p> - ^c%d empty + ^c%d empty -)"""%(a,b,a,b,b,a,a,b))
# note: the move rule above removes ^c<b> empty and ^c<a> <p>, adds ^c<b> <p> and ^c<a> empty
for p in 'XO':
    q=OPP[p]
    sp("morris*apply*place*book*%s"%p,"""    (state <s> ^name three-mens-morris ^operator <o> ^turn %s ^remaining-%s <r> ^plies <n>)
    (<o> ^name place ^player %s)
    -->
    (<s> ^turn %s + ^turn %s - ^remaining-%s (- <r> 1) + ^remaining-%s <r> - ^plies (+ <n> 1) + ^plies <n> -)"""%(p,p,p,q,p,p,p))
    sp("morris*apply*move*book*%s"%p,"""    (state <s> ^name three-mens-morris ^operator <o> ^turn %s ^plies <n>)
    (<o> ^name move ^player %s)
    -->
    (<s> ^turn %s + ^turn %s - ^plies (+ <n> 1) + ^plies <n> -)"""%(p,p,q,p))

# ---- evaluation of a lookahead state, from the point of view of the player who just moved
for p in 'XO':
    q=OPP[p]
    base="""    (state <s> ^name three-mens-morris ^quiescence t ^turn %s ^desired <d> ^look-ahead-operator <lo>)
    (<lo> ^player %s)"""%(q,p)
    sp("morris*elaborate*stage1*%s"%p,"""    (state <s> ^name three-mens-morris ^turn %s ^look-ahead-operator <lo>)
    (<lo> ^player %s)
    -->
    (<s> ^stage1 yes +)"""%(q,p))
    sp("morris*elaborate*stage2*%s"%p,"""    (state <s> ^name three-mens-morris ^stage1 yes)
    -->
    (<s> ^stage2 yes +)""")
    sp("morris*evaluate*win*%s"%p,base+"""
    (<s> ^winner %s)
    -->
    (<s> ^numeric-value 100 +)"""%p)
    sp("morris*evaluate*lose*%s"%p,base+"""
    (<s> ^winner %s)
    -->
    (<s> ^numeric-value -100 +)"""%q)
    sp("morris*evaluate*opponent-threat*%s"%p,base+"""
    (<s> ^threat %s -^winner <w>)
    -->
    (<s> ^numeric-value -100 +)"""%q)
    # otherwise: small positional score: centre and own readiness (own threat is not visible
    # here because it is the opponent's turn; use the centre only)
    sp("morris*evaluate*centre*%s"%p,base+"""
    (<s> ^stage2 yes ^board <b> -^winner <w> -^threat %s)
    (<b> ^c4 %s)
    -->
    (<s> ^numeric-value 2 +)"""%(q,p))
    sp("morris*evaluate*other*%s"%p,base+"""
    (<s> ^stage2 yes ^board <b> -^winner <w> -^threat %s)
    (<b> -^c4 %s)
    -->
    (<s> ^numeric-value 0 +)"""%(q,p))

# ---- top state: monitoring and halting
sp("morris*monitor*place","""    (state <s> ^superstate nil ^name three-mens-morris ^operator <o>)
    (<o> ^name place ^player <p> ^cell <c>)
    -->
    (write (crlf) <p> | places | <c>)""")
sp("morris*monitor*move","""    (state <s> ^superstate nil ^name three-mens-morris ^operator <o>)
    (<o> ^name move ^player <p> ^from <a> ^to <c>)
    -->
    (write (crlf) <p> | moves | <a> | -> | <c>)""")
sp("morris*propose*finish","""    (state <s> ^superstate nil ^name three-mens-morris)
    (<s> ^{ << winner draw >> <k> } <w>)
    -->
    (<s> ^operator <o> +)
    (<o> ^name finish + ^kind <k> + ^what <w> +)""")
sp("morris*apply*finish*winner","""    (state <s> ^superstate nil ^operator <o>)
    (<o> ^name finish ^kind winner ^what <w>)
    -->
    (write (crlf) |WINNER: | <w>)
    (halt)""")
sp("morris*apply*finish*draw","""    (state <s> ^superstate nil ^operator <o>)
    (<o> ^name finish ^kind draw)
    -->
    (write (crlf) |DRAW|)
    (halt)""")
open(OUTF,'w').write("# Three Men's Morris, played by Soar against itself with the default selection space\n# (generated by gen.py)\n"+"chunk never\nsource selection.soar\n\n"+"\n".join(out))
print(len(out),"rules")
