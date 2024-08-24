"""sopel-kym

Meme definition plugin for Sopel IRC bots.
"""
from __future__ import annotations

import memedict

from sopel import plugin


PLUGIN_PREFIX = '[kym] '


@plugin.command('kym')
@plugin.output_prefix(PLUGIN_PREFIX)
def search(bot, trigger):
    query = trigger.group(2)

    if not query:
        bot.reply("What meme am I supposed to look up?")
        return plugin.NOLIMIT

    result = define_meme(query)

    if result is None:
        bot.reply("No results.")

    _, url = memedict.search_meme(query)

    bot.say(result, truncation=' […]', trailing=' | ' + url)


@plugin.url(r'https://knowyourmeme\.com/memes/([^/]+)')
@plugin.output_prefix(PLUGIN_PREFIX)
def link(bot, trigger):
    query = trigger.group(1)

    if not query:
        return plugin.NOLIMIT

    result = define_meme(query.replace('-', ' '))

    if result is None:
        return plugin.NOLIMIT

    bot.say(result, truncation=' […]')


def define_meme(name):
    result = memedict.search(name)

    if not result:
        return None

    return result
