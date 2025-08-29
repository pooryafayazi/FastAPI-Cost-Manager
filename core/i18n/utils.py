# core/i18n/utils.py
from __future__ import annotations
import gettext
from pathlib import Path
from typing import Iterable
from babel.core import Locale, negotiate_locale
from werkzeug.http import parse_accept_header


TRANSLATIONS_DIR = Path(__file__).parent / "translations"
DOMAIN = "messages"
DEFAULT_LANG = "en"
SUPPORTED_LANGS = ["en", "fa"]

class _Translations:
    _inst: "_Translations | None" = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
            cls._inst._set_language(DEFAULT_LANG)
        return cls._inst

    def _set_language(self, lang: str) -> None:
        self.t = gettext.translation(
            DOMAIN,
            localedir=str(TRANSLATIONS_DIR),
            languages=[lang],
            fallback=True,
        )
        self.t.install()  # sets built-in _
        self.lang = lang

    def set_from_header(self, accept_language: str | None) -> None:
        # accept_language : "fa-IR,fa;q=0.9,en;q=0.8"
        choices: Iterable[str] = SUPPORTED_LANGS
        if accept_language:
            parsed = parse_accept_header(accept_language)
            langs = [lang for lang, _q in parsed]  # لیست زبان‌ها
        else:
            langs = []
        selected = negotiate_locale(langs, choices)
        self._set_language(selected or DEFAULT_LANG)

_tr = _Translations()

def set_locale_from_header(accept_language: str | None):
    _tr.set_from_header(accept_language)

def _(message: str) -> str:
    return _tr.t.gettext(message)


def get_current_lang() -> str:
    return _tr.lang