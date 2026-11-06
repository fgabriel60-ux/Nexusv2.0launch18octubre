from pathlib import Path
import json,base64,shutil
from PIL import Image
from collections import Counter,defaultdict
import numpy as np
from scipy.spatial import Delaunay
r=Path('entregables/implante_dental/rostro_assets')
pts=json.loads((r/'landmarks.json').read_text())['points'][:468]
faces=[]
for l in (r/'canonical_face_model.obj').read_text().splitlines():
 if l.startswith('f '):faces.append([int(s.split('/')[0])-1 for s in l.split()[1:]])
inner_mouth={78,95,88,178,87,14,317,402,318,324,308,415,310,311,312,13,82,81,80,191}
removed=[f for f in faces if all(i in inner_mouth for i in f)]
faces=[f for f in faces if not all(i in inner_mouth for i in f)]
print('mouth cap triangles removed',len(removed))
# Canonical surface preserves the lip opening. Close only the eye holes with photographic surface patches.
edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
adj=defaultdict(list)
for (a,b),n in edges.items():
 if n==1:adj[a].append(b);adj[b].append(a)
loops=[];seen=set()
for start in adj:
 if start in seen:continue
 loop=[];cur=start;prev=None
 while cur not in seen:
  loop.append(cur);seen.add(cur);nxt=[x for x in adj[cur] if x!=prev];prev,cur=cur,nxt[0]
 loops.append(loop)
print('Boundary loops',[(len(l),round(sum(pts[i][1] for i in l)/len(l),3)) for l in loops])
for loop in loops:
 cy=sum(pts[i][1] for i in loop)/len(loop)
 if .20<cy<.5 and len(loop)<30:
  center=np.mean([pts[i] for i in loop],axis=0).tolist();idx=len(pts);pts.append(center)
  faces += [[loop[j],loop[(j+1)%len(loop)],idx] for j in range(len(loop))]
W,H=941,1672;S=.017;cx,cy=550,947
verts=[[(u*W-cx)*S,z*W*S+.5,(cy-v*H)*S] for u,v,z in pts]
uvs=[[u,1-v] for u,v,z in pts]
data={'vertices':verts,'uv':uvs,'faces':faces,'scale_per_pixel':S,'photo_size':[W,H],'origin_pixel':[cx,cy]}
(r/'face_mesh.json').write_text(json.dumps(data))
source=Path('visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/clientes/Vision Agencia/veneers_dental/last_frame_diente_faltante.png')
shutil.copyfile(source,r/'CHICA_ALBEDO.png')
# OBJ with a usable UV texture, independent of Blender.
with (r/'CHICA_ROSTRO.obj').open('w') as f:
 f.write('mtllib CHICA_ROSTRO.mtl\no CHICA_ROSTRO\n')
 for v in verts:f.write('v '+' '.join(map(str,v))+'\n')
 for uv in uvs:f.write('vt '+' '.join(map(str,uv))+'\n')
 f.write('usemtl CHICA_PIEL\n')
 for face in faces:f.write('f '+' '.join(f'{i+1}/{i+1}' for i in face)+'\n')
(r/'CHICA_ROSTRO.mtl').write_text('newmtl CHICA_PIEL\nKd 1 1 1\nmap_Kd CHICA_ALBEDO.png\n')
print('mesh',len(verts),len(faces))
# Photo-textured surrounding hair/neck context, separate from the editable face surface.
outer=max(loops,key=len)
uvpoints=[[pts[i][0],pts[i][1]] for i in outer]
for t in np.linspace(0,1,22):uvpoints.extend([[float(t),0],[float(t),1],[0,float(t)],[1,float(t)]])
uvpoints=np.unique(np.array(uvpoints),axis=0)
tri=Delaunay(uvpoints)
poly=np.array([[pts[i][0],pts[i][1]] for i in outer])
def inside(x,y):
 flag=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if ((yi>y)!=(yj>y)) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:flag=not flag
  j=i
 return flag
contextfaces=[f.tolist() for f in tri.simplices if not inside(*np.mean(uvpoints[f],axis=0))]
contextverts=[]
for u,v in uvpoints:
 d,idx=min(((u-pts[i][0])**2+(v-pts[i][1])**2,i) for i in outer)
 depth=verts[idx][1] if d<1e-10 else 8
 contextverts.append([(u*W-cx)*S,depth,(cy-v*H)*S])
data['context']={'vertices':contextverts,'faces':contextfaces,'uv':[[float(u),float(1-v)] for u,v in uvpoints]}
data['outer']=outer
(r/'face_mesh.json').write_text(json.dumps(data))
