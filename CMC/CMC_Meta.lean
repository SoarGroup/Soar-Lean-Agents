/-!
# The Common Model of Cognition with metacognition — a Lean 4 draft

This file extends `CMC.lean` (the 2017 Standard Model) with the metacognition proposal.
`CMC.lean` is left unchanged so both versions remain available.

Sources
* [LLR17] Laird, J. E., Lebiere, C., & Rosenbloom, P. S. (2017). A Standard Model of the
  Mind. *AI Magazine* 38(4). Table 1 items (A.1 … D.2b) refer to this paper.
* [RLL17] Rosenbloom, P. S., Laird, J. E., & Lebiere, C. (2017). Précis of
  'A Standard Model of the Mind'. *Advances in Cognitive Systems*.
* [LLRS] Laird, J. E., Lebiere, C., Rosenbloom, P. S., & Stocco, A. Unified, Comprehensive
  Metacognition within the Common Model of Cognition. AGI (final version).

Conventions
* Every definition quotes the passage it formalizes.
* `DECIDED` / `CONFIRMED`: a clarification by John Laird, with date. Decisions dated
  2026-10-28 that concern the metacognition extension are marked `[META]`.
* `OPEN`: unresolved by the papers. `FUTURE`: planned extension. `VARIANT`: permitted
  architectural variation, recorded but not formalized. `NOT FORMALIZED`: recorded only.

