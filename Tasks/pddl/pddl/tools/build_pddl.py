"""Assemble Tasks/pddl from the downloaded sources and hand-written instances.

Usage: python3 build_pddl.py <download-dir> <repo>/Tasks/pddl
"""
import os, shutil, subprocess, sys, re
from pathlib import Path

DL = Path(sys.argv[1]); OUT = Path(sys.argv[2])
PI = DL / "pddl-instances"
PG = DL / "pddl-generators"
SG = DL / "Domains-Planning-Domain-Definition-Language"

URL_PI = "https://github.com/potassco/pddl-instances"
URL_PG = "https://github.com/AI-Planning/pddl-generators"
URL_SG = "https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language"
URL_FF = "https://fai.cs.uni-saarland.de/hoffmann/ff-domains.html"


def git_show(repo, path):
    return subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{path}"],
                          capture_output=True, text=True, check=True).stdout


def copy_ipc(src_dir, dst):
    (dst / "problems").mkdir(parents=True, exist_ok=True)
    shutil.copy(src_dir / "domain.pddl", dst / "domain.pddl")
    files = sorted((src_dir / "instances").glob("instance-*.pddl"),
                   key=lambda p: int(re.search(r"(\d+)", p.name).group(1)))
    for f in files:
        shutil.copy(f, dst / "problems" / f.name)
    if (src_dir / "README.md").exists():
        shutil.copy(src_dir / "README.md", dst / "SOURCE-README.md")
    return [f.name for f in files]


def write_problems(dst, problems):
    (dst / "problems").mkdir(parents=True, exist_ok=True)
    for name, text in problems:
        (dst / "problems" / name).write_text(text.strip() + "\n")
    return [n for n, _ in problems]


# ---------- hand-written instances (following each generator's scheme) ----------

def bw3_problems():
    return [
        ("p01-sussman.pddl", """
; Sussman anomaly: C on A; A and B on the table. Goal: A on B on C.
(define (problem bw3-sussman) (:domain blocksworld-3ops)
  (:objects a b c)
  (:init (on-table a) (on-table b) (on c a) (clear c) (clear b))
  (:goal (and (on a b) (on b c))))"""),
        ("p02-4blocks.pddl", """
(define (problem bw3-4blocks) (:domain blocksworld-3ops)
  (:objects a b c d)
  (:init (on-table a) (on b a) (on c b) (on-table d) (clear c) (clear d))
  (:goal (and (on a b) (on b c) (on c d))))"""),
        ("p03-5blocks.pddl", """
(define (problem bw3-5blocks) (:domain blocksworld-3ops)
  (:objects a b c d e)
  (:init (on-table a) (on b a) (on-table c) (on d c) (on e d) (clear b) (clear e))
  (:goal (and (on e a) (on a c) (on c b) (on b d))))"""),
    ]


def ferry_problems():
    def prob(name, locs, cars, start, goal):
        init = [f"(location {l})" for l in locs] + [f"(car {c})" for c in cars]
        init += [f"(not-eq {a} {b})" for a in locs for b in locs if a != b]
        init += ["(empty-ferry)", f"(at-ferry {locs[0]})"]
        init += [f"(at {c} {start[c]})" for c in cars]
        g = " ".join(f"(at {c} {goal[c]})" for c in cars)
        return (f"{name}.pddl", f"(define (problem {name}) (:domain ferry)\n  (:objects {' '.join(locs + cars)})\n  (:init {' '.join(init)})\n  (:goal (and {g})))")
    return [
        prob("p01-l2-c1", ["l0", "l1"], ["c0"], {"c0": "l0"}, {"c0": "l1"}),
        prob("p02-l3-c2", ["l0", "l1", "l2"], ["c0", "c1"], {"c0": "l1", "c1": "l2"}, {"c0": "l2", "c1": "l0"}),
        prob("p03-l3-c3", ["l0", "l1", "l2"], ["c0", "c1", "c2"], {"c0": "l0", "c1": "l1", "c2": "l2"}, {"c0": "l1", "c1": "l2", "c2": "l0"}),
    ]


