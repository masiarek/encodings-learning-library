// The Rust string checklist, run rather than asserted.
//
// Rust's strings are not hard. They are a different question being answered:
// not "what is a character?" but "which of the three lengths did you mean, and
// have these bytes been checked yet?" Once those are separate questions, every
// rule below is obvious — and the compiler is enforcing them either way.
//
// Run:  rustc --edition 2024 rust_strings_in_practice_rs.rs -o /tmp/rsprac && /tmp/rsprac

use std::ffi::OsStr;

fn bar() {
    println!("{}", "-".repeat(72));
}

fn head(n: u8, title: &str) {
    println!();
    println!("{n}. {title}");
    bar();
}

// THE parameter rule: take &str, not &String. A &String can only come from a
// String; a &str comes from a String, a literal, or a slice of either.
fn shout(s: &str) -> String {
    s.to_uppercase()
}

fn main() {
    head(1, "TAKE &str, RETURN String, AND STOP THINKING ABOUT IT");
    let owned = String::from("płyta");
    println!("   shout(\"literal\")   = {:?}", shout("literal"));
    println!("   shout(&owned)      = {:?}", shout(&owned));
    println!("   shout(&owned[0..3])= {:?}", shout(&owned[0..3]));
    println!("   One function, three callers, no allocation to call it. A &str");
    println!("   is a borrowed window onto bytes that are already valid UTF-8;");
    println!("   String owns them. That is the whole distinction.");

    head(2, "THREE LENGTHS. THE COMPILER WILL NOT PICK ONE FOR YOU.");
    for s in ["hello", "Łódź", "café", "cafe\u{301}", "日本語"] {
        println!(
            "   bytes {:2}   chars {:2}   {:?}",
            s.len(),
            s.chars().count(),
            s
        );
    }
    println!("   Rows 3 and 4 look identical and are not: 'café' composed is 4");
    println!("   chars, decomposed is 5. `len()` is BYTES — it is the one people");
    println!("   mean least often and reach for most, because it is the short name.");

    head(3, "NEVER INVENT A BYTE INDEX. ASK FOR ONE.");
    let s = "Łódź";
    println!("   s.find('d')            = {:?}   <- a real boundary, from std", s.find('d'));
    println!("   s.get(0..2)            = {:?}", s.get(0..2));
    println!("   s.get(0..1)            = {:?}   <- inside a character: None", s.get(0..1));
    println!("   s.char_indices()       = {:?}", s.char_indices().collect::<Vec<_>>());
    println!("   s.chars().next()       = {:?}", s.chars().next());
    println!("   Indices that came from std (`find`, `char_indices`, `split`) are");
    println!("   always boundaries. An index you computed by counting letters is");
    println!("   not, and `&s[0..1]` panics rather than returning half a letter.");

    head(4, "ASCII METHODS ARE FAST AND WRONG; UNICODE ONES ARE RIGHT AND SLOWER");
    for s in ["Straße", "ŁÓDŹ"] {
        println!("   {s:?}");
        println!("      to_lowercase()       {:?}", s.to_lowercase());
        println!("      to_ascii_lowercase() {:?}   <- non-ASCII left alone", s.to_ascii_lowercase());
    }
    println!("   Use the ascii_ methods when the data really is ASCII (a protocol");
    println!("   token, a hex digit, an HTTP header name) — they are branch-free.");
    println!("   Use the Unicode ones for anything a person typed.");
    println!();
    println!("   And note the length change, which is why case is not per-char:");
    println!(
        "   \"ß\".to_uppercase() = {:?}, {} chars from 1",
        "ß".to_uppercase(),
        "ß".to_uppercase().chars().count()
    );

    head(5, "REVERSING BY chars() IS NOT REVERSING A WORD");
    let composed = "café";
    let decomposed = "cafe\u{301}";
    println!("   composed   {composed:?} reversed -> {:?}", composed.chars().rev().collect::<String>());
    println!("   decomposed {decomposed:?} reversed -> {:?}", decomposed.chars().rev().collect::<String>());
    println!("   The accent came off the 'e' and landed on the front. `chars()`");
    println!("   yields Unicode SCALAR VALUES, and a user-perceived character can");
    println!("   be several of them — that is what the `unicode-segmentation`");
    println!("   crate is for, and there is no std substitute. Same reason emoji");
    println!("   families and flags cannot be counted with `chars().count()`.");

    head(6, "AT THE BOUNDARY: BYTES IN, CHECKED TEXT OUT");
    let from_the_wire: &[u8] = b"order,caf\xc3\xa9,2";
    match std::str::from_utf8(from_the_wire) {
        Ok(s) => println!("   from_utf8(good) -> Ok({s:?})"),
        Err(e) => println!("   from_utf8(good) -> Err({e})"),
    }
    // built at run time, so rustc's `invalid_from_utf8` lint does not fire on
    // a literal it can see through — the point is a file that arrives this way
    let latin1: Vec<u8> = b"order,caf\xe9,2".to_vec();
    match std::str::from_utf8(&latin1) {
        Ok(s) => println!("   from_utf8(latin-1) -> Ok({s:?})"),
        Err(e) => println!("   from_utf8(latin-1) -> Err: {e}"),
    }
    println!("   lossy              -> {:?}", String::from_utf8_lossy(&latin1));
    println!("   Decode once, at the edge, and carry &str inwards. `from_utf8` for");
    println!("   data you will act on; `from_utf8_lossy` only for something a human");
    println!("   reads, because it destroys the bytes it could not understand.");
    println!("   `unsafe {{ from_utf8_unchecked }}` is for a checked-elsewhere hot");
    println!("   path and nothing else: a &str that lies is undefined behaviour.");

    head(7, "PATHS AND ARGUMENTS ARE NOT &str, AND THAT IS NOT PEDANTRY");
    let name = OsStr::new("report.csv");
    println!("   OsStr::to_str()          = {:?}", name.to_str());
    println!("   OsStr::to_string_lossy() = {:?}", name.to_string_lossy());
    println!("   A Unix filename is any bytes except NUL and '/', and a Windows");
    println!("   one is any UTF-16 units including unpaired surrogates. Neither");
    println!("   is guaranteed to be UTF-8, so `Path` is not a `str` — handle the");
    println!("   `None` from `to_str()` rather than unwrapping it in a tool that");
    println!("   will one day be pointed at somebody else's disk.");

    head(8, "WHEN THE DATA IS NOT TEXT, SAY SO IN THE TYPE");
    let magic: Vec<u8> = b"\x89PNG\r\n\x1a\n".to_vec();
    println!("   b\"\\x89PNG...\"          = {magic:02x?}");
    println!("   is it UTF-8?            {:?}", std::str::from_utf8(&magic).is_ok());
    println!("   Binary is `&[u8]`/`Vec<u8>`, and it should never be forced through");
    println!("   String on the way past. The type IS the documentation: `&[u8]`");
    println!("   says 'unknown bytes', `&str` says 'already checked'.");
}
