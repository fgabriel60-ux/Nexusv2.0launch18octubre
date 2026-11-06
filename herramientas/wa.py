import json,os,urllib.request,time
# Si las variables no están en el entorno, las carga del .env de la raíz del workspace (sin imprimirlas).
if 'WAAPI_INSTANCE' not in os.environ or 'WAAPI_TOKEN' not in os.environ:
    _env=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','.env')
    if os.path.exists(_env):
        for _l in open(_env):
            if '=' in _l and not _l.lstrip().startswith('#'):
                _k,_v=_l.split('=',1); os.environ.setdefault(_k.strip(),_v.strip().strip('"\''))
B='https://waapi.app/api/v1/instances/'+os.environ['WAAPI_INSTANCE']
def accion(a,body):
    for i in range(4):
        try:
            r=urllib.request.Request(B+'/client/action/'+a,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+os.environ['WAAPI_TOKEN'],'Content-Type':'application/json'})
            with urllib.request.urlopen(r,timeout=120) as x: return json.load(x)
        except Exception as e: print('reint',a,e); time.sleep(8)