What the metacognition extension adds ([LLRS] §4–6, "two structural extensions: module
process-state buffers and episodic memory"):
1. A *process-data area* for every module, written only by the architecture
   (`PPart.process`, `DPart.process`, `MPart.process`, `Loc.procProcess`, `Loc.wmProcess`).
2. Procedural selection reports *why* it failed (`SelFail`), instead of being silent.
3. Episodic recording of working memory on every cycle (`Arch.record`), into a designated
   declarative memory (`Sig.epi`).
4. Retrieval updates the metadata of what it retrieves (`Arch.retrieveTouch`).
5. A working-memory appraisal hook (`Arch.appraise`).
And, by construction, *no* metacognitive module: "metacognition requires no dedicated
metacognitive reasoning modules: it reuses the CMC's existing cognitive capabilities"
([LLRS] abstract). Metareasoning is ordinary reasoning over meta-information in working
memory, so it is carried out by the same `Step.cycle` as base-level reasoning.
-/

namespace CMC.Meta

/-! ## Utilities -/

/-- Point update of a function (core Lean has no `Function.update`). -/
def upd {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) : α → β :=
  fun x => if x = a then v else f x

theorem upd_same {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) :
    upd f a v a = v := by simp [upd]

theorem upd_other {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) {x : α}
    (h : x ≠ a) : upd f a v x = f x := by simp [upd, h]

/-- Point updates at distinct places commute. -/
theorem upd_comm {α β : Type} [DecidableEq α] (f : α → β) {a₁ a₂ : α} (v₁ v₂ : β)
    (h : a₁ ≠ a₂) : upd (upd f a₁ v₁) a₂ v₂ = upd (upd f a₂ v₂) a₁ v₁ := by
  funext x
  by_cases h₁ : x = a₁ <;> by_cases h₂ : x = a₂ <;> simp_all [upd]

/-! ## Signature -/

/-- The types a particular architecture must supply. As in `CMC.lean`, plus `epi`.

[META] DECIDED (Laird, 2026-10-28): "let's be conservative and leave the option for two
memories, or one that supports episodic functions." The extension designates one
declarative memory, `epi`, that receives episodic recordings. With
`DMem := {semantic, episodic}` and `epi := episodic` this is Soar's arrangement; with
`DMem := Unit` the single declarative memory supports episodic functions, which is the
Sigma (and partly ACT-R) arrangement.

> "we now include separate semantic and episodic long-term memories … the mechanisms for
> storing and retrieving information in episodic memory may differ from those used in
> semantic memory." — [LLRS] §4.3 -/
structure Sig where
  Sym  : Type
  Val  : Type
  PMod : Type
  MMod : Type
  DMem : Type
  Input  : Type
  PLearn : Type
  MLearn : Type
  Output : Type
  /-- Kinds of numeric metadata: fixed within this architecture. -/
  MK : Type
  [decMK : DecidableEq MK]
  utilityK : MK
  frequencyK : MK
  recencyK : MK
  /-- The declarative memory that receives episodic recordings. -/
  epi : DMem
  [decP : DecidableEq PMod]
  [decM : DecidableEq MMod]
  [decD : DecidableEq DMem]

attribute [instance] Sig.decP Sig.decM Sig.decD Sig.decMK

variable {σ : Sig}

/-! ## Content (unchanged from `CMC.lean`)

Definitions carried over unchanged keep only short comments here; their full documentation,
source quotations and decisions are in `CMC.lean`. -/

/-- *Numeric* metadata: not examinable by rules (DECIDED 2026-10-28). -/
abbrev Meta (σ : Sig) := σ.MK → Option σ.Val

/-- A relation over symbols (CONFIRMED 2026-10-28). -/
structure Rel (σ : Sig) where
  pred : σ.Sym
  args : List σ.Sym

/-- A symbol structure with its numeric metadata (CONFIRMED 2026-10-28). -/
structure Elem (σ : Sig) where
  rel  : Rel σ
  meta : Meta σ

/-! ## Working memory with process-data areas -/

/-- Parts of a perceptual buffer: what is perceived, and the module's process data. -/
inductive PPart where
  | content | process
  deriving DecidableEq

/-- Parts of a declarative buffer: cue, retrieved result, and the module's process data. -/
inductive DPart where
  | cue | result | process
  deriving DecidableEq

/-- Parts of a motor buffer: the command, and the module's process data. -/
inductive MPart where
  | command | process
  deriving DecidableEq

/-- Locations in working memory.

> "Our first extension to the CMC provides partial access to the internal states of modules
> by expanding the existing buffers in working memory and adding new buffers for every
> module, both existing (procedural and working memory) and new (semantic and episodic
> memory). … these additional buffers hold architecturally generated data that summarizes
> each module's processing state." — [LLRS] §4.2

[META] DECIDED (Laird, 2026-10-28):
* Every module gets a *process-data area*. Modules that already had buffers (perception,
  declarative memories, motor) gain a process part beside their existing parts; procedural
  memory and working memory get process-only buffers (`procProcess`, `wmProcess`).
* Process data is written *only* by the architecture; procedural memory can never write
  it, and forgetting cannot remove it. Each report *replaces* the previous one ("it
  captures a snapshot of the module's current state", [LLRS] §4.2).
* Status signals move to the process areas: retrieval failure, confidence and partiality go
  in the declarative process part, so the result part holds only what was retrieved; motor
  success or failure goes in the motor process part, and the motor buffer has no result
  part.
* Process data may be quantitative ("as in surprise"): architecture-generated structures may
  include symbols that denote graded values. Raw numeric metadata on memory elements is
  still never delivered to working memory.

The region (goals, intermediate results, task models) is unchanged from `CMC.lean`. -/
inductive Loc (P M D : Type) where
  | percept : P → PPart → Loc P M D
  | motor   : M → MPart → Loc P M D
  | decl    : D → DPart → Loc P M D
  /-- Procedural memory's process data: e.g., failure to select. -/
  | procProcess : Loc P M D
  /-- Working memory's process data: task-independent appraisals. -/
  | wmProcess : Loc P M D
  /-- The region of working memory not associated with any module. -/
  | region  : Loc P M D
  deriving DecidableEq

abbrev L (σ : Sig) := Loc σ.PMod σ.MMod σ.DMem

/-- Locations written only by the architecture: every process area, and declarative
results. Procedural memory may not write them and forgetting may not remove from them. -/
def Loc.archWritten {P M D : Type} : Loc P M D → Bool
  | .percept _ .process => true
  | .motor _ .process => true
  | .decl _ .result => true
  | .decl _ .process => true
  | .procProcess => true
  | .wmProcess => true
  | _ => false

/-- Working memory: the contents of each location. -/
abbrev WM (σ : Sig) := L σ → List (Elem σ)

/-- The symbolic content of working memory, metadata erased. -/
def symView (w : WM σ) : L σ → List (Rel σ) := fun b => (w b).map Elem.rel

theorem symView_upd_other (w : WM σ) (a : L σ) (v : List (Elem σ)) {ℓ : L σ} (h : ℓ ≠ a) :
    symView (upd w a v) ℓ = symView w ℓ := by
  simp [symView, upd_other _ _ _ h]

/-! ## Procedural memory -/

/-- A predicate on working memory that ignores numeric metadata (DECIDED 2026-10-28).
Process data, being symbolic structures in working memory, *is* visible to rules: that is
how metareasoning is triggered.

> "The knowledge for monitoring is typically represented as procedural knowledge that tests
> for appropriate structures in working memory, matching alongside the rules for base-level
> reasoning within the same cognitive cycle." — [LLRS] §4 -/
def MetaBlind (c : WM σ → Prop) : Prop :=
  ∀ w₁ w₂ : WM σ, symView w₁ = symView w₂ → (c w₁ ↔ c w₂)

structure Rule (σ : Sig) where
  cond : WM σ → Prop
  act  : WM σ → WM σ
  meta : Meta σ

abbrev ProcMem (σ : Sig) := List (Rule σ)
abbrev Act (σ : Sig) := WM σ → WM σ

/-- Why selection failed.

> "Procedural Memory: Signals of failure to select or carry out a decision, such as a set of
> competing or conflicting actions" — [LLRS] §4.2
>
> "such as multiple actions being retrieved but insufficient or conflicting knowledge to
> choose between them, or no progress being made with the previously selected action."
> — [LLRS] §5

[META] DECIDED (Laird, 2026-10-28): all four reasons are in scope for the CMC extension,
including no progress with the previously selected action. -/
inductive SelFail where
  | noCandidates | tie | conflict | noProgress
  deriving DecidableEq

/-- The outcome of selection: one deliberate act, or a failure with its reason. -/
inductive Outcome (σ : Sig) where
  | act  (a : Act σ)
  | fail (r : SelFail)

def Outcome.failure : Outcome σ → Option SelFail
  | .act _ => none
  | .fail r => some r

def Outcome.apply : Outcome σ → WM σ → WM σ
  | .act a, w => a w
  | .fail _, w => w

/-! ## Declarative memory -/

structure DeclMem (σ : Sig) where
  elems : List (Elem σ)

/-! ## State -/

structure State (σ : Sig) where
  wm : WM σ
  pm : ProcMem σ
  dm : σ.DMem → DeclMem σ
  lastCycle : Option (WM σ × WM σ)
  ps : σ.PMod → σ.PLearn
  ms : σ.MMod → σ.MLearn

/-! ## Architecture -/

/-- An architecture conforming to the CMC with metacognition.

No field is a metacognitive module. Every new field is either a report of a module's own
process state, episodic recording, or the metadata effect of retrieval.

> "In our proposal, there are no structural boundaries between base-level reasoning and
> metareasoning." — [LLRS] §6 -/
structure Arch (σ : Sig) where
  /-- **Selection**: one deliberate act, or a reported failure. -/
  select : ProcMem σ → WM σ → Outcome σ
  /-- Procedural memory never writes architecture-written locations (process areas and
  declarative results). -/
  select_respects_arch : ∀ pm w a, select pm w = .act a →
      ∀ ℓ : L σ, ℓ.archWritten = true → a w ℓ = w ℓ
  /-- **Procedural process data**: what the architecture reports about the cycle, given the
  failure reason if any. Written on every cycle; it replaces the previous report.

  [META] DECIDED (Laird, 2026-10-28): replaces the 2017 model's silence about selection
  failure. -/
  procReport : Option SelFail → List (Elem σ)
  /-- **Declarative retrieval**: from the memory and the cue, the result and the process
  data (failure, confidence, partiality; e.g., a tip-of-the-tongue state).

  Episodic retrieval goes through the same step for `σ.epi`. A retrieved episode appears in
  the episodic buffer's result area, never in the region, which keeps past and present
  apart.

  [META] DECIDED (Laird, 2026-10-28): temporal navigation (retrieving the next or previous
  episode relative to the last one retrieved) is part of the extension. It is expressed
  through the cue and the episodic memory's own metadata, which this function may use. -/
  retrieve : (d : σ.DMem) → DeclMem σ → List (Elem σ) → List (Elem σ) × List (Elem σ)
  /-- **Metadata effect of retrieval**: the act of retrieval updates metadata (e.g.,
  recency and frequency) of what is retrieved.

  > "retrievals from declarative memory (which update metadata such as recency and
  > frequency)" — [LLRS] §4

  [META] DECIDED (Laird, 2026-10-28). -/
  retrieveTouch : (d : σ.DMem) → DeclMem σ → List (Elem σ) → DeclMem σ
  /-- Retrieval changes only metadata in declarative memory, never symbolic content. -/
  retrieveTouch_symbolic : ∀ d dm c,
      (retrieveTouch d dm c).elems.map Elem.rel = dm.elems.map Elem.rel
  /-- **Perception**: what is perceived, and perception's process data (failure, novelty,
  surprise, incompleteness; e.g., an occluded object that cannot be identified). -/
  perceive : (p : σ.PMod) → σ.PLearn → σ.Input → WM σ → List (Elem σ) × List (Elem σ)
  /-- **Motor**: external action from the command. -/
  motor : (m : σ.MMod) → σ.MLearn → List (Elem σ) → σ.Output
  /-- **Motor process data**: success or failure of execution, including the reason
  (e.g., a grasp that slips because the object is heavier than expected).

  [META] DECIDED (Laird, 2026-10-28): all motor status is process data. -/
  motorStatus : (m : σ.MMod) → σ.MLearn → List (Elem σ) → List (Elem σ)
  /-- **Working-memory appraisal hook**: task-independent appraisals of working memory and
  overall operation (e.g., surprise, inherent desirability).

  [META] DECIDED (Laird, 2026-10-28): the hook is kept; its content is left abstract.
  FUTURE: the emotion proposal (Rosenbloom et al., ICCM 2024) would refine it. -/
  appraise : WM σ → List (Elem σ)
  /-- **Episodic recording** of working memory into memory `σ.epi`.

  > "Episodic memory automatically stores the contents of working memory as a temporal
  > stream" — [LLRS] §4.3

  [META] DECIDED (Laird, 2026-10-28): recording happens on every cycle. Episodes can decay
  and be forgotten (through `decayDM` and forgetting, like any declarative content).
  Recording is not subject to `learnBound`: an episode is a snapshot of all of working
  memory, which the model does not bound. -/
  record : DeclMem σ → WM σ → DeclMem σ
  /-- Recording keeps every existing episode. -/
  record_incremental : ∀ dm w r, r ∈ dm.elems.map Elem.rel →
      r ∈ (record dm w).elems.map Elem.rel
  perceptLearn : (p : σ.PMod) → σ.PLearn → σ.Input → WM σ → σ.PLearn
  motorLearn : (m : σ.MMod) → σ.MLearn → List (Elem σ) → σ.Output → σ.MLearn
  compose : ProcMem σ → (WM σ × WM σ) → ProcMem σ
  rlTune : ProcMem σ → (WM σ × WM σ) → ProcMem σ
  declCreate : (d : σ.DMem) → DeclMem σ → (WM σ × WM σ) → DeclMem σ
  declTune : (d : σ.DMem) → DeclMem σ → (WM σ × WM σ) → DeclMem σ
  rlTune_symbolic : ∀ pm e, (rlTune pm e).map (fun r => (r.cond, r.act)) =
                            pm.map (fun r => (r.cond, r.act))
  rlTune_only_utility : ∀ pm e,
      (rlTune pm e).map (fun r k => if k = σ.utilityK then none else r.meta k) =
      pm.map (fun r k => if k = σ.utilityK then none else r.meta k)
  declTune_symbolic : ∀ d dm e, (declTune d dm e).elems.map Elem.rel = dm.elems.map Elem.rel
  learnBound : Nat
  declCreate_incremental : ∀ d dm e r, r ∈ dm.elems.map Elem.rel →
                                      r ∈ (declCreate d dm e).elems.map Elem.rel
  declCreate_bounded : ∀ d dm e,
      (declCreate d dm e).elems.length ≤ dm.elems.length + learnBound
  compose_bounded : ∀ pm e, ∃ new, new.length ≤ learnBound ∧ compose pm e = pm ++ new
  decayWM : Meta σ → Meta σ
  decayDM : Meta σ → Meta σ
  forgettable : Meta σ → Bool
  cycleMs : Nat := 50

