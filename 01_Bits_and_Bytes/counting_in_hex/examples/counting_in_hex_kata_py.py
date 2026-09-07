"""Answer key: five turns of the hex odometer, said out loud before checking.

Nothing here needs a converter -- that is the point of the kata. The program
exists so the answers are printed by something that counts rather than by
somebody who was fairly sure.
"""

print("1. COUNT FROM 3E TO 45")
seq = [f"{n:02X}" for n in range(0x3E, 0x46)]
print("   " + " ".join(seq))
carries = [(a, b) for a, b in zip(seq, seq[1:]) if a[-1] == "F"]
print(f"   Eight values, and exactly ONE carry: {carries[0][0]} -> {carries[0][1]}.")
print("   The low wheel rolled past F to 0 and the high wheel stepped 3 to 4.")
print("   Every other step in that run leaves the high digit alone -- which is")
print("   the thing worth feeling, because it is the same odometer you already")
print("   turn in decimal and the only new rule is where F sits.")
assert len(carries) == 1, carries

print()
print("2. WHAT COMES NEXT")
for n in (0x4F, 0xFF, 0x1FF):
    print(f"   {n:02X} -> {n + 1:02X}")
print("   FF -> 100 is the same carry twice in one step, which is why a byte")
print("   that holds FF and is incremented lands on 00 and takes the 1 with it")
print("   into a place a byte does not have.")

print()
print("3. WHICH IS BIGGER, 0x20 OR 29?")
print(f"   0x20 is {0x20}. 29 has two answers: {29} if it is decimal, {0x29} if it is hex.")
print("   So 0x20 < 29 as decimal, and 0x20 < 0x29 as hex -- the comparison")
print("   goes the same way by luck, not by argument. Only one of the two")
print("   spellings says what base it is in, and that is the whole trap.")

print()
print("4. 0xB IN DECIMAL, AND 12 IN HEX")
print(f"   0xB = {0xB}")
print(f"   12  = {12:X}   (decimal twelve, so the digit after B)")

print()
print("5. A BYTE HOLDING 0x7F IS INCREMENTED")
print(f"   {0x7F:02X} -> {0x80:02X}      binary {0x7F:08b} -> {0x80:08b}")
print("   Every bit changed. Seven ones fell to zero and the eighth rose --")
print("   one step on the odometer, and the byte's top bit is now set, which is")
print("   the bit that decides whether a signed reading calls this 128 or -128.")

assert seq[-1] == "45" and len(seq) == 8
assert f"{12:X}" == "C"
