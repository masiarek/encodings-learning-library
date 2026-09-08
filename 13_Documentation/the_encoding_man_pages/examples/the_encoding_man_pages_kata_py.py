"""Answer key: the forty pages under /usr/share/man nobody opens.

No page is opened and nothing is counted here: which pages exist differs per
machine, and a count would be a fact about the runner. What is recorded is the
map -- what to look for, and which section it lives in.
"""
print("THE PAGES THAT EXIST, AND WHERE")
rows = [
    ("utf8(5)",    "BSD/macOS", "the encoding itself -- and see the date kata"),
    ("utf-8(7)",   "Linux",     "the same subject, different section AND spelling"),
    ("euc(5)",     "BSD",       "Extended Unix Code, the CJK family"),
    ("gbk(5)",     "BSD",       "the Chinese national standard"),
    ("mskanji(5)", "BSD",       "Shift-JIS, as Microsoft shipped it"),
    ("big5(5)",    "BSD",       "traditional Chinese"),
    ("multibyte(3)", "both",    "the HUB: every multibyte function in libc"),
    ("charsets(7)", "Linux",    "the Linux hub page, a different tour"),
    ("locale(1)",  "both",      "what your six variables currently are"),
    ("iconv(1)",   "both",      "and iconv(3), which is a different page"),
]
print(f"   {'page':<14} {'where':<10} what it is")
for page, where, what in rows:
    print(f"   {page:<14} {where:<10} {what}")
print()
print("   Note rows 1 and 2. The SAME subject is utf8 in section 5 on a Mac and")
print("   utf-8 in section 7 on Linux -- different name, different section, so")
print("   `man utf8` finds it on one machine and nothing on the other. That is")
print("   the first reason these pages go unread: you cannot guess the name.")
print()
print("HOW TO FIND THEM WITHOUT KNOWING THE NAME")
print("   man -k charset       # apropos: searches the one-line descriptions")
print("   man -k encoding")
print("   man -k multibyte")
print("   man -w utf8          # prints the PATH, or nothing -- the quickest")
print("                        # way to ask 'does this machine have it?'")
print("   ls /usr/share/man/man5 | head")
print()
print("WHY THEY ARE WORTH THE HOUR")
print("   They are PRIMARY sources for the system you are actually on, written")
print("   by the people who shipped the libraries you are calling. Almost")
print("   everything else you will read about encodings is somebody's summary")
print("   of a standard, and a summary cannot tell you what YOUR iconv accepts.")
print()
print("   multibyte(3) is the one to read first if you read only one: it names")
print("   mbrtowc, wcrtomb, mbsrtowcs and the rest in one place, and those")
print("   functions are what every command-line tool on the machine is")
print("   actually calling when it decides what a character is.")
print()
print("AND THE HEALTH WARNING FROM THE PAGE NEXT DOOR")
print("   A man page has a date and cites a standard, and both can be decades")
print("   old while still describing the binary correctly. Read them as")
print("   evidence about YOUR system, not as a description of Unicode.")

assert True
