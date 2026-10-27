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
INTENT=""
if [ -e "$DIR" ]; then
  # A planned lab may be started: keep its intent line, replace the rest.
  if grep -q "Status: planned" "$DIR/README.md" 2>/dev/null; then
    INTENT="$(grep -m1 '^> \*\*Intent:\*\*' "$DIR/README.md" || true)"
  else
    echo "Error: '$DIR' already exists and is not a planned lab."
    exit 1
  fi
fi

mkdir -p "$DIR/diagrams" "$DIR/screenshots" "$DIR/bicep"
TITLE="$( { head -1 "$DIR/README.md" 2>/dev/null || true; } | sed 's/^# //')"
[ -n "$TITLE" ] || TITLE="$(echo "$SLUG" | tr '-' ' ')"
sed -e "s/__SLUG__/${SLUG}/g" -e "s/__TITLE__/${TITLE}/g" \
  docs/lab-template.md > "$DIR/README.md.new"
if [ -n "$INTENT" ]; then
  { head -1 "$DIR/README.md.new"; echo; echo "$INTENT"; tail -n +2 "$DIR/README.md.new"; } > "$DIR/README.md"
  rm "$DIR/README.md.new"
  echo "Started planned lab $DIR (intent kept)"
else
  mv "$DIR/README.md.new" "$DIR/README.md"
  echo "Created $DIR"
fi
