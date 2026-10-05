#!/usr/bin/env python3
"""Гейты среды: всё ли на месте после разворачивания скиллом modular-life-os-sreda.

    python3 check.py <путь к среде>

✗ — нарушение, среда не готова (код выхода 1).
! — показать архитектору, чинить не обязательно.
"""
import re
import sys
from pathlib import Path

REQUIRED = [
    "CLAUDE.md",
    "map.md",
    "data-standard.md",
    "intervention-rule.md",
    "gates.md",
    "automations.md",
    "about-me/00-overview.md",
    "about-me/profile.md",
    "about-me/how-to-talk-to-me.md",
    "about-me/goals.md",
    "about-me/verbatim.md",
    "about-me/CLAUDE.md",
    "memory/MEMORY.md",
    "architecture.py",
    "architecture.json",
]
SYSTEM_DIRS = {"about-me", "constitution", "memory", "brand"}
NAME_OK = re.compile(r"^[a-z0-9][a-z0-9.\-]*$|^(CLAUDE|MEMORY|README|SKILL|AGENTS)\.md$")
SECRETS = re.compile(
    r"sk-[A-Za-z0-9_\-]{20,}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|(?i:(?:password|пароль|api[_-]?key|token|токен)\s*[:=]\s*\S{6,})"
)

errors, notes = [], []


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    return None if end < 0 else text[4:end]


def tag_vocabulary(root):
    std = root / "data-standard.md"
    if not std.exists():
        return None
    m = re.search(r"## 4\.(.*?)\n## 5\.", std.read_text(encoding="utf-8"), re.S)
    return set(re.findall(r"`([a-z][a-z\-]*)`", m.group(1))) if m else None


def section_filled(text, title):
    m = re.search(rf"^## {re.escape(title)}\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return False
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s or s.startswith(">") or set(s) <= set("|-: "):
            continue
        if s.startswith("| Правило |") or "пока не сказал" in s or "{{" in s:
            continue
        if s.strip("-| ").strip():
            return True
    return False


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"✗ Нет папки: {root}")
        sys.exit(1)

    if re.search(r"[^A-Za-z0-9_\-/.]", str(root)):
        notes.append(f"В пути к среде кириллица или пробелы: {root}. Лучше латиницей, иначе путь памяти в ~/.claude/projects нечитаемый")

    for f in REQUIRED:
        if not (root / f).exists():
            errors.append(f"Нет файла: {f}")

    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if not NAME_OK.match(p.name):
            errors.append(f"Имя не английское или не в kebab-case: {rel}")
    if (root / "_module").exists():
        errors.append("Остался шаблон «_module/» — скопируй его под проекты и удали")

    map_text = (root / "map.md").read_text(encoding="utf-8") if (root / "map.md").exists() else ""
    claude_text = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").exists() else ""
    projects = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith((".", "_")):
            continue
        if f"{d.name}/" not in map_text and f"`{d.name}`" not in map_text:
            errors.append(f"Папка «{d.name}/» не внесена в map.md")
        if d.name != "memory" and not (d / "00-overview.md").exists():
            errors.append(f"В папке «{d.name}/» нет карты 00-overview.md")
        if d.name != "memory" and not (d / "CLAUDE.md").exists():
            errors.append(f"У модуля «{d.name}/» нет своего CLAUDE.md")
        if not (d / "architecture.json").exists():
            errors.append(f"У модуля «{d.name}/» нет машинной карты — прогони python3 architecture.py")
        if d.name not in claude_text:
            errors.append(f"Модуля «{d.name}/» нет в корневом CLAUDE.md")
        if d.name in SYSTEM_DIRS:
            continue
        projects.append(d.name)
    if not projects:
        notes.append("Ни одной папки проекта. Если проекты назвали — разложи их по папкам")

    vocab = tag_vocabulary(root)
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        text = md.read_text(encoding="utf-8")
        if SECRETS.search(text):
            errors.append(f"Похоже на пароль или токен: {rel}")
        n = text.count("{{")
        if n:
            errors.append(f"Незаполненные плейсхолдеры {{{{…}}}} ({n}): {rel}")
        if rel.parts[0] == "memory":
            continue
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"Нет YAML-шапки: {rel}")
            continue
        for field in ("name:", "tags:", "обновлён:"):
            if field not in fm:
                errors.append(f"В шапке нет «{field[:-1]}»: {rel}")
        m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.M)
        if m and vocab:
            alien = [t.strip() for t in m.group(1).split(",") if t.strip() and t.strip() not in vocab]
            if alien:
                errors.append(f"Метки вне словаря {alien}: {rel}")
        opened = re.search(r"^## Открытые вопросы\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        if opened and re.search(r"^-\s*\S", opened.group(1), re.M):
            notes.append(f"Есть открытые вопросы: {rel}")

    arch = root / "architecture.json"
    if arch.exists():
        import json
        try:
            known = set(json.loads(arch.read_text(encoding="utf-8")).get("документы", {}))
        except ValueError:
            known = None
            errors.append("architecture.json не читается — прогони python3 architecture.py")
        if known is not None:
            fresh = {str(md.relative_to(root)) for md in root.rglob("*.md")
                     if not any(part.startswith(".") for part in md.relative_to(root).parts)
                     and frontmatter(md.read_text(encoding="utf-8")) is not None}
            if fresh - known:
                errors.append(f"Машинная карта отстала от файлов ({len(fresh - known)} документов нет в ней) — прогони python3 architecture.py")
    hook = root / ".claude/settings.json"
    if not hook.exists() or "architecture.py" not in hook.read_text(encoding="utf-8"):
        notes.append("Хук пересборки карт не подключён (.claude/settings.json) — карты придётся пересобирать руками")

    showcase = root / "brand/style-reference.html"
    if showcase.exists() and re.search(r"^\s*example:\s*true", showcase.read_text(encoding="utf-8"), re.M):
        errors.append("В brand/style-reference.html остались значения-пример — заполни TOKENS и убери «example: true»")
    if (root / "brand").is_dir() and not (root / "brand/style-reference.md").exists():
        errors.append("В brand/ нет style-reference.md — истина по стилю живёт в MD, а не в HTML")

    talk = root / "about-me/how-to-talk-to-me.md"
    if talk.exists():
        text = talk.read_text(encoding="utf-8")
        for title in ("Как надо", "Как не надо"):
            if not section_filled(text, title):
                errors.append(f"В how-to-talk-to-me.md пустой раздел «{title}» — без него агент говорит «как со всеми»")

    goals = root / "about-me/goals.md"
    if goals.exists() and "не назвал" in goals.read_text(encoding="utf-8"):
        notes.append("В целях есть цифры, которые человек не назвал")

    mem = root / "memory"
    index = mem / "MEMORY.md"
    if index.exists():
        listing = index.read_text(encoding="utf-8")
        for f in sorted(mem.glob("*.md")):
            if f.name != "MEMORY.md" and f"({f.name})" not in listing:
                errors.append(f"Заметка памяти не внесена в MEMORY.md: {f.name}")

    for e in errors:
        print(f"✗ {e}")
    for n in notes:
        print(f"! {n}")
    if not errors:
        print(f"✓ Среда проходит гейты: {root}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