def WFProc (pm : ProcMem σ) : Prop := ∀ r ∈ pm, MetaBlind r.cond

/-! ## Dynamics -/

/-- Working memory after one cognitive cycle: the outcome is applied, and procedural
memory's process area is overwritten with the architecture's report of the cycle. -/
def cycleWM (A : Arch σ) (pm : ProcMem σ) (w : WM σ) : WM σ :=
  upd ((A.select pm w).apply w) Loc.procProcess (A.procReport (A.select pm w).failure)

def decayElemWM (A : Arch σ) (e : Elem σ) : Elem σ := { e with meta := A.decayWM e.meta }
def decayElemDM (A : Arch σ) (e : Elem σ) : Elem σ := { e with meta := A.decayDM e.meta }

/-- Steps of the architecture. Interleaving semantics, as in `CMC.lean` (DECIDED
2026-10-28: the theory assumes simultaneity; interleaving is a modelling device).

VARIANT (not formalized; [META] DECIDED, Laird, 2026-10-28): impasses and substates. In
Soar and Sigma, a selection failure creates a substate that holds information about the
impasse, with the prior information structured in the top state; substates can stack, and
are removed when the impasse is resolved. This keeps meta-level reasoning (including over
retrieved episodes and hypothetical states) separate from the representation of the current
situation. [LLRS] §5 presents this as one architectural realization, not part of the CMC
extension; conceptually, the substate is the procedural process buffer. -/
inductive Step (A : Arch σ) : State σ → Option σ.Output → State σ → Prop where
  | perceive (s : State σ) (p : σ.PMod) (i : σ.Input) :
      Step A s none
        { s with wm := upd (upd s.wm (Loc.percept p .content)
                              (A.perceive p (s.ps p) i s.wm).1)
                           (Loc.percept p .process) (A.perceive p (s.ps p) i s.wm).2 }
  /-- Retrieval writes result and process data, and updates metadata in the memory. -/
  | retrieve (s : State σ) (d : σ.DMem) :
      Step A s none
        { s with wm := upd (upd s.wm (Loc.decl d .result)
                              (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).1)
                           (Loc.decl d .process) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).2,
                 dm := upd s.dm d (A.retrieveTouch d (s.dm d) (s.wm (Loc.decl d .cue))) }
  | motor (s : State σ) (m : σ.MMod) :
      Step A s (some (A.motor m (s.ms m) (s.wm (Loc.motor m .command))))
        { s with wm := upd s.wm (Loc.motor m .process)
                          (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .command))) }
  /-- Working-memory appraisal: writes the working-memory process area. -/
  | appraise (s : State σ) :
      Step A s none { s with wm := upd s.wm Loc.wmProcess (A.appraise s.wm) }
  | learnPercept (s : State σ) (p : σ.PMod) (i : σ.Input) :
      Step A s none { s with ps := upd s.ps p (A.perceptLearn p (s.ps p) i s.wm) }
  | learnMotor (s : State σ) (m : σ.MMod) :
      Step A s none
        { s with ms := upd s.ms m (A.motorLearn m (s.ms m) (s.wm (Loc.motor m .command))
                                     (A.motor m (s.ms m) (s.wm (Loc.motor m .command)))) }
  /-- A cognitive cycle: base-level reasoning and metareasoning alike. The outcome is
  applied, procedural process data is reported, and the resulting working memory is
  recorded in episodic memory. -/
  | cycle (s : State σ) :
      Step A s none
        { s with wm := cycleWM A s.pm s.wm,
                 lastCycle := some (s.wm, cycleWM A s.pm s.wm),
                 dm := upd s.dm σ.epi (A.record (s.dm σ.epi) (cycleWM A s.pm s.wm)) }
  | learnCompose (s : State σ) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with pm := A.compose s.pm e }
  | learnRL (s : State σ) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with pm := A.rlTune s.pm e }
  | learnCreate (s : State σ) (d : σ.DMem) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with dm := upd s.dm d (A.declCreate d (s.dm d) e) }
  | learnTune (s : State σ) (d : σ.DMem) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with dm := upd s.dm d (A.declTune d (s.dm d) e) }
  | decay (s : State σ) :
      Step A s none { s with wm := fun b => (s.wm b).map (decayElemWM A),
                             dm := fun d => ⟨(s.dm d).elems.map (decayElemDM A)⟩ }
  /-- Forgetting from working memory: never from architecture-written locations. -/
  | forgetWM (s : State σ) (b : L σ) (hb : b.archWritten = false) :
      Step A s none { s with wm := upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta)) }
  | forgetDecl (s : State σ) (d : σ.DMem) :
      Step A s none
        { s with dm := upd s.dm d ⟨(s.dm d).elems.filter (fun e => !A.forgettable e.meta)⟩ }

