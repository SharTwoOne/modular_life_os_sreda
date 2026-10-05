#!/usr/bin/env python3
"""Собирает машинные карты среды: architecture.json в корне и по одному в каждом модуле.

    python3 architecture.py            (из папки среды)
    python3 architecture.py --quiet    (без вывода, так его зовёт хук)

Корневая карта: дерево папок с назначением, все MD-документы с метками из шапки,
обратный индекс «метка → файлы», список модулей.
Карта модуля: то же самое про одну папку плюс «что читать сначала» и «правила».

Руками сюда ничего вписывать не надо. Скрипт берёт всё из MD:
  · назначение папки — из таблиц в map.md и в 00-overview.md (строка «| `папка/` | что это |»)
  · «что читать сначала» — из раздела «Что читать первым» в CLAUDE.md модуля
  · «правила» — из раздела «Правила…» там же
  · «скиллы» — из раздела «Скиллы» там же, если он есть

Модуль — любая папка верхнего уровня. Завёл папку с CLAUDE.md и 00-overview.md,
вписал строку в map.md — карта у модуля появится при следующем прогоне.
"""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
QUIET = "--quiet" in sys.argv
MAP_NAME = "architecture.json"

# Служебное — в карту не попадает
SKIP = {".git", ".claude", "node_modules", ".venv", "venv", "__pycache__", ".DS_Store",
        ".obsidian", "output", "dist", "build"}

HEADER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]*?)\s*\|")
TODAY = datetime.date.today().strftime("%Y-%m-%d")


def header(f: pathlib.Path) -> dict:
    """name / tags / обновлён / статус / description из YAML-шапки. Без внешних библиотек."""
    try:
        head = f.read_text(encoding="utf-8")[:1500]
    except Exception:
        return {}
    m = HEADER.match(head)
    if not m:
        return {}
    d = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "tags":
            d["метки"] = [t.strip() for t in v.strip("[]").split(",") if t.strip()]
        elif k == "name":
            d["название"] = v
        elif k == "description":
            d["описание"] = v
        elif k in ("обновлён", "статус"):
            d[k] = v
    return d


def size(n: float) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "Б" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} ТБ"


def read(f: pathlib.Path) -> str:
    try:
        return f.read_text(encoding="utf-8")
    except Exception:
        return ""


def purposes() -> dict:
    """Назначение папок из таблиц: map.md описывает верхний уровень, 00-overview.md — свою папку."""
    found = {}
    sources = [(ROOT / "map.md", "")]
    sources += [(f, str(f.parent.relative_to(ROOT)))
                for f in sorted(ROOT.rglob("00-overview.md"))
                if not any(p in SKIP or p.startswith(".") for p in f.relative_to(ROOT).parts)]
    for f, base in sources:
        for line in read(f).splitlines():
            m = ROW.match(line.strip())
            if not m or "{{" in line:
                continue
            name = m.group(1).strip().rstrip("/")
            rel = f"{base}/{name}" if base else name
            if (ROOT / rel).is_dir() and m.group(2):
                found.setdefault(rel, m.group(2))
    return found


