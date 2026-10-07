from pathlib import Path
import json,subprocess,wave,math
import numpy as np
from scipy.signal import butter,sosfilt
R=Path(__file__).resolve().parent.parent;SR=44100
old=json.loads((R.parent/'source/storyboard.json').read_text()); voices=R/'voices';(voices/'processed').mkdir(exist_ok=True)
def decode(path,sr=SR):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','1','-ar',str(sr),'-']),dtype='<f4').copy()
def writewav(p,x,sr=SR):
 with wave.open(str(p),'wb') as w:w.setnchannels(1 if x.ndim==1 else x.shape[1]);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def robotize(src,out):
 sr=32000;raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-af','rubberband=pitch=0.90:formant=preserved','-f','f32le','-ac','1','-ar',str(sr),'-']);x=np.frombuffer(raw,dtype='<f4').astype(float);t=np.arange(len(x))/sr
 carrier=np.zeros(len(x))
 for h in range(1,49):carrier+=np.sin(2*np.pi*168*h*t)/(h**.82)
 carrier/=np.sqrt(np.mean(carrier**2));carrier=carrier*.94+np.random.default_rng(71).normal(0,1,len(x))*.06
 edges=np.geomspace(110,10500,31);rob=np.zeros(len(x))
 for lo,hi in zip(edges[:-1],edges[1:]):
  filt=butter(3,[lo,hi],btype='bandpass',fs=sr,output='sos');mod=sosfilt(filt,x);env=np.sqrt(np.maximum(sosfilt(butter(2,42,fs=sr,output='sos'),mod*mod),0));c=sosfilt(filt,carrier);rob+=c/(np.sqrt(np.mean(c*c))+1e-8)*env
 hi=sosfilt(butter(2,4400,btype='highpass',fs=sr,output='sos'),x);rob=rob*.84+x*.12+hi*.3;rob=sosfilt(butter(2,[100,11500],btype='bandpass',fs=sr,output='sos'),rob);rob*=.69/max(np.max(np.abs(rob)),1e-9);writewav(out,rob,sr)
# Treat every robot line exactly like the delivered revised sample, no new provider requests.
for s in old:
 if s['speaker'] in ['阿程','积木']:
  source=voices/f"line-{s['start']:02}.mp3"
  if not source.exists():raise FileNotFoundError(source)
  if s['speaker']=='积木':robotize(source,voices/'processed'/f"line-{s['start']:02}-robot.wav")
new=[];cursor=0;audio_by_id={}
for i,s0 in enumerate(old):
 s=dict(s0);s['source_start']=s0['start'];s['source_end']=s0['end']
 if s['speaker'] in ['阿程','积木']:
  base=f"line-{s0['start']:02}";p=voices/'processed'/f'{base}-robot.wav' if s['speaker']=='积木' else voices/f'{base}.mp3';a=decode(p)
  nz=np.flatnonzero(np.abs(a)>.0015)
  if len(nz):a=a[max(0,nz[0]-int(.06*SR)):min(len(a),nz[-1]+int(.12*SR))]
  a*=.67/max(float(np.max(np.abs(a))),1e-9);audio_by_id[base]=a
  dur=len(a)/SR;lead=.25 if i!=13 else .08;tail={1:1.05,2:.6,3:.65,4:.8,5:1.15,6:1.1,7:.8,9:.6,11:.6,12:.18,13:1.15}[i]
  length=lead+dur+tail;s.update(voice_lead=lead,voice_file=str(p.relative_to(voices)),voice_duration=dur,voice_raw_duration=dur,line_id=base)
 else:length={0:3,8:6,10:6.5,14:3.5}[i]
 s['start']=cursor;cursor+=length;s['end']=cursor;new.append(s)
if cursor<60:
 extra=(60-cursor)/5
 for i in [4,5,6,8,10]:new[i]['end']+=extra
 cursor=0
 for s in new:
  length=s['end']-s['start'];s['start']=cursor;cursor+=length;s['end']=cursor
