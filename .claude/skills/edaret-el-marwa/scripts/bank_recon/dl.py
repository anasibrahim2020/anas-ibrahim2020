import sys, json, base64, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'/tmp/claude-0')
from odoo_client import model, login
uid=login()
items=json.load(open('uniq.json'))
os.makedirs('dl',exist_ok=True)
def get(x):
    p=f"dl/{x['id']}.pdf"
    if os.path.exists(p) and os.path.getsize(p)>0: return 1
    for _ in range(3):
        try:
            a=model(uid,'ir.attachment','read',x['id'],['datas'])
            open(p,'wb').write(base64.b64decode(a[0]['datas'])); return 1
        except Exception as e: err=e
    return 0
with ThreadPoolExecutor(8) as ex: r=list(ex.map(get,items))
print('downloaded',sum(r),'of',len(items))
