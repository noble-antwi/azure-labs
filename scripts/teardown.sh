#!/usr/bin/env bash
# Deletes a lab resource group after confirmation.
# Usage: ./teardown.sh rg-lab-vnet

set -euo pipefail

RG="${1:-}"
if [ -z "$RG" ]; then
  echo "Usage: $0 <resource-group>"
  exit 1
fi

echo "Resources in $RG:"
az resource list --resource-group "$RG" --output table

read -r -p "Delete this resource group? (y/N) " reply
if [[ "$reply" =~ ^[Yy]$ ]]; then
  az group delete --name "$RG" --yes --no-wait
  echo "Deletion started."
else
  echo "Cancelled."
fi
