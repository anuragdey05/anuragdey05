"""Render original ASCII cassette loops. Requires Pillow; uses a local mono font.

Run from any directory: python3 tools/render_ascii_tapes.py
Pass --font /path/to/font.ttf on systems without Menlo or DejaVu Sans Mono.
"""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PALETTE = {'bg': '#121612', 'ink': '#e4ddc9', 'muted': '#8c947f',
           'accent': '#e39665', 'line': '#68745c'}
COLS, CELL, LINE, MARGIN = 68, 11, 23, 24
SIZE = (COLS * CELL + MARGIN * 2, 520)


def render_frame(font, side, frame):
    image = Image.new('RGB', SIZE, PALETTE['bg'])
    draw = ImageDraw.Draw(image)
    def text(x, y, value, color='ink'):
        draw.text((MARGIN+x*CELL, MARGIN+y*LINE), value, font=font, fill=PALETTE[color])
    def row(y, value='', color='ink'):
        text(0, y, '|', 'line')
        text(2, y, value[:64], color)
        text(67, y, '|', 'line')

    tracks = {
        'a': [('A1', 'ISHARA STUDIO', 'a studio website, made to be explored.'),
              ('A2', "AIRN'T", 'making invisible air visible.')],
        'b': [('B1', 'AUEC VOTING PORTAL', 'ballots, receipts, and the logic between.'),
              ('B2', 'SPAN MARGIN CALCULATOR', 'sixteen scenarios. one portfolio.'),
              ('B3', 'ARTEMIS IMAGE CAPTIONING', 'from painted images to generated language.')]
    }[side]
    track_index = frame // 24
    code, title, subtitle = tracks[track_index]
    label = 'CREATIVE / INTERFACES & EXPERIENCES' if side == 'a' else 'TECHNICAL / SYSTEMS & MODELS'
    text(0, 0, 'ANURAG DEY', 'ink')
    text(47, 0, 'SELECTED RECORDINGS', 'muted')
    text(0, 1, '.' + '-'*66 + '.', 'line')
    row(2, 'SIDE '+side.upper()+'   /   '+label, 'accent')
    row(3, '-'*64, 'line')
    row(4)
    row(5, code+'   '+title, 'ink')
    row(6, subtitle, 'muted')
    row(7)
    row(8, ' .-------------------.            .-------------------.', 'line')
    row(9, ' |                   |============|                   |', 'line')
    row(10,' |                   |            |                   |', 'line')
    row(11,' |                   |============|                   |', 'line')
    row(12," '-------------------'            '-------------------'", 'line')
    row(13)
    row(14,'  [ ORIGINAL MATERIAL ]                 [ SIDE '+side.upper()+' ]', 'muted')
    row(15)
    row(16,'            /--------------------------------\\', 'line')
    row(17,'           /___o________________________o______\\', 'line')
    text(0,18,"'"+'-'*66+"'",'line')
    text(0,19,'PICK A SIDE. FOLLOW THE WORK.', 'accent')
    text(47,19,f'TRACK {track_index+1:02d} / {len(tracks):02d}', 'muted')

    # Each reel is an ASCII raster of a rotating six-spoke tape hub.
    for cx, direction in [(13,1),(47,1)]:
        for yy in range(-2,3):
            for xx in range(-7,8):
                x, y = xx/1.7, yy
                radius = math.hypot(x,y)
                if radius > 2.5:
                    continue
                angle = math.atan2(y,x) - direction*frame*math.pi/9
                glyph = ' '
                if radius > 1.95:
                    glyph = '.' if yy<0 else ':'
                elif radius < .55:
                    glyph = 'O'
                elif abs(math.sin(angle*3))<.47:
                    glyph = '#'
                if glyph!=' ':
                    text(cx+xx, 10+yy*.49, glyph, 'accent')
    # A small moving tape signal connects both hubs; it is visual motion only.
    for i in range(10):
        text(25+i,10, '~' if (i+frame)%4<2 else '-', 'muted')
    return image.convert('P', palette=Image.Palette.ADAPTIVE, colors=16)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font')
    args=parser.parse_args()
    candidates=[args.font, '/System/Library/Fonts/Menlo.ttc',
                '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
    font_path=next((p for p in candidates if p and Path(p).is_file()),None)
    if not font_path:
        raise SystemExit('Pass --font with a monospace TrueType font path.')
    font=ImageFont.truetype(font_path,18)
    out=ROOT/'assets'
    out.mkdir(exist_ok=True)
    for side,count in [('a',2),('b',3)]:
        frames=[render_frame(font,side,n) for n in range(count*24)]
        path=out/f'side-{side}.gif'
        frames[0].save(path,save_all=True,append_images=frames[1:],duration=100,
                       loop=0,optimize=True,disposal=2)
        frames[0].convert('RGB').save(out/f'side-{side}-still.png')
        print(f'{path.name}: {len(frames)} frames, {path.stat().st_size:,} bytes')


if __name__=='__main__':
    main()
