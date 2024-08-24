# sopel-kym

Meme definition plugin for Sopel IRC bots.

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-kym
```

## Using

`sopel-kym` provides a `.kym` command to search for memes by name, and also
tries to fetch details for `knowyourmeme.com` meme page links:

```
<dgw> .kym false promise juice
<Sopel> [kym] False Promise Juice. False Promises Juice refers to a series of
        object labeled Nanalan' remixes on TikTok in which Mona, labeled
        "Management" attempts to feed juice, labeled "False Promise Juice," to
        a duck stuffed animal, labeled "Burnt employees." The template grew
        popular on the site in the summer of 2024. |
        https://knowyourmeme.com/memes/false-promise-juice

<dgw> https://knowyourmeme.com/memes/all-your-base-are-belong-to-us
<Sopel> [kym] All Your Base Are Belong To Us. "All Your Base Are Belong to Us"
        is a popular engrish catchphrase that grew popular across the internet
        as early as in 1998. An awkward translation of "all of your bases are
        now under our control", the quote originally appeared in the opening
        dialogue of Zero Wing, a 16-bit shoot'em up game released in 1989.
        Marked by poor grammar, the "All Your Base" phrase and the dialogue
        scene went […]
```
