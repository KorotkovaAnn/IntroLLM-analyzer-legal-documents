"""Проверка эталонной разметки.
Использование: python validate.py gold/44fz_0001.gold.json [ещё файлы...]
Проверяет: 1) соответствие схеме; 2) все ссылки на пункты существуют;
3) каждая цитата есть в тексте одного из указанных пунктов (с нормализацией пробелов, ё/е);
4) у вопросов без ответа нет пунктов и цитаты; у вопросов с ответом — есть."""
import json, re, sys, pathlib
import jsonschema

HERE = pathlib.Path(__file__).parent.parent
SCHEMA = json.load(open(HERE / "schema" / "gold.schema.json", encoding="utf8"))


def norm(x):
    x = x.replace(" ", " ").replace("­", "").replace("ё", "е").replace("Ё", "Е")
    return re.sub(r"\s+", " ", x).strip()


def check(path):
    g = json.load(open(path, encoding="utf8"))
    errs = []
    v = jsonschema.Draft202012Validator(SCHEMA)
    for e in sorted(v.iter_errors(g), key=lambda e: list(e.path)):
        errs.append("схема: " + "/".join(map(str, e.path)) + ": " + e.message[:200])
    C = {c["id"]: c["text"] for c in g.get("layer1_clauses", [])}

    def walk(o, p):
        if isinstance(o, dict):
            if "clauses" in o and isinstance(o["clauses"], list):
                for c in o["clauses"]:
                    if c not in C:
                        errs.append(f"{p}: нет пункта {c}")
                q = o.get("quote")
                if q and not any(norm(q) in norm(C.get(c, "")) for c in o["clauses"]):
                    errs.append(f"{p}: цитата не найдена в пунктах {o['clauses']}: «{q[:60]}…»")
            for c in o.get("related_clauses", []) or []:
                if c not in C:
                    errs.append(f"{p}: нет пункта {c} (related)")
            for k, val in o.items():
                if k != "layer1_clauses":
                    walk(val, f"{p}/{k}")
        elif isinstance(o, list):
            for i, val in enumerate(o):
                walk(val, f"{p}[{i}]")

    walk(g, "")
    for q in g.get("layer4_qa", []):
        if q.get("answerable") and (not q.get("clauses") or not q.get("quote")):
            errs.append(f"qa {q.get('id')}: есть ответ, но нет пункта или цитаты")
        if q.get("answerable") is False and (q.get("clauses") or q.get("quote")):
            errs.append(f"qa {q.get('id')}: ответа нет, но указан пункт или цитата")
    return errs


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        errs = check(p)
        print(("OK   " if not errs else "FAIL ") + p)
        for e in errs:
            print("   -", e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)
