import json, datetime, itertools
from collections import defaultdict
R=json.load(open('analysis_raw.json'))
TODAY=datetime.date(2026,10,17)
def c(x): return int(round(x*100))
def D(s): return datetime.date.fromisoformat(s)
ANCHOR={'207':'2026-05-07'}   # QIB: قيد الافتتاح (Transfer from 101101) بتاريخ 7/5 يطابق رصيد البنك
out={}
for key,r in R.items():
    cov=sorted(r['cov'],key=lambda x:x['from'])
    anchor=ANCHOR.get(key)
    if not anchor:
        anchor=min(l['date'] for l in r['ol'])
    scope=[cv for cv in cov if cv['to']>=anchor]
    pre_chains=[cv for cv in cov if cv['to']<anchor]
    od=[{'date':l['date'],'amt':round(l['debit']-l['credit'],2),'name':(l['name'] or '')[:80],'move':l['move_name'] or '','uid':(l['create_uid'] or [None])[0]} for l in r['ol'] if l['date']>=anchor]
    # opening line
    c1=scope[0]; opening=None
    for o in od:
        if o['date']==anchor and abs(o['amt']-c1['open'])<0.005 and key=='207':
            opening=o; break
    if opening: od.remove(opening)
    bank=[dict(t) for t in r['txs'] if any(cv['from']<=t['date']<=cv['to'] for cv in scope)]
    # --- matching
    idx=defaultdict(list)
    for o in od: idx[(o['date'],c(o['amt']))].append(o)
    bl=[]; m_exact=0; slx_m=[]
    for b in bank:
        k=(b['date'],c(b['amt']))
        if idx.get(k):
            oo=idx[k].pop(); m_exact+=1
            if oo['uid']==62: slx_m.append(oo)
        else: bl.append(b)
    ol=[o for lst in idx.values() for o in lst]
    shifted=[]; bl2=[]
    for b in sorted(bl,key=lambda x:x['date']):
        cand=[o for o in ol if c(o['amt'])==c(b['amt']) and abs((D(o['date'])-D(b['date'])).days)<=5]
        if cand:
            cand.sort(key=lambda o:abs((D(o['date'])-D(b['date'])).days)); o=cand[0]; ol.remove(o)
            if o['uid']==62: slx_m.append(o)
            shifted.append({'bank_date':b['date'],'odoo_date':o['date'],'amt':b['amt'],'desc':b['desc'],'move':o['move']})
        else: bl2.append(b)
    # aggregate: one bank line = 2/3 odoo lines  (and the reverse)
    groups=[]
    def try_agg(single_list,multi_list,single_is_bank):
        res=[]
        for s in list(single_list):
            cands=[m for m in multi_list if (m['amt']>0)==(s['amt']>0) and abs((D(m['date'])-D(s['date'])).days)<=5 and abs(m['amt'])<=abs(s['amt'])+0.005][:25]
            hit=None
            for n in (2,3):
                for comb in itertools.combinations(cands,n):
                    if c(sum(x['amt'] for x in comb))==c(s['amt']): hit=comb; break
                if hit: break
            if hit:
                for x in hit: multi_list.remove(x)
                single_list.remove(s)
                res.append({'single_side':'bank' if single_is_bank else 'odoo','single':s,'multi':list(hit)})
        return res
    groups+=try_agg(bl2,ol,True)
    groups+=try_agg(ol,bl2,False)
    likely=[]
    def inch(d): return any(cv['from']<=d<=cv['to'] for cv in scope)
    for b in list(bl2):
        cand=[o for o in ol if inch(o['date']) and c(o['amt'])==c(b['amt']) and abs((D(o['date'])-D(b['date'])).days)<=15]
        if cand:
            cand.sort(key=lambda o:abs((D(o['date'])-D(b['date'])).days)); o=cand[0]; ol.remove(o); bl2.remove(b)
            likely.append({'bank_date':b['date'],'odoo_date':o['date'],'amt':b['amt'],'desc':b['desc'],'move':o['move'],'name':o['name'],'uid':o['uid'],'days':abs((D(o['date'])-D(b['date'])).days)})
    # --- chain / gap decomposition
    B0=round(r['odoo_bal']['o:'+c1['from']]+(opening['amt'] if opening else 0)-c1['open'],2)
    # Odoo balance before c1.from already includes lines < from; if opening line on from-date, it's added above
    rows=[]; run=B0
    def onet(a,b): return round(sum(o['amt'] for o in r_all if a<=o['date']<=b),2)
    r_all=od+([opening] if opening else [])
    # recompute odoo net excluding opening
    r_all=od
    for i,cv in enumerate(scope):
        bn=round(cv['close']-cv['open'],2); on=onet(cv['from'],cv['to']); d=round(on-bn,2); run=round(run+d,2)
        rows.append({'type':'chain','from':cv['from'],'to':cv['to'],'n':cv['n'],'bank_open':cv['open'],'bank_close':cv['close'],'bank_net':bn,'odoo_net':on,'diff':d,'running':run})
        if i+1<len(scope):
            nx=scope[i+1]
            g0=(D(cv['to'])+datetime.timedelta(days=1)).isoformat(); g1=(D(nx['from'])-datetime.timedelta(days=1)).isoformat()
            if g0<=g1:
                gb=round(nx['open']-cv['close'],2); go=onet(g0,g1); gd=round(go-gb,2); run=round(run+gd,2)
                rows.append({'type':'gap','from':g0,'to':g1,'days':(D(g1)-D(g0)).days+1,'bank_net':gb,'odoo_net':go,'diff':gd,'running':run})
    last=scope[-1]
    final_diff=round(r['odoo_bal']['c:'+last['to']]-last['close'],2)
    ok=abs(run-final_diff)<0.011
    after=[o for o in od if o['date']>last['to']]
    res={'journal':r['journal'],'anchor':anchor,'opening_line':bool(opening),'B0':B0,'rows':rows,'identity_ok':ok,'identity_run':run,'final_diff':final_diff,
         'last_bank_date':last['to'],'bank_close':last['close'],'odoo_at_last':r['odoo_bal']['c:'+last['to']],'stale_days':(TODAY-D(last['to'])).days,
         'n_scope_bank':len(bank),'matched_exact':m_exact,'likely':likely,'slx_matched':{'n':len(slx_m),'sum':round(sum(o['amt'] for o in slx_m),2)},'matched_shifted':shifted,'groups':groups,
         'bank_only':bl2,'odoo_only':ol,'pre_books_chains':len(pre_chains),
         'odoo_after_last':{'n':len(after),'net':round(sum(o['amt'] for o in after),2),'lines':after[:40]},
         'n_chains':len(scope),'odoo_now':r['odoo_bal_now']}
    out[key]=res
    print(f"{key:3} B0={B0:>15,.2f} final={final_diff:>+15,.2f} chain-sum-ok={ok} (run={run:,.2f}) bank_only={len(bl2)} odoo_only={len(ol)} shift={len(shifted)} agg={len(groups)} gaps={sum(1 for x in rows if x['type']=='gap')} chains={len(scope)}")
json.dump(out,open('compare2.json','w'),ensure_ascii=False)
