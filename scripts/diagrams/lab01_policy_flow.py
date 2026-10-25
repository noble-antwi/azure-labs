"""Builds 01-governance-tagging/diagrams/policy-flow.svg: an animated view of
three create requests passing through the lab's four policies.
Palette: Biira (navy / cyan / teal / rust), flat fills, no gradients."""
import sys

OUT = sys.argv[1]

NAVY, NAVY2, CYAN, CYAN_INK = "#08152F", "#1B2F5E", "#2DD4E8", "#0E7490"
TEAL, RUST, SLATE, SKY, ICE, MINT, ROSE, AMBER = (
    "#0F6E56", "#B0422A", "#5B6B85", "#ECF6F9", "#D6EEF4", "#E3F4EE", "#F7E4DF", "#D98E04")
INK, LINE, WHITE = "#16202B", "#D3DEE6", "#FFFFFF"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 730
CYCLE = 14  # seconds per loop

# gate centres (x) and lane centres (y)
GATES = [
    ("P1", "Modify", "inherit costCenter", "resource group", 360, "modify"),
    ("P2", "Deny", "require costCenter", "resource group", 540, "deny"),
    ("P3", "Deny", "require owner", "resource group", 720, "deny"),
    ("P4", "Deny", "allowed locations: East US", "subscription", 900, "deny"),
]
LANES = [
    # name, request text, region, stop gate index (None = created), outcome, outcome sub
    ("vnet-p3-ok", "tags: owner", "East US", None,
     "Created", "costCenter added, owner kept"),
    ("vnet-p3-noowner", "tags: none", "East US", 2,
     "Refused by P3", "RequestDisallowedByPolicy"),
    ("vnet-westus", "tags: owner", "West US", 3,
     "Refused by P4", "RequestDisallowedByPolicy"),
]
LANE_Y = [300, 420, 540]
PKT_W, PKT_H = 176, 58
START_CX = 150          # packet centre at rest
RESULT_CX = 1080

# timeline (fractions of the cycle) for reaching each stop
T_START = 0.06
T_GATE = [0.16, 0.30, 0.44, 0.58]
T_RESULT = 0.72
T_HOLD_END = 0.92


def pct(f):
    return f"{f * 100:.1f}%"


def stops_for(stop):
    """(time, translateX) keyframes for one lane."""
    pts = [(0.0, 0), (T_START, 0)]
    last = len(GATES) if stop is None else stop + 1
    for i in range(last):
        pts.append((T_GATE[i], GATES[i][4] - START_CX))
    if stop is None:
        pts.append((T_RESULT, RESULT_CX - START_CX))
    end_x = pts[-1][1]
    pts += [(T_HOLD_END, end_x), (1.0, end_x)]
    return pts


css = [f"""
.t{{font-family:{FONT};fill:{INK}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important}} }}
@keyframes fadecycle{{0%,{pct(T_HOLD_END)}{{opacity:1}}97%{{opacity:0}}100%{{opacity:0}}}}
"""]

body = []
add = body.append

# card and masthead
add(f'<rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="{WHITE}"/>')
add(f'<rect x="0" y="0" width="{W}" height="96" rx="18" fill="{NAVY}"/>')
add(f'<rect x="0" y="78" width="{W}" height="18" fill="{NAVY}"/>')
add(f'<rect x="0" y="96" width="{W}" height="4" fill="{CYAN}"/>')
add(f'<text class="t" x="40" y="44" font-size="24" font-weight="700" fill="{WHITE}" style="fill:{WHITE}">How Azure Policy judged three requests</text>')
add(f'<text class="t" x="40" y="74" font-size="14" style="fill:{ICE}">azure-labs &#183; lab 01 governance and tagging &#183; every create or update runs Modify first, then every Deny</text>')

# order strip
add(f'<text class="t" x="40" y="132" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE}">EVALUATION ORDER</text>')
order = [("1  Modify / Append", CYAN_INK, ICE), ("2  Deny", RUST, ROSE), ("3  Audit", SLATE, SKY),
         ("4  DeployIfNotExists", SLATE, SKY)]
