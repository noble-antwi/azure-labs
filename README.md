# azure-labs

Hands-on Azure infrastructure labs. Each lab is built twice: once by hand in the
portal to understand what the service actually does, then again as Bicep to make
it repeatable. Each one documents the architecture, the steps, and what came out
of it.

## How each lab is structured

| File or folder | Purpose |
|---|---|
| `README.md` | Overview, architecture, portal walkthrough, findings |
| `diagrams/` | `.drawio` source and exported `.png` for the architecture |
| `screenshots/` | Portal captures worth keeping |
| `bicep/` | The infrastructure-as-code version, written after the portal build |

## How each lab is run

1. Build it in the portal. Take screenshots of the decisions, not every click.
2. Break something deliberately and record what happened.
3. Export the ARM template from the portal to see what Azure created.
4. Write the Bicep from scratch, deploy to a clean resource group, compare.
5. Write up findings. Tear everything down.

## Layout

| Path | Contents |
|---|---|
| `NN-lab-name/` | One lab, structured as above |
| `modules/` | Shared Bicep modules reused across labs |
| `scripts/` | Teardown and cost-check helpers |
| `docs/` | Cross-cutting notes and reference diagrams |

## Conventions

- One resource group per lab, named `rg-lab-<topic>`.
- Every resource carries `environment=lab`, `purpose=lab`,
  `lab=<lab-name>` and `autoDelete=true`.
- Region is `eastus` unless a lab specifically needs another.
- Run `scripts/check-running.sh` before closing the laptop.

## Diagrams

Architecture diagrams use the official Microsoft Azure icon set, available in
draw.io under More Shapes → Networking → Azure. Commit both the `.drawio` source
and a `.png` export so the README renders without the tool.

Simple structural views can go inline as Mermaid, which GitHub renders natively.

## Labs

### Foundations
1. Governance and tagging policy
2. Storage account access tiers
3. Virtual machine deep dive
4. Custom RBAC role
5. Entra ID users and groups at scale
6. Azure Files share

### Composition
7. Three-tier virtual network
8. Hub-and-spoke with Bastion
9. Load balancer failover
10. Monitoring and alerting
11. Backup and restore
12. Key Vault with managed identity
13. VNet-to-VNet VPN
14. App Service deployment slots
15. Private Endpoint for storage

### Applied
16. Bicep CI/CD pipeline
17. Security baseline with Defender for Cloud
18. Cost guardrail automation
19. Conditional Access and PIM
20. Full environment, built and destroyed from one template
