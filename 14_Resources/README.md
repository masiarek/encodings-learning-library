# 14_Resources — things to practise with

**Level:** reference

**One line:** Material that is not a lesson: things you review, print, or come back to after the reading is done.

The thirteen chapters before this one are the course. This one is what you use once a page has been read and you want the fact to still be there in a month — starting with spaced repetition, which is the only tool on this list that does anything about forgetting.

| | What it is |
|---|---|
| [Anki: hexadecimal](anki/README.md) | 22 flashcards on hex, every snippet compiled and run in four languages first |

## Why a deck at all, when the pages are right there

Reading an explanation and understanding it is not the same act as retrieving it, and only the second one survives a month. A page can teach you that `\x` means different things in a `str` and a `bytes` literal; nothing on the page makes you *produce* that difference from nothing, which is the act that has to be practised.

So the cards here never ask you to recognise a definition. Every one asks for something back: predict the output of a program, say whether it compiles, write the line, or choose between two spellings and say why. The strongest kind is *predict the output*, because you cannot fake having answered one.

The same discipline applies to a card as to a page: **no card claims output that no program produced.** Each deck ships with a `verify.py` that runs every snippet and diffs its stdout against the card's answer key, and a card that claims a compile error must fail with that error. That is [`tools/run_examples.py`](../tools/run_examples.py)'s contract, applied one level down.

The idea and both scripts come from the sibling [rust-learning-library ↗](https://github.com/masiarek/rust-learning-library/tree/master/10_Resources/anki), which has five decks built the same way.

## What is not here yet

- **Katas** — exercises on the lesson page with a compiled solution, which [ROADMAP.md](../ROADMAP.md) parks until chapter 3 exists, since *"encode this code point by hand"* is the natural first one and it needs the UTF-8 page to point at.
- **More decks.** Hex is the first because it is the first thing the library teaches and the first thing people half-remember. The obvious next two are the code-point/byte distinction and the encode/decode boundary in Python — both of which are already written as lessons, which is the precondition: a deck that outruns its pages has nothing to check itself against.
