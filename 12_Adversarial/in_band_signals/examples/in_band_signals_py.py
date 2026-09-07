#!/usr/bin/env python3
"""Data that lands in a slot somebody else parses.

The interpolator below is a toy with two operators, but it has the property the
real ones have: its output is fed back through it. That single fact is what
makes a filter on the input insufficient.
"""

import re

ENV = {"HOME": "/home/svc", "AWS_SECRET": "sk-live-0000-1111"}
LOOKUP = re.compile(r"\$\{([^{}]*)\}")  # innermost ${...}, no braces inside


def evaluate(expr: str) -> str:
    op, _, arg = expr.partition(":")
    if op == "lower":
        return arg.lower()
    if op == "upper":
        return arg.upper()
    if op == "env":
        return ENV.get(arg, "")
    return "${" + expr + "}"


def interpolate(s: str, rounds: int = 8) -> str:
    """Resolve innermost lookups, then look again -- the loop is the whole bug."""
    for _ in range(rounds):
        new = LOOKUP.sub(lambda m: evaluate(m.group(1)), s)
        if new == s:
            return s
        s = new
    return s


print("1. MARKERS: A CHARACTER THAT MEANS SOMETHING TO SOMEBODY ELSE")
markers = [
    ("00", "NUL", "C: the string stops here"),
    ("27", "'", "SQL: the literal stops here"),
    ("2F", "/", "a path: the segment stops here"),
    ("0D 0A", "CR LF", "HTTP and log files: the line stops here"),
    ("24 7B", "${", "a logger or template: what follows is an expression"),
    ("1B", "ESC", "a terminal: what follows is a command"),
    ("25", "%", "printf: what follows names an argument"),
]
print(f"   {'bytes':<8} {'char':<6} {'read by whom, as what'}")
for b, c, who in markers:
    print(f"   {b:<8} {c:<6} {who}")
print("   None of these is dangerous. Each is dangerous in exactly one place:")
print("   inside a field that somebody downstream parses instead of storing.")
print()

print("2. A LOGGER THAT INTERPOLATES WHAT IT LOGS")
plain = "alice"
payload = "${env:AWS_SECRET}"
for name in (plain, payload):
    print(f"   log('user=' + {name!r})")
    print(f"     -> {interpolate('user=' + name)}")
print("   The logger was asked to record a username. It read the username as a")
print("   program, because the two live in the same string and nothing marks")
print("   which part came from outside. That is Log4Shell's shape -- with a")
print("   lookup that fetched a remote class instead of an environment variable.")
print()

print("3. AND A FILTER ON THE MARKER LOSES")
blocked = "env:"
attempts = [
    "${env:AWS_SECRET}",
    "${${lower:E}nv:AWS_SECRET}",
    "${${lower:E}${lower:N}${lower:V}:AWS_SECRET}",
]
for a in attempts:
    seen = blocked in a
    print(f"   input          {a}")
    print(f"     filter sees {blocked!r}?  {seen}")
    print(f"     result        {interpolate(a)}")
print("   The second and third never contain the blocked string. They contain")
print("   instructions for BUILDING it, and the builder is the interpolator")
print("   itself -- so the marker exists only after the filter has finished.")
print("   You cannot block a substring that your own code is going to assemble.")
print("   Log4j also matched lookup names case-insensitively, so ${jNdI:...} got")
print("   through a rule for 'jndi' with no nesting at all. Two independent ways")
print("   past the same filter, which is what a filter on a keyword is worth.")
print()

print("4. THE RULE")
print("   The bug is not the payload and not the missing filter. It is that a")
print("   value from outside was placed where a parser was going to look.")
print("     wrong:  log('user=' + name)          format string built from data")
print("     right:  log('user={}', name)         data passed beside the format")
print("   Same for SQL (parameters, not concatenation), for shells (argv, not a")
print("   command line), for HTML (a text node, not markup) and for printf")
print("   (a literal format, never a variable). One rule, five syntaxes:")
print("   KEEP THE DATA OUT OF THE SENTENCE.")