(R/'source/storyboard.json').write_text(json.dumps(new,ensure_ascii=False,indent=2));(R/'source/timing-revision.json').write_text(json.dumps({'original_duration':80,'new_duration':cursor,'scene_order_unchanged':True,'retime':'Actual dialogue lengths + reaction and reading pauses','scenes':new},ensure_ascii=False,indent=2))
# Original score, newly placed on the revised scene map.
x=np.zeros((math.ceil(cursor*SR),2),np.float32);rng=np.random.default_rng(19)
def add(at,freq,duration=.15,gain=.07,pan=0,kind='pluck'):
 n=int(duration*SR);t=np.arange(n)/SR
 if kind=='pluck':y=(np.sin(2*np.pi*freq*t)+.22*np.sin(4*np.pi*freq*t))*np.exp(-t*12)*np.minimum(t*150,1)
 elif kind=='bell':y=(np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*freq*2.7*t))*np.exp(-t*7)
 elif kind=='tick':y=rng.normal(0,.4,n)*np.exp(-t*65)
 else:y=np.sin(2*np.pi*(freq*t+150*t*t))*np.exp(-t*8)
 k=max(0,int(at*SR));n=min(n,len(x)-k)
 if n>0:x[k:k+n,0]+=y[:n]*gain*(1-pan*.5);x[k:k+n,1]+=y[:n]*gain*(1+pan*.5)
notes=[261.63,329.63,392,329.63,220,261.63,329.63,293.66]
for k in range(int(cursor*2)-1):
 at=.5+k*.5
 if any(new[j]['start']<at<new[j]['end'] for j in [5,8,13]):continue
 add(at,notes[k%8],.38,.024,(-1 if k%2 else 1)*.3)
 if k%4==0:add(at,notes[k%8]/2,.48,.03)
 if k%2:add(at,1200,.06,.012,kind='tick')
for at in [new[1]['start']-.15,new[2]['start'],new[4]['start']+.25,new[4]['start']+new[4]['voice_duration']*.34,new[4]['start']+new[4]['voice_duration']*.60]:add(at,510,.27,.055,kind='sweep')
for j in [3,7,9,11]:
 for at in np.arange(new[j]['start']+.3,new[j]['end']-.5,.13):add(float(at),1300,.035,.045,float(rng.uniform(-.4,.4)),kind='tick')
for at in [new[8]['start'],new[10]['start']]:add(at,880,.35,.07,kind='bell');add(at+.16,1174.66,.6,.065,kind='bell')
add(new[5]['end']-.45,160,.3,.09);add(new[6]['end']-.4,220,.32,.08);add(new[13]['start'],90,.3,.15,kind='tick');add(new[13]['start']+.06,100,.25,.12)
for j,f in enumerate([392,329.63,261.63,523.25]):add(new[14]['start']+j*.18,f,.8,.045,kind='bell')
x=np.tanh(x*1.2);writewav(R/'score-retimed.wav',x)
duck=np.ones(len(x),np.float32);speech=np.zeros_like(x);envs={who:np.zeros(math.ceil(cursor*50)+1) for who in ['阿程','积木']};timing=[]
for s in new:
 if s['speaker'] not in envs:continue
 a=audio_by_id[s['line_id']];start=s['start']+s['voice_lead'];at=int(start*SR);n=len(a);speech[at:at+n,0]+=a*.97;speech[at:at+n,1]+=a
 lo=max(0,at-int(.13*SR));hi=min(len(x),at+n+int(.2*SR));duck[lo:at]=np.minimum(duck[lo:at],np.linspace(1,.25,at-lo));duck[at:at+n]=.25;duck[at+n:hi]=np.minimum(duck[at+n:hi],np.linspace(.25,1,hi-at-n))
 for k in range(int(len(a)/SR*50)):
  chunk=a[int(k*SR/50):int((k+1)*SR/50)];rms=np.sqrt(np.mean(chunk*chunk));envs[s['speaker']][int(start*50)+k]=float(min(1,rms*8))
 timing.append({'line_id':s['line_id'],'speaker':s['speaker'],'start':start,'end':start+len(a)/SR,'source_audio':s['voice_file']})
mix=x*duck[:,None]+speech;peak=np.max(np.abs(mix))
if peak>.89:mix*=.89/peak
mix[:2205]*=np.linspace(0,1,2205)[:,None];mix[-22050:]*=np.linspace(1,0,22050)[:,None];writewav(R/'sound.wav',mix)
(voices/'envelopes.json').write_text(json.dumps({k:v.tolist() for k,v in envs.items()}));(voices/'timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2))
print(json.dumps({'runtime':cursor,'lines':len(timing),'robot_processed':sum(s['speaker']=='积木' for s in new),'peak_dbfs':float(20*np.log10(np.max(np.abs(mix))))},ensure_ascii=False),flush=True)
