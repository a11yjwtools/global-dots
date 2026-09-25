"""
Builds the public website into the folder `public/`.

Only two files are published:
    public/index.html  - the Symbol Finder page
    public/data.json   - the symbols (Section 5 of rules.txt) and their translations

Source/rules.txt and the dictionary files themselves are NOT published,
so they stay visible only to members of the project.

GitLab runs this automatically (see .gitlab-ci.yml). To try it on your
computer:  python build_site.py
"""
import json
import os
import re
import shutil
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "public")
RULES = os.path.join(BASE, "Source", "rules.txt")
MEANINGS = os.path.join(BASE, "Source", "symbol_meanings.json")
LANGS = os.path.join(BASE, "Languages", "languages.json")

SPECIAL = {"HOLYSPIRIT": "holy spirit", "HOWMANY": "how many", "TIMEPASSING": "time passing",
           "JEHOVAHSWITNESSES": "Jehovah's Witnesses", "KINGDOMHALL": "Kingdom Hall"}
PROPER = {"JEHOVAH", "JESUS", "ADAM", "EVE", "SATAN", "TIMOTHY", "REVELATION", "BIBLE",
          "HEAVEN", "PARADISE"}
RULE_RE = re.compile(r"^1 \[([^\]]+)\]=(.*)$")


def is_word(w):
    return bool(re.fullmatch(r"[A-Z0-9]+", w))


def default_english(w):
    if not is_word(w):
        return w
    if w in SPECIAL:
        return SPECIAL[w]
    return w.capitalize() if w in PROPER else w.lower()


def read_json(path, default):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def read_rules():
    with open(RULES, encoding="utf-8-sig", errors="replace") as f:
        lines = f.read().splitlines()
    start = next((i for i, l in enumerate(lines) if "SECTION 5" in l), None)
    if start is None:
        raise SystemExit("rules.txt has no SECTION 5")
    out = []
    for line in lines[start:]:
        if line.startswith("# These rules creates the space"):
            break
        m = RULE_RE.match(line.rstrip())
        if not m or not m.group(1).strip():
            continue
        rhs = m.group(2).rstrip()
        if re.search(r"\s-$", rhs):
            rhs = re.sub(r"\s+-$", "", rhs)
        code = rhs.replace("|", "").strip()
        if code:
            out.append((m.group(1), code))
    return out


def read_dict(code):
    d = {}
    p = os.path.join(BASE, "Languages", code, "dictionary.txt")
    if os.path.exists(p):
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    a, b = s.split("=", 1)
                    if a.strip() and b.strip():
                        d.setdefault(a.strip().lower(), b.strip())
    return d


def main():
    langs = read_json(LANGS, {})
    meanings = read_json(MEANINGS, {})
    dicts = {c: read_dict(c) for c in langs}
    symbols = []
    for word, code in read_rules():
        info = meanings.get(word, {})
        category = info.get("category") or ("word" if is_word(word) else "punctuation")
        english = info.get("english") or default_english(word)
        tr = {}
        if category != "punctuation":
            for c, d in dicts.items():
                if english.lower() in d:
                    tr[c] = d[english.lower()]
        symbols.append({"word": word, "code": code, "english": english, "category": category, "tr": tr})

    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "languages": [{"code": c, "name": n} for c, n in langs.items()],
            "symbols": symbols}
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copy(os.path.join(BASE, "index.html"), OUT)
    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"Built public/ with {len(symbols)} symbols and {len(langs)} languages.")


if __name__ == "__main__":
    main()