/-! ## Labelled, deterministic execution (for whole-run reasoning) -/

inductive Label (σ : Sig) where
  | perceive (p : σ.PMod) (i : σ.Input)
  | retrieve (d : σ.DMem)
  | motor (m : σ.MMod)
  | appraise
  | learnPercept (p : σ.PMod) (i : σ.Input)
  | learnMotor (m : σ.MMod)
  | cycle
  | compose
  | rl
  | create (d : σ.DMem)
  | tune (d : σ.DMem)
  | decay
  | forgetWM (b : L σ)
  | forgetDecl (d : σ.DMem)

def Label.isRetrieve : Label σ → Bool
  | .retrieve _ => true
  | _ => false

def exec (A : Arch σ) : Label σ → State σ → State σ × Option σ.Output
  | .perceive p i, s =>
      ({ s with wm := upd (upd s.wm (Loc.percept p .content) (A.perceive p (s.ps p) i s.wm).1)
                          (Loc.percept p .process) (A.perceive p (s.ps p) i s.wm).2 }, none)
  | .retrieve d, s =>
      ({ s with wm := upd (upd s.wm (Loc.decl d .result) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).1)
                          (Loc.decl d .process) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).2,
                dm := upd s.dm d (A.retrieveTouch d (s.dm d) (s.wm (Loc.decl d .cue))) }, none)
  | .motor m, s =>
      ({ s with wm := upd s.wm (Loc.motor m .process) (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .command))) },
       some (A.motor m (s.ms m) (s.wm (Loc.motor m .command))))
  | .appraise, s => ({ s with wm := upd s.wm Loc.wmProcess (A.appraise s.wm) }, none)
  | .learnPercept p i, s => ({ s with ps := upd s.ps p (A.perceptLearn p (s.ps p) i s.wm) }, none)
  | .learnMotor m, s =>
      ({ s with ms := upd s.ms m (A.motorLearn m (s.ms m) (s.wm (Loc.motor m .command))
                                   (A.motor m (s.ms m) (s.wm (Loc.motor m .command)))) }, none)
  | .cycle, s =>
      ({ s with wm := cycleWM A s.pm s.wm, lastCycle := some (s.wm, cycleWM A s.pm s.wm),
                dm := upd s.dm σ.epi (A.record (s.dm σ.epi) (cycleWM A s.pm s.wm)) }, none)
  | .compose, s => match s.lastCycle with
      | some e => ({ s with pm := A.compose s.pm e }, none)
      | none => (s, none)
  | .rl, s => match s.lastCycle with
      | some e => ({ s with pm := A.rlTune s.pm e }, none)
      | none => (s, none)
  | .create d, s => match s.lastCycle with
      | some e => ({ s with dm := upd s.dm d (A.declCreate d (s.dm d) e) }, none)
      | none => (s, none)
  | .tune d, s => match s.lastCycle with
      | some e => ({ s with dm := upd s.dm d (A.declTune d (s.dm d) e) }, none)
      | none => (s, none)
  | .decay, s =>
      ({ s with wm := fun b => (s.wm b).map (decayElemWM A),
                dm := fun d => ⟨(s.dm d).elems.map (decayElemDM A)⟩ }, none)
  | .forgetWM b, s =>
      if b.archWritten then (s, none)
      else ({ s with wm := upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta)) }, none)
  | .forgetDecl d, s =>
      ({ s with dm := upd s.dm d ⟨(s.dm d).elems.filter (fun e => !A.forgettable e.meta)⟩ }, none)

def execAll (A : Arch σ) : List (Label σ) → State σ → State σ × List (Option σ.Output)
  | [], s => (s, [])
  | l :: ls, s =>
      let r := exec A l s
      let rs := execAll A ls r.1
      (rs.1, r.2 :: rs.2)

/-! ## Theorems -/

section Theorems
variable {A : Arch σ}

