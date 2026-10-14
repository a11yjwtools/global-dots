"""
Builds the public Global Dots Symbol Finder website into the folder `public/`.

Published files:
    public/index.html                - the Symbol Finder page
    public/data.json                 - the symbols (Section 5 of rules.txt) and their translations
    public/dictionary-template.txt   - a blank dictionary listing every English meaning

VISIT STATISTICS (optional, private to you)
    Put your Umami website id in Source/analytics.json:
        { "umami_website_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" }
    The page then counts visits anonymously (no cookies) and also records which
    language people translate into. Leave the id empty to switch statistics off.

ADDING A LANGUAGE
    Create  Languages/<CODE>/dictionary.txt  (for example Languages/ZH/dictionary.txt).
    That is all: every folder with a dictionary.txt appears on the website automatically.
    The language name is taken from, in this order:
        1. Languages/languages.json        { "ZH": "Chinese" }
        2. the first line of the dictionary "# Chinese Language Dictionary (Language Code: ZH)"
        3. the folder name
    To hide a language without deleting it, put  "ZH": false  in languages.json.

DICTIONARY LINES
    English meaning = translation        (a full-width ＝ or a Tab also works)
    Lines starting with # are notes. UTF-8, UTF-16 and Chinese (GB18030) files are all accepted.

GitHub runs this automatically (see .github/workflows/pages.yml) and shows a
report on each run's summary page. To try it on your computer:  python build_site.py
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
LANG_DIR = os.path.join(BASE, "Languages")
LANGS = os.path.join(LANG_DIR, "languages.json")
ANALYTICS = os.path.join(BASE, "Source", "analytics.json")

SPECIAL = {"HOLYSPIRIT": "holy spirit", "HOWMANY": "how many", "TIMEPASSING": "time passing",
           "JEHOVAHSWITNESSES": "Jehovah's Witnesses", "KINGDOMHALL": "Kingdom Hall"}
PROPER = {"JEHOVAH", "JESUS", "ADAM", "EVE", "SATAN", "TIMOTHY", "REVELATION", "BIBLE",
          "HEAVEN", "PARADISE"}
KNOWN_NAMES = {"S": "Spanish", "P": "Portuguese", "F": "French", "G": "German", "I": "Italian",
               "ZH": "Chinese", "CH": "Chinese", "CHS": "Chinese", "CN": "Chinese", "JA": "Japanese",
               "KO": "Korean", "RU": "Russian", "AR": "Arabic", "HI": "Hindi", "EN": "English"}
RULE_RE = re.compile(r"^1 \[([^\]]+)\]=(.*)$")
SEP_RE = re.compile(r"\s*(?:=|＝|\t)\s*")

report = []          # lines for the build summary
warnings = []


def read_text(path):
    """Read a text file whatever its encoding (UTF-8, UTF-16, GB18030, Windows-1252)."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "gb18030", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def read_json(path, default):
    try:
        return json.loads(read_text(path))
    except (OSError, ValueError) as e:
        if os.path.exists(path):
            warnings.append(f"`{os.path.relpath(path, BASE)}` could not be read ({e}); it was ignored.")
        return default


def is_word(w):
    return bool(re.fullmatch(r"[A-Z0-9]+", w))


def default_english(w):
    if not is_word(w):
        return w
    if w in SPECIAL:
        return SPECIAL[w]
    return w.capitalize() if w in PROPER else w.lower()


def read_rules():
    lines = read_text(RULES).splitlines()
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


