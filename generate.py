from pathlib import Path
import torch
from train import TinyCharLM, BLOCK_SIZE
from tokenizer import CharTokenizer
def load_model():
 mp,tp=Path('data/bal_brain.pt'),Path('data/tokenizer.json')
 if not mp.exists() or not tp.exists(): return None,None
 try: ckpt=torch.load(mp,map_location='cpu',weights_only=True)
 except TypeError: ckpt=torch.load(mp,map_location='cpu')
 tok=CharTokenizer.load(tp); model=TinyCharLM(ckpt['vocab_size']); model.load_state_dict(ckpt['model_state']); model.eval(); return model,tok
@torch.no_grad()
def generate_reply(model,tok,prompt,max_new_tokens=180,temperature=.8):
 ids=tok.encode('کاربر: '+prompt.strip()+'\nبال چت:')
 if not ids: return 'متن ورودی قابل پردازش نیست.'
 x=torch.tensor([ids[-BLOCK_SIZE:]],dtype=torch.long); generated=[]
 for _ in range(max_new_tokens):
  logits=model(x)[:,-1,:]/max(temperature,.05); logits[:,0]=-float('inf'); logits[:,tok.unk_id]=-float('inf')
  nxt=torch.multinomial(torch.softmax(logits,dim=-1),1); generated.append(int(nxt.item())); x=torch.cat([x,nxt],dim=1)[:,-BLOCK_SIZE:]
  decoded=tok.decode(generated)
  if '\nکاربر:' in decoded: decoded=decoded.split('\nکاربر:',1)[0]; break
 return tok.decode(generated).strip() or 'هنوز پاسخ مناسبی تولید نکردم.'
