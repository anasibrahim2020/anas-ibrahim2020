import sys, json, datetime
from collections import defaultdict
sys.path.insert(0,'/tmp/claude-0')
from odoo_client import model, login
uid=login()
P=json.load(open('parsed.json'))
# --- integrity of each parsed pdf
bad=[p for p in P if not p['tx'] or p['close'] is None or abs(p['tx'][-1]['bal']-p['close'])>0.01]
print('integrity issues:',len(bad),[ (b['name'],b['key']) for b in bad[:6]])
J={b['code']:b for b in model(uid,'account.journal','search_read',[['type','=','bank']],fields=['id','code','name','default_account_id'])}
KEY2J={'207':'QIB',**{f'{k:03d}':f'QN{k:03d}' for k in (1,2,3,4,5,6,7,8,9,11,12)}}
def c(x): return int(round(x*100))
res={}
for key,jc in KEY2J.items():
    acct=J[jc]['default_account_id'][0]
    # unique bank txns
    seen=set(); txs=[]
    for p in P:
        if p['key']!=key: continue
        for t in p['tx']:
            if t['amt'] is None: continue
            k=(t['date'],c(t['amt']),c(t['bal']))
            if k in seen: continue
            seen.add(k); txs.append(dict(t))
    # chains by balance linkage
    start_map=defaultdict(list)
    for t in txs: start_map[c(t['bal'])-c(t['amt'])].append(t)
    endbals={c(t['bal']) for t in txs}
    heads=[t for t in txs if (c(t['bal'])-c(t['amt'])) not in endbals]
    used=set(); chains=[]
    def follow(h):
        ch=[h]; used.add(id(h)); cur=h
        while True:
            nxt=[x for x in start_map.get(c(cur['bal']),[]) if id(x) not in used]
            if not nxt: break
            nxt.sort(key=lambda x:x['date']); cur=nxt[0]; used.add(id(cur)); ch.append(cur)
        return ch
    for h in sorted(heads,key=lambda x:x['date']): chains.append(follow(h))
    # leftovers (cycles etc.)
    left=[t for t in txs if id(t) not in used]
    cov=[]
    for ch in chains:
        cov.append({'from':ch[0]['date'],'to':ch[-1]['date'],'open':round((c(ch[0]['bal'])-c(ch[0]['amt']))/100,2),'close':ch[-1]['bal'],'n':len(ch)})
    # merge chains that are contiguous by balance already handled; sort
    cov.sort(key=lambda x:x['from'])
    # odoo lines
    ol=model(uid,'account.move.line','search_read',[['account_id','=',acct],['parent_state','=','posted'],['date','>=','2026-04-01']],fields=['date','name','debit','credit','move_name','ref','create_uid'])
    obal_before={}
    allb=model(uid,'account.move.line','search_read',[['account_id','=',acct],['parent_state','=','posted']],fields=['date','balance'])
    def odoo_bal(upto,strict=False):
        return round(sum(l['balance'] for l in allb if (l['date']<upto if strict else l['date']<=upto)),2)
    res[key]={'journal':jc,'acct':acct,'cov':cov,'n_tx':len(txs),'n_left':len(left),'txs':txs,'ol':ol,
              'odoo_bal':{ },'odoo_last_date':max((l['date'] for l in allb),default=None)}
    for cv in cov:
        res[key]['odoo_bal']['o:'+cv['from']]=odoo_bal(cv['from'],True)
        res[key]['odoo_bal']['c:'+cv['to']]=odoo_bal(cv['to'])
    res[key]['odoo_bal_now']=odoo_bal('2099-01-01')
    print(key,jc,'tx',len(txs),'chains',len(cov),[ (x['from'],x['to']) for x in cov][:6],'left',len(left))
json.dump(res,open('analysis_raw.json','w'),ensure_ascii=False)
