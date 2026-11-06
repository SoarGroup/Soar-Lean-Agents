import Agent
import Lean.Data.Json
/-! `agentgen FAMILY OUT.json`: the generated projects of a family as JSON (files with Soar text,
commands, the English, and which originals each variant replaces). `tools/vsproject.py` writes
them out as VisualSoar projects. -/
open Agent Lean

def schemaJson (s : Schema) : Json :=
  let attr (d : AttrDecl) : Json := Json.mkObj [("name", d.name), ("multi", d.multi), ("derived", d.derived),
    ("doc", d.doc), ("type", match d.ty with
      | .int => Json.mkObj [("kind", "int")]
      | .sym cs => Json.mkObj [("kind", "sym"), ("choices", Json.arr (cs.map Json.str).toArray)]
      | .obj t => Json.mkObj [("kind", "obj"), ("type", t)])]
  Json.mkObj [("task", s.task), ("state", Json.arr (s.stateAttrs.map attr).toArray),
    ("types", Json.arr (s.types.map fun t => Json.mkObj [("name", t.name), ("doc", t.doc),
      ("attrs", Json.arr (t.attrs.map attr).toArray)]).toArray)]

def variantJson (name : String) (a : Agent) (replaces : List String) : Json :=
  let files := (compile a).map fun f => Json.mkObj [("path", f.path), ("kind", f.kind),
    ("rules", Json.arr (f.prods.map fun p => Json.str p.toSoar).toArray),
    ("cmds", Json.arr (f.cmds.map Json.str).toArray)]
  Json.mkObj [("name", name), ("task", a.schema.task), ("replaces", Json.arr (replaces.map Json.str).toArray),
    ("selection", needsSelection a), ("check", Json.arr ((check a).map Json.str).toArray),
    ("english", english a), ("schema", schemaJson a.schema),
    ("ops", Json.arr (a.ops.map fun o => Json.str o.name).toArray),
    ("files", Json.arr files.toArray)]

def main (args : List String) : IO Unit := do
  match args with
  | ["water-jug", out] =>
    let vs := WaterJug.variants.map fun (n, a, r) => variantJson n a r
    IO.FS.writeFile out (Json.arr vs.toArray).pretty
    IO.println s!"{vs.length} variants written to {out}"
  | _ => IO.eprintln "usage: agentgen water-jug OUT.json"
