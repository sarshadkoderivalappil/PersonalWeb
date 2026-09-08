#!/usr/bin/env python3
"""
Generates phage-line.svg — a hand-drawn, one-line animation of the host/phage arms race.

Style: loose ink, angular phage heads, oversized googly eyes, monochrome on white.
No shape is a true circle: outlines are curves pushed through jittered points, and
heads are straight-edged polygons with random vertices. Seeds are fixed, so re-running
redraws the same picture. Change a seed to redraw a character differently.

    python3 build_phage_line.py
"""
import math, random

W, H   = 1100, 112       # scene period (units), strip height
VIEW_W = 600             # visible window
GROUND = 94              # the line everyone stands on
INK, GHOST, RULE = "#111111", "#d7d7d7", "#e8e8e8"

# ----------------------------------------------------------------- ink helpers

def _cm(pts, closed=True):
    """Catmull-Rom through points -> bezier path. Organic outlines."""
    n = len(pts)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in (range(n) if closed else range(n - 1)):
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1, p2 = pts[i % n], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + ("Z" if closed else "")

def blob(rx, ry, seed, wob=0.11, n=13):
    r = random.Random(seed)
    return _cm([(rx * (1 + r.uniform(-wob, wob)) * math.cos(2*math.pi*i/n),
                 ry * (1 + r.uniform(-wob, wob)) * math.sin(2*math.pi*i/n)) for i in range(n)])

def poly(r_, seed, n=6, jag=0.16, squash=0.92):
    """Straight-edged head. Angular is what makes it read as a phage capsid."""
    rr = random.Random(seed)
    pts = []
    for i in range(n):
        t = 2*math.pi*i/n + rr.uniform(-.22, .22)
        rad = r_ * rr.uniform(1 - jag, 1 + jag)
        pts.append(f"{rad*math.cos(t):.1f},{rad*math.sin(t)*squash:.1f}")
    return "M" + " L".join(pts) + " Z"

def eye(x, y, r_, look=(0, 0), seed=1):
    return (f'<g transform="translate({x},{y})">'
            f'<path class="fill" d="{blob(r_, r_*1.04, seed, .08, 11)}"/>'
            f'<path class="pupil" d="{blob(r_*.52, r_*.56, seed+7, .12, 9)}" '
            f'transform="translate({look[0]*r_*.34:.1f},{look[1]*r_*.34:.1f})"/></g>')

def spiral_eye(x, y, r_, seed=1):
    rr = random.Random(seed)
    pts = []
    for i in range(49):
        t = 2.9 * 2*math.pi * i/48
        rad = r_ * .92 * (i/48) * rr.uniform(.93, 1.07)
        pts.append(f"{rad*math.cos(t):.1f},{rad*math.sin(t):.1f}")
    return (f'<g transform="translate({x},{y})">'
            f'<path class="fill" d="{blob(r_, r_*1.04, seed, .08, 11)}"/>'
            f'<polyline class="hair" points="{" ".join(pts)}"/></g>')

def coil(y0, y1, turns=4, amp=6):
    """A real spring: semicircular arcs alternating side to side."""
    seg, d, sweep = (y1 - y0)/turns, f"M0,{y0}", 1
    for i in range(turns):
        d += f" A{amp:.1f},{seg/2:.1f} 0 1 {sweep} 0,{y0 + seg*(i+1):.1f}"
        sweep = 1 - sweep
    return d

def legs(spread=11, drop=16, seed=3, n=3, hooked=False):
    """Baseplate bar plus splayed, kinked tail fibres."""
    r = random.Random(seed)
    out = [f'<path class="ink" d="M{-spread*.5:.1f},0 L{spread*.5:.1f},0"/>']
    for i in range(n):
        u  = -1 + 2*i/(n-1)
        x0 = u*spread*.5
        kx, ky = x0 + u*spread*.4 + r.uniform(-1, 1), drop*.55
        ex, ey = x0 + u*spread*1.0 + r.uniform(-1.5, 1.5), drop*r.uniform(.9, 1.05)
        d = f"M{x0:.1f},0 L{kx:.1f},{ky:.1f} L{ex:.1f},{ey:.1f}"
        if hooked:                                   # gripping fibres: the counter-adaptation
            d += f" q{u*3.5:.1f},3.5 {u*6:.1f},0.5"
        out.append(f'<path class="ink" d="{d}"/>')
    return "".join(out)

