# Numerical verification evidence

The verification programs implement the compact interface, conservation,
temporal-refinement, spatial-mapping, and connected-groundwater checks used by
the manuscript. The small `reference-results.json` file records expected
signatures for the audit; it is not a raw simulation archive.

Run the audit from the workflow repository root after building its image:

```bash
./scripts/run-verification-evidence.sh
```

The full manuscript runner includes this audit as its `verification` stage and
stores detailed outputs under `analysis/vic-mf6-manuscript/verification/`.
