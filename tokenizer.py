import json
from pathlib import Path

class CharTokenizer:
    def __init__(self, chars=None):
        self.chars = sorted(set(chars or []))
        self.stoi = {ch: i + 1 for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for ch, i in self.stoi.items()}
        self.pad_id = 0
        self.unk_id = len(self.chars) + 1

    @classmethod
    def train(cls, texts):
        chars = set()
        for text in texts:
            chars.update(text)
        return cls(chars)

    def encode(self, text):
        return [self.stoi.get(ch, self.unk_id) for ch in text]

    def decode(self, ids):
        return "".join(self.itos.get(int(i), "") for i in ids
                       if int(i) not in (self.pad_id, self.unk_id))

    def save(self, path):
        Path(path).write_text(json.dumps({"chars": self.chars}, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    @classmethod
    def load(cls, path):
        return cls(json.loads(Path(path).read_text(encoding="utf-8"))["chars"])
