#!/usr/bin/env bash

set -euo pipefail

workflow_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project_dir=$(dirname -- "$workflow_dir")
output_dir=${VICMF6_MANUSCRIPT_OUTPUT_DIR:-$project_dir/analysis/vic-mf6-manuscript}
if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
    output_dir=$1
    shift
fi
if [[ "$output_dir" != /* ]]; then
    output_dir=$project_dir/$output_dir
fi
mkdir -p -- "$output_dir"
output_dir=$(realpath -- "$output_dir")
if [ -n "$(find "$output_dir" -mindepth 1 -print -quit)" ]; then
    printf 'output directory must be empty: %s\n' "$output_dir" >&2
    exit 2
fi

image=${VICMF6_WORKFLOW_IMAGE:-vic-mf6-workflow:manuscript}
printf 'Host manuscript results: %s\n' "$output_dir"
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
        --env "VICMF6_HOST_OUTPUT_DIR=$output_dir" \
        --volume "$output_dir:/results/manuscript" \
        "$image" /opt/vic-mf6-workflow/manuscript/scripts/run-manuscript.py \
        --output-dir /results/manuscript "$@"
then
    printf '[OK] manuscript results saved on host: %s\n' "$output_dir"
else
    status=$?
    printf '[FAIL] manuscript run failed; partial results and logs are in: %s\n' "$output_dir" >&2
    exit "$status"
fi
