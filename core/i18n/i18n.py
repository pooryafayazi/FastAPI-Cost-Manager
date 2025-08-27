from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict
import json
from fastapi import Query, Request
from core.config import settings

LOCALES_DIR = Path(__file__).parent / "locales"


def _dig(d: Dict[str, Any], dotted_key: str) -> Any:
    cur = d
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


@lru_cache(maxsize=1)
def load_catalogs() -> Dict[str, Dict[str, Any]]:
    catalogs: Dict[str, Dict[str, Any]] = {}
    for p in LOCALES_DIR.glob("*.json"):
        with p.open("r", encoding="utf-8") as f:
            catalogs[p.stem] = json.load(f)
    return catalogs


def parse_accept_language(header_val: str | None) -> str | None:
    if not header_val:
        return None
    parts = [seg.strip() for seg in header_val.split(",")]
    for seg in parts:
        code = seg.split(";")[0].strip().lower()
        code = code.split("-")[0]  # en-US -> en
        if code in settings.SUPPORTED_LANGUAGES:
            return code
    return None


class I18n:
    def __init__(self, lang: str, catalogs: Dict[str, Dict[str, Any]]):
        self.lang = lang
        self.catalogs = catalogs

    def __call__(self, key: str, **kwargs) -> str:
        return self.t(key, **kwargs)

    def t(self, key: str, **kwargs) -> str:
        text = _dig(self.catalogs.get(self.lang, {}), key)
        if text is None:
            text = _dig(self.catalogs.get("en", {}), key)
        if text is None:
            text = key
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text


def get_translator(
    request: Request,
    lang: str | None = Query(default=None, alias="lang"),
) -> I18n:
    catalogs = load_catalogs()
    chosen = (
        lang
        or parse_accept_language(request.headers.get("accept-language"))
        or settings.DEFAULT_LANGUAGE
    )
    if chosen not in settings.SUPPORTED_LANGUAGES:
        chosen = settings.DEFAULT_LANGUAGE
    return I18n(chosen, catalogs)