ox = 180
for label, fg, bg in order:
    wpx = 26 + 8 * len(label)
    add(f'<rect x="{ox}" y="116" width="{wpx}" height="24" rx="12" fill="{bg}" stroke="{fg}" stroke-width="1"/>')
    add(f'<text class="t" x="{ox + wpx / 2}" y="133" font-size="12" font-weight="600" text-anchor="middle" style="fill:{fg}">{label}</text>')
    ox += wpx + 26
    if label != order[-1][0]:
        add(f'<path d="M{ox - 22} 128 h14 m-5 -4 l5 4 l-5 4" fill="none" stroke="{SLATE}" stroke-width="1.5"/>')

# column headings + gate pillars
for code, eff, desc, scope, gx, kind in GATES:
    fg, bg = (CYAN_INK, ICE) if kind == "modify" else (RUST, ROSE)
    add(f'<rect x="{gx - 62}" y="160" width="124" height="460" rx="14" fill="{bg}" opacity="0.65"/>')
    add(f'<rect x="{gx - 62}" y="160" width="124" height="6" rx="3" fill="{fg}"/>')
    add(f'<text class="t" x="{gx}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{fg}">{code} &#183; {eff}</text>')
    add(f'<text class="t" x="{gx}" y="207" font-size="11" text-anchor="middle" style="fill:{INK}">{desc}</text>')
    sc_fg = AMBER if scope == "subscription" else SLATE
    add(f'<text class="t" x="{gx}" y="222" font-size="10" font-weight="600" letter-spacing="0.8" text-anchor="middle" style="fill:{sc_fg}">ON {scope.upper()}</text>')

# result column heading
add(f'<text class="t" x="{RESULT_CX}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{NAVY}">Result</text>')
add(f'<text class="t" x="{START_CX}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{NAVY}">Request</text>')

