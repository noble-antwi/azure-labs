# Storage tiers

![Where a file lives, and what it takes to get it back](diagrams/tier-flow.svg)

*Animated. A file walks down the tiers under a lifecycle rule, goes offline in
Archive, is refused a read, and is rehydrated back to Hot; every tier change
travels through Event Grid and a Logic App to a phone alert. Built by
[`scripts/diagrams/lab02_tier_flow.py`](../scripts/diagrams/lab02_tier_flow.py).*

> **Intent:** Find the real cost and latency differences between hot, cool, cold and archive tiers, and what rehydrating an archived blob actually involves.

> **Status:** built and tested in the portal. Still running: the `fast-demo` lifecycle moves (Cool and Cold done; Archive to come) and the
> early-deletion charge on the bill. See [Still waiting on](#still-waiting-on).

## What this lab is

Azure Blob Storage keeps files ("blobs") in four **access tiers**. The colder
the tier, the cheaper it is to *store* a file and the dearer it is to *read*
it back. Archive is so cold the file is offline: it cannot be read at all until
Azure brings it back, which takes hours.

Picking the wrong tier is one of the easiest ways to waste money in Azure,
either by paying hot prices for data nobody reads, or by archiving data that
then has to be pulled back in a hurry.

## Questions

1. **What does each tier really cost:** to store a file, and to read it back?
2. **What happens when you try to open an archived file,** and what does it
   take, in time and money, to get it back?
3. **What does moving a file to a colder tier too early cost?** Cool, cold and
   archive each have a minimum stay.
4. **Once the account's master keys are switched off, who can still read the
   files?** Owner manages the account, but reading data needs a separate data
   role. (Added mid-lab after spotting that the portal quietly uses the key.)

### Predictions (written before building)

| # | My prediction | What actually happened |
|---|---|---|
| 1 | Cool. |  |
| 2 | It is first moved out of archive, through cold and cool to hot, and only then can be read. | Half right. It cannot be read until it is brought back online (step 4), but there is no stepping through tiers: it goes straight to whichever online tier is chosen. |
| 3 | You pay for one day. |  |
| 4 | No. Owner cannot open the files once keys are off. | Correct. Owner manages the account but has no data rights; reading needed a separate data role (step 10). |

## Key ideas, from zero

| Term | Plain meaning |
|---|---|
| **Storage account** | The top-level container for storage in Azure. Its name becomes part of a public web address, so it must be unique worldwide. |
| **Container** | A folder inside the account that holds blobs. |
| **Blob** | One file. |
| **Access tier** | Hot, Cool, Cold or Archive. Set per blob; the account has a default for new blobs. |
| **Hot** | Data read often. Highest storage price, lowest read price. |
| **Cool / Cold** | Data read rarely. Cheaper to store, dearer to read, with a minimum stay (cool 30 days, cold 90). |
| **Archive** | Data almost never read. Cheapest to store, **offline**, minimum stay 180 days. |
| **Rehydration** | Bringing an archived blob back online by moving it to a warmer tier. Standard priority can take up to 15 hours; High priority is faster and costs more. |
| **Early deletion charge** | Move or delete a blob before its tier's minimum stay and you pay for the remaining days anyway. |
| **Lifecycle management** | Rules that move or delete blobs automatically by age, e.g. "cool after 30 days, archive after 180". |
| **Redundancy (LRS)** | How many copies Azure keeps. Locally redundant storage keeps three copies in one datacentre: the cheapest option, and one that supports the archive tier. |

## Architecture

![Lab 02 architecture](diagrams/architecture.png)

*Source: [`diagrams/architecture.drawio`](diagrams/architecture.drawio), editable in
[draw.io](https://app.diagrams.net). Rendered with
[`scripts/diagrams/render_drawio.py`](../scripts/diagrams/render_drawio.py).*

## What gets built

| Resource | SKU / setting | Why it's here |
|---|---|---|
| `rg-lab-storage-tiers` | resource group, East US | holds the lab |
| `stlabtiersnoble01` | StorageV2, Standard, **LRS**, default tier Hot | LRS is the cheapest redundancy that supports archive |
| Container `tiers` | private | no anonymous access |
| Four report files | one per tier, identical content | only the tier differs |
| `report-archive-standard.txt` | Archive | second archived file, to time Standard against High rehydration |
| `lc-1.txt` to `lc-3.txt` | Hot at upload | watched by the fast lifecycle rule |
| Lifecycle rules | `tier-by-age` 30/180 days, `fast-demo` 1/2/3 days | automated tiering, one realistic and one fast enough to watch |
| Logic App `la-tier-alerts` | Consumption | turns tier-change events into phone alerts |
| Event Grid system topic | created by the Logic App trigger | routes storage events |
| Role assignment | Storage Blob Data Reader on `tiers` | data access once the master keys were switched off |

## Build it in the portal

### 1. Create the storage account

`stlabtiersnoble01` in a new group `rg-lab-storage-tiers`, East US. The
portal now asks for a **primary service** (Blob Storage) and a **primary
workload**; **General purpose** was chosen because the workload presets quietly
change defaults on later tabs. Choosing it also reset the resource group to
`NetworkWatcherRG`, which had to be put back: re-check earlier fields after
changing a preset.

![Basics](screenshots/02-01-basics.png)

Standard performance, **LRS** redundancy (three copies in one datacentre: the
cheapest, and it supports archive). The portal recommends RA-GRS for general
purpose, which copies to a second region; a lab does not need it.

**The default access tier offers Hot, Cool and Cold, but not Archive.** The
account default applies to every new blob, and an archived blob is offline, so
it cannot be the default. Archive is set per blob.

![Advanced: no Archive in the default tier](screenshots/02-02-advanced-tiers-no-archive.png)

The other tabs, and why each was left as it was:

| Tab | Setting | Why |
|---|---|---|
| Advanced | Hierarchical namespace **off** | Real folders (Data Lake Gen2) are for analytics; cannot be turned off once on |
| Networking | Public network access, all networks | Reachable is not readable: every request still needs a key or a sign-in. Private access is lab 15 |
| Data protection | Soft delete 7 days on; versioning, change feed, immutability off | A recycle bin, without extra copies that would cloud the tier results. Soft-deleted data is still billed |
| Security | Anonymous access **off** (now the default), secure transfer, TLS 1.2 | No unauthenticated reads |
| Security | Storage account key access **on** | Kept on for now; part 4 turns it off |
| Encryption | Microsoft-managed keys | Data is always encrypted at rest; this only decides who holds the key |

![Networking](screenshots/02-03-networking.png)
![Data protection](screenshots/02-04-data-protection.png)
![Security](screenshots/02-05-security.png)
![Encryption](screenshots/02-06-encryption.png)
![Tags](screenshots/02-07-tags.png)

The review page shows the six tags applied to the storage account **and** to
resource types this deployment did not create (virtual network, private
endpoint): the portal's tag picker defaults to "all resources selected" for
anything the template could include.

![Review: tags per resource type](screenshots/02-08-review-tags.png)
![Review](screenshots/02-09-review.png)

### 2. Create a container

A container is the top-level grouping for blobs: a security boundary (access
can be granted per container), a boundary for lifecycle and immutability rules,
and the equivalent of an S3 bucket. Containers do not nest.

`tiers` was created **Private**, and the access level was greyed out because
anonymous access is off for the whole account.

![New container: private, greyed out](screenshots/02-10-new-container-private.png)

A second container, **`$logs`**, appeared without being created. It is a
system container Azure reserves for storage analytics logs.

![Containers: $logs and tiers](screenshots/02-11-containers-logs-and-tiers.png)

### 3. Upload one file per tier

The four files in [`sample-files/`](sample-files/) are identical apart from one
word, so the only real difference between them is the tier. Each was uploaded
on its own, with the tier set under **Advanced**.

The tier list offers **Hot (Inferred)** as well as **Hot**. *Inferred* means
the blob has no tier of its own and follows the account default; if that
default later changed to Cool, the blob would silently change with it. Plain
**Hot** pins the tier to the blob. **Archive** is offered here, per blob, even
though the account default cannot be Archive. **Smart** (automatic tiering by
access pattern) was listed but greyed out.

![Upload: tier options](screenshots/02-12-upload-tier-options.png)

![Four files, four tiers](screenshots/02-13-four-files-four-tiers.png)

The container page reads **Authentication method: Access key**: the portal was
using the account's master key behind the scenes, not the signed-in user.

### 4. Try to open each file

Hot, Cool and Cold all opened in the portal editor straight away, with the same
content. From the reader's side, the online tiers behave identically; only the
bill differs.

![Cold opens](screenshots/02-16-cold-opens.png)
![Cool opens](screenshots/02-17-cool-opens.png)
![Hot opens](screenshots/02-18-hot-opens.png)

The archived file did not open, and would not download:

![Download failed](screenshots/02-14-archive-download-failed.png)

![This operation is not permitted on an archived blob](screenshots/02-15-archive-not-permitted.png)

> This operation is not permitted on an archived blob. To view or edit the blob,
> copy and paste the blob to rehydrate or change the blob's access tier to an
> online access tier.

The data is still there and still billed; it is offline. The message also names
the **two** ways back: change the blob's tier, or copy it to a new blob in an
online tier. Neither steps through Cold and Cool on the way: the target can be
any online tier directly.

### 5. Rehydrate: High versus Standard priority

A second file, `report-archive-standard.txt`, was archived so both speeds could
run side by side. Each was moved back to **Hot** with **Change tier**, one at
each **rehydrate priority**. The portal warns: *"Rehydrating a blob from
Archive to Hot or Cool may take several hours to complete."*

![High priority](screenshots/02-19-rehydrate-high.png)
![Standard priority](screenshots/02-20-rehydrate-standard.png)

Both started at 19:10 UTC (20 seconds apart) and immediately read
**Archive (rehydrating to Hot)**: still archive, still unreadable, until the
copy back online finishes.

![Both rehydrating](screenshots/02-21-both-rehydrating.png)

Prediction: High within an hour, Standard several hours. Both correct: High ≈ 37 minutes, Standard ≈ 3 h 15 min, far inside its 15-hour ceiling.

| File | Priority | Started (UTC) | Online (UTC) | Took |
|---|---|---|---|---|
| `report-archive.txt` | High | 19:10:03 | ≈ 19:47 | **≈ 37 minutes** |
| `report-archive-standard.txt` | Standard | 19:10:23 | ≈ 22:21 to 22:25 | **≈ 3 h 15 min** |

Status was read every two minutes with `az storage blob show`, so the High
finish time is accurate to about two minutes; Standard was checked every five.

### 6. A lifecycle rule

Moving files by hand does not scale. **Lifecycle management** applies rules
once a day: `tier-by-age` moves blobs to Cool **30 days** after their last
modification and to Archive at **180 days**, both counted from the same last
change (180 is not 30 + 180). Changing tier does not count as a modification;
editing a file resets the clock.

![Rule details](screenshots/02-22-lifecycle-rule-details.png)

*Base blobs* means the current file, as opposed to snapshots or old versions;
real policies often add separate rules to expire old versions, which pile up
unseen. *Skip blobs rehydrated in the last 7 days* stops a rule from
re-archiving a file someone has just brought back.

![30 and 180 days](screenshots/02-23-lifecycle-30-180.png)
![Prefix filter](screenshots/02-24-lifecycle-prefix.png)

The prefix `tiers/lc-` limits the rule to files whose names start with `lc-`,
so the four test files are untouched. A new rule *"can take up to 24 hours to
go into effect"*, and at 30 days it would never fire within a one-day lab: the
rule can be seen, not watched.

![Rule enabled](screenshots/02-25-lifecycle-rule-enabled.png)

**Code View** shows the same rule as JSON (`tierToCool`,
`daysAfterModificationGreaterThan: 30`, `daysAfterLastTierChangeGreaterThan: 7`,
`prefixMatch`): every click became a line of text that could live in Git.

![The rule as JSON](screenshots/02-26-lifecycle-code-view.png)

### 7. A fast rule to watch over a few days

To see a rule actually act, a second rule, `fast-demo`, uses the shortest
practical gaps: Cool after **1** day, Cold after **2**, Archive after **3**,
on three new files `lc-1.txt` to `lc-3.txt` uploaded Hot. Days are the
smallest unit lifecycle rules accept, and rules run once a day, so this plays
out over about four days.

![fast-demo: 1, 2, 3 days](screenshots/02-27-fast-demo-1-2-3.png)
![fast-demo prefix](screenshots/02-28-fast-demo-prefix.png)

Both rules match the `lc-` files. Where rules overlap, the cheapest action
wins, so `fast-demo` decides.

| Daily run (UTC) | `lc-1.txt` to `lc-3.txt` | Run summary |
|---|---|---|
| 31 Oct, 22:55 | stayed Hot | nothing to move: the files were under a day old |
| 1 Nov, 22:26 | **Hot to Cool**, all three | `tierToCool` 3 of 3 succeeded |
| 2 Nov, 22:26 | **Cool to Cold**, all three | `tierToCold` 3 of 3 succeeded |
| 3 Nov | *pending: Archive* | |

The first move arrived on the phone as it happened: three tier-change alerts
at the same minute, then the run's summary about **30 minutes later**. The
alerts show the lifecycle engine changing tiers through the same
`SetBlobTier` operation a person uses in the portal; only the timing is
automated.

![First lifecycle moves, as phone alerts](screenshots/02-47-phone-first-lifecycle-moves.png)
![Second run: Cool to Cold](screenshots/02-48-phone-cool-to-cold.png)

### 8. Alerts on every tier change

Instead of checking the portal, every tier change now pushes a notification to
a phone:

```
storage account ──event──► Event Grid ──► Logic App ──HTTP POST──► ntfy.sh/<private topic> ──push──► phone
```

- **Event Grid** is Azure's event router. A storage account publishes events
  such as `Microsoft.Storage.BlobTierChanged` (one blob changed tier) and
  `Microsoft.Storage.LifecyclePolicyCompleted` (the daily rule run finished).
- **Logic App** (Consumption plan, pay per run) subscribes with the trigger
  *When a resource event occurs*: Azure's own resource events, as opposed to
  *When an event occurs*, which is for events your own apps publish.
- **ntfy** is a free publish/subscribe relay. The phone app subscribes to a
  topic; anything POSTed to `https://ntfy.sh/<topic>` is pushed to it. Anyone
  who knows a topic name can read it, so the topic is random and kept out of
  this repository.

Email was the first idea, but a Logic App cannot send mail through a personal
Gmail account, so a push service was used instead.

![Logic App hosting plans](screenshots/02-29-logic-app-plans.png)
![Logic App basics](screenshots/02-30-logic-app-basics.png)
![Trigger with both event types](screenshots/02-31-trigger-event-types.png)

The trigger's connection uses **OAuth**, so it acts as the signed-in Owner. A
production version would use a managed identity with only the rights it needs,
the same least-privilege point as lab 01's Tag Contributor finding.

The action is the built-in **HTTP** step. Its body must be inserted as an
**expression** (an *fx* chip); pasted as plain text it would send the formula's
own words.

![HTTP action with the body expression](screenshots/02-32-http-body-expression.png)

**Gotcha: the trigger failed silently.** After publishing, no event
subscription existed and the trigger's history read *Failed*. The cause was
the subscription itself: the **`Microsoft.EventGrid` resource provider was
not registered** on `sub-noble-seclab-001`. Every Azure service is a resource
provider that has to be switched on per subscription; common ones are
registered automatically, Event Grid was not. Registering it and publishing
again created the subscription.

![Registering Microsoft.EventGrid](screenshots/02-33-eventgrid-provider.png)

```
az provider show -n Microsoft.EventGrid --query registrationState   →  Registered
trigger status                                                       →  Succeeded (was Failed)
event subscription                                                   →  WebHook, BlobTierChanged + LifecyclePolicyCompleted
```

**Test.** `report-hot.txt` was moved Hot → Cool by hand. The Logic App ran one
second later and ntfy received the message. The test push arrived first:

![Test push](screenshots/02-35-phone-test-push.png)

The first real alert carried the raw event type and path:

![First alert](screenshots/02-36-phone-first-alert.png)

The event's own payload carries `previousTier`, `accessTier` and the `api`
that made the change, so the body became a conditional expression:

```
if(equals(triggerBody()?['eventType'],'Microsoft.Storage.BlobTierChanged'),
   concat(last(split(triggerBody()?['subject'],'/')), ': ',
          triggerBody()?['data']?['previousTier'], ' -> ',
          triggerBody()?['data']?['accessTier'], ' (by ', triggerBody()?['data']?['api'], ')'),
   concat('Daily lifecycle run finished: ', string(triggerBody()?['data'])))
```

Moving the file back to Hot produced *report-hot.txt: Cool -> Hot (by
SetBlobTier)*:

![Formatted alert](screenshots/02-37-phone-formatted-alert.png)

That move back also took a blob out of Cool minutes after it went in, well
inside Cool's 30-day minimum: an early-deletion charge to look for on the bill
(question 3).

![lc files uploaded; report-archive.txt back online](screenshots/02-34-lc-files-and-archive-online.png)

### 9. Switch off the master keys

Until now the portal read files with the account's **access key**, a master
password for the whole account. **Configuration > Allow storage account key
access: Disabled.** The portal warns that every Shared Key request, including
SAS tokens signed with the key, will now be refused.

![Key access disabled](screenshots/02-38-key-access-disabled.png)

The container stopped listing anything, for the subscription **Owner**:

> You do not have permissions to list the data using your user account with
> Microsoft Entra ID.

![Owner cannot read the data](screenshots/02-39-owner-cannot-read-data.png)

Azure keeps two kinds of rights apart:

| Kind | Roles | Controls |
|---|---|---|
| Management (control plane) | Owner, Contributor, Reader | the storage account: settings, networking, deletion |
| Data (data plane) | Storage Blob Data Reader / Contributor / Owner | the files inside |

Owner is all control plane. The key had been hiding the missing data role.

### 10. Grant only what is needed

**Storage Blob Data Reader**, assigned on the **`tiers` container** (not the
account), to the one user, with an audit-style description: purpose, scope,
why Reader and not Contributor, approver, review date, change reference. No ABAC
condition; the container scope was narrow enough.

![Assigning Storage Blob Data Reader](screenshots/02-40-assign-blob-data-reader.png)

The user's access on the container now shows the difference between inherited
and direct rights:

![Owner inherited, Reader direct](screenshots/02-41-my-access-inherited-vs-direct.png)

The first read, seconds after assigning, still failed: role assignments take a
few minutes to reach the storage service. A few minutes later, with the
container switched to **Microsoft Entra user account** authentication, all
eight files listed and opened.

![Entra authentication lists the files](screenshots/02-42-entra-auth-lists-files.png)

Upload was refused, as it should be: *"This request is not authorized to
perform this operation using this permission."* Reader reads; it cannot
upload, delete, overwrite or even change a blob's tier.

![Reader cannot upload](screenshots/02-43-reader-cannot-upload.png)

The command-line status checks used for step 5 had been reading with the key
too; they were switched to the same identity (`--auth-mode login`) and worked
under the Reader role, so even the lab's own tooling ended up on least
privilege.

### 11. Share one file safely: a user delegation SAS

A **shared access signature (SAS)** is a URL with a permission slip built in:
which file, which actions, from when, until when. Whoever holds the URL can use
it, with no Azure account at all.

| SAS type | Signed with | Works with key access off? |
|---|---|---|
| Account SAS, service SAS | the account key | no |
| **User delegation SAS** | a key Azure issues to a signed-in Entra identity | **yes** |

**Generate SAS** on `report-hot.txt`: signing method **User delegation key**
(Account key was greyed out, with the warning that Shared Key requests would be
denied), permission **Read**, valid for **one hour**, **HTTPS only**, no IP
restriction, user-bound off.

![User delegation SAS](screenshots/02-44-sas-user-delegation.png)

A SAS can never grant more than its signer holds. The signer here has
Storage Blob Data Reader, so a link signed by this user cannot write whatever
boxes are ticked.

Pasted into a private browser window with no sign-in, the URL returned the
file:

![The SAS opens with no sign-in](screenshots/02-45-sas-opens-incognito.png)

The URL's query string carries the slip in plain view: `sp=r` (read),
`st` and `se` (start and expiry, UTC), `skoid` (the signer's object ID), and
`sig`, a signature computed over all of it. Changing **one character** of `sig`
was refused:

```
AuthenticationFailed: Signature did not match.
```

![A tampered SAS is refused](screenshots/02-46-sas-tampered-refused.png)

So a holder cannot widen `sp=r` to write or push `se` later; the only lever is
the expiry, and the link dies on its own. The flip side: until it expires,
anyone who gets the URL can use it, so a SAS URL is handled like a password.
The account's **Configuration** page can cap every SAS's lifetime
(*upper limit for SAS expiry*), a sensible default in a real tenant.

## Break it

Every break ran inside the build:

| Attempt | Result | Why |
|---|---|---|
| Open or download the archived file | refused: *not permitted on an archived blob* | Archive is offline storage |
| Set the account's default tier to Archive | not offered | a default must be readable |
| Phone alerts straight after publishing | trigger *Failed*, no event subscription | `Microsoft.EventGrid` provider not registered |
| HTTP body pasted as text | the formula itself would have been sent | expressions must be inserted as *fx* |
| Read files with key access disabled, as Owner | refused | Owner is control plane only |
| Read seconds after assigning Reader | refused | role assignments take minutes to arrive |
| Upload as Storage Blob Data Reader | refused: *not authorized* | Reader cannot write |
| SAS URL with one character of `sig` changed | refused: *Signature did not match* | the signature covers every field |

## Rebuild it as code

Planned, after the waiting items below are recorded: the storage account
(keys off, anonymous off, TLS 1.2), container, both lifecycle rules and the
role assignment in Bicep. The lifecycle rules translate almost one to one: the
portal's **Code View** already shows them as JSON.

## What I found

**1. The colder the tier, the cheaper to keep and the dearer to read.** From the
reader's side Hot, Cool and Cold behave identically: the files opened straight
away in all three. The difference is only on the bill, which will be read
before question 1 is answered here.

**2. Archive is offline, not slow.** An archived blob cannot be opened or
downloaded at all. Getting it back means changing its tier, or copying it, to
any online tier directly; there is no stepping through Cold and Cool. High
priority took about **37 minutes** for a tiny file and Standard about **3 hours 15 minutes**: roughly five times longer, for the same 150-byte file.

**3. Minimum stays are charged, not enforced.** Azure let a file leave Cool
minutes after entering it. The 30-day minimum is billed, not blocked: the
early-deletion charge should appear on the bill.

**4. Owner is not data access.** With key access disabled, the subscription
Owner could not list a single file. A data-plane role, Storage Blob Data
Reader, scoped to one container, restored read access and nothing more:
upload was still refused. Sharing still worked without the key: a one-hour,
read-only **user delegation SAS**, signed with Entra, opened the file in a
browser with no sign-in, and a single altered character in its signature was
refused.

**Also learned:**

- The portal read the files with the account key until it was switched off:
  *Authentication method: Access key* was on screen the whole time.
- Workload presets on the create form reset earlier fields; the resource group
  silently changed to `NetworkWatcherRG`.
- Lifecycle rules count days from the last modification, run once a day, and
  "can take up to 24 hours" to start. A 30-day rule cannot be watched inside a
  one-day lab, hence the 1/2/3-day rule.
- A new subscription may need resource providers registered before a service
  works, and the failure can be silent.
- Storage events carry `previousTier`, `accessTier` and the `api` that made the
  change: enough for a useful one-line alert.

**The one sentence to remember:** *Tiers trade the cost of keeping against the
cost and speed of reading; Archive is offline until rehydrated, minimum stays
are billed rather than enforced, and managing a storage account never implies
reading its data.*

## Still waiting on

| Item | Expected | Where it goes |
|---|---|---|
| `fast-demo` moving `lc-1` to `lc-3` to Archive | daily run on 3 Nov, about 22:26 UTC | step 7 table, phone screenshots |
| Early-deletion charge for Cool and Archive | 24 to 48 h on the bill | question 3, Cost |
| Real per-tier costs | Cost Management, a few days in | question 1 |

## Cost

A few cents. The files are tiny and storage is billed per GB per month. The
items worth watching are the **early-deletion charges** (Cool's 30-day
minimum was broken on purpose; the archived files will be deleted inside 180
days), High-priority rehydration, and Logic App runs, which are billed per
action and come to fractions of a cent here. Real figures from Cost Management
will replace this paragraph.

## Teardown

Deleting the resource group removes the storage account, the Logic App and its
Event Grid subscription. Deleting archived blobs early bills the rest of their
180 days; for a few kilobytes that is a fraction of a cent, and it is part of
what this lab measures.

```bash
az group delete --name rg-lab-storage-tiers --yes --no-wait
```

The ntfy topic needs no cleanup: with the Logic App gone it simply goes quiet.
