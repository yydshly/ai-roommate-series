from PIL import Image,ImageDraw,ImageFont
import math,json,subprocess,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'site/dist'; OUT.mkdir(parents=True,exist_ok=True)
W,H=1280,720
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fonts={}
def ft(n,b=False):
 k=(n,b)
 if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n)
 return fonts[k]
INK='#243547'; PAPER='#fff8e9'; MINT='#72d7c2'; ORANGE='#ed8a42'; NAVY='#273d55'
scenes=json.loads((ROOT/'source/storyboard.json').read_text())
def mix(a,b,v):return a+(b-a)*v
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def txt(d,p,s,size=25,color=INK,b=False,anchor=None): d.text(p,s,font=ft(size,b),fill=color,anchor=anchor)
def rr(d,box,r,fill,outline=None,width=1):d.rounded_rectangle(tuple(map(int,box)),r,fill,outline,width)
def line(d,pts,fill,width=3): d.line(pts,fill,width,joint='curve')
def ellipse(d,box,fill,outline=None,width=1):d.ellipse(box,fill,outline,width)
def room(t):
 im=Image.new('RGB',(W,H),'#efdcb8');d=ImageDraw.Draw(im)
 # cinematic apartment architecture, direct morning light
 d.polygon([(0,0),(950,0),(950,490),(0,490)],fill='#f5e8ce')
 d.polygon([(950,0),(1280,0),(1280,490),(950,490)],fill='#dec99f')
 d.polygon([(0,490),(1280,490),(1280,720),(0,720)],fill='#a87857')
 for y in range(520,721,65):line(d,[(0,y),(1280,y)],'#916245',2)
 for x in range(-200,1400,180):line(d,[(x,490),(x+220,720)],'#95674b',2)
 # sun projection
 d.polygon([(86,300),(324,300),(896,620),(330,620)],fill='#f4cf88')
 rr(d,(74,56,375,340),12,INK);rr(d,(86,68,363,328),5,'#7cbbc7')
 for x,y,h in [(96,225,94),(140,207,111),(203,239,79),(253,170,148),(312,214,104)]:
  d.rectangle((x,y,x+38,318),fill='#a2ccd0')
  for yy in range(y+12,300,24):d.rectangle((x+9,yy,x+17,yy+8),fill='#d8e7d7')
 ellipse(d,(285,89,325,129),'#ffedb1')
 d.rectangle((217,65,226,330),fill=INK);d.rectangle((84,198,367,207),fill=INK)
 d.rectangle((54,332,395,348),fill='#d59558'); d.rectangle((58,58,79,325),fill='#efb568')
 for x in (61,69):line(d,[(x,60),(x,324)],'#d59954',2)
 # clock
 ellipse(d,(532,66,622,156),PAPER,INK,5);line(d,[(577,111),(577,81)],INK,4);line(d,[(577,111),(598,120)],INK,4)
 for a in range(12):
  th=a*math.pi/6;line(d,[(577+33*math.sin(th),111-33*math.cos(th)),(577+38*math.sin(th),111-38*math.cos(th))],INK,2)
 # shelf
 rr(d,(1042,105,1220,117),3,'#9c694c')
 for j,c in enumerate(['#d58351','#739e91','#e1b861','#355265']):rr(d,(1060+j*26,52+j%2*8,1080+j*26,105),2,c)
 txt(d,(1124,158),'先做完',24,INK,True);txt(d,(1124,189),'再完美',24,INK,True)
 # framed reminder
 rr(d,(735,79,873,238),3,INK);rr(d,(742,86,866,231),2,PAPER)
 txt(d,(804,122),'一件',25,INK,True,'mm');txt(d,(804,162),'小事',25,INK,True,'mm');line(d,[(771,197),(837,197)],ORANGE,6)
 # sofa
 rr(d,(86,402,398,548),28,'#3d6774',INK,4);rr(d,(106,377,376,503),24,'#56858b',INK,4)
 line(d,[(241,384),(241,496)],'#36606b',3);rr(d,(92,460,132,557),16,'#598990',INK,4)
 rr(d,(344,460,385,557),16,'#598990',INK,4);rr(d,(139,484,339,550),11,'#467783',INK,3)
 line(d,[(120,550),(111,590)],INK,9);line(d,[(357,552),(367,590)],INK,9)
 # cushion, blanket
 d.polygon([(142,405),(207,396),(222,464),(153,474)],fill='#e7b768',outline=INK)
 d.polygon([(291,420),(342,422),(335,563),(285,565)],fill='#e8dcc1')
 for yy in range(430,560,12):line(d,[(290,yy),(337,yy)],'#c7804d',2)
 # floor plant
 line(d,[(1171,505),(1164,319)],'#416952',7)
 for x,y,s in [(1126,350,1),(1193,380,-1),(1133,420,1),(1186,315,-1)]:
  ellipse(d,(x-26,y-18,x+24,y+18),'#59875c');line(d,[(x,y),(1167,y+25)],'#416952',5)
 d.polygon([(1127,479),(1204,479),(1190,565),(1142,565)],fill='#d87f4e',outline=INK)
 rr(d,(1120,474,1210,490),5,'#e09360',INK,3)
 # carpet
 ellipse(d,(355,537,1084,677),'#516d71');ellipse(d,(384,550,1050,661),'#709292')
 return im

