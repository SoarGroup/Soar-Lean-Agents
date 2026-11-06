/-!
# The Common Model of Cognition (Standard Model of the Mind) — a Lean 4 draft

Sources
* [LLR17] Laird, J. E., Lebiere, C., & Rosenbloom, P. S. (2017). A Standard Model of the
  Mind. *AI Magazine* 38(4). Section numbers (§4.1 …) and Table 1 items (A.1 … D.2b)
  refer to this paper.
* [RLL17] Rosenbloom, P. S., Laird, J. E., & Lebiere, C. (2017). Précis of
  'A Standard Model of the Mind'. *Advances in Cognitive Systems*.

Conventions used in this file
* Every definition quotes the passage it formalizes.
* `CHOICE:` marks an interpretation the papers do not force. Each one is a decision the
  authors should confirm or overturn.
* `OPEN:` marks something the papers leave unresolved, which the formalization exposes.
* `NOT FORMALIZED:` marks a commitment that is empirical or about internal processing,
  and is recorded as an annotation rather than stated as a property.

Scope: the 2017 model only. Metacognition and emotion, added since, are not included
([LLR17] §6 lists them as gaps).

Style: the model is a *specification*, not an architecture. Everything an architecture
fills in (symbol types, how rules are integrated, how retrieval ranks candidates, …) is a
parameter. A particular architecture (Soar, ACT-R, Sigma) is an *instance* of `Arch`.
Commitments are either built into the types (so no instance can violate them) or stated
as proof obligations in `Arch` (so every instance must prove them).
-/

namespace CMC

/-! ## Utilities -/

/-- Point update of a function (core Lean has no `Function.update`). -/
def upd {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) : α → β :=
  fun x => if x = a then v else f x

theorem upd_same {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) :
    upd f a v a = v := by simp [upd]

theorem upd_other {α β : Type} [DecidableEq α] (f : α → β) (a : α) (v : β) {x : α}
    (h : x ≠ a) : upd f a v x = f x := by simp [upd, h]

/-! ## Signature: what the standard model leaves open -/

/-- The types a particular architecture must supply.

> "Each of the modules in Figure 4 can be seen as unitary or further decomposed into
> multiple modules or sub-modules, such as multiple perceptual and motor modalities,
> multiple working memory buffers, semantic vs. episodic declarative memory, and various
> stages of procedural matching, selection and execution." — [LLR17] §4.1

`PMod`, `MMod` and `DMem` index the perceptual modalities, motor modules and declarative
memories. `DMem := Unit` gives a single declarative memory (ACT-R);
`DMem := {semantic, episodic}` gives two (Soar).

OPEN: "There is not yet a consensus concerning whether there is a single uniform
declarative memory or whether there are two memories" ([LLR17] §4.2, Table 1 B.4a). Here it
is a parameter, so the formalization stays neutral. -/
structure Sig where
  /-- Symbols. -/
  Sym  : Type
  /-- Quantitative values carried by metadata (activations, utilities, frequencies, …). -/
  Val  : Type
  /-- Perceptual modalities (vision, audition, …). -/
  PMod : Type
  /-- Motor modules (arms, legs, …). -/
  MMod : Type
  /-- Declarative memories. -/
  DMem : Type
  /-- External input arriving at the senses (left unspecified by the model). -/
  Input  : Type
  /-- Internal, learnable state of a perceptual module (opaque to the rest of the model;
  "assumed to be predominantly non-symbolic in nature", [LLR17] §4.4). -/
  PLearn : Type
  /-- Internal, learnable state of a motor module (opaque to the rest of the model). -/
  MLearn : Type
  /-- External output produced by effectors. -/
  Output : Type
  /-- Architecture-defined *symbolic* metadata: a fixed set of status symbols that the
  architecture itself deposits in working-memory buffers, so that rules can test them.
  Examples: retrieval success or failure in a declarative buffer (ACT-R and Soar), the
  existence and type of a substate (Soar), acceptable preferences (Soar).

  DECIDED (Laird, 2026-10-28): there are two kinds of metadata. Numeric metadata on
  memory elements (activation, utility, …) is never examinable by rules, and its values
  are never delivered to working memory. Symbolic metadata is a fixed, architecture-defined
  set of symbols placed in buffers, and rules may test it like any other symbol. -/
  Signal : Type
  /-- Kinds of numeric metadata: fixed within this architecture. -/
  MK : Type
  [decMK : DecidableEq MK]
  /-- Required core kind: utility, carried by rules and tuned by reinforcement learning. -/
  utilityK : MK
  /-- Required core kind: frequency, carried by declarative elements. -/
  frequencyK : MK
  /-- Required core kind: recency, carried by declarative elements. -/
  recencyK : MK
  /-- How each signal appears as a symbol. -/
  sigSym : Signal → Sym
  sigSym_inj : ∀ a b, sigSym a = sigSym b → a = b
  [decP : DecidableEq PMod]
  [decM : DecidableEq MMod]
  [decD : DecidableEq DMem]

attribute [instance] Sig.decP Sig.decM Sig.decD Sig.decMK

variable {σ : Sig}

/-! ## B. Memory and content -/

/-! Kinds of quantitative metadata are a field of `Sig` (`Sig.MK`).

> "Frequency information is a pervasive form of metadata … Other examples of metadata
> include recency, co-occurrence, similarity, utility, and more general notions of
> activation." — [LLR17] §4.2
>
> "The set of available metadata for symbols and relations and the associated mechanisms
> are fixed within the architecture." — [LLR17] §4.2

DECIDED (Laird, 2026-10-28): the set of kinds is fixed *within* each architecture but may
vary across architectures; the standard model does not state what the set is. It does
require a core that the learning commitments depend on: utility on rules (where
reinforcement learning puts its weights) and frequency and recency on declarative
elements. -/

/-- *Numeric* metadata annotating one symbol structure: a value for some subset of the
kinds.

DECIDED (Laird, 2026-10-28): numeric metadata is not examinable. "ACT-R (and Soar) can
test information in retrieval buffers from long-term memories, but they cannot test
activations of structures in those long-term memories, nor do they get the activation."
Enforced by `MetaBlind`: rule conditions see only `symView`, which erases this field. -/
abbrev Meta (σ : Sig) := σ.MK → Option σ.Val

/-- A relation over symbols.

> "The core of this content is represented as relations over symbols." — [LLR17] §4.2
>
> "There is a strict distinction between domain data – symbols and relations – and such
> metadata. … relations cannot be defined over quantitative metadata." — [LLR17] §4.2

Commitment built into the types: `Rel` has only `Sym` arguments, and `Sym` and `Val` are
distinct types, so no relation can take a metadata value as an argument.

CONFIRMED (Laird, 2026-10-28): a relation is a predicate symbol plus an argument list. This
covers Soar triples (identifier, attribute, value) and ACT-R chunk slots; Sigma's predicates
fit too. -/
structure Rel (σ : Sig) where
  pred : σ.Sym
  args : List σ.Sym

