# From English to a Tested Soar Agent: Pipeline Data Flow

Mermaid source for the pipeline diagrams, converted from `soar-pipeline-dataflow.pptx` (slides 2, 3, 4 and 12).
Edit the code blocks below; GitHub renders them directly.

**Conventions (the legend)**

| Shape | Meaning |
|---|---|
| Rounded box (blue) | Process |
| Document shape (white) | Data or artifact |
| Cylinder (green) | Knowledge source |
| Dashed arrow (red) | Feedback |
| Solid thin arrow from a cylinder | Knowledge feeds a process |

Node IDs are stable (`P_` process, `D_` data, `K_` knowledge); keep them when renaming labels so diffs stay readable.

---

## 1. The main path: five processes, five artifacts

Forward path only. The implementation process is code generation: a deterministic program (agentgen), not Claude, because its input is a formal Lean design.

```mermaid
flowchart TB
  classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0b1f4d
  classDef data fill:#ffffff,stroke:#475569,color:#0f172a

  subgraph SPEC["Specification phase"]
    direction LR
    D_english@{ shape: doc, label: "English description" }
    P_specify("Specify<br/>Claude + human")
    D_spec@{ shape: doc, label: "Specification document" }
    D_english --> P_specify --> D_spec
  end

  subgraph DESIGN["Design phase"]
    direction LR
    P_design("Design<br/>Claude, in Lean")
    D_lean@{ shape: doc, label: "Lean design" }
    P_design --> D_lean
  end

  subgraph IMPL["Implementation phase"]
    direction LR
    P_gen("Generate code<br/>agentgen (Lean)")
    D_soar@{ shape: doc, label: "Soar program +<br/>VisualSoar project" }
    P_gen --> D_soar
  end

  subgraph VERIFY["Verification and testing"]
    direction LR
    P_verify("Verify statically<br/>worldcheck")
    P_run("Run and test<br/>Soar + soar-lean")
    D_tested@{ shape: doc, label: "Tested agent" }
    P_verify --> P_run --> D_tested
  end

  D_spec --> P_design
  D_lean --> P_gen
  D_soar --> P_verify

  class P_specify,P_design,P_gen,P_verify,P_run process
  class D_english,D_spec,D_lean,D_soar,D_tested data
  style SPEC fill:#f8fafc,stroke:#cbd5e1
  style DESIGN fill:#f8fafc,stroke:#cbd5e1
  style IMPL fill:#f8fafc,stroke:#cbd5e1
  style VERIFY fill:#f8fafc,stroke:#cbd5e1
```

---

## 2. Data flow 1: English to an approved Lean design

Specify turns the English into a clause-numbered, mostly human-readable spec. Tests are derived from the spec before any design exists. Design review renders the Lean design back to English and checks it by round trip.

```mermaid
flowchart TB
  classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0b1f4d
  classDef data fill:#ffffff,stroke:#475569,color:#0f172a
  classDef know fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef exit fill:#f1f5f9,stroke:#475569,stroke-dasharray: 4 3,color:#0f172a

  K_claude[("Common-sense and<br/>domain knowledge (Claude)")]
  K_conv[("Soar + world<br/>conventions")]
  K_spec[("Lean Soar spec")]
  K_examples[("Example agents")]
  K_libs[("Capability libraries")]

  D_english@{ shape: doc, label: "English description" }
  P_specify("Specify<br/>Claude + human")
  D_spec@{ shape: doc, label: "Spec document" }
  P_design("Design<br/>Claude + Lean check")
  D_lean@{ shape: doc, label: "Lean design" }
  X_gen(["To generate code"])

  D_english --> P_specify --> D_spec --> P_design --> D_lean --> X_gen

  K_claude --> P_specify
  K_claude --> P_design
  K_conv --> P_design
  K_spec --> P_design
  K_examples --> P_design
  K_libs --> P_design

  P_tests("Derive tests<br/>Claude + human")
  D_tests@{ shape: doc, label: "Test scenarios" }
  P_review("Review design<br/>renderer + round trip")
  D_rendered@{ shape: doc, label: "Rendered English" }

  D_spec --> P_tests --> D_tests
  D_lean --> P_review --> D_rendered

  P_design -. "Gaps found" .-> P_specify
  P_review -. "Mismatch" .-> P_design

  class P_specify,P_design,P_tests,P_review process
  class D_english,D_spec,D_lean,D_tests,D_rendered data
  class K_claude,K_conv,K_spec,K_examples,K_libs know
  class X_gen exit

  linkStyle 15,16 stroke:#b91c1c,stroke-dasharray: 5 4
```

