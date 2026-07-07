#!/usr/bin/env bash
# Run the agent container locally against the sample tasks, mimicking the harness.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p local/output
rm -f local/output/results.json

docker run --rm \
  --env-file .env \
  -v "$(pwd)/local/tasks.sample.json:/input/tasks.json:ro" \
  -v "$(pwd)/local/output:/output" \
  zayndev-agent

echo "--- results ---"
cat local/output/results.json | python3 -m json.tool
