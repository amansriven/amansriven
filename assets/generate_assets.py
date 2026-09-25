"""Generates the animated SVG assets for the profile README."""
from html import escape
import os

MONO = "'JetBrains Mono','Fira Code','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
# calm palette: github dark neutrals + one muted blue accent
BG, BAR, LINE = "#0D1117", "#161B22", "#30363D"
TEXT, BODY, MUTED, DIM = "#E6EDF3", "#C9D1D9", "#8B949E", "#6E7681"
ACCENT = "#7AA2F7"
ACCENT_MID = "#5B8DEF"  # footer sits on the page background, so it must read on light and dark
OUT = os.path.dirname(os.path.abspath(__file__))  # writes next to this script
os.makedirs(OUT, exist_ok=True)


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


def show_at(t):
    return f'<set attributeName="visibility" to="visible" begin="{t:.2f}s" fill="freeze"/>'


def fade_in(t, dur=0.6, dy=8):
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" '
            f'begin="{t:.2f}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>')


def blink(begin):
    return (f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="1.05s" begin="{begin:.2f}s" repeatCount="indefinite"/>')


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 500
    x0 = 56

    # line 1: $ whoami
    l1, t = typed("whoami", 0.6, 0.09)
    # line 2: name
    name, t_name_end = typed("aman sriven", t + 0.35, 0.065)
    t_tag = t_name_end + 0.15
    # line 3: $ cat ./focus.md
    t_p2 = t_tag + 0.75
    l3, t = typed("cat ./focus.md", t_p2 + 0.1, 0.05)
    t_f1, t_f2, t_f3 = t + 0.2, t + 0.45, t + 0.7
    t_final = t_f3 + 0.5

    # agent graph (right side)
    cx, cy = 985, 285
    nodes = [("planner", 830, 165), ("retriever", 1130, 165),
             ("tools", 830, 420), ("evals", 1130, 420), ("llm", 985, 135)]
    durs = [2.6, 3.1, 3.7, 2.9, 2.3]

    edges, packets, node_svg = [], [], []
    for (label, nx, ny), d in zip(nodes, durs):
        edges.append(f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="url(#edge)" stroke-width="1.2" '
                     f'stroke-dasharray="4 6"><animate attributeName="stroke-dashoffset" from="0" to="-40" '
                     f'dur="2s" repeatCount="indefinite"/></line>')
        packets.append(f'<circle r="2.6" fill="{ACCENT}" opacity="0.8">'
                       f'<animateMotion dur="{d}s" repeatCount="indefinite" '
                       f'path="M{cx},{cy} L{nx},{ny} L{cx},{cy}" keyPoints="0;0.5;1" keyTimes="0;0.5;1" '
                       f'calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1"/></circle>')
        ly = ny - 20 if ny < cy else ny + 30
        node_svg.append(
            f'<circle cx="{nx}" cy="{ny}" r="6" fill="none" stroke="{MUTED}" stroke-width="1" opacity="0.4">'
            f'<animate attributeName="r" values="6;16" dur="{d * 1.6:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.4;0" dur="{d * 1.6:.1f}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{nx}" cy="{ny}" r="6" fill="{BG}" stroke="{MUTED}" stroke-width="1.5"/>'
            f'<circle cx="{nx}" cy="{ny}" r="2" fill="{BODY}"/>'
            f'<text x="{nx}" y="{ly}" text-anchor="middle" class="lbl">{label}</text>')

    graph = f'''
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.9s" dur="1.2s" fill="freeze"/>
    <circle cx="{cx}" cy="{cy}" r="118" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 8">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/>
    </circle>
    {''.join(edges)}
    {''.join(packets)}
    {''.join(node_svg)}
    <circle cx="{cx}" cy="{cy}" r="15" fill="{BG}" stroke="{ACCENT}" stroke-width="1.5"/>
    <circle cx="{cx}" cy="{cy}" r="4.5" fill="{ACCENT}"/>
    <text x="{cx}" y="{cy + 50}" text-anchor="middle" class="lbl hi">orchestrator</text>
  </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="$ whoami — aman sriven, ai / ml engineer, cs @ texas a&amp;m">
  <defs>
    <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="800" y1="100" x2="1150" y2="420">
      <stop offset="0" stop-color="{MUTED}" stop-opacity="0.45"/><stop offset="1" stop-color="{MUTED}" stop-opacity="0.25"/>
    </linearGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="{MUTED}" opacity="0.1"/>
    </pattern>
    <clipPath id="win"><rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="18"/></clipPath>
  </defs>
  <style>
    text {{ font-family: {MONO}; }}
    .p  {{ fill: {ACCENT}; font-size: 22px; font-weight: 700; }}
    .c  {{ fill: {TEXT}; font-size: 22px; }}
    .d  {{ fill: {MUTED}; font-size: 22px; }}
    .o  {{ fill: {BODY}; font-size: 20px; }}
    .ar {{ fill: {ACCENT}; }}
    .k  {{ fill: {DIM}; }}
    .lbl {{ fill: {MUTED}; font-size: 13px; letter-spacing: 0.5px; }}
    .hi {{ fill: {TEXT}; }}
    .name {{ fill: {TEXT}; font-size: 70px; font-weight: 700; letter-spacing: -1px; }}
  </style>

  <!-- window -->
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="18" fill="{BG}"/>
  <g clip-path="url(#win)">
    <rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="url(#dots)"/>
    <!-- title bar -->
    <rect x="8" y="8" width="{W - 16}" height="44" fill="{BAR}"/>
    <line x1="8" y1="52" x2="{W - 8}" y2="52" stroke="{LINE}"/>
  </g>
  <rect x="8.5" y="8.5" width="{W - 17}" height="{H - 17}" rx="17.5" fill="none" stroke="{LINE}" stroke-width="1"/>
  <circle cx="38" cy="30" r="6" fill="{LINE}"/><circle cx="60" cy="30" r="6" fill="{LINE}"/><circle cx="82" cy="30" r="6" fill="{LINE}"/>
  <text x="{W / 2}" y="35" text-anchor="middle" class="lbl">aman@tamu: ~ — zsh</text>

  <!-- terminal -->
  <text x="{x0}" y="112"><tspan class="p">❯ </tspan><tspan class="c">{l1}</tspan></text>

  <text x="{x0 - 4}" y="196" class="name">{name}</text>

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

  <!-- live status pill -->
  <g opacity="0">{fade_in(t_final, 0.5, 0)}
    <rect x="{W - 212}" y="19" width="182" height="23" rx="11.5" fill="{BG}" stroke="{LINE}"/>
    <circle cx="{W - 195}" cy="30.5" r="3.5" fill="{ACCENT}">
      <animate attributeName="opacity" values="1;0.4;1" dur="2.4s" repeatCount="indefinite"/>
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
      <stop offset="0" stop-color="{MUTED}" stop-opacity="0"/><stop offset="0.15" stop-color="{MUTED}" stop-opacity="0.35"/>
      <stop offset="0.85" stop-color="{MUTED}" stop-opacity="0.35"/><stop offset="1" stop-color="{MUTED}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="spark" x1="0" x2="1">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="0.5" stop-color="{ACCENT}" stop-opacity="0.6"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="5.5" width="{W}" height="1" fill="url(#base)"/>
  <rect x="-200" y="5.5" width="200" height="1" fill="url(#spark)">
    <animate attributeName="x" values="-200;{W}" dur="9s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/>
  </rect>
</svg>'''


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1200, 150
    cmd, t = typed("echo $STATUS", 0.4, 0.07)
    t_out = t + 0.35
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="open to swe / ml internships — reach out">
  <style>
    text {{ font-family: {MONO}; }}
    .p {{ fill: {ACCENT}; font-weight: 700; }}
    .m {{ fill: {MUTED}; }}
  </style>
  <text x="{W / 2}" y="48" text-anchor="middle" font-size="20"><tspan class="p">❯ </tspan><tspan class="m">{cmd}</tspan></text>
  <g opacity="0">{fade_in(t_out)}
    <text x="{W / 2}" y="98" text-anchor="middle" font-size="34" font-weight="700" fill="{ACCENT_MID}">open to swe / ml internships<tspan fill="{ACCENT_MID}"> ▋{blink(t_out + 0.6)}</tspan></text>
    <text x="{W / 2}" y="134" text-anchor="middle" font-size="16" class="m">let's build something · reach out ↗</text>
  </g>
</svg>'''


if __name__ == "__main__":
    h, t = header()
    open(f"{OUT}/header.svg", "w").write(h)
    open(f"{OUT}/divider.svg", "w").write(divider())
    open(f"{OUT}/footer.svg", "w").write(footer())
    print("header animation settles at", round(t, 2), "s")
