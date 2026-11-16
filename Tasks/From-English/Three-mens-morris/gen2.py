"""Option 2: Three Men's Morris with cell objects, coordinates and links (no per-cell rules).

Static geometry: 9 cell objects (^id ^x ^y, direction links ^east ^south ^southeast ^southwest,
^adj to neighbours, ^centre yes on the middle) created once at the top state under ^geometry.
Dynamic state: 9 occupancy objects (^pos <cell> ^owner empty|X|O) and 2 player objects.
Only the occupancy and player objects are duplicated for lookahead; ^pos is copied as a POINTER to the
shared static cell, so the geometry is never copied.
Usage: gen2.py OUTFILE BOARD TURN REMX REMO PLIES   (optional start position)
"""
import sys
A=sys.argv[1:]
OUTF=A[0] if A else 'morris2.soar'
BOARD=A[1] if len(A)>1 else '.'*9
TURN=A[2] if len(A)>2 else 'X'
REMX,REMO,PLIES=(A[3:6] if len(A)>5 else (3,3,0))
MAXPLY=30
XY={i:(i%3,i//3) for i in range(9)}
def at(x,y): return y*3+x if 0<=x<3 and 0<=y<3 else None
DIRS={'east':(1,0),'south':(0,1),'southeast':(1,1),'southwest':(-1,1)}
adj=sorted({(a,b) for a in range(9) for b in range(9) if a!=b and ((abs(a-b)==1 and a//3==b//3) or abs(a-b)==3 or a==4 or b==4)})
out=[]
def sp(n,b): out.append("sp {%s\n%s\n}\n"%(n,b))
S="(state <s> ^name three-mens-morris"

sp("morris*propose*initialize","""    (state <s> ^superstate nil -^name <n>)
    -->
    (<s> ^operator <o> +)
    (<o> ^name initialize-morris +)""")
cells=[]
for i in range(9):
    x,y=XY[i]; l="    (<c%d> ^id %d + ^x %d + ^y %d +"%(i,i,x,y)
    for d,(dx,dy) in DIRS.items():
        j=at(x+dx,y+dy)
        if j is not None: l+=" ^%s <c%d> +"%(d,j)
    for (a,b) in adj:
        if a==i: l+=" ^adj <c%d> +"%b
    if i==4: l+=" ^centre yes +"
    cells.append(l+")")
occ=["    (<o%d> ^pos <c%d> + ^owner %s +)"%(i,i,{'.':'empty'}.get(BOARD[i],BOARD[i])) for i in range(9)]
sp("morris*apply*initialize","""    (state <s> ^operator <op>)
    (<op> ^name initialize-morris)
    -->
    (<s> ^name three-mens-morris + ^turn %s + ^plies %s + ^desired <d> + ^geometry <g> +
         ^player <px> + ^player <po> +"""%(TURN,PLIES)+"".join(" ^occ <o%d> +"%i for i in range(9))+""")
    (<d> ^name win + ^better higher +)
    (<g> """+"".join("^cell <c%d> + "%i for i in range(9))+""")
    (<px> ^name X + ^opponent O + ^remaining %s +)
    (<po> ^name O + ^opponent X + ^remaining %s +)
"""%(REMX,REMO)+"\n".join(cells)+"\n"+"\n".join(occ))
sp("morris*elaborate*problem-space","""    (state <s> ^name three-mens-morris)
    -->
    (<s> ^problem-space <p> +)
    (<p> ^name three-mens-morris + ^default-state-copy yes + ^all-attributes-at-level one +
         ^two-level-attributes occ + ^two-level-attributes player +
         ^dont-copy geometry + ^dont-copy winner + ^dont-copy threat + ^dont-copy draw +
         ^dont-copy stage1 + ^dont-copy stage2 + ^dont-copy moving + ^dont-copy placing +)""")

sp("morris*elaborate*phase*moving",S+""" ^turn <p> ^player <pl>)
    (<pl> ^name <p> ^remaining 0)
    -->
    (<s> ^moving <p> +)""")
sp("morris*elaborate*phase*placing",S+""" ^turn <p> ^player <pl>)
    (<pl> ^name <p> ^remaining > 0)
    -->
    (<s> ^placing <p> +)""")
# winner: a chain of three occupied-by-the-same-player cells along one direction
for d in DIRS:
    sp("morris*elaborate*winner*"+d,S+""")
    (<s> ^occ <o1>)
    (<o1> ^pos <c1> ^owner { <> empty <p> })
    (<c1> ^%s <c2>)
    (<s> ^occ <o2>)
    (<o2> ^pos <c2> ^owner <p>)
    (<c2> ^%s <c3>)
    (<s> ^occ <o3>)
    (<o3> ^pos <c3> ^owner <p>)
    -->
    (<s> ^winner <p> +)"""%(d,d))
# blocked: movement phase, no piece of the mover has an adjacent empty cell
sp("morris*elaborate*winner*blocked",S+""" ^turn <p> ^player <pl>)
    (<pl> ^name <p> ^remaining 0 ^opponent <q>)
   -{ (<s> ^occ <o2>)
      (<o2> ^pos <c2> ^owner <p>)
      (<c2> ^adj <c3>)
      (<s> ^occ <o3>)
      (<o3> ^pos <c3> ^owner empty) }
    -->
    (<s> ^winner <q> +)""")
sp("morris*elaborate*draw",S+""" ^plies >= %d -^winner <w>)
    -->
    (<s> ^draw yes +)"""%MAXPLY)
# threat: the player to move can complete a line next move (placement / movement)
for d in DIRS:
    for empty in (1,2,3):
        own=[k for k in (1,2,3) if k!=empty]
        def conds():
            l=[]
            for k in (1,2,3):
                l.append("    (<s> ^occ <o%d>)\n    (<o%d> ^pos <c%d> ^owner %s)"%(k,k,k,"<p>" if k in own else "empty"))
                if k<3: l.append("    (<c%d> ^%s <c%d>)"%(k,d,k+1))
            return "\n".join(l)
        sp("morris*elaborate*threat*place*%s*%d"%(d,empty),S+""" ^placing <p>)
"""+conds()+"""
    -->
    (<s> ^threat <p> +)""")
        a_,b_=own
        sp("morris*elaborate*threat*move*%s*%d"%(d,empty),S+""" ^moving <p>)
"""+conds()+"""
    (<c%d> ^adj <cz>)
    (<s> ^occ <oz>)
    (<oz> ^pos { <> <c%d> <> <c%d> <cz> } ^owner <p>)
    -->
    (<s> ^threat <p> +)"""%(empty,a_,b_))

# operators
sp("morris*propose*place",S+""" ^turn <p> ^placing <p> -^winner <w> -^draw yes -^tried-tied-operator <t>)
    (<s> ^occ <o>)
    (<o> ^owner empty)
    -->
    (<s> ^operator <op> +)
    (<op> ^name place + ^player <p> + ^occ <o> +)""")
sp("morris*propose*move",S+""" ^turn <p> ^moving <p> -^winner <w> -^draw yes -^tried-tied-operator <t>)
    (<s> ^occ <o1>)
    (<o1> ^pos <c1> ^owner <p>)
    (<c1> ^adj <c2>)
    (<s> ^occ <o2>)
    (<o2> ^pos <c2> ^owner empty)
    -->
    (<s> ^operator <op> +)
    (<op> ^name move + ^player <p> + ^from <o1> + ^to <o2> +)""")
sp("morris*apply*place*cell",S+""" ^operator <op>)
    (<op> ^name place ^player <p> ^occ <o>)
    (<o> ^owner empty)
    -->
    (<o> ^owner <p> + ^owner empty -)""")
sp("morris*apply*move*cell",S+""" ^operator <op>)
    (<op> ^name move ^player <p> ^from <o1> ^to <o2>)
    (<o1> ^owner <p>)
    (<o2> ^owner empty)
    -->
    (<o1> ^owner <p> - ^owner empty +)
    (<o2> ^owner empty - ^owner <p> +)""")
sp("morris*apply*place*book",S+""" ^operator <op> ^turn <p> ^plies <n> ^player <pl>)
    (<op> ^name place ^player <p>)
    (<pl> ^name <p> ^opponent <q> ^remaining <r>)
    -->
    (<s> ^turn <q> + ^turn <p> - ^plies (+ <n> 1) + ^plies <n> -)
    (<pl> ^remaining (- <r> 1) + ^remaining <r> -)""")
sp("morris*apply*move*book",S+""" ^operator <op> ^turn <p> ^plies <n> ^player <pl>)
    (<op> ^name move ^player <p>)
    (<pl> ^name <p> ^opponent <q>)
    -->
    (<s> ^turn <q> + ^turn <p> - ^plies (+ <n> 1) + ^plies <n> -)""")

# evaluation of a lookahead state from the point of view of the player who just moved
base=S+""" ^quiescence t ^turn <q> ^desired <d> ^look-ahead-operator <lo> ^player <pl>)
    (<lo> ^player <p>)
    (<pl> ^name <p> ^opponent <q>)"""
sp("morris*elaborate*stage1",S+""" ^turn <q> ^look-ahead-operator <lo> ^player <pl>)
    (<lo> ^player <p>)
    (<pl> ^name <p> ^opponent <q>)
    -->
    (<s> ^stage1 yes +)""")
sp("morris*elaborate*stage2",S+""" ^stage1 yes)
    -->
    (<s> ^stage2 yes +)""")
sp("morris*evaluate*win",base+"""
    (<s> ^winner <p>)
    -->
    (<s> ^numeric-value 100 +)""")
sp("morris*evaluate*lose",base+"""
    (<s> ^winner <q>)
    -->
    (<s> ^numeric-value -100 +)""")
sp("morris*evaluate*opponent-threat",base+"""
    (<s> ^threat <q> -^winner <w>)
    -->
    (<s> ^numeric-value -100 +)""")
sp("morris*evaluate*centre",base+"""
    (<s> ^stage2 yes -^winner <w> -^threat <q> ^occ <oc>)
    (<oc> ^pos <cc> ^owner <p>)
    (<cc> ^centre yes)
    -->
    (<s> ^numeric-value 2 +)""")
sp("morris*evaluate*other",base+"""
    (<s> ^stage2 yes -^winner <w> -^threat <q>)
   -{ (<s> ^occ <oc>)
      (<oc> ^pos <cc> ^owner <p>)
      (<cc> ^centre yes) }
    -->
    (<s> ^numeric-value 0 +)""")

# top state: monitoring and finishing
sp("morris*monitor*place","""    (state <s> ^superstate nil ^name three-mens-morris ^operator <op>)
    (<op> ^name place ^player <p> ^occ <o>)
    (<o> ^pos <c>)
    (<c> ^id <n>)
    -->
    (write (crlf) <p> | places | <n>)""")
sp("morris*monitor*move","""    (state <s> ^superstate nil ^name three-mens-morris ^operator <op>)
    (<op> ^name move ^player <p> ^from <o1> ^to <o2>)
    (<o1> ^pos <c1>)
    (<c1> ^id <a>)
    (<o2> ^pos <c2>)
    (<c2> ^id <b>)
    -->
    (write (crlf) <p> | moves | <a> | -> | <b>)""")
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
open(OUTF,'w').write("# Three Men's Morris, option 2: cell objects with coordinates, links and pointer-shared geometry\n# (generated by gen2.py)\nchunk never\nsource selection.soar\n\n"+"\n".join(out))
print(len(out),"rules")
