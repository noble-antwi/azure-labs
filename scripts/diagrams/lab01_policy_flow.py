"""Builds 01-governance-tagging/diagrams/policy-flow.svg: an animated view of
three create requests passing through the lab's four policies.
Dark "radar" look shared with the Biira Bank AI-agent lab: deep navy ground,
Signal Cyan accents, mint for allowed, coral for refused. Flat fills only.

Usage: python lab01_policy_flow.py <output.svg>
"""
import sys

OUT = sys.argv[1]

# Biira dark colourway
BG, PANEL, EDGE = "#060D1F", "#0A1830", "#1C3050"
GRID = "#101F38"
NAVY = "#08152F"
CYAN, CYAN_SOFT, ICE = "#2DD4E8", "#9BE8F2", "#D6EEF4"
SLATE_L = "#8FA3BF"
GREEN, GREEN_D = "#2BD99F", "#0F3B31"
RED, RED_D = "#FF6B5E", "#3A1620"
AMBER = "#FFC04D"
WHITE = "#F4FAFD"
MODIFY_FILL, DENY_FILL = "#0B2638", "#26131C"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 730
CYCLE = 14  # seconds per loop

GATES = [
    ("P1", "Modify", "inherit costCenter", "resource group", 360, "modify"),
    ("P2", "Deny", "require costCenter", "resource group", 540, "deny"),
    ("P3", "Deny", "require owner", "resource group", 720, "deny"),
    ("P4", "Deny", "allowed locations: East US", "subscription", 900, "deny"),
]
LANES = [
    ("vnet-p3-ok", "tags: owner", "East US", None, "Created", "costCenter added, owner kept"),
    ("vnet-p3-noowner", "tags: none", "East US", 2, "Refused by P3", "RequestDisallowedByPolicy"),
    ("vnet-westus", "tags: owner", "West US", 3, "Refused by P4", "RequestDisallowedByPolicy"),
]
LANE_Y = [300, 420, 540]
PKT_W, PKT_H = 176, 58
START_CX, RESULT_CX = 150, 1080

T_START = 0.06
T_GATE = [0.16, 0.30, 0.44, 0.58]
T_RESULT = 0.72
T_HOLD_END = 0.92


def pct(f):
    return f"{f * 100:.1f}%"


