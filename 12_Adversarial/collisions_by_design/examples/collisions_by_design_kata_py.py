"""Answer key: who owns the equivalence class?"""
import unicodedata as ud

def fold(s): return ud.normalize("NFKC", s).casefold()

CANDIDATES = ["admin", "ADMIN", "Admin", "ａdmin", "ⓐdmin", "admın"]
classes = {}
for c in CANDIDATES:
    classes.setdefault(fold(c), []).append(c)

print("SIX SIGNUPS, AND THE CLASSES THEY FALL INTO")
for key, members in classes.items():
    print(f"   {key!r:<10} <- {members}")
print()
print(f"   {len(CANDIDATES)} distinct strings became {len(classes)} identities. That is not a")
print("   failure of the folding function -- it is the definition of one. Any")
print("   function that decides two different strings are the same person is")
print("   many-to-one by construction.")
print()
print("SO THE QUESTION IS NEVER 'DOES IT COLLIDE'")
print("   It is: who gets the class? Three answers, and every system picks one")
print("   whether it knows it or not:")
print("     FIRST COMES, FIRST SERVED   the earliest registration owns the")
print("       class and every later spelling is refused. Simple, and it means")
print("       an attacker who registers first owns YOUR name's class.")
print("     RESERVE THE WHOLE CLASS     registering 'admin' also blocks every")
print("       spelling that folds to it. Safe, and it burns names.")
print("     REFUSE AMBIGUITY            reject any name whose folded form")
print("       differs from itself -- so only the canonical spelling can ever be")
print("       registered. Strictest, and it excludes legitimate scripts.")
print()
print("THE ONE THAT IS NOT AN ANSWER")
print("   Storing the ORIGINAL and comparing the FOLDED. Then two accounts")
print("   exist, both display the same name, and which one a lookup finds")
print("   depends on the index. That is not a policy; it is the absence of one.")
print()
print("THE SAME SHAPE OUTSIDE TEXT")
print("   A hash function, a case-insensitive filesystem, an email provider")
print("   that ignores dots before the @, a phone number normalizer. Each")
print("   creates classes; each has to answer the ownership question; and the")
print("   ones that made news answered it late.")
print()
print("WHAT TO WRITE DOWN")
print("   The folding function, the stored form, and the owner rule -- three")
print("   sentences, in the spec, before the first account is created. They")
print("   cannot be changed afterwards without invalidating identities.")

assert fold("ａdmin") == "admin"
assert len(classes) < len(CANDIDATES)
