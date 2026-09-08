// Rust has no UTF-7, so this is what writing one costs -- and what it exposes.
//
// The standard library ships no charset registry at all: the only text
// conversions in std are between UTF-8 and Unicode's own other forms. There is
// no `from_utf7`, and reaching for a crate would hide the interesting half,
// which is that a UTF-7 run is UTF-16 and Rust's `char` will not hold a lone
// surrogate. So section 2 hand-rolls the narrow case in std, and section 3
// shows the input where this decoder must refuse and Python's does not.
//
// Build:  rustc --edition 2024 utf7_and_the_seven_bit_transport_rs.rs
// Run:    ./utf7_and_the_seven_bit_transport_rs

const RULE: &str = "------------------------------------------------------------------------";

fn say(title: &str) {
    println!("\n{title}\n{RULE}");
}

/// The modified Base64 alphabet of RFC 2152: RFC 2045's, minus the '=' pad.
fn sextet(b: u8) -> Option<u32> {
    match b {
        b'A'..=b'Z' => Some((b - b'A') as u32),
        b'a'..=b'z' => Some((b - b'a') as u32 + 26),
        b'0'..=b'9' => Some((b - b'0') as u32 + 52),
        b'+' => Some(62),
        b'/' => Some(63),
        _ => None,
    }
}

/// Decode one UTF-7 byte string. Narrow on purpose: it implements the shift
/// mechanism and nothing else -- no charset detection, no error recovery.
fn decode_utf7(input: &[u8]) -> Result<String, String> {
    let mut out = String::new();
    let mut units: Vec<u16> = Vec::new(); // the UTF-16 code units of one run
    let mut bits: u32 = 0; // accumulated payload
    let mut nbits: u32 = 0; // how many of them are real
    let mut in_run = false;
    let mut i = 0;

    // A run is finished: turn its UTF-16 code units into characters.
    fn flush(units: &mut Vec<u16>, out: &mut String) -> Result<(), String> {
        for item in char::decode_utf16(units.drain(..)) {
            match item {
                Ok(c) => out.push(c),
                Err(e) => {
                    return Err(format!(
                        "unpaired surrogate U+{:04X} -- not a character, so not a `char`",
                        e.unpaired_surrogate()
                    ));
                }
            }
        }
        Ok(())
    }

    while i < input.len() {
        let b = input[i];
        if !in_run {
            if b == b'+' {
                in_run = true;
                bits = 0;
                nbits = 0;
                units.clear();
                i += 1;
                // "+-" is the escape for a literal '+'.
                if i < input.len() && input[i] == b'-' {
                    out.push('+');
                    in_run = false;
                    i += 1;
                }
            } else if b < 0x80 {
                out.push(b as char);
                i += 1;
            } else {
                return Err(format!("byte 0x{b:02X} is above 0x7F -- not UTF-7 at all"));
            }
            continue;
        }
        match sextet(b) {
            Some(v) => {
                bits = (bits << 6) | v;
                nbits += 6;
                if nbits >= 16 {
                    nbits -= 16;
                    units.push((bits >> nbits) as u16);
                }
                i += 1;
            }
            None => {
                // The run ends here. A terminating '-' is absorbed; anything
                // else is a character in its own right and is left to the loop.
                if bits & ((1 << nbits) - 1) != 0 {
                    return Err("non-zero padding bits -- ill-formed by RFC 2152".into());
                }
                flush(&mut units, &mut out)?;
                in_run = false;
                if b == b'-' {
                    i += 1;
                }
            }
        }
    }
    if in_run {
        if bits & ((1u32 << nbits) - 1) != 0 {
            return Err("non-zero padding bits -- ill-formed by RFC 2152".into());
        }
        flush(&mut units, &mut out)?;
    }
    Ok(out)
}

fn main() {
    say("1. WHAT std HAS, AND WHAT IT DOES NOT");

    println!("   Rust's standard library converts between UTF-8 and Unicode's");
    println!("   own other forms, and offers no other character table at all:");
    println!();
    let bytes = "café".as_bytes();
    let utf16: Vec<u16> = "café".encode_utf16().collect();
    println!("   std::str::from_utf8(&{:02x?})", bytes);
    println!("     -> {:?}", std::str::from_utf8(bytes).unwrap());
    println!("   String::from_utf16(&{utf16:04x?})");
    println!("     -> {:?}", String::from_utf16(&utf16).unwrap());
    println!("   std::str::from_utf7 / Encoding::UTF7 / anything charset-shaped");
    println!("     -> does not exist. Not deprecated, not feature-gated: absent.");
    println!();
    println!("   That absence is the finding, and it is deliberate. std carries");
    println!("   the encoding forms Unicode defines and stops there; every legacy");
    println!("   table -- UTF-7, Shift-JIS, cp1252 -- lives in a crate. Nothing");
    println!("   in a Rust program can decide a byte string is UTF-7 by accident,");
    println!("   because nothing in a Rust program knows what UTF-7 is.");

    say("2. SO HERE IS THE NARROW CASE, HAND-ROLLED IN std");

    let cases: [&[u8]; 5] = [
        b"caf+AOk-",
        b"+ADw-script+AD4-",
        b"<script>",
        b"+2D3eAA-",
        b"1 +- 1",
    ];
    for input in cases {
        let shown = String::from_utf8_lossy(input);
        match decode_utf7(input) {
            Ok(s) => println!("   {shown:<18} -> {s:?}"),
            Err(e) => println!("   {shown:<18} -> refused: {e}"),
        }
    }
    println!();
    println!("   Line two is the whole security story in one row: sixteen bytes");
    println!("   of unremarkable ASCII, and a tag on the other side. Line three");
    println!("   is the same tag spelled directly, which is what an encoder");
    println!("   writes. Both are legal UTF-7 and they are not the same bytes.");

    say("3. WHERE RUST AND PYTHON PART, AND WHY");

    let lone: &[u8] = b"+2D0-";
    match decode_utf7(lone) {
        Ok(s) => println!("   {:?} -> {s:?}", String::from_utf8_lossy(lone)),
        Err(e) => println!("   \"+2D0-\" -> refused: {e}"),
    }
    println!("   char::from_u32(0xD83D) -> {:?}", char::from_u32(0xD83D));
    println!();
    println!("   The Python block on this page accepts those same five bytes");
    println!("   and hands back a str holding one lone surrogate -- a string");
    println!("   that cannot then be encoded to UTF-8. Rust cannot reach that");
    println!("   state: `char` is a Unicode SCALAR value, the surrogate range");
    println!("   is a hole in it, and so the refusal happens at the decode");
    println!("   instead of two stages later. Same input, same specification,");
    println!("   two different places to find out -- which is a differential");
    println!("   between languages, inside a format built to be carried");
    println!("   between machines.");
}