/-- A symbol structure with its metadata (Table 1 B.1: "symbol structures and associated
quantitative metadata").

CONFIRMED (Laird, 2026-10-28): metadata is attached per relation instance. The paper says
metadata "annotates instances of symbols and relations"; per-symbol metadata is not
represented separately, because it can be encoded as metadata on a unary relation over that
symbol. -/
structure Elem (σ : Sig) where
  rel  : Rel σ
  meta : Meta σ

/-! ### Working memory -/

/-- The two parts of a module buffer that has a command/result structure: declarative
memories (cue and retrieved result) and motor modules (command and execution status). -/
inductive Part where
  | cue | result
  deriving DecidableEq

/-- Locations in working memory: the module buffers, plus one region that is not a buffer.

> "[Working memory] includes buffers for initiating retrievals from declarative memory and
> motor actions, as well as buffers for maintaining the results of perception and
> declarative memory retrieval. It also includes temporary information necessary for
> behavior production and problem solving, such as information about goals, intermediate
> results of a problem, and models of a task." — [LLR17] §4.2
>
> "Retrieval is initiated by the creation of a cue in the designated buffer in working
> memory, with the result being deposited in that buffer." — [LLR17] §4.2

DECIDED (Laird, 2026-10-28): one buffer per declarative memory, with substructure: a
*cue* part and a *result* part. The result part holds the retrieved structures together
with symbolic metadata about the retrieval (e.g., success or failure; see `Sig.Signal`).
`Loc.decl d Part.cue` and `Loc.decl d Part.result` name the two parts of the one buffer.

DECIDED (Laird, 2026-10-28): *buffers are module interfaces.* Each buffer is associated
with a module: a perceptual modality, a motor module or a declarative memory. The
"temporary information" (goals, intermediate results, task models) lives in a separate
`region` of working memory that is not associated with any module, and the model does not
call it a buffer: that is not the right concept. (ACT-R calls its version the imaginal
buffer; earlier versions had a goal buffer. Soar keeps it in one graph rooted in the state.)
Specifically:
1. Its internal structure is left to the architecture.
2. The model places no bound on its size; any capacity limit is an architecture parameter.
3. In the 2017 model only procedural memory (through cycles) and forgetting write it
   (`region_only_by_cycle_or_forgetting`). Structure written by the architecture, such as
   Soar substates, comes with the metacognition extension.
4. Goals are not architectural; they are content in the region.
5. Persistence is a variation point: an architecture may retract structures automatically
   when the conditions that created them no longer hold (Soar's i-support) without the
   model requiring it. Not formalized here.

OPEN: "[Working memory] can be considered as unitary, or consist of separate
modality-specific memories" ([LLR17] §4.1). A buffer decomposition covers both readings. -/
inductive Loc (P M D : Type) where
  /-- Buffer of a perceptual modality. -/
  | percept : P → Loc P M D
  /-- Buffer of a motor module (command in the cue part, execution status in the result
  part). -/
  | motor   : M → Part → Loc P M D
  /-- Buffer of a declarative memory (cue or result part). -/
  | decl    : D → Part → Loc P M D
  /-- The region of working memory not associated with any module: not a buffer. -/
  | region  : Loc P M D
  deriving DecidableEq

abbrev L (σ : Sig) := Loc σ.PMod σ.MMod σ.DMem

/-- Whether a location is the result area of a buffer (declarative result or motor status). -/
def Loc.isResult {P M D : Type} : Loc P M D → Bool
  | .decl _ .result => true
  | .motor _ .result => true
  | _ => false

/-- Whether a location is a module buffer (everything except the region). -/
def Loc.isBuffer {P M D : Type} : Loc P M D → Bool
  | .region => false
  | _ => true

/-- Working memory: the contents of each buffer and of the region.

> "Working memory provides a temporary global space within which symbol structures can be
> dynamically composed from the outputs of perception and long-term memories." — [LLR17] §4.2

DECIDED (Laird, 2026-10-28): the internal structure of buffers is unconstrained, except
that declarative (and motor) buffers have a cue area and a result area. Lists are only this
formalization's representation of "some collection of structures"; no theorem depends on
their order or multiplicity. -/
abbrev WM (σ : Sig) := L σ → List (Elem σ)

/-- The symbolic content of working memory, with all metadata erased. Used to state that
rule conditions are patterns over symbols (see `MetaBlind`). -/
def symView (w : WM σ) : L σ → List (Rel σ) := fun b => (w b).map Elem.rel

/-! ### Procedural memory -/

/-- A predicate on working memory that ignores metadata.

> "Rule conditions specify symbolic patterns over the contents of working memory"
> — [LLR17] §4.2
>
> "relations cannot be defined over quantitative metadata." — [LLR17] §4.2

DECIDED (Laird, 2026-10-28), option (c): rule conditions are blind to *numeric* metadata,
which enters only through selection, retrieval and learning ("with metadata influencing
the selection"). Rules may test *symbolic* metadata, the architecture-defined signals of
`Sig.Signal`, because those are ordinary relations in working memory and so are part of
`symView`.

Soar: only *acceptable* preferences are in working memory. Other preferences are held in
a separate preference memory that productions cannot test; here that memory is internal to
`Arch.select`.

OPEN: Sigma's position on this has not yet been checked.
-/
def MetaBlind (c : WM σ → Prop) : Prop :=
  ∀ w₁ w₂ : WM σ, symView w₁ = symView w₂ → (c w₁ ↔ c w₂)

/-- A rule.

> "procedural memory is instead based on pattern-directed invocation of actions, typically
> cast in the form of rules with conditions and actions. Rule conditions specify symbolic
> patterns over the contents of working memory and rule actions modify working memory,
> including the buffers used for cuing declarative memory and motor actions."
> — [LLR17] §4.2 (Table 1 B.3a–b)

The action is a function `WM → WM`, so "each action can perform multiple modifications to
working memory" ([LLR17] §4.1) is allowed. A rule cannot read or write anything except
working memory, which builds in "no direct access to the contents of long-term declarative
memory" ([LLR17] §4.1).

`meta` carries rule-level metadata such as utility (Table 1 B.1a: "rules with utilities"). -/
structure Rule (σ : Sig) where
  cond : WM σ → Prop
  act  : WM σ → WM σ
  meta : Meta σ

/-- Procedural memory. -/
abbrev ProcMem (σ : Sig) := List (Rule σ)

/-- A deliberate act: one transformation of working memory. -/
abbrev Act (σ : Sig) := WM σ → WM σ

/-! ### Declarative memory -/

/-- One declarative long-term memory.

> "Declarative memory is a long-term store for facts and concepts. It is structured as a
> persistent graph of symbolic relations, with metadata reflecting attributes such as
> recency and frequency of (co-)occurrence that are used in learning and retrieval."
> — [LLR17] §4.2

CONFIRMED (Laird, 2026-10-28): the "graph" is a collection of annotated relations, with the graph structure
implicit in shared symbols. -/
structure DeclMem (σ : Sig) where
  elems : List (Elem σ)

/-! ## The state of a mind -/

/-- The full architectural state: working memory plus the long-term memories, and the
record of the most recent cognitive cycle.

`lastCycle` is the "experience" that learning operates on; see the learning section. -/
structure State (σ : Sig) where
  wm : WM σ
  pm : ProcMem σ
  dm : σ.DMem → DeclMem σ
  /-- Working memory before and after the most recent cognitive cycle, if any. -/
  lastCycle : Option (WM σ × WM σ)
  /-- Learnable internal state of each perceptual module. -/
  ps : σ.PMod → σ.PLearn
  /-- Learnable internal state of each motor module. -/
  ms : σ.MMod → σ.MLearn

/-! ## The architecture: parameters plus proof obligations -/

/-- An architecture conforming to the standard model.

Data fields are the mechanisms the model leaves to each architecture. Proof fields are
commitments every conforming architecture must satisfy.

**A.2** "Processing is based on a small number of task-independent modules."
Built into the structure: the modules are perception (per `PMod`), motor (per `MMod`),
declarative memory (per `DMem`) and procedural memory, and nothing in `Arch` depends on a
task.

> "there is a strong commitment that no additional specialized architectural modules are
> necessary for performing complex cognitive activities such as planning, language
> processing and Theory of Mind" — [LLR17] §4.1 (Table 1 A.5)

Built in: `Arch` has no planning, language or other higher-level module. -/
structure Arch (σ : Sig) where
  /-- **Selection.** "Procedural memory induces the processing required to select a single
  deliberate act per cycle. … There is variation in how the knowledge from multiple
  matching rules is integrated together, but agreement that a single deliberate act is the
  result, with metadata influencing the selection." — [LLR17] §4.1, §4.2

  The integration method (Soar: proposal, preferences, decision, application; ACT-R:
  conflict resolution by utility) is the architecture's choice. Its type admits only
  procedural memory and working memory as inputs.

  DECIDED (Laird, 2026-10-28), option (a): the 2017 model is silent about selection
  failure. `none` means no act is selected this cycle and working memory is unchanged. In
  ACT-R no production fires.

  FUTURE (metacognition extension): metacognition adds a buffer that has a result part only,
  with no cue, into which the architecture deposits information about the state of
  processing, such as a failure to select. In Soar, a substate is conceptually that buffer.
  When added, this becomes a new `Loc` constructor written only by the architecture, with a
  provenance theorem analogous to `result_provenance`. -/
  select : ProcMem σ → WM σ → Option (Act σ)
  /-- **Procedural memory cannot write results.**

  DECIDED (Laird, 2026-10-28): procedural memory may write the cue part of a declarative
  buffer but never its result part. Only retrieval changes results, so a
  result in working memory is guaranteed to have come from declarative memory. The same
  holds for the status part of motor buffers, which only the motor module writes. -/
  select_respects_results : ∀ pm w a, select pm w = some a →
      (∀ d, a w (Loc.decl d .result) = w (Loc.decl d .result)) ∧
      (∀ m, a w (Loc.motor m .result) = w (Loc.motor m .result))
  /-- **Declarative retrieval** for memory `d`: given the memory and the cue currently in
  its buffer, the new buffer contents. Metadata (activation, recency, …) may drive the
  choice. -/
  retrieve : (d : σ.DMem) → DeclMem σ → List (Elem σ) → List (Elem σ)
  /-- **Perception** for modality `p`: from external input, and possibly the current
  working memory (top-down influence, Table 1 D.1d), the new contents of `p`'s buffer. -/
  perceive : (p : σ.PMod) → σ.PLearn → σ.Input → WM σ → List (Elem σ)
  /-- **Motor** module `m`: converts the contents of its buffer into external action
  (Table 1 D.2). -/
  motor : (m : σ.MMod) → σ.MLearn → List (Elem σ) → σ.Output
  /-- **Motor status**: the symbolic execution status the motor module reports in the result
  part of its buffer, given its command.

  DECIDED (Laird, 2026-10-28): motor buffers have status information available. As with
  retrieval results, status is written only by the motor module. -/
  motorStatus : (m : σ.MMod) → σ.MLearn → List (Elem σ) → List (Elem σ)
  /-- **Perceptual learning** (Table 1 D.1b): "Perceptual learning acquires new patterns and
  tunes existing ones." Updates the module's internal state from input, and possibly
  top-down information from working memory.

  DECIDED (Laird, 2026-10-28), option (b): stated as an abstract hook. The model commits to
  the existence of perceptual learning, not to how it works. -/
  perceptLearn : (p : σ.PMod) → σ.PLearn → σ.Input → WM σ → σ.PLearn
  /-- **Motor learning** (Table 1 D.2b): "Motor learning acquires new action patterns and
  tunes existing ones." Updates the module's internal state from the commanded structures
  and the action produced. Same status as `perceptLearn`. -/
  motorLearn : (m : σ.MMod) → σ.MLearn → List (Elem σ) → σ.Output → σ.MLearn
  /- **Attentional bottleneck** (Table 1 D.1c): "An attentional bottleneck constrains the
  amount of information that becomes available in working memory."

  DECIDED (Laird, 2026-10-28): NOT FORMALIZED. The model names a bottleneck but places no
  cap on it, so there is no property to state. (An earlier draft bounded the number of
  elements one perceptual update could deposit; that bound was not in the theory.)

  FUTURE: deliberate attention as a competency may motivate a more specific account. -/
  /- **C.1, all long-term content is learnable.**

  DECIDED (Laird, 2026-10-28), option (a): the claim is *syntactic* completeness, not
  semantic. Every representation of long-term knowledge (rules, rule metadata, declarative
  relations, declarative metadata) has an associated learning mechanism; these are the four
  fields below. There is no claim that all useful content of a given representation can be
  learned; the paper's wording is aspirational about content.

  FUTURE: a semantic version, namely that any rule or fact is reachable by learning given an
  initial procedural memory sufficient to interpret instruction, is a candidate theorem for a
  Soar instance with interactive task learning, not a commitment of the model. -/
  /-- **Procedural learning by composition** (Table 1 C.3b): "creates new rules from the
  composition of rule firings in some form". Input: the current rules and the most recent
  cycle's experience. -/
  compose : ProcMem σ → (WM σ × WM σ) → ProcMem σ
  /-- **Procedural learning by reinforcement** (Table 1 C.3a): "tunes the selection between
  competing deliberative acts via reinforcement learning", yielding "weights over action
  selection". -/
  rlTune : ProcMem σ → (WM σ × WM σ) → ProcMem σ
  /-- **Declarative learning, creation** (Table 1 C.4): "one to create new relations". -/
  declCreate : (d : σ.DMem) → DeclMem σ → (WM σ × WM σ) → DeclMem σ
  /-- **Declarative learning, tuning** (Table 1 C.4): "one to tune the associated
  metadata". -/
  declTune : (d : σ.DMem) → DeclMem σ → (WM σ × WM σ) → DeclMem σ
  /-- RL tuning changes only metadata: the symbolic content of every rule is preserved,
  so RL yields "weights over action selection" and nothing else.

  CONFIRMED (Laird, 2026-10-28): stated as preservation of the rules' conditions and
  actions, in order. -/
  rlTune_symbolic : ∀ pm e, (rlTune pm e).map (fun r => (r.cond, r.act)) =
                            pm.map (fun r => (r.cond, r.act))
  /-- Reinforcement learning tunes utility only: every other metadata kind on every rule is
  unchanged (Table 1 C.3a: "Reinforcement learning yields weights over action selection"). -/
  rlTune_only_utility : ∀ pm e,
      (rlTune pm e).map (fun r k => if k = σ.utilityK then none else r.meta k) =
      pm.map (fun r k => if k = σ.utilityK then none else r.meta k)
  /-- Metadata tuning in declarative memory changes only metadata (Table 1 C.4). -/
  declTune_symbolic : ∀ d dm e, (declTune d dm e).elems.map Elem.rel = dm.elems.map Elem.rel
  /-- **Bounded acquisition** (Table 1 C.2: "Learning occurs online and incrementally").

  DECIDED (Laird, 2026-10-28): learning mechanisms make *bounded additions* to long-term
  memory from a single experience. Learning never removes symbolic content; forgetting
  happens only through decay of numeric metadata (see `decay`, `forgettable`). Symbolic
  content in working memory and declarative memory can be removed as a result of decay.

  `learnBound` is the maximum number of new structures one learning event may add. -/
  learnBound : Nat
  /-- Declarative creation keeps every existing relation. -/
  declCreate_incremental : ∀ d dm e r, r ∈ dm.elems.map Elem.rel →
                                      r ∈ (declCreate d dm e).elems.map Elem.rel
  /-- Declarative creation adds at most `learnBound` structures. -/
  declCreate_bounded : ∀ d dm e,
      (declCreate d dm e).elems.length ≤ dm.elems.length + learnBound
  /-- Composition keeps every existing rule and adds at most `learnBound` new ones. -/
  compose_bounded : ∀ pm e, ∃ new, new.length ≤ learnBound ∧ compose pm e = pm ++ new
  /-- **Decay** of numeric metadata in working memory with the passage of time (for
  example, base-level activation). It acts only on metadata.

  DECIDED (Laird, 2026-10-28): working memory and declarative memory may have different
  decay functions. -/
  decayWM : Meta σ → Meta σ
  /-- **Decay** of numeric metadata in declarative memory. -/
  decayDM : Meta σ → Meta σ
  /-- **Forgetting threshold.** An element is forgettable when its numeric metadata has
  decayed below the architecture's threshold. Whether an element is forgettable depends on
  its metadata alone, never on its symbolic content.

  DECIDED (Laird, 2026-10-28): there is no procedural forgetting. Soar associates no
  activation with RL rules or chunks, and neither is ever removed; `compose_bounded`
  already guarantees existing rules are kept. -/
  forgettable : Meta σ → Bool
  /-- Typical cycle time in milliseconds when mapped to human behavior (Table 1 A.4).

  NOT FORMALIZED: "cognitive cycles operate at roughly 50 ms" ([LLR17] §4.1) is an
  empirical mapping, so it is recorded here and never used in a proof. -/
  cycleMs : Nat := 50

/-! ## Well-formed procedural memory -/

/-- Every rule's condition is a symbolic pattern (see `MetaBlind`). An invariant on the
states we consider well formed. -/
def WFProc (pm : ProcMem σ) : Prop := ∀ r ∈ pm, MetaBlind r.cond

/-! ## Dynamics -/

/-- The working memory that results from one cognitive cycle.

> "The heart of the standard model is the cognitive cycle. Procedural memory induces the
> processing required to select a single deliberate act per cycle." — [LLR17] §4.1

Seriality ("The restriction to selecting a single deliberate act per cycle yields a serial
bottleneck", [LLR17] §4.1) is built in: at most one act is applied. -/
def cycleWM (A : Arch σ) (pm : ProcMem σ) (w : WM σ) : WM σ :=
  match A.select pm w with
  | some a => a w
  | none   => w

/-- Apply working-memory decay to one element's metadata. -/
def decayElemWM (A : Arch σ) (e : Elem σ) : Elem σ := { e with meta := A.decayWM e.meta }

/-- Apply declarative-memory decay to one element's metadata. -/
def decayElemDM (A : Arch σ) (e : Elem σ) : Elem σ := { e with meta := A.decayDM e.meta }

/-- One step of the architecture.

> "Significant parallelism can also occur across components, each of which has its own
> time course and runs independently once initiated." — [LLR17] §4.1 (Table 1 A.3a)

DECIDED (Laird, 2026-10-28): the theory is more abstract and assumes modules can run
simultaneously. Interleaving is this formalization's modelling commitment, not the
theory's. Any module may take a step at any time, which covers the asynchronous case
(ACT-R, Soar; Table 1 A.3.a.i); Sigma's synchronous processing is one particular schedule.

Interleaving loses nothing when simultaneous steps read and write disjoint parts of the
state, because they then commute (see `retrieve_commute`). It is not exact when one step
reads what another writes: perception reads all of working memory (top-down influence,
D.1d), so a perception step and a simultaneous retrieval need not commute. A
true-concurrency semantics would be needed to model that case exactly.

NOT FORMALIZED: parallelism *within* modules (Table 1 A.3b), because "the details of the
internal processing of these components are not specified as part of the standard model"
([LLR17] §4.1).

`emit o` on the motor step records the external action produced. -/
inductive Step (A : Arch σ) : State σ → Option σ.Output → State σ → Prop where
  /-- Perception deposits its result in its own buffer and nowhere else (Table 1 D.1). -/
  | perceive (s : State σ) (p : σ.PMod) (i : σ.Input) :
      Step A s none
        { s with wm := upd s.wm (Loc.percept p) (A.perceive p (s.ps p) i s.wm) }
  /-- Declarative retrieval reads the cue part of its buffer and deposits the result,
  with its symbolic metadata, in the result part of the same buffer.

  The result area is *replaced*, not added to: a new retrieval discards the previous result
  (Laird, 2026-10-28). Result areas are therefore non-monotonic even though nothing is ever
  forgotten from them. The same holds for motor status. -/
  | retrieve (s : State σ) (d : σ.DMem) :
      Step A s none
        { s with wm := upd s.wm (Loc.decl d .result)
                          (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))) }
  /-- The motor module reads the command in the cue part of its buffer, acts in the world,
  and writes execution status in the result part (DECIDED, Laird, 2026-10-28). Buffers are
  thus uniform across declarative memory and motor; the metacognition buffer described
  under `Arch.select` would add a result-only case. -/
  | motor (s : State σ) (m : σ.MMod) :
      Step A s (some (A.motor m (s.ms m) (s.wm (Loc.motor m .cue))))
        { s with wm := upd s.wm (Loc.motor m .result)
                          (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .cue))) }
  /-- Perceptual learning (Table 1 D.1b): changes only the module's internal state. -/
  | learnPercept (s : State σ) (p : σ.PMod) (i : σ.Input) :
      Step A s none { s with ps := upd s.ps p (A.perceptLearn p (s.ps p) i s.wm) }
  /-- Motor learning (Table 1 D.2b): changes only the module's internal state. -/
  | learnMotor (s : State σ) (m : σ.MMod) :
      Step A s none
        { s with ms := upd s.ms m (A.motorLearn m (s.ms m) (s.wm (Loc.motor m .cue))
                                     (A.motor m (s.ms m) (s.wm (Loc.motor m .cue)))) }
  /-- A cognitive cycle: procedural memory selects and applies at most one deliberate act.
  The before/after pair is recorded as experience for learning. -/
  | cycle (s : State σ) :
      Step A s none
        { s with wm := cycleWM A s.pm s.wm, lastCycle := some (s.wm, cycleWM A s.pm s.wm) }
  /-- Procedural learning, a side effect of the last cycle (Table 1 C.2, C.3). -/
  | learnCompose (s : State σ) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with pm := A.compose s.pm e }
  | learnRL (s : State σ) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with pm := A.rlTune s.pm e }
  /-- Declarative learning, a side effect of the last cycle (Table 1 C.2, C.4). -/
  | learnCreate (s : State σ) (d : σ.DMem) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with dm := upd s.dm d (A.declCreate d (s.dm d) e) }
  | learnTune (s : State σ) (d : σ.DMem) (e : WM σ × WM σ) (h : s.lastCycle = some e) :
      Step A s none { s with dm := upd s.dm d (A.declTune d (s.dm d) e) }
  /-- Decay: numeric metadata of working-memory and declarative elements changes with time;
  symbolic content is untouched. -/
  | decay (s : State σ) :
      Step A s none { s with wm := fun b => (s.wm b).map (decayElemWM A),
                             dm := fun d => ⟨(s.dm d).elems.map (decayElemDM A)⟩ }
  /-- Forgetting from working memory: removes exactly the forgettable elements.

  DECIDED (Laird, 2026-10-28): there is no forgetting in buffer result areas (declarative
  results and motor status). -/
  | forgetWM (s : State σ) (b : L σ) (hb : b.isResult = false) :
      Step A s none { s with wm := upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta)) }
  /-- Forgetting from a declarative memory: removes exactly the forgettable elements. -/
  | forgetDecl (s : State σ) (d : σ.DMem) :
      Step A s none
        { s with dm := upd s.dm d ⟨(s.dm d).elems.filter (fun e => !A.forgettable e.meta)⟩ }

