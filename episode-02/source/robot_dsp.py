from pathlib import Path
import subprocess,wave
import numpy as np
from scipy.signal import butter,sosfilt
SR=44100


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