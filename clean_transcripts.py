"""Conservative post-pass over raw large-v3 transcripts.

large-v3 already handles almost everything. Only a few high-confidence entity
errors typically remain; fix just those and leave anything uncertain for a
human/analysis step.

Entity corrections are project-specific and are NOT stored in this repo. Put
them in a local JSON file (default: transcript_fixes.json, gitignored) shaped as:

    [
      {"pattern": "regex", "replacement": "text", "why": "note"},
      ...
    ]

Usage: python clean_transcripts.py output/*/<name>.txt [--fixes transcript_fixes.json]
"""
import argparse
import json
import os
import re

DEFAULT_FIXES_FILE = "transcript_fixes.json"


def load_fixes(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [(item["pattern"], item["replacement"]) for item in data]


def clean(text, fixes):
    for pat, repl in fixes:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text


def reflow(text):
    """mlx-whisper emits very short segments (one per line). Join them back into
    readable paragraphs: one flowing string, broken every ~4 sentences."""
    joined = " ".join(line.strip() for line in text.splitlines() if line.strip())
    joined = re.sub(r"\s+", " ", joined)
    sentences = re.findall(r".+?(?:[.!?…]+(?:\s|$)|$)", joined)
    paras, buf = [], []
    for s in sentences:
        buf.append(s.strip())
        if len(buf) >= 4:
            paras.append(" ".join(buf))
            buf = []
    if buf:
        paras.append(" ".join(buf))
    return "\n\n".join(paras) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Conservative transcript cleanup + reflow")
    parser.add_argument("files", nargs="+", help="transcript .txt files")
    parser.add_argument("--fixes", default=DEFAULT_FIXES_FILE, help="JSON file of entity corrections")
    args = parser.parse_args()

    fixes = load_fixes(args.fixes)

    for path in args.files:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        out = reflow(clean(raw, fixes))
        dst = path.replace(".txt", ".clean.txt")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        n = 0
        if fixes:
            n = sum(1 for _ in re.finditer("|".join(p for p, _ in fixes), raw, re.IGNORECASE))
        print(f"{dst}  ({n} substitution site(s))")


if __name__ == "__main__":
    main()