/-- Behavior over time: any finite sequence of steps.

> "Complex behavior, both external and internal, arises from sequences of such cycles."
> — [LLR17] §4.1 (Table 1 A.5)

Because `Step` has no other constructors, *every* behavior of a conforming architecture is
a sequence of module steps, cycles and learning steps. This is the formal content of "no
separate architectural module for global optimization (or planning)". -/
inductive Run (A : Arch σ) : State σ → List (Option σ.Output) → State σ → Prop where
  | done (s : State σ) : Run A s [] s
  | step {s t u : State σ} {o : Option σ.Output} {os : List (Option σ.Output)} :
      Step A s o t → Run A t os u → Run A s (o :: os) u

/-! ## Theorems: consequences of the commitments -/

section Theorems
variable {A : Arch σ}

/-- **Seriality.** A cycle applies exactly the selected act, or nothing. -/
theorem cycle_serial (pm : ProcMem σ) (w : WM σ) :
    (∃ a, A.select pm w = some a ∧ cycleWM A pm w = a w) ∨
    (A.select pm w = none ∧ cycleWM A pm w = w) := by
  unfold cycleWM
  cases h : A.select pm w with
  | none => exact Or.inr ⟨rfl, rfl⟩
  | some a => exact Or.inl ⟨a, rfl, rfl⟩