def person(t,pose='normal',speaking=False):
 im=Image.new('RGBA',(500,590));d=ImageDraw.Draw(im)
 bob=math.sin(t*2.4)*2; lean=0; headTilt=0
 # body silhouette seated, animated shoulders
 if pose=='proud': lean=-10*math.sin(t*1.4);headTilt=-3
 if pose=='doubt':lean=-16;headTilt=4
 if pose=='stop':lean=22*ease((t-72)/.25);headTilt=-5
 bx=250+lean;by=280+bob
 # chair
 rr(d,(149,310,336,489),25,'#caa572',INK,5);line(d,[(175,474),(157,574)],INK,10);line(d,[(305,475),(333,574)],INK,10)
 # legs articulated
 legbob=math.sin(t*2)*3
 line(d,[(bx-32,430),(211,496),(218,551+legbob)],NAVY,38)
 line(d,[(bx+30,430),(308,490),(341,550)],NAVY,38)
 rr(d,(187,537+legbob,248,565+legbob),11,'#ebeee0',INK,4);rr(d,(321,535,385,563),11,'#ebeee0',INK,4)
 line(d,[(194,554+legbob),(239,554+legbob)],INK,3);line(d,[(334,551),(379,551)],INK,3)
 # hoodie
 d.polygon([(bx-56,by-14),(bx+55,by-14),(bx+70,by+131),(bx-72,by+132)],fill=ORANGE,outline=INK)
 rr(d,(bx-49,by+73,bx+47,by+114),12,'#dd7334',INK,3)
 # neck
 rr(d,(bx-17,by-49,bx+20,by+2),13,'#eab389',INK,3)
 # hood and collar
 d.arc((bx-56,by-36,bx+56,by+41),0,180,fill=INK,width=4)
 line(d,[(bx-9,by+8),(bx-12,by+61)],'#ffe4b9',3);line(d,[(bx+14,by+8),(bx+18,by+55)],'#ffe4b9',3)
 # head drawn independently for squash/tilt
 head=Image.new('RGBA',(225,230));h=ImageDraw.Draw(head)
 ellipse(h,(18,90,51,127),'#edb58c',INK,3);ellipse(h,(178,90,208,127),'#edb58c',INK,3)
 rr(h,(35,37,191,190),52,'#f3c399',INK,4)
 # hair graphic tuft with irregular silhouette
 h.polygon([(33,113),(23,60),(42,39),(38,19),(65,26),(87,7),(109,21),(137,9),(158,30),(186,29),(203,62),(186,99),(174,71),(158,78),(146,55),(113,70),(85,55),(60,79),(47,76),(46,119)],fill=INK)
 # glasses
 rr(h,(46,92,107,134),12,None,INK,5);rr(h,(122,92,181,134),12,None,INK,5);line(h,[(107,109),(122,109)],INK,4)
 blink=math.sin(t*2.5)>0.995
 brow= -5 if pose in ['proud','stop'] else (6 if pose=='doubt' else 0)
 line(h,[(57,82+brow),(96,82-brow/2)],INK,4);line(h,[(132,82-brow/2),(170,82+brow)],INK,4)
 eyeShift=4 if pose in ['doubt','stop'] else 2
 for x in [77,150]:
  if blink:line(h,[(x-7,113),(x+7,113)],INK,3)
  else:ellipse(h,(x-5+eyeShift,103,x+3+eyeShift,118),INK)
 line(h,[(112,119),(110,138),(120,138)],'#c28d6d',3)
 if speaking:
  mh=5+int(abs(math.sin(t*13))*13);ellipse(h,(96,151,135,151+mh),INK)
  if mh>12:ellipse(h,(107,160,126,151+mh),'#e79287')
 elif pose=='doubt':line(h,[(96,160),(131,158)],INK,3)
 else:h.arc((93,145,140,170),0,180,INK,3)
 # subtle freckles
 for x in [60,67,162,169]:ellipse(h,(x,143,x+2,145),'#c48468')
 head=head.rotate(headTilt+math.sin(t*1.7)*1.2,resample=Image.Resampling.BICUBIC)
 im.alpha_composite(head,(int(bx-114),int(by-226)))
 # arms with animated elbows and palms
 armphase=math.sin(t*4)*8 if speaking else math.sin(t*1.7)*2
 left=[(bx-53,by+9),(bx-80,by+70),(bx-8,by+88+armphase)]
 right=[(bx+53,by+9),(bx+80,by+64),(bx+119,by+68+armphase)]
 if pose=='proud':right=[(bx+50,by+9),(bx+94,by-8),(bx+85,by-75+armphase)]
 if pose=='doubt':right=[(bx+50,by+9),(bx+73,by+78),(bx+111,by+24+armphase)]
 if pose=='stop':right=[(bx+50,by+9),(bx+122,by-33),(bx+200,by-44)]
 if pose=='typing':right=[(bx+50,by+9),(bx+73,by+70),(bx+119,by+74+math.sin(t*22)*4)]
 for points in [left,right]:
  line(d,points,INK,31);line(d,points,ORANGE,24)
  x,y=points[-1];ellipse(d,(x-15,y-13,x+17,y+15),'#f3c399',INK,3)
  if pose=='stop' and points==right:
   rr(d,(x-17,y-30,x+15,y+17),9,'#f3c399',INK,3)
   for xx in [x-12,x-5,x+2,x+9]:line(d,[(xx,y-20),(xx,y+1)],'#b17d5f',2)
 return im