def tyre_problems():
    out = []
    for n in (1, 2, 3):
        hubs = [f"the-hub{i}" for i in range(1, n + 1)]
        nuts = [f"nuts{i}" for i in range(1, n + 1)]
        flats = [f"w{i}" for i in range(1, n + 1)]
        spares = [f"r{i}" for i in range(1, n + 1)]
        init = ["(in jack boot)", "(in pump boot)", "(in wrench boot)", "(unlocked boot)", "(closed boot)"]
        goal = []
        for h, nu, w, r in zip(hubs, nuts, flats, spares):
            init += [f"(intact {r})", f"(in {r} boot)", f"(not-inflated {r})",
                     f"(on {w} {h})", f"(on-ground {h})", f"(tight {nu} {h})", f"(fastened {h})"]
            goal += [f"(on {r} {h})", f"(inflated {r})", f"(tight {nu} {h})", f"(in {w} boot)"]
        goal += ["(in wrench boot)", "(in jack boot)", "(in pump boot)", "(closed boot)"]
        objs = (f"{' '.join(flats + spares)} - wheel {' '.join(nuts)} - nut "
                f"{' '.join(hubs)} - hub boot - container")
        out.append((f"p{n:02d}-tyres{n}.pddl",
                    f"(define (problem tyreworld-{n}) (:domain tyreworld)\n  (:objects {objs})\n"
                    f"  (:init {' '.join(init)})\n  (:goal (and {' '.join(goal)})))"))
    return out


def briefcase_problems():
    def prob(name, objs, locs, bc_start, start, bc_goal, goal):
        init = [f"(is-at {bc_start})"] + [f"(at {o} {start[o]})" for o in objs]
        g = [f"(at {o} {goal[o]})" for o in objs] + [f"(is-at {bc_goal})"]
        return (f"{name}.pddl", f"(define (problem {name}) (:domain briefcase)\n  (:objects {' '.join(objs)} - portable {' '.join(locs)} - location)\n"
                f"  (:init {' '.join(init)})\n  (:goal (and {' '.join(g)})))")
    return [
        prob("p01-o1", ["o1"], ["l0", "l1"], "l0", {"o1": "l0"}, "l0", {"o1": "l1"}),
        prob("p02-o2", ["o1", "o2"], ["l0", "l1", "l2"], "l0", {"o1": "l1", "o2": "l2"}, "l1", {"o1": "l2", "o2": "l0"}),
        prob("p03-o3", ["o1", "o2", "o3"], ["l0", "l1", "l2", "l3"], "l3", {"o1": "l0", "o2": "l1", "o3": "l2"}, "l0", {"o1": "l2", "o2": "l3", "o3": "l1"}),
    ]


def fridge_problems():
    out = []
    for nf, ns in ((1, 2), (1, 4), (2, 3)):
        screws, init, goal, comps, fr, bps = [], [], [], [], [], []
        for f in range(1, nf + 1):
            fr.append(f"f{f}"); bps.append(f"b{f}")
            old, new = f"c{f}-old", f"c{f}-new"; comps += [old, new]
            init += [f"(attached {old} f{f})", f"(fridge-on f{f})"]
            goal += [f"(attached {new} f{f})", f"(fridge-on f{f})"]
            for s in range(1, ns + 1):
                sc = f"s{f}-{s}"; screws.append(sc)
                init += [f"(screwed {sc})", f"(fits {sc} {old})", f"(fits {sc} {new})"]
                goal += [f"(screwed {sc})"]
        objs = (f"{' '.join(screws)} - screw {' '.join(bps)} - backplane "
                f"{' '.join(comps)} - compressor {' '.join(fr)} - fridge")
        out.append((f"p{len(out)+1:02d}-f{nf}-s{ns}.pddl",
                    f"(define (problem fridge-f{nf}-s{ns}) (:domain fridge-domain)\n  (:objects {objs})\n"
                    f"  (:init {' '.join(init)})\n  (:goal (and {' '.join(goal)})))"))
    return out


# ---------- the 13 domains ----------
DOMAINS = []

def add(**kw):
    DOMAINS.append(kw)

