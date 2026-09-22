# VIC-MF6 manuscript workflow

This repository contains the application workflow used for the VIC-MF6
manuscript. The reusable framework remains in
[`vic-mf6`](https://github.com/mabdazzam/vic-mf6); the paper sources remain in
[`vic-mf6-paper`](https://github.com/mabdazzam/vic-mf6-paper). This repository
creates the manuscript experiments, runs them with a pinned framework image,
and retains raw outputs under the project `analysis/` directory.

The expected checkout layout is:

```text
<project-dir>/
├── vic-mf6/
├── vic-mf6-workflow/
├── vic-mf6-paper/
└── analysis/vic-mf6-manuscript/
```

## Linux

Install Docker Engine from the [official Linux guide](https://docs.docker.com/engine/install/), then check it:

```bash
docker --version
docker info
docker run --rm hello-world
```

Run the complete workflow:

```bash
mkdir -p ~/projects/vic-mf6-manuscript
cd ~/projects/vic-mf6-manuscript
git clone --recurse-submodules --branch manuscript https://github.com/mabdazzam/vic-mf6.git vic-mf6
git clone --branch manuscript https://github.com/mabdazzam/vic-mf6-workflow.git vic-mf6-workflow
git clone --branch manuscript https://github.com/mabdazzam/vic-mf6-paper.git vic-mf6-paper
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r vic-mf6-paper/scripts/requirements-figures.txt
cd vic-mf6
VICMF6_VERSION=manuscript-2026-09-19 ./bundle/scripts/build-image.sh vic-mf6:manuscript
cd ../vic-mf6-workflow
VICMF6_IMAGE=vic-mf6:manuscript ./scripts/build-image.sh vic-mf6-workflow:manuscript
./scripts/run-manuscript.sh --workers 2
python3 manuscript/scripts/compare-manuscript-tables.py
cd ../vic-mf6-paper
python3 scripts/create-manuscript-figures.py
make -C manuscript
make -C manuscript supplement graphical-abstract
```

## macOS

Install and start [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/), then check it from Terminal:

```bash
docker --version
docker info
docker run --rm hello-world
```

On Apple silicon, set the x86-64 container architecture before running the
Linux commands above:

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

## Windows

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with Linux containers and WSL 2. In PowerShell:

```powershell
docker --version
docker info
docker run --rm hello-world
wsl --install -d Ubuntu
wsl
```

Run the Linux commands above inside the Ubuntu WSL terminal. The workflow uses
Bash, MPI, `make`, and Linux container mounts.

## Inspect results

From the `vic-mf6-workflow` checkout, the host results are stored beside the
repositories:

```bash
find ../analysis/vic-mf6-manuscript -mindepth 1 -maxdepth 1 -type d -printf '%f/\n' | sort
cat ../analysis/vic-mf6-manuscript/execution.csv
```

The top-level results include `acceptance/`, `verification/`, `process/`,
`reference/`, `nonlinear/`, `robustness/`, `initialization/`, `tables/`, and
`logs/`. `/results/manuscript` is only the path inside the workflow container.
The output directory must be empty before each run; choose a new analysis
directory for another run.

The workflow image is built on the framework image. It installs only the
workflow-specific Python packages and contains the experiment scripts under
`manuscript/` and `examples/stehekin/experiments/`. Generated model decks,
NetCDF, NPZ, JSON, logs, PDFs, and campaign directories stay outside Git.
