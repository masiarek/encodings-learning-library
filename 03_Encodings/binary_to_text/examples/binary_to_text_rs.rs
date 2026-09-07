// Base64 in std, because the point is the types rather than the table.
//
// The encoder below is twenty lines and no crate. What it shows that a crate
// call would hide: the input is `&[u8]` and the output is `String`, and both
// of those are claims. Bytes go in because base64 has never been told what
// text they are; a `String` comes out because every character it can produce
// is ASCII, so the result is valid UTF-8 by construction and cannot fail.
//
// Run:  rustc --edition 2024 binary_to_text_rs.rs -o /tmp/btt && /tmp/btt

const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const RULE: &str = "------------------------------------------------------------------------";

fn say(title: &str) {
    println!("\n{title}\n{RULE}\n");
}

/// Bytes in, text out. There is no error case and no `Result`.
fn encode(data: &[u8]) -> String {
    let mut out = String::with_capacity(data.len().div_ceil(3) * 4);
    for chunk in data.chunks(3) {
        // One 24-bit accumulator, zero-filled when the chunk is short.
        let mut v = 0u32;
        for (i, &b) in chunk.iter().enumerate() {
            v |= (b as u32) << (16 - 8 * i);
        }
        for i in 0..4 {
            if i <= chunk.len() {
                out.push(ALPHABET[((v >> (18 - 6 * i)) & 63) as usize] as char);
            } else {
                out.push('=');
            }
        }
    }
    out
}

/// Text in, bytes out — and strict, which means checking the bits nobody checks.
fn decode_strict(s: &str) -> Result<Vec<u8>, String> {
    let b = s.as_bytes();
    if b.len() % 4 != 0 || b.is_empty() {
        return Err(format!("length {} is not a positive multiple of four", b.len()));
    }
    let pad = b.iter().rev().take_while(|&&c| c == b'=').count();
    if pad > 2 {
        return Err(format!("{pad} padding characters"));
    }
    let mut out = Vec::with_capacity(b.len() / 4 * 3);
    let last = b.len() / 4 - 1;
    for (g, group) in b.chunks(4).enumerate() {
        // Only the final group may be padded.
        let pad = if g == last { pad } else { 0 };
        let mut v = 0u32;
        for (i, &c) in group.iter().enumerate() {
            let n = if c == b'=' {
                0
            } else {
                ALPHABET
                    .iter()
                    .position(|&a| a == c)
                    .ok_or_else(|| format!("{:?} is not in the alphabet", c as char))? as u32
            };
            v |= n << (18 - 6 * i);
        }
        for i in 0..(3 - pad) {
            out.push(((v >> (16 - 8 * i)) & 0xff) as u8);
        }
        // A group carries 24 bits; the data in it is 8 * (3 - pad). The rest
        // are defined to be zero, and nothing forces them to be -- so a strict
        // decoder is simply the one that looks.
        if pad > 0 && (v & ((1u32 << (8 * pad)) - 1)) != 0 {
            return Err(format!("non-canonical: the {} unused bits are not zero", 8 * pad));
        }
    }
    Ok(out)
}

fn main() {
    say("1. THE OUTPUT IS A String, AND NOTHING CAN MAKE IT NOT BE");

    let cases: [(&str, &[u8]); 3] = [
        ("\"café\" as UTF-8", "café".as_bytes()),
        ("the same word in Latin-1", &[0x63, 0x61, 0x66, 0xe9]),
        ("not text at all", &[0xc3, 0x28, 0xff]),
    ];
    for (label, bytes) in cases {
        println!("   {label:<26} {:<14} -> {}", hex(bytes), encode(bytes));
    }
    println!();
    println!("   The third row is the one that matters. Those three bytes are");
    println!("   not valid UTF-8 and never will be:");
    match String::from_utf8(vec![0xc3, 0x28, 0xff]) {
        Ok(s) => println!("     String::from_utf8 -> Ok({s:?})"),
        Err(e) => println!("     String::from_utf8 -> Err({})", e.utf8_error()),
    }
    println!("     encode(..)        -> {:?}   an infallible fn(&[u8]) -> String", encode(&[0xc3, 0x28, 0xff]));
    println!();
    println!("   That signature IS the definition of a binary-to-text encoding.");
    println!("   Anything that can hand back a `String` for every possible byte");
    println!("   sequence, without a Result, is one; anything that can fail on");
    println!("   some inputs is a text decoder wearing the wrong name.");

    say("2. THE INPUT IS &[u8], SO THERE IS NO CHARSET TO GET WRONG");

    println!("   {:<26} {}", "\"café\".as_bytes()", hex("café".as_bytes()));
    println!("   {:<26} {}", "encode(that)", encode("café".as_bytes()));
    println!("   {:<26} {}", "encode(Latin-1 bytes)", encode(&[0x63, 0x61, 0x66, 0xe9]));
    println!();
    println!("   Rust makes the missing question visible at the call site: you");
    println!("   cannot pass a `&str` to a function that wants `&[u8]` without");
    println!("   writing `.as_bytes()`, which is the moment the encoding was");
    println!("   chosen. In a language where the two are the same type, that");
    println!("   moment does not appear in the source at all.");

    say("3. DECODING RETURNS Vec<u8>, BECAUSE THAT IS ALL IT KNOWS");

    for s in ["Y2Fmw6k=", "Y2Fm6Q==", "wyj/"] {
        match decode_strict(s) {
            Ok(bytes) => {
                let as_text = match std::str::from_utf8(&bytes) {
                    Ok(t) => format!("valid UTF-8: {t:?}"),
                    Err(e) => format!("not UTF-8: {e}"),
                };
                println!("   {s:<10} -> {:<14} {as_text}", hex(&bytes));
            }
            Err(e) => println!("   {s:<10} -> Err({e})"),
        }
    }
    println!();
    println!("   Three successful decodes, and only the first is UTF-8. The");
    println!("   second is the SAME WORD in Latin-1 -- a base64 string a");
    println!("   partner could hand you as `café`, decoding to bytes that");
    println!("   are not valid text in the encoding you assumed. The third");
    println!("   was never text at all. base64 could not tell you any of");
    println!("   this, because base64 was never told; decode, then validate,");
    println!("   the same two-step that any read from a file or socket is.");

    say("4. STRICT MEANS CHECKING THE BITS NOBODY CHECKS");

    for s in ["QQ==", "QR==", "Qf==", "QQ=", "Q!=="] {
        match decode_strict(s) {
            Ok(bytes) => println!("   {s:<8} -> Ok({})", hex(&bytes)),
            Err(e) => println!("   {s:<8} -> Err({e})"),
        }
    }
    println!();
    println!("   QR== and Qf== are rejected HERE and accepted almost");
    println!("   everywhere else -- Python, Go, Java and the shell tool all");
    println!("   return 0x41 for them, because the bits the padding covers are");
    println!("   read and discarded rather than checked. Sixteen spellings of");
    println!("   one byte. The check that stops it is the four lines above.");
    println!();
    println!("   The rule that follows is short: compare decoded bytes, never");
    println!("   the encoded string. A signature, a cache key or an allow-list");
    println!("   over base64 TEXT is a comparison over a spelling, and the");
    println!("   spelling is not unique.");
}

fn hex(bytes: &[u8]) -> String {
    bytes
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect::<Vec<_>>()
        .join(" ")
}
