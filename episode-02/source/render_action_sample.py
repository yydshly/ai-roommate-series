from pathlib import Path
import sys,math,json,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT.parent/'source'))
import render as rig
W,H=1280,720;INK=rig.INK;MINT=rig.MINT;PAPER=rig.PAPER;ORANGE=rig.ORANGE
DURATION=24;FPS=24
ACTIVE_SPEAKER=None
ACTIVE_ENERGY=0.0

def txt(d,pos,text,size=24,color=INK,bold=False,anchor=None):rig.txt(d,pos,text,size,color,bold,anchor)
def rr(d,b,r,fill,outline=None,width=1):rig.rr(d,b,r,fill,outline,width)
def e(x):return rig.ease(x)
def scene(t):
 im=rig.room(t);person=rig.person(t,'proud' if t<6 else 'doubt' if t<12 else 'normal',ACTIVE_SPEAKER=='阿程' and ACTIVE_ENERGY>.025);bot=rig.robot(t,'normal' if t<8 else 'sales',ACTIVE_SPEAKER=='积木' and ACTIVE_ENERGY>.025)
 im.paste(person,(323,102),person);im.paste(bot,(801,213),bot);rig.desk(im,t)
 return im

def cursor(d,x,y,pressed=False):
 d.polygon([(x,y),(x+8,y+32),(x+15,y+22),(x+26,y+25)],fill=PAPER,outline=INK)
 if pressed:
  for a in range(4):
   th=a*math.pi/2;rig.line(d,[(x+math.cos(th)*13,y+math.sin(th)*13),(x+math.cos(th)*22,y+math.sin(th)*22)],ORANGE,3)
def phone(d):
 rr(d,(414,72,866,606),38,INK);rr(d,(427,88,853,590),29,PAPER)
 rr(d,(560,94,720,116),11,INK);txt(d,(640,160),'一个小网页',25,INK,True,'mm')
 rr(d,(457,199,823,282),12,'#cbe2dd');txt(d,(640,239),'看一眼，再决定',26,INK,True,'mm')
 for y in [316,342,368]:rr(d,(476,y,805-(y-316),y+10),5,'#d6d9d2')
 rr(d,(557,427,723,475),11,ORANGE,INK,3);txt(d,(640,451),'先看看',24,INK,True,'mm')
 rr(d,(592,564,688,571),3,INK)
def finger(d,x,y,contact=False):
 # articulated thumb moving in from the lower right, not a floating pointer
 rig.line(d,[(1070,665),(975,595),(x+58,y+61),(x,y)],INK,50)
 rig.line(d,[(1070,665),(975,595),(x+58,y+61),(x,y)],'#f3c399',42)
 rig.ellipse(d,(x-23,y-23,x+23,y+23),'#f3c399',INK,3)
 rr(d,(x-13,y-16,x+12,y+1),7,'#f8d8b8','#cf9c78',2)
 if contact:rig.ellipse(d,(x-31,y-31,x+31,y+31),None,'#bd7954',2)
def ring(d,x,y,progress,good=False):
 rad=10+progress*38;rig.ellipse(d,(x-rad,y-rad,x+rad,y+rad),None,MINT if good else '#d16e56',max(1,round(5*(1-progress))))