def read_dict(path):
    """Return ({english_lower: translation}, header_name)."""
    entries, name = {}, None
    for line in read_text(path).splitlines():
        s = line.strip().lstrip("﻿")
        if not s:
            continue
        if s.startswith("#"):
            m = re.match(r"#\s*(.+?)\s+Language Dictionary", s, re.I)
            if m and not name:
                name = m.group(1).strip()
            continue
        parts = SEP_RE.split(s, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            entries.setdefault(parts[0].strip().strip('"').lower(), parts[1].strip().strip('"'))
    return entries, name


def discover_languages():
    """Every Languages/<folder>/dictionary.txt is a language; languages.json only adds names or hides."""
    names = read_json(LANGS, {})
    names = {str(k).upper(): v for k, v in names.items()} if isinstance(names, dict) else {}
    found = []
    if os.path.isdir(LANG_DIR):
        for folder in sorted(os.listdir(LANG_DIR)):
            if folder.startswith((".", "_")):
                continue
            path = os.path.join(LANG_DIR, folder)
            if not os.path.isdir(path):
                continue
            dict_file = next((f for f in os.listdir(path) if f.lower() == "dictionary.txt"), None)
            if not dict_file:
                warnings.append(f"`Languages/{folder}` has no `dictionary.txt`; it was skipped.")
                continue
            code = folder.upper()
            if code == "E":
                warnings.append("`Languages/E` was skipped: E is reserved for English.")
                continue
            if names.get(code) is False:
                report.append(f"- {code}: hidden (set to false in languages.json)")
                continue
            entries, header = read_dict(os.path.join(path, dict_file))
            name = names.get(code) if isinstance(names.get(code), str) and names.get(code).strip() else None
            name = name or header or KNOWN_NAMES.get(code) or (folder if len(folder) > 3 else code)
            found.append({"code": code, "name": name, "entries": entries})
    for code in names:
        if names[code] is not False and code not in {l["code"] for l in found}:
            warnings.append(f"languages.json lists `{code}` but there is no `Languages/{code}/dictionary.txt`.")
    return found


def write_summary(text):
    print(text)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def main():
    meanings = read_json(MEANINGS, {})
    langs = discover_languages()
    symbols = []
    for word, code in read_rules():
        info = meanings.get(word, {})
        category = info.get("category") or ("word" if is_word(word) else "punctuation")
        english = info.get("english") or default_english(word)
        symbols.append({"word": word, "code": code, "english": english, "category": category, "tr": {}})

    words = [s for s in symbols if s["category"] != "punctuation"]
    english_set = {s["english"].lower() for s in words}
    rows = []
    for lang in langs:
        hits = 0
        for s in words:
            t = lang["entries"].get(s["english"].lower())
            if t:
                s["tr"][lang["code"]] = t
                hits += 1
        missing = [s["english"] for s in words if lang["code"] not in s["tr"]]
        rows.append(f"| {lang['name']} | {lang['code']} | {len(lang['entries'])} | {hits} of {len(words)} | "
                    + (", ".join(missing[:12]) + (" …" if len(missing) > 12 else "") if missing else "—") + " |")
        if lang["entries"] and hits == 0:
            sample = ", ".join(list(lang["entries"])[:5])
            warnings.append(f"**{lang['name']}**: none of its {len(lang['entries'])} lines match a symbol. "
                            f"The left side must be the English meaning (e.g. `love = …`). First lines found: {sample}")
        elif not lang["entries"]:
            warnings.append(f"**{lang['name']}**: no `English = translation` lines were found in its dictionary.")

    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "languages": [{"code": l["code"], "name": l["name"]} for l in langs],
            "symbols": symbols}

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    page = read_text(os.path.join(BASE, "index.html")).replace("__BUILD_VERSION__", version)
    # Anonymous visit statistics (Umami). Only added when Source/analytics.json has a website id.
    stats = read_json(ANALYTICS, {})
    site_id = str(stats.get("umami_website_id", "")).strip() if isinstance(stats, dict) else ""
    if site_id:
        src = str(stats.get("umami_script", "https://cloud.umami.is/script.js")).strip()
        tag = (f'<script defer src="{src}" data-website-id="{site_id}"></script>'
               '<script>window.GD_ANALYTICS=true;</script>')
        page = page.replace("<!--ANALYTICS-->", tag, 1)
        report.append("- Visit statistics: on (Umami)")
    else:
        report.append("- Visit statistics: off (add your Umami website id to Source/analytics.json to turn them on)")
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "dictionary-template.txt"), "w", encoding="utf-8") as f:
        f.write("# NAME Language Dictionary (Language Code: CODE)\n"
                "# Replace NAME and CODE above, then write the translation after each = sign.\n"
                "# Save as UTF-8 in Languages/CODE/dictionary.txt\n\n")
        for e in sorted({s["english"] for s in words}, key=str.lower):
            f.write(f"{e} = \n")

    write_summary("## Global Dots Symbol Finder build\n")
    write_summary(f"**{len(symbols)} symbols** ({len(words)} words or signs) and **{len(langs) + 1} languages** (English + {len(langs)}).\n")
    if rows:
        write_summary("| Language | Code | Lines in dictionary | Symbols translated | Still missing |\n|---|---|---|---|---|")
        for r in rows:
            write_summary(r)
    for r in report:
        write_summary(r)
    if warnings:
        write_summary("\n### Please check\n")
        for w in warnings:
            write_summary(f"- ⚠️ {w}")


if __name__ == "__main__":
    main()
