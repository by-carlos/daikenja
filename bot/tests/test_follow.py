import threading
import unittest

from daikenja_bot.confluence import ConfluenceError, ConfluenceNotConfigured
from daikenja_bot.config import parse_config
from daikenja_bot.follow import MAX_CHARS, MAX_LINKS, MAX_TOTAL_CHARS, follow, truncate
from daikenja_bot.links import PageTitleRef
from daikenja_bot.resolve import CONFLUENCE, SLACK, Resolved, Resolver, thread_links
from daikenja_bot.slack_io import SlackIO
from daikenja_bot.subject import PAGE, THREAD, Subject

from .fakes import FakeSlackClient, make_config

WIKI = "https://example.atlassian.net/wiki/spaces/HARBOR/pages"
PERMALINK = "https://example.slack.com/archives/C0OTHER/p1758067200000100"
THREAD_SUBJECT = Subject(kind=THREAD, label="#harbor-rollout, 4 messages", body="[1] hi")


def page(n: int, body: str = "Friday") -> Subject:
    return Subject(kind=PAGE, label=f"Page {n}", body=body, source_url=f"{WIKI}/{n}")


class StubResolver:
    """Answers `kind_of` by URL shape and `resolve` from a table."""

    def __init__(self, pages=None, errors=None, block=None):
        self.pages = pages or {}
        self.errors = errors or {}
        self.block = block
        self.resolved: list = []

    def kind_of(self, link, *, found=False):
        if isinstance(link, PageTitleRef) or "/wiki/" in link:
            return CONFLUENCE
        if "slack.com/archives" in link:
            return SLACK
        return None

    def resolve(self, link, *, timeout=None, default_space=None):
        self.resolved.append((link, default_space))
        if self.block is not None and link in self.block[1]:
            self.block[0].wait(5)
        if link in self.errors:
            raise self.errors[link]
        return Resolved(subject=self.pages[link])


class FollowTests(unittest.TestCase):
    def test_nothing_linked_leaves_the_subject_as_it_was(self):
        self.assertIs(follow(THREAD_SUBJECT, (), StubResolver(), ()), THREAD_SUBJECT)

    def test_a_found_page_is_attached(self):
        url = f"{WIKI}/1"
        out = follow(THREAD_SUBJECT, (), StubResolver({url: page(1)}), [url])
        self.assertEqual([a.label for a in out.attachments], ["Page 1"])
        self.assertEqual(out.unread, ())

    def test_one_hop_only(self):
        # The attachment's own links are never looked at: `follow` reads only
        # the subject it was given.
        url = f"{WIKI}/1"
        linked = Subject(kind=PAGE, label="Page 1", body=f"see {WIKI}/2", source_url=url)
        resolver = StubResolver({url: linked})
        follow(THREAD_SUBJECT, (), resolver, [url])
        self.assertEqual([link for link, _ in resolver.resolved], [url])

    def test_repeats_and_the_subjects_own_url_are_dropped(self):
        own = f"{WIKI}/9"
        subject = Subject(kind=PAGE, label="Page 9", body="x", source_url=own)
        url = f"{WIKI}/1"
        resolver = StubResolver({url: page(1)})
        out = follow(subject, (url,), resolver, [own, url, url])
        self.assertEqual(len(out.attachments), 1)
        self.assertEqual(len(resolver.resolved), 1)

    def test_a_page_linking_to_itself_by_title_is_not_fetched(self):
        subject = Subject(kind=PAGE, label="Cutover plan", body="x", source_url=f"{WIKI}/9")
        resolver = StubResolver()
        follow(subject, (), resolver, [PageTitleRef("Cutover plan")])
        self.assertEqual(resolver.resolved, [])

    def test_found_slack_and_other_links_are_ignored(self):
        resolver = StubResolver()
        out = follow(THREAD_SUBJECT, (), resolver, [PERMALINK, "https://example.com/x"])
        self.assertEqual(resolver.resolved, [])
        self.assertIs(out, THREAD_SUBJECT)

    def test_an_explicit_slack_link_is_followed(self):
        thread = Subject(kind=THREAD, label="#other", body="[1] yo", source_url=PERMALINK)
        out = follow(THREAD_SUBJECT, (PERMALINK,), StubResolver({PERMALINK: thread}), ())
        self.assertEqual(out.attachments[0].label, "#other")

    def test_an_explicit_unknown_link_is_recorded(self):
        out = follow(THREAD_SUBJECT, ("https://example.com/x",), StubResolver(), ())
        self.assertEqual(out.unread[0].reason, "not a link I can read")

    def test_the_link_cap_keeps_explicit_arguments_first(self):
        urls = [f"{WIKI}/{n}" for n in range(MAX_LINKS + 2)]
        pages = {u: page(n) for n, u in enumerate(urls)}
        explicit = urls[-1]
        out = follow(THREAD_SUBJECT, (explicit,), StubResolver(pages), urls[:-1])
        labels = [a.label for a in out.attachments]
        self.assertEqual(len(labels), MAX_LINKS)
        self.assertEqual(labels[0], f"Page {MAX_LINKS + 1}")
        self.assertEqual([u.reason for u in out.unread], ["over the link limit"] * 2)

    def test_the_title_lookup_gets_the_linking_pages_space(self):
        ref = PageTitleRef("Runbook")
        resolver = StubResolver({ref: page(1)})
        follow(THREAD_SUBJECT, (), resolver, [ref], space_key="HARBOR")
        self.assertEqual(resolver.resolved, [(ref, "HARBOR")])

    def test_an_attachment_over_the_cap_is_truncated(self):
        url = f"{WIKI}/1"
        out = follow(THREAD_SUBJECT, (), StubResolver({url: page(1, "x" * (MAX_CHARS + 50))}), [url])
        body = out.attachments[0].body
        self.assertTrue(body.endswith(f"[truncated at {MAX_CHARS} characters]"))
        self.assertLess(len(body), MAX_CHARS + 50)

    def test_the_total_cap_truncates_then_drops(self):
        urls = [f"{WIKI}/{n}" for n in range(5)]
        pages = {u: page(n, "y" * MAX_CHARS) for n, u in enumerate(urls)}
        out = follow(THREAD_SUBJECT, (), StubResolver(pages), urls)
        total = sum(len(a.body) for a in out.attachments)
        self.assertLessEqual(total, MAX_TOTAL_CHARS + 100)
        self.assertEqual(len(out.attachments), 4)
        self.assertIn("truncated", out.attachments[-1].body)
        self.assertEqual(out.unread[0].reason, "over the total size limit")

    def test_a_failure_is_recorded_not_raised(self):
        good, bad, off = f"{WIKI}/1", f"{WIKI}/2", f"{WIKI}/3"
        resolver = StubResolver(
            {good: page(1)},
            errors={
                bad: ConfluenceError("gone", reason="not found or not visible"),
                off: ConfluenceNotConfigured(),
            },
        )
        out = follow(THREAD_SUBJECT, (), resolver, [good, bad, off])
        self.assertEqual(len(out.attachments), 1)
        self.assertEqual(
            [(u.url, u.reason) for u in out.unread],
            [(bad, "not found or not visible"), (off, "Confluence not configured")],
        )

    def test_a_fetch_past_the_deadline_is_recorded_as_timed_out(self):
        fast, slow = f"{WIKI}/1", f"{WIKI}/2"
        release = threading.Event()
        resolver = StubResolver({fast: page(1), slow: page(2)}, block=(release, {slow}))
        try:
            out = follow(THREAD_SUBJECT, (), resolver, [fast, slow], deadline=0.2)
        finally:
            release.set()
        self.assertEqual([a.label for a in out.attachments], ["Page 1"])
        self.assertEqual([(u.url, u.reason) for u in out.unread], [(slow, "timed out")])