def stops_for(stop):
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
.t{{font-family:{FONT};fill:{ICE}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important}} }}
@keyframes fadecycle{{0%,{pct(T_HOLD_END)}{{opacity:1}}97%{{opacity:0}}100%{{opacity:0}}}}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
"""]

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
  <path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/>
</pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%">
  <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.75"/>
</filter>
<filter id="glowG" x="-80%" y="-80%" width="260%" height="260%">
  <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{GREEN}" flood-opacity="0.8"/>
</filter>
<filter id="glowR" x="-80%" y="-80%" width="260%" height="260%">
  <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{RED}" flood-opacity="0.8"/>
</filter>
</defs>'''

body = []
add = body.append

add(f'<rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="{BG}"/>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="url(#grid)"/>')

# masthead with a small radar shield
add(f'<text class="t" x="96" y="44" font-size="24" font-weight="700" style="fill:{WHITE}">How Azure Policy judged three requests</text>')
add(f'<text class="t" x="96" y="74" font-size="14" style="fill:{CYAN_SOFT}">azure-labs &#183; lab 01 governance and tagging &#183; every create or update runs Modify first, then every Deny</text>')
add(f'<rect x="0" y="96" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')
add(f'<g transform="translate(52 52)">'
    f'<path d="M0 -26 L20 -17 V4 Q20 16 0 26 Q-20 16 -20 4 V-17 Z" fill="{NAVY}" stroke="{CYAN}" stroke-width="2.5" filter="url(#glowC)"/>'
    f'<circle cx="0" cy="0" r="12" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.5"/>'
    f'<circle cx="0" cy="0" r="4" fill="{CYAN}"/>'
    f'<g class="anim" style="animation:sweep 6s linear infinite;transform-origin:0px 0px">'
    f'<path d="M0 0 L-7 -16 A17 17 0 0 1 7 -16 Z" fill="{CYAN}" opacity="0.45"/></g></g>')

# evaluation order strip
add(f'<text class="t" x="40" y="132" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE_L}">EVALUATION ORDER</text>')
order = [("1  Modify / Append", CYAN), ("2  Deny", RED), ("3  Audit", SLATE_L), ("4  DeployIfNotExists", SLATE_L)]
ox = 190
for label, fg in order:
    wpx = 26 + 8 * len(label)
    add(f'<rect x="{ox}" y="116" width="{wpx}" height="24" rx="12" fill="{PANEL}" stroke="{fg}" stroke-width="1.2"/>')
    add(f'<text class="t" x="{ox + wpx / 2}" y="133" font-size="12" font-weight="600" text-anchor="middle" style="fill:{fg}">{label}</text>')
    ox += wpx + 26
    if label != order[-1][0]:
        add(f'<path d="M{ox - 22} 128 h14 m-5 -4 l5 4 l-5 4" fill="none" stroke="{SLATE_L}" stroke-width="1.5"/>')

# gate pillars
for code, eff, desc, scope, gx, kind in GATES:
    fg = CYAN if kind == "modify" else RED
    bg = MODIFY_FILL if kind == "modify" else DENY_FILL
    add(f'<rect x="{gx - 62}" y="160" width="124" height="460" rx="14" fill="{bg}" stroke="{EDGE}" stroke-width="1"/>')
    add(f'<rect x="{gx - 62}" y="160" width="124" height="6" rx="3" fill="{fg}"/>')
    add(f'<text class="t" x="{gx}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{fg}">{code} &#183; {eff}</text>')
    add(f'<text class="t" x="{gx}" y="207" font-size="11" text-anchor="middle" style="fill:{ICE}">{desc}</text>')
    sc_fg = AMBER if scope == "subscription" else SLATE_L
    add(f'<text class="t" x="{gx}" y="222" font-size="10" font-weight="600" letter-spacing="0.8" text-anchor="middle" style="fill:{sc_fg}">ON {scope.upper()}</text>')

add(f'<text class="t" x="{RESULT_CX}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{WHITE}">Result</text>')
add(f'<text class="t" x="{START_CX}" y="190" font-size="15" font-weight="700" text-anchor="middle" style="fill:{WHITE}">Request</text>')

for li, (name, tags, region, stop, outcome, sub) in enumerate(LANES):
    y = LANE_Y[li]
    add(f'<line x1="{START_CX + PKT_W / 2}" y1="{y}" x2="{RESULT_CX - 70}" y2="{y}" stroke="{EDGE}" stroke-width="2" stroke-dasharray="4 6"/>')

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
            add(f'<g class="anim {cls}"><rect x="{gx - 52}" y="{my - 13}" width="104" height="22" rx="11" fill="{CYAN}" filter="url(#glowC)"/>'
                f'<text class="t m" x="{gx}" y="{my + 3}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{NAVY}">+ costCenter</text></g>')
        elif failed:
            add(f'<g class="anim {cls}"><circle cx="{gx}" cy="{my}" r="13" fill="{RED}" filter="url(#glowR)"/>'
                f'<path d="M{gx - 5} {my - 5} l10 10 m0 -10 l-10 10" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round"/></g>')
        else:
            add(f'<g class="anim {cls}"><circle cx="{gx}" cy="{my}" r="13" fill="{GREEN}" filter="url(#glowG)"/>'
                f'<path d="M{gx - 6} {my} l4 4 l8 -9" fill="none" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>')

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
    st_fill, st_stroke = (RED_D, RED) if bad else (GREEN_D, GREEN)
    add(f'<g class="anim mv{li}">'
        f'<g style="animation:fadecycle {CYCLE}s linear infinite">'
        f'<rect x="{px}" y="{py}" width="{PKT_W}" height="{PKT_H}" rx="12" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.4"/>'
        f'<rect class="anim st{li}" x="{px}" y="{py}" width="{PKT_W}" height="{PKT_H}" rx="12" fill="{st_fill}" stroke="{st_stroke}" stroke-width="1.6"/>'
        f'<rect x="{px}" y="{py + 10}" width="5" height="{PKT_H - 20}" rx="2.5" fill="{CYAN}"/>'
        f'<text class="t m" x="{px + 18}" y="{py + 22}" font-size="13" font-weight="700" style="fill:{WHITE}">{name}</text>'
        f'<text class="t" x="{px + 18}" y="{py + 41}" font-size="11.5" style="fill:{ICE}">{tags} &#183; {region}</text>'
        f'<g class="anim cp{li}"><rect x="{px + PKT_W - 74}" y="{py - 9}" width="82" height="18" rx="9" fill="{CYAN}"/>'
        f'<text class="t" x="{px + PKT_W - 33}" y="{py + 4}" font-size="10" font-weight="700" text-anchor="middle" style="fill:{NAVY}">+ costCenter</text></g>'
        f'</g></g>')

    t_out = (T_GATE[stop] + 0.03) if stop is not None else (T_RESULT + 0.01)
    css.append(f"@keyframes oc{li}{{0%,{pct(t_out - 0.001)}{{opacity:0}}{pct(t_out + 0.03)},{pct(T_HOLD_END)}{{opacity:1}}97%,100%{{opacity:0}}}}"
               f".oc{li}{{animation:oc{li} {CYCLE}s linear infinite}}")
    oc_fg, oc_bg = (RED, RED_D) if bad else (GREEN, GREEN_D)
    add(f'<g class="anim oc{li}"><rect x="{RESULT_CX - 92}" y="{y + 34}" width="184" height="46" rx="10" fill="{oc_bg}" stroke="{oc_fg}" stroke-width="1.2"/>'
        f'<text class="t" x="{RESULT_CX}" y="{y + 54}" font-size="13" font-weight="700" text-anchor="middle" style="fill:{oc_fg}">{outcome}</text>'
        f'<text class="t m" x="{RESULT_CX}" y="{y + 71}" font-size="10" text-anchor="middle" style="fill:{ICE}">{sub}</text></g>')

# footer
add(f'<rect x="24" y="650" width="{W - 48}" height="56" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
add(f'<rect x="40" y="668" width="22" height="24" rx="4" fill="{AMBER}"/>')
add(f'<path d="M45 668 v-5 a6 6 0 0 1 12 0 v5" fill="none" stroke="{AMBER}" stroke-width="2.5"/>')
add(f'<text class="t" x="76" y="678" font-size="13" font-weight="700" style="fill:{WHITE}">Lock on the resource group: Delete (CanNotDelete)</text>')
add(f'<text class="t" x="76" y="696" font-size="12" style="fill:{SLATE_L}">Blocks deletion for everyone, Owners included. Changes still go through, and still face every Deny rule.</text>')
add(f'<text class="t" x="{W - 40}" y="686" font-size="12" text-anchor="end" style="fill:{CYAN_SOFT}">A remediation task is an update too: P3 refused P1&#8217;s fix on vnet-before.</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Three virtual network create requests pass through policies P1 Modify, P2, P3 and P4 Deny. '
       f'vnet-p3-ok is created with costCenter added; vnet-p3-noowner is refused by P3; vnet-westus is refused by P4.">'
       f'<title>How Azure Policy judged three requests</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