/-- **Procedural memory has no direct access to declarative memory** ([LLR17] §4.1). The
result of a cycle is the same in any two states that agree on working memory and
procedural memory, whatever their declarative memories hold. -/
theorem cycle_independent_of_decl (s₁ s₂ : State σ)
    (hw : s₁.wm = s₂.wm) (hp : s₁.pm = s₂.pm) :
    cycleWM A s₁.pm s₁.wm = cycleWM A s₂.pm s₂.wm := by
  rw [hw, hp]

/-- **Perception is local.** "[Perception and motor modules] are all restricted to
accessing and modifying their associated working memory buffers" ([LLR17] §4.1). A
perception step changes no buffer except its own. -/
theorem perceive_local (s : State σ) (p : σ.PMod) (i : σ.Input) (b : L σ)
    (hb : b ≠ Loc.percept p) :
    (upd s.wm (Loc.percept p) (A.perceive p (s.ps p) i s.wm)) b = s.wm b :=
  upd_other _ _ _ hb

/-- **Declarative memory is local.** A retrieval step changes nothing except the result
part of its own buffer; in particular it never alters the cue. -/
theorem retrieve_local (s : State σ) (d : σ.DMem) (b : L σ) (hb : b ≠ Loc.decl d .result) :
    (upd s.wm (Loc.decl d .result) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue)))) b = s.wm b :=
  upd_other _ _ _ hb

