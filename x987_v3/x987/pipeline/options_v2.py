import re
from types import SimpleNamespace
from ..utils import log

def _norm(s):
    return (s or "").strip()

def _is_cayman_r(row):
    model = _norm(row.get("model"))
    trim = _norm(row.get("trim"))
    ymt = f"{model} {trim}".strip().lower()
    return "cayman r" in ymt or (model.lower() == "cayman" and trim.lower() == "r")

def _compile_catalog(cfg):
    v2 = (cfg.get("options_v2") or {})
    catalog_cfg = v2.get("catalog") or []
    compiled = []
    for item in catalog_cfg:
        cid = item.get("id") or ""
        display = item.get("display") or cid
        value = int(item.get("value_usd") or 0)
        codes_alias = list(item.get("codes_alias") or [])
        standard_on = [str(x) for x in (item.get("standard_on") or [])]
        syns = item.get("synonyms") or []
        pats = []
        for pat in syns:
            try:
                pats.append(re.compile(pat, re.I))
            except re.error:
                pass
        compiled.append(SimpleNamespace(
            id=cid,
            display=display,
            value=value,
            codes_alias=codes_alias,
            standard_on=standard_on,
            patterns=pats,
            show_in_view=(cid != "250"),
        ))
    compiled.sort(key=lambda x: (-x.value, x.display.lower()))
    return compiled

def recompute_options_v2(rows, cfg):
    if not (cfg.get("options_v2") or {}).get("enabled", False):
        return rows
    log.step("options")
    catalog = _compile_catalog(cfg)
    count = 0
    for r in rows:
        raw_opts = r.get("raw_options") or []
        if isinstance(raw_opts, list):
            haystack = "\n".join(_norm(x) for x in raw_opts)
        else:
            haystack = _norm(raw_opts)
        is_r = _is_cayman_r(r)
        codes, labels = [], []
        total_value = 0
        for ent in catalog:
            if is_r and any("cayman r" == s.lower() for s in ent.standard_on):
                present = False
            else:
                present = any(p.search(haystack) for p in ent.patterns)
            if ent.id == "250":
                trans = _norm(r.get("transmission_norm") or r.get("transmission_raw"))
                year = r.get("year")
                if year and 2009 <= int(year) <= 2012 and trans.lower() == "automatic":
                    present = True
            if present:
                codes.append(ent.id)
                codes.extend(ent.codes_alias)
                if not (is_r and any("cayman r" == s.lower() for s in ent.standard_on)):
                    total_value += ent.value
                if ent.show_in_view and ent.display not in labels:
                    labels.append(ent.display)
        r["option_codes_present"] = codes
        r["option_labels_display"] = labels
        r["option_value_usd_total"] = total_value
        r["top5_options_present"] = labels
        r["top5_options_count"] = len(labels)
        count += 1
    log.ok(count=count)
    return rows
