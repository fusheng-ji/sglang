from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
font_path = '/usr/share/fonts/truetype/dejavu/'
def font(size, bold=False):
    return ImageFont.truetype(font_path + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), size)
ink = '#182c3b'
muted = '#4a6070'
canvas = Image.new('RGB', (2112, 1760), '#f5f7fa')
draw = ImageDraw.Draw(canvas)
draw.text((36,28), 'Hunyuan3D | Mesh validation', font=font(42,True), fill=ink)
draw.text((36,90), 'Fixed reference and real API output · identical cameras, scale, lighting and clay material', font=font(24), fill=muted)
views = [('front','Front'),('three_quarter','Three-quarter'),('rear','Rear')]
for i,(_,label) in enumerate(views):
    draw.text((36+i*680,140),label,font=font(26,True),fill=ink)
for row,(key,label) in enumerate([('reference','FIXED REFERENCE'),('generated','GENERATED · API GLB')]):
    top=188+row*736
    draw.text((36,top),label,font=font(26,True),fill=ink)
    for i,(view,_) in enumerate(views):
        canvas.paste(Image.open(root/f'{key}_{view}.png').convert('RGB'),(36+i*680,top+42))
draw.line((36,1670,2076,1670),fill='#d0d9e1',width=2)
draw.text((36,1689),'Reference diagonal D = 2.9875327625     Normalized squared Chamfer C = 0.0001331739',font=font(24),fill=ink)
draw.text((36,1725),'Threshold = 0.01 · PASS     |     Geometry comparison only; original textures shown separately.',font=font(22),fill=muted)
canvas.save(root/'mesh-comparison.png',optimize=True)
hero = Image.new('RGB',(752,810),'#f5f7fa')
d=ImageDraw.Draw(hero)
d.text((36,20),'Generated API GLB',font=font(30,True),fill=ink)
d.text((36,60),'Original texture · three-quarter view',font=font(21),fill=muted)
hero.paste(Image.open(root/'generated_textured.png').convert('RGB'),(36,98))
hero.save(root/'generated-textured.png',optimize=True)
