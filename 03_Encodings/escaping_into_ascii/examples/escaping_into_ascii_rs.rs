// The escape you are writing is decided by the iterator you reach for.
//
// A JSON \uXXXX is one UTF-16 code unit; a %XX is one byte. Rust has a
// separate iterator for each -- `encode_utf16()` and `bytes()` -- so the
// choice of layer is made in the type system, in view, and a program cannot
// drift from one to the other by accident the way a string-concatenating
// escaper in a dynamic language can.
//
// The second half is the one std is strict about: rebuilding text FROM those
// escapes. Half a surrogate pair is a legal JSON token and a legal u16, and it
// is not a character -- `String::from_utf16` refuses it, and `from_utf8`
// refuses the truncated byte a half-written %XX leaves behind.
//
// Build:  rustc --edition 2024 escaping_into_ascii_rs.rs -o /tmp/escapes && /tmp/escapes

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{}", "-".repeat(72));
}

/// One \uXXXX per UTF-16 code unit, printable ASCII left alone -- the JSON rule.
fn json_escape(s: &str) -> String {
    s.encode_utf16()
        .map(|u| match u {
            0x20..=0x21 | 0x23..=0x5b | 0x5d..=0x7e => char::from(u as u8).to_string(),
            _ => format!("\\u{u:04x}"),
        })
        .collect()
}

/// One %XX per byte, RFC 3986's unreserved set left alone -- the URL rule.
fn percent_escape(s: &str) -> String {
    s.bytes()
        .map(|b| {
            if b.is_ascii_alphanumeric() || b"-._~".contains(&b) {
                char::from(b).to_string()
            } else {
                format!("%{b:02X}")
            }
        })
        .collect()
}

/// %XX back to bytes. Note the return type: bytes, not a String.
fn percent_decode(s: &str) -> Vec<u8> {
    let raw = s.as_bytes();
    let mut out = Vec::new();
    let mut i = 0;
    while i < raw.len() {
        if raw[i] == b'%' && i + 2 < raw.len() {
            let hex = std::str::from_utf8(&raw[i + 1..=i + 2]).unwrap_or("");
            if let Ok(b) = u8::from_str_radix(hex, 16) {
                out.push(b);
                i += 3;
                continue;
            }
        }
        out.push(raw[i]);
        i += 1;
    }
    out
}

fn main() {
    // -------------------------------------------------------------- 1
    head(1, "TWO ITERATORS, TWO SCHEMES, ONE STRING");
    for s in ["żółw", "😀"] {
        println!(
            "   {s:?} -- chars {}, bytes {}, utf-16 units {}",
            s.chars().count(),
            s.len(),
            s.encode_utf16().count()
        );
        println!("     .bytes()          -> {}", percent_escape(s));
        println!("     .encode_utf16()   -> {}", json_escape(s));
    }
    println!();
    println!("   Same text, two escapes, and neither can be turned into the");
    println!("   other without decoding first. `len()` is bytes and is what a");
    println!("   URL counts; `encode_utf16().count()` is code units and is what");
    println!("   a JSON escape counts; `chars().count()` is neither, and is the");
    println!("   only one of the three a person would call the length.");

    // -------------------------------------------------------------- 2
    head(2, "ABOVE U+FFFF THE PAIR BECOMES VISIBLE");
    for s in ["A", "é", "ż", "€", "😀"] {
        let c = s.chars().next().unwrap();
        let cp = format!("U+{:04X}", c as u32);
        println!(
            "   {cp:<8} {} byte(s)  {} unit(s)   json {:<14} {s:?}",
            s.len(),
            s.encode_utf16().count(),
            json_escape(s)
        );
    }
    println!();
    println!("   One `char` is always one Unicode scalar value and always four");
    println!("   bytes wide in memory, but it is one OR TWO code units on the");
    println!("   wire. \\ud83d\\ude00 is not two characters sitting together; it");
    println!("   is one character UTF-16 cannot hold in a single unit, written");
    println!("   into a format whose files are UTF-8 and contain no surrogates");
    println!("   anywhere.");

    // -------------------------------------------------------------- 3
    head(3, "STD REFUSES HALF A PAIR -- A JSON PARSER WILL HAND YOU ONE");
    let pair: [u16; 2] = [0xd83d, 0xde00];
    let lone: [u16; 1] = [0xd83d];
    println!("   String::from_utf16(&[d83d, de00])  -> {:?}", String::from_utf16(&pair));
    println!(
        "   String::from_utf16(&[d83d])        -> Err({:?})",
        String::from_utf16(&lone).unwrap_err().to_string()
    );
    println!();
    println!("   char::decode_utf16 names the offending unit rather than the string:");
    for (i, r) in char::decode_utf16(lone.iter().copied()).enumerate() {
        match r {
            Ok(c) => println!("     unit {i}: {c:?}"),
            Err(e) => println!("     unit {i}: unpaired surrogate U+{:04X}", e.unpaired_surrogate()),
        }
    }
    println!();
    println!("   That is the guard the escape form itself does not have.");
    println!("   \"\\ud83d\" alone is valid JSON syntax, so a parser may legally");
    println!("   hand a program half a character. In Rust it cannot become a");
    println!("   `String`, so the failure lands at the parse boundary instead of");
    println!("   three layers later at somebody else's encode.");

    // -------------------------------------------------------------- 4
    head(4, "UNESCAPING A URL ENDS AT THE VALIDATOR EVERY OTHER READ ENDS AT");
    for encoded in ["%C5%BC", "%C5", "caf%C3%A9"] {
        let bytes = percent_decode(encoded);
        print!("   {encoded:<11} -> {:02x?} -> String::from_utf8 ", bytes);
        match String::from_utf8(bytes) {
            Ok(s) => println!("Ok({s:?})"),
            Err(e) => println!("Err(valid_up_to = {})", e.utf8_error().valid_up_to()),
        }
    }
    println!();
    println!("   `percent_decode` returns `Vec<u8>` because that is honestly all");
    println!("   it knows: percent-decoding produces bytes, and the URL never");
    println!("   said what encoding made them. A truncated escape leaves a lead");
    println!("   byte with nothing behind it -- the same truncation case as a");
    println!("   short read from a file, arriving through a query string, and");
    println!("   caught by the same one line of validation.");
}
