import importlib.util, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from web_search import search as web_search
DB=Path('data/memory.sqlite3')
# Keep experimental generation disabled until a separate quality evaluation passes.
ENABLE_EXPERIMENTAL_GENERATION=False
STOP={'چی','چه','یادت','یاد','هست','است','بود','من','تو','بال','چت','حافظه','درباره','را','رو','از','به'}
def normalize(s): return ' '.join(str(s).replace('ي','ی').replace('ك','ک').split()).strip()
def terms(s): return [w for w in re.findall(r'[\wآ-ی]+',normalize(s).lower()) if len(w)>1 and w not in STOP]
class BalBrain:
 def __init__(self,db_path=DB):
  self.db_path=Path(db_path); self.db_path.parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(str(self.db_path)); self.db.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, content TEXT NOT NULL, created_at TEXT NOT NULL)'); self.db.commit()
  self.model=self.tokenizer=None
  if ENABLE_EXPERIMENTAL_GENERATION and importlib.util.find_spec('torch') is not None:
   try:
    from generate import load_model
    self.model,self.tokenizer=load_model()
   except Exception as e: print('مدل زبانی بارگذاری نشد:',e)
 def remember(self,fact):
  fact=normalize(fact)
  if fact: self.db.execute('INSERT INTO memories(content,created_at) VALUES (?,?)',(fact,datetime.now(timezone.utc).isoformat())); self.db.commit()
 def recall(self,query='',limit=5):
  q=terms(query); rows=self.db.execute('SELECT content FROM memories ORDER BY id DESC LIMIT 500').fetchall()
  if not q: return [x[0] for x in rows[:limit]]
  ranked=[]
  for (content,) in rows:
   score=sum(w in set(terms(content)) for w in q)
   if score: ranked.append((score,content))
  ranked.sort(key=lambda x:x[0],reverse=True); return [x[1] for x in ranked[:limit]]
 def reply(self,message):
  msg=normalize(message)
  if not msg: return 'پیامی دریافت نکردم؛ چیزی بنویس.'
  if msg.startswith('یادت باشه '):
   fact=msg[len('یادت باشه '):].strip()
   if fact: self.remember(fact); return 'این مورد را در حافظه BAL CHAT ذخیره کردم.'
   return 'چه چیزی را ذخیره کنم؟'
  if msg.startswith('جستجو کن '):
   q=msg[len('جستجو کن '):].strip()
   if not q: return 'موضوع جستجو را هم بنویس.'
   res=web_search(q)
   if res and 'error' not in res[0]: return '\n'.join(f"- {x['title']}\n  {x['url']}" for x in res) or 'نتیجه‌ای پیدا نشد.'
   return res[0].get('error','جست‌وجو انجام نشد.') if res else 'نتیجه‌ای پیدا نشد.'
  if any(k in msg for k in ('چی یادت هست','حافظه‌ات','چه چیزهایی ذخیره')):
   found=self.recall('',10); return 'هنوز چیزی ذخیره نشده.' if not found else 'این‌ها را به خاطر دارم:\n- '+'\n- '.join(found)
  if 'یادت هست' in msg or 'درباره' in msg:
   found=self.recall(msg)
   if found: return 'این را در حافظه پیدا کردم:\n- '+'\n- '.join(found)
  if self.model is not None:
   from generate import generate_reply
   return generate_reply(self.model,self.tokenizer,msg)
  if any(x in msg for x in ('سلام','درود')): return 'سلام! من BAL CHAT هستم. 💙'
  return 'پیامت را دریافت کردم. در این نسخه حافظه و جست‌وجوی وبِ پیکربندی‌شده قابل استفاده‌اند؛ مدل زبانی آزمایشی هنوز پاسخ قابل‌اعتماد تولید نمی‌کند.'
 def close(self): self.db.close()
if __name__=='__main__':
 bot=BalBrain(); print('BAL CHAT BRAIN COMBINED 1.1 | خروج: /exit')
 try:
  while True:
   try: msg=input('شما: ').strip()
   except (EOFError,KeyboardInterrupt): break
   if msg.lower() in ('/exit','exit','خروج'): break
   print('بال چت:',bot.reply(msg))
 finally: bot.close()
