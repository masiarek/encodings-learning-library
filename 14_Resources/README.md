# 14_Resources — things to practise with

**Level:** reference

**One line:** Material that is not a lesson: things you review, print, or come back to after the reading is done.

The thirteen chapters before this one are the course. This one is what you use once a page has been read: spaced repetition, which is the only tool here that does anything about forgetting, and a corpus, which is what you point at your own code once you believe you have understood it.

| | What it is |
|---|---|
| [Anki: hexadecimal](anki/README.md) | 22 flashcards on hex, every snippet compiled and run in four languages first |
| [The hard strings](hard_strings/README.md) | 19 test strings, one per behaviour, with a column per check saying which of them reaches each row |

## Why a deck at all, when the pages are right there

Reading an explanation and understanding it is not the same act as retrieving it, and only the second one survives a month. A page can teach you that `\x` means different things in a `str` and a `bytes` literal; nothing on the page makes you *produce* that difference from nothing, which is the act that has to be practised.

So the cards here never ask you to recognise a definition. Every one asks for something back: predict the output of a program, say whether it compiles, write the line, or choose between two spellings and say why. The strongest kind is *predict the output*, because you cannot fake having answered one.

The same discipline applies to a card as to a page: **no card claims output that no program produced.** Each deck ships with a `verify.py` that runs every snippet and diffs its stdout against the card's answer key, and a card that claims a compile error must fail with that error. That is [`tools/run_examples.py`](../tools/run_examples.py)'s contract, applied one level down.

The idea and both scripts come from the sibling [rust-learning-library ↗](https://github.com/masiarek/rust-learning-library/tree/master/10_Resources/anki), which has five decks built the same way.

## What is not here yet

- **Katas** — no longer pending: they live on the lesson pages, each with a solution CI runs, and [KATAS.md](../KATAS.md) puts them in an order. This line is kept because the *shape* of the answer is the interesting part — a kata belongs to its topic, not to a resources folder, so the only thing that could live here was the index, and the index lives at the root.
- **More decks.** Hex is the first because it is the first thing the library teaches and the first thing people half-remember. The obvious next two are the code-point/byte distinction and the encode/decode boundary in Python — both of which are already written as lessons, which is the precondition: a deck that outruns its pages has nothing to check itself against.
- **A corpus for a second question.** [The hard strings](hard_strings/README.md) is about text a field might be handed. The obvious sibling is a corpus of *bytes* a decoder might be handed — truncated sequences, overlongs, lone continuation bytes — which [Validation is a boundary](../03_Encodings/validation_is_a_boundary/README.md) and [Overlong sequences](../03_Encodings/overlong_sequences/README.md) already generate one at a time and nothing yet collects.
