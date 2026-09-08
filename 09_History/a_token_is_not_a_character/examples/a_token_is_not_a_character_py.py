#!/usr/bin/env python3
"""A byte-level BPE tokenizer, trained inside this program, on a corpus you can read.

This library lays five rulers along one string -- bytes, code units, code points,
grapheme clusters, terminal columns. A language model uses a sixth, and it
is the only one whose answers depend on a TRAINING CORPUS rather than on a
standard -- so it is the first ruler in this library where `it depends who is
counting` is true of two machines running the same correct code.

Nothing here talks to a network or imports a tokenizer library. The merges are
learned from the corpus below, in about twenty lines, which is the actual
algorithm GPT-2 used -- at 50257 tokens instead of 48, over far more text.

Run:  python3 a_token_is_not_a_character_py.py
"""

from collections import Counter

# The corpus. Small enough to read, and the test strings below are deliberately
# NOT in it -- a tokenizer scored on its own training text proves nothing.
ENGLISH = (
    "the small cat sat on the warm mat and the small dog sat on the cold floor. "
    "a berry is a small fruit. the raspberry and the blueberry are berries that "
    "grow on a small bush. a straw hat sat on the mat in the warm house. "
    "the small dog and the small cat are both animals that sit in the warm house. "
)
POLISH = (
    "kot siedzi na macie. pies siedzi na podłodze. mały kot i duży pies. "
    "żółw to małe zwierzę. dom jest ciepły. kot i pies są w domu. "
    "mały żółw i mały kot. dom jest mały i ciepły. "
)

# A real tokenizer has a fixed vocabulary size, so the merge count is a BUDGET,
# not a target. Holding it equal is what makes the two corpora comparable.
BUDGET = 48


def train(corpus: bytes, budget: int) -> list[tuple[bytes, bytes]]:
    """Byte Pair Encoding: repeatedly glue the commonest adjacent pair."""
    seq = [bytes([b]) for b in corpus]        # every byte is a token, to begin with
    merges = []
    for _ in range(budget):
        pairs = Counter(zip(seq, seq[1:]))
        if not pairs:
            break
        # commonest pair; ties broken lexicographically so the run is deterministic
        (a, b), count = max(pairs.items(), key=lambda kv: (kv[1], kv[0]))
        if count < 2:
            break                              # nothing repeats: there is no more to learn
        merges.append((a, b))
        seq = apply_merge(seq, a, b)
    return merges


def apply_merge(seq: list[bytes], a: bytes, b: bytes) -> list[bytes]:
    out, i = [], 0
    while i < len(seq):
        if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(seq[i])
            i += 1
    return out


def encode(text: bytes, merges: list[tuple[bytes, bytes]]) -> list[bytes]:
    """Apply the learned merges, in the order they were learned."""
    seq = [bytes([b]) for b in text]
    for a, b in merges:
        seq = apply_merge(seq, a, b)
    return seq


def vocab(merges) -> dict[bytes, int]:
    """Token -> id. The 256 single bytes first, then each merge in order."""
    v = {bytes([i]): i for i in range(256)}
    for n, (a, b) in enumerate(merges):
        v[a + b] = 256 + n
    return v


def show(token: bytes) -> str:
    """A token is BYTES. It need not be a whole character, so decoding may fail."""
    try:
        return repr(token.decode())
    except UnicodeDecodeError:
        return token.hex()


def rule(title: str) -> None:
    print(title)
    print("-" * 72)