for li, (name, tags, region, stop, outcome, sub) in enumerate(LANES):
    y = LANE_Y[li]
    # lane rail
    end_x = RESULT_CX if stop is None else GATES[stop][4]
    add(f'<line x1="{START_CX + PKT_W / 2}" y1="{y}" x2="{RESULT_CX - 70}" y2="{y}" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 6"/>')

    # verdict marks at each gate the packet reaches
    for gi, (code, eff, desc, scope, gx, kind) in enumerate(GATES):
        if stop is not None and gi > stop:
            continue
        failed = stop == gi
        t_show = T_GATE[gi] + 0.01
        cls = f"mk{li}{gi}"
        css.append(f"@keyframes {cls}{{0%,{pct(t_show - 0.001)}{{opacity:0}}{pct(t_show + 0.02)},{pct(T_HOLD_END)}{{opacity:1}}97%,100%{{opacity:0}}}}"
                   f".{cls}{{animation:{cls} {CYCLE}s linear infinite}}")
        my = y - 44
        if kind == "modify":
            add(f'<g class="anim {cls}"><rect x="{gx - 52}" y="{my - 13}" width="104" height="22" rx="11" fill="{CYAN_INK}"/>'
                f'<text class="t m" x="{gx}" y="{my + 3}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{WHITE}">+ costCenter</text></g>')
        elif failed:
            add(f'<g class="anim {cls}"><circle cx="{gx}" cy="{my}" r="13" fill="{RUST}"/>'
                f'<path d="M{gx - 5} {my - 5} l10 10 m0 -10 l-10 10" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round"/></g>')
        else:
            add(f'<g class="anim {cls}"><circle cx="{gx}" cy="{my}" r="13" fill="{TEAL}"/>'
                f'<path d="M{gx - 6} {my} l4 4 l8 -9" fill="none" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>')

    # moving packet
    kf = stops_for(stop)
    frames = "".join(f"{pct(t)}{{transform:translateX({x}px)}}" for t, x in kf)
    css.append(f"@keyframes mv{li}{{{frames}}}"
               f".mv{li}{{animation:mv{li} {CYCLE}s cubic-bezier(.45,.05,.35,1) infinite}}")
    t_fail = (T_GATE[stop] + 0.015) if stop is not None else T_RESULT
    bad = stop is not None
    css.append(f"@keyframes st{li}{{0%,{pct(t_fail - 0.001)}{{opacity:0}}{pct(t_fail + 0.02)},{pct(T_HOLD_END)}{{opacity:1}}97%,100%{{opacity:0}}}}"
               f".st{li}{{animation:st{li} {CYCLE}s linear infinite}}")
    t_chip = T_GATE[0] + 0.01
    css.append(f"@keyframes cp{li}{{0%,{pct(t_chip - 0.001)}{{opacity:0}}{pct(t_chip + 0.02)},{pct(T_HOLD_END)}{{opacity:1}}97%,100%{{opacity:0}}}}"
               f".cp{li}{{animation:cp{li} {CYCLE}s linear infinite}}")
    px, py = START_CX - PKT_W / 2, y - PKT_H / 2
    state_fill = RUST if bad else TEAL
    add(f'<g class="anim mv{li}">'
        f'<g style="animation:fadecycle {CYCLE}s linear infinite">'
        f'<rect x="{px}" y="{py}" width="{PKT_W}" height="{PKT_H}" rx="12" fill="{NAVY}"/>'
        f'<rect class="anim st{li}" x="{px}" y="{py}" width="{PKT_W}" height="{PKT_H}" rx="12" fill="{state_fill}"/>'
        f'<rect x="{px}" y="{py}" width="6" height="{PKT_H}" rx="3" fill="{CYAN}"/>'
        f'<text class="t m" x="{px + 16}" y="{py + 22}" font-size="13" font-weight="700" style="fill:{WHITE}">{name}</text>'
        f'<text class="t" x="{px + 16}" y="{py + 41}" font-size="11.5" style="fill:{ICE}">{tags} &#183; {region}</text>'
        f'<g class="anim cp{li}"><rect x="{px + PKT_W - 74}" y="{py - 9}" width="82" height="18" rx="9" fill="{CYAN}"/>'
        f'<text class="t" x="{px + PKT_W - 33}" y="{py + 4}" font-size="10" font-weight="700" text-anchor="middle" style="fill:{NAVY}">+ costCenter</text></g>'
        f'</g></g>')

    # outcome label (right column), fades in when lane finishes
    t_out = (T_GATE[stop] + 0.03) if stop is not None else (T_RESULT + 0.01)
    css.append(f"@keyframes oc{li}{{0%,{pct(t_out - 0.001)}{{opacity:0}}{pct(t_out + 0.03)},{pct(T_HOLD_END)}{{opacity:1}}97%,100%{{opacity:0}}}}"
               f".oc{li}{{animation:oc{li} {CYCLE}s linear infinite}}")
    oc_fg = RUST if bad else TEAL
    oc_bg = ROSE if bad else MINT
    add(f'<g class="anim oc{li}"><rect x="{RESULT_CX - 92}" y="{y + 34}" width="184" height="46" rx="10" fill="{oc_bg}" stroke="{oc_fg}" stroke-width="1.2"/>'
        f'<text class="t" x="{RESULT_CX}" y="{y + 54}" font-size="13" font-weight="700" text-anchor="middle" style="fill:{oc_fg}">{outcome}</text>'
        f'<text class="t m" x="{RESULT_CX}" y="{y + 71}" font-size="10" text-anchor="middle" style="fill:{INK}">{sub}</text></g>')

# footer
add(f'<rect x="24" y="650" width="{W - 48}" height="56" rx="12" fill="{SKY}"/>')
add(f'<rect x="40" y="666" width="22" height="24" rx="4" fill="{AMBER}"/>')
add(f'<path d="M45 666 v-5 a6 6 0 0 1 12 0 v5" fill="none" stroke="{AMBER}" stroke-width="2.5"/>')
add(f'<text class="t" x="76" y="676" font-size="13" font-weight="700" style="fill:{NAVY}">Lock on the resource group: Delete (CanNotDelete)</text>')
add(f'<text class="t" x="76" y="694" font-size="12" style="fill:{SLATE}">Blocks deletion for everyone, Owners included. Changes still go through, and still face every Deny rule.</text>')
add(f'<text class="t" x="{W - 40}" y="684" font-size="12" text-anchor="end" style="fill:{CYAN_INK}">A remediation task is an update too: P3 refused P1&#8217;s fix on vnet-before.</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Three virtual network create requests pass through policies P1 Modify, P2, P3 and P4 Deny. '
       f'vnet-p3-ok is created with costCenter added; vnet-p3-noowner is refused by P3; vnet-westus is refused by P4.">'
       f'<title>How Azure Policy judged three requests</title>'
       f'<style>{"".join(css)}</style>' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
