"""Small shared I/O helpers; each repo is self-contained."""
import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

def need(obj, *keys):
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ValueError("Missing fields: " + ", ".join(missing))

def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a measurement")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Measurements must be finite")
    return value

def unique_ids(rows, key="id"):
    ids = [r[key] for r in rows]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("IDs must be nonempty unique strings")

def run(analyze):
    parser = argparse.ArgumentParser(description=analyze.__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        data = json.loads(raw)
        result = analyze(data)
        result["provenance"] = {
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "python": platform.python_version(),
            "data_kind": data.get("data_kind", "user-supplied; not independently verified"),
        }
        text = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text)
        else:
            print(text, end="")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))
