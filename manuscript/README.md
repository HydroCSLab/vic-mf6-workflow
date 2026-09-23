# Manuscript workflow contents

The repository root contains the complete copy-and-paste workflow. This
directory contains the experiment drivers, verification programs, table
collection, and analysis scripts used by the paper.

Run outputs follow the project layout:

```text
runs/vic-mf6-manuscript/       raw model outputs and campaign files
analysis/vic-mf6-manuscript/   CSV tables, figures, logs, and provenance
```

Run the complete workflow from anywhere inside the checkout:

```bash
# Move to the workflow checkout.
cd ~/projects/nmhydro/vic-mf6-workflow

# Run all manuscript stages in the workflow image.
./scripts/run-manuscript.sh --workers 2

# Inspect the generated evidence.
find runs/vic-mf6-manuscript -maxdepth 2 -type d | sort
find analysis/vic-mf6-manuscript/tables -maxdepth 1 -type f | sort
```

The stages are grouped as follows:

| Stage | Purpose |
| --- | --- |
| `unit`, `acceptance` | Framework tests and the packaged Stehekin case |
| `verification` | Interface, restart, mapping, and conservation checks |
| `process` | Snowmelt, withdrawal, timestep, and replay experiments |
| `reference` | Coupled and independently solvable time-integration tests |
| `robustness` | Conductance and initial-condition sensitivity |
| `initialization` | Groundwater initialization and controller checks |

Raw runs are never overwritten. Use new directories through
`VICMF6_RUNS_DIR` and `VICMF6_ANALYSIS_DIR` when repeating a stage.