def main() -> None:
    en = train(ENGLISH.encode(), BUDGET)
    mixed = train((ENGLISH + POLISH).encode(), BUDGET)

    # ------------------------------------------------------------------
    rule("1. WHAT THE TRAINING LEARNED, IN ORDER")
    print(f"   corpus: {len(ENGLISH)} characters of English, {len(ENGLISH.encode())} bytes")
    print(f"   budget: {BUDGET} merges      learned: {len(en)}")
    print()
    print("   The first twelve pairs it glued together:")
    print()
    for n, (a, b) in enumerate(en[:12]):
        print(f"     {256 + n:>4}  {show(a):<10} + {show(b):<10} -> {show(a + b)}")
    print()
    print("   Nobody chose those. `small` is one token because that paragraph")
    print("   keeps saying it, and `berry` becomes one for the same reason. A")
    print("   different paragraph makes a different tokenizer, and there is no")
    print("   standard anywhere in this section -- only counting.")
    print()

    # ------------------------------------------------------------------
    rule("2. WHY THE MODEL CANNOT COUNT THE LETTERS")
    v = vocab(en)
    word = "strawberry"
    toks = encode(word.encode(), en)
    print(f"   {word!r}   {len(word)} characters, {len(word.encode())} bytes, "
          f"{len(toks)} tokens")
    print()
    print(f"   {'token':<10} {'id':>5}   what the model receives")
    for t in toks:
        print(f"   {show(t):<10} {v[t]:>5}   an opaque integer")
    print()
    print(f"   the model sees:  {[v[t] for t in toks]}")
    print()
    print("   Count the letter `r` in that list. You cannot, and neither can the")
    print("   model, because the r's are INSIDE the tokens. Two of them live in")
    print(f"   token {v[encode(b'berry', en)[0]]} and one in another, and a token id is a position in a")
    print("   lookup table, not a string. Nothing in the model's input says how")
    print("   any token is spelled.")
    print()
    print("   What is demonstrated here is the input, not the model: nothing")
    print("   in that list of five integers carries a spelling. It follows that")
    print("   a model answering `how many r's` correctly is drawing on something")
    print("   other than what it was handed -- the spelling has to have been")
    print("   learned as a fact ABOUT the token rather than read OFF it.")
    print()

    # ------------------------------------------------------------------
    rule("3. THE SAME MEANING COSTS DIFFERENT AMOUNTS")
    tests = [
        ("the cat sat in the warm house", "English"),
        ("żółw siedzi w ciepłym domu", "Polish"),
    ]
    print(f"   Tokenized by the ENGLISH-trained merges above.")
    print()
    print(f"   {'':<32} {'chars':>5} {'bytes':>6} {'tokens':>7}  bytes/token")
    for text, lang in tests:
        b = text.encode()
        t = encode(b, en)
        print(f"   {text!r:<32} {len(text):>5} {len(b):>6} {len(t):>7}  "
              f"{len(b) / len(t):>5.2f}   {lang}")
    print()
    print("   Two sentences of about the same length. One costs 8 tokens and the")
    print("   other 28 -- three and a half times as much to say a comparable")
    print("   thing. The Polish sentence is barely compressed at all: almost")
    print("   every byte is still its own token, because none of its byte pairs")
    print("   was common enough in an English paragraph to earn a merge.")
    print()
    print("   That is the whole mechanism behind `the same text costs more in")
    print("   Polish`. It is not about the language being harder, and only")
    print("   partly about UTF-8 being wider. It is about whose text the merges")
    print("   were learned from.")
    print()

    # ------------------------------------------------------------------
    rule("4. AND THE BUDGET IS ZERO-SUM")
    print(f"   The same {BUDGET} merges, learned from English + Polish instead:")
    print()
    print(f"   {'':<32} {'English corpus':>15} {'mixed corpus':>14}")
    for text, lang in tests:
        b = text.encode()
        print(f"   {text!r:<32} {len(encode(b, en)):>15} {len(encode(b, mixed)):>14}")
    print()
    print("   The Polish sentence got much cheaper. The ENGLISH one got dearer.")
    print()
    print("   That is not a flaw in the experiment, it is the point. A vocabulary")
    print("   is a fixed budget, and a merge spent on a Polish byte pair is a")
    print("   merge not spent on an English one. Every language in the corpus is")
    print("   competing for the same slots, and the majority language wins them.")
    print()
    print("   Which is why a real tokenizer, trained on text that is mostly")
    print("   English, is cheap for English -- not by design, and not by")
    print("   anybody's decision, but as arithmetic.")
    print()

    # ------------------------------------------------------------------
    rule("5. A TOKEN IS BYTES, SO IT NEED NOT BE A CHARACTER")
    for text in ("żółw", "berry"):
        toks = encode(text.encode(), en)
        n = len(toks)
        print(f"   {text!r} through the English merges -> {n} token{'s' if n != 1 else ''}")
        for t in toks:
            print(f"     {t.hex():<8} {show(t)}")
        print()
    print("   Every token of the Polish word is a lone byte, and six of the seven")
    print("   are HALF A CHARACTER -- the first or second byte of a two-byte")
    print("   UTF-8 sequence, which no decoder will accept on its own. That is")
    print("   why `show` above has to fall back to hex.")
    print()
    print("   This is the same boundary problem as a chunked read cutting a")
    print("   character in two, arriving in a new place. A byte-level tokenizer")
    print("   can never fail on unfamiliar text -- there is always a token for")
    print("   every byte -- and the price of never failing is that the pieces")
    print("   it hands the model are not characters.")
    print()

    # ------------------------------------------------------------------
    rule("6. WHAT THIS PROGRAM IS NOT")
    print("   Everything above is real BPE and none of it is a real tokenizer.")
    print("   The differences that matter:")
    print()
    print("     scale       48 merges over one paragraph; a production vocabulary")
    print("                 is 50,000 to 200,000 tokens over a corpus measured in")
    print("                 terabytes. Every number here is smaller than a real")
    print("                 one; the RATIOS are the transferable part.")
    print("     pre-tokens  real implementations split on a regex FIRST, so that")
    print("                 a merge can never cross a word boundary. This one has")
    print("                 no such rule, which is why `the ` includes its space")
    print("                 and why a merge could in principle span two words.")
    print("     the mapping GPT-2 remaps the 256 bytes into printable code points")
    print("                 before merging, so that a vocabulary file is text.")
    print("                 That is cosmetics over the same algorithm.")
    print()
    print("   And one thing this page deliberately does NOT contain: a token")
    print("   count from a real model. There is no tokenizer library here, no")
    print("   network, and no vocabulary file -- so a number attributed to a")
    print("   named model would be a number nothing in this repository can")
    print("   check, which is the one kind of claim this library does not make.")
    print("   The mechanism is the claim, and the mechanism is on this page.")


if __name__ == "__main__":
    main()
