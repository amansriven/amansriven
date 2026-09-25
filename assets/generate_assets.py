"""Generates the animated SVG assets for the profile README."""
from html import escape
import os
import random

MONO = "'JetBrains Mono','Fira Code','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
# github dark neutrals + a blue -> indigo gradient accent
BG, BAR, LINE = "#0D1117", "#161B22", "#30363D"
TEXT, BODY, MUTED, DIM = "#E6EDF3", "#C9D1D9", "#8B949E", "#6E7681"
BLUE, INDIGO, SHEEN = "#7AA2F7", "#8B7CF6", "#DCE6FF"
# footer + divider sit on the page background, so they must read on light and dark
BLUE_MID, INDIGO_MID = "#5B8DEF", "#7C6CF0"
OUT = os.path.dirname(os.path.abspath(__file__))  # writes next to this script
os.makedirs(OUT, exist_ok=True)
random.seed(7)  # stable output, so regenerating doesn't produce noisy diffs


def typed(text, start, step, cls=""):
    """Each character is a tspan that becomes visible at its own time -> typing effect.
    Uses natural font metrics, so it works with whatever monospace font the viewer has."""
    parts = []
    for i, ch in enumerate(text):
        t = start + i * step
        parts.append(
            f'<tspan visibility="hidden"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{escape(ch)}'
            f'<set attributeName="visibility" to="visible" begin="{t:.2f}s" fill="freeze"/></tspan>'
        )
    return "".join(parts), start + len(text) * step


def decoded(text, x, y, start, size, cls):
    """Decode effect: each glyph cycles through random symbols before resolving.
    Glyphs are absolutely positioned at a 0.6em monospace advance."""
    pool = "01<>/\\{}[]#$%&*+=?!_"
    adv = size * 0.6
    out, end = [], start
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        gx = x + i * adv
        t = start + i * 0.035
        resolve = start + 0.28 + i * 0.07
        while t < resolve:
            out.append(f'<text x="{gx:.1f}" y="{y}" class="scr" visibility="hidden">{escape(random.choice(pool))}'
                       f'<set attributeName="visibility" to="visible" begin="{t:.2f}s"/>'
                       f'<set attributeName="visibility" to="hidden" begin="{t + 0.055:.2f}s" fill="freeze"/></text>')
            t += 0.055
        out.append(f'<text x="{gx:.1f}" y="{y}" class="{cls}" visibility="hidden">{escape(ch)}'
                   f'<set attributeName="visibility" to="visible" begin="{resolve:.2f}s" fill="freeze"/></text>')
        end = resolve
    return "".join(out), end


def show_at(t):
    return f'<set attributeName="visibility" to="visible" begin="{t:.2f}s" fill="freeze"/>'


def fade_in(t, dur=0.6, dy=8):
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" '
            f'begin="{t:.2f}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>')


