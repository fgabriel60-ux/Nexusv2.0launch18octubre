import subprocess
S='spiderman/'; F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
V=1.4; M=6.08/V; L=0.65; H=M+L; D=H-1.6
W=[(1.60,3.42,'¿Buscas casa en Rosarito?'),(3.96,5.30,'Vizcaíno Residencial'),(5.70,6.40,'¡Mira esto!')]
subs=','.join(f"drawtext=fontfile={F}:text='{w}':fontsize=44:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=h*0.70:enable='between(t,{a+D:.2f},{e+D+0.1:.2f})'" for a,e,w in W)
fc=(f"[0:v][1:v]concat=n=2:v=1:a=0,setpts=PTS/{V},scale=720:1280,fps=30,setsar=1[f];"
 f"[2:v]trim=2.95:{2.95+L},setpts=PTS-STARTPTS,scale=720:1280,fps=30,setsar=1,fade=t=in:st=0:d=0.12:color=white[l];"
 "[3:v]trim=0:5.17,setpts=PTS-STARTPTS,scale=720:1280,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=0.5,trim=0:5.55[h];"
 "[4:v]trim=7.15,setpts=PTS-STARTPTS,scale=720:1280,fps=30,setsar=1[c];"
 f"[f][l][h][c]concat=n=4:v=1:a=0,{subs}[v];"
 f"[4:a]atrim=1.6,asetpts=PTS-STARTPTS,adelay={int(H*1000)}|{int(H*1000)}[vo];"
 f"[4:a]atrim=0:1.5,asetpts=PTS-STARTPTS,aloop=loop=3:size=66150,atrim=0:{H},afade=t=out:st={H-0.3}:d=0.3,volume=0.6[intro];"
 f"[5:a]adelay=600|600,volume=0.9[w1];[5:a]adelay=2600|2600,volume=0.8[w2];[6:a]adelay={int(M*1000)}|{int(M*1000)},volume=1.1[g];"
 "[intro][w1][w2][g][vo]amix=inputs=5:normalize=0:duration=longest[a]")
subprocess.run(['ffmpeg','-v','error','-y','-i',S+'r6/salida/KT1_salto.mp4','-i',S+'r6/salida/KT2_cae.mp4','-i',S+'r4v/S_salto.mp4','-i',S+'r4v/S_habla.mp4','-i','Vizcaino_v5_gancho_spiderman_v2.mp4','-i','/workspaces/Nexusv2.0launch18octubre/clientes/Guillermo/video/sfx/whoosh.wav','-i','/workspaces/Nexusv2.0launch18octubre/clientes/Guillermo/video/sfx/golpe.wav','-filter_complex',fc,
 '-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','Vizcaino_v5_gancho_spiderman_v6b.mp4'],check=True)