/-- Every step is the execution of some label. -/
theorem step_is_exec {s t : State σ} {o : Option σ.Output} (h : Step A s o t) :
    ∃ l, exec A l s = (t, o) := by
  cases h with
  | perceive p i => exact ⟨.perceive p i, rfl⟩
  | retrieve d => exact ⟨.retrieve d, rfl⟩
  | motor m => exact ⟨.motor m, rfl⟩
  | appraise => exact ⟨.appraise, rfl⟩
  | learnPercept p i => exact ⟨.learnPercept p i, rfl⟩
  | learnMotor m => exact ⟨.learnMotor m, rfl⟩
  | cycle => exact ⟨.cycle, rfl⟩
  | learnCompose e he => exact ⟨.compose, by simp [exec, he]⟩
  | learnRL e he => exact ⟨.rl, by simp [exec, he]⟩
  | learnCreate d e he => exact ⟨.create d, by simp [exec, he]⟩
  | learnTune d e he => exact ⟨.tune d, by simp [exec, he]⟩
  | decay => exact ⟨.decay, rfl⟩
  | forgetWM b hb => exact ⟨.forgetWM b, by simp [exec, hb]⟩
  | forgetDecl d => exact ⟨.forgetDecl d, rfl⟩

/-- **Seriality, with reported failure.** Outside procedural memory's process area, a
cycle applies exactly the selected act, or changes nothing. -/
theorem cycle_serial (pm : ProcMem σ) (w : WM σ) (ℓ : L σ) (hℓ : ℓ ≠ Loc.procProcess) :
    (∃ a, A.select pm w = .act a ∧ cycleWM A pm w ℓ = a w ℓ) ∨
    (∃ r, A.select pm w = .fail r ∧ cycleWM A pm w ℓ = w ℓ) := by
  unfold cycleWM
  rw [upd_other _ _ _ hℓ]
  cases h : A.select pm w with
  | act a => exact Or.inl ⟨a, rfl, rfl⟩
  | fail r => exact Or.inr ⟨r, rfl, rfl⟩

/-- **Selection failure is reported.** After a cycle, procedural memory's process area holds
the architecture's report of the cycle's outcome, including the reason for any failure. -/
theorem cycle_reports (pm : ProcMem σ) (w : WM σ) :
    cycleWM A pm w Loc.procProcess = A.procReport (A.select pm w).failure :=
  upd_same _ _ _

/-- **No direct access to declarative memory**, unchanged from 2017. -/
theorem cycle_independent_of_decl (s₁ s₂ : State σ) (hw : s₁.wm = s₂.wm) (hp : s₁.pm = s₂.pm) :
    cycleWM A s₁.pm s₁.wm = cycleWM A s₂.pm s₂.wm := by
  rw [hw, hp]

/-- A cycle leaves every architecture-written location except procedural process data
unchanged. -/
theorem cycle_keeps_arch (pm : ProcMem σ) (w : WM σ) (ℓ : L σ) (ha : ℓ.archWritten = true)
    (hℓ : ℓ ≠ Loc.procProcess) : cycleWM A pm w ℓ = w ℓ := by
  unfold cycleWM
  rw [upd_other _ _ _ hℓ]
  cases h : A.select pm w with
  | act a => exact A.select_respects_arch pm w a h ℓ ha
  | fail r => rfl

/-- Which label is the architectural writer of each architecture-written location. -/
def Label.archOwns : Label σ → L σ → Bool
  | .perceive p _, ℓ => decide (ℓ = Loc.percept p .process)
  | .retrieve d, ℓ => decide (ℓ = Loc.decl d .result) || decide (ℓ = Loc.decl d .process)
  | .motor m, ℓ => decide (ℓ = Loc.motor m .process)
  | .appraise, ℓ => decide (ℓ = Loc.wmProcess)
  | .cycle, ℓ => decide (ℓ = Loc.procProcess)
  | _, _ => false

/-- A step that is not the owner of an architecture-written location leaves its symbolic
content unchanged. -/
theorem arch_untouched (l : Label σ) (s : State σ) (ℓ : L σ) (ha : ℓ.archWritten = true)
    (hown : l.archOwns ℓ = false) : symView (exec A l s).1.wm ℓ = symView s.wm ℓ := by
  cases l with
  | perceive p i =>
    have h1 : ℓ ≠ Loc.percept p .process := by simpa [Label.archOwns] using hown
    have h2 : ℓ ≠ Loc.percept p .content := by intro e; subst e; simp [Loc.archWritten] at ha
    simp only [exec]
    rw [symView_upd_other _ _ _ h1, symView_upd_other _ _ _ h2]
  | retrieve d =>
    have h : ¬(ℓ = Loc.decl d .result ∨ ℓ = Loc.decl d .process) := by
      simpa [Label.archOwns] using hown
    have h1 : ℓ ≠ Loc.decl d .process := fun e => h (Or.inr e)
    have h2 : ℓ ≠ Loc.decl d .result := fun e => h (Or.inl e)
    simp only [exec]
    rw [symView_upd_other _ _ _ h1, symView_upd_other _ _ _ h2]
  | motor m =>
    have h1 : ℓ ≠ Loc.motor m .process := by simpa [Label.archOwns] using hown
    simp only [exec]
    rw [symView_upd_other _ _ _ h1]
  | appraise =>
    have h1 : ℓ ≠ Loc.wmProcess := by simpa [Label.archOwns] using hown
    simp only [exec]
    rw [symView_upd_other _ _ _ h1]
  | cycle =>
    have h1 : ℓ ≠ Loc.procProcess := by simpa [Label.archOwns] using hown
    simp only [exec, symView]
    rw [cycle_keeps_arch s.pm s.wm ℓ ha h1]
  | learnPercept => rfl
  | learnMotor => rfl
  | compose => simp only [exec]; split <;> rfl
  | rl => simp only [exec]; split <;> rfl
  | create => simp only [exec]; split <;> rfl
  | tune => simp only [exec]; split <;> rfl
  | decay =>
    simp [exec, symView, List.map_map, Function.comp, decayElemWM]
  | forgetWM b =>
    by_cases hb : b.archWritten = true
    · simp [exec, hb]
    · have h1 : ℓ ≠ b := by intro e; subst e; exact hb ha
      have hb' : b.archWritten = false := by simpa using hb
      simp only [exec, hb', Bool.false_eq_true, ↓reduceIte]
      rw [symView_upd_other _ _ _ h1]
  | forgetDecl => rfl

/-- **Provenance of process data and results.** If any step changes the symbolic content of
an architecture-written location, that step was the location's own module reporting:
perception for its process area, retrieval for its result and process areas, the motor
module for its process area, appraisal for working memory's process area, and the cycle for
procedural memory's process area. No deliberate act can write process data, which is why it
is ground truth about its module.

> "In terms of veracity, accessibility, and scope, a module's process data is ground-truth
> and immediately available to procedural memory for reasoning" — [LLRS] §4.2 -/
theorem arch_provenance (l : Label σ) (s : State σ) (ℓ : L σ) (ha : ℓ.archWritten = true)
    (hne : symView (exec A l s).1.wm ℓ ≠ symView s.wm ℓ) : l.archOwns ℓ = true := by
  cases h : l.archOwns ℓ with
  | true => rfl
  | false => exact absurd (arch_untouched l s ℓ ha h) hne

/-- Step-level form of `arch_provenance`. -/
theorem arch_provenance_step {s t : State σ} {o : Option σ.Output} (h : Step A s o t)
    (ℓ : L σ) (ha : ℓ.archWritten = true) (hne : symView t.wm ℓ ≠ symView s.wm ℓ) :
    ∃ l, exec A l s = (t, o) ∧ l.archOwns ℓ = true := by
  obtain ⟨l, hl⟩ := step_is_exec h
  refine ⟨l, hl, arch_provenance (A := A) l s ℓ ha ?_⟩
  rw [hl]; exact hne

/-- **Process data is a snapshot.** Each report replaces the previous one. -/
theorem retrieve_replaces (s : State σ) (d : σ.DMem) :
    (exec A (.retrieve d) s).1.wm (Loc.decl d .process) =
      (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).2 ∧
    (exec A (.retrieve d) s).1.wm (Loc.decl d .result) =
      (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))).1 := by
  constructor
  · simp only [exec]; exact upd_same _ _ _
  · simp only [exec]
    rw [upd_other _ _ _ (by intro e; cases e), upd_same]

