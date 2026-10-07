import numpy as np,wave
from pathlib import Path
R=Path(__file__).resolve().parent.parent
sr=44100;dur=80
x=np.zeros((sr*dur,2),dtype=np.float32)
rng=np.random.default_rng(19)
def add(at,freq,duration=.15,gain=.07,pan=0,kind='pluck'):
 n=int(duration*sr);t=np.arange(n)/sr
 if kind=='pluck': y=(np.sin(2*np.pi*freq*t)+.22*np.sin(4*np.pi*freq*t))*np.exp(-t*12)*np.minimum(t*150,1)
 elif kind=='bell':y=(np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*freq*2.7*t))*np.exp(-t*7)
 elif kind=='tick':y=rng.normal(0,.4,n)*np.exp(-t*65)
 elif kind=='sweep':y=np.sin(2*np.pi*(freq*t+150*t*t))*np.exp(-t*8)
 else:y=np.sin(2*np.pi*freq*t)*np.sin(np.pi*t/duration)**2
 k=int(at*sr);n=min(n,len(x)-k)
 if n>0:x[k:k+n,0]+=y[:n]*gain*(1-pan*.5);x[k:k+n,1]+=y[:n]*gain*(1+pan*.5)
# Warm pizzicato score, original eight-bar pattern. Deliberate silence during punchlines.
notes=[261.63,329.63,392,329.63,220,261.63,329.63,293.66]
for k in range(157):
 at=.5+k*.5
 if 27<at<32 or 42<at<50 or 71.5<at<76:continue
 add(at,notes[k%8],.38,.024,(-1 if k%2 else 1)*.3)
 if k%4==0:add(at,notes[k%8]/2,.48,.03)
 if k%2==1:add(at,1200,.06,.012,kind='tick')
# Opening spring, awakening, typing, text chips, notification and final stop.
for at in [3.8,10,20.1,21.75,23.4]:add(at,510,.27,.055,kind='sweep')
for a,b in [(15.4,19),(37,40.7),(51,54.8),(64.5,67.5)]:
 for at in np.arange(a,b,.13):add(float(at),1300,.035,.045,pan=float(rng.uniform(-.4,.4)),kind='tick')
for at in [41.8,56.2]:
 add(at,880,.35,.07,kind='bell');add(at+.16,1174.66,.6,.065,kind='bell')
add(31.4,160,.3,.09,kind='pluck');add(36.6,220,.32,.08,kind='pluck')
add(71.95,90,.3,.15,kind='tick');add(72.03,100,.25,.12,kind='pluck')
for j,f in enumerate([392,329.63,261.63,523.25]):add(76+j*.18,f,.8,.045,kind='bell')
# final limiting and gentle edges
x=np.tanh(x*1.2);x[:2205]*=np.linspace(0,1,2205)[:,None];x[-22050:]*=np.linspace(1,0,22050)[:,None]
with wave.open(str(R/'sound.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((x*32767).astype('<i2').tobytes())
print('Original stereo score + SFX, no spoken audio')
