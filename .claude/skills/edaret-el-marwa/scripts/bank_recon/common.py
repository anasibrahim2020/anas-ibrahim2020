import json, datetime
C=json.load(open('compare2.json')); P=json.load(open('parsed.json'))
NAMES={'207':'QIB 207','001':'QNB-001 UML','002':'QNB-002 A/N','003':'QNB-003 B/U','004':'QNB-004 S/L','005':'QNB-005 A/K','006':'QNB-006 AL/W','007':'QNB-007 AHR','008':'QNB-008 KRT','009':'QNB-009 MAR','011':'QNB-011 SHA','012':'QNB-012 RYN'}
ORDER=['207','001','002','003','004','005','006','007','008','009','011','012']
def D(s): return datetime.date.fromisoformat(s)
def inchain(r,d): return any(x['type']=='chain' and x['from']<=d<=x['to'] for x in r['rows'])
def activity(r): return round(r['final_diff']-r['B0'],2)
def coverage(r):
    ch=[x for x in r['rows'] if x['type']=='chain']; gp=[x for x in r['rows'] if x['type']=='gap']
    cd=sum((D(x['to'])-D(x['from'])).days+1 for x in ch); gd=sum(x['days'] for x in gp)
    return cd,gd,(cd/(cd+gd) if cd+gd else 1.0),len(gp)
def status(r):
    s=[]
    if abs(activity(r))>0.5: s.append(('فروق حركات','#c0392b'))
    if r['stale_days']>7: s.append(('كشف متأخر','#b8860b'))
    if abs(r['B0'])>0.5: s.append(('فرق افتتاحي','#6a4ea0'))
    if not s: s.append(('مطابق','#2e7d32'))
    return s
def real_diffs(r):
    """الفروق الحقيقية المتبقية بعد المطابقة (بنك فقط / أودو فقط داخل فترات الكشوف / محتملة)."""
    out=[]
    for b in r['bank_only']: out.append({'kind':'في البنك وغير موجود في أودو','date':b['date'],'amt':b['amt'],'desc':b['desc'],'ref':'','note':''})
    for o in r['odoo_only']:
        if inchain(r,o['date']):
            note='قيد من إنتاج التدقيق الداخلي (uid 62)' if o['uid']==62 else ''
            for g in r['rows']:
                if g['type']=='gap' and abs(g['diff']+o['amt'])<0.005 and abs((D(g['from'])-D(o['date'])).days)<=6:
                    note=(note+' — ' if note else '')+f"يقابله فرق {g['diff']:,.2f} في فجوة بلا كشف {g['from']}→{g['to']} (غالبًا نفس الحركة بتاريخ مختلف)"; break
            out.append({'kind':'في أودو وغير موجود في الكشف','date':o['date'],'amt':o['amt'],'desc':o['name'],'ref':o['move'],'note':note})
    for l in r['likely']:
        out.append({'kind':'مطابقة محتملة (فرق تاريخ كبير)','date':l['bank_date'],'amt':l['amt'],'desc':l['desc'],'ref':l['move'],'note':f"تاريخ أودو {l['odoo_date']} ({l['days']} يوم) — {l['name']}"})
    out.sort(key=lambda x:(x['date'],x['kind']))
    return out