/-- Decay leaves the symbolic content of every buffer unchanged. -/
theorem decay_preserves_symbols (w : WM σ) :
    symView (fun b => (w b).map (decayElemWM A)) = symView w := by
  funext b
  simp [symView, List.map_map, Function.comp, decayElemWM]

/-- **Only procedural memory and forgetting change shared working memory.** If a step
changes the symbolic content of the region (goals, intermediate results, task
models), that step was a cognitive cycle or forgetting. -/
theorem region_only_by_cycle_or_forgetting {s t : State σ} {o : Option σ.Output}
    (h : Step A s o t) (hne : symView t.wm Loc.region ≠ symView s.wm Loc.region) :
    t = { s with wm := cycleWM A s.pm s.wm, lastCycle := some (s.wm, cycleWM A s.pm s.wm) } ∨
    ∃ b, t = { s with wm := upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta)) } := by
  cases h with
  | perceive p i =>
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.region) s.wm (Loc.percept p)
      (A.perceive p (s.ps p) i s.wm) (by intro h; cases h)]) hne
  | retrieve d =>
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.region) s.wm (Loc.decl d .result)
      (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))) (by intro h; cases h)]) hne
  | motor => exact absurd rfl hne
  | cycle => exact Or.inl rfl
  | learnCompose => exact absurd rfl hne
  | learnRL => exact absurd rfl hne
  | learnCreate => exact absurd rfl hne
  | learnTune => exact absurd rfl hne
  | decay => exact absurd (congrFun (decay_preserves_symbols (A := A) s.wm) Loc.region) hne
  | forgetWM b _ => exact Or.inr ⟨b, rfl⟩
  | forgetDecl => exact absurd rfl hne
  | learnPercept => exact absurd rfl hne
  | learnMotor => exact absurd rfl hne

/-- A cycle never changes the result part of a declarative buffer. -/
theorem cycle_keeps_results (pm : ProcMem σ) (w : WM σ) (d : σ.DMem) :
    cycleWM A pm w (Loc.decl d .result) = w (Loc.decl d .result) := by
  unfold cycleWM
  cases h : A.select pm w with
  | none => rfl
  | some a => exact (A.select_respects_results pm w a h).1 d

/-- A cycle never changes the status part of a motor buffer. -/
theorem cycle_keeps_status (pm : ProcMem σ) (w : WM σ) (m : σ.MMod) :
    cycleWM A pm w (Loc.motor m .result) = w (Loc.motor m .result) := by
  unfold cycleWM
  cases h : A.select pm w with
  | none => rfl
  | some a => exact (A.select_respects_results pm w a h).2 m

/-- **Provenance of motor status.** If a step changes the symbolic content of the status
part of motor buffer `m`, that step was an action by motor module `m`. -/
theorem status_provenance {s t : State σ} {o : Option σ.Output} (h : Step A s o t) (m : σ.MMod)
    (hne : symView t.wm (Loc.motor m .result) ≠ symView s.wm (Loc.motor m .result)) :
    t = { s with wm := upd s.wm (Loc.motor m .result)
                          (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .cue))) } := by
  cases h with
  | perceive p i =>
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.motor m .result) s.wm
      (Loc.percept p) (A.perceive p (s.ps p) i s.wm) (by intro h; cases h)]) hne
  | retrieve d =>
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.motor m .result) s.wm
      (Loc.decl d .result) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue)))
      (by intro h; cases h)]) hne
  | motor m' =>
    by_cases hm : m' = m
    · subst hm; rfl
    · exact absurd (by simp only [symView]; rw [upd_other (x := Loc.motor m .result) s.wm
        (Loc.motor m' .result) (A.motorStatus m' (s.ms m') (s.wm (Loc.motor m' .cue)))
        (by intro h; cases h; exact hm rfl)]) hne
  | cycle =>
    exact absurd (by simp only [symView]; rw [cycle_keeps_status]) hne
  | learnCompose => exact absurd rfl hne
  | learnRL => exact absurd rfl hne
  | learnCreate => exact absurd rfl hne
  | learnTune => exact absurd rfl hne
  | decay =>
    exact absurd (congrFun (decay_preserves_symbols (A := A) s.wm) (Loc.motor m .result)) hne
  | forgetWM b hr =>
    have hb : b ≠ Loc.motor m .result := by intro e; subst e; simp [Loc.isResult] at hr
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.motor m .result) s.wm b _
      (fun h => hb h.symm)]) hne
  | forgetDecl => exact absurd rfl hne
  | learnPercept => exact absurd rfl hne
  | learnMotor => exact absurd rfl hne

