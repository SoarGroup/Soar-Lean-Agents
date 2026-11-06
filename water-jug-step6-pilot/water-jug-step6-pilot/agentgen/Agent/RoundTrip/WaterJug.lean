import Agent.Families.WaterJug
import Agent.RoundTrip.WaterJugReform
/-!
# Round trip for the Water Jug family

`WaterJugReform.lean` was written by a separate model from the blind English review alone
(review/blind-review.md), without the Lean description or the original agents. Here it is
compared with the description the English came from.
-/
namespace Agent.RoundTrip

/-- For each variant: the parts that differ (empty = structurally equal, docs and assumptions
aside; tie heuristics compared by meaning). -/
def report : List (String × List String) :=
  WaterJug.variants.map fun (n, a, _) =>
    match (Reform.WaterJug.variants.find? (·.1 == n)) with
    | some (_, b) => (n, diffCore a b)
    | none => (n, ["missing in the re-formalization"])


/-- The round trip is exact for every variant: equal structurally, except that the tie heuristic is
compared by its table (the re-formalization grouped the same table into entries differently). -/
theorem water_jug_round_trip : report.all (·.2.isEmpty) = true := by decide

end Agent.RoundTrip
