# Diagram conventions

## Tooling

draw.io (diagrams.net), with the official Microsoft Azure icon set:
More Shapes → Networking → Azure → Enable.

Commit both files per diagram:
- `architecture.drawio` — the editable source
- `architecture.png` — exported at 2x scale, transparent background off

## What to draw

Show containment and flow, not every resource. A reader should see in five
seconds: what region, what network boundaries, what talks to what, and where
the trust boundaries are.

Include:
- Region and availability zone boundaries where they matter
- VNet and subnet address ranges, labelled
- NSGs on the boundary they protect
- Direction of traffic, with arrows
- What is public-facing and what is not

Leave out:
- Resource groups (they are a management boundary, not an architectural one)
- Every individual NIC, disk and public IP
- Icons for things you are not discussing

## Mermaid alternative

For quick structural views, Mermaid renders natively on GitHub and diffs
cleanly. Use it for flows and hierarchies; use draw.io when the spatial
layout carries meaning.
