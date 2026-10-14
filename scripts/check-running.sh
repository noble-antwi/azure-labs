#!/usr/bin/env bash
# Shows anything still running or billable before you close the laptop.

set -euo pipefail

echo "== Running VMs =="
az vm list -d \
  --query "[?powerState=='VM running'].{name:name, rg:resourceGroup, size:hardwareProfile.vmSize}" \
  --output table

echo
echo "== Billable network resources (gateways, firewalls, Bastion) =="
az resource list \
  --query "[?contains(type,'virtualNetworkGateways') || contains(type,'azureFirewalls') || contains(type,'bastionHosts') || contains(type,'applicationGateways')].{name:name, type:type, rg:resourceGroup}" \
  --output table

echo
echo "== Everything tagged autoDelete=true =="
az resource list --tag autoDelete=true \
  --query "[].{name:name, type:type, rg:resourceGroup}" \
  --output table
