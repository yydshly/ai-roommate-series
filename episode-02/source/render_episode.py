"""Episode 02 full visual implementation. Uses local assets only, no API calls."""
from pathlib import Path
import json,sys,math,subprocess,wave,importlib.util
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(Path(__file__).parent));import render_action_sample as sample
rig=sample.rig;W,H=1280,720;INK=rig.INK;PAPER=rig.PAPER;MINT=rig.MINT;ORANGE=rig.ORANGE
BOARD=json.loads((ROOT/'source/storyboard.json').read_text())['shots']
# Dialogue can be dropped into this same timeline later without replacing character geometry.
ENV=json.loads((ROOT/'voices/envelopes.json').read_text()) if (ROOT/'voices/envelopes.json').exists() else {}
TIMING=json.loads((ROOT/'voices/timing.json').read_text()) if (ROOT/'voices/timing.json').exists() else []
DURATION=78;FPS=24
CURRENT_T=0
if TIMING:
 spec=importlib.util.spec_from_file_location('episode01_voiced_rig',ROOT.parent/'v2/source/render.py')
 voicedrig=importlib.util.module_from_spec(spec);spec.loader.exec_module(voicedrig)
 rig=voicedrig;sample.rig=voicedrig
 rig.energy=lambda ignored,who:level(CURRENT_T,who)


def txt(d,pos,s,size=24,color=INK,b=False,anchor=None):rig.txt(d,pos,s,size,color,b,anchor)
def rr(d,b,r,fill,outline=None,width=1):rig.rr(d,b,r,fill,outline,width)
def level(t,who):
 a=ENV.get(who,[]);i=int(t*50);return a[i] if 0<=i<len(a) else 0

def stage(t,pose='normal',botpose='normal',cable=True):
 im=rig.room(t);p=rig.person(t,pose,level(t,'阿程')>.025);b=rig.robot(t,botpose,level(t,'积木')>.025)
 im.paste(p,(323,102),p);im.paste(b,(801,213),b);rig.desk(im,t)
 if cable:
  d=ImageDraw.Draw(im);rig.line(d,[(997,559),(966,605),(733,630),(511,620),(479,602),(505,580),(528,603),(507,624),(375,642)],INK,5)
 return im

def dialog(d,who,line):
 rr(d,(110,615,1170,702),14,INK);txt(d,(133,624),who,17,MINT if who=='积木' else '#ffbf7c',True)
 txt(d,(640,671),line,28 if len(line)>24 else 30,PAPER,True,'mm')
def message(d,line):
 rr(d,(183,69,1097,187),17,PAPER,INK,4);txt(d,(210,83),'客户 · 新消息',20,'#48646b',True);txt(d,(640,143),line,35,INK,True,'mm')
def smallphone(d,x=693,y=346,tilt=0):
 rr(d,(x,y,x+60,y+99),8,INK);rr(d,(x+5,y+9,x+55,y+89),4,PAPER);rr(d,(x+14,y+64,x+48,y+75),4,ORANGE)

def cable_closeup(t,u,freeing=False):
 im=rig.room(t);im=im.crop((355,426,1122,720)).resize((W,H),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im)
 lift=0
 if freeing:lift=58*rig.ease(u/1.0)*(1-rig.ease((u-3.0)/1.0))
 # Purpose-built closeup of the same wooden chair leg and cable, both articulate.
 d.polygon([(298,35-lift),(567,35-lift),(579,104-lift),(285,104-lift)],fill='#caa572',outline=INK)
 rig.line(d,[(285,104-lift),(579,104-lift)],INK,5)
 d.polygon([(384,93-lift),(443,93-lift),(467,568-lift),(399,568-lift)],fill='#caa572',outline=INK)
 rig.line(d,[(399,568-lift),(467,568-lift)],INK,6)
 unwind=rig.ease((u-.65)/2.1) if freeing else 0
 pts=[(1040,514),(811,562),(595,576),(470,541-unwind*52),(380,503-unwind*27),(367,450+unwind*48),(431,423+unwind*75),(487,471+unwind*33),(458,542-unwind*35),(272,585)]
 rig.line(d,pts,INK,10);rig.line(d,pts,'#557c83',5)
 # Left hand lifts, robot hand draws the cable back once unhooked.
 if freeing:
  rig.line(d,[(174,166),(270,220-lift),(387,211-lift)],INK,50);rig.line(d,[(174,166),(270,220-lift),(387,211-lift)],ORANGE,42);rig.ellipse(d,(362,185-lift,413,237-lift),'#f3c399',INK,4)
  bx=1060+unwind*95;rig.line(d,[(1232,356),(1177,440),(bx,514)],INK,18);rig.line(d,[(1232,356),(1177,440),(bx,514)],'#bed7ce',11);rig.ellipse(d,(bx-22,493,bx+20,534),PAPER,INK,4)
  if u>3.4:txt(d,(841,262),'可以动了',37,INK,True,'mm')
 else:
  rig.line(d,[(1177,316),(1070,347),(956,431)],INK,18);rig.line(d,[(1177,316),(1070,347),(956,431)],'#bed7ce',11);rig.ellipse(d,(934,411,975,450),PAPER,INK,3)
 return im

