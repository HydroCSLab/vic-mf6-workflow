#!/usr/bin/env bash

set -euo pipefail

workflow_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project_dir=${VICMF6_PROJECT_DIR:-$workflow_dir}
runs_dir=${VICMF6_RUNS_DIR:-$project_dir/runs/vic-mf6-manuscript}
analysis_dir=${VICMF6_ANALYSIS_DIR:-$project_dir/analysis/vic-mf6-manuscript}
if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
    runs_dir=$1/runs
    analysis_dir=$1/analysis
    shift
fi
if [[ "$runs_dir" != /* ]]; then
    runs_dir=$project_dir/$runs_dir
fi
if [[ "$analysis_dir" != /* ]]; then
    analysis_dir=$project_dir/$analysis_dir
fi
mkdir -p -- "$runs_dir" "$analysis_dir"
runs_dir=$(realpath -- "$runs_dir")
analysis_dir=$(realpath -- "$analysis_dir")
for directory in "$runs_dir" "$analysis_dir"; do
    if [ -n "$(find "$directory" -mindepth 1 -print -quit)" ]; then
        printf 'output directory must be empty: %s\n' "$directory" >&2
        exit 2
    fi
done

image=${VICMF6_WORKFLOW_IMAGE:-vic-mf6-workflow:manuscript}
printf 'Workflow project directory: %s\n' "$project_dir"
printf 'Host raw runs: %s\n' "$runs_dir"
printf 'Host analysis: %s\n' "$analysis_dir"
printf 'Workflow image: %s\n' "$image"
printf 'Image ID: '
docker image inspect --format '{{.Id}}' "$image"
if [ -n "${VICMF6_COLOR:-}" ]; then
    color_setting=$VICMF6_COLOR
elif [ -t 1 ]; then
    color_setting=always
else
    color_setting=never
fi

if docker run --rm --init --shm-size=1g \
        --entrypoint python \
        --env OMP_NUM_THREADS=1 --env OPENBLAS_NUM_THREADS=1 \
        --env MKL_NUM_THREADS=1 --env NUMEXPR_NUM_THREADS=1 \
        --env "VICMF6_COLOR=$color_setting" \
        --env VICMF6_WORKFLOW_DIR=/opt/vic-mf6-workflow \
        --env "VICMF6_HOST_OUTPUT_DIR=$project_dir" \
        --volume "$runs_dir:/results/runs" \
        --volume "$analysis_dir:/results/analysis" \
        "$image" /opt/vic-mf6-workflow/manuscript/scripts/run-manuscript.py \
        --run-dir /results/runs \
        --analysis-dir /results/analysis "$@"
then
    printf '[OK] manuscript runs saved on host: %s\n' "$runs_dir"
    printf '[OK] manuscript analysis saved on host: %s\n' "$analysis_dir"
else
    status=$?
    printf '[FAIL] manuscript run failed; partial runs and analysis are in: %s and %s\n' "$runs_dir" "$analysis_dir" >&2
    exit "$status"
fi
