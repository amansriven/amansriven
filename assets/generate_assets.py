"""Generates the SVG assets for the profile README."""
from base64 import b64encode
from html import escape
import os

# near-black neutrals + a single red accent. every asset is its own black card, so one
# version reads the same on github's light and dark page backgrounds
BG, BAR, LINE = "#0A0A0A", "#111111", "#262626"
TEXT, BODY, MUTED, DIM = "#FAFAFA", "#D4D4D4", "#A3A3A3", "#525252"
RED = "#EF4444"
OUT = os.path.dirname(os.path.abspath(__file__))  # writes next to this script

# jetbrains mono, subset to ascii + the few symbols used here (fonts/), embedded in every svg
# so it renders the same for everyone instead of falling back to whatever mono they have
MONO = "'JBM','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FONT_CSS = "".join(
    f"@font-face{{font-family:'JBM';font-weight:{weight};"
    f"src:url(data:font/woff2;base64,{b64encode(open(f'{OUT}/fonts/jetbrains-mono-{name}.woff2', 'rb').read()).decode()}) format('woff2');}}"
    for name, weight in [("regular", 400), ("bold", 700)])
CHAR = 0.6  # glyph advance in em; jetbrains mono is strictly monospaced


def style(css=""):
    return f"<style>{FONT_CSS} text {{ font-family: {MONO}; }} {css}</style>"


def typed(text, start, step):
    """Each character is a tspan that becomes visible at its own time -> typing effect."""
    parts = []
    for i, ch in enumerate(text):
        parts.append(f'<tspan visibility="hidden">{escape(ch)}'
                     f'<set attributeName="visibility" to="visible" begin="{start + i * step:.2f}s" fill="freeze"/></tspan>')
    return "".join(parts), start + len(text) * step


def show_at(t):
    return f'<set attributeName="visibility" to="visible" begin="{t:.2f}s" fill="freeze"/>'


def fade_in(t, dur=0.5):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{dur}s" fill="freeze"/>'


