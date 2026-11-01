# VM deep dive

> **Intent:** Settle what a VM is made of (size family, disks, NIC, IP) and prove the billing difference between shutting down inside the OS and deallocating from Azure.

> **Status:** in progress.

## What this lab is

A virtual machine looks like one thing in the portal, but Azure builds it from
several separate resources: the compute (a **size**), an **OS disk**, a
**network interface** in a subnet, usually a **public IP** and a **network
security group**. Each is billed and deleted on its own terms, which is where
most VM surprises on a bill come from.

The lab builds one small Linux VM with **no inbound ports open at all**,
manages it without SSH, and then tests the two ways of "turning it off".

## Questions

1. **What is a VM actually made of?** Which separate resources appear in the
   resource group, and which of them still cost money when the VM is off?
2. **Is shutting down from inside the OS the same as stopping it in Azure?**
   Which one stops the compute charge?
3. **What survives a deallocate?** The OS disk, the temporary disk, the public
   IP address, the private IP address.

### Predictions (written before building)

| # | My prediction | What actually happened |
|---|---|---|
| 1 | When the VM is off, the disk still costs money (not sure what else). |  |
| 2 | Shutting down from inside Linux stops the compute charge; only the disk keeps billing. |  |
| 3 | A file on the temporary disk (`/mnt`) does not survive: it is ephemeral storage. |  |

## Key ideas, from zero

| Term | Plain meaning |
|---|---|
| **Size** | The VM's CPU and memory, e.g. `Standard_B1s` (1 vCPU, 1 GiB). The family letter says what it is for; **B** is burstable: cheap, banks CPU credits when idle. |
| **OS disk** | A managed disk holding the operating system. Survives stop and deallocate; billed while it exists. |
| **Temporary disk** | Fast local storage on the physical host, mounted at `/mnt` on Linux. **Wiped** when the VM moves to another host. |
| **NIC** | Network interface: connects the VM to a subnet and holds its private IP. |
| **Public IP** | A separate resource. Standard SKU, static: billed per hour whether the VM runs or not. |
| **NSG** | Network security group: inbound and outbound allow/deny rules. |
| **Stopped** | Shut down from inside the OS: the VM still holds its place on the host. |
| **Stopped (deallocated)** | Stopped from Azure: the host is released. |
| **Run Command** | Runs a script inside the VM through the Azure agent, with no inbound port needed. |
| **Auto-shutdown** | A daily deallocate at a set time: the safety net against a forgotten lab VM. |

## Architecture

```mermaid
graph LR
  subgraph RG["rg-lab-vm (East US)"]
    VNET["vnet-lab-vm 10.30.0.0/16<br/>subnet default 10.30.0.0/24"]
    NSG["nsg: no inbound rules"]
    NIC["NIC<br/>private IP"]
    PIP["Public IP<br/>Standard, static"]
    VM["vm-lab-01<br/>Ubuntu · Standard_B1s"]
    OS["OS disk<br/>Standard SSD"]
  end
  NSG --- NIC
  VNET --- NIC
  PIP --- NIC
  NIC --- VM
  OS --- VM
  ADMIN["Portal: Run Command"] -. "no inbound port" .-> VM
```

## What gets built

| Resource | SKU / setting | Why it's here |
|---|---|---|
| `rg-lab-vm` | resource group, East US | holds the lab |
| `vm-lab-01` | Ubuntu Server LTS, `Standard_B1s` | the smallest general size, pennies per hour |
| OS disk | Standard SSD | survives stop and deallocate; still billed |
| Virtual network, NIC, public IP, NSG | created with the VM | to see each as its own resource |
| Inbound ports | **none** | managed through Run Command, never exposed to the internet |
| Auto-shutdown | daily | the safety net |

## Build it in the portal

<!--
The primary record. Numbered steps covering the decisions, not every click.
Note anything the portal defaulted to that you had to think about, and why
you chose what you chose. Screenshots go in screenshots/ and are referenced
inline where they clarify something.
-->

1.
2.
3.

## Break it

<!--
Deliberately misconfigure one thing and record the failure mode. This is
where most of the learning happens and it is the part people skip.
What did you break, what error appeared, how did you diagnose it?
-->

## Rebuild it as code

Export the portal's template first to see what Azure created:

```bash
az group export --name rg-lab-vm > exported-reference.json
```

Then write `bicep/main.bicep` yourself and deploy to a clean group:

```bash
az group create --name rg-lab-vm-iac --location eastus \
  --tags environment=lab purpose=lab lab=vm-deep-dive autoDelete=true

az deployment group create \
  --resource-group rg-lab-vm-iac \
  --template-file bicep/main.bicep
```

## What I found

<!--
The answer to the question above, in your own words. Include anything that
surprised you, anything the documentation got wrong or left out, and the
one sentence you would want to read back later.
-->

## Cost

`Standard_B1s` is about a cent per hour of compute while running. The disk and
the public IP keep billing while the VM is stopped or deallocated, which is
the point of question 1. Auto-shutdown and deallocating between sessions keep
the lab to cents.

## Teardown

```bash
az group delete --name rg-lab-vm --yes --no-wait
az group delete --name rg-lab-vm-iac --yes --no-wait
```