def section(text: str, title_start: str) -> str:
    """Тело раздела «## <title_start>…» до следующего «## »."""
    m = re.search(rf"^## {re.escape(title_start)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def items(body: str) -> list:
    """Пункты списка. Строки-продолжения приклеиваются к своему пункту."""
    out = []
    for line in body.splitlines():
        s = line.strip()
        m = re.match(r"^(?:\d+\.|[-*])\s*(.*)$", s)
        if m:
            out.append(m.group(1).strip())
        elif s and out and not s.startswith(("|", ">", "#")):
            out[-1] = f"{out[-1]} {s}".strip()
    return [re.sub(r"\*\*(.+?)\*\*", r"\1", i) for i in out if i]


def module_config(rel: str, purpose: str) -> dict:
    d = ROOT / rel
    text = read(d / "CLAUDE.md")
    if not purpose:
        body = [p.strip() for p in section(text, "Что это").split("\n\n") if p.strip()]
        purpose = " ".join(body[0].split()) if body and "{{" not in body[0] else ""
    first = []
    for item in items(section(text, "Что читать первым")):
        m = re.search(r"`([^`]+)`", item)
        if not m:
            continue
        p = m.group(1)
        first.append(p if p.startswith(f"{rel}/") or (ROOT / p).exists() and not (d / p).exists()
                     else f"{rel}/{p}")
    if not first:
        first = [f"{rel}/{n}" for n in ("CLAUDE.md", "00-overview.md", "MEMORY.md") if (d / n).exists()]
    return {
        "назначение": purpose,
        "читать": first,
        "правила": items(section(text, "Правила")),
        "скиллы": sorted(set(re.findall(r"`(/[a-z0-9:\-]+)`", section(text, "Скиллы")))),
    }


PURPOSE = purposes()


def walk(d: pathlib.Path, rel: str, docs: dict, index: dict) -> dict:
    node = {"путь": rel, "назначение": PURPOSE.get(rel, "")}
    files, weight, folders, here = 0, 0, [], []
    for p in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name in SKIP or p.name.startswith(".") or p.name == MAP_NAME:
            continue
        path = f"{rel}/{p.name}" if rel != "." else p.name
        if p.is_dir():
            child = walk(p, path, docs, index)
            files += child.pop("_files")
            weight += child.pop("_bytes")
            folders.append(child)
            continue
        files += 1
        try:
            weight += p.stat().st_size
        except OSError:
            pass
        if p.suffix == ".md":
            info = header(p)
            here.append({"файл": p.name, **info})
            if info:
                docs[path] = info
                for t in info.get("метки", []):
                    index.setdefault(t, []).append(path)
    node["файлов"] = files
    node["размер"] = size(weight)
    if here:
        node["документы"] = here
    if folders:
        node["папки"] = folders
    node["_files"], node["_bytes"] = files, weight
    return node


def clean(node: dict) -> dict:
    node.pop("_files"), node.pop("_bytes")
    return node


def write(path: pathlib.Path, data: dict) -> None:
    """Пишем, только если изменилось содержимое, а не одна дата."""
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
        if {**old, "обновлён": ""} == {**data, "обновлён": ""}:
            return
    except Exception:
        pass
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


modules = [p.name for p in sorted(ROOT.iterdir(), key=lambda x: x.name.lower())
           if p.is_dir() and p.name not in SKIP and not p.name.startswith((".", "_"))]

built = []
for rel in modules:
    conf = module_config(rel, PURPOSE.get(rel, ""))
    docs, index = {}, {}
    tree = clean(walk(ROOT / rel, rel, docs, index))
    write(ROOT / rel / MAP_NAME, {
        "обновлён": TODAY,
        "модуль": rel,
        "назначение": conf["назначение"],
        "как_читать": (
            "Карта одного модуля для агента. Пути — от корня среды. Сначала «что_читать_сначала» "
            "по порядку, потом «правила», и только потом работа. Общая карта среды — "
            "architecture.json в корне. Пересобрать: python3 architecture.py"
        ),
        "что_читать_сначала": conf["читать"],
        "правила": conf["правила"],
        "скиллы": conf["скиллы"],
        "метки": {k: sorted(v) for k, v in sorted(index.items())},
        "документы": docs,
        "дерево": tree,
    })
    built.append({"модуль": rel, "назначение": conf["назначение"],
                  "карта": f"{rel}/{MAP_NAME}", "документов": len(docs)})

docs, index = {}, {}
tree = clean(walk(ROOT, ".", docs, index))
write(ROOT / MAP_NAME, {
    "обновлён": TODAY,
    "корень": str(ROOT),
    "как_читать": (
        "Карта всей среды для агента. «модули» — разделы, у каждого своя карта и свой CLAUDE.md. "
        "«метки» — обратный индекс: метка → файлы. «документы» — все MD с шапкой. "
        "Как называть файлы и ставить метки — data-standard.md. Пересобрать: python3 architecture.py"
    ),
    "модули": built,
    "метки": {k: sorted(v) for k, v in sorted(index.items())},
    "документы": docs,
    "дерево": tree,
})

if not QUIET:
    print(f"architecture.json: документов {len(docs)}, меток {len(index)}, "
          f"файлов всего {tree['файлов']} ({tree['размер']})")
    print("карты модулей: " + ", ".join(f"{m['модуль']} ({m['документов']})" for m in built))
