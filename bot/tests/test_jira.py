import json
import unittest
import urllib.error
from unittest import mock

from daikenja_bot import jira
from daikenja_bot.config import ConfluenceConfig
from daikenja_bot.jira import JiraError, JiraNotConfigured, fetch_issue, render_issue
from daikenja_bot.subject import ISSUE

CONFIG = ConfluenceConfig(
    base_url="https://example.atlassian.net", email="rimuru@example.com"
)
ISSUE_URL = "https://example.atlassian.net/browse/HAR-12"

FIELDS = {
    "summary": "Move the cutover to Friday",
    "issuetype": {"name": "Story"},
    "status": {"name": "In Progress"},
    "assignee": {"displayName": "Shion"},
    "reporter": {"displayName": "Rigurd"},
    "description": "We need a quieter window.",
}


def comment(n: int, body: str = "") -> dict:
    return {
        "author": {"displayName": f"person{n}"},
        "created": f"2026-09-{10 + n:02d}T09:00:00.000+1200",
        "body": body or f"comment {n}",
    }


def responder(issue: dict, comments: list, seen: list | None = None):
    def fetch(url: str, headers: dict) -> bytes:
        if seen is not None:
            seen.append(url)
        if "/comment" in url:
            return json.dumps({"comments": comments, "total": len(comments)}).encode()
        return json.dumps(issue).encode()

    return fetch


class RenderIssueTests(unittest.TestCase):
    def test_header_description_then_comments_oldest_first(self):
        body = render_issue("HAR-12", FIELDS, [comment(1), comment(2)])
        self.assertTrue(body.startswith("HAR-12 (Story, In Progress)\nAssignee: Shion\nReporter: Rigurd"))
        self.assertIn("Description:\nWe need a quieter window.", body)
        self.assertIn("Comments (2):", body)
        self.assertLess(body.index("comment 1"), body.index("comment 2"))
        self.assertIn("[2026-09-11] person1:\ncomment 1", body)

    def test_no_comments_no_comment_heading(self):
        self.assertNotIn("Comments", render_issue("HAR-12", FIELDS, []))

    def test_missing_people_and_description_are_named(self):
        body = render_issue("HAR-12", {"summary": "x"}, [])
        self.assertIn("Assignee: unassigned", body)
        self.assertIn("Description:\n(none)", body)

    def test_over_the_limit_drops_the_oldest_comments_first(self):
        comments = [comment(n, f"c{n} " + "z" * 200) for n in range(1, 6)]
        full = render_issue("HAR-12", FIELDS, comments)
        limit = len(full) - 300
        body = render_issue("HAR-12", FIELDS, comments, limit)
        self.assertLessEqual(len(body), limit)
        self.assertNotIn("c1 ", body)
        self.assertNotIn("c2 ", body)
        self.assertIn("c5 ", body)
        self.assertIn("[2 older comments dropped]", body)
        self.assertIn("We need a quieter window.", body)

    def test_a_description_over_the_limit_is_cut_and_every_comment_dropped(self):
        fields = dict(FIELDS, description="d" * 500)
        body = render_issue("HAR-12", fields, [comment(1)], limit=200)
        self.assertIn("[truncated at 200 characters]", body)
        self.assertIn("[1 older comment dropped]", body)
        self.assertNotIn("comment 1", body)


class FetchIssueTests(unittest.TestCase):
    def test_the_issue_and_its_comments_become_a_subject(self):
        seen: list = []
        newest_first = [comment(2), comment(1)]
        subject = fetch_issue(CONFIG, ISSUE_URL, "t", responder({"fields": FIELDS}, newest_first, seen))
        self.assertEqual(subject.kind, ISSUE)
        self.assertEqual(subject.label, "HAR-12: Move the cutover to Friday")
        self.assertEqual(subject.source_url, ISSUE_URL)
        self.assertLess(subject.body.index("comment 1"), subject.body.index("comment 2"))
        self.assertTrue(seen[0].startswith("https://example.atlassian.net/rest/api/2/issue/HAR-12?fields="))
        self.assertIn("/rest/api/2/issue/HAR-12/comment?orderBy=-created", seen[1])

    def test_a_board_link_reads_the_selected_issue(self):
        seen: list = []
        url = "https://example.atlassian.net/jira/software/projects/HAR/boards/3?selectedIssue=HAR-7"
        fetch_issue(CONFIG, url, "t", responder({"fields": FIELDS}, [], seen))
        self.assertIn("/issue/HAR-7?", seen[0])

    def test_not_configured(self):
        with self.assertRaises(JiraNotConfigured) as caught:
            fetch_issue(None, ISSUE_URL, "t")
        self.assertEqual(caught.exception.reason, "Jira not configured")
        self.assertIn("confluence", str(caught.exception))

    def test_no_token(self):
        with self.assertRaises(JiraError):
            fetch_issue(CONFIG, ISSUE_URL, None)

    def test_not_an_issue(self):
        with self.assertRaises(JiraError) as caught:
            fetch_issue(CONFIG, ISSUE_URL, "t", responder({"errorMessages": []}, []))
        self.assertEqual(caught.exception.reason, "not an issue")


class ErrorMappingTests(unittest.TestCase):
    def _raise(self, exc):
        with mock.patch.object(jira.urllib.request, "urlopen", side_effect=exc):
            with self.assertRaises(JiraError) as caught:
                jira._default_fetch("https://example.atlassian.net/x", {})
        return caught.exception

    def _http(self, code):
        return urllib.error.HTTPError("https://example.atlassian.net/x", code, "no", {}, None)

    def test_not_found(self):
        self.assertEqual(self._raise(self._http(404)).reason, "not found or not visible")

    def test_rejected_credentials(self):
        err = self._raise(self._http(401))
        self.assertIn("credentials", str(err))
        self.assertEqual(err.reason, "HTTP 401, credentials rejected")

    def test_other_status(self):
        self.assertEqual(self._raise(self._http(502)).reason, "HTTP 502")

    def test_timeout(self):
        self.assertEqual(self._raise(TimeoutError()).reason, "timed out")

    def test_unreachable(self):
        self.assertEqual(self._raise(urllib.error.URLError("dns")).reason, "unreachable")
