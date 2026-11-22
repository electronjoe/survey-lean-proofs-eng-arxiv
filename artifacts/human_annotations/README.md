# Human Annotations & Inter-Rater Reliability (IRR)

This directory stores version-controlled, license-safe human verification records used to calibrate and validate the automated LLM-as-a-judge stages (Stage 4 classification and Stage 5 Layer-A semantic fidelity audits).

## Planned Files & Schemas

### 1. `stage4_irr.csv` (Stage 4 Classification Calibration)
Independent human labels on a stratified sample of Stage-2 Lean candidates (comparing against `artifacts/slices/<slice_id>/classifications.json` for Cohen's $\kappa$ / Krippendorff's $\alpha$):

```csv
slice_id,arxiv_id,annotator_id,lean_usage_status,paper_domain_role,authoring_paradigm,verification_tier,ai_agent_assisted,notes
```

### 2. `layer_a_human_verification.json` (Stage 5 Human Audit & Commit-SHA Pins)
Human-verified ground truth for audited `engineering_math_proof` repositories, pinning exact arXiv versions and Git commit SHAs before citing named findings in publication variants:

```json
{
  "schema_version": "1.0",
  "records": [
    {
      "slice_id": "2026-11",
      "arxiv_id": "2611.XXXXX",
      "arxiv_version": "v1",
      "repo_url": "https://github.com/owner/repo",
      "commit_sha": "0000000000000000000000000000000000000000",
      "annotator_id": "annotator_1",
      "verified_at": "2026-12-01",
      "overall_fidelity": "mostly_faithful_with_disclosed_gaps",
      "mode1_severity": "none",
      "mode2_severity": "minor_disclosed",
      "mode3_severity": "none",
      "mode4_severity": "none",
      "verified_file_lines": ["Path/To/File.lean:42"],
      "reconciliation_notes": ""
    }
  ]
}
```

## Licensing & Anonymity Notes
- All files in this directory are curated metadata and annotations released under **CC-BY-4.0** (no third-party `.lean` source code or copyrighted paper full text).
- Use pseudonymous `annotator_id` labels (`annotator_1`, `annotator_2`) rather than personal names so `scripts/export_blind_artifact.py` can include IRR records directly in double-blind review packages.
