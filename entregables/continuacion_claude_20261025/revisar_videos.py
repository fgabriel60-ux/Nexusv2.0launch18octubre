"""Verifica decodificación y prepara hojas de cuadros de los entregables seleccionados."""
from pathlib import Path
import json,subprocess,re
import cv2,imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
VIDEOS={
 'Benjamina':('clientes/Mariano/flyers_animados/Mariano_flyer_Benjamina_v5.mp4',[.2,1,3.5,6.8]),
 'Bugambilia_pareja':('clientes/Mariano/flyers_animados/Mariano_flyer_Bugambilia_v5.mp4',[.2,1,3.5,6.8]),
 'Sotol_familia':('clientes/Mariano/flyers_animados/Mariano_flyer_Sotol_familia_v5.mp4',[.2,1,3.5,6.8]),
 'Bugambilia_mejor_opcion':('clientes/Mariano/flyers_animados/Mariano_flyer_Bugambilia_mejor_opcion_v5.mp4',[.2,1,3.5,6.8]),
 'Pixar':('clientes/Carlos_Nexus/pixar/Pixar_v6_efectos_v2.mp4',[.5,5,8,13.5,16.7,18.6,20.5,23.5,26.5,33]),
 'Dental':('clientes/Alberto/video/Veneers_Dra_Angeles_implantes_estilo_ref_v4.mp4',[.5,3,5,8,11,14,17,20,24,30]),
 'Spiderman':('clientes/Mariano/video/Vizcaino_v5_gancho_spiderman_v2.mp4',[.2,1,2.5,5,8,10.5,13,16.5,19.5,23.5,28,31]),
 'Pajaro':('proyectos/pajaro_mecanico_nitinol/video_realista/pajaro_realista_v1.mp4',[.2,2,4.5,6.5,9,11,13,14.6])}
def main():
    reports={}
    for name,(rel,times) in VIDEOS.items():
        p=ROOT/rel
        if not p.exists():continue
        cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS);n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        assert fps>0 and n>0,rel
        cols=min(5,len(times));rows=(len(times)+cols-1)//cols
        sheet=Image.new('RGB',(cols*240,rows*450),'#202020');draw=ImageDraw.Draw(sheet)
        for i,t in enumerate(times):
            cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read();assert ok,(name,t)
            im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)).resize((240,426));xy=((i%cols)*240,(i//cols)*450)
            sheet.paste(im,(xy[0],xy[1]+24));draw.text(xy,f'{name} {t}s',fill='white')
        sheet.save(OUT/'revisiones'/f'{name}.jpg')
        dims=[int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))];cap.release()
        check=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
        assert check.returncode==0 and not check.stderr,(name,check.stderr)
        meta=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
        assert 'h264 (Main)' in meta,(name,meta[:600])
        assert 'Audio: aac' in meta,(name,'sin audio AAC')
        assert p.stat().st_size<16_000_000,(name,'supera 16 MB')
        reports[name]={'archivo':rel,'dimensiones':dims,'fps':fps,'duracion_s':round(n/fps,3),'MB':round(p.stat().st_size/1e6,3),'decodificacion':'OK','video':'H264 Main','audio':'AAC'}
        print(name,reports[name],flush=True)
    (OUT/'validacion.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
