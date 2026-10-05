# Stehekin process experiments

These scripts run the ten application cases used in the manuscript. They use
the generic VIC-MF6 runtime from `/opt/vicmf6` and the bundled synthetic
Stehekin inputs. The groundwater fixture is a numerical test case, not a
calibrated basin model.

Run the complete application workflow from the repository root:

```bash
./scripts/run-manuscript.sh --stages process
```

The generated campaign is written to
`analysis/vic-mf6-manuscript/process/`. The campaign script can also be run
inside the workflow image with one empty absolute output directory:

```bash
examples/stehekin/experiments/run-feedback-campaign.sh /results/campaign
```

The campaign produces model inputs, VIC restart chains, MODFLOW 6 budgets,
diagnostics, provenance records, compact analysis tables, and figure data.
Generated campaign directories stay outside Git.
