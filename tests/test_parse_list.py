"""Tests for the pure parsing helpers in meme_bot.

Run with:  python -m unittest discover tests

The third-party modules meme_bot imports (streamlit, ddgs, langchain) are
stubbed out below, so these tests need nothing beyond the standard library
and never call the LLM or the network.
"""

import os
import sys
import types
import unittest


def _stub(name, **attrs):
    if name not in sys.modules:
        module = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules[name] = module


class _PromptStub:
    @staticmethod
    def from_template(template):
        return template


_stub("streamlit", cache_resource=lambda f: f, secrets={})
_stub("ddgs", DDGS=object)
_stub("langchain_core")
_stub("langchain_core.prompts", ChatPromptTemplate=_PromptStub)
_stub("langchain_openai", ChatOpenAI=object)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meme_bot import _keyword_fallback, _parse_list  # noqa: E402


class ParseListTests(unittest.TestCase):
    def test_plain_json_list(self):
        self.assertEqual(
            _parse_list('["eye roll", "side eye", "slow clap"]'),
            ["eye roll", "side eye", "slow clap"],
        )

    def test_code_fenced_json(self):
        self.assertEqual(
            _parse_list('```json\n["eye roll", "slow clap"]\n```'),
            ["eye roll", "slow clap"],
        )

    def test_list_embedded_in_prose_with_trailing_comma(self):
        # Regression: the trailing-comma cleanup used to delete the closing
        # bracket too, so this fell through to the line parser and produced
        # 'Sure! Here you go: ["eye roll' as a search phrase.
        self.assertEqual(
            _parse_list('Sure! Here you go: ["eye roll", "side eye", "slow clap",]'),
            ["eye roll", "side eye", "slow clap"],
        )

    def test_object_embedded_in_prose_with_trailing_comma(self):
        self.assertEqual(
            _parse_list('Here: {"phrases": ["eye roll", "slow clap",]} enjoy'),
            ["eye roll", "slow clap"],
        )

    def test_python_literal_single_quotes(self):
        self.assertEqual(
            _parse_list("['eye roll', 'slow clap']"),
            ["eye roll", "slow clap"],
        )

    def test_smart_quotes(self):
        self.assertEqual(
            _parse_list("[“eye roll”, “slow clap”]"),
            ["eye roll", "slow clap"],
        )

    def test_list_of_dicts(self):
        self.assertEqual(
            _parse_list('[{"phrase": "eye roll"}, {"query": "slow clap"}]'),
            ["eye roll", "slow clap"],
        )

    def test_numbered_lines_skip_chatty_filler(self):
        answer = "Sure! Here are 3 phrases:\n1. eye roll\n2. side eye\n3. slow clap"
        self.assertEqual(_parse_list(answer), ["eye roll", "side eye", "slow clap"])

    def test_chatty_opener_without_colon_is_dropped(self):
        # Regression: the filler regex ended in a literal backspace byte
        # instead of \b, so lines like "Sure thing" were kept as phrases.
        answer = "Sure thing\neye roll\nslow clap"
        self.assertEqual(_parse_list(answer), ["eye roll", "slow clap"])

    def test_filler_check_needs_whole_word(self):
        # "hope" must not swallow phrases that merely start with those letters.
        self.assertEqual(_parse_list("hopeful smile\nslow clap"),
                         ["hopeful smile", "slow clap"])

    def test_empty_answer(self):
        self.assertEqual(_parse_list(""), [])
        self.assertEqual(_parse_list("   "), [])


class KeywordFallbackTests(unittest.TestCase):
    def test_flavour_comes_first(self):
        self.assertEqual(
            _keyword_fallback("My boss scheduled a meeting", "Sarcastic"),
            ["eye roll boss scheduled meeting", "eye roll", "boss scheduled meeting"],
        )

    def test_no_words_uses_flavour(self):
        self.assertEqual(_keyword_fallback("!!!", "Dramatic"), ["dramatic gasp"])


if __name__ == "__main__":
    unittest.main()