---

## 3. Data flow 2: Lean design to a tested Soar agent

Generate code is agentgen: the Lean generator runs (compile) with no LLM and produces Soar rules and the VisualSoar project (rule files, datamap, provenance doc strings), linking in capability libraries.

```mermaid
flowchart TB
  classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0b1f4d
  classDef data fill:#ffffff,stroke:#475569,color:#0f172a
  classDef know fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef tool fill:#fef9c3,stroke:#a16207,color:#422006
  classDef exit fill:#f1f5f9,stroke:#475569,stroke-dasharray: 4 3,color:#0f172a

  K_libs[("Capability libraries<br/>(agent-world, selection-world)")]
  K_conv[("Soar + world<br/>conventions")]
  K_spec[("Lean Soar spec")]
  K_kernel[("Soar kernel")]
  D_tests@{ shape: doc, label: "Test scenarios" }

  D_lean@{ shape: doc, label: "Approved Lean design" }
  P_gen("Generate code<br/>agentgen")
  D_soar@{ shape: doc, label: "Soar program +<br/>VisualSoar project" }
  P_verify("Verify statically<br/>worldcheck")
  P_run("Run and test<br/>Soar + Lean spec")
  D_tested@{ shape: doc, label: "Tested agent" }

  D_lean --> P_gen --> D_soar --> P_verify --> P_run --> D_tested

  K_libs --> P_gen
  K_conv --> P_gen
  K_conv --> P_verify
  K_spec --> P_verify
  K_spec --> P_run
  K_kernel --> P_run
  D_tests --> P_run

  T_edit{{"View, edit, debug<br/>VisualSoar or VS Code"}}
  D_soar -.- T_edit

  D_report@{ shape: doc, label: "Verification report" }
  D_traces@{ shape: doc, label: "Traces + results" }
  P_diagnose("Diagnose<br/>Claude")
  X_err(["Spec or design error"])

  P_verify --> D_report
  P_run --> D_traces --> P_diagnose

  P_verify -. "Static check fails" .-> P_gen
  P_diagnose -. "Generator bug" .-> P_gen
  P_diagnose -.-> X_err

  class P_gen,P_verify,P_run,P_diagnose process
  class D_lean,D_soar,D_tested,D_tests,D_report,D_traces data
  class K_libs,K_conv,K_spec,K_kernel know
  class T_edit tool
  class X_err exit

  linkStyle 16,17,18 stroke:#b91c1c,stroke-dasharray: 5 4
```

---

## 4. Proposal: a revised flow that uses the Soar MCP server tools

Changes from flows 2 and 3, using ideas from Wray, Schmidt & Jones (2026). Orange boxes are the new processes. If agentgen already writes the datamap, the MCP role reduces to validation. Faults go back to a person as proposals, not automatic fixes.

```mermaid
flowchart LR
  classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0b1f4d
  classDef newp fill:#ffedd5,stroke:#c2410c,color:#431407
  classDef data fill:#ffffff,stroke:#475569,color:#0f172a

  D_spec@{ shape: doc, label: "Spec document" }
  P_design("Design<br/>Claude, in Lean")
  D_lean@{ shape: doc, label: "Lean design" }
  P_gen("Generate rules<br/>agentgen")
  D_rules@{ shape: doc, label: "Soar rules" }

  P_build("Build project<br/>Soar MCP")
  D_vs@{ shape: doc, label: "VisualSoar folders<br/>+ datamap" }
  P_gates("Static gates<br/>worldcheck + MCP")
  P_test("Test<br/>scenarios via MCP")
  P_debug("Debug<br/>subagent, live kernel")

  D_spec --> P_design --> D_lean --> P_gen --> D_rules
  D_rules --> P_build --> D_vs --> P_gates --> P_test --> P_debug
  P_debug -. "Fault found:<br/>proposals to a person" .-> P_design

  N1["Thin slices: run the whole loop on a minimal agent, then add capability"]
  N2["Developer on the loop: view, edit and debug in VisualSoar or VS Code"]

  class P_design,P_gen process
  class P_build,P_gates,P_test,P_debug newp
  class D_spec,D_lean,D_rules,D_vs data

  linkStyle 9 stroke:#b91c1c,stroke-dasharray: 5 4
```
