"""Builds 02-storage-tiers/diagrams/tier-flow.svg: an animated view of lab 02.
A file walks down the tiers (the fast-demo lifecycle rule), goes offline in
Archive, is refused a read, and is rehydrated back to Hot. Each tier change
pulses through Event Grid and the Logic App to a phone alert.
Dark Biira colourway, flat fills, CSS animation only (plays on GitHub).

Usage: python lab02_tier_flow.py <output.svg>
"""
import sys

OUT = sys.argv[1]

BG, PANEL, EDGE, GRID = "#060D1F", "#0A1830", "#1C3050", "#101F38"
NAVY = "#08152F"
CYAN, CYAN_SOFT, ICE = "#2DD4E8", "#9BE8F2", "#D6EEF4"
SLATE_L = "#8FA3BF"
GREEN, GREEN_D = "#2BD99F", "#0F3B31"
RED, RED_D = "#FF6B5E", "#3A1620"
AMBER = "#FFC04D"
WHITE = "#F4FAFD"
# one hue per tier, warm to cold
TIERS = [
    ("HOT", "online", "none", "#FF8A5B", 1.00, 0.12),
    ("COOL", "online", "30 days", "#2DD4E8", 0.55, 0.35),
    ("COLD", "online", "90 days", "#5B8DEF", 0.30, 0.60),
    ("ARCHIVE", "OFFLINE", "180 days", "#A78BFA", 0.10, 1.00),
]
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 760
CYCLE = 18
CX = [160, 453, 746, 1040]          # tier card centres
CARD_W, CARD_TOP, CARD_H = 240, 150, 250
TOKEN_Y = 300

# timeline (fractions of the cycle)
T_MOVE = [(0.08, 0.16), (0.24, 0.32), (0.40, 0.48)]   # hot->cool->cold->archive
T_DENY = 0.54
T_REHY = (0.62, 0.74)
T_END = 0.94
PULSES = [0.16, 0.32, 0.48, 0.74]   # when an event fires
MESSAGES = [
    "lc-1.txt: Hot -> Cool",
    "lc-1.txt: Cool -> Cold",
    "lc-1.txt: Cold -> Archive",
    "lc-1.txt: Archive -> Hot",
]


def pct(f):
    return f"{f * 100:.1f}%"


css = [f"""
.t{{font-family:{FONT};fill:{ICE}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important}} }}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
"""]


def window(name, t_on, t_off, fade=0.015):
    """opacity keyframes: hidden, visible between t_on and t_off, hidden."""
    css.append(
        f"@keyframes {name}{{0%,{pct(max(t_on - 0.001, 0))}{{opacity:0}}"
        f"{pct(t_on + fade)},{pct(t_off)}{{opacity:1}}"
        f"{pct(min(t_off + fade, 0.999))},100%{{opacity:0}}}}"
        f".{name}{{animation:{name} {CYCLE}s linear infinite}}")


body = []
add = body.append

