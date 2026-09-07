// std gives you the number door and not the other one, which is the whole
// argument on this page made by an omission.
//
// `u32::from_str_radix(s, 16)` is right there. There is no `Vec<u8>::from_hex`
// anywhere in std -- so the moment your hex string is DATA rather than a
// quantity, you write the loop yourself, and writing it is what forces you to
// decide about width, odd length and leading zeros.
//
// Run:  rustc --edition 2024 hex_number_or_bytes_rs.rs -o /tmp/hnb && /tmp/hnb

const RULE: &str = "------------------------------------------------------------------------";

fn say(title: &str) {
    println!("\n{title}\n{RULE}\n");
}

/// The door std does not give you. Strict on purpose: every rule here is one
/// `from_str_radix` does not have to have, because a number has no width.
fn from_hex(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 {
        return Err(format!("{} digits is not a whole number of bytes", s.len()));
    }
    let mut out = Vec::with_capacity(s.len() / 2);
    let b = s.as_bytes();
    for pair in b.chunks(2) {
        let hi = (pair[0] as char)
            .to_digit(16)
            .ok_or_else(|| format!("{:?} is not a hex digit", pair[0] as char))?;
        let lo = (pair[1] as char)
            .to_digit(16)
            .ok_or_else(|| format!("{:?} is not a hex digit", pair[1] as char))?;
        out.push((hi * 16 + lo) as u8);
    }
    Ok(out)
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    say("1. THE NUMBER DOOR IS STRICT ABOUT SPELLING AND BLIND TO WIDTH");

    let cases = ["41", "0x41", "4_1", " 41 ", "+41", "-41", "41\n", "4G", "", "00041"];
    println!("   {:<10} {}", "input", "u32::from_str_radix(s, 16)");
    for s in cases {
        let got = match u32::from_str_radix(s, 16) {
            Ok(v) => format!("Ok({v})"),
            Err(e) => format!("Err({e})"),
        };
        println!("   {:<10} {got}", format!("{s:?}"));
    }
    println!();
    println!("   Compare Python, which accepts the first seven of those. Rust");
    println!("   takes digits and an optional `+`, and nothing else -- no");
    println!("   prefix, no underscore, no whitespace, no newline. But look at");
    println!("   the last row: \"00041\" parses happily to 65, because leading");
    println!("   zeros are noise in a number and there is no width to violate.");
    println!("   Strictness about SPELLING is not strictness about MEANING.");

    say("2. THE WIDTH IS IN THE TYPE, NOT IN THE STRING");

    for (label, r) in [
        ("u8  \"ff\"", u8::from_str_radix("ff", 16).map(u32::from).map_err(|e| e.to_string())),
        ("u8  \"100\"", u8::from_str_radix("100", 16).map(u32::from).map_err(|e| e.to_string())),
        ("u32 \"100\"", u32::from_str_radix("100", 16).map_err(|e| e.to_string())),
    ] {
        println!("   {label:<12} -> {r:?}");
    }
    println!();
    println!("   \"100\" is three hex digits and fits no byte, and only the type");
    println!("   knows that. This is the width that a hex string does not");
    println!("   carry, supplied by the one place in Rust that always has it.");
    println!("   In a dynamically typed language nothing asks the question at");
    println!("   all, which is why the same string quietly becomes an int.");

    say("3. THE BYTE DOOR, WHICH YOU HAVE TO WRITE");

    for s in ["0041", "41", "123", "c3a9", "c3zz", ""] {
        let n = match u32::from_str_radix(s, 16) {
            Ok(v) => format!("{v}"),
            Err(_) => "-".to_string(),
        };
        let b = match from_hex(s) {
            Ok(v) if v.is_empty() => "nothing at all (0 bytes)".to_string(),
            Ok(v) => format!("{} ({} byte{})", hex(&v), v.len(), if v.len() == 1 { "" } else { "s" }),
            Err(e) => format!("Err({e})"),
        };
        println!("   {:<8} as a number {:>6}   as bytes {b}", format!("{s:?}"), n);
    }
    println!();
    println!("   Read the first two rows together: as numbers they are the");
    println!("   same value, as bytes they are different lengths, and the");
    println!("   difference is a NUL byte. The third is the odd-length case --");
    println!("   which is an error here, an error in Python, and a silent");
    println!("   truncation in `xxd -r -p`. The last is empty, which is a");
    println!("   legitimate zero-byte value and not a number at all.");

    say("4. WHY THE OMISSION IS THE ARGUMENT");

    println!("   std::primitive::u32::from_str_radix   exists");
    println!("   std::vec::Vec::<u8>::from_hex         does not exist");
    println!();
    println!("   Every hex-to-bytes crate in the ecosystem re-implements the");
    println!("   twenty lines above, and they differ from each other exactly");
    println!("   where this page says they would: whether whitespace is");
    println!("   skipped, whether an odd length is an error or is left-padded,");
    println!("   whether the output length is checked against an expected one.");
    println!("   Those are not implementation details. They are the questions");
    println!("   a hex string cannot answer about itself, and somebody has to.");
}
