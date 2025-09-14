import json
import os
from typing import Optional, Dict

PREFS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'user_prefs.json')

def _ensure_file():
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    if not os.path.exists(PREFS_PATH):
        with open(PREFS_PATH, 'w', encoding='utf-8') as f:
            json.dump({"line": {}}, f, ensure_ascii=False, indent=4)

def _read_all() -> Dict:
    _ensure_file()
    try:
        with open(PREFS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"line": {}}

def _write_all(data: Dict) -> None:
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    with open(PREFS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Public APIs

def get_user_line(tg: int) -> Optional[str]:
    data = _read_all()
    return data.get('line', {}).get(str(tg))


def set_user_line(tg: int, url: Optional[str]) -> None:
    data = _read_all()
    if 'line' not in data:
        data['line'] = {}
    key = str(tg)
    if not url:
        # remove preference
        if key in data['line']:
            data['line'].pop(key)
    else:
        data['line'][key] = url
    _write_all(data)
