// Kata answers for From UTF-8, and lossy.
//
// Build & run:  rustc --edition 2024 from_utf8_and_lossy_kata_rs.rs && ./from_utf8_and_lossy_kata_rs

use std::borrow::Cow;

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    let bytes = b"caf\xe9".to_vec();
    println!("THE INPUT: {}   'caf' and a Latin-1 e-acute", hex(&bytes));
    println!();

    println!("1. from_utf8 — CHECK");
    match String::from_utf8(bytes.clone()) {
        Ok(s) => println!("   Ok({s:?})"),
        Err(e) => {
            let back = e.into_bytes();
            println!("   Err(FromUtf8Error). Nothing was converted and nothing was lost:");
            println!("   into_bytes() returns {} — identical to the input? {}", hex(&back), back == bytes);
        }
    }
    println!("   You still hold the bytes, so you can still decide this file was Latin-1.");
    println!();

    println!("2. from_utf8_lossy — REPLACE");
    let lossy = String::from_utf8_lossy(&bytes);
    println!("   {lossy:?}   {} bytes out of {} in", lossy.len(), bytes.len());
    println!("   Cow::{}", match lossy { Cow::Borrowed(_) => "Borrowed", Cow::Owned(_) => "Owned — so something WAS replaced" });
    println!("   One byte in, three out: U+FFFD is ef bf bd. The e9 is gone, and no");
    println!("   later code can tell it was ever there or what it was.");
    println!();

    println!("3. from_utf8_unchecked — PROMISE");
    println!("   A String whose bytes are not UTF-8. Not a panic and not a wrong answer:");
    println!("   undefined behaviour, because every &str method is allowed to assume the");
    println!("   promise. Correct only where something upstream already checked and you");
    println!("   can point at the check. Nothing is run here, deliberately.");
    println!();

    println!("4. THE TWO NUMBERS, AND WHY ONE BYTE CHANGES THEM");
    for probe in [&b"caf\xe9"[..], &b"caf\xe9\x20"[..]] {
        let e = std::str::from_utf8(probe).unwrap_err();
        println!("   {:<15} valid_up_to {}   error_len {:?}", hex(probe), e.valid_up_to(), e.error_len());
    }
    println!("   valid_up_to is 3 both times: 'caf' is text either way.");
    println!("   error_len changes because e9 is a legal START byte — it opens a three-byte");
    println!("   sequence. On its own at the end of input, the decoder cannot yet say the");
    println!("   input is wrong, only that it is INCOMPLETE, so it answers None. Append any");
    println!("   byte that is not a continuation (0x20 is a space) and the sequence can");
    println!("   never be completed, so the verdict becomes Some(1): one byte, definitely");
    println!("   not text. None means 'read more'; Some(n) means 'skip n and carry on'.");
    println!();

    println!("5. THREE STRAY CONTINUATION BYTES");
    let stray = b"\x80\x80\x80";
    let out = String::from_utf8_lossy(stray);
    println!("   from_utf8_lossy({}) -> {out:?}", hex(stray));
    println!("   {} replacement characters, not one.", out.chars().filter(|c| *c == char::REPLACEMENT_CHARACTER).count());
    println!("   The rule is one U+FFFD per MAXIMAL SUBPART — the longest prefix that could");
    println!("   still have become a character. 0x80 is a continuation byte, so it cannot");
    println!("   begin anything; each one is a failed start of its own and gets its own");
    println!("   mark. Compare a truncated sequence, where the bytes DO belong together:");
    for probe in [&b"\xe0\xb2"[..], &b"\xf0\x9f\x98"[..]] {
        let o = String::from_utf8_lossy(probe);
        println!("     {:<12} -> {} mark", hex(probe), o.chars().filter(|c| *c == char::REPLACEMENT_CHARACTER).count());
    }
    println!("   Two and three bytes, one mark each, because each is one interrupted");
    println!("   character. The count is about structure, not about how many bytes went bad.");
}