def squiggles(n, seed, side=-1, y=0):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        px, py = side*r.uniform(26, 32), y + r.uniform(-7, 7)
        d = f"M{px:.1f},{py:.1f}"
        for _ in range(3):
            nx, ny = px + side*r.uniform(9, 16), py + r.uniform(-12, 12)
            d += f" Q{px + side*r.uniform(3,10):.1f},{py + r.uniform(-13,13):.1f} {nx:.1f},{ny:.1f}"
            px, py = nx, ny
        out.append(f'<path class="hair" d="{d}"/>')
    return "".join(out)

def streaks(x, y, n=3, seed=5, length=24, side=-1):
    r = random.Random(seed)
    return "".join(
        f'<path class="streak" d="M{x + r.uniform(-4,4):.1f},{y + (i - n/2)*9 + r.uniform(-2,2):.1f} '
        f'q{side*length*.5:.1f},{r.uniform(-4,4):.1f} {side*length:.1f},{r.uniform(-3,3):.1f}"/>'
        for i in range(n))

# ----------------------------------------------------------------- characters

BODY_RX, BODY_RY = 34, 15        # bacterium

def host(seed=20, mood="ok", look=(0,0), tilt=-4, flag=2, bumpy=False, squash=1.0):
    """Bacterium sitting ON the ground line. Face at the right end, flagella trailing left,
    so it reads as something going somewhere rather than a pebble."""
    ry_ = BODY_RY*squash
    g = [squiggles(flag, seed+3, -1, 2), f'<path class="fill" d="{blob(BODY_RX, ry_, seed, .12, 15)}"/>']

    if bumpy:                       # switched receptor: knobs bulging off the free rim
        rr = random.Random(seed+40)
        for i in range(5):
            a = math.radians(-178 + i*14)
            px, py = BODY_RX*math.cos(a), ry_*math.sin(a)
            nx, ny = math.cos(a)/BODY_RX, math.sin(a)/ry_          # outward normal
            L = math.hypot(nx, ny); nx, ny = nx/L, ny/L
            tx, ty = -ny, nx                                       # tangent
            k = rr.uniform(3.8, 5.0)
            g.append(f'<path class="knob" d="M{px-tx*k:.1f},{py-ty*k:.1f} '
                     f'Q{px+nx*k*2.2:.1f},{py+ny*k*2.2:.1f} {px+tx*k:.1f},{py+ty*k:.1f}"/>')

    if mood == "dead":
        g += [spiral_eye(6, -7, 7.2, seed+1), spiral_eye(19, -9, 6.8, seed+4),
              f'<path class="hair" d="M{BODY_RX*.95:.1f},1 q7,5 12,1"/>']      # lolling tongue
    elif mood == "alarmed":
        g += [eye(6, -11, 8.6, look, seed+1), eye(20, -12, 8.0, look, seed+4)]
    else:
        g += [eye(7, -8, 7.4, look, seed+1), eye(19, -9, 7.0, look, seed+4)]

    return f'<g transform="translate(0,{-ry_ - 4:.1f}) rotate({tilt})">{"".join(g)}</g>'

HEAD_R = 17

def phage(seed=1, evolved=False, eyes="wide", look=(0,0)):
    """Head at local origin; coil tail and crown of fibres hang below."""
    g = [f'<path class="fill" d="{poly(HEAD_R, seed, 9, .34) if evolved else poly(HEAD_R, seed, 6, .17)}"/>']
    if eyes == "spiral":
        g += [spiral_eye(-8, -2, 7.4, seed+2), spiral_eye(8, -3, 7.0, seed+5)]
    else:
        g += [eye(-8, -2, 7.6, look, seed+2), eye(8.5, -3, 7.2, look, seed+5)]
    g += [f'<path class="ink" d="{coil(HEAD_R*.85, HEAD_R*.85+19, 4, 5.5)}"/>',
          f'<g transform="translate(0,{HEAD_R*.85+19:.1f})">'
          f'{legs(11, 16, seed+9, 3, hooked=evolved)}</g>']
    return "".join(g)

def mini_phage(seed):
    return (f'<path class="fill" d="{poly(10, seed, 6, .22)}"/>'
            f'<path class="pupil" d="{blob(2.4, 2.4, seed+3, .18, 8)}" transform="translate(-2,-1)"/>'
            f'<path class="pupil" d="{blob(2.4, 2.4, seed+9, .18, 8)}" transform="translate(3,-1.5)"/>'
            f'<path class="hair" d="{coil(7, 15, 3, 2.8)}"/>')

# ----------------------------------------------------------------- the beats

