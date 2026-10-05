#!/usr/bin/env python3
"""Run the manuscript experiments with raw runs and analysis kept separate."""
import argparse
import csv
import hashlib
import importlib.metadata
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time


STAGES = ["unit", "acceptance", "verification", "process", "reference", "robustness", "initialization"]


def _ansi(code, text, enabled):
    """Wrap text in an ANSI color when terminal output supports it."""
    return f"\033[{code}m{text}\033[0m" if enabled else text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--analysis-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--install-dir", type=Path, default=Path("/opt/vicmf6"))
    parser.add_argument("--workflow-dir", type=Path, default=Path("/opt/vic-mf6-workflow"))
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--stages", default=",".join(STAGES), help="Comma-separated stages; default: all.")
    args = parser.parse_args()
    selected = args.stages.split(",")
    if args.workers < 1 or not selected or any(s not in STAGES for s in selected) or len(set(selected)) != len(selected):
        parser.error("Provide a positive worker count and unique valid stages: " + ",".join(STAGES))
    if args.output_dir and (args.run_dir or args.analysis_dir):
        parser.error("Use --output-dir by itself, or use --run-dir and --analysis-dir together.")
    if args.output_dir:
        run_out = analysis_out = args.output_dir.resolve()
    elif args.run_dir and args.analysis_dir:
        run_out = args.run_dir.resolve()
        analysis_out = args.analysis_dir.resolve()
    else:
        parser.error("Provide --run-dir and --analysis-dir.")
    for directory in {run_out, analysis_out}:
        directory.mkdir(parents=True, exist_ok=True)
        if any(directory.iterdir()):
            parser.error(f"Output directory must be empty; previous runs are never overwritten: {directory}")
    scripts = Path(__file__).resolve().parent
    install = args.install_dir.resolve()
    workflow = args.workflow_dir.resolve()
    coupler = install / "src/vic-mf6"
    logs = analysis_out / "logs"
    logs.mkdir()
    tables = analysis_out / "tables"
    tables.mkdir()
    host_output = os.environ.get("VICMF6_HOST_OUTPUT_DIR")
    if host_output:
        print(f"Host output directory: {host_output}", flush=True)
        print(f"Container run directory: {run_out}", flush=True)
        print(f"Container analysis directory: {analysis_out}", flush=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    env["PYTHONUNBUFFERED"] = "1"
    color_setting = os.environ.get("VICMF6_COLOR", "auto").lower()
    color = color_setting == "always" or (color_setting == "auto" and sys.stdout.isatty())
    blue = lambda text: _ansi(34, text, color)
    cyan = lambda text: _ansi(36, text, color)
    green = lambda text: _ansi(32, text, color)
    red = lambda text: _ansi(31, text, color)
    shutil.copy2(install / "share/component-revisions.txt", analysis_out / "component-revisions.txt")
    with (analysis_out / "python-packages.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["package", "version"])
        writer.writerows(sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()))
    with (analysis_out / "source-hashes.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["file", "sha256"])
        for root in [workflow, coupler / "src", coupler / "tests", install / "examples/stehekin"]:
            for path in sorted(root.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    writer.writerow([str(path), hashlib.sha256(path.read_bytes()).hexdigest()])
        for path in [install / "bin/vic_image.exe", install / "lib/libmf6.so", install / "lib/libvic_parent_disconnect.so"]:
            writer.writerow([str(path), hashlib.sha256(path.read_bytes()).hexdigest()])
    records = []

    def run(name, command, cwd=None):
        print(blue(f"[manuscript] {name}"), flush=True)
        print(cyan("$ " + " ".join(shlex.quote(str(part)) for part in command)), flush=True)
        start = time.monotonic()
        with (logs / f"{name}.log").open("w") as stream:
            process = subprocess.Popen(
                list(map(str, command)),
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                stream.write(line)
                stream.flush()
                sys.stdout.write(line)
                sys.stdout.flush()
            returncode = process.wait()
        records.append([name, returncode, time.monotonic() - start])
        with (analysis_out / "execution.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["stage", "exit_code", "seconds"])
            writer.writerows(records)
        if returncode:
            print(red(f"[FAIL] {name} (exit code {returncode})"), flush=True)
            raise RuntimeError(f"{name} failed; inspect {logs / (name + '.log')}")
        print(green(f"[OK] {name}"), flush=True)

    def script(name, *arguments):
        run(name, [sys.executable, scripts / f"{name}.py", *arguments])

    if "unit" in selected:
        run("unit", [coupler / "scripts/run_unit_tests.sh"], coupler)
        run("mpi-collectives", [coupler / "scripts/run_mpi_smoke.sh"], coupler)
        run("mpi-failure", [coupler / "scripts/run_mpi_failure_smoke.sh"], coupler)
    if "acceptance" in selected:
        run("acceptance", [install / "bin/container-entrypoint", "acceptance", run_out / "acceptance"])
        script("run-groundwater-control", "--acceptance-dir", run_out / "acceptance",
               "--output-dir", analysis_out / "groundwater-control", "--install-dir", install)
    if "verification" in selected:
        script("run-verification", "--output-dir", run_out / "verification", "--install-dir", install)
    if "process" in selected:
        run("process", [workflow / "examples/stehekin/experiments/run-feedback-campaign.sh", run_out / "process"])
        script("create-data-process-figures", "--campaign-dir", run_out / "process", "--output-dir", tables)
    if "reference" in selected:
        script("run-coupled-reference", "--output-dir", run_out / "reference", "--install-dir", install)
        inputs = install / "examples/stehekin/input"
        script("create-data-nonlinear-reference", "--output-dir", run_out / "nonlinear-reference",
               "--parameter-file", inputs / "stehekin_parameters_20160327.nc",
               "--domain-file", inputs / "domain_stehekin_20151028.nc")
        script("run-nonlinear-interface-reference", "--output-dir", run_out / "nonlinear",
               "--install-dir", install, "--reference-dir", run_out / "nonlinear-reference")
    if "robustness" in selected:
        script("run-robustness-campaign", "--output-dir", run_out / "robustness", "--install-dir", install, "--workflow-dir", workflow, "--workers", args.workers)
        script("analyze-robustness-campaign", "--campaign-dir", run_out / "robustness", "--output-dir", tables)
    if "initialization" in selected:
        script("run-review-campaign", "--output-dir", run_out / "initialization", "--install-dir", install, "--workflow-dir", workflow, "--workers", args.workers)
        script("analyze-review-campaign", "--campaign-dir", run_out / "initialization", "--output-dir", tables)
        script("run-spatial-mapping-diagnostic", "--campaign-dir", run_out / "initialization", "--output-dir", tables, "--coupler-dir", coupler)
    script("collect-manuscript-tables", "--run-dir", run_out, "--analysis-dir", analysis_out,
           "--output-dir", tables)
    (analysis_out / "completion.txt").write_text("Completed stages: " + ", ".join(selected) + "\n")
    if host_output:
        print(f"[OK] completed {', '.join(selected)}; host run files: {host_output}/runs", flush=True)
        print(f"[OK] host analysis files: {host_output}/analysis", flush=True)
    else:
        print(f"[OK] completed {', '.join(selected)}; container run files: {run_out}", flush=True)
        print(f"[OK] container analysis files: {analysis_out}", flush=True)


if __name__ == "__main__":
    main()
