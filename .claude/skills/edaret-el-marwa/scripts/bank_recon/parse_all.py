import re, glob, json, subprocess, os, datetime
NUM=re.compile(r'-?[\d,]+\.\d{2}')
def nums(s): return [float(x.replace(',','')) for x in NUM.findall(s)]
MON={m:i+1 for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
QIB_D=re.compile(r'^\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s+(.*)')
QNB_D=re.compile(r'^\s*(\d{2})/(\d{2})/(\d{4})\s+(.*)')
def txt(f): return subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout
def parse(f):
    t=txt(f)
    if not t.strip(): return None
    key=None; kind=None
    m=re.search(r'ACCOUNT NO\s+0260-197375-(\d{3})',t)
    if m: key=m.group(1); kind='QNB'
    if re.search(r'Account Number\s*:\s*0110351760207',t): key='207'; kind='QIB'
    if not key: return None
    lines=t.split('\n')
    ob=cb=None
    for ln in lines:
        if re.search(r'Open(ing)? Balance',ln,re.I):
            n=nums(ln)
            if n and ob is None: ob=n[-1]
        if re.search(r'Clos(e|ing) Balance',ln,re.I):
            n=nums(ln)
            if n: cb=n[-1]
    tx=[]; prev=ob; last=None
    for ln in lines:
        if kind=='QIB':
            mm=QIB_D.match(ln)
            if mm and mm.group(2) in MON:
                d=datetime.date(int(mm.group(3)),MON[mm.group(2)],int(mm.group(1))); rest=mm.group(4)
            else: mm=None
        else:
            mm=QNB_D.match(ln)
            if mm:
                try: d=datetime.date(int(mm.group(3)),int(mm.group(2)),int(mm.group(1)))
                except: mm=None
                rest=mm.group(4) if mm else ''
        if mm:
            ns=nums(ln)
            if len(ns)>=2:
                bal=ns[-1]
                if prev is None: amt=None
                else: amt=round(bal-prev,2)
                tx.append({'date':d.isoformat(),'desc':NUM.sub('',rest).strip()[:90],'amt':amt,'bal':bal})
                prev=bal; last=tx[-1]; continue
        elif last is not None and ln.strip() and not re.search(r'Close Balance|Closing Balance|Terms and|www|Generated|Page \d',ln) and len(ln)-len(ln.lstrip())>=10 and not NUM.search(ln):
            if len(last['desc'])<90: last['desc']=(last['desc']+' | '+ln.strip())[:140]
    first=min((x['date'] for x in tx),default=None); lastd=max((x['date'] for x in tx),default=None)
    return {'key':key,'kind':kind,'open':ob,'close':cb,'first':first,'last':lastd,'tx':tx}
if __name__=='__main__':
    names={x['id']:x['name'] for x in json.load(open('uniq.json'))}
    out=[]
    for f in sorted(glob.glob('dl/*.pdf')):
        try: r=parse(f)
        except Exception as e: r=None
        if r:
            r['file']=os.path.basename(f); r['name']=names.get(int(os.path.basename(f)[:-4]),'')
            out.append(r)
    json.dump(out,open('parsed.json','w'),ensure_ascii=False)
    from collections import Counter
    print('parsed statements:',len(out),Counter(o['key'] for o in out))
