"""Assemble already-generated authorized local takes. Never calls a provider."""
from pathlib import Path
import json,wave
import numpy as np
from robot_dsp import decode,writewav,robotize
ROOT=Path(__file__).resolve().parent.parent;SR=44100
shots=json.loads((ROOT/'source/storyboard.json').read_text())['shots'];needed=[(s,d) for s in shots for d in s['dialogue']]
missing=[f"e02-line-{s['shot']:02}.mp3" for s,d in needed if not (ROOT/'voices'/f"e02-line-{s['shot']:02}.mp3").exists()]
if missing:raise SystemExit('Awaiting authorized local voice takes: '+', '.join(missing))
import render_episode
render_episode.score()
with wave.open(str(ROOT/'output/full-visual-sound.wav'),'rb') as w:bg=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32).reshape(-1,2)/32768
voice=np.zeros_like(bg);duck=np.ones(len(bg));env={who:np.zeros(78*50) for who in ['阿程','积木']};timings=[]
(ROOT/'voices/processed').mkdir(exist_ok=True)
for s,d in needed:
 name=f"e02-line-{s['shot']:02}";src=ROOT/'voices'/f'{name}.mp3'
 if d['speaker']=='积木':
  processed=ROOT/'voices/processed'/f'{name}-robot.wav';robotize(src,processed);src=processed
 a=decode(src);nz=np.flatnonzero(np.abs(a)>.0015)
 if len(nz):a=a[max(0,nz[0]-int(.06*SR)):min(len(a),nz[-1]+int(.12*SR))]
 a*=.67/max(float(np.max(np.abs(a))),1e-9);start=s['start']+.28;end=start+len(a)/SR
 if end>s['end']-.15:raise SystemExit(f'{name} exceeds shot; retime before rendering, never truncate')
 at=int(start*SR);n=len(a);voice[at:at+n,0]+=a*.97;voice[at:at+n,1]+=a
 lo=max(0,at-int(.13*SR));hi=min(len(bg),at+n+int(.2*SR));duck[lo:at]=np.minimum(duck[lo:at],np.linspace(1,.25,at-lo));duck[at:at+n]=.25;duck[at+n:hi]=np.minimum(duck[at+n:hi],np.linspace(.25,1,hi-at-n))
 for k in range(int(len(a)/SR*50)):
  chunk=a[int(k*SR/50):int((k+1)*SR/50)];env[d['speaker']][int(start*50)+k]=float(min(1,np.sqrt(np.mean(chunk*chunk))*8))
 timings.append({'shot':s['shot'],'speaker':d['speaker'],'text':d['text'],'start':start,'end':end,'file':str(src.relative_to(ROOT/'voices'))})
mix=bg*duck[:,None]+voice;p=float(np.max(np.abs(mix)))
if p>.89:mix*=.89/p
writewav(ROOT/'output/voiced-mix.wav',mix);(ROOT/'voices/envelopes.json').write_text(json.dumps({k:v.tolist() for k,v in env.items()}));(ROOT/'voices/timing.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2))
print('Mixed',len(timings),'takes; no API calls')
