"""Assemble only a complete 1050-frame render, preserving the existing narration."""
from pathlib import Path
import subprocess, sys
base=Path(__file__).resolve().parent
frames=base/(sys.argv[1] if len(sys.argv)>1 else 'final_v2')
missing=[f for f in range(1,1051) if not (frames/('frame_%04d.png'%f)).is_file()]
if missing:raise SystemExit('Render incompleto: faltan %d cuadros; primero %s'%(len(missing),missing[:8]))
out=base/'IMPLANTE_DENTAL_PARA_ALBERTO.mp4'
subprocess.run(['ffmpeg','-y','-framerate','30','-start_number','1','-i',str(frames/'frame_%04d.png'),'-i',str(base.parent/'voz_fish/IMPLANTE_VOZ_35s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af','apad','-t','35','-movflags','+faststart',str(out)],check=True)
print(out)
