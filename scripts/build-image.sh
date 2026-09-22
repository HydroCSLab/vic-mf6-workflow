#!/usr/bin/env bash

set -euo pipefail

workflow_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
image=${1:-${VICMF6_WORKFLOW_IMAGE:-vic-mf6-workflow:manuscript}}
framework_image=${VICMF6_IMAGE:-vic-mf6:manuscript}

if [ "$#" -gt 1 ]; then
    printf 'usage: %s [IMAGE]\n' "$0" >&2
    exit 2
fi

docker build \
    --network "${VICMF6_BUILD_NETWORK:-default}" \
    --build-arg "VICMF6_IMAGE=$framework_image" \
    --tag "$image" \
    --file "$workflow_dir/Dockerfile" \
    "$workflow_dir"

printf '%s\n' "[OK] built $image from $framework_image"
