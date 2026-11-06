"""Consulta de solo lectura del supervisor y actividad de Codex en Modal."""
import json
import os
os.environ['MODAL_PROFILE'] = 'carlosfavelajeje'
import modal
sb = modal.Sandbox.from_name('nexus-chatgpt-noche', 'chatgpt-noche')
code = r'''
import json,os,subprocess
from pathlib import Path
d=Path('/workspaces/Nexusv2.0launch18octubre/entregables/chatgpt_modal_noche_20261101')
out={'supervisor':json.loads((d/'supervisor_estado.json').read_text()) if (d/'supervisor_estado.json').exists() else None}
out['herramientas']={k:bool(os.environ.get(k)) for k in ['FISH_API_KEY','WAAPI_TOKEN','MODAL_TOKEN_ID']}
out['token_modal_guardado']=Path('/vol/claude-config/modal-carlosfavelajeje.env').is_file()
out['archivos_workspace']=len(list(Path('/workspaces/Nexusv2.0launch18octubre').iterdir()))
out['codex_version']=subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip()
out['login']=subprocess.run(['codex','login','status'],capture_output=True,text=True).stderr.strip()[:300]
out['logs']=[]
for f in sorted(d.glob('*_intento_*.jsonl')):
 events=[]
 for line in f.read_text(errors='replace').splitlines():
  try: events.append(json.loads(line))
  except ValueError: pass
 commands=[x for x in events if x.get('item',{}).get('type')=='command_execution']
 messages=[x['item']['text'] for x in events if x.get('item',{}).get('type')=='agent_message' and x.get('item',{}).get('text')]
 errors=[x for x in events if x.get('type') in ['error','turn.failed']]
 out['logs'].append({'archivo':f.name,'bytes':f.stat().st_size,'comandos':len(commands),'ultimo_mensaje':messages[-1][:1400] if messages else None,'errores':errors[-2:]})
print(json.dumps(out,ensure_ascii=False,indent=2))
'''
p = sb.exec('python3', '-c', code, timeout=30)
print('sandbox', sb.object_id)
print(p.stdout.read())
err = p.stderr.read()
if err:
    print(err[:1000])
print('consulta_rc', p.wait())
