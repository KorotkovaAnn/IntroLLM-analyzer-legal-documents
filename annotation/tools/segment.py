"""Нарезка договора на пункты. Общая для 44-ФЗ и 223-ФЗ.
Единицы: preamble (шапка+преамбула), нумерованные пункты x.y[.z], тело раздела без пунктов
(например реквизиты, id = номер раздела), приложения app1, app2..."""
import re, json, sys
txt=open(sys.argv[1],encoding='utf8').read()
lines=txt.split('\n')
offs=[];o=0
for l in lines: offs.append(o); o+=len(l)+1
clause_re=re.compile(r'^(\d+(?:\.\d+)+)\.?\s')
sect_re=re.compile(r'^(\d+)\.\s+(\S.{0,120})$')
app_re=re.compile(r'^Приложение\s*№\s*(\d+)\s+к\s+(договору|контракту)',re.I)
units=[];cur=None;section=None;in_app=False;last_sec=0
def close(end):
    global cur
    if cur:
        L=[i for i in range(cur['l0'],end) if lines[i].strip()]
        if L:
            s=offs[L[0]]; e=offs[L[-1]]+len(lines[L[-1]])
            u={k:v for k,v in cur.items() if k!='l0'}; u.update(start=s,end=e,text=txt[s:e]); units.append(u)
    cur=None
cur=dict(id='preamble',number=None,section='Шапка и преамбула',l0=0)
for i,l in enumerate(lines):
    t=l.strip()
    m=app_re.match(t)
    if m:
        close(i); in_app=True; n=m.group(1)
        cur=dict(id=f'app{n}',number=None,section=f'Приложение № {n}',l0=i); continue
    if in_app: continue
    m=clause_re.match(t)
    if m:
        close(i); cur=dict(id=m.group(1),number=m.group(1),section=section,l0=i); continue
    m=sect_re.match(t)
    if m and int(m.group(1))==last_sec+1 and not t.endswith((';',',')):
        last_sec+=1; close(i); section=f"{m.group(1)}. {m.group(2).strip()}"
        cur=dict(id=m.group(1),number=m.group(1),section=section,l0=i+1)  # тело раздела, если пунктов нет
close(len(lines))
json.dump(units,open(sys.argv[2],'w',encoding='utf8'),ensure_ascii=False,indent=1)
if len(sys.argv)>3:
    for u in units: print(u['id'],'|',(u['section'] or '')[:28],'|',len(u['text']),'|',u['text'][:55].replace('\n',' '))