add(folder="blocksworld-4ops", title="Blocksworld (4 operators, robot arm)",
    origin="Winograd (1972) and Sussman (1974) lineage; this PDDL encoding (pick-up, put-down, stack, unstack) was used at AIPS-2000.",
    source=("ipc", PI / "ipc-2000/domains/blocks-strips-untyped"),
    source_text=f"`ipc-2000/domains/blocks-strips-untyped` of [{URL_PI}]({URL_PI}) (original AIPS-2000 files; file names in SOURCE-README.md)",
    pddl="Untyped STRIPS", requirements=":strips",
    description="Restack blocks on a table with a one-block robot arm. The goal fixes some on-relations.",
    overlap="Blocks World family (Tasks/Families) and the Rosie blocks-world puzzles (Tasks/From-English/rosie-teaching/block-puzzles).",
    notes="Straightforward STRIPS. Instances grow from 4 to 50 blocks; the smallest are the first candidates.")

add(folder="blocksworld-3ops", title="Blocksworld (3 operators, no arm)",
    origin="Winograd and Sussman lineage; taken by the FF collection from the IPP domain collection.",
    source=("hand", bw3_problems),
    source_text=f"domain from `blocksworld/3ops/domain.pddl` of [{URL_PG}]({URL_PG}); the three problems were written for this collection (Sussman anomaly, 4 and 5 blocks), since the repository has a generator but no instances",
    pddl="Untyped STRIPS with equality and a negative precondition", requirements=":strips :equality :negative-preconditions",
    description="Move a clear block onto another clear block or the table, with no arm. The goal fixes some on-relations.",
    overlap="As blocksworld-4ops; the 3-operator form is closer to the Rosie blocks-world task.",
    notes="Uses `(not (= ?bm ?bt))`. Negated conditions in operators are outside the current WorldSpec well-formedness (negation stays out of operators; convention L11-003). How to translate an inequality is a question to settle before conversion.")

add(folder="gripper", title="Gripper",
    origin="Jana Koehler; AIPS-1998, round 1.",
    source=("ipc", PI / "ipc-1998/domains/gripper-round-1-strips"),
    source_text=f"`ipc-1998/domains/gripper-round-1-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS", requirements="none declared (STRIPS)",
    description="A robot with two grippers carries N balls from room A to room B, one ball per gripper.",
    overlap="None.",
    notes="The two grippers are interchangeable, and so are the balls: the standard example of symmetry pruning (strategy catalog PH-12).")

add(folder="hanoi", title="Towers of Hanoi",
    origin="Origin of this encoding unknown (IPP collection); the formalization comment credits Hector Geffner.",
    source=("hanoi", None),
    source_text=f"domain and problems `pddl/hanoi.pddl`, `pddl/hanoi-3.pddl` to `hanoi-8.pddl` of [{URL_SG}]({URL_SG}), SoarGroup's earlier PDDL-to-Soar translator; the domain is identical in content to `hanoi/domain.pddl` of [{URL_PG}]({URL_PG})",
    pddl="Untyped STRIPS", requirements=":strips",
    description="Move a stack of discs from the first peg to the third, one disc at a time, never placing a disc on a smaller one. Pegs are treated as very large discs.",
    overlap="Rosie tower-of-hanoi, -4 and -5 (Tasks/From-English/rosie-teaching/block-puzzles), which do not solve for 4 and 5 discs within the look-ahead depth limit.",
    notes="A direct comparison of English-derived and PDDL-derived agents for 3 to 8 discs.")

add(folder="tyreworld", title="Tyreworld (flat tyre)",
    origin="Stuart Russell; multi-tyre version by Jana Koehler; IPP collection.",
    source=("hand", tyre_problems),
    source_text=f"domain from `tyreworld/domain.pddl` of [{URL_PG}]({URL_PG}); the problems for 1, 2 and 3 tyres were written for this collection following the generator's scheme (no randomization), since the repository has a generator but no instances",
    pddl="Typed STRIPS with constants", requirements=":strips :typing",
    description="Replace flat tyres with inflated spares: open the boot, fetch the tools, loosen the nuts, jack up the hub, swap the wheels, and put everything away.",
    overlap="None.",
    notes="Long plans from a fixed procedure; a good case for task decomposition and verification before halt. One change to the source domain file: the `(:constants ...)` line was moved before `(:predicates ...)`, as the PDDL grammar requires (strict parsers reject the original order); nothing else changed.")

