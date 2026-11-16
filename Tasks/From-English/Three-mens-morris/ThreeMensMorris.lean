/-
Three Men's Morris: a specification in Lean 4 (core library only).

The game as the Soar agent plays it (Morris-Soar-Summary, 31 October 2026):
* a 3 × 3 board; X moves first;
* each player places 3 pieces, one per turn, on empty points;
* once a player has placed all three, the player moves one piece per turn to an adjacent empty
  point: orthogonal neighbours, and every point to and from the centre;
* three of a player's pieces in a line (a row, a column or a diagonal) win at once;
* a player who must move a piece and has no legal move loses;
* the game is a draw after 30 plies without a winner.

Part 1 defines the game; Part 2 proves properties of it; Part 3 specifies the move choice of
the Soar agent (one-ply look-ahead with the agent's evaluation).
-/

namespace Morris

/-! ## Part 1. The game -/

inductive Player where
  | X | O
  deriving DecidableEq, Repr, Inhabited

def Player.other : Player → Player
  | .X => .O
  | .O => .X

/-- The nine points, numbered row by row:
```
0 - 1 - 2
| \ | / |
3 - 4 - 5
| / | \ |
6 - 7 - 8
```  -/
abbrev Cell := Fin 9

def Cell.x (c : Cell) : Nat := c.val % 3
def Cell.y (c : Cell) : Nat := c.val / 3

/-- The eight lines: three rows, three columns, two diagonals, each in board order. -/
def lines : List (Cell × Cell × Cell) :=
  [(0, 1, 2), (3, 4, 5), (6, 7, 8),
   (0, 3, 6), (1, 4, 7), (2, 5, 8),
   (0, 4, 8), (2, 4, 6)]

/-- Two points are adjacent when they are next to each other on a line. -/
def adj (a b : Cell) : Bool :=
  lines.any fun (p, q, r) => (a == p && b == q) || (a == q && b == p) ||
                             (a == q && b == r) || (a == r && b == q)

/-- The board: which player, if any, holds each point. -/
abbrev Board := Cell → Option Player

def Board.empty : Board := fun _ => none

def Board.set (b : Board) (c : Cell) (v : Option Player) : Board :=
  fun c' => if c' = c then v else b c'

structure State where
  board : Board
  /-- The player to move. -/
  turn : Player
  /-- Pieces each player still has to place. -/
  remaining : Player → Nat
  /-- Moves made so far. -/
  plies : Nat

def drawLimit : Nat := 30
def piecesPerPlayer : Nat := 3

def init : State :=
  { board := Board.empty, turn := .X, remaining := fun _ => piecesPerPlayer, plies := 0 }

inductive Move where
  /-- Put a piece on an empty point. -/
  | place (c : Cell)
  /-- Move a piece from one point to an adjacent empty point. -/
  | step (src dst : Cell)
  deriving DecidableEq, Repr

/-- Player `p` holds the three points of a line. -/
def hasLine (b : Board) (p : Player) : Bool :=
  lines.any fun (x, y, z) => b x == some p && b y == some p && b z == some p

/-- The moves the rules allow the player to move, ignoring whether the game is over. -/
def Allowed (s : State) : Move → Prop
  | .place c => s.remaining s.turn > 0 ∧ s.board c = none
  | .step a b => s.remaining s.turn = 0 ∧ s.board a = some s.turn ∧ s.board b = none ∧ adj a b = true

instance (s : State) (m : Move) : Decidable (Allowed s m) := by
  cases m <;> unfold Allowed <;> infer_instance

/-- The player to move is moving pieces and none of its pieces can move. -/
def blocked (s : State) : Bool :=
  s.remaining s.turn == 0 &&
    !(List.finRange 9).any fun a => (List.finRange 9).any fun b =>
      s.board a == some s.turn && s.board b == none && adj a b

/-- The winner, if any: a player with a line, else the opponent of a blocked player. -/
def winner (s : State) : Option Player :=
  if hasLine s.board .X then some .X
  else if hasLine s.board .O then some .O
  else if blocked s then some s.turn.other
  else none

def draw (s : State) : Bool := (winner s).isNone && s.plies ≥ drawLimit

def over (s : State) : Bool := (winner s).isSome || draw s

/-- A legal move: allowed by the rules in a game that is not over. -/
def Legal (s : State) (m : Move) : Prop := over s = false ∧ Allowed s m

instance (s : State) (m : Move) : Decidable (Legal s m) := by unfold Legal; infer_instance

def play (s : State) : Move → State
  | .place c =>
    { board := s.board.set c (some s.turn), turn := s.turn.other,
      remaining := fun p => if p = s.turn then s.remaining p - 1 else s.remaining p,
      plies := s.plies + 1 }
  | .step a b =>
    { board := (s.board.set a none).set b (some s.turn), turn := s.turn.other,
      remaining := s.remaining, plies := s.plies + 1 }

/-- All legal moves, places first, in point order. -/
def legalMoves (s : State) : List Move :=
  let cs := List.finRange 9
  ((cs.map Move.place) ++ cs.flatMap fun a => cs.map fun b => Move.step a b).filter
    fun m => decide (Legal s m)

/-- The states reachable from the initial state by legal moves. -/
inductive Reachable : State → Prop where
  | init : Reachable init
  | play {s : State} {m : Move} : Reachable s → Legal s m → Reachable (play s m)

/-! ## Part 2. Properties -/

theorem adj_symm : ∀ a b : Cell, adj a b = adj b a := by decide

theorem adj_irrefl : ∀ a : Cell, adj a a = false := by decide

/-- The centre is adjacent to every other point. -/
theorem adj_centre : ∀ a : Cell, a ≠ 4 → adj 4 a = true := by decide

/-- Each corner has three neighbours and each edge point three; the centre has eight. -/
theorem adj_degrees :
    ((List.finRange 9).map fun a => ((List.finRange 9).filter fun b => adj a b).length)
      = [3, 3, 3, 3, 8, 3, 3, 3, 3] := by decide

theorem mem_legalMoves (s : State) (m : Move) : m ∈ legalMoves s ↔ Legal s m := by
  unfold legalMoves
  simp only [List.mem_filter, decide_eq_true_eq]
  constructor
  · exact fun h => h.2
  · intro h
    refine ⟨?_, h⟩
    cases m with
    | place c => exact List.mem_append_left _ (List.mem_map.mpr ⟨c, List.mem_finRange c, rfl⟩)
    | step a b =>
      exact List.mem_append_right _ (List.mem_flatMap.mpr
        ⟨a, List.mem_finRange a, List.mem_map.mpr ⟨b, List.mem_finRange b, rfl⟩⟩)

/-- The number of points player `p` holds. -/
def count (b : Board) (p : Player) : Nat := (List.finRange 9).countP fun c => b c == some p

theorem countP_set (l : List Cell) (hn : l.Nodup) (b : Board) (c : Cell) (v : Option Player)
    (p : Player) (hc : c ∈ l) :
    l.countP (fun x => b.set c v x == some p) + (if b c == some p then 1 else 0)
      = l.countP (fun x => b x == some p) + (if v == some p then 1 else 0) := by
  induction l with
  | nil => cases hc
  | cons x l ih =>
    have hn' := List.nodup_cons.mp hn
    simp only [List.countP_cons]
    by_cases hx : x = c
    · subst hx
      have hrest : l.countP (fun y => b.set x v y == some p) = l.countP (fun y => b y == some p) := by
        apply List.countP_congr
        intro y hy
        have : y ≠ x := fun e => hn'.1 (e ▸ hy)
        simp [Board.set, this]
      have hx : b.set x v x = v := by simp [Board.set]
      simp only [hrest, hx]
      split <;> split <;> omega
    · have hc' : c ∈ l := by
        rcases List.mem_cons.mp hc with e | h
        · exact absurd e.symm hx
        · exact h
      have := ih hn'.2 hc'
      have hx' : b.set c v x = b x := by simp [Board.set, hx]
      simp only [hx']
      omega

theorem count_set (b : Board) (c : Cell) (v : Option Player) (p : Player) :
    count (b.set c v) p + (if b c == some p then 1 else 0)
      = count b p + (if v == some p then 1 else 0) :=
  countP_set _ (List.nodup_finRange 9) b c v p (List.mem_finRange c)

/-- Pieces are conserved: a player's pieces on the board and still to place make three. -/
theorem pieces (s : State) (h : Reachable s) (p : Player) :
    count s.board p + s.remaining p = piecesPerPlayer := by
  induction h with
  | init => cases p <;> decide
  | @play s m _ hl ih =>
    obtain ⟨_, ha⟩ := hl
    cases m with
    | place c =>
      obtain ⟨hr, hb⟩ := ha
      have e := count_set s.board c (some s.turn) p
      rw [hb] at e
      simp only [play]
      by_cases hp : p = s.turn
      · subst hp; simp at e; simp; omega
      · have : (some s.turn == some p) = false := by simp; exact fun h => hp h.symm
        simp [this] at e; simp [hp]; omega
    | step a b =>
      obtain ⟨_, hfa, hnb, _⟩ := ha
      have e1 := count_set s.board a none p
      have e2 := count_set (s.board.set a none) b (some s.turn) p
      have hb2 : (s.board.set a none) b = none := by
        unfold Board.set; split <;> simp_all
      rw [hb2] at e2
      rw [hfa] at e1
      simp only [play]
      by_cases hp : p = s.turn
      · subst hp; simp at e1 e2; omega
      · have : (some s.turn == some p) = false := by simp; exact fun h => hp h.symm
        simp [this] at e1 e2; omega

/-- No player ever has more than three pieces on the board. -/
theorem count_le (s : State) (h : Reachable s) (p : Player) : count s.board p ≤ 3 := by
  have := pieces s h p; unfold piecesPerPlayer at this; omega

/-- The plies played are bounded by the draw limit: a game lasts at most 30 moves. -/
theorem plies_le (s : State) (h : Reachable s) : s.plies ≤ drawLimit := by
  induction h with
  | init => decide
  | @play s m _ hl _ =>
    have hlt : s.plies < drawLimit := by
      have ho := hl.1
      unfold over draw at ho
      cases hw : (winner s) with
      | some _ => simp [hw] at ho
      | none => simp [hw] at ho; omega
    cases m <;> simp only [play] <;> omega

/-- A reachable state with no legal move is over: the game never gets stuck. -/
theorem no_moves_over (s : State) (h : Reachable s) (hm : legalMoves s = []) : over s = true := by
  cases ho : over s
  · exfalso
    have hpieces := pieces s h s.turn
    by_cases hr : s.remaining s.turn > 0
    · -- placing: some point is empty, since at most five pieces are on the board
      have hx := count_le s h s.turn.other
      have hempty : ∃ c, s.board c = none := by
        apply Classical.byContradiction
        intro hne
        have hall : ∀ c, s.board c ≠ none := fun c hc => hne ⟨c, hc⟩
        have htot : count s.board .X + count s.board .O = 9 := by
          unfold count
          have : ∀ l : List Cell, (∀ c ∈ l, s.board c ≠ none) →
              l.countP (fun c => s.board c == some .X) + l.countP (fun c => s.board c == some .O)
                = l.length := by
            intro l hl
            induction l with
            | nil => rfl
            | cons x l ih =>
              have := ih (fun c hc => hl c (List.mem_cons_of_mem _ hc))
              have hx := hl x (List.mem_cons_self ..)
              simp only [List.countP_cons, List.length_cons]
              cases hb : s.board x with
              | none => exact absurd hb hx
              | some q => cases q <;> simp <;> omega
          rw [this _ (fun c _ => hall c)]; rfl
        have h1 := pieces s h s.turn
        have h2 := count_le s h s.turn.other
        cases ht : s.turn <;> rw [ht] at h1 hr h2 <;> simp [Player.other, piecesPerPlayer] at h1 h2 <;>
          omega
      obtain ⟨c, hc⟩ := hempty
      have : Move.place c ∈ legalMoves s := (mem_legalMoves s _).mpr ⟨ho, hr, hc⟩
      rw [hm] at this; cases this
    · -- moving: not blocked (else the game is over), so some piece can move
      have hr0 : s.remaining s.turn = 0 := by omega
      have hnb : blocked s = false := by
        cases hb : blocked s
        · rfl
        · have : over s = true := by
            unfold over winner
            simp only [hb]
            split <;> (try split) <;> simp
          rw [ho] at this; cases this
      unfold blocked at hnb
      simp [hr0] at hnb
      obtain ⟨a, b, hab⟩ := hnb
      have : Move.step a b ∈ legalMoves s :=
        (mem_legalMoves s _).mpr ⟨ho, hr0, hab.1.1, hab.1.2, hab.2⟩
      rw [hm] at this; cases this
  · rfl

/-! ## Part 3. The Soar agent's move choice

One-ply look-ahead: each legal move is played in a copy of the state and the result scored
from the mover's point of view; the agent chooses among the moves with the highest score
(Soar's selection space makes them indifferent, so the choice among them is random). -/

/-- The score of the state after the mover `p` has moved (its opponent is now to move):
100 if `p` has won; −100 if the opponent has won or can complete a line on its next turn;
otherwise 2 if `p` holds the centre, else 0. -/
def threat (s : State) : Bool :=
  (legalMoves s).any fun m => hasLine (play s m).board s.turn

def score (p : Player) (s : State) : Int :=
  if winner s = some p then 100
  else if winner s = some p.other then -100
  else if threat s then -100
  else if s.board 4 = some p then 2
  else 0

def value (s : State) (m : Move) : Int := score s.turn (play s m)

/-- The moves the agent may choose: the legal moves of highest value. -/
def choices (s : State) : List Move :=
  let ms := legalMoves s
  let best := ms.foldl (fun acc m => max acc (value s m)) (-1000)
  ms.filter fun m => value s m == best

/-- The agent never chooses an illegal move. -/
theorem choices_legal (s : State) (m : Move) (h : m ∈ choices s) : Legal s m :=
  (mem_legalMoves s m).mp (List.mem_filter.mp h).1

/-- X's first move in the opening: the centre is the only choice. -/
example : choices init = [.place 4] := by decide

end Morris
