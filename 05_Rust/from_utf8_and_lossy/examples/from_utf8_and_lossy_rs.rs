// Three ways to turn bytes into a String, and the three different promises they
// make. Also: the error type is a MEASUREMENT — two numbers you can act on —
// rather than a sentence you print.
//
// Build & run:  rustc --edition 2024 from_utf8_and_lossy_rs.rs && ./from_utf8_and_lossy_rs

use std::borrow::Cow;

/// The same six byte strings every section walks. Each one breaks in its own way.
const CASES: [(&str, &[u8]); 6] = [
    ("valid", "café".as_bytes()),
    ("Latin-1 é", b"caf\xe9 au"),
    ("cut mid-character", b"\xe0\xb2"),
    ("bad continuation", b"\xe0\xb2\x28"),
    ("surrogate, as UTF-8", b"\xed\xa0\x80"),
    ("three stray bytes", b"\x80\x80\x80"),
];

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

/// Python's `errors='backslashreplace'`, which std does not ship — built out of
/// the two numbers the error carries, and nothing else.
fn backslash_replace(mut bytes: &[u8]) -> String {
    let mut out = String::new();
    loop {
        match std::str::from_utf8(bytes) {
            Ok(s) => {
                out.push_str(s);
                return out;
            }
            Err(e) => {
                let good = e.valid_up_to();
                // SAFETY-free: valid_up_to() is by definition a valid boundary.
                out.push_str(std::str::from_utf8(&bytes[..good]).unwrap());
                // error_len() is None only at the end of input, where the rest is
                // all we will ever get — so consume it and stop.
                let bad = e.error_len().unwrap_or(bytes.len() - good);
                for b in &bytes[good..good + bad] {
                    out.push_str(&format!("\\x{b:02x}"));
                }
                bytes = &bytes[good + bad..];
            }
        }
    }
}

fn main() {
    println!("1. THREE FUNCTIONS, THREE CONTRACTS");
    println!("   String::from_utf8(v)             -> Result<String, FromUtf8Error>");
    println!("       CHECK. Returns the bytes to you on failure; nothing is lost or changed.");
    println!("   String::from_utf8_lossy(&v)      -> Cow<str>");
    println!("       REPLACE. Always succeeds, and the bad bytes are gone for good.");
    println!("   String::from_utf8_unchecked(v)   -> String            (unsafe)");
    println!("       PROMISE. No check at all. You are the proof, and a wrong one is");
    println!("       undefined behaviour rather than a panic.");
    println!("   Same input, same output type, three different things done about failure.");
    println!();

    println!("2. THE ERROR IS TWO NUMBERS, NOT A SENTENCE");
    println!("   {:<21} {:<21} {:>12} {:>10}", "case", "bytes", "valid_up_to", "error_len");
    for (label, bytes) in CASES {
        let (v, e) = match std::str::from_utf8(bytes) {
            Ok(_) => ("Ok".to_string(), "-".to_string()),
            Err(e) => (
                e.valid_up_to().to_string(),
                match e.error_len() {
                    Some(n) => n.to_string(),
                    None => "None".to_string(),
                },
            ),
        };
        println!("   {label:<21} {:<21} {v:>12} {e:>10}", hex(bytes));
    }
    println!("   valid_up_to() is a byte offset: everything before it IS text, and slicing");
    println!("   there is safe without another check. That is the number a tool reports when");
    println!("   it says which byte of your file stopped making sense.");
    println!();

    println!("3. AND error_len() IS A VERDICT, WHICH IS THE HALF PEOPLE MISS");
    println!("   Some(n)   these n bytes are DEFINITELY not text. Skip them and carry on.");
    println!("   None      the input just ENDED mid-character. More bytes might fix it.");
    println!();
    println!("   Same three bytes, arriving whole and arriving in two reads:");
    let whole = "😀".as_bytes();
    println!("     {:<10} {:<12} -> from_utf8 is Ok", "all 4", hex(whole));
    for cut in 1..4 {
        let part = &whole[..cut];
        let e = std::str::from_utf8(part).unwrap_err();
        println!("     {:<10} {:<12} -> valid_up_to {}  error_len {:?}", format!("first {cut}"), hex(part), e.valid_up_to(), e.error_len());
    }
    println!("   Every prefix says None. A chunked reader that treats None as an error");
    println!("   corrupts every character that straddles a read boundary; one that treats");
    println!("   it as 'hold these bytes and ask again' is correct. That is the whole");
    println!("   difference between a decoder and an incremental decoder.");
    println!();

    println!("4. LOSSY, AND HOW MANY U+FFFD IT SPENDS");
    println!("   {:<21} {:<21} {:>7}   result", "case", "bytes", "U+FFFD");
    for (label, bytes) in CASES {
        let lossy = String::from_utf8_lossy(bytes);
        let n = lossy.chars().filter(|c| *c == char::REPLACEMENT_CHARACTER).count();
        println!("   {label:<21} {:<21} {n:>7}   {lossy:?}", hex(bytes));
    }
    println!("   The count is not one per bad byte, and not one per attempt. It is one per");
    println!("   MAXIMAL SUBPART: the longest prefix of the bad run that could still have");
    println!("   become a character. 'e0 b2' is one such prefix, so one mark; three stray");
    println!("   continuation bytes are three failed starts, so three. The Unicode Standard");
    println!("   makes this a RECOMMENDATION and not a rule, so it is worth checking that");
    println!("   your other language agrees rather than assuming it does.");
    println!();

    println!("5. Cow: THE RETURN TYPE TELLS YOU WHETHER ANYTHING HAPPENED");
    for (label, bytes) in CASES {
        let which = match String::from_utf8_lossy(bytes) {
            Cow::Borrowed(_) => "Borrowed  — the bytes were already text, nothing allocated",
            Cow::Owned(_) => "Owned     — a replacement was made, so a new String exists",
        };
        println!("   {label:<21} {which}");
    }
    println!("   So `matches!(s, Cow::Owned(_))` is the question 'was my input damaged?',");
    println!("   asked after the fact and for free. from_utf8_lossy is the only repair in");
    println!("   std that hands back that flag; the Result version hands back the bytes.");
    println!();

    println!("6. THE HANDLER std DOES NOT SHIP, BUILT FROM THOSE TWO NUMBERS");
    for (label, bytes) in CASES {
        println!("   {label:<21} {}", backslash_replace(bytes));
    }
    println!("   That loop is short, and it is reversible where lossy is not: every byte is");
    println!("   still named. Python spells this errors='backslashreplace' and ships eight");
    println!("   such handlers; Rust ships one, and the two numbers you need to write the");
    println!("   others yourself. That is the trade, and it is the same one the whole");
    println!("   language makes: fewer defaults, and the parts in reach.");
    println!();

    println!("7. AND THE unsafe ONE");
    let good = "café".as_bytes().to_vec();
    let s = unsafe { String::from_utf8_unchecked(good.clone()) };
    println!("   from_utf8_unchecked on bytes that ARE valid  -> {s:?}   (sound, and free)");
    println!("   from_utf8_unchecked on bytes that are NOT     -> undefined behaviour.");
    println!("   Not a panic, not a wrong answer, not an error you can catch: a &str whose");
    println!("   promise is false, handed to code that is allowed to assume it. The right");
    println!("   use is a hot path where something upstream already checked and you can");
    println!("   point at the check. 'It has always been UTF-8 so far' is not the check.");
}
