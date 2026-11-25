"""Помощники для записи эталонной разметки по схеме 0.2."""
import json


def ev(clauses, quote=None, note=None):
    return {"clauses": clauses if isinstance(clauses, list) else [clauses], "quote": quote, "note": note}


def none_ev(note):
    """Значения в договоре нет."""
    return {"clauses": [], "quote": None, "note": note}


def party(role, role_norm, name_full=None, name_short=None, inn=None, signatory=None, basis=None, e=None):
    return {"name_full": name_full, "name_short": name_short, "inn": inn, "role": role, "role_norm": role_norm,
            "signatory": signatory, "basis": basis, **(e or none_ev("не указано"))}


def term(value=None, date=None, relative=None, e=None, **extra):
    return {"value": value, "date": date, "relative": relative, **extra, **(e or none_ev("не указано"))}


def pen(payer, for_, type_, size, e):
    return {"payer": payer, "for": for_, "type": type_, "size": size, **e}


def val(value, e, **extra):
    return {"value": value, **extra, **e}


def save(path, meta, clauses, fields, qa, notes):
    gold = {"meta": {**meta, "schema_version": "0.2"}, "layer1_clauses": clauses, "layer2_fields": fields,
            "layer3_risks": {"status": "не размечено, ждёт нормативной базы"}, "layer4_qa": qa, "notes": notes}
    json.dump(gold, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=2)
