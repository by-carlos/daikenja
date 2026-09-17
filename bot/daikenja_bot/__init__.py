"""Daikenja's personal-instance Slack bot.

A thin transport. The model never holds a Slack credential and never posts:
`runner` produces text, `slack_io` sends it. See ``bot/README.md`` for why
that split is a requirement rather than a preference.
"""

__all__ = ["__version__"]

# Tracks the plugin's own version only loosely: the bot ships inside the
# plugin, so `.claude-plugin/plugin.json` is the version users quote. This
# string exists for the startup banner and for bug reports.
__version__ = "0.1.0"
