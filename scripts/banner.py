"""Builds assets/banner-light.svg and assets/banner-dark.svg for the profile README.

The penguin is the real Pengopal mark (colours untouched); its wake is made of code from the
projects, flowing away from it, the "Code Current" idea from pengopal.com. A typed line cycles
through what I build. Both animations are CSS, so `prefers-reduced-motion` stops them and the
banner settles on the first line.

Usage: python scripts/banner.py <path to pengopal mark.svg>
"""
import re
import sys
from html import escape
from pathlib import Path

W, H = 1200, 420
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "light": {
        "bg0": "#ffffff", "bg1": "#f5f6fa", "dot": "#12224a14",
        "ink": "#12224a", "muted": "#4a5a85", "eyebrow": "#2a3d78",
        "border": "#12224a1f",
        # The site's deep opal (each one at least 3:1 on white).
        "opal": ["#1789ad", "#5f6bff", "#a35cff", "#d14a87"],
        "prompt": "#5f6bff",
    },
    "dark": {
        "bg0": "#0e1a3a", "bg1": "#13224a", "dot": "#eef2ff12",
        "ink": "#eef2ff", "muted": "#b9c4e8", "eyebrow": "#9fb0e6",
        "border": "#eef2ff1f",
        # The site's light opal, sampled from the logo.
        "opal": ["#6fe0f2", "#8fa8ff", "#d3a6ff", "#ffb6d3", "#ffe2a6", "#8df0cf"],
        "prompt": "#8fa8ff",
    },
}

PHRASES = [
    "multi-tenant SaaS, isolated by design",
    "identity & access on Keycloak and OPA",
    "AI features in real products",
    "web apps, built end to end",
]

# Code from the projects' own stacks: Postgres RLS, OPA, Keycloak, the monorepo.
CODE = [
    "SET app.tenant_id = $1; -- row-level security",
    'allow if { input.user.role == "admin" }',
    "const realm = await kc.realms.create(template);",
    "iss === `${authUrl}/realms/${tenant}`",
    "pnpm turbo run lint typecheck test build",
    "<Workspace brand={tenant.brand} />",
    "decision := opa.eval(policy, input)",
]

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'Cascadia Code', Menlo, Consolas, monospace"

CYCLE = 20.0  # seconds for all four phrases
SLOT = CYCLE / len(PHRASES)
TYPE, ERASE = 0.06, 0.025


def pct(t):
    return f"{t / CYCLE * 100:.3f}%"


def typing(theme):
    css, groups = [], []
    for k, phrase in enumerate(PHRASES):
        n = len(phrase)
        spans = []
        for i, ch in enumerate(phrase):
            on = k * SLOT + 0.3 + TYPE * i
            off = k * SLOT + SLOT - 1.0 + ERASE * (n - 1 - i)
            name = f"p{k}c{i}"
            css.append(
                f"@keyframes {name}{{0%,{pct(on - 0.001)}{{opacity:0}}{pct(on)},{pct(off)}{{opacity:1}}"
                f"{pct(off + 0.001)},100%{{opacity:0}}}}"
                f".{name}{{animation:{name} {CYCLE}s linear infinite both}}"
            )
            text = " " if ch == " " else escape(ch)
            # Without motion, only the first line shows, fully typed; the animation overrides this.
            base = 1 if k == 0 else 0
            spans.append(f'<tspan class="{name}" style="opacity:{base}">{text}</tspan>')
        groups.append(f'<text x="98" y="300" class="type">{"".join(spans)}</text>')
    return "".join(css), "".join(groups)


def stream(theme):
    rows, css = [], []
    for r, code in enumerate(CODE):
        colour = theme["opal"][r % len(theme["opal"])]
        speed = 26 + (r * 7) % 15
        y = 118 + r * 34
        copy = escape(code) + "  "
        css.append(f".s{r}{{animation:flow {speed}s linear infinite;animation-delay:-{r * 3}s}}")
        rows.append(
            f'<text class="code s{r}" x="640" y="{y}" fill="{colour}">{copy}{copy}</text>'
        )
    return "".join(css), "".join(rows)


def mark(svg_text, dark):
    vb = re.search(r'viewBox="([^"]+)"', svg_text).group(1)
    inner = svg_text[svg_text.index(">") + 1: svg_text.rindex("</svg>")]
    inner = re.sub(r'id="([^"]+)"', r'id="m-\1"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", r"url(#m-\1)", inner)
    inner = re.sub(r'href="#([^"]+)"', r'href="#m-\1"', inner)
    # Dark mode: a light ring around the navy body, as the site's dark logo does.
    group = f'<g filter="url(#ring)">{inner}</g>' if dark else inner
    return f'<svg x="880" y="70" width="290" height="290" viewBox="{vb}">{group}</svg>'


def build(name, theme, mark_svg):
    type_css, type_svg = typing(theme)
    flow_css, flow_svg = stream(theme)
    dark = name == "dark"
    style = (
        f".type{{font:500 25px {MONO};fill:{theme['ink']}}}"
        f".code{{font:500 15px {MONO};opacity:.9;transform-box:fill-box}}"
        "@keyframes flow{from{transform:translateX(0)}to{transform:translateX(-50%)}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.15}}"
        ".prompt{animation:blink 1.1s steps(1) infinite}"
        f"{flow_css}{type_css}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    )
    ring = (
        '<filter id="ring" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
        '<feMorphology in="SourceAlpha" operator="dilate" radius="22" result="grown"/>'
        '<feFlood flood-color="#C9D3F5"/><feComposite in2="grown" operator="in" result="ring"/>'
        '<feMerge><feMergeNode in="ring"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        if dark else ""
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Muhammad Furqan, founder of Pengopal Technologies</title>
<desc id="d">Software and AI, built end to end. The Pengopal penguin swims ahead of a wake of flowing code.</desc>
<style>{style}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{theme['bg0']}"/><stop offset="1" stop-color="{theme['bg1']}"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="{theme['dot']}"/></pattern>
<linearGradient id="fade" x1="680" y1="0" x2="900" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".6" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
<mask id="wake"><rect x="680" y="80" width="300" height="260" fill="url(#fade)"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
{ring}
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<g mask="url(#wake)">{flow_svg}</g>
{mark(mark_svg, dark)}
<text x="64" y="104" style="font:700 15px {SANS};letter-spacing:4px" fill="{theme['eyebrow']}">FOUNDER · PENGOPAL TECHNOLOGIES</text>
<text x="60" y="186" style="font:700 68px {SANS};letter-spacing:-1.5px" fill="{theme['ink']}">Muhammad Furqan</text>
<text x="64" y="234" style="font:400 25px {SANS}" fill="{theme['muted']}">Software and AI, built end to end.</text>
<text x="64" y="300" class="prompt" style="font:700 25px {MONO}" fill="{theme['prompt']}">❯</text>
{type_svg}
<text x="64" y="364" style="font:500 16px {MONO}" fill="{theme['muted']}">pengopal.com</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{theme['border']}"/>
</svg>
"""


def main():
    mark_svg = Path(sys.argv[1]).read_text(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        path = OUT / f"banner-{name}.svg"
        path.write_text(build(name, theme, mark_svg), encoding="utf-8")
        print(path.name, path.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
