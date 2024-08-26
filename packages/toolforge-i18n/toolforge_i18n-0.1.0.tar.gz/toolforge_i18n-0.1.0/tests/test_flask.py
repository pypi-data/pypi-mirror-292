from typing import Any

import pytest
from flask import Flask
from markupsafe import Markup

import toolforge_i18n._user_agent
from toolforge_i18n._flask import (
    add_lang_if_needed,
    assert_html_language_codes_empty,
    init_html_language_codes,
    interface_language_code_from_request,
    pop_html_lang,
    push_html_lang,
)

toolforge_i18n._user_agent.set_user_agent(  # noqa: SLF001
    'toolforge-i18n test (https://gitlab.wikimedia.org/lucaswerkmeister/toolforge_i18n/; mail@lucaswerkmeister.de)'
)


app = Flask(__name__)


def test_html_lang_stack() -> None:
    with app.test_request_context():
        init_html_language_codes()
        assert push_html_lang('en') == Markup('lang="en" dir="ltr"')
        assert push_html_lang('ar') == Markup('lang="ar" dir="rtl"')
        assert pop_html_lang('ar') == Markup('')
        assert pop_html_lang('en') == Markup('')
        response: Any = 'unused argument that should be returned unchanged'
        assert assert_html_language_codes_empty(response) == response


def test_html_lang_stack_wrong_order() -> None:
    with app.test_request_context():
        init_html_language_codes()
        assert push_html_lang('en') == Markup('lang="en" dir="ltr"')
        assert push_html_lang('ar') == Markup('lang="ar" dir="rtl"')
        with pytest.raises(AssertionError):
            pop_html_lang('en')


def test_html_lang_stack_not_empty() -> None:
    with app.test_request_context():
        init_html_language_codes()
        assert push_html_lang('en') == Markup('lang="en" dir="ltr"')
        assert push_html_lang('ar') == Markup('lang="ar" dir="rtl"')
        assert pop_html_lang('ar') == Markup('')
        response: Any = 'unused argument that should be returned unchanged'
        with pytest.raises(AssertionError):
            assert_html_language_codes_empty(response)


def test_add_lang_if_needed() -> None:
    with app.test_request_context():
        init_html_language_codes()
        push_html_lang('en')
        assert add_lang_if_needed(Markup('msg'), 'ar') == Markup('<span lang="ar" dir="rtl">msg</span>')


def test_add_lang_if_needed_unneeded() -> None:
    with app.test_request_context():
        init_html_language_codes()
        push_html_lang('en')
        push_html_lang('ar')
        assert add_lang_if_needed(Markup('msg'), 'ar') == Markup('msg')


def test_interface_language_code_from_request_params() -> None:
    with app.test_request_context('/?uselang=simple'):
        translations: dict[str, dict[str, str]] = {
            'en': {},
            'en-us': {},
            'simple': {},
        }
        assert interface_language_code_from_request(translations) == 'simple'


def test_interface_language_code_from_request_headers() -> None:
    with app.test_request_context(headers=[('Accept-Language', 'de;q=0.9, en-simple;q=0.8, en;q=0.7')]):
        translations: dict[str, dict[str, str]] = {
            'en': {},
            'en-us': {},
            'simple': {},
        }
        assert interface_language_code_from_request(translations) == 'simple'


def test_interface_language_code_from_request_nothing() -> None:
    with app.test_request_context():
        translations: dict[str, dict[str, str]] = {
            'en': {},
            'en-us': {},
            'simple': {},
        }
        assert interface_language_code_from_request(translations) == 'en'
