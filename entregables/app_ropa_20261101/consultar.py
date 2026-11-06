import base64,json,sys,urllib.request,time
U='https://carlosfavelajeje--glimmer-chat-glimmer-web.us-east.modal.run/chat'
K=open('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/4272cf5c-0fc4-4477-ba34-d486da84e965/scratchpad/clave.txt').read().strip()
fotos=[base64.b64encode(open(f,'rb').read()).decode() for f in ['DZd00LrsCGQ_hoja.jpg','DJ4nXYLhl8D_hoja.jpg']]
for n in sys.argv[1:]:
    t0=time.time()
    body={'mensajes':[{'rol':'user','texto':open(f'prompt_{n}.txt').read(),'fotos':fotos}],'tokens':6000}
    r=urllib.request.Request(U,data=json.dumps(body).encode(),headers={'content-type':'application/json','x-clave':K})
    j=json.loads(urllib.request.urlopen(r,timeout=1500).read())
    open(f'glimmer_{n}.md','w').write(j['respuesta']); print(n,round(time.time()-t0),'s',len(j['respuesta']),flush=True)
