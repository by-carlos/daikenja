import json
import unittest

from daikenja_bot.confluence import (
    ConfluenceError,
    ConfluenceNotConfigured,
    fetch_page,
    find_page,
    read_page,
    storage_links,
    storage_to_text,
)
from daikenja_bot.config import ConfluenceConfig
from daikenja_bot.links import PageTitleRef, parse_confluence_page_id

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


class StorageLinksTests(unittest.TestCase):
    def test_anchors_and_internal_links_in_order(self):
        storage = (
            '<p><a href="https://example.atlassian.net/wiki/spaces/HARBOR/pages/1?a=1&amp;b=2">x</a></p>'
            '<ac:link><ri:page ri:space-key="OPS" ri:content-title="Runbook &amp; rota" /></ac:link>'
            '<ac:link><ri:page ri:content-title="Rollback" /></ac:link>'
        )
        self.assertEqual(
            storage_links(storage),
            [
                "https://example.atlassian.net/wiki/spaces/HARBOR/pages/1?a=1&b=2",
                PageTitleRef("Runbook & rota", "OPS"),
                PageTitleRef("Rollback", None),
            ],
        )

    def test_a_page_named_inside_an_attachment_or_image_is_not_a_link(self):
        storage = (
            '<ac:image><ri:attachment ri:filename="a.png">'
            '<ri:page ri:content-title="Other" /></ri:attachment></ac:image>'
        )
        self.assertEqual(storage_links(storage), [])

    def test_relative_and_mail_links_are_dropped(self):
        storage = '<a href="/wiki/x">a</a><a href="mailto:a@example.com">b</a>'
        self.assertEqual(storage_links(storage), [])


class ReadPageTests(unittest.TestCase):
    def test_the_page_comes_back_with_its_links_and_space(self):
        payload = {
            "title": "Cutover plan",
            "body": {"storage": {"value": '<p>see <ri:page ri:content-title="Runbook" /></p>'}},
        }
        page = read_page(CONFIG, PAGE_URL, "t", fetch=responder(payload))
        self.assertEqual(page.subject.label, "Cutover plan")
        self.assertEqual(page.links, (PageTitleRef("Runbook"),))
        self.assertEqual(page.space_key, "HARBOR")

    def test_a_short_link_has_a_short_reason(self):
        with self.assertRaises(ConfluenceError) as caught:
            read_page(CONFIG, "https://example.atlassian.net/wiki/x/AbCd", "t")
        self.assertEqual(caught.exception.reason, "short link has no page id")

    def test_not_configured_has_a_short_reason(self):
        with self.assertRaises(ConfluenceNotConfigured) as caught:
            read_page(None, PAGE_URL, "t")
        self.assertEqual(caught.exception.reason, "Confluence not configured")


class FindPageTests(unittest.TestCase):
    def test_the_lookup_uses_the_default_space_and_returns_a_readable_url(self):
        seen: list = []
        url = find_page(
            CONFIG,
            PageTitleRef("Runbook & rota"),
            "t",
            fetch=responder({"results": [{"id": "777"}]}, seen),
            default_space="HARBOR",
        )
        self.assertIn("spaceKey=HARBOR", seen[0]["url"])
        self.assertIn("title=Runbook+%26+rota", seen[0]["url"])
        self.assertEqual(parse_confluence_page_id(url), "777")

    def test_the_links_own_space_wins(self):
        seen: list = []
        find_page(
            CONFIG,
            PageTitleRef("Runbook", "OPS"),
            "t",
            fetch=responder({"results": [{"id": "1"}]}, seen),
            default_space="HARBOR",
        )
        self.assertIn("spaceKey=OPS", seen[0]["url"])

    def test_no_match_is_not_found(self):
        with self.assertRaises(ConfluenceError) as caught:
            find_page(CONFIG, PageTitleRef("Nope"), "t", fetch=responder({"results": []}))
        self.assertEqual(caught.exception.reason, "not found or not visible")

    def test_two_matches_are_not_guessed_between(self):
        with self.assertRaises(ConfluenceError) as caught:
            find_page(
                CONFIG,
                PageTitleRef("Runbook"),
                "t",
                fetch=responder({"results": [{"id": "1"}, {"id": "2"}]}),
            )
        self.assertEqual(caught.exception.reason, "title matches several pages")


class JiraMacroTests(unittest.TestCase):
    MACRO = (
        '<p>tracked in <ac:structured-macro ac:name="jira" ac:schema-version="1">'
        '<ac:parameter ac:name="server">System Jira</ac:parameter>'
        '<ac:parameter ac:name="key">HAR-12</ac:parameter>'
        '</ac:structured-macro> and <a href="https://example.com/x">x</a></p>'
    )

    def test_a_jira_macro_becomes_an_issue_link_in_order(self):
        self.assertEqual(
            storage_links(self.MACRO, "https://example.atlassian.net"),
            ["https://example.atlassian.net/browse/HAR-12", "https://example.com/x"],
        )

    def test_without_a_site_the_macro_is_skipped(self):
        self.assertEqual(storage_links(self.MACRO), ["https://example.com/x"])

    def test_a_jql_macro_names_no_single_issue(self):
        storage = (
            '<ac:structured-macro ac:name="jira">'
            '<ac:parameter ac:name="jqlQuery">project = HAR</ac:parameter>'
            '</ac:structured-macro>'
        )
        self.assertEqual(storage_links(storage, "https://example.atlassian.net"), [])
