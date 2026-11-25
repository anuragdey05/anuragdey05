"""Render an original ASCII mixtape GIF and still image with Pillow.

Usage: python3 tools/render_ascii_tapes.py [--font /path/to/mono.ttf]
No source video or generated imagery is used; every frame is drawn from text.
"""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (960, 480)
BG = '#eee8d8'
INK = '#34382f'
LINE = '#666e5b'
FAINT = '#aaa693'
ACCENT = '#a44f36'
STEP_X, STEP_Y = 9, 13
HOLD = 64
FLIP = 10


def label(draw, xy, value, font, fill=INK):
    draw.text(xy, value, font=font, fill=fill)


def shell(font, bold, side):
    im = Image.new('RGB', SIZE, BG)
    d = ImageDraw.Draw(im)
    # A cassette shell, drawn as text, without a terminal-window surround.
    x, y, cols = 75, 40, 90
    def line(row, value, color=LINE):
        label(d, (x, y + row*STEP_Y), value, font, color)
    line(0, ' .'+ '-'*(cols-4)+'.')
    line(1, '/'+ ' '*(cols-2)+'\\')
    for row in range(2,28):
        line(row, '|'+ ' '*(cols-2)+'|')
    line(28, '\\'+ ' '*(cols-2)+'/')
    line(29, " '"+ '-'*(cols-4)+"'")
    for px,py in [(99,72),(855,72),(99,383),(855,383)]:
        label(d,(px,py),'(+)',font,LINE)
    # Label stock and its printed rules.
    for row in [4]:
        line(row,'|     '+ '-'*76+'     |',FAINT)
    label(d,(148,109),'ANURAG DEY',bold,INK)
    label(d,(148,145),'PERSONAL RECORDINGS',font,LINE)
    label(d,(685,108),'SIDE '+side,bold,ACCENT)
    # The oval tape window leaves room around both circular reels.
    label(d,(170,198),'.'+'-'*67+'.',font,LINE)
    label(d,(161,211),'/',font,LINE)
    label(d,(791,211),'\\',font,LINE)
    for py in range(224,303,13):
        label(d,(152,py),'|',font,LINE)
        label(d,(800,py),'|',font,LINE)
    label(d,(161,315),'\\',font,LINE)
    label(d,(791,315),'/',font,LINE)
    label(d,(170,328),"'"+'-'*67+"'",font,LINE)
    # Lower guide plate: a continuous trapezoid and the tape-guide holes.
    label(d,(309,340),'_'*38,font,LINE)
    for step in range(4):
        label(d,(300-step*9,353+step*13),'/',font,LINE)
        label(d,(660+step*9,353+step*13),'\\',font,LINE)
    label(d,(282,392),'_'*44,font,LINE)
    label(d,(302,379),'o    .     [____________]     .    o',font,LINE)
    label(d,(161,352),'I / NORMAL',font,LINE)
    label(d,(702,352),'STEREO',font,LINE)
    return im


def spool(draw,font,cx,cy,angle,radius):
    # Circular tape rolls and six-spoke hubs are sampled onto a monospace grid.
    for yy in range(-5,6):
        for xx in range(-9,10):
            x,y=xx*STEP_X, yy*STEP_Y
            r=math.hypot(x,y)
            if r>radius:
                continue
            glyph=' '
            color=LINE
            if r>radius-8:
                glyph=':'
            elif r>29:
                glyph='.' if (xx+yy)%3 else ':'
                color=FAINT
            elif r<9:
                glyph='O';color=ACCENT
            elif abs(math.sin(3*(math.atan2(y,x)-angle)))<.49:
                glyph='#';color=INK
            if glyph!=' ':
                label(draw,(cx+x-4,cy+y-6),glyph,font,color)


def frame(font,bold,side,n):
    im=shell(font,bold,side)
    d=ImageDraw.Draw(im)
    phase=n/HOLD
    # One roll feeds the other, with a small visible change in winding radius.
    spool(d,font,300,263,n*.065,58-3*phase)
    spool(d,font,660,263,n*.078,52+3*phase)
    for i in range(27):
        glyph='-' if (i+n)%6<4 else '='
        label(d,(363+i*9,260),glyph,font,FAINT)
    return im


def flip_frames(start,end,palette):
    # A soft horizontal turn takes the label from A to B, then back again.
    for n in range(1,FLIP+1):
        t=n/(FLIP+1)
        width=max(3,round(SIZE[0]*abs(math.cos(math.pi*t))))
        source=start if t<.5 else end
        narrow=source.resize((width,SIZE[1]),Image.Resampling.LANCZOS)
        canvas=Image.new('RGB',SIZE,BG)
        canvas.paste(narrow,((SIZE[0]-width)//2,0))
        yield canvas.quantize(palette=palette,dither=Image.Dither.NONE)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font')
    args=parser.parse_args()
    options=[args.font,'/System/Library/Fonts/Menlo.ttc',
             '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
    path=next((p for p in options if p and Path(p).is_file()),None)
    if not path:
        raise SystemExit('Pass --font with a monospace TrueType font path.')
    font=ImageFont.truetype(path,15)
    bold=ImageFont.truetype(path,25)
    raw_a=[frame(font,bold,'A',n) for n in range(HOLD)]
    raw_b=[frame(font,bold,'B',n) for n in range(HOLD)]
    palette=raw_a[0].quantize(colors=64)
    frames=[]
    for source,dest in [(raw_a,raw_b),(raw_b,raw_a)]:
        frames.extend(im.quantize(palette=palette,dither=Image.Dither.NONE) for im in source)
        frames.extend(flip_frames(source[-1],dest[0],palette))
    out=ROOT/'assets';out.mkdir(exist_ok=True)
    raw_a[0].save(out/'cassette-still.png')
    frames[0].save(out/'cassette.gif',save_all=True,append_images=frames[1:],
                   duration=80,loop=0,optimize=True,disposal=2)
    print(f'{len(frames)} frames; {len(frames)*80/1000:.2f}s loop; {(out/"cassette.gif").stat().st_size:,} bytes')


if __name__=='__main__':
    main()
