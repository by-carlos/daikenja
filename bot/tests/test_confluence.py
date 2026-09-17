import json
import unittest

from daikenja_bot.confluence import (
    ConfluenceError,
    ConfluenceNotConfigured,
    fetch_page,
    storage_to_text,
)
from daikenja_bot.config import ConfluenceConfig

CONFIG = ConfluenceConfig(
    base_url="https://example.atlassian.net", email="rimuru@example.com"
)
PAGE_URL = "https://example.atlassian.net/wiki/spaces/HARBOR/pages/424242/Cutover+plan"


def responder(payload: dict, recorder: list | None = None):
    def fetch(url: str, headers: dict) -> bytes:
        if recorder is not None:
            recorder.append({"url": url, "headers": headers})
        return json.dumps(payload).encode("utf-8")

    return fetch


class StorageToTextTests(unittest.TestCase):
    def test_paragraphs_become_lines(self):
        self.assertEqual(
            storage_to_text("<p>first</p><p>second</p>"), "first\nsecond"
        )

    def test_list_items_get_a_dash(self):
        text = storage_to_text("<ul><li>one</li><li>two</li></ul>")
        self.assertIn("- one", text)
        self.assertIn("- two", text)

    def test_entities_are_unescaped(self):
        self.assertEqual(storage_to_text("<p>a &amp; b</p>"), "a & b")

    def test_macro_bodies_in_cdata_are_kept(self):
        text = storage_to_text(
            "<ac:structured-macro><ac:plain-text-body>"
            "<![CDATA[SELECT 1;]]>"
            "</ac:plain-text-body></ac:structured-macro>"
        )
        self.assertIn("SELECT 1;", text)

    def test_runs_of_blank_lines_collapse(self):
        self.assertEqual(storage_to_text("<p>a</p><p></p><p></p><p>b</p>"), "a\n\nb")

    def test_empty_storage_is_empty(self):
        self.assertEqual(storage_to_text(""), "")


class FetchPageTests(unittest.TestCase):
    def test_a_page_comes_back_as_a_subject(self):
        subject = fetch_page(
            CONFIG,
            PAGE_URL,
            "token",
            fetch=responder(
                {"title": "Cutover plan", "body": {"storage": {"value": "<p>Friday</p>"}}}
            ),
        )
        self.assertEqual(subject.label, "Cutover plan")
        self.assertEqual(subject.body, "Friday")
        self.assertEqual(subject.source_url, PAGE_URL)

    def test_the_v2_endpoint_and_basic_auth_are_used(self):
        calls: list = []
        fetch_page(
            CONFIG,
            PAGE_URL,
            "token",
            fetch=responder(
                {"title": "Cutover plan", "body": {"storage": {"value": "<p>x</p>"}}},
                calls,
            ),
        )
        self.assertEqual(
            calls[0]["url"],
            "https://example.atlassian.net/wiki/api/v2/pages/424242?body-format=storage",
        )
        self.assertTrue(calls[0]["headers"]["Authorization"].startswith("Basic "))

    def test_no_config_is_a_distinct_error(self):
        with self.assertRaises(ConfluenceNotConfigured) as caught:
            fetch_page(None, PAGE_URL, "token")
        self.assertIn("not configured", str(caught.exception))

    def test_no_token_says_which_variable_to_export(self):
        with self.assertRaises(ConfluenceError) as caught:
            fetch_page(CONFIG, PAGE_URL, None)
        self.assertIn("token_env", str(caught.exception))

    def test_a_short_link_is_refused_with_an_explanation(self):
        with self.assertRaises(ConfluenceError) as caught:
            fetch_page(
                CONFIG, "https://example.atlassian.net/wiki/x/AbCdEf", "token"
            )
        self.assertIn("page id", str(caught.exception))

    def test_an_empty_page_is_refused(self):
        with self.assertRaises(ConfluenceError) as caught:
            fetch_page(
                CONFIG,
                PAGE_URL,
                "token",
                fetch=responder({"title": "Blank", "body": {"storage": {"value": ""}}}),
            )
        self.assertIn("empty", str(caught.exception))

    def test_a_non_json_response_is_reported(self):
        def fetch(url: str, headers: dict) -> bytes:
            return b"<html>error</html>"

        with self.assertRaises(ConfluenceError) as caught:
            fetch_page(CONFIG, PAGE_URL, "token", fetch=fetch)
        self.assertIn("not JSON", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