def blink(begin):
    return (f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="1.05s" begin="{begin:.2f}s" repeatCount="indefinite"/>')


def card(W, H):
    return f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>'


def prompt(cmd, x=48, y=56):
    """The `$ cmd` line that heads each card, standing in for a markdown heading."""
    return f'<text x="{x}" y="{y}" font-size="20"><tspan fill="{RED}" font-weight="700">$ </tspan><tspan fill="{MUTED}">{escape(cmd)}</tspan></text>'


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 340
    x0 = 48

    l1, t = typed("whoami", 0.5, 0.08)
    name, t = typed("aman sriven", t + 0.35, 0.09)
    t_dot = t + 0.15  # the red full stop lands a beat after the name
    t_tag = t_dot + 0.35
    t_final = t_tag + 0.5

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="$ whoami — aman sriven, software engineer, cs @ texas a&amp;m '28">
  {style(f"""
    .p    {{ fill: {RED}; font-size: 20px; font-weight: 700; }}
    .c    {{ fill: {TEXT}; font-size: 20px; }}
    .d    {{ fill: {MUTED}; font-size: 22px; }}
    .r    {{ fill: {RED}; }}
    .lbl  {{ fill: {DIM}; font-size: 13px; letter-spacing: 0.5px; }}
    .name {{ fill: {TEXT}; font-size: 68px; font-weight: 700; letter-spacing: -2px; }}""")}

  {card(W, H)}
  <path d="M0.5,12.5 A12,12 0 0 1 12.5,0.5 H{W - 12.5} A12,12 0 0 1 {W - 0.5},12.5 V44 H0.5 Z" fill="{BAR}"/>
  <line x1="0.5" y1="44" x2="{W - 0.5}" y2="44" stroke="{LINE}"/>
  <circle cx="26" cy="22" r="5.5" fill="{LINE}"/><circle cx="46" cy="22" r="5.5" fill="{LINE}"/><circle cx="66" cy="22" r="5.5" fill="{LINE}"/>
  <text x="{W / 2}" y="27" text-anchor="middle" class="lbl">aman@tamu: ~</text>

  <!-- status pill -->
  <rect x="{W - 192}" y="11" width="176" height="22" rx="11" fill="{BG}" stroke="{LINE}"/>
  <circle cx="{W - 176}" cy="22" r="3.5" fill="{RED}">
    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
  </circle>
  <text x="{W - 165}" y="26.5" class="lbl" style="font-size:12px; fill:{MUTED}">open to internships</text>

  <!-- terminal -->
  <text x="{x0}" y="102"><tspan class="p">$ </tspan><tspan class="c">{l1}</tspan></text>

  <text x="{x0 - 3}" y="182" class="name">{name}<tspan class="r" visibility="hidden">.{show_at(t_dot)}</tspan></text>
  <g opacity="0">{fade_in(t_tag)}
    <text x="{x0}" y="228" class="d">software engineer · texas a&amp;m '28</text>
  </g>

  <text x="{x0}" y="296" visibility="hidden">{show_at(t_final)}<tspan class="p">$ </tspan><tspan class="r" style="font-size:20px">▋{blink(t_final)}</tspan></text>
</svg>'''
    return svg, t_final


# ---------------------------------------------------------------- text panels
def panel(cmd, rows, label, size=19, lh=33):
    """A card headed by `$ cmd`, then rows of (column, text, color) segments.
    Columns are character cells, so everything lines up like real terminal output."""
    W, x0, adv = 1200, 48, size * CHAR
    y, body = 112, []
    for row in rows:
        for col, text, color in row:
            body.append(f'<text x="{x0 + col * adv:.1f}" y="{y}" xml:space="preserve" font-size="{size}" fill="{color}">{escape(text)}</text>')
        y += lh
    H = y - lh + 52
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">
  {style()}
  {card(W, H)}
  {prompt(cmd)}
  {"".join(body)}
</svg>'''


def whoami():
    rows = [
        ("focus", "backend & distributed systems"),
        ("also", "applied ai / ml"),
        ("building", "roleward, delta code"),
        ("prev", "humana, jaggaer, tamu cares lab"),
    ]
    return panel("whoami --verbose", [[(0, k, MUTED), (11, v, TEXT)] for k, v in rows],
                 "whoami — " + "; ".join(f"{k}: {v}" for k, v in rows))


def thinking():
    items = ["retry storms and provider failover", "lease-based coordination under failure",
             "agents that explain findings, not decide facts"]
    rows = [[(0, "+", MUTED), (2, s, TEXT)] for s in items] + [[(0, "-", DIM), (2, "yaml", DIM)]]
    return panel("git diff ~/currently-thinking-about", rows, "currently thinking about: " + "; ".join(items) + ". less yaml.")


# ---------------------------------------------------------------- footer
def footer():
    W, H = 800, 84
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="open to swe and ai / ml internships — reach out">
  {style()}
  {card(W, H)}
  <text x="{W / 2}" y="50" text-anchor="middle" font-size="22" fill="{TEXT}">open to swe + ai / ml internships <tspan fill="{MUTED}">→ reach out</tspan><tspan fill="{RED}"> ▋{blink(0)}</tspan></text>
</svg>'''


def button(label, glyph):
    """Link pill for the header row; each link needs its own <img>."""
    lx = 20 + len(glyph) * 9 + 12  # label starts after the glyph, so "in" gets as much room as "@"
    w = round(lx + len(label) * 9 + 22)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 44" width="{w}" height="44" role="img" aria-label="{escape(label)}">
  {style()}
  <rect x="0.5" y="0.5" width="{w - 1}" height="43" rx="10" fill="{BG}" stroke="{LINE}"/>
  <text x="20" y="27.5" font-size="15" font-weight="700" fill="{RED}">{escape(glyph)}</text>
  <text x="{lx}" y="27.5" font-size="15" fill="{TEXT}">{escape(label)}</text>
</svg>'''


if __name__ == "__main__":
    h, t = header()
    open(f"{OUT}/header.svg", "w").write(h)
    open(f"{OUT}/whoami.svg", "w").write(whoami())
    open(f"{OUT}/thinking.svg", "w").write(thinking())
    open(f"{OUT}/footer.svg", "w").write(footer())
    for name, label, glyph in [("site", "amansriven.com", "↗"), ("linkedin", "linkedin", "in"), ("email", "email", "@")]:
        open(f"{OUT}/btn-{name}.svg", "w").write(button(label, glyph))
    print("header animation settles at", round(t, 2), "s")
