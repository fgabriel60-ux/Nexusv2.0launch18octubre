"""Pista sintética moderna (126 BPM) para el spot LED: bombo, hi-hat, bajo y acordes."""
import numpy as np
from scipy.io import wavfile
sr=44100; bpm=126; dur=31; beat=60/bpm
n=int(sr*dur); out=np.zeros(n)
def add(t0,x,g=1):
    i=int(t0*sr); x=x[:max(0,n-i)]; out[i:i+len(x)]+=x*g
t=np.arange(int(sr*.3))/sr
kick=np.sin(2*np.pi*(50+110*np.exp(-t*30))*t)*np.exp(-t*9)
th=np.arange(int(sr*.08))/sr
hat=np.random.default_rng(1).standard_normal(len(th))*np.exp(-th*60); hat=np.diff(hat,prepend=0)
clap=np.random.default_rng(2).standard_normal(int(sr*.15))*np.exp(-np.arange(int(sr*.15))/sr*28)
def tone(f,d,sh=0.5):
    tt=np.arange(int(sr*d))/sr
    w=np.sign(np.sin(2*np.pi*f*tt))*0.5+np.sin(2*np.pi*f*tt)
    return w*np.minimum(1,tt*40)*np.exp(-tt*sh*4)
roots=[55,43.65,49,41.2]  # A F G E (bajo)
chords=[[220,277.2,329.6],[174.6,220,261.6],[196,246.9,293.7],[164.8,207.7,246.9]]
nb=int(dur/beat)
for b in range(nb):
    T=b*beat; bar=(b//4)%4
    if b%1==0: add(T,kick,1.0)
    add(T+beat/2,hat,.35)
    if b%2==1: add(T,clap,.5)
    add(T+beat*.5,tone(roots[bar]*2,beat*.4),.35)
    add(T,tone(roots[bar],beat*.9),.5)
for bar in range(int(dur/(4*beat))):
    for f in chords[bar%4]: add(bar*4*beat,tone(f,4*beat,.15),.09)
out/=np.abs(out).max(); 
fade=np.minimum(1,np.minimum(np.arange(n)/(sr*1.0),(n-np.arange(n))/(sr*2.0)))
wavfile.write('musica.wav',sr,(out*fade*32000).astype(np.int16))