def robot(t,pose='normal',speaking=False):
 im=Image.new('RGBA',(390,420));d=ImageDraw.Draw(im); bob=math.sin(t*3)*7
 if t<4:bob=math.sin(t*1.6)*2
 x=185;y=173+bob
 # underlight, feet/charging base
 ellipse(d,(111,341,261,363),'#284552')
 ellipse(d,(116,333,256,353),'#a8e8d3',INK,3)
 line(d,[(153,y+116),(146,336)],INK,12);line(d,[(220,y+116),(228,336)],INK,12)
 rr(d,(128,326,161,345),8,'#f7efdc',INK,3);rr(d,(211,326,245,345),8,'#f7efdc',INK,3)
 # segmented arms
 wave=math.sin(t*7)*16 if speaking else math.sin(t*2)*4
 lx,ly=80,y+70;rx,ry=295,y+55
 if pose in ['sales','three']:rx,ry=300,y-25+wave
 if pose=='send':rx,ry=317,y+90
 if pose=='stop':rx,ry=273,y+60
 for pts in [[(121,y+64),(94,y+100),(lx,ly)],[(253,y+64),(280,y+100),(rx,ry)]]:
  line(d,pts,INK,15);line(d,pts,'#bed7ce',9)
  for j in pts[1:2]:ellipse(d,(j[0]-8,j[1]-8,j[0]+8,j[1]+8),'#fbf0d9',INK,3)
  xx,yy=pts[-1];ellipse(d,(xx-15,yy-13,xx+15,yy+13),'#fbf0d9',INK,3)
 if pose=='three':
  for dx in [-10,0,10]:line(d,[(rx+dx,ry),(rx+dx,ry-25)],INK,8);line(d,[(rx+dx,ry),(rx+dx,ry-25)],'#fbf0d9',4)
 # body
 rr(d,(106,y-21,264,y+125),43,'#fff3d8',INK,5)
 rr(d,(120,y-1,251,y+77),24,MINT,INK,4)
 line(d,[(184,y-21),(184,y-53)],INK,5)
 ellipse(d,(173,y-70,196,y-47),ORANGE,INK,3)
 if t>=10:
  for a in [-.8,0,.8]:line(d,[(184+math.sin(a)*21,y-59-math.cos(a)*22),(184+math.sin(a)*28,y-59-math.cos(a)*32)],'#d68434',3)
 # expression: LEDs stay tied to body
 sleeping=t<3.5
 blink=math.sin(t*2.7)>0.982
 for ex in [151,217]:
  if sleeping or blink:line(d,[(ex-10,y+27),(ex+10,y+27)],INK,5)
  elif pose=='sales':d.arc((ex-12,y+16,ex+12,y+42),180,360,INK,5)
  else:rr(d,(ex-6,y+14,ex+6,y+36),5,INK)
 if speaking:
  mh=4+abs(math.sin(t*15))*9;rr(d,(175,y+45,196,y+45+mh),4,INK)
 else:d.arc((169,y+37,201,y+56),0,180,INK,3)
 # blush/power mark
 line(d,[(131,y+44),(139,y+44)],'#349a89',3);line(d,[(231,y+44),(239,y+44)],'#349a89',3)
 ellipse(d,(177,y+96,193,y+112),ORANGE,INK,2)
 if sleeping:txt(d,(280,90),'z',28,'#6b8d8a',True)
 return im