def blink(begin):
    return (f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="1.05s" begin="{begin:.2f}s" repeatCount="indefinite"/>')


def rounded_rect_path(x, y, w, h, r):
    return (f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} "
            f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} "
            f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z")


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 500
    x0 = 56
    NAME_SIZE = 70

    # line 1: $ whoami
    l1, t = typed("whoami", 0.6, 0.09)
    # line 2: name, decoded from noise
    name, t_name_end = decoded("aman sriven", x0 - 4, 196, t + 0.3, NAME_SIZE, "name")
    name_w = len("aman sriven") * NAME_SIZE * 0.6
    t_tag = t_name_end + 0.2
    # line 3: $ cat ./focus.md
    t_p2 = t_tag + 0.7
    l3, t = typed("cat ./focus.md", t_p2 + 0.1, 0.05)
    t_f1, t_f2, t_f3 = t + 0.2, t + 0.45, t + 0.7
    t_final = t_f3 + 0.5

    # agent graph (right side)
    cx, cy = 985, 285
    nodes = [("planner", 830, 165), ("retriever", 1130, 165),
             ("tools", 830, 420), ("evals", 1130, 420), ("llm", 985, 135)]
    durs = [2.6, 3.1, 3.7, 2.9, 2.3]
    colors = [BLUE, INDIGO, INDIGO, BLUE, BLUE]

    edges, packets, node_svg = [], [], []
    for (label, nx, ny), d, c in zip(nodes, durs, colors):
        edges.append(f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="url(#edge)" stroke-width="1" '
                     f'stroke-dasharray="3 6"><animate attributeName="stroke-dashoffset" from="0" to="-36" '
                     f'dur="2.4s" repeatCount="indefinite"/></line>')
        packets.append(f'<circle r="2.8" fill="{c}" filter="url(#glow)">'
                       f'<animateMotion dur="{d}s" repeatCount="indefinite" '
                       f'path="M{cx},{cy} L{nx},{ny} L{cx},{cy}" keyPoints="0;0.5;1" keyTimes="0;0.5;1" '
                       f'calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1"/></circle>')
        ly = ny - 20 if ny < cy else ny + 30
        node_svg.append(
            f'<circle cx="{nx}" cy="{ny}" r="6" fill="none" stroke="{c}" stroke-width="1" opacity="0.5">'
            f'<animate attributeName="r" values="6;18" dur="{d * 1.4:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.5;0" dur="{d * 1.4:.1f}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{nx}" cy="{ny}" r="6" fill="{BG}" stroke="{c}" stroke-width="1.5"/>'
            f'<circle cx="{nx}" cy="{ny}" r="2.2" fill="{c}"/>'
            f'<text x="{nx}" y="{ly}" text-anchor="middle" class="lbl">{label}</text>')

    graph = f'''
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.9s" dur="1.2s" fill="freeze"/>
    <circle cx="{cx}" cy="{cy}" r="118" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="1 7">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="80s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx}" cy="{cy}" r="170" fill="none" stroke="url(#edge)" stroke-width="1" stroke-dasharray="40 1028" opacity="0.6">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="14s" repeatCount="indefinite"/>
    </circle>
    {''.join(edges)}
    {''.join(packets)}
    {''.join(node_svg)}
    <circle cx="{cx}" cy="{cy}" r="30" fill="url(#core)" opacity="0.3">
      <animate attributeName="r" values="24;34;24" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx}" cy="{cy}" r="15" fill="{BG}" stroke="url(#grad)" stroke-width="1.5"/>
    <circle cx="{cx}" cy="{cy}" r="4.5" fill="url(#grad)"/>
    <text x="{cx}" y="{cy + 50}" text-anchor="middle" class="lbl hi">orchestrator</text>
  </g>'''

    frame = rounded_rect_path(8.5, 8.5, W - 17, H - 17, 17.5)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="$ whoami — aman sriven, ai / ml engineer, cs @ texas a&amp;m">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{INDIGO}"/>
    </linearGradient>
    <!-- name: blue -> indigo with a soft sheen gliding through -->
    <linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="{x0 - 4}" y1="0" x2="{x0 - 4 + name_w}" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{BLUE}"/><stop offset="0.45" stop-color="{SHEEN}"/><stop offset="1" stop-color="{INDIGO}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{2 * name_w:.0f} 0" dur="9s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="800" y1="100" x2="1150" y2="420">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0.5"/><stop offset="1" stop-color="{INDIGO}" stop-opacity="0.5"/>
    </linearGradient>
    <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0.55"/><stop offset="0.5" stop-color="{LINE}"/>
      <stop offset="1" stop-color="{INDIGO}" stop-opacity="0.55"/>
    </linearGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{INDIGO}"/>
    </linearGradient>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0.07"/>
    </linearGradient>
    <radialGradient id="core"><stop offset="0" stop-color="{INDIGO}"/><stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/></radialGradient>
    <radialGradient id="aura" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0.2"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aura2" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{INDIGO}" stop-opacity="0.16"/><stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/>
    </radialGradient>
    <!-- fine grid that fades out toward the edges -->
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{MUTED}" stroke-width="0.5" opacity="0.22"/>
    </pattern>
    <radialGradient id="fade" cx="0.35" cy="0.45" r="0.75">
      <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="gridmask"><rect x="0" y="0" width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <filter id="glow" x="-200%" y="-200%" width="500%" height="500%">
      <feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="halo" x="-20%" y="-60%" width="140%" height="220%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
    <filter id="beamblur" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
    <clipPath id="win"><rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="18"/></clipPath>
  </defs>
  <style>
    text {{ font-family: {MONO}; }}
    .p  {{ fill: {BLUE}; font-size: 22px; font-weight: 700; }}
    .c  {{ fill: {TEXT}; font-size: 22px; }}
    .d  {{ fill: {MUTED}; font-size: 22px; }}
    .o  {{ fill: {BODY}; font-size: 20px; }}
    .ar {{ fill: {BLUE}; }}
    .k  {{ fill: {DIM}; }}
    .lbl {{ fill: {MUTED}; font-size: 13px; letter-spacing: 0.5px; }}
    .hi {{ fill: {TEXT}; }}
    .name {{ fill: url(#shimmer); font-size: {NAME_SIZE}px; font-weight: 800; }}
    .scr  {{ fill: {BLUE}; opacity: 0.55; font-size: {NAME_SIZE}px; font-weight: 400; }}
    .meta {{ fill: {DIM}; font-size: 12px; letter-spacing: 0.5px; }}
  </style>

  <!-- window -->
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="18" fill="{BG}"/>
  <g clip-path="url(#win)">
    <rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="url(#grid)" mask="url(#gridmask)"/>
    <ellipse cx="300" cy="215" rx="340" ry="170" fill="url(#aura)">
      <animate attributeName="cx" values="260;380;260" dur="14s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="985" cy="285" rx="260" ry="220" fill="url(#aura2)">
      <animate attributeName="rx" values="240;290;240" dur="11s" repeatCount="indefinite"/>
    </ellipse>
    <!-- scan line: a faint gradient band with a crisp leading edge -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 -80;0 {H}" dur="7s" repeatCount="indefinite"/>
      <rect x="8" y="0" width="{W - 16}" height="80" fill="url(#scan)"/>
      <rect x="8" y="79.5" width="{W - 16}" height="1" fill="{BLUE}" opacity="0.12"/>
    </g>
    <!-- title bar -->
    <rect x="8" y="8" width="{W - 16}" height="44" fill="{BAR}" opacity="0.92"/>
    <line x1="8" y1="52" x2="{W - 8}" y2="52" stroke="{LINE}"/>
  </g>

  <!-- frame: gradient hairline + a light beam travelling around it -->
  <path d="{frame}" fill="none" stroke="url(#frame)" stroke-width="1"/>
  <path d="{frame}" pathLength="1000" fill="none" stroke="url(#beam)" stroke-width="3" stroke-linecap="round"
        stroke-dasharray="90 910" filter="url(#beamblur)" opacity="0.8">
    <animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="10s" repeatCount="indefinite"/>
  </path>
  <path d="{frame}" pathLength="1000" fill="none" stroke="url(#beam)" stroke-width="1.2" stroke-linecap="round"
        stroke-dasharray="90 910">
    <animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="10s" repeatCount="indefinite"/>
  </path>

  <circle cx="38" cy="30" r="6" fill="{LINE}"/><circle cx="60" cy="30" r="6" fill="{LINE}"/><circle cx="82" cy="30" r="6" fill="{LINE}"/>
  <text x="{W / 2}" y="35" text-anchor="middle" class="lbl">aman@tamu: ~ — zsh</text>

  <!-- terminal -->
  <text x="{x0}" y="112"><tspan class="p">❯ </tspan><tspan class="c">{l1}</tspan></text>

  <!-- soft halo behind the name, fades in once it resolves -->
  <text x="{x0 - 4}" y="196" class="name" filter="url(#halo)" opacity="0">aman sriven
    <animate attributeName="opacity" from="0" to="0.45" begin="{t_name_end:.2f}s" dur="1.2s" fill="freeze"/>
  </text>
  {name}

  <g opacity="0">{fade_in(t_tag)}
    <text x="{x0}" y="242" class="d">ai / ml engineer <tspan class="ar">·</tspan> cs @ texas a&amp;m</text>
  </g>

  <text x="{x0}" y="312" visibility="hidden">{show_at(t_p2)}<tspan class="p">❯ </tspan><tspan class="c">{l3}</tspan></text>

  <g opacity="0">{fade_in(t_f1)}
    <text x="{x0}" y="352" class="o"><tspan class="ar">→ </tspan>llm infrastructure <tspan class="k">&amp;</tspan> inference routing</text></g>
  <g opacity="0">{fade_in(t_f2)}
    <text x="{x0}" y="386" class="o"><tspan class="ar">→ </tspan>multi-agent systems at scale</text></g>
  <g opacity="0">{fade_in(t_f3)}
    <text x="{x0}" y="420" class="o"><tspan class="ar">→ </tspan>model reliability <tspan class="k">&amp;</tspan> rag evaluation</text></g>

  <text x="{x0}" y="468" visibility="hidden">{show_at(t_final)}<tspan class="p">❯ </tspan><tspan class="ar">▋{blink(t_final)}</tspan></text>

  {graph}

  <!-- statusline -->
  <g opacity="0">{fade_in(t_final, 0.8, 0)}
    <text x="{W - 40}" y="476" text-anchor="end" class="meta"><tspan fill="{BLUE}">●</tspan> 5 agents online · p50 38ms · utf-8</text>
  </g>

  <!-- live status pill -->
  <g opacity="0">{fade_in(t_final, 0.5, 0)}
    <rect x="{W - 212}" y="19" width="182" height="23" rx="11.5" fill="{BG}" stroke="{LINE}"/>
    <circle cx="{W - 195}" cy="30.5" r="3.5" fill="{BLUE}">
      <animate attributeName="opacity" values="1;0.35;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="{W - 184}" y="35" class="lbl" style="font-size:12px">open to internships</text>
  </g>
</svg>'''
    return svg, t_final


# ---------------------------------------------------------------- divider
def divider():
    W, H = 1200, 12
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="presentation">
  <defs>
    <linearGradient id="base" x1="0" x2="1">
      <stop offset="0" stop-color="{BLUE_MID}" stop-opacity="0"/><stop offset="0.2" stop-color="{BLUE_MID}" stop-opacity="0.45"/>
      <stop offset="0.8" stop-color="{INDIGO_MID}" stop-opacity="0.45"/><stop offset="1" stop-color="{INDIGO_MID}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="spark" x1="0" x2="1">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset="0.5" stop-color="{SHEEN}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/>
    </linearGradient>
    <filter id="g" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="2.5"/></filter>
  </defs>
  <rect x="0" y="5.5" width="{W}" height="1" fill="url(#base)"/>
  <rect x="-200" y="4.5" width="200" height="3" rx="1.5" fill="url(#spark)" filter="url(#g)">
    <animate attributeName="x" values="-200;{W}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/>
  </rect>
  <rect x="-200" y="5.5" width="200" height="1" fill="url(#spark)">
    <animate attributeName="x" values="-200;{W}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/>
  </rect>
</svg>'''


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1200, 150
    cmd, t = typed("echo $STATUS", 0.4, 0.07)
    t_out = t + 0.35
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="open to swe / ml internships — reach out">
  <defs>
    <linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="870" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{BLUE_MID}"/><stop offset="0.5" stop-color="{BLUE}"/><stop offset="1" stop-color="{INDIGO_MID}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1080 0" dur="9s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: {MONO}; }}
    .p {{ fill: {BLUE_MID}; font-weight: 700; }}
    .m {{ fill: {MUTED}; }}
  </style>
  <text x="{W / 2}" y="48" text-anchor="middle" font-size="20"><tspan class="p">❯ </tspan><tspan class="m">{cmd}</tspan></text>
  <g opacity="0">{fade_in(t_out)}
    <text x="{W / 2}" y="98" text-anchor="middle" font-size="34" font-weight="800" fill="url(#shimmer)">open to swe / ml internships<tspan fill="{INDIGO_MID}"> ▋{blink(t_out + 0.6)}</tspan></text>
    <text x="{W / 2}" y="134" text-anchor="middle" font-size="16" class="m">let's build something · reach out ↗</text>
  </g>
</svg>'''


if __name__ == "__main__":
    h, t = header()
    open(f"{OUT}/header.svg", "w").write(h)
    open(f"{OUT}/divider.svg", "w").write(divider())
    open(f"{OUT}/footer.svg", "w").write(footer())
    print("header animation settles at", round(t, 2), "s")
