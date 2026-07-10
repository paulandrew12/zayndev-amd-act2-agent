#!/usr/bin/env bash
# One-command submission build: cross-build the linux/amd64 image and push it to a
# PUBLIC registry (GitHub Container Registry), then print the image reference to
# paste into the lablab Track 1 submission.
#
# Prereqs (run once):
#   gh auth refresh -h github.com -s write:packages   # grant package push scope
#
# Usage:
#   GH_USER=paulandrew12 ./scripts/build_and_push.sh
set -euo pipefail
cd "$(dirname "$0")/.."

GH_USER="${GH_USER:-paulandrew12}"
IMAGE="ghcr.io/${GH_USER}/zayndev-agent:latest"

echo ">> logging in to ghcr.io as ${GH_USER}"
gh auth token | docker login ghcr.io -u "${GH_USER}" --password-stdin

echo ">> building + pushing ${IMAGE} (linux/amd64)"
docker buildx build --platform linux/amd64 -t "${IMAGE}" \
  --label "org.opencontainers.image.source=https://github.com/${GH_USER}/zayndev-amd-act2-agent" \
  --push .

cat <<EOF

Pushed: ${IMAGE}

Two things before submitting:
  1. Make the package PUBLIC (image must be publicly pullable, or it scores zero):
     https://github.com/users/${GH_USER}/packages/container/zayndev-agent/settings
     -> Danger Zone -> Change visibility -> Public
  2. Verify it pulls anonymously:
     docker logout ghcr.io && docker pull ${IMAGE}

Then paste ${IMAGE} into the Track 1 submission on your lablab team dashboard.
EOF
