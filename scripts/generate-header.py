#!/usr/bin/env python3
"""Generate the two script-free SVG variants of the profile animation."""
from pathlib import Path
from math import sin, cos, pi
from html import escape

ROOT = Path(__file__).resolve().parents[1]
LINES = [
    '"For the most part we do not first see, and then define,',
    ' we define first and then see."',
    ' — Walter Lippmann, 1922',
]
LETTERS = [dict(ch=ch, x=76+col*13.2, y=137+row*39, col=col, row=row)
           for row, line in enumerate(LINES) for col, ch in enumerate(line)]
SELECTED = []
for ch in 'ANOMIE':
    SELECTED.append(next(i for i, p in enumerate(LETTERS)
                         if p['ch'].upper() == ch and i not in SELECTED))


def smooth(x):
    x = max(0, min(1, x))
    return x*x*x*(x*(x*6-15)+10)


def mix(a, b, t):
    return a+(b-a)*t


def num(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.') or '0'


def frame(p, i, t):
    out, gather, back = smooth((t-3.7)/3.2), smooth((t-7.1)/2.2), smooth((t-11.3)/3.2)
    amount = out*(1-back)
    u = i/len(LETTERS)
    theta = u*pi*5-(t-3.7)*.42
    z = sin(theta)
    x, y = 450+cos(theta)*(155+u*100), 175+sin(theta)*73+(u-.5)*46
    size, alpha, angle = 18+(z+1)*5, .3+(z+1)*.35, sin(theta)*48
    if i in SELECTED:
        k = SELECTED.index(i)
        x, y = mix(x, 265+k*61, gather), mix(y, 193, gather)
        size, alpha, angle = mix(size, 54, gather), mix(alpha, 1, gather), angle*(1-gather)
    else:
        alpha *= 1-gather
        x, y = mix(x, 450+(x-450)*.15, gather), mix(y, 176+(y-176)*.15, gather)
    x, y = mix(p['x'], x, amount), mix(p['y'], y, amount)
    glitch = smooth((t-2.4)/.4)*(1-smooth((t-3.7)/.35))
    if p['row'] == 0 and 18 <= p['col'] < 22:
        y -= glitch*3
    if p['row'] == 1 and 16 <= p['col'] < 20:
        x += glitch*3
    angle *= amount*pi/180
    scale = mix(22, size, amount)/22
    a, b = cos(angle)*scale, sin(angle)*scale
    transform = ','.join(num(v) for v in (a, b, -b, a, x, y))
    return f'transform:matrix({transform});opacity:{num(mix(1, alpha, amount))}'


# Sample the choreography; CSS interpolates between frames without any script.
TIMES = sorted(set([0, 2.4, 2.8, 3.7, 7.1, 9.3, 11.3, 14.5, 16] +
                   [round(2.4+i*.16, 2) for i in range(77)]))
CSS = ['text{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;font-size:22px}',
       '.glyph{animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}',
       '.upper{opacity:0;font-weight:550;animation:capital 16s linear infinite}',
       '.lower{animation:lowercase 16s linear infinite}',
       '@keyframes capital{0%,46%{opacity:0}52%,71%{opacity:1}79%,100%{opacity:0}}',
       '@keyframes lowercase{0%,46%{opacity:1}52%,71%{opacity:0}79%,100%{opacity:1}}',
       '.surface{animation:surface 16s linear infinite}',
       '@keyframes surface{0%,23%{opacity:1}43%,71%{opacity:.06}91%,100%{opacity:1}}']
NODES = []
for i, p in enumerate(LETTERS):
    # Spaces are laid out already and do not need their own animation.
    if p['ch'] == ' ':
        continue
    CSS.append(f'.g{i}'+'{animation-name:f'+str(i)+'}')
    CSS.append(f'@keyframes f{i}'+'{'+''.join(
        num(t/16*100)+'%{'+frame(p, i, t)+'}' for t in TIMES)+'}')
    content = f'<text xml:space="preserve">{escape(p["ch"])}</text>'
    if i in SELECTED:
        content = (f'<text class="lower">{escape(p["ch"])}</text>'
                   f'<text class="upper">{escape(p["ch"].upper())}</text>')
    NODES.append(f'<g class="glyph g{i}" transform="translate({num(p["x"])} {num(p["y"])})">{content}</g>')
CSS.append('@media(prefers-reduced-motion:reduce){.glyph,.surface,.upper,.lower{animation:none}}')

for name, foreground, muted, surface in [
    ('header.svg', '#e6edf3', '#8b949e', '#161b22'),
    ('header-light.svg', '#1f2328', '#656d76', '#f6f8fa'),
]:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340" viewBox="0 0 900 340" role="img" aria-labelledby="title description">\n'
           '<title id="title">Define first. Then see.</title>\n'
           '<desc id="description">“For the most part we do not first see, and then define, we define first and then see.” — Walter Lippmann, 1922. The letters unfold into ANOMIE and return to the quote.</desc>\n'
           '<style>'+''.join(CSS)+'</style>\n'
           f'<rect class="surface" x="49" y="83" width="802" height="190" rx="6" fill="{surface}"/>\n'
           f'<g fill="{foreground}">'+''.join(NODES)+'</g>\n</svg>\n')
    path = ROOT/'assets'/name
    path.write_text(svg)
    print(f'{path.relative_to(ROOT)}: {len(svg.encode()):,} bytes')
