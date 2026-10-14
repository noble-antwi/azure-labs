#!/usr/bin/env bash
# Creates a new lab folder from the standard template.
# Usage: ./new-lab.sh 21 nat-gateway

set -euo pipefail

NUM="${1:-}"
SLUG="${2:-}"
if [ -z "$NUM" ] || [ -z "$SLUG" ]; then
  echo "Usage: $0 <number> <slug>"
  echo "Example: $0 21 nat-gateway"
  exit 1
fi

DIR="${NUM}-${SLUG}"
if [ -e "$DIR" ]; then
  echo "Error: '$DIR' already exists."
  exit 1
fi

mkdir -p "$DIR/diagrams" "$DIR/screenshots" "$DIR/bicep"
touch "$DIR/diagrams/.gitkeep" "$DIR/screenshots/.gitkeep" "$DIR/bicep/.gitkeep"
TITLE="$(echo "$SLUG" | tr '-' ' ')"
sed -e "s/__SLUG__/${SLUG}/g" -e "s/__TITLE__/${TITLE}/g" \
  docs/lab-template.md > "$DIR/README.md"

echo "Created $DIR"
