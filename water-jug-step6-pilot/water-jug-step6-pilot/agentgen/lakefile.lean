import Lake
open Lake DSL

package agentgen

require cmcsoar from "../cmcsoar/cmcsoar"

@[default_target]
lean_lib Agent

lean_exe agentgen where
  root := `AgentGen