/-- **Provenance of retrieval results.** If a step changes the symbolic content of the
result part of declarative buffer `d`, that step was a retrieval from `d`. No deliberate act,
perception or motor step can place something there, and nothing is forgotten from it. -/
theorem result_provenance {s t : State σ} {o : Option σ.Output} (h : Step A s o t) (d : σ.DMem)
    (hne : symView t.wm (Loc.decl d .result) ≠ symView s.wm (Loc.decl d .result)) :
    t = { s with wm := upd s.wm (Loc.decl d .result)
                          (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))) } := by
  cases h with
  | perceive p i =>
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.decl d .result) s.wm
      (Loc.percept p) (A.perceive p (s.ps p) i s.wm) (by intro h; cases h)]) hne
  | retrieve d' =>
    by_cases hd : d' = d
    · subst hd; rfl
    · exact absurd (by simp only [symView]; rw [upd_other (x := Loc.decl d .result) s.wm
        (Loc.decl d' .result) (A.retrieve d' (s.dm d') (s.wm (Loc.decl d' .cue)))
        (by intro h; cases h; exact hd rfl)]) hne
  | motor => exact absurd rfl hne
  | cycle =>
    exact absurd (by simp only [symView]; rw [cycle_keeps_results]) hne
  | learnCompose => exact absurd rfl hne
  | learnRL => exact absurd rfl hne
  | learnCreate => exact absurd rfl hne
  | learnTune => exact absurd rfl hne
  | decay =>
    exact absurd (congrFun (decay_preserves_symbols (A := A) s.wm) (Loc.decl d .result)) hne
  | forgetWM b hr =>
    have hb : b ≠ Loc.decl d .result := by intro e; subst e; simp [Loc.isResult] at hr
    exact absurd (by simp only [symView]; rw [upd_other (x := Loc.decl d .result) s.wm b _
      (fun h => hb h.symm)]) hne
  | forgetDecl => exact absurd rfl hne
  | learnPercept => exact absurd rfl hne
  | learnMotor => exact absurd rfl hne

/-- **Results are replaced.** After a retrieval, the result area holds exactly the new
result; whatever was there before is gone. -/
theorem retrieve_replaces (s : State σ) (d : σ.DMem) :
    (upd s.wm (Loc.decl d .result) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))))
      (Loc.decl d .result) = A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue)) :=
  upd_same _ _ _

/-- **Status is replaced.** After a motor action, the status area holds exactly the new
status. -/
theorem motor_replaces (s : State σ) (m : σ.MMod) :
    (upd s.wm (Loc.motor m .result) (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .cue))))
      (Loc.motor m .result) = A.motorStatus m (s.ms m) (s.wm (Loc.motor m .cue)) :=
  upd_same _ _ _

/-- Point updates at distinct places commute. -/
theorem upd_comm {α β : Type} [DecidableEq α] (f : α → β) {a₁ a₂ : α} (v₁ v₂ : β)
    (h : a₁ ≠ a₂) : upd (upd f a₁ v₁) a₂ v₂ = upd (upd f a₂ v₂) a₁ v₁ := by
  funext x
  by_cases h₁ : x = a₁ <;> by_cases h₂ : x = a₂ <;> simp_all [upd]

/-- **Retrievals from different declarative memories commute**, so interleaving them is
equivalent to running them simultaneously. Each reads only its own cue and memory and
writes only its own result. -/
theorem retrieve_commute (s : State σ) {d₁ d₂ : σ.DMem} (h : d₁ ≠ d₂) :
    let w₁ := upd s.wm (Loc.decl d₁ .result) (A.retrieve d₁ (s.dm d₁) (s.wm (Loc.decl d₁ .cue)))
    let w₂ := upd s.wm (Loc.decl d₂ .result) (A.retrieve d₂ (s.dm d₂) (s.wm (Loc.decl d₂ .cue)))
    upd w₁ (Loc.decl d₂ .result) (A.retrieve d₂ (s.dm d₂) (w₁ (Loc.decl d₂ .cue))) =
    upd w₂ (Loc.decl d₁ .result) (A.retrieve d₁ (s.dm d₁) (w₂ (Loc.decl d₁ .cue))) := by
  intro w₁ w₂
  have c₂ : w₁ (Loc.decl d₂ .cue) = s.wm (Loc.decl d₂ .cue) :=
    upd_other _ _ _ (by intro e; cases e)
  have c₁ : w₂ (Loc.decl d₁ .cue) = s.wm (Loc.decl d₁ .cue) :=
    upd_other _ _ _ (by intro e; cases e)
  rw [c₁, c₂]
  exact upd_comm s.wm _ _ (by intro e; cases e; exact h rfl)

/-- **Long-term memories change only through learning.** Perception, retrieval, motor
steps and cycles leave procedural and declarative memory unchanged ([LLR17] §4.1: "All
long-term memories have one or more associated learning mechanisms that automatically
store, modify, or tune information"). -/
theorem ltm_stable_perceive (s : State σ) (p : σ.PMod) (i : σ.Input) :
    let t : State σ := { s with wm := upd s.wm (Loc.percept p) (A.perceive p (s.ps p) i s.wm) }
    t.pm = s.pm ∧ t.dm = s.dm := ⟨rfl, rfl⟩

theorem ltm_stable_cycle (s : State σ) :
    let t : State σ := { s with wm := cycleWM A s.pm s.wm,
                                lastCycle := some (s.wm, cycleWM A s.pm s.wm) }
    t.pm = s.pm ∧ t.dm = s.dm := ⟨rfl, rfl⟩

/-- **Learning is a side effect of performance** (Table 1 C.2). Before any cognitive cycle
has occurred, no step can change procedural memory or add symbolic content to declarative
memory. (Decay and forgetting can still occur.) -/
theorem no_acquisition_without_experience {s t : State σ} {o : Option σ.Output}
    (h : Step A s o t) (hn : s.lastCycle = none) :
    t.pm = s.pm ∧ ∀ d r, r ∈ (t.dm d).elems.map Elem.rel → r ∈ (s.dm d).elems.map Elem.rel := by
  cases h with
  | perceive => exact ⟨rfl, fun _ _ h => h⟩
  | retrieve => exact ⟨rfl, fun _ _ h => h⟩
  | motor => exact ⟨rfl, fun _ _ h => h⟩
  | cycle => exact ⟨rfl, fun _ _ h => h⟩
  | learnCompose e he => rw [hn] at he; cases he
  | learnRL e he => rw [hn] at he; cases he
  | learnCreate d e he => rw [hn] at he; cases he
  | learnTune d e he => rw [hn] at he; cases he
  | decay =>
    refine ⟨rfl, fun d r hr => ?_⟩
    simpa [List.map_map, Function.comp, decayElemDM] using hr
  | forgetWM => exact ⟨rfl, fun _ _ h => h⟩
  | learnPercept => exact ⟨rfl, fun _ _ h => h⟩
  | learnMotor => exact ⟨rfl, fun _ _ h => h⟩
  | forgetDecl d' =>
    refine ⟨rfl, fun d r hr => ?_⟩
    dsimp only at hr
    by_cases hd : d = d'
    · subst hd
      rw [upd_same] at hr
      simp only [List.mem_map, List.mem_filter] at hr ⊢
      obtain ⟨e, ⟨he, _⟩, rfl⟩ := hr
      exact ⟨e, he, rfl⟩
    · rw [upd_other _ _ _ hd] at hr
      exact hr

/-- **Forgetting removes only decayed elements** from a working-memory buffer. -/
theorem forgetWM_keeps (s : State σ) (b : L σ) (e : Elem σ) (he : e ∈ s.wm b)
    (hf : A.forgettable e.meta = false) :
    e ∈ (upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta))) b := by
  rw [upd_same]
  simp [List.mem_filter, he, hf]

