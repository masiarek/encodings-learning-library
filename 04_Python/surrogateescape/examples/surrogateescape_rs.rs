//! The same undecodable filename, in a language that has no surrogateescape.
//!
//! Rust cannot do PEP 383's trick: `char` refuses the code points it needs.
//! What it does instead is keep the bytes in a different type and make you
//! say, at each use, whether you want text or not.

use std::borrow::Cow;
use std::ffi::OsStr;
use std::os::unix::ffi::OsStrExt;
use std::path::Path;

const RULE: &str = "------------------------------------------------------------------------";

// The same twelve bytes the Python example reads: "cafe au lait" with the
// e-acute written in Latin-1, so it is the single byte 0xE9.
const RAW: &[u8] = b"caf\xe9 au lait";

fn hex(bytes: &[u8]) -> String {
    bytes
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    // Built at runtime rather than passed as a literal: rustc has a lint,
    // `invalid_from_utf8`, that spots `str::from_utf8` on a byte literal it can
    // see is invalid and warns at compile time. Nice, and in the way here.
    let raw: Vec<u8> = RAW.to_vec();

    println!("1. THE SAME TWELVE BYTES");
    println!("{RULE}");
    println!("     {}", hex(&raw));
    println!();
    match std::str::from_utf8(&raw) {
        Ok(s) => println!("     decoded: {s}"),
        Err(e) => {
            println!("     str::from_utf8      Err({e})");
            println!("     valid_up_to()       {}", e.valid_up_to());
            println!("     error_len()         {:?}", e.error_len());
        }
    }
    println!();
    println!("   Same verdict as Python's strict decode, with the offset in a");
    println!("   method rather than in a sentence.");
    println!();

    println!("2. THE ESCAPE HAS NOWHERE TO LIVE");
    println!("{RULE}");
    println!("   PEP 383 parks the byte at U+DCE9. In Rust that value is not a");
    println!("   char, and the constructor says so rather than producing one:");
    println!();
    println!("     char::from_u32(0xDCE9)   {:?}", char::from_u32(0xDCE9));
    println!("     char::from_u32(0x00E9)   {:?}", char::from_u32(0x00E9));
    println!();
    println!("   A char is a Unicode scalar value, and the surrogate range is");
    println!("   the part of the code space that definition removes. So the");
    println!("   trick is not merely absent from std -- there is no value for");
    println!("   it to use. String is bytes that promise UTF-8, and a promise");
    println!("   with an escape hatch in it is not one.");
    println!();

    println!("3. WHAT std OFFERS INSTEAD: LOSSY, AND HONEST ABOUT IT");
    println!("{RULE}");
    let lossy = String::from_utf8_lossy(RAW);
    println!("     from_utf8_lossy          {lossy:?}");
    println!("     its bytes                {}", hex(lossy.as_bytes()));
    println!("     same as we started with? {}", lossy.as_bytes() == RAW);
    println!();
    println!("   One byte in, three bytes out: U+FFFD is EF BF BD. This is");
    println!("   Python's errors='replace', and like it, it is a one-way door.");
    println!("   Nothing downstream can tell which byte was lost, or how many");
    println!("   there were.");
    println!();
    println!("   The one piece of information std does hand back is whether");
    println!("   anything was replaced at all, and it is in the return type:");
    println!("   Cow::Borrowed means the bytes were already UTF-8 and nothing");
    println!("   was allocated, Cow::Owned means a replacement was made.");
    println!();
    for (label, sample) in [("caf\\xe9 au lait", RAW), ("caf au lait", b"caf au lait")] {
        let cow = String::from_utf8_lossy(sample);
        let variant = match cow {
            Cow::Borrowed(_) => "Cow::Borrowed  (nothing was replaced)",
            Cow::Owned(_) => "Cow::Owned     (a byte was replaced)",
        };
        println!("     {label:<17}{variant}");
    }
    println!();

    println!("4. THE ANSWER IS A SECOND TYPE, NOT A SECOND ENCODING");
    println!("{RULE}");
    let name: &OsStr = OsStr::from_bytes(RAW);
    let path = Path::new(name);
    println!("     OsStr::from_bytes(RAW)");
    println!("     name.len()               {}", name.len());
    println!("     name.to_str()            {:?}", name.to_str());
    println!("     name.as_bytes()          {}", hex(name.as_bytes()));
    println!("     byte-identical to RAW?   {}", name.as_bytes() == RAW);
    println!();
    println!("   That last line is the whole design. OsStr round-trips because");
    println!("   it never converted: on Unix it IS the bytes, and to_str()");
    println!("   returns Option rather than guessing. Python carries the byte");
    println!("   through a str by widening what a str may contain; Rust carries");
    println!("   it by refusing to call it a str at all.");
    println!();
    println!("   Path is the same bytes with path methods on it, so a name you");
    println!("   cannot print is still one you can open, split and rename:");
    println!();
    println!("     path.extension()         {:?}", path.extension());
    println!("     path.file_name()         {:?}", path.file_name().is_some());
    println!("     path.display()           {}", path.display());
    println!();
    println!("   display() is the show-it-anyway door, and it is lossy by");
    println!("   contract -- the U+FFFD above, not the bytes. It is for humans,");
    println!("   the way Python's backslashreplace is; neither is a value to");
    println!("   pass on to anything.");
    println!();

    println!("5. THE TRADE, IN ONE TABLE");
    println!("{RULE}");
    println!("     question                     Python 3            Rust");
    println!("     one type or two?             str                 String + OsString");
    println!("     undecodable byte becomes     U+DC80..U+DCFF      nothing; it stays a byte");
    println!("     reversible?                  yes, same handler   yes, no conversion happened");
    println!("     can it leak into text?       yes -- section 9    no; the types differ");
    println!("     cost                         a str may hold a    every use site must say");
    println!("                                  non-character       which of the two it wants");
}
