import sys, json, re
sys.path.insert(0,'/tmp/claude-0')
from odoo_client import model, login
uid=login()
atts=model(uid,'ir.attachment','search_read',[['res_model','=','account.move'],['mimetype','=','application/pdf'],['create_date','>=','2026-04-01']],fields=['id','name','res_id','file_size','create_date'])
print('pdfs since Apr:',len(atts))
mids=list({a['res_id'] for a in atts}); jr={}
for i in range(0,len(mids),300):
    for m in model(uid,'account.move','read',mids[i:i+300],['journal_id']):
        jr[m['id']]=m['journal_id'][1] if m['journal_id'] else ''
cands=[]
for a in atts:
    j=jr.get(a['res_id'],'')
    if j in ('Vendor Bills','Customer Invoices'): continue
    if re.search(r'\d{2}[-/ ]\d{2}[-/ ]20\d{2}',a['name']) or re.match(r'\d{3}-',a['name']) or 'QNB' in a['name'].upper() or 'QIB' in a['name'].upper():
        cands.append({'id':a['id'],'name':a['name'],'journal':j,'size':a['file_size']})
print('candidates:',len(cands), 'total MB', round(sum(c['size'] or 0 for c in cands)/1e6,1))
json.dump(cands,open('cands.json','w'),ensure_ascii=False)
from collections import Counter
print(Counter(c['journal'][:30] for c in cands).most_common(20))
