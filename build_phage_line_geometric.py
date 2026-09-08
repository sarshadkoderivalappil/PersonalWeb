#!/usr/bin/env python3
"""
Generates phage-line.svg — a one-line animation of the host/phage arms race.

The scene is written once here and emitted twice, side by side, so the strip
scrolls seamlessly. Edit the beats below and re-run:  python3 build_phage_line.py
"""
import math

W, H = 900, 58          # scene period (units) and strip height
VIEW_W = 600            # visible window
BASE_Y = 48             # the line everything sits on
HOST_Y = 36             # host cell centre
R = 11                  # host radius
INK, MUTED, RULE = "#111111", "#6b6b6b", "#e8e8e8"

def receptors(kind):
    """Three surface receptors on the upper arc. 'tick' = naive, 'tee' = switched."""
    out = []
    for deg in (-40, -75, -105, -140):
        a = math.radians(deg)
        bx, by = R * math.cos(a), R * math.sin(a)
        tx, ty = 14.5 * math.cos(a), 14.5 * math.sin(a)
        out.append(f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{tx:.2f}" y2="{ty:.2f}"/>')
        if kind == "tee":                      # crossbar: a different receptor
            px, py = -math.sin(a), math.cos(a)
            out.append(f'<line x1="{tx+2.5*px:.2f}" y1="{ty+2.5*py:.2f}" '
                       f'x2="{tx-2.5*px:.2f}" y2="{ty-2.5*py:.2f}"/>')
    return "".join(out)

def host(kind="tick", lysed=False):
    if lysed:
        return (f'<circle class="lysed" cx="0" cy="0" r="{R}"/>')
    return (f'<circle class="cell" cx="0" cy="0" r="{R}"/>' + receptors(kind))

def phage(evolved=False):
    head = '<polygon class="head" points="0,-5.5 4.5,-2.75 4.5,2.75 0,5.5 -4.5,2.75 -4.5,-2.75"/>'
    tail = '<line class="fibre" x1="0" y1="5.5" x2="0" y2="12"/>'
    if evolved:
        legs = ('<path class="fibre" d="M0,12 L-4,15.5 L-7,14"/>'
                '<path class="fibre" d="M0,12 L4,15.5 L7,14"/>'
                '<circle class="dot" cx="0" cy="0" r="1.6"/>')
    else:
        legs = ('<line class="fibre" x1="0" y1="12" x2="-4" y2="15.5"/>'
                '<line class="fibre" x1="0" y1="12" x2="4" y2="15.5"/>')
    return head + tail + legs

def burst():
    heads = []
    for deg in (-25, -70, -110, -155):
        a = math.radians(deg)
        x, y = 21 * math.cos(a), 21 * math.sin(a)
        heads.append(f'<polygon class="head" transform="translate({x:.2f},{y:.2f})" '
                     f'points="0,-3.5 3,-1.75 3,1.75 0,3.5 -3,1.75 -3,-1.75"/>')
    return f'<g class="burst">{"".join(heads)}</g>'

def beat(x, body):
    return f'<g transform="translate({x},{HOST_Y})">{body}</g>'

def scene():
    b = []
    # 1 — a naive host; a phage drifts in
    b.append(beat(90, host("tick") +
             f'<g transform="translate(26,{8-HOST_Y}) rotate(14)">'
             f'<g class="bob">{phage()}</g></g>'))
    # 2 — it docks
    b.append(beat(270, host("tick") +
             f'<g transform="translate(0,{12-HOST_Y})">{phage()}</g>'))
    # 3 — lysis
    b.append(beat(450, host(lysed=True) + burst()))
    # 4 — a survivor with a switched receptor; the phage bounces off
    b.append(beat(630, host("tee") +
             '<path class="arc" d="M14,-14 Q26,-22 34,-14"/>' +
             f'<g transform="translate(30,{4-HOST_Y}) rotate(32)">{phage()}</g>'))
    # 5 — the phage answers back and docks again
    b.append(beat(810, host("tee") +
             f'<g transform="translate(0,{12-HOST_Y})">{phage(evolved=True)}</g>'))
    return "".join(b)

SCENE = scene()

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {H}"
     width="100%" role="img"
     aria-label="An animated line: a phage infects a host cell and bursts it; a surviving cell carries a different surface receptor that the phage cannot bind; a changed phage binds it anyway. The cycle repeats.">
<style>
  .cell   {{ fill:#fff; stroke:{INK}; stroke-width:1.4 }}
  line, path {{ stroke:{INK}; stroke-width:1.4; fill:none; stroke-linecap:round; stroke-linejoin:round }}
  .head   {{ fill:{INK} }}
  .dot    {{ fill:#fff; stroke:none }}
  .lysed  {{ fill:none; stroke:{MUTED}; stroke-width:1.2; stroke-dasharray:3 4 }}
  .arc    {{ stroke:{MUTED}; stroke-width:1; stroke-dasharray:2 3 }}
  .rule   {{ stroke:{RULE}; stroke-width:1 }}

  .track  {{ animation: scroll 48s linear infinite }}
  @keyframes scroll {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-{W}px) }} }}

  .bob    {{ animation: bob 3.5s ease-in-out infinite alternate }}
  @keyframes bob {{ to {{ transform: translateY(3px) }} }}

  .burst  {{ transform-origin: 0 0; animation: burst 4s ease-out infinite }}
  @keyframes burst {{
    0%   {{ transform: scale(.5);  opacity:0 }}
    20%  {{ opacity:1 }}
    100% {{ transform: scale(1.3); opacity:0 }}
  }}

  /* Stops moving for anyone who asks it to. The story still reads left to right. */
  @media (prefers-reduced-motion: reduce) {{
    .track, .bob, .burst {{ animation: none }}
  }}
</style>

<defs>
  <linearGradient id="fadeL" x1="0" x2="1">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fadeR" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/>
  </linearGradient>
</defs>

<g class="track">
  <g transform="translate(0,0)">{SCENE}</g>
  <g transform="translate({W},0)">{SCENE}</g>
</g>

<rect x="0" y="0" width="80" height="{H}" fill="url(#fadeL)"/>
<rect x="{VIEW_W-80}" y="0" width="80" height="{H}" fill="url(#fadeR)"/>

<line class="rule" x1="0" y1="{BASE_Y}" x2="{VIEW_W}" y2="{BASE_Y}"/>
</svg>
'''

open("phage-line.svg", "w").write(svg)
print("wrote phage-line.svg")