def frame(t):
 global CURRENT_T
 CURRENT_T=t
 s=next((x for x in BOARD if x['start']<=t<x['end']),BOARD[-1]);i=s['shot'];u=t-s['start'];sample.ACTIVE_SPEAKER=s['dialogue'][0]['speaker'] if s['dialogue'] else None;sample.ACTIVE_ENERGY=level(t,sample.ACTIVE_SPEAKER) if sample.ACTIVE_SPEAKER else 0;im=stage(t,'doubt' if i in [5,6,7] else 'typing' if i in [2,9,10] else 'normal','sales' if i==8 else 'normal');d=ImageDraw.Draw(im)
 if i==1:
  rr(d,(399,48,1042,172),17,PAPER,INK,3);txt(d,(720,94),'室友正在优化',42,INK,True,'mm');txt(d,(720,145),'第 02 集  /  大一点',26,INK,True,'mm')
 elif i==2:message(d,'按钮再大一点。');smallphone(d)
 elif i==3:
  im=im.crop((666,176,1272,575)).resize((W,H),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im);txt(d,(824,184),'？',66,INK,True,'mm')
 elif i==4:im=sample.frame(2+u*6/7);d=ImageDraw.Draw(im)
 elif i==5:
  if u<2.7:im=sample.frame(8+u);d=ImageDraw.Draw(im)
  else:
   im=stage(t,'doubt','normal').crop((647,166,1278,576)).resize((W,H),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im)
   rr(d,(-95,100,350,566),22,ORANGE,INK,5);txt(d,(136,327),'先看看',56,INK,True,'mm')
 elif i==6:im=sample.frame(12+u*3.95/7);d=ImageDraw.Draw(im)
 elif i==7:
  smallphone(d);im=im.crop((262,91,987,575)).resize((W,H),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im)
 elif i==8:im=sample.frame(16+u*2.58/8);d=ImageDraw.Draw(im)
 elif i==9:im=sample.frame(18.6+u*4.99/6);d=ImageDraw.Draw(im)
 elif i==10:
  message(d,'可以了，谢谢！')
  rise=rig.ease((u-1)/.8);x=802;y=360+(1-rise)*112
  rr(d,(x,y,x+118,y+71),3,'#f4d983',INK,2);txt(d,(x+59,y+34),'先问一句',22,INK,True,'mm')
 elif i==11:
  if u<2.4:txt(d,(1121,272),'…',47,INK,True,'mm')
  else:im=cable_closeup(t,u-2.4,False);d=ImageDraw.Draw(im)
 elif i==12:
  if u<4.7:im=cable_closeup(t,u,True);d=ImageDraw.Draw(im)
  else:
   im=stage(t,'normal','normal',False);d=ImageDraw.Draw(im);rr(d,(426,73,1035,203),18,PAPER,INK,4);txt(d,(729,122),'第一单，完成。',41,INK,True,'mm');txt(d,(729,175),'下一集  别收拾太干净',24,INK,True,'mm')
 # Replace all excerpt tags and captions with the full-episode review UI.
 rr(d,(26,24,455,62),10,INK);txt(d,(42,31),'第二集 大一点  /  全片动态分镜',18,PAPER,True)
 rr(d,(960,24,1254,62),10,INK);txt(d,(977,32),'配音待授权  ·  画面制作版' if not TIMING else '双角色配音制作版',16,MINT)
 # Clear inherited excerpt subtitle before laying out the canonical board dialogue.
 if i in [4,5,6,8,9]:rr(d,(110,615,1170,704),14,INK)
 if s['dialogue']:
  talk=s['dialogue'][0];dialog(d,talk['speaker'],talk['text'])
 elif i==6:dialog(d,'客户消息','手机上，我总点到旁边。')
 return im

def score():
 sr=44100;a=np.zeros((sr*DURATION,2),np.float32);rng=np.random.default_rng(90)
 def add(at,f,dur=.2,g=.06,kind='pluck'):
  n=int(dur*sr);tt=np.arange(n)/sr
  if kind=='tap':y=rng.normal(0,.35,n)*np.exp(-tt*64)
  elif kind=='slide':y=np.sin(2*np.pi*(f*tt+170*tt*tt))*np.exp(-tt*7)
  else:y=(np.sin(2*np.pi*f*tt)+.16*np.sin(4*np.pi*f*tt))*np.exp(-tt*9)
  k=int(at*sr);n=min(n,len(a)-k)
  if n>0:a[k:k+n]+=y[:n,None]*g
 for k in range(142):
  at=.3+k*.54
  if 23<at<30:continue
  add(at,[261.6,329.6,392,293.7,220,261.6][k%6],.3,.017)
 for at in [4,30,58]:add(at,880,.4,.055);add(at+.14,1174,.4,.04)
 for at,f in [(16,260),(18.3,390),(20.6,520)]:add(at,f,.4,.1,'slide')
 for at in [32.3,35.3]:add(at,120,.14,.08,'tap')
 add(44,650,.3,.045,'slide')
 for at in [52,54.6]:add(at,880,.35,.06);add(at+.12,1174,.4,.05)
 for at in [72,75.1]:add(at,180,.25,.1,'tap')
 for j,f in enumerate([392,329.6,523.2]):add(76.2+j*.16,f,.5,.05)
 a=np.tanh(a);a[-22050:]*=np.linspace(1,0,22050)[:,None]
 with wave.open(str(ROOT/'output/full-visual-sound.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32767).astype('<i2').tobytes())

def main():
 out=ROOT/'output';score();audio=out/'voiced-mix.wav' if TIMING and (out/'voiced-mix.wav').exists() else out/'full-visual-sound.wav';output=out/('episode-02-voiced.mp4' if TIMING else 'episode-02-visual-cut.mp4');p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate',str(FPS),'-i','-','-i',str(audio),'-t',str(DURATION),'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
 for n in range(DURATION*FPS):
  p.stdin.write(frame(n/FPS).tobytes())
  if n%240==0:print('Full visual cut',n/FPS,flush=True)
 p.stdin.close();assert p.wait()==0
 for t in [5,11,21,26,34,40,48,55,62,69,74,77]:frame(t).save(out/f'full-{t}.jpg',quality=92)
 print('Done full visual cut')
if __name__=='__main__':main()