/-- **Forgetting removes only decayed elements** from a declarative memory. -/
theorem forgetDecl_keeps (s : State σ) (d : σ.DMem) (e : Elem σ) (he : e ∈ (s.dm d).elems)
    (hf : A.forgettable e.meta = false) :
    e ∈ (upd s.dm d ⟨(s.dm d).elems.filter (fun e => !A.forgettable e.meta)⟩ d).elems := by
  rw [upd_same]
  simp [List.mem_filter, he, hf]

/-- **C.5, complex learning arises from the fixed simple mechanisms.**

> "More complex forms of learning involve combinations of the fixed set of simpler forms of
> learning" (Table 1 C.5). "Learning over longer time scales is assumed to arise from the
> accumulation of learning over short-term experiences. These longer time scales can include
> explicit deliberation over past experiences." — [LLR17] §4.3

DECIDED (Laird, 2026-10-28), option (b): the learning analogue of A.5. There is no
architectural module for complex learning, just as there is none for planning. Learning from
instruction, from examples or by reflection is deliberate processing over sequences of
cognitive cycles, whose results are captured by the fixed mechanisms.

Formal content: every change to procedural memory in a single step is composition or
reinforcement learning. (Declarative memory changes only by creation, tuning, decay or
forgetting; see the `Step` constructors.)

OPEN: the fixed set is expected to be incomplete. Perceptual and motor learning (D.1b,
D.2b) are assumed by the model but have no mechanisms here, and other mechanisms are likely
missing. -/
theorem proc_change_is_learning {s t : State σ} {o : Option σ.Output} (h : Step A s o t)
    (hne : t.pm ≠ s.pm) :
    (∃ e, s.lastCycle = some e ∧ t = { s with pm := A.compose s.pm e }) ∨
    (∃ e, s.lastCycle = some e ∧ t = { s with pm := A.rlTune s.pm e }) := by
  cases h with
  | learnCompose e he => exact Or.inl ⟨e, he, rfl⟩
  | learnRL e he => exact Or.inr ⟨e, he, rfl⟩
  | perceive => exact absurd rfl hne
  | retrieve => exact absurd rfl hne
  | motor => exact absurd rfl hne
  | cycle => exact absurd rfl hne
  | learnCreate => exact absurd rfl hne
  | learnTune => exact absurd rfl hne
  | decay => exact absurd rfl hne
  | forgetWM => exact absurd rfl hne
  | forgetDecl => exact absurd rfl hne
  | learnPercept => exact absurd rfl hne
  | learnMotor => exact absurd rfl hne

/-- **Rule conditions are symbolic.** In well-formed procedural memory, whether a rule
matches cannot depend on metadata. -/
theorem match_ignores_metadata {pm : ProcMem σ} (hwf : WFProc pm) {r : Rule σ} (hr : r ∈ pm)
    {w₁ w₂ : WM σ} (h : symView w₁ = symView w₂) : r.cond w₁ ↔ r.cond w₂ :=
  hwf r hr w₁ w₂ h

/-- **Symbolic signals are visible to rules.** Any element in a buffer, including an
architecture-defined signal, appears in the symbolic view that rule conditions read. -/
theorem buffer_content_visible (w : WM σ) (b : L σ) (e : Elem σ) (h : e ∈ w b) :
    e.rel ∈ symView w b :=
  List.mem_map_of_mem Elem.rel h

/-- **Reinforcement learning preserves well-formedness.** Because RL changes only rule
metadata, it cannot make a condition test metadata. -/
theorem rlTune_preserves_conditions (pm : ProcMem σ) (e : WM σ × WM σ) :
    (A.rlTune pm e).map Rule.cond = pm.map Rule.cond := by
  have h := congrArg (List.map Prod.fst) (A.rlTune_symbolic pm e)
  simpa [List.map_map] using h

/-! ## Derived prediction: declarative knowledge reaches behavior only through retrieval

To reason about whole runs of two different states, steps are given labels and a
deterministic execution function that mirrors `Step` (`step_is_exec` shows every `Step` is
one). The prediction is then a non-interference theorem: two states that differ only in
declarative memory produce identical working memory, identical procedural memory and
identical external actions along any sequence of steps that contains no retrieval. -/

/-- Labels for the kinds of step. -/
inductive Label (σ : Sig) where
  | perceive (p : σ.PMod) (i : σ.Input)
  | retrieve (d : σ.DMem)
  | motor (m : σ.MMod)
  | cycle
  | compose
  | rl
  | create (d : σ.DMem)
  | tune (d : σ.DMem)
  | decay
  | forgetWM (b : L σ)
  | forgetDecl (d : σ.DMem)
  | learnPercept (p : σ.PMod) (i : σ.Input)
  | learnMotor (m : σ.MMod)

/-- Whether a label is a declarative retrieval. -/
def Label.isRetrieve : Label σ → Bool
  | .retrieve _ => true
  | _ => false

/-- Deterministic execution of one labelled step, returning the new state and any external
action. Learning steps with no experience yet, and forgetting aimed at a result area, do
nothing (in `Step` they are simply not possible). -/
def exec (A : Arch σ) : Label σ → State σ → State σ × Option σ.Output
  | .perceive p i, s => ({ s with wm := upd s.wm (Loc.percept p) (A.perceive p (s.ps p) i s.wm) }, none)
  | .retrieve d, s =>
      ({ s with wm := upd s.wm (Loc.decl d .result) (A.retrieve d (s.dm d) (s.wm (Loc.decl d .cue))) }, none)
  | .motor m, s =>
      ({ s with wm := upd s.wm (Loc.motor m .result) (A.motorStatus m (s.ms m) (s.wm (Loc.motor m .cue))) },
       some (A.motor m (s.ms m) (s.wm (Loc.motor m .cue))))
  | .cycle, s =>
      ({ s with wm := cycleWM A s.pm s.wm, lastCycle := some (s.wm, cycleWM A s.pm s.wm) }, none)
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
      if b.isResult then (s, none)
      else ({ s with wm := upd s.wm b ((s.wm b).filter (fun e => !A.forgettable e.meta)) }, none)
  | .forgetDecl d, s =>
      ({ s with dm := upd s.dm d ⟨(s.dm d).elems.filter (fun e => !A.forgettable e.meta)⟩ }, none)
  | .learnPercept p i, s =>
      ({ s with ps := upd s.ps p (A.perceptLearn p (s.ps p) i s.wm) }, none)
  | .learnMotor m, s =>
      ({ s with ms := upd s.ms m (A.motorLearn m (s.ms m) (s.wm (Loc.motor m .cue))
                                   (A.motor m (s.ms m) (s.wm (Loc.motor m .cue)))) }, none)

/-- Execute a sequence of labelled steps, collecting external actions. -/
def execAll (A : Arch σ) : List (Label σ) → State σ → State σ × List (Option σ.Output)
  | [], s => (s, [])
  | l :: ls, s =>
      let r := exec A l s
      let rs := execAll A ls r.1
      (rs.1, r.2 :: rs.2)

