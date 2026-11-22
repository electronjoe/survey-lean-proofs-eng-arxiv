import Lean

/-!
Programmatic `#print axioms` auditor for sandboxed Lean 4 builds.

Intended to be concatenated after `import <RootModule>` lines inside an ephemeral
driver file and executed via `lake env lean <driver.lean>` inside a `--network=none`
container. Uses Lean's built-in `Lean.collectAxioms` (the exact kernel dependency
collector invoked by `#print axioms`) across every theorem declaration defined in
the target project's own modules, emitting a single JSON summary line prefixed with
`SANDBOX_AXIOMS_JSON:`.
-/

namespace SandboxAxiomAudit

open Lean

private def jsonEscape (s : String) : String :=
  let s := s.replace "\\" "\\\\"
  let s := s.replace "\"" "\\\""
  let s := s.replace "\n" "\\n"
  let s := s.replace "\r" "\\r"
  let s := s.replace "\t" "\\t"
  s

private def jsonStr (s : String) : String :=
  "\"" ++ jsonEscape s ++ "\""

private def jsonStrArray (xs : List String) : String :=
  "[" ++ String.intercalate "," (xs.map jsonStr) ++ "]"

private def isStandardAxiom (n : Name) : Bool :=
  n == `propext || n == `Classical.choice || n == `Quot.sound

private def isTargetModule (prefixes : List String) (modName : Name) : Bool :=
  let s := modName.toString
  prefixes.any fun p => s == p || s.startsWith (p ++ ".")

private def isUserTheoremName (n : Name) : Bool :=
  if n.isInternal then false
  else
    let s := n.toString
    !(s.startsWith "_private.") &&
    !(s.endsWith "._proof_1") &&
    !(s.endsWith "._proof_2") &&
    !(s.endsWith "._proof_3") &&
    !(s.endsWith ".eq_1") &&
    !(s.endsWith ".eq_2") &&
    !(s.endsWith ".eq_def") &&
    !(s.endsWith ".inj") &&
    !(s.endsWith ".injEq") &&
    !(s.endsWith ".sizeOf_spec") &&
    !(s.endsWith ".brecOn") &&
    !(s.endsWith ".recOn") &&
    !(s.endsWith ".casesOn") &&
    !(s.endsWith ".noConfusion") &&
    !(s.endsWith ".noConfusionType") &&
    !(s.endsWith ".below") &&
    !(s.endsWith ".ibelow")

/-- Collect transitive axioms for all theorems belonging to modules matching `prefixes`. -/
def runAudit (prefixes : List String) (maxSample : Nat := 60) : CoreM Unit := do
  let env ← getEnv
  let modNames := env.header.moduleNames
  let mut targetModIdxs : Array Nat := #[]
  for i in [:modNames.size] do
    if isTargetModule prefixes modNames[i]! then
      targetModIdxs := targetModIdxs.push i

  let mut thmNames : Array Name := #[]
  -- Check imported declarations belonging to target modules
  for idx in targetModIdxs do
    if h : idx < env.header.moduleData.size then
      let mdata := env.header.moduleData[idx]
      for i in [:mdata.constNames.size] do
        let nm := mdata.constNames[i]!
        if isUserTheoremName nm then
          if let some ci := env.find? nm then
            match ci with
            | ConstantInfo.thmInfo _ => thmNames := thmNames.push nm
            | _ => pure ()

  -- Also check declarations in the current file (for single-file `lean` checks without imports)
  if prefixes.contains "__LOCAL__" then
    for (nm, ci) in env.constants.map₂.toList do
      if isUserTheoremName nm then
        match ci with
        | ConstantInfo.thmInfo _ => thmNames := thmNames.push nm
        | _ => pure ()

  let mut totalTheorems : Nat := 0
  let mut stdAxiomsSet : List String := []
  let mut nonStdAxiomsSet : List String := []
  let mut sorryDetected : Bool := false
  let mut ofReduceBoolDetected : Bool := false
  let mut trustCompilerDetected : Bool := false
  let mut nonStdEntries : List (String × List String) := []
  let mut sampleEntries : List (String × List String) := []

  for nm in thmNames do
    totalTheorems := totalTheorems + 1
    let axs ← Lean.collectAxioms nm
    let axStrs := axs.toList.map Name.toString
    let mut hasNonStd := false
    for a in axs do
      let s := a.toString
      if isStandardAxiom a then
        if !stdAxiomsSet.contains s then
          stdAxiomsSet := stdAxiomsSet ++ [s]
      else
        hasNonStd := true
        if !nonStdAxiomsSet.contains s then
          nonStdAxiomsSet := nonStdAxiomsSet ++ [s]
        if a == `sorryAx || s == "sorryAx" then
          sorryDetected := true
        if a == `Lean.ofReduceBool || s == "Lean.ofReduceBool" then
          ofReduceBoolDetected := true
        if a == `Lean.trustCompiler || s == "Lean.trustCompiler" then
          trustCompilerDetected := true
    if hasNonStd then
      if nonStdEntries.length < 100 then
        nonStdEntries := nonStdEntries ++ [(nm.toString, axStrs)]
    else if sampleEntries.length < maxSample then
      sampleEntries := sampleEntries ++ [(nm.toString, axStrs)]

  let allEntries := nonStdEntries ++ sampleEntries
  let mapParts := allEntries.map fun (k, vs) => jsonStr k ++ ":" ++ jsonStrArray vs
  let mapJson := "{" ++ String.intercalate "," mapParts ++ "}"
  let out :=
    "{"
    ++ "\"target_modules_count\":" ++ toString targetModIdxs.size ++ ","
    ++ "\"total_theorems_checked\":" ++ toString totalTheorems ++ ","
    ++ "\"standard_axioms_used\":" ++ jsonStrArray stdAxiomsSet ++ ","
    ++ "\"nonstandard_axioms_detected\":" ++ jsonStrArray nonStdAxiomsSet ++ ","
    ++ "\"sorry_ax_detected\":" ++ (if sorryDetected then "true" else "false") ++ ","
    ++ "\"of_reduce_bool_detected\":" ++ (if ofReduceBoolDetected then "true" else "false") ++ ","
    ++ "\"trust_compiler_detected\":" ++ (if trustCompilerDetected then "true" else "false") ++ ","
    ++ "\"nonstandard_theorem_count\":" ++ toString nonStdEntries.length ++ ","
    ++ "\"axioms_by_theorem\":" ++ mapJson
    ++ "}"
  IO.println ("SANDBOX_AXIOMS_JSON:" ++ out)

end SandboxAxiomAudit