theorem motor_replaces (s : State σ) (m : σ.MMod) :
    (exec A (.motor m) s).1.wm (Loc.motor m .process) =
      A.motorStatus m (s.ms m) (s.wm (Loc.motor m .command)) := by
  simp only [exec]; exact upd_same _ _ _

theorem appraise_replaces (s : State σ) :
    (exec A .appraise s).1.wm Loc.wmProcess = A.appraise s.wm := by
  simp only [exec]; exact upd_same _ _ _

/-- **Retrieval changes only metadata in declarative memory.** -/
theorem retrieve_metadata_only (s : State σ) (d d' : σ.DMem) :
    ((exec A (.retrieve d) s).1.dm d').elems.map Elem.rel = (s.dm d').elems.map Elem.rel := by
  simp only [exec]
  by_cases h : d' = d
  · subst h; rw [upd_same]; exact A.retrieveTouch_symbolic _ _ _
  · rw [upd_other _ _ _ h]

/-- **Every cycle records an episode.** -/
theorem cycle_records (s : State σ) :
    (exec A .cycle s).1.dm σ.epi = A.record (s.dm σ.epi) (cycleWM A s.pm s.wm) := by
  simp only [exec]; exact upd_same _ _ _

/-- **Declarative content (including episodes) is removed only by forgetting.** Any step
other than forgetting from memory `d` keeps every relation in `d`. -/
theorem decl_content_kept (l : Label σ) (s : State σ) (d : σ.DMem)
    (hl : l ≠ .forgetDecl d) (r : Rel σ) (hr : r ∈ (s.dm d).elems.map Elem.rel) :
    r ∈ ((exec A l s).1.dm d).elems.map Elem.rel := by
  cases l with
  | retrieve d' => rw [retrieve_metadata_only]; exact hr
  | cycle =>
    simp only [exec]
    by_cases h : d = σ.epi
    · subst h; rw [upd_same]; exact A.record_incremental _ _ _ hr
    · rw [upd_other _ _ _ h]; exact hr
  | create d' =>
    simp only [exec]
    split
    · by_cases h : d = d'
      · subst h; simp only; rw [upd_same]; exact A.declCreate_incremental _ _ _ _ hr
      · simp only; rw [upd_other _ _ _ h]; exact hr
    · exact hr
  | tune d' =>
    simp only [exec]
    split
    · by_cases h : d = d'
      · subst h; simp only; rw [upd_same, A.declTune_symbolic]; exact hr
      · simp only; rw [upd_other _ _ _ h]; exact hr
    · exact hr
  | decay => simpa [exec, List.map_map, Function.comp, decayElemDM] using hr
  | forgetDecl d' =>
    have h : d ≠ d' := by intro e; subst e; exact hl rfl
    simp only [exec]; rw [upd_other _ _ _ h]; exact hr
  | compose => simp only [exec]; split <;> exact hr
  | rl => simp only [exec]; split <;> exact hr
  | forgetWM b => simp only [exec]; split <;> exact hr
  | perceive => exact hr
  | motor => exact hr
  | appraise => exact hr
  | learnPercept => exact hr
  | learnMotor => exact hr

/-- Locations where deliberate reasoning puts its content: the region and the cue parts of
buffers. -/
def Loc.deliberate {P M D : Type} : Loc P M D → Bool
  | .region => true
  | .decl _ .cue => true
  | .motor _ .command => true
  | _ => false

/-- **Metareasoning uses the same cognitive cycle.** If any step changes the symbolic
content of the region or of a cue, that step was a cognitive cycle or forgetting at that
location. Base-level reasoning and metareasoning therefore have the same, single source of
deliberate change: there is no metacognitive module.

> "metacognitive processing is not a distinct or restricted form of processing; it uses
> the same cognitive cycle and learning capabilities as other forms of reasoning."
> — [LLRS] §2 -/
theorem deliberate_only_by_cycle (l : Label σ) (s : State σ) (ℓ : L σ)
    (hd : ℓ.deliberate = true) (hne : symView (exec A l s).1.wm ℓ ≠ symView s.wm ℓ) :
    l = .cycle ∨ l = .forgetWM ℓ := by
  have hna : ℓ.archWritten = false := by
    cases ℓ with
    | percept p q => simp [Loc.deliberate] at hd
    | motor m q => cases q <;> simp_all [Loc.deliberate, Loc.archWritten]
    | decl d q => cases q <;> simp_all [Loc.deliberate, Loc.archWritten]
    | procProcess => simp [Loc.deliberate] at hd
    | wmProcess => simp [Loc.deliberate] at hd
    | region => rfl
  cases l with
  | cycle => exact Or.inl rfl
  | forgetWM b =>
    by_cases hb : b = ℓ
    · subst hb; exact Or.inr rfl
    · exfalso; apply hne
      by_cases hw : b.archWritten = true
      · simp [exec, hw]
      · have hw' : b.archWritten = false := by simpa using hw
        simp only [exec, hw', Bool.false_eq_true, ↓reduceIte]
        rw [symView_upd_other _ _ _ (fun e => hb e.symm)]
  | perceive p i =>
    exfalso; apply hne
    have h1 : ℓ ≠ Loc.percept p .process := by intro e; subst e; simp [Loc.deliberate] at hd
    have h2 : ℓ ≠ Loc.percept p .content := by intro e; subst e; simp [Loc.deliberate] at hd
    simp only [exec]; rw [symView_upd_other _ _ _ h1, symView_upd_other _ _ _ h2]
  | retrieve d =>
    exfalso; apply hne
    have h1 : ℓ ≠ Loc.decl d .process := by intro e; subst e; simp [Loc.deliberate] at hd
    have h2 : ℓ ≠ Loc.decl d .result := by intro e; subst e; simp [Loc.deliberate] at hd
    simp only [exec]; rw [symView_upd_other _ _ _ h1, symView_upd_other _ _ _ h2]
  | motor m =>
    exfalso; apply hne
    have h1 : ℓ ≠ Loc.motor m .process := by intro e; subst e; simp [Loc.deliberate] at hd
    simp only [exec]; rw [symView_upd_other _ _ _ h1]
  | appraise =>
    exfalso; apply hne
    have h1 : ℓ ≠ Loc.wmProcess := by intro e; subst e; simp [Loc.deliberate] at hd
    simp only [exec]; rw [symView_upd_other _ _ _ h1]
  | decay => exfalso; apply hne; simp [exec, symView, List.map_map, Function.comp, decayElemWM]
  | learnPercept => exact absurd rfl hne
  | learnMotor => exact absurd rfl hne
  | compose => exfalso; apply hne; simp only [exec]; split <;> rfl
  | rl => exfalso; apply hne; simp only [exec]; split <;> rfl
  | create => exfalso; apply hne; simp only [exec]; split <;> rfl
  | tune => exfalso; apply hne; simp only [exec]; split <;> rfl
  | forgetDecl => exact absurd rfl hne

/-- **Influence on long-term procedural memory is through learning only.** Neither
metareasoning nor base-level reasoning modifies procedural memory directly; only composition
and reinforcement learning do.

> "Neither metareasoning nor base-level reasoning modifies the architecture, and their
> influence on long-term memory is indirect, mediated by changes to working memory,
> retrievals from declarative memory …, and the architectural learning mechanisms."
> — [LLRS] §4 -/
theorem proc_change_is_learning (l : Label σ) (s : State σ)
    (hne : (exec A l s).1.pm ≠ s.pm) : l = .compose ∨ l = .rl := by
  cases l with
  | compose => exact Or.inl rfl
  | rl => exact Or.inr rfl
  | create => exfalso; apply hne; simp only [exec]; split <;> rfl
  | tune => exfalso; apply hne; simp only [exec]; split <;> rfl
  | forgetWM b => exfalso; apply hne; simp only [exec]; split <;> rfl
  | _ => exact absurd rfl hne

/-- **Acquisition requires a cycle.** Before any cycle has occurred, no step other than a
cycle (which records an episode) changes procedural memory or adds symbolic content to
declarative memory. -/
theorem acquisition_requires_cycle (l : Label σ) (s : State σ) (hc : l ≠ .cycle)
    (hn : s.lastCycle = none) :
    (exec A l s).1.pm = s.pm ∧
    ∀ d r, r ∈ ((exec A l s).1.dm d).elems.map Elem.rel → r ∈ (s.dm d).elems.map Elem.rel := by
  cases l with
  | cycle => exact absurd rfl hc
  | compose => simp [exec, hn]
  | rl => simp [exec, hn]
  | create => simp [exec, hn]
  | tune => simp [exec, hn]
  | retrieve d =>
    refine ⟨rfl, fun d' r hr => ?_⟩
    rw [retrieve_metadata_only] at hr; exact hr
  | decay =>
    refine ⟨rfl, fun d r hr => ?_⟩
    simpa [exec, List.map_map, Function.comp, decayElemDM] using hr
  | forgetDecl d' =>
    refine ⟨rfl, fun d r hr => ?_⟩
    simp only [exec] at hr
    by_cases hd : d = d'
    · subst hd
      rw [upd_same] at hr
      simp only [List.mem_map, List.mem_filter] at hr ⊢
      obtain ⟨e, ⟨he, _⟩, rfl⟩ := hr
      exact ⟨e, he, rfl⟩
    · rw [upd_other _ _ _ hd] at hr; exact hr
  | forgetWM b => simp only [exec]; split <;> exact ⟨rfl, fun _ _ h => h⟩
  | perceive => exact ⟨rfl, fun _ _ h => h⟩
  | motor => exact ⟨rfl, fun _ _ h => h⟩
  | appraise => exact ⟨rfl, fun _ _ h => h⟩
  | learnPercept => exact ⟨rfl, fun _ _ h => h⟩
  | learnMotor => exact ⟨rfl, fun _ _ h => h⟩

/-- Two states that agree on everything except declarative memory. -/
def AgreeExceptDM (s₁ s₂ : State σ) : Prop :=
  s₁.wm = s₂.wm ∧ s₁.pm = s₂.pm ∧ s₁.lastCycle = s₂.lastCycle ∧ s₁.ps = s₂.ps ∧ s₁.ms = s₂.ms

theorem exec_agree (l : Label σ) (hl : l.isRetrieve = false)
    {s₁ s₂ : State σ} (h : AgreeExceptDM s₁ s₂) :
    AgreeExceptDM (exec A l s₁).1 (exec A l s₂).1 ∧ (exec A l s₁).2 = (exec A l s₂).2 := by
  obtain ⟨w₁, p₁, d₁, c₁, ps₁, ms₁⟩ := s₁
  obtain ⟨w₂, p₂, d₂, c₂, ps₂, ms₂⟩ := s₂
  obtain ⟨hw, hp, hc, hps, hms⟩ := h
  simp only at hw hp hc hps hms
  subst hw hp hc hps hms
  cases l with
  | retrieve d => simp [Label.isRetrieve] at hl
  | compose => cases c₁ <;> simp [exec, AgreeExceptDM]
  | rl => cases c₁ <;> simp [exec, AgreeExceptDM]
  | create d => cases c₁ <;> simp [exec, AgreeExceptDM]
  | tune d => cases c₁ <;> simp [exec, AgreeExceptDM]
  | forgetWM b => by_cases hb : b.archWritten <;> simp [exec, AgreeExceptDM, hb]
  | _ => simp [exec, AgreeExceptDM]

/-- **Declarative knowledge reaches behavior only through retrieval** (carried over from
`CMC.lean`, now including episodic memory): two states that differ only in declarative
memory, episodes included, produce identical working memory and actions along any sequence
of steps without a retrieval. Past experience therefore informs metareasoning only after an
episodic retrieval delivers it. -/
theorem decl_influence_requires_retrieval (ls : List (Label σ))
    (hno : ∀ l ∈ ls, l.isRetrieve = false) {s₁ s₂ : State σ} (h : AgreeExceptDM s₁ s₂) :
    AgreeExceptDM (execAll A ls s₁).1 (execAll A ls s₂).1 ∧
    (execAll A ls s₁).2 = (execAll A ls s₂).2 := by
  induction ls generalizing s₁ s₂ with
  | nil => exact ⟨h, rfl⟩
  | cons l ls ih =>
    have hl := hno l (List.mem_cons_self l ls)
    have hrest : ∀ l' ∈ ls, l'.isRetrieve = false :=
      fun l' hl' => hno l' (List.mem_cons_of_mem l hl')
    obtain ⟨h1, ho⟩ := exec_agree (A := A) l hl h
    obtain ⟨h2, hos⟩ := ih hrest h1
    exact ⟨h2, by simp [execAll, ho, hos]⟩

/-- **Rule conditions are symbolic**, and process data is visible to them. -/
theorem match_ignores_metadata {pm : ProcMem σ} (hwf : WFProc pm) {r : Rule σ} (hr : r ∈ pm)
    {w₁ w₂ : WM σ} (h : symView w₁ = symView w₂) : r.cond w₁ ↔ r.cond w₂ :=
  hwf r hr w₁ w₂ h

theorem content_visible (w : WM σ) (ℓ : L σ) (e : Elem σ) (h : e ∈ w ℓ) :
    e.rel ∈ symView w ℓ :=
  List.mem_map_of_mem Elem.rel h

end Theorems

/-! ## Consistency: a minimal conforming architecture -/

namespace Toy

@[reducible] def σ₀ : Sig where
  Sym := Nat
  Val := Nat
  PMod := Unit
  MMod := Unit
  DMem := Bool          -- semantic (false) and episodic (true)
  Input := Unit
  PLearn := Unit
  MLearn := Unit
  Output := List Nat
  MK := Fin 3
  utilityK := 0
  frequencyK := 1
  recencyK := 2
  epi := true

def arch : Arch σ₀ where
  select := fun _ _ => .fail .noCandidates
  select_respects_arch := by intro _ _ _ h; cases h
  procReport := fun r => match r with
    | none => []
    | some _ => [⟨⟨0, []⟩, fun _ => none⟩]   -- "selection failed"
  retrieve := fun _ dm cue =>
    match cue with
    | [] => ([], [])
    | c :: _ =>
      match (dm.elems.filter (fun e => decide (e.rel.pred = c.rel.pred))).take 1 with
      | [] => ([], [⟨⟨1, []⟩, fun _ => none⟩])   -- process data: retrieval failed
      | r  => (r, [])
  retrieveTouch := fun _ dm _ => dm
  retrieveTouch_symbolic := by intro _ _ _; rfl
  perceive := fun _ _ _ _ => ([], [])
  motor := fun _ _ buf => buf.map (fun e => e.rel.pred)
  motorStatus := fun _ _ _ => []
  appraise := fun _ => []
  record := fun dm w => ⟨dm.elems ++ w .region⟩
  record_incremental := by intro _ _ _ h; simp only [List.map_append, List.mem_append]; exact Or.inl h
  perceptLearn := fun _ l _ _ => l
  motorLearn := fun _ l _ _ => l
  compose := fun pm _ => pm
  rlTune := fun pm _ => pm
  declCreate := fun _ dm _ => dm
  declTune := fun _ dm _ => dm
  rlTune_symbolic := by intro _ _; rfl
  rlTune_only_utility := by intro _ _; rfl
  declTune_symbolic := by intro _ _ _; rfl
  learnBound := 0
  declCreate_incremental := by intro _ _ _ _ h; exact h
  declCreate_bounded := by intro _ _ _; simp
  compose_bounded := by intro pm _; exact ⟨[], by simp, by simp⟩
  decayWM := id
  decayDM := id
  forgettable := fun _ => false

end Toy

/-! ## Coverage of the metacognition proposal ([LLRS])

| Claim | Status | Where |
|-------|--------|-------|
| No dedicated metacognitive modules; metareasoning uses the same cycle | by construction; proved that only cycles (and forgetting) change deliberate content | `Arch`, `Step`, `deliberate_only_by_cycle` |
| Process-state buffers for every module, architecturally generated | locations plus provenance theorem | `Loc`, `Loc.archWritten`, `arch_provenance`, `arch_provenance_step` |
| Process data is ground truth, a snapshot, immediately available | provenance; replacement; visible to rules | `arch_provenance`, `*_replaces`, `content_visible` |
| Procedural failure signals (competing, conflicting, no progress) | `SelFail`, reported every cycle | `Arch.procReport`, `cycle_reports`, `cycle_serial` |
| Perception, declarative, motor process data | process parts written by their modules | `Arch.perceive`, `Arch.retrieve`, `Arch.motorStatus` |
| Working-memory appraisals | abstract hook | `Arch.appraise`, `appraise_replaces` |
| Separate semantic and episodic memories | either two memories or one supporting episodic functions | `Sig.epi` |
| Episodic memory stores working memory as a temporal stream | recorded every cycle; kept until forgotten | `Arch.record`, `cycle_records`, `decl_content_kept` |
| Retrieved episodes do not interfere with the current situation | retrieval writes only its own result and process areas | `arch_provenance`, `deliberate_only_by_cycle` |
| Retrieval updates metadata | metadata-only touch | `Arch.retrieveTouch`, `retrieve_metadata_only` |
| Influence on long-term memory is indirect | only learning changes procedural memory; only retrieval brings declarative knowledge to behavior | `proc_change_is_learning`, `decl_influence_requires_retrieval` |
| Impasses and substates (Soar, Sigma) | VARIANT, not formalized | `Step` doc |
| Derived information (self-observation, other agents, recorded information) | not architectural: ordinary content acquired through perception and learning | — |
-/

end CMC.Meta