/-- Every step of the architecture is the execution of some label. -/
theorem step_is_exec {A : Arch σ} {s t : State σ} {o : Option σ.Output} (h : Step A s o t) :
    ∃ l, exec A l s = (t, o) := by
  cases h with
  | perceive p i => exact ⟨.perceive p i, rfl⟩
  | retrieve d => exact ⟨.retrieve d, rfl⟩
  | motor m => exact ⟨.motor m, rfl⟩
  | cycle => exact ⟨.cycle, rfl⟩
  | learnCompose e he => exact ⟨.compose, by simp [exec, he]⟩
  | learnRL e he => exact ⟨.rl, by simp [exec, he]⟩
  | learnCreate d e he => exact ⟨.create d, by simp [exec, he]⟩
  | learnTune d e he => exact ⟨.tune d, by simp [exec, he]⟩
  | decay => exact ⟨.decay, rfl⟩
  | forgetWM b hb => exact ⟨.forgetWM b, by simp [exec, hb]⟩
  | forgetDecl d => exact ⟨.forgetDecl d, rfl⟩
  | learnPercept p i => exact ⟨.learnPercept p i, rfl⟩
  | learnMotor m => exact ⟨.learnMotor m, rfl⟩

/-- Two states that agree on everything except declarative memory. -/
def AgreeExceptDM (s₁ s₂ : State σ) : Prop :=
  s₁.wm = s₂.wm ∧ s₁.pm = s₂.pm ∧ s₁.lastCycle = s₂.lastCycle ∧ s₁.ps = s₂.ps ∧ s₁.ms = s₂.ms

/-- One non-retrieval step preserves agreement and produces the same external action. -/
theorem exec_agree {A : Arch σ} (l : Label σ) (hl : l.isRetrieve = false)
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
  | forgetWM b => by_cases hb : b.isResult <;> simp [exec, AgreeExceptDM, hb]
  | _ => simp [exec, AgreeExceptDM]

/-- **Derived prediction: declarative knowledge influences behavior only through
retrieval.** If two states differ only in declarative memory, then along any sequence of
steps containing no retrieval they produce identical working memory, procedural memory and
external actions.

Read with `cycle_independent_of_decl` (a cycle sees declarative memory only through working
memory) and `result_provenance` (only retrieval writes results): knowledge in declarative
memory can affect a deliberate act or an external action no earlier than the first cycle
after a retrieval that delivers it. -/
theorem decl_influence_requires_retrieval {A : Arch σ} (ls : List (Label σ))
    (hno : ∀ l ∈ ls, l.isRetrieve = false) {s₁ s₂ : State σ} (h : AgreeExceptDM s₁ s₂) :
    AgreeExceptDM (execAll A ls s₁).1 (execAll A ls s₂).1 ∧
    (execAll A ls s₁).2 = (execAll A ls s₂).2 := by
  induction ls generalizing s₁ s₂ with
  | nil => exact ⟨h, rfl⟩
  | cons l ls ih =>
    have hl := hno l (List.mem_cons_self l ls)
    have hrest : ∀ l' ∈ ls, l'.isRetrieve = false := fun l' hl' => hno l' (List.mem_cons_of_mem l hl')
    obtain ⟨h1, ho⟩ := exec_agree (A := A) l hl h
    obtain ⟨h2, hos⟩ := ih hrest h1
    exact ⟨h2, by simp [execAll, ho, hos]⟩


end Theorems

/-! ## Consistency: a minimal conforming architecture

A toy instance with one sense, one effector and one declarative memory. It shows that the
commitments in `Arch` are jointly satisfiable, i.e., the axioms are not contradictory.

Behavior: the first rule whose condition is decidable-true fires; retrieval returns the
first stored fact whose predicate matches the cue's; perception deposits at most one
element. -/

namespace Toy

/-- Natural numbers as symbols and values; `Unit` for every module index. -/
@[reducible] def σ₀ : Sig where
  Sym := Nat
  Val := Nat
  PMod := Unit
  MMod := Unit
  DMem := Unit
  Input := Unit
  Output := List Nat
  PLearn := Unit
  MLearn := Unit
  Signal := Unit            -- one signal: retrieval failure
  MK := Fin 3               -- utility, frequency, recency
  utilityK := 0
  frequencyK := 1
  recencyK := 2
  sigSym := fun _ => 0
  sigSym_inj := by intro a b _; cases a; cases b; rfl

def arch : Arch σ₀ where
  select := fun _ _ => none
  select_respects_results := by intro _ _ _ h; cases h
  retrieve := fun _ dm cue =>
    match cue with
    | [] => []
    | c :: _ =>
      match (dm.elems.filter (fun e => decide (e.rel.pred = c.rel.pred))).take 1 with
      | [] => [⟨⟨σ₀.sigSym (), []⟩, fun _ => none⟩]   -- symbolic signal: retrieval failed
      | r  => r
  perceive := fun _ _ _ _ => []
  motor := fun _ _ buf => buf.map (fun e => e.rel.pred)
  motorStatus := fun _ _ _ => []
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

/-- The empty procedural memory is well formed. -/
theorem wf_empty : WFProc ([] : ProcMem σ₀) := by intro r hr; cases hr

end Toy

/-! ## Coverage of Table 1 ([LLR17] §5)

| Item | Status | Where |
|------|--------|-------|
| A.1 bounded rationality, not optimality | NOT FORMALIZED (a stance, not a structural property) | — |
| A.2 small number of task-independent modules | by construction | `Arch`, `Sig` |
| A.3a parallel across modules (async/sync) | interleaving semantics | `Step` |
| A.3b parallel within modules | NOT FORMALIZED (internal processing) | — |
| A.4 sequential selection, ~50 ms cycle | seriality proved; timing annotated | `cycleWM`, `cycle_serial`, `Arch.cycleMs` |
| A.5 complex behavior from cycles, no planning module | by construction | `Run` |
| B.1 symbols plus quantitative metadata | types; kinds fixed per architecture, with a required core | `Rel`, `Elem`, `Meta`, `Sig.MK`, `rlTune_only_utility` |
| B.2 global communication via working memory | types plus locality theorems | `WM`, `perceive_local`, `retrieve_local`, `region_only_by_cycle_or_forgetting` |
| B.3 global control by procedural memory; rules alter WM | types | `Rule`, `Arch.select`, `cycle_independent_of_decl` |
| B.4 factual knowledge in declarative memory | types; one vs. two memories left open | `DeclMem`, `Sig.DMem` |
| C.1 all LTM content learnable | syntactic completeness: a mechanism exists for each representation (semantic completeness not claimed) | `Arch.compose`, `rlTune`, `declCreate`, `declTune` |
| C.2 online, incremental, side effect of performance | proved; bounded additions; forgetting only via metadata decay | `Step.learn*`, `no_acquisition_without_experience`, `*_bounded`, `Step.decay`, `Step.forget*`, `forget*_keeps` |
| C.3 procedural: RL plus composition | fields plus metadata-only RL | `rlTune_symbolic`, `rlTune_preserves_conditions` |
| C.4 declarative: create plus tune | fields plus metadata-only tuning | `declTune_symbolic` |
| C.5 complex learning from combinations of simple forms | no complex-learning module (analogue of A.5); fixed set expected to be incomplete | `proc_change_is_learning`, `Step` |
| D.1 perception into own buffer; modalities; learning | buffer locality; perceptual learning as an abstract hook | `Step.perceive`, `Arch.perceptLearn`, `Step.learnPercept` |
| D.1c attentional bottleneck | NOT FORMALIZED: named but uncapped | — |
| D.1d top-down influence | `perceive` reads WM | `Arch.perceive` |
| D.2 motor converts buffer contents to action | types; motor learning as an abstract hook | `Arch.motor`, `Arch.motorLearn`, `Step.motor`, `Step.learnMotor` |
-/

end CMC
