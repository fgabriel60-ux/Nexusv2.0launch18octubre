"""Envía una vez los ocho videos a Carlos al reconectarse WhatsApp. Autorizado en el chat."""
import argparse,base64,json,time,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
REC=OUT/'recibos_whatsapp.json'
DESTINO='44522318905388@lid'  # Chat consigo mismo de Carlos, registrado en el proyecto.
def env():
    d={}
    for line in (ROOT/'.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1);d[k.strip()]=v.strip().strip('\"\'')
    return d
E=env();BASE=E.get('WAAPI_BASE','https://waapi.app/api/v1').rstrip('/')+'/instances/'+E['WAAPI_INSTANCE']
def call(path,body=None):
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers={'Authorization':'Bearer '+E['WAAPI_TOKEN'],'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=300) as r:return json.load(r)
def find(obj,key):
    if isinstance(obj,dict):
        if key in obj:return obj[key]
        for v in obj.values():
            r=find(v,key)
            if r is not None:return r
    if isinstance(obj,list):
        for v in obj:
            r=find(v,key)
            if r is not None:return r
    return None
def failures(obj):
    if isinstance(obj,dict):
        if obj.get('status')=='error':return obj.get('message','error')
        for v in obj.values():
            r=failures(v)
            if r:return r
    if isinstance(obj,list):
        for v in obj:
            r=failures(v)
            if r:return r
    return None
def save(d):
    tmp=REC.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2));tmp.replace(REC)
def main(wait):
    videos=json.loads((OUT/'validacion.json').read_text())
    assert len(videos)==8
    for row in videos.values():
        p=ROOT/row['archivo'];assert p.is_file() and p.stat().st_size<16_000_000,p
    receipt=json.loads(REC.read_text()) if REC.exists() else {'destino':DESTINO,'piezas':{},'estado':'esperando_conexion'}
    save(receipt);deadline=time.monotonic()+wait;last=None
    while True:
        state=find(call('/client/status'),'instanceStatus')
        if state!=last:print('Conexión:',state,flush=True);last=state
        if state=='ready':break
        if time.monotonic()>=deadline:
            receipt['estado']='pendiente_reconectar';save(receipt);print('Terminó la espera. No se enviaron videos pendientes.',flush=True);return
        time.sleep(15)
    for i,(name,row) in enumerate(videos.items(),1):
        if name in receipt['piezas']:
            if receipt['piezas'][name].get('estado')=='aceptado':continue
            raise RuntimeError('Un envío anterior requiere verificar antes de repetir: '+name)
        p=ROOT/row['archivo']
        receipt['piezas'][name]={'estado':'en_proceso','archivo':row['archivo'],'inicio':datetime.now(timezone.utc).isoformat()};save(receipt)
        try:
            response=call('/client/action/send-media',{'chatId':DESTINO,'mediaBase64':base64.b64encode(p.read_bytes()).decode(),'mediaName':p.name,'mediaCaption':f'{i}/8 · '+name.replace('_',' '),'asDocument':False})
            error=failures(response)
            if error:raise RuntimeError(error)
            receipt['piezas'][name].update({'estado':'aceptado','respuesta':response,'fecha':datetime.now(timezone.utc).isoformat()});save(receipt)
            print('Aceptado:',name,flush=True)
        except Exception as exc:
            receipt['estado']='verificar_envio';receipt['piezas'][name]['estado']='requiere_verificar';receipt['piezas'][name]['error']=str(exc);save(receipt)
            raise
        time.sleep(5)
    receipt['estado']='ocho_aceptados';save(receipt);print('Los ocho videos fueron aceptados por WhatsApp.',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wait',type=int,default=600);main(p.parse_args().wait)
