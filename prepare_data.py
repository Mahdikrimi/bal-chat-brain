import json
from pathlib import Path
SRC=Path('data/train.jsonl'); DST=Path('data/train_clean.jsonl')
def norm(v): return ' '.join(str(v).replace('ي','ی').replace('ك','ک').split())
def main():
 if not SRC.exists(): raise SystemExit('فایل data/train.jsonl وجود ندارد.')
 DST.parent.mkdir(parents=True,exist_ok=True); count=0
 with SRC.open(encoding='utf-8') as src, DST.open('w',encoding='utf-8') as dst:
  for n,line in enumerate(src,1):
   if not line.strip(): continue
   try:
    obj=json.loads(line); p=norm(obj.get('prompt','')); r=norm(obj.get('response',''))
    if not p or not r: print(f'ردیف {n} خالی بود و رد شد.'); continue
    dst.write(json.dumps({'prompt':p,'response':r},ensure_ascii=False)+'\n'); count+=1
   except (json.JSONDecodeError,TypeError,AttributeError) as e: print(f'ردیف {n} رد شد: {e}')
 print(f'{count} نمونه آموزشی آماده شد: {DST}')
if __name__=='__main__': main()
