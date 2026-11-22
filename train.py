from pathlib import Path
import json
import torch
from torch import nn
from tokenizer import CharTokenizer

DATA = Path("data/train_clean.jsonl")
MODEL_PATH, TOKENIZER_PATH = Path("data/bal_brain.pt"), Path("data/tokenizer.json")
BLOCK_SIZE, BATCH_SIZE, EPOCHS = 128, 8, 6
WIDTH, LAYERS, HEADS = 96, 2, 4

class TinyCharLM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, WIDTH)
        self.pos = nn.Embedding(BLOCK_SIZE, WIDTH)
        layer = nn.TransformerEncoderLayer(d_model=WIDTH, nhead=HEADS,
            dim_feedforward=WIDTH*4, batch_first=True, activation="gelu")
        self.transformer = nn.TransformerEncoder(layer, num_layers=LAYERS)
        self.norm, self.head = nn.LayerNorm(WIDTH), nn.Linear(WIDTH, vocab_size)

    def forward(self, x):
        _, t = x.shape
        pos = torch.arange(t, device=x.device)
        h = self.embed(x) + self.pos(pos)[None, :, :]
        mask = torch.triu(torch.ones(t, t, device=x.device), diagonal=1).bool()
        return self.head(self.norm(self.transformer(h, mask=mask)))

def main():
    if not DATA.exists():
        raise SystemExit("ابتدا python prepare_data.py را اجرا کن.")
    rows = [json.loads(s) for s in DATA.read_text(encoding="utf-8").splitlines() if s.strip()]
    corpus = "\n".join("کاربر: " + r["prompt"] + "\nبال چت: " + r["response"] for r in rows) + "\n"
    tok = CharTokenizer.train(corpus)
    ids = torch.tensor(tok.encode(corpus), dtype=torch.long)
    if len(ids) <= BLOCK_SIZE + 2:
        raise SystemExit("داده کم است؛ نمونه‌های آموزشی بیشتری اضافه کن.")
    vocab = tok.unk_id + 1
    model, opt = TinyCharLM(vocab), None
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    for epoch in range(EPOCHS):
        losses = []
        for _ in range(min(40, max(1, len(ids)//(BLOCK_SIZE*BATCH_SIZE)))):
            starts = torch.randint(0, len(ids)-BLOCK_SIZE-1, (BATCH_SIZE,))
            x = torch.stack([ids[s:s+BLOCK_SIZE] for s in starts])
            y = torch.stack([ids[s+1:s+BLOCK_SIZE+1] for s in starts])
            loss = nn.functional.cross_entropy(model(x).reshape(-1, vocab), y.reshape(-1))
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            losses.append(loss.item())
        print(f"دوره {epoch+1}/{EPOCHS}: loss={sum(losses)/len(losses):.4f}")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    tok.save(TOKENIZER_PATH)
    torch.save({"model_state": model.state_dict(), "vocab_size": vocab}, MODEL_PATH)
    print("مدل ذخیره شد:", MODEL_PATH)

if __name__ == "__main__":
    main()