PHAGE_ON_HOST = -(BODY_RY*2 + HEAD_R*.85 + 19 + 9)     # head height so fibres rest on the host
LAND_X = -9                                            # on its back, clear of the face

def beat(x, body):
    return f'<g transform="translate({x},{GROUND})">{body}</g>'

def scene():
    b = []

    # 1 — a phage comes bounding in. The host hasn't noticed.
    b.append(beat(110,
        host(21, "ok", look=(-1, 0), tilt=-5) +
        streaks(-14, -74, 3, 11, 26, -1) +
        f'<g transform="translate(34,-80) rotate(-14)"><g class="bob">{phage(31, look=(-1, 1))}</g></g>'))

    # 2 — it lands. The host notices.
    b.append(beat(330,
        host(41, "alarmed", look=(0, -1), tilt=-3) +
        f'<g transform="translate({LAND_X},{PHAGE_ON_HOST:.0f}) rotate(4)">{phage(51, look=(0, 1))}</g>'))

    # 3 — lysis
    b.append(beat(550,
        host(61, "dead", tilt=7, squash=.72) +
        '<g class="burst">' +
        "".join(f'<g transform="translate({34*math.cos(math.radians(a)):.0f},'
                f'{-20 + 30*math.sin(math.radians(a)):.0f}) rotate({(a+90)*.5:.0f})">{mini_phage(70+i)}</g>'
                for i, a in enumerate((-28, -72, -112, -156))) +
        '</g>'))

    # 4 — a survivor with a different surface. The next phage bounces off, dazed.
    b.append(beat(770,
        host(81, "ok", look=(1, -1), tilt=-6, flag=3, bumpy=True) +
        '<path class="streak" d="M22,-34 q18,-18 34,-7"/>' +
        f'<g transform="translate(60,-72) rotate(36)">{phage(91, eyes="spiral")}</g>'))

    # 5 — a phage whose fibres grip the new surface
    b.append(beat(990,
        host(101, "alarmed", look=(0, -1), tilt=-3, bumpy=True) +
        f'<g transform="translate({LAND_X},{PHAGE_ON_HOST:.0f}) rotate(-3)">{phage(111, evolved=True, look=(0,1))}</g>'))

    return "".join(b)

SCENE = scene()

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {H}"
     width="100%" role="img"
     aria-label="A hand-drawn animated line: a bacteriophage bounds up to a bacterium, lands on it and bursts it into new phages. A surviving bacterium with a different, bumpy surface shrugs the next phage off, which reels away dizzy. Then a phage whose fibres grip the new surface arrives. The cycle repeats.">
<style>
  .fill   {{ fill:#fff; stroke:{INK}; stroke-width:2.2; stroke-linejoin:round }}
  .ink    {{ fill:none; stroke:{INK}; stroke-width:2.2; stroke-linecap:round; stroke-linejoin:round }}
  .hair   {{ fill:none; stroke:{INK}; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round }}
  .pupil  {{ fill:{INK}; stroke:none }}
  .knob   {{ fill:#fff; stroke:{INK}; stroke-width:2.2; stroke-linecap:round }}
  .streak {{ fill:none; stroke:{GHOST}; stroke-width:2; stroke-linecap:round }}
  .rule   {{ stroke:{RULE}; stroke-width:1 }}

  .track  {{ animation: scroll 56s linear infinite }}
  @keyframes scroll {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-{W}px) }} }}

  /* A CSS transform REPLACES the transform attribute, so anything animated sits in
     its own inner group that carries no transform attribute of its own. */
  .bob    {{ animation: bob 2.6s ease-in-out infinite alternate }}
  @keyframes bob {{ to {{ transform: translate(-6px, 9px) rotate(6deg) }} }}

  .burst  {{ transform-origin: 0 0; animation: burst 4.4s ease-out infinite }}
  @keyframes burst {{
    0%   {{ transform: scale(.3) rotate(-10deg); opacity:0 }}
    18%  {{ opacity:1 }}
    100% {{ transform: scale(1.4) rotate(8deg); opacity:0 }}
  }}

  @media (prefers-reduced-motion: reduce) {{ .track, .bob, .burst {{ animation:none }} }}
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

<rect x="0" y="0" width="70" height="{H}" fill="url(#fadeL)"/>
<rect x="{VIEW_W-70}" y="0" width="70" height="{H}" fill="url(#fadeR)"/>
<line class="rule" x1="0" y1="{GROUND}" x2="{VIEW_W}" y2="{GROUND}"/>
</svg>
'''
open("phage-line.svg","w").write(svg)
print("wrote phage-line.svg")
