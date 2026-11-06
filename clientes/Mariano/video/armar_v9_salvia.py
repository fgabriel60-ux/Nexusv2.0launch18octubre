"""Mariano v7 (31 oct): gancho v6 (marometa MiniMax + aterrizaje + habla) → recorrido premium Salvia (7 tomas MiniMax L40S, escenas largas) → cierre de v2."""
import subprocess
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
G=10.54
SV=['SV1_fachada','SV2_sala','SV3_comedor','SV5_estancia','SV6_recamara','SV4_cocina','SV7_terraza']
lab=['Salvia · Vizcaíno Residencial','Sala','Comedor','Estancia familiar','Recámara principal','Vista a las amenidades','Roof garden']
D=2.5; T2=D*len(SV); C0=26.53
inp=['-i','Vizcaino_v5_gancho_spiderman_v6b.mp4']+sum([['-i',f'salvia_premium/salida/{s}_v.mp4'] for s in SV],[])+['-i','Vizcaino_v5_gancho_spiderman_v2.mp4','-i','/workspaces/Nexusv2.0launch18octubre/entregables/prospectos_sancarlos_20261031/musica/villa_s3.wav','-i','spiderman/voz/salvia.wav','-i','spiderman/voz/privada.wav']
n=len(SV); fc=f"[0:v]trim=0:{G},setpts=PTS-STARTPTS,fps=30,setsar=1[g];"
for i in range(n):
    fc+=f"[{i+1}:v]trim=0.1:{0.1+D},setpts=PTS-STARTPTS,scale=720:1280,fps=30,setsar=1,drawtext=fontfile={F}:text='{lab[i]}':fontsize=40:fontcolor=white:borderw=4:bordercolor=black@0.6:x=(w-text_w)/2:y=h*0.80[s{i}];"
fc+=f"[{n+1}:v]trim={C0},setpts=PTS-STARTPTS,fps=30,setsar=1[c];"
fc+="[g]"+''.join(f'[s{i}]' for i in range(n))+"[c]concat=n="+str(n+2)+":v=1:a=0,drawtext=fontfile="+F+f":text='SALVIA · 4 recámaras · desde $3.1 MDP':fontsize=27:fontcolor=white:box=1:boxcolor=black@0.45:boxborderw=12:x=(w-text_w)/2:y=h*0.12:enable='between(t,{G},{G+T2})'[v];"
fc+=f"[0:a]atrim=0:{G},asetpts=PTS-STARTPTS[a0];[{n+2}:a]atrim=0:{T2},volume=0.25,afade=t=in:d=0.3,afade=t=out:st={T2-0.4}:d=0.4[mu];[{n+3}:a]atrim=0.13,asetpts=PTS-STARTPTS,adelay=500|500,volume=1.3[v1];[{n+4}:a]adelay=6800|6800,volume=1.3[v2];[mu][v1][v2]amix=inputs=3:normalize=0:duration=first[a1];[{n+1}:a]atrim={C0},asetpts=PTS-STARTPTS[a2];[a0][a1][a2]concat=n=3:v=0:a=1[a]"
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',fc,'-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','Vizcaino_Mariano_v9_salvia_premium.mp4'],check=True)
