"""Anuncio Visión para dueños de villas. Reutiliza tomas pagadas; no genera escenas."""
from pathlib import Path
import difflib,json,os,re,subprocess,unicodedata,urllib.request,wave
import av,imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
FF=imageio_ffmpeg.get_ffmpeg_exe()
SRC=ROOT/'entregables/prospectos_sancarlos_20261031/villabahia_3c/salida'
FOTOS=ROOT/'entregables/prospectos_sancarlos_20261031/casago_1043362'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def run(args):subprocess.run([FF,'-v','error','-y',*map(str,args)],check=True)
def duration(path):
    with av.open(str(path)) as v:return v.duration/1e6
def norm(s):
    s=unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()
    s=s.replace('whats app','whatsapp').replace('uatsap','whatsapp')
    for n,w in [('500','quinientos'),('250','doscientos cincuenta'),('10','diez'),('8','ocho')]:s=re.sub(r'\b'+n+r'\b',w,s)
    return re.sub(r'[^a-z ]','',s).split()
def loadenv():
    for line in (ROOT/'.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip().strip('\"').strip("'"))
def transcribe(model,path):
    raw=subprocess.run([FF,'-v','error','-i',str(path),'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout
    segs,_=model.transcribe(np.frombuffer(raw,np.int16).astype(np.float32)/32768,language='es',word_timestamps=True,vad_filter=True)
    segments=list(segs);return {'texto':' '.join(s.text.strip() for s in segments),'palabras':[{'word':w.word.strip(),'start':w.start,'end':w.end} for s in segments for w in s.words]}
def voice(script):
    loadenv();from faster_whisper import WhisperModel
    model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
    takes=[]
    for i in range(4):
        dest=OUT/f'voz_toma_{i+1}.wav'
        if not dest.exists():
            req=urllib.request.Request('https://api.fish.audio/v1/tts',data=json.dumps({'text':script,'format':'wav','reference_id':'1f679152b5d64c09a8e8eeecd3eb5424'}).encode(),headers={'Authorization':'Bearer '+os.environ['FISH_API_KEY'],'Content-Type':'application/json','model':'s2-pro'})
            with urllib.request.urlopen(req,timeout=90) as response:dest.write_bytes(response.read())
        result=transcribe(model,dest);ratio=difflib.SequenceMatcher(None,norm(script),norm(result['texto'])).ratio()
        takes.append({'ruta':str(dest),'coincidencia':ratio,**result});print('toma',i+1,round(ratio,4),result['texto'],flush=True)
    (OUT/'tomas_whisper.json').write_text(json.dumps(takes,ensure_ascii=False,indent=2))
    choice=max(takes,key=lambda x:x['coincidencia'])
    if choice['coincidencia']<.98:raise RuntimeError('La voz no coincide con el guion. Revisar tomas_whisper.json antes de montar.')
    (OUT/'voz_elegida.json').write_text(json.dumps(choice,ensure_ascii=False,indent=2));return choice,model
def ass_time(t):
    cent=round(t*100);return f'{cent//360000}:{cent//6000%60:02}:{cent//100%60:02}.{cent%100:02}'
def build(script,choice):
    T=duration(choice['ruta'])+.65
    cuts=[('VBT1_aereo.mp4',1.3),('foto',1.2),('VBT4_sala.mp4',2.6),('balconfoto',1.1),('VBT3_balcon.mp4',2.6),('VBT2_alberca.mp4',2.1),('VBT5_cocina.mp4',1.7),('VBT6_recamara.mp4',1.7),('VBT7_terraza.mp4',2.4),('VBT2_alberca.mp4',2.4),('VBT3_balcon.mp4',2.6),('VBT4_sala.mp4',max(2.5,T-21.7))]
    accumulated=0;files=[]
    for i,(file,sec) in enumerate(cuts):
        out=OUT/f'segmento_{i:02}.mp4'
        if file in ['foto','balconfoto']:
            original=FOTOS/('14.jpg' if file=='foto' else '09.jpg')
            im=Image.new('RGB',(720,1280),'#142630');photo=ImageOps.contain(Image.open(original).convert('RGB'),(664,790));im.paste(photo,((720-photo.width)//2,(1280-photo.height)//2));d=ImageDraw.Draw(im);d.text((360,300),'LA FOTO ORIGINAL',font=ImageFont.truetype(FONT,33),anchor='mm',fill='#f3dca3');png=OUT/f'foto_{i}.png';im.save(png)
            inp=['-loop','1','-i',png]
            vf='scale=720:1280,setsar=1,fps=30,format=yuv420p'
        else:
            inp=['-stream_loop','-1','-ss','0.25','-i',SRC/file]
            vf='scale=720:1280,setsar=1,fps=30,format=yuv420p'
        run([*inp,'-t',sec,'-an','-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','20','-threads','2',out]);files.append(out);accumulated+=sec
    concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(p)+"'" for p in files))
    base=OUT/'base_v1.mp4';run(['-f','concat','-safe','0','-i',concat,'-c','copy',base])
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,38,&H00FFFFFF,&H00FFFFFF,&H00201510,&H90201510,-1,0,0,0,100,100,0,0,1,3,1,2,65,65,225,1
Style: Head,DejaVu Sans,47,&H00FFFFFF,&H00FFFFFF,&H00201510,&H80201510,-1,0,0,0,100,100,0,0,1,3,1,8,60,60,175,1
Style: Label,DejaVu Sans,23,&H00D3EDE2,&H00FFFFFF,&H00201510,&H80201510,-1,0,0,0,100,100,2,0,1,2,0,8,40,40,105,1
Style: Offer,DejaVu Sans,49,&H00FFFFFF,&H00FFFFFF,&H00201510,&H80201510,-1,0,0,0,100,100,0,0,3,18,0,5,50,50,0,1
Style: Small,DejaVu Sans,28,&H00D3EDE2,&H00FFFFFF,&H00201510,&H80201510,-1,0,0,0,100,100,0,0,1,3,0,8,50,50,290,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events=[]
    def add(start,end,style,text,layer=0):events.append(f'Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}')
    add(0,T,'Label','VISIÓN AGENCIA   /   MUESTRA ILUSTRATIVA')
    add(0,5.1,'Head','DUEÑOS DE VILLAS\\N¿RENTAS TU PROPIEDAD?')
    add(2.5,5.1,'Small','DE TUS FOTOS → A UN RECORRIDO')
    add(6.2,min(16,T-8),'Head','IA DE FACEBOOK\\NBUSCAMOS UNA CALIFICACIÓN DE 8/10')
    add(min(16,T-8),max(17,T-5),'Head','APLÍCALO ANTES\\NQUE TU COMPETENCIA')
    offer_start=min(12,T-11)
    offer_end=T-5
    add(offer_start,offer_end,'Offer','VIDEOS + ESTRATEGIA\\N$500 MXN / MES\\N{\\fs28}Pauta de Meta aparte · desde $250 MXN/mes')
    add(max(offer_end,T-6),T,'Head','¿TIENES UNA VILLA?\\NESCRIBE «VILLA» + TU CIUDAD')
    add(max(offer_end,T-6),T,'Offer','{\\pos(360,720)\\fs48}631 247 0486\\N{\\fs30}WhatsApp · Mándame 3 fotos')
    words=choice['palabras'];original_words=script.split()
    # Voz verificada; mostrar guion original en grupos legibles, con tiempos de Whisper.
    recognized=[norm(w['word']) for w in words]
    flat=[(token,i) for i,ts in enumerate(recognized) for token in ts]
    source_tokens=[(token,i) for i,w in enumerate(original_words) for token in norm(w)]
    mapping={}
    for block in difflib.SequenceMatcher(None,[x[0] for x in source_tokens],[x[0] for x in flat]).get_matching_blocks():
        for n in range(block.size):mapping[source_tokens[block.a+n][1]]=flat[block.b+n][1]
    for start in range(0,len(original_words),4):
        group=original_words[start:start+4];indices=[mapping[i] for i in range(start,min(start+4,len(original_words))) if i in mapping]
        if not indices:continue
        a=words[min(indices)]['start'];b=words[max(indices)]['end']+.12
        add(a,b,'Sub',' '.join(group),1)
    ass=OUT/'subtitulos_v1.ass';ass.write_text(header+'\n'.join(events)+'\n')
    music=ROOT/'entregables/prospectos_sancarlos_20261031/musica/villa_s3.wav'
    out=OUT/'Vision_duenos_villas_v1.mp4'
    run(['-i',base,'-i',choice['ruta'],'-stream_loop','-1','-i',music,'-filter_complex',f"[0:v]ass='{ass}'[v];[1:a]apad,volume=1.3[voz];[2:a]volume=0.07,afade=t=out:st={T-1}:d=1[m];[voz][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",'-map','[v]','-map','[a]','-t',T,'-c:v','libx264','-profile:v','main','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-threads','2','-c:a','aac','-b:a','128k','-movflags','+faststart',out])
    return out
def main():
    script=(OUT/'guion.txt').read_text().strip()
    if (OUT/'voz_elegida.json').exists():
        choice=json.loads((OUT/'voz_elegida.json').read_text());from faster_whisper import WhisperModel
        model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
    else:choice,model=voice(script)
    out=build(script,choice);result=transcribe(model,out);(OUT/'video_final_whisper.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('FINAL',out,'segundos',duration(out),'MB',out.stat().st_size/1e6,flush=True)
if __name__=='__main__':main()