def frame(t):
 im=scene(t);d=ImageDraw.Draw(im)
 if t<12:
  # A real UI panel appears over the apartment for the comic screen insert.
  pop=e(t/.7);panel_y=160+(1-pop)*350
  rr(d,(173,panel_y,1100,panel_y+373),18,PAPER,INK,4)
  rr(d,(173,panel_y,1100,panel_y+42),17,INK)
  for j in range(3):rig.ellipse(d,(192+j*20,panel_y+14,201+j*20,panel_y+23),[ORANGE,MINT,'#e6cb87'][j])
  txt(d,(258,panel_y+9),'预览  /  手机页面',18,PAPER,True)
  # Escalation is keyed in three distinct pulls, with overshoot on the third.
  growth=e((t-2)/1.2)*.22+e((t-4)/1.25)*.30+e((t-6)/1.5)*.48
  spring=math.sin((t-6)*13)*math.exp(-max(0,t-6)*2)*.07 if t>6 else 0
  growth=max(0,min(1.06,growth+spring));bw=150+growth*830;bh=46+growth*283
  # Content compresses and slides away instead of merely zooming the whole frame.
  for j in range(3):
   x=212+j*274-growth*90;yy=panel_y+65+growth*80
   rr(d,(x,yy,x+236*(1-growth*.64),yy+62),9,'#d2e4df',INK,1)
  cx=637;cy=panel_y+250-growth*20
  rr(d,(cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2),13+int(growth*15),ORANGE,INK,4)
  txt(d,(cx,cy),'先看看',round(23+growth*61),INK,True,'mm')
  if t<8:
   x=cx+bw/2+4;y=cy+bh/2;cursor(d,x,y,any(abs(t-a)<.25 for a in [2,4,6]))
   rr(d,(x-5,y-5,x+5,y+5),2,PAPER,INK,2)
  if t>=8:
   # Human reaction cutout above the intrusive button: eyes and raised eyebrows remain visible.
   head=rig.person(t,'doubt',False).crop((130,32,370,250)).resize((216,196))
   im.paste(head,(211,142),head);d=ImageDraw.Draw(im)
   d.rectangle((198,285,438,374),fill=ORANGE)
  sub='还能是哪儿？就是这个嘛。' if t<8 else '嗯。网页好像被按钮吃了。'
  speaker='阿程' if t<8 else '积木'
 else:
  # New shot: a phone and an articulated thumb demonstrate misses, then a larger hit area.
  shade=Image.new('RGBA',(W,H),(24,42,51,155));im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB');d=ImageDraw.Draw(im)
  phone(d);u=t-12
  if u>=4:
   spread=e((u-4)/1.2);pad=7+spread*37
   layer=Image.new('RGBA',(W,H));q=ImageDraw.Draw(layer)
   q.rounded_rectangle((557-pad,427-pad,723+pad,475+pad),radius=18,fill=(114,215,194,65),outline=(53,138,122,230),width=3)
   im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(im)
   rr(d,(557,427,723,475),11,ORANGE,INK,3);txt(d,(640,451),'先看看',24,INK,True,'mm')
   for xx,yy in [(557-pad,427-pad),(723+pad,475+pad)]:rr(d,(xx-6,yy-6,xx+6,yy+6),2,PAPER,INK,2)
  # Four distinct thumb reaches: two old misses and two corrected successful taps.
  hits=[(1.3,750,486,False),(3.0,738,410,False),(6.6,750,486,True),(8.8,738,410,True)]
  active=None
  for at,x,y,good in hits:
   if at-.7<=u<=at+.65:active=(at,x,y,good)
  if active:
   at,x,y,good=active;delta=u-at;reach=e((delta+.7)/.7) if delta<0 else 1-e(delta/.65);fx=1040+(x-1040)*reach;fy=620+(y-620)*reach
   finger(d,fx,fy,abs(delta)<.14)
   if 0<=delta<.65:ring(d,x,y,delta/.65,good)
  else:finger(d,1050,625)
  for at,x,y,good in hits:
   if 0<=u-at<.8:
    if good:txt(d,(640,526),'点到了',24,'#277f6a',True,'mm')
    else:
     rig.line(d,[(x-10,y-10),(x+10,y+10)],'#bc5b45',5);rig.line(d,[(x+10,y-10),(x-10,y+10)],'#bc5b45',5)
  if u>10:
   rr(d,(463,308,817,389),13,MINT,INK,3);txt(d,(640,350),'这回对了',31,INK,True,'mm')
  sub='手机上，我总点到旁边。' if u<4 else '给手指留点余地。' if u<10 else '这回对了。'
  speaker='客户消息' if u<4 else '积木' if u<10 else '阿程'
 # Consistent review label, clear that the new performance is not recorded yet.
 rr(d,(26,24,422,62),10,INK);txt(d,(43,31),'第二集 大一点  /  动作与时序样段',18,PAPER,True)
 rr(d,(961,25,1252,62),10,INK);txt(d,(979,32),'本集对白待录  ·  原创音效',16,MINT)
 rr(d,(111,620,1169,702),14,INK);txt(d,(133,629),speaker,17,MINT if speaker=='积木' else '#ffbf7c',True);txt(d,(640,671),sub,30,PAPER,True,'mm')
 if abs(t-12)<.085:im=Image.blend(Image.new('RGB',(W,H),INK),im,min(1,abs(t-12)/.085))
 return im

def audio():
 sr=44100;x=np.zeros((DURATION*sr,2),np.float32);rng=np.random.default_rng(81)
 def add(at,f,dur=.18,vol=.07,kind='pluck'):
  n=int(dur*sr);tt=np.arange(n)/sr
  if kind=='sweep':y=np.sin(2*np.pi*(f*tt+230*tt*tt))*np.exp(-tt*9)
  elif kind=='click':y=rng.normal(0,.4,n)*np.exp(-tt*70)
  else:y=(np.sin(2*np.pi*f*tt)+.2*np.sin(2*np.pi*f*2*tt))*np.exp(-tt*10)
  i=int(at*sr);n=min(n,len(x)-i);x[i:i+n]+=y[:n,None]*vol
 for k in range(42):
  at=.3+k*.55
  if 8<at<12:continue
  add(at,[261.6,329.6,392,293.7][k%4],.25,.018)
 for t,f in [(2,260),(4,390),(6,520)]:add(t,f,.38,.10,'sweep')
 add(8.1,140,.3,.09)
 for at in [13.3,15]:add(at,130,.12,.09,'click')
 add(16,650,.3,.045,'sweep')
 for at in [18.6,20.8]:add(at,880,.35,.07);add(at+.12,1174,.4,.06)
 add(22.2,523,.6,.05)
 x=np.tanh(x);x[:2205]*=np.linspace(0,1,2205)[:,None];x[-11025:]*=np.linspace(1,0,11025)[:,None]
 with wave.open(str(ROOT/'output/action-sound.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((x*32767).astype('<i2').tobytes())

def main():
 out=ROOT/'output';out.mkdir(exist_ok=True);audio();p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate',str(FPS),'-i','-','-i',str(out/'action-sound.wav'),'-t',str(DURATION),'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/'episode-02-action-sample.mp4')],stdin=subprocess.PIPE)
 for n in range(DURATION*FPS):
  p.stdin.write(frame(n/FPS).tobytes())
  if n%120==0:print('Rendered',n/FPS,'seconds',flush=True)
 p.stdin.close();assert p.wait()==0
 for t in [1,4.7,8.7,13.35,16.7,18.7,22.5]:frame(t).save(out/f'frame-{t}.jpg',quality=92)
 print('Done',out/'episode-02-action-sample.mp4')
if __name__=='__main__':main()