class TruncateTests(unittest.TestCase):
    def test_short_text_is_untouched(self):
        self.assertEqual(truncate("abc", 10), "abc")

    def test_long_text_keeps_the_start(self):
        self.assertEqual(truncate("abcdef", 3), "abc\n[truncated at 3 characters]")


class ResolverKindTests(unittest.TestCase):
    def _resolver(self, confluence=True):
        raw = {"slack": {"owner_user_id": "U0RIMURU"}}
        if confluence:
            raw["confluence"] = {
                "base_url": "https://example.atlassian.net",
                "email": "rimuru@example.com",
            }
        return Resolver(parse_config(raw), SlackIO(FakeSlackClient()), {})

    def test_a_permalink_is_slack(self):
        self.assertEqual(self._resolver().kind_of(PERMALINK), SLACK)

    def test_a_page_on_the_site_is_confluence_when_found(self):
        self.assertEqual(self._resolver().kind_of(f"{WIKI}/1", found=True), CONFLUENCE)

    def test_any_wiki_url_is_not_confluence_when_found(self):
        url = "https://en.example.org/wiki/Harbor"
        resolver = self._resolver()
        self.assertIsNone(resolver.kind_of(url, found=True))

    def test_an_unconfigured_bot_still_recognises_atlassian_cloud(self):
        resolver = self._resolver(confluence=False)
        self.assertEqual(resolver.kind_of(f"{WIKI}/1", found=True), CONFLUENCE)

    def test_a_title_reference_is_confluence(self):
        self.assertEqual(self._resolver().kind_of(PageTitleRef("Runbook")), CONFLUENCE)

    def test_an_unconfigured_page_raises_not_configured(self):
        resolver = Resolver(make_config(), SlackIO(FakeSlackClient()), {})
        with self.assertRaises(ConfluenceNotConfigured):
            resolver.resolve(f"{WIKI}/1")


class ThreadLinksTests(unittest.TestCase):
    def test_text_and_unfurl_cards_are_both_read(self):
        messages = [
            {"text": f"please review <{WIKI}/1|the plan>"},
            {
                "text": "",
                "attachments": [
                    {"title_link": f"{WIKI}/2", "original_url": f"{WIKI}/2"},
                    {"original_url": f"{WIKI}/3"},
                ],
            },
            {"text": f"again <{WIKI}/1>"},
        ]
        self.assertEqual(thread_links(messages), [f"{WIKI}/1", f"{WIKI}/2", f"{WIKI}/3"])