def desk(im,t):
 d=ImageDraw.Draw(im)
 # desk surfaces, foreground laptop
 d.polygon([(438,464),(900,464),(943,514),(416,514)],fill='#cc985f',outline=INK)
 rr(d,(418,510,943,527),3,'#93623e',INK,4)
 for x in [443,895]:d.polygon([(x,524),(x+17,524),(x+23,650),(x+3,650)],fill=INK)
 # laptop
 d.polygon([(638,386),(804,386),(792,489),(624,489)],fill='#456577',outline=INK)
 line(d,[(638,386),(804,386),(792,489),(624,489),(638,386)],INK,4)
 ellipse(d,(700,423,724,447),MINT)
 d.polygon([(624,489),(792,489),(832,503),(603,503)],fill='#77989d',outline=INK)
 # cup
 rr(d,(463,438,496,480),5,'#fff3d8',INK,3);d.arc((486,446,509,468),270,90,INK,4)
 for j in range(2):
  off=math.sin(t*2+j)*3;line(d,[(475+j*9,430),(473+j*9+off,417),(477+j*9,406)],'#d6bea0',2)
 # papers
 d.polygon([(846,479),(891,477),(909,497),(858,499)],fill=PAPER,outline=INK)
 for y in [484,489]:line(d,[(856,y),(885,y-1)],'#8ba0a0',2)

def bubble(im,text,title='积木优化中',t=0):
 d=ImageDraw.Draw(im);rr(d,(790,273,1196,424),19,'#fffaf0',INK,4)
 rr(d,(811,292,907,320),9,MINT);txt(d,(825,295),title,15,INK,True)
 txt(d,(813,340),text,28,INK,True)

