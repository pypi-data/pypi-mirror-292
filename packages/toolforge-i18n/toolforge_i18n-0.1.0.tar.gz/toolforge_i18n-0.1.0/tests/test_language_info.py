import pytest

import toolforge_i18n._user_agent
from toolforge_i18n._language_info import lang_autonym, lang_dir, lang_fallbacks, lang_mw_to_bcp47

toolforge_i18n._user_agent.set_user_agent(  # noqa: SLF001
    'toolforge-i18n test (https://gitlab.wikimedia.org/lucaswerkmeister/toolforge_i18n/; mail@lucaswerkmeister.de)'
)


@pytest.mark.parametrize(
    'code, expected', [('en', 'English'), ('de', 'Deutsch'), ('fa', 'فارسی'), ('bn-x-Q6747180', None)]
)
def test_lang_autonym(code: str, expected: str | None) -> None:
    assert lang_autonym(code) == expected


@pytest.mark.parametrize('code, expected', [('en', 'en'), ('simple', 'en-simple'), ('unknown', 'unknown')])
def test_lang_mw_to_bcp47(code: str, expected: str) -> None:
    assert lang_mw_to_bcp47(code) == expected


@pytest.mark.parametrize('code, expected', [('en', 'ltr'), ('fa', 'rtl'), ('unknown', 'auto')])
def test_lang_dir(code: str, expected: str) -> None:
    assert lang_dir(code) == expected


@pytest.mark.parametrize(
    'code, expected',
    [
        ('en', []),
        ('de', []),
        ('de-at', ['de']),
        ('sh', ['sh-latn', 'sh-cyrl', 'bs', 'sr-el', 'sr-latn', 'hr']),
    ],
)
def test_lang_fallbacks(code: str, expected: list[str]) -> None:
    assert lang_fallbacks(code) == expected