add(folder="ferry", title="Ferry",
    origin="Origin unknown; IPP collection. The FF version restricts sailing to different locations.",
    source=("hand", ferry_problems),
    source_text=f"domain from `ferry/domain.pddl` of [{URL_PG}]({URL_PG}); three problems written for this collection following the generator's scheme",
    pddl="Untyped STRIPS (types given as unary predicates)", requirements="none declared (STRIPS)",
    description="A ferry that holds one car at a time carries cars between locations to their goal locations.",
    overlap="Related in kind to the river crossings (Tasks/From-English/rosie-teaching/river-crossing-puzzles).",
    notes="`not-eq` facts are listed in the initial state, so no negation is needed.")

add(folder="briefcaseworld", title="Briefcaseworld",
    origin="First described by Edwin Pednault; IPP collection.",
    source=("hand", briefcase_problems),
    source_text=f"domain from `briefcaseworld/domain.pddl` of [{URL_PG}]({URL_PG}); three problems written for this collection following the generator's scheme (objects and briefcase over objects + 1 locations)",
    pddl="Typed ADL: a conditional effect over all objects", requirements=":adl",
    description="Carry objects between locations in a briefcase. Moving the briefcase moves everything inside it.",
    overlap="None.",
    notes="`move` has a `forall ... when` conditional effect, which is close to WorldSpec's `each` effect. `put-in` has a negative precondition `(not (in ?x))`, outside current WorldSpec operator conditions (L11-003); to be settled before conversion.")

add(folder="logistics", title="Logistics",
    origin="Manuela Veloso (Prodigy); this version by Selman and Kautz; AIPS-1998, round 1.",
    source=("ipc", PI / "ipc-1998/domains/logistics-round-1-strips"),
    source_text=f"`ipc-1998/domains/logistics-round-1-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS (types as unary predicates)", requirements=":strips",
    description="Trucks carry packages within cities and airplanes carry them between cities' airports, to deliver every package to its goal location.",
    overlap="None; transport tasks of the same kind are not yet in the repository.",
    notes="Packages can be delivered nearly independently: the standard case for decomposition by goal conjunct.")

add(folder="movie", title="Movie",
    origin="Corin Anderson; AIPS-1998, round 1.",
    source=("ipc", PI / "ipc-1998/domains/movie-round-1-strips"),
    source_text=f"`ipc-1998/domains/movie-round-1-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS", requirements="none declared (STRIPS)",
    description="Get ready to watch a movie: buy one snack of each kind, rewind the movie and reset the counter.",
    overlap="None.",
    notes="Trivial plans; useful as a first end-to-end test of the PDDL front end. Instances grow only in the number of interchangeable snacks.")

add(folder="grid", title="Grid",
    origin="Drew McDermott; AIPS-1998, round 2.",
    source=("ipc", PI / "ipc-1998/domains/grid-round-2-strips"),
    source_text=f"`ipc-1998/domains/grid-round-2-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS", requirements=":strips",
    description="A robot moves on a grid, picks up and carries one key at a time, unlocks locked cells with keys of the matching shape, and brings keys to goal cells.",
    overlap="None.",
    notes="Only five instances, all large; smaller ones may have to be written for first runs.")

add(folder="mystery", title="Mystery",
    origin="Drew McDermott; AIPS-1998, round 1.",
    source=("ipc", PI / "ipc-1998/domains/mystery-round-1-strips"),
    source_text=f"`ipc-1998/domains/mystery-round-1-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS (types as unary predicates)", requirements="none declared (STRIPS)",
    description="A disguised transport problem: vehicles with limited space and fuel move cargo over a map. Object and operator names are deliberately meaningless (pleasures, cravings, foods).",
    overlap="None.",
    notes="The meaningless names make it a test of blind back-translation to English: the back-translator cannot lean on the names.")

