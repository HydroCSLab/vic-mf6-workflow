# VIC-MF6 manuscript workflow

This repository contains the project-specific workflow used by the VIC-MF6
manuscript. The reusable framework is in `vic-mf6`; the paper source is in
`vic-mf6-paper`. Generated files stay under this workflow checkout and are
ignored by Git:

```text
vic-mf6-workflow/
├── data/       # raw data, when needed
├── inputs/     # generated model inputs
├── models/     # generated model setups
├── runs/       # raw simulation outputs
└── analysis/   # tables, plots, logs, and provenance
```

## Linux

Install Docker Engine using the [official Linux guide](https://docs.docker.com/engine/install/).
Run these commands from a shell:

```bash
# Check that Docker is installed and can start containers.
docker --version
docker info
docker run --rm hello-world

# Create the project checkout directory.
mkdir -p ~/projects/nmhydro
cd ~/projects/nmhydro

# Clone the reusable framework.
git clone --recurse-submodules \
  https://github.com/HydroCSLab/vic-mf6.git vic-mf6

# Clone this workflow.
git clone https://github.com/HydroCSLab/vic-mf6-workflow.git vic-mf6-workflow

# Build the reusable framework image.
cd ~/projects/nmhydro/vic-mf6
VICMF6_VERSION=manuscript \
VICMF6_BUILD_NETWORK=host \
./bundle/scripts/build-image.sh vic-mf6:manuscript

# Build the workflow image on top of the framework image.
cd ~/projects/nmhydro/vic-mf6-workflow
VICMF6_IMAGE=vic-mf6:manuscript \
VICMF6_BUILD_NETWORK=host \
./scripts/build-image.sh vic-mf6-workflow:manuscript

# Run every manuscript stage.
./scripts/run-manuscript.sh --workers 2

# List the raw runs and derived analysis products.
find runs/vic-mf6-manuscript -maxdepth 2 -type d | sort
find analysis/vic-mf6-manuscript -maxdepth 2 -type f | sort

# Display the execution record and generated manuscript tables.
cat analysis/vic-mf6-manuscript/execution.csv
find analysis/vic-mf6-manuscript/tables -maxdepth 1 -type f | sort
```

Use a new empty run and analysis directory for another run. To run only a
quick smoke test:

```bash
# Return to the workflow checkout.
cd ~/projects/nmhydro/vic-mf6-workflow

# Run the unit tests and packaged acceptance case.
VICMF6_RUNS_DIR="$PWD/runs/vic-mf6-smoke" \
VICMF6_ANALYSIS_DIR="$PWD/analysis/vic-mf6-smoke" \
./scripts/run-manuscript.sh --stages unit,acceptance --workers 2
```

Building the paper PDF is optional. `HydroCSLab/vic-mf6-paper` is private,
so this step requires repository access, GitHub SSH authentication, and the
LaTeX tools documented in that repository:

```bash
cd ~/projects/nmhydro
git clone git@github.com:HydroCSLab/vic-mf6-paper.git vic-mf6-paper
make -C vic-mf6-paper/manuscript
```

## macOS

Install and start [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/).
Run these commands in Terminal:

```bash
# Check that Docker Desktop is running.
docker --version
docker info
docker run --rm hello-world

# Use x86-64 containers on Apple silicon.
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Follow the Linux clone, build, run, and inspection commands above.
cd ~/projects/nmhydro/vic-mf6-workflow
./scripts/run-manuscript.sh --workers 2
```

## Windows

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
enable Linux containers and WSL 2, and run the workflow inside Ubuntu WSL:

```powershell
# Check that Docker Desktop is installed and running.
docker --version
docker info
docker run --rm hello-world

# Install and enter Ubuntu WSL if it is not already installed.
wsl --install -d Ubuntu
wsl
```

```bash
# Follow the Linux clone, build, run, and inspection commands in this WSL shell.
cd ~/projects/nmhydro/vic-mf6-workflow
./scripts/run-manuscript.sh --workers 2
```

The framework image supplies VIC, MODFLOW 6, MPI, and the coupling runtime.
The workflow image adds the manuscript experiment drivers and their Python
dependencies. The generated `runs/` and `analysis/` directories are local
evidence and are not committed. The paper reads the reviewed CSV and figure
files produced from `analysis/`.
