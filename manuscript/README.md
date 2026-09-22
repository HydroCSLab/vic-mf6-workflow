# Manuscript workflow contents

The repository root contains the copy-and-paste reproduction commands. This
directory holds the experiment drivers and verification programs used by that
workflow.

The workflow image receives the reusable runtime from `vic-mf6` and adds only
the Python packages and scripts needed for the application experiments. A run
writes generated model decks, restart files, diagnostics, logs, and compact
tables to `analysis/vic-mf6-manuscript/`; those products are local evidence,
not repository inputs.

The stages are grouped by purpose:

| Stage | What it checks |
| --- | --- |
| `unit`, `acceptance` | Framework tests and the packaged Stehekin case |
| `verification` | Numerical interface and conservation checks |
| `process` | Ten snowmelt, withdrawal, timestep, and replay cases |
| `reference` | Coupled and independently solvable time-integration references |
| `robustness` | Conductance and initial-condition sensitivity |
| `initialization` | Groundwater initialization and controller-path checks |

Use `scripts/run-manuscript.sh` for the complete sequence or select stages
with `--stages`. Use a new empty output directory for every run.