add(folder="mprime", title="Mystery Prime (Mprime)",
    origin="Drew McDermott; AIPS-1998, round 1.",
    source=("ipc", PI / "ipc-1998/domains/mystery-prime-round-1-strips"),
    source_text=f"`ipc-1998/domains/mystery-prime-round-1-strips` of [{URL_PI}]({URL_PI}) (original competition files)",
    pddl="Untyped STRIPS with one inequality", requirements=":negative-preconditions :equality",
    description="Mystery with one more operator: fuel can be passed between locations.",
    overlap="None.",
    notes="Second round, after Mystery. The fuel-passing operator has `(not (= ?n1 ?n2))`, a correction added by Malte Helmert to the original file; as with blocksworld-3ops, how to translate an inequality is to be settled before conversion.")

add(folder="fridge", title="Fridge",
    origin="Tony Barrett (University of Washington, 1993-94); quantified version by Joerg Hoffmann; IPP collection.",
    source=("hand", fridge_problems),
    source_text=f"domain from `fridge/domain.pddl` of [{URL_PG}]({URL_PG}); three problems written for this collection following the generator's scheme (no randomization). The domain file carries a University of Washington copyright notice permitting non-commercial research use only, which must stay with the file",
    pddl="Typed ADL: quantified, negative and disjunctive (imply) preconditions", requirements=":strips :typing :quantified-preconditions :negative-preconditions :disjunctive-preconditions",
    description="For each fridge, turn it off, unfasten the screws of the backplane, swap the broken compressor for a new one, fasten the screws and turn it on.",
    overlap="None.",
    notes="Universal and existential preconditions are not in WorldSpec; second round.")

add(folder="assembly", title="Assembly",
    origin="Drew McDermott; AIPS-1998, round 1 (ADL track only).",
    source=("ipc", PI / "ipc-1998/domains/assembly-round-1-adl"),
    source_text=f"`ipc-1998/domains/assembly-round-1-adl` of [{URL_PI}]({URL_PI}) (original competition files; the source notes buggy versions of some instances, kept there under additional-notes and not copied here)",
    pddl="Typed ADL: quantified and conditional preconditions and effects", requirements=":adl",
    description="Assemble an object from a tree of parts, subject to resources, transient parts and ordering constraints between parts.",
    overlap="None.",
    notes="The most complex of the set; last.")


def readme_for(d, probs):
    lines = [f"# {d['title']}", "",
             "**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.", "",
             f"**Origin.** {d['origin']}", "",
             f"**Task.** {d['description']}", "",
             f"**PDDL.** {d['pddl']}. Requirements: {d['requirements']}.", "",
             f"**Source.** {d['source_text']}.", "",
             f"**Overlap with existing tasks.** {d['overlap']}", "",
             f"**Notes for conversion.** {d['notes']}", "",
             "## Files", "",
             "| File | What it is |", "|---|---|",
             "| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |",
             f"| `problems/` | {len(probs)} problem files: {probs[0]}{' to ' + probs[-1] if len(probs) > 1 else ''} |"]
    if d["source"][0] == "ipc":
        lines.append("| `SOURCE-README.md` | The source repository's notes, with the original competition file names |")
    lines += ["",
              "Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), "
              "`<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`."]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for d in DOMAINS:
        dst = OUT / d["folder"]
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        kind, src = d["source"]
        if kind == "ipc":
            probs = copy_ipc(src, dst)
        elif kind == "hanoi":
            (dst / "domain.pddl").write_text(git_show(SG, "pddl/hanoi.pddl"))
            probs = write_problems(dst, [(f"hanoi-{n}.pddl", git_show(SG, f"pddl/hanoi-{n}.pddl")) for n in range(3, 9)])
        else:
            gen_dir = {"blocksworld-3ops": "blocksworld/3ops"}.get(d["folder"], d["folder"])
            shutil.copy(PG / gen_dir / "domain.pddl", dst / "domain.pddl")
            probs = write_problems(dst, src())
        if d["folder"] == "tyreworld":
            t = (dst / "domain.pddl").read_text()
            const = "(:constants wrench jack pump - tool)"
            assert const in t
            t = t.replace(const + "\n", "").replace("(:predicates", const + "\n(:predicates", 1)
            (dst / "domain.pddl").write_text(t)
        (dst / "README.md").write_text(readme_for(d, probs))
        rows.append((d, len(probs)))
    return rows


if __name__ == "__main__":
    for d, n in main():
        print(f"{d['folder']}: {n} problems")