def frame(t):
 idx=next((i for i,s in enumerate(scenes) if s['start']<=t<s['end']),len(scenes)-1);s=scenes[idx];u=t-s['start']
 speaking=s['speaker']=='阿程';rSpeak=s['speaker']=='积木'
 pp='typing' if idx in [7,9,11] else ('proud' if idx==1 else ('doubt' if idx in [4,5,6,8] else ('stop' if idx==13 else 'normal')))
 rp='sales' if idx in [2,4,6] else ('three' if idx==12 else ('send' if idx==7 else ('stop' if idx==13 else 'normal')))
 im=room(t)
 p=person(t,pp,speaking);r=robot(t,rp,rSpeak)
 im.paste(p,(323,102),p);im.paste(r,(801,213),r)
 desk(im,t)
 # anticipation card / exaggerated pitch stacks
 if idx==4:
  labels=['全栈架构师','增长专家','全天候交付引擎']
  for j,lab in enumerate(labels):
   appear=ease((u-j*1.65)/.35)
   if appear>0:
    d=ImageDraw.Draw(im);x=820+int((1-appear)*420);y=42+j*75
    rr(d,(x,y,x+340,y+62),12,'#fff7df',INK,3);txt(d,(x+21,y+11),lab,28,INK,True)
 if idx==7 and u>3:
  d=ImageDraw.Draw(im);rr(d,(738,343,869,388),12,MINT,INK,3);txt(d,(757,349),'已发送 ✓',21,INK,True)
 # staging closeups/cuts, actual motions are independent of camera
 crop=None
 if idx==1:crop=(305,90,850,580)
 if idx in [2,6,12]:crop=(755,152,1230,579)
 if idx==5:crop=(300,98,861,603)
 if crop:
  # maintain aspect: expand horizontal crop around subject to 16:9
  x0,y0,x1,y1=crop;hh=y1-y0;ww=hh*16/9;cx=(x0+x1)/2
  crop=(max(0,cx-ww/2),y0,min(W,cx+ww/2),y1)
  im=im.crop(tuple(map(int,crop))).resize((W,H),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im)
 if idx in [8,10]:
  # readable client message as foreground insert; actors remain reacting below
  y=80;rr(d,(128,y,1152,y+225),22,'#fffaf0',INK,4)
  ellipse(d,(159,y+29,207,y+77),'#7b9dac');txt(d,(183,y+52),'客',22,'#fffaf0',True,'mm')
  txt(d,(225,y+31),'客户 · 新消息',22,'#557077',True)
  if idx==8:
   txt(d,(178,y+106),'你写的是你会做，',38,INK,True);txt(d,(178,y+164),'还是准备让 AI 学会做？',38,INK,True)
  else:
   txt(d,(178,y+102),'那先帮我改个按钮。',36,INK,True);txt(d,(178,y+158),'把“立即购买”改成“先看看”。',36,INK,True)
 if idx==13 and u<.4:
  # 4-frame snap impact graphic, never replaces the animated acting
  for a in range(8):
   th=a*math.pi/4;line(d,[(970+math.cos(th)*65,381+math.sin(th)*65),(970+math.cos(th)*94,381+math.sin(th)*94)],PAPER,6)
 # graphic episode title/open/close
 if idx in [0,14]:
  if idx==0:
   rr(d,(425,30,1025,147),16,PAPER,INK,3)
   txt(d,(725,68),'室友正在优化',43,INK,True,'mm');txt(d,(725,117),'第 01 集  /  先别承诺',23,'#876c51',False,'mm')
  else:
   overlay=Image.new('RGBA',(W,H),(27,45,57,235));im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
   txt(d,(640,189),'室友正在优化',68,PAPER,True,'mm')
   txt(d,(640,284),'下一集：只是一个按钮？',32,MINT,True,'mm')
   rr(d,(373,348,907,409),16,'#38515d');txt(d,(640,378),'积木：正在优化「承诺方式」…',24,PAPER,False,'mm')
   txt(d,(640,528),'原创动画试播 · 字幕与音效版',21,'#b6c5c5',False,'mm')
 # film chapter tag + safe-area subtitles
 if idx not in [0,14]:
  rr(d,(31,24,228,61),12,INK);txt(d,(48,30),'室友正在优化 · 01',17,PAPER,True)
  if s['speaker'] not in ['客户消息','']:
   lines=[s['text']]
   if len(s['text'])>23:
    # explicit readable two-line dialogue split
    cut=next((k+1 for k,c in enumerate(s['text']) if c in '，。' and 7<k<20),len(s['text'])//2)
    lines=[s['text'][:cut],s['text'][cut:]]
   nh=48*len(lines)+40
   rr(d,(105,690-nh,1175,700),14,INK)
   txt(d,(134,701-nh),s['speaker'],18,MINT if rSpeak else '#ffbc77',True)
   for j,l in enumerate(lines):txt(d,(640,728-nh+j*45),l,32,PAPER,True,'mm')
 # cut transition 2 frames, short blink not a crossfade slideshow
 frac=u
 if idx>0 and frac<.083:
  ov=Image.new('RGB',(W,H),INK);im=Image.blend(ov,im,min(1,frac/.083))
 return im

def render(end=80,name='pilot'):
 fps=12
 cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(fps),'-i','-','-i',str(ROOT/'sound.wav'),'-t',str(end),'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/(name+'.mp4'))]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for n in range(round(end*fps)):
  proc.stdin.write(frame(n/fps).tobytes())
  if n%120==0:print(f'{name}: {n/fps:.0f}/{end}s',flush=True)
 proc.stdin.close();assert proc.wait()==0
 if name=='pilot':
  for ti in [5,12,23,29,34,45,59,70,73]:frame(ti).save(OUT/f'frame-{ti}.jpg',quality=90)
  frame(5).save(OUT/'poster.jpg',quality=92)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='stills':
  for ti in [5,12,23,29,34,45,59,70,73]:frame(ti).save(OUT/f'frame-{ti}.jpg',quality=90)
 else:render(float(sys.argv[1]) if len(sys.argv)>1 else 80,sys.argv[2] if len(sys.argv)>2 else 'pilot')
