import sys, zipfile, io
from pathlib import Path
SC=Path(sys.argv[0]).parent; sys.path.insert(0,str(SC))
from render import render_line
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(r"C:\Users\Designer\Documents\Base Agency Designer\Font\BASE AGENCY OFFICIAL FONT\BASE-Meridion-Kurdish-1.010-Base-Agency")

# extract the shipped 1.012 Regular for an honest before/after
old_dir=SC/"v012"; old_dir.mkdir(exist_ok=True)
z=zipfile.ZipFile(ROOT/"build"/"BASE-Meridion-Kurdish-1.012-Base-Agency.zip")
name=[n for n in z.namelist() if n.endswith("Regular.ttf")][0]
(old_dir/"Regular.ttf").write_bytes(z.read(name))
OLD=old_dir/"Regular.ttf"; NEW=ROOT/"fonts"/"BASEMeridionKurdish-Regular.ttf"

NAVY=(17,30,52); CREAM=(246,241,232); BLUE=(49,94,255); RED=(190,45,45); GREEN=(20,120,70)
try:
    F_H=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",44)
    F_S=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",19)
    F_L=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",24)
except Exception:
    F_H=F_S=F_L=ImageFont.load_default()

WORDS=["کەم","گەرم","ناوم","سڵاوم","بەردەم","خۆم","ژیانم","ئەم"]
pairs=[]
for w in WORDS:
    a,_=render_line(OLD,w,px=112); b,_=render_line(NEW,w,px=112)
    pairs.append((a,b))
colw=max(max(a.width,b.width) for a,b in pairs)+40
rh=max(max(a.height,b.height) for a,b in pairs)
head=180; PAD=40
W=PAD*2+colw*2+40; H=head+rh*len(pairs)+40
img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
y=head
for i,(a,b) in enumerate(pairs):
    for k,im in enumerate((a,b)):
        x=PAD+k*(colw+40)
        img.paste(im.convert("RGB"),(x+colw-im.width-20,y),Image.eval(im,lambda v:255-v))
    y+=rh
    d.line([(PAD,y-2),(W-PAD,y-2)],fill=(224,216,202))
d.rectangle([0,0,W,head-46],fill=NAVY)
d.text((PAD,40),"Word-final م  -  before and after",font=F_H,fill=CREAM)
d.text((PAD,100),"BASE MERIDION KURDISH  -  Regular  -  every word here ends in an isolated meem",
       font=F_S,fill=(150,170,215))
d.text((PAD+colw-190,head-36),"1.012  (shipped)",font=F_L,fill=RED)
d.text((PAD+colw+40+colw-190,head-36),"1.013  (fixed)",font=F_L,fill=GREEN)
d.line([(PAD+colw+20,head-10),(PAD+colw+20,H-30)],fill=(210,202,188))
img.save(SC/"meem_before_after.png"); print("saved",img.size)