add(f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>')
add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>')

# masthead
add(f'<g transform="translate(52 52)">'
    f'<path d="M0 -26 L20 -17 V4 Q20 16 0 26 Q-20 16 -20 4 V-17 Z" fill="{NAVY}" stroke="{CYAN}" stroke-width="2.5" filter="url(#glowC)"/>'
    f'<circle r="12" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.5"/><circle r="4" fill="{CYAN}"/>'
    f'<g class="anim" style="animation:sweep 6s linear infinite;transform-origin:0px 0px">'
    f'<path d="M0 0 L-7 -16 A17 17 0 0 1 7 -16 Z" fill="{CYAN}" opacity="0.45"/></g></g>')
add(f'<text class="t" x="96" y="44" font-size="24" font-weight="700" style="fill:{WHITE}">Where a file lives, and what it takes to get it back</text>')
add(f'<text class="t" x="96" y="74" font-size="14" style="fill:{CYAN_SOFT}">azure-labs &#183; lab 02 storage tiers &#183; lifecycle moves it down, Archive takes it offline, rehydration brings it back</text>')
add(f'<rect x="0" y="96" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')

# legend for the bars
add(f'<text class="t" x="40" y="132" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE_L}">EACH TIER (bars are relative, not to scale)</text>')
add(f'<rect x="372" y="122" width="22" height="8" rx="4" fill="{GREEN}"/><text class="t" x="400" y="131" font-size="12" style="fill:{ICE}">cost to keep</text>')
add(f'<rect x="500" y="122" width="22" height="8" rx="4" fill="{RED}"/><text class="t" x="528" y="131" font-size="12" style="fill:{ICE}">cost to read</text>')

# tier cards
for i, (name, state, minstay, hue, keep, read) in enumerate(TIERS):
    cx = CX[i]
    x0 = cx - CARD_W / 2
    add(f'<rect x="{x0}" y="{CARD_TOP}" width="{CARD_W}" height="{CARD_H}" rx="16" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
    add(f'<rect x="{x0}" y="{CARD_TOP}" width="{CARD_W}" height="6" rx="3" fill="{hue}"/>')
    add(f'<text class="t" x="{cx}" y="{CARD_TOP + 38}" font-size="20" font-weight="800" letter-spacing="2" text-anchor="middle" style="fill:{hue}">{name}</text>')
    st_fill = RED if state == "OFFLINE" else GREEN
    add(f'<text class="t" x="{cx}" y="{CARD_TOP + 58}" font-size="11" font-weight="700" letter-spacing="1.5" text-anchor="middle" style="fill:{st_fill}">{state.upper()}</text>')
    # bars
    bx, bw = x0 + 24, CARD_W - 48
    add(f'<rect x="{bx}" y="{CARD_TOP + 186}" width="{bw}" height="8" rx="4" fill="{EDGE}"/>')
    add(f'<rect x="{bx}" y="{CARD_TOP + 186}" width="{bw * keep:.0f}" height="8" rx="4" fill="{GREEN}"/>')
    add(f'<rect x="{bx}" y="{CARD_TOP + 206}" width="{bw}" height="8" rx="4" fill="{EDGE}"/>')
    add(f'<rect x="{bx}" y="{CARD_TOP + 206}" width="{bw * read:.0f}" height="8" rx="4" fill="{RED}"/>')
    add(f'<text class="t" x="{cx}" y="{CARD_TOP + 238}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">minimum stay: {minstay}</text>')

# arrows between cards with lifecycle day labels
for i in range(3):
    xa = CX[i] + CARD_W / 2 + 4
    xb = CX[i + 1] - CARD_W / 2 - 4
    add(f'<path d="M{xa} {TOKEN_Y} H{xb - 6} m-6 -5 l6 5 l-6 5" fill="none" stroke="{SLATE_L}" stroke-width="1.6"/>')
    add(f'<text class="t" x="{(xa + xb) / 2}" y="{TOKEN_Y - 12}" font-size="10" text-anchor="middle" style="fill:{SLATE_L}">day {i + 1}</text>')

# offline padlock on archive
lx, ly = CX[3], 232
window("lock", T_MOVE[2][1], T_REHY[0])
add(f'<g class="anim lock"><rect x="{lx - 14}" y="{ly}" width="28" height="22" rx="4" fill="{RED}"/>'
    f'<path d="M{lx - 8} {ly} v-6 a8 8 0 0 1 16 0 v6" fill="none" stroke="{RED}" stroke-width="3"/></g>')

# denied read bubble
window("deny", T_DENY, T_REHY[0])
add(f'<g class="anim deny"><rect x="{CX[3] - 118}" y="412" width="236" height="34" rx="10" fill="{RED_D}" stroke="{RED}" stroke-width="1.2"/>'
    f'<text class="t" x="{CX[3]}" y="434" font-size="11.5" font-weight="600" text-anchor="middle" style="fill:{RED}">read refused: blob is archived</text></g>')

# rehydration arc (archive back to hot)
arc = f"M{CX[3]} {CARD_TOP + CARD_H + 8} C {CX[3]} 470, {CX[0]} 470, {CX[0]} {CARD_TOP + CARD_H + 8}"
window("rarc", T_REHY[0], T_END)
add(f'<path class="anim rarc" d="{arc}" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="6 6"/>')
add(f'<g class="anim rarc"><rect x="{(CX[0] + CX[3]) / 2 - 170}" y="436" width="340" height="30" rx="15" fill="{PANEL}" stroke="{AMBER}" stroke-width="1"/>'
    f'<text class="t" x="{(CX[0] + CX[3]) / 2}" y="456" font-size="12" font-weight="600" text-anchor="middle" style="fill:{AMBER}">rehydrate: High &#8776; 37 min &#183; Standard up to 15 h</text></g>')

# the travelling file token
frames = [(0.0, CX[0]), (T_MOVE[0][0], CX[0]), (T_MOVE[0][1], CX[1]), (T_MOVE[1][0], CX[1]),
          (T_MOVE[1][1], CX[2]), (T_MOVE[2][0], CX[2]), (T_MOVE[2][1], CX[3]), (T_REHY[0], CX[3])]
kf = "".join(f"{pct(t)}{{transform:translate({x - CX[0]}px,0px)}}" for t, x in frames)
# arc back: approximate with a few points along the curve
for k in range(1, 9):
    u = k / 8
    # cubic bezier x(u), y(u) between archive and hot along the arc
    p0, p1, p2, p3 = (CX[3], 0), (CX[3], 170), (CX[0], 170), (CX[0], 0)
    x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
    y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
    t = T_REHY[0] + (T_REHY[1] - T_REHY[0]) * u
    kf += f"{pct(t)}{{transform:translate({x - CX[0]:.0f}px,{y:.0f}px)}}"
kf += f"100%{{transform:translate(0px,0px)}}"
css.append(f"@keyframes tok{{{kf}}}.tok{{animation:tok {CYCLE}s cubic-bezier(.45,.05,.35,1) infinite}}")
# token colour: normal, then grey while archived
window("tokoff", T_MOVE[2][1], T_REHY[0])
tx = CX[0]
add(f'<g class="anim tok">'
    f'<rect x="{tx - 58}" y="{TOKEN_Y - 20}" width="116" height="40" rx="10" fill="{WHITE}" filter="url(#glowC)"/>'
    f'<rect class="anim tokoff" x="{tx - 58}" y="{TOKEN_Y - 20}" width="116" height="40" rx="10" fill="{SLATE_L}"/>'
    f'<path d="M{tx - 44} {TOKEN_Y - 11} h12 l6 6 v16 h-18 z" fill="none" stroke="{NAVY}" stroke-width="1.6"/>'
    f'<text class="t m" x="{tx - 18}" y="{TOKEN_Y + 5}" font-size="13" font-weight="700" style="fill:{NAVY}">lc-1.txt</text></g>')

# event pipeline
PY = 600
nodes = [("Storage account", "BlobTierChanged", 130), ("Event Grid", "routes the event", 370),
         ("Logic App", "builds the message", 610), ("ntfy.sh", "private topic", 850), ("Phone", "push alert", 1070)]
add(f'<text class="t" x="40" y="{PY - 66}" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE_L}">EVERY TIER CHANGE BECOMES A PHONE ALERT</text>')
add(f'<line x1="{nodes[0][2]}" y1="{PY}" x2="{nodes[-1][2]}" y2="{PY}" stroke="{EDGE}" stroke-width="2"/>')
for label, sub, nx in nodes:
    add(f'<rect x="{nx - 92}" y="{PY - 30}" width="184" height="60" rx="12" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.2"/>')
    add(f'<text class="t" x="{nx}" y="{PY - 4}" font-size="14" font-weight="700" text-anchor="middle" style="fill:{WHITE}">{label}</text>')
    add(f'<text class="t" x="{nx}" y="{PY + 15}" font-size="11" text-anchor="middle" style="fill:{CYAN_SOFT}">{sub}</text>')

# pulses + phone messages
for k, tp in enumerate(PULSES):
    name = f"pl{k}"
    t1 = tp + 0.07
    css.append(f"@keyframes {name}{{0%,{pct(tp - 0.001)}{{transform:translateX(0px);opacity:0}}"
               f"{pct(tp + 0.005)}{{opacity:1}}{pct(t1)}{{transform:translateX({nodes[-1][2] - nodes[0][2]}px);opacity:1}}"
               f"{pct(t1 + 0.01)},100%{{transform:translateX({nodes[-1][2] - nodes[0][2]}px);opacity:0}}}}"
               f".{name}{{animation:{name} {CYCLE}s linear infinite}}")
    add(f'<circle class="anim {name}" cx="{nodes[0][2]}" cy="{PY}" r="7" fill="{CYAN}" filter="url(#glowC)"/>')
    nxt = PULSES[k + 1] if k + 1 < len(PULSES) else T_END
    window(f"msg{k}", t1, nxt - 0.01)
    MX = min(nodes[-1][2], W - 186)
    add(f'<g class="anim msg{k}"><rect x="{MX - 150}" y="{PY + 46}" width="300" height="40" rx="12" fill="{GREEN_D}" stroke="{GREEN}" stroke-width="1.2"/>'
        f'<text class="t m" x="{MX}" y="{PY + 71}" font-size="12.5" font-weight="700" text-anchor="middle" style="fill:{GREEN}">{MESSAGES[k]}</text></g>')

# footer
add(f'<rect x="24" y="{H - 64}" width="{W - 48}" height="44" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
add(f'<text class="t" x="44" y="{H - 37}" font-size="12.5" style="fill:{ICE}">'
    f'<tspan font-weight="700" style="fill:{AMBER}">Keys off.</tspan> Owner manages the account but cannot read a file; '
    f'reading takes a data role. Storage Blob Data Reader on the container: list and read, never write.</text>')

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.7"/></filter>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="A file moves from Hot to Cool, Cold and Archive under a lifecycle rule, is refused a read while archived, '
       f'and is rehydrated back to Hot. Each tier change flows from the storage account through Event Grid and a Logic App to a phone alert.">'
       f'<title>Where a file lives, and what it takes to get it back</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
