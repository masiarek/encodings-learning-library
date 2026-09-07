// U+0000 in Rust: an ordinary char, valid UTF-8, and refused at every C boundary.
//
// Build & run:  rustc --edition 2024 the_nul_byte_rs.rs -o /tmp/nulbyte && /tmp/nulbyte

use std::ffi::{CStr, CString};

fn main() {
    println!("1. '\\0' IS AN ORDINARY char, AND ORDINARY UTF-8");
    let nul = '\0';
    println!("   char::from_u32(0)            = {:?}", char::from_u32(0));
    println!("   nul as u32                   = {}", nul as u32);
    println!("   nul.len_utf8()               = {}   one byte, like any ASCII character", nul.len_utf8());
    println!("   str::from_utf8(&[0])         = {:?}", std::str::from_utf8(&[0u8]));
    println!("   nul.is_control()             = {}", nul.is_control());
    println!("   No validator on this page rejects it. Being valid is not the problem.");
    println!();

    println!("2. A str HOLDS IT WITHOUT COMPLAINT");
    let s = "ab\0cd";
    println!("   s = {:?}", s);
    println!("   s.len()                      = {}   bytes", s.len());
    println!("   s.chars().count()            = {}   characters", s.chars().count());
    println!("   s.split('\\0')                = {:?}", s.split('\0').collect::<Vec<_>>());
    println!();

    println!("3. THE BOUNDARIES WHERE RUST STOPS YOU");
    match CString::new(s) {
        Ok(_) => println!("   CString::new(s)              -> Ok"),
        Err(e) => println!(
            "   CString::new(s)              -> Err, nul_position = {}",
            e.nul_position()
        ),
    }
    match std::fs::File::open("a\0b") {
        Ok(_) => println!("   File::open(\"a\\0b\")           -> Ok"),
        Err(e) => println!("   File::open(\"a\\0b\")           -> Err, kind = {:?}", e.kind()),
    }
    println!("   Rust refuses at the door rather than hand C a string it will cut short.");
    println!("   Python raises ValueError at the same two places, for the same reason.");
    println!();

    println!("4. READING A C STRING BACK OUT OF A BUFFER");
    let buffer = b"name.txt\0\0\0\0\0\0\0\0";
    let hex: Vec<String> = buffer.iter().map(|b| format!("{b:02x}")).collect();
    println!("   buffer -- 16 bytes of a fixed-width record field:");
    println!("     {}", hex.join(" "));
    match CStr::from_bytes_until_nul(buffer) {
        Ok(c) => println!(
            "   CStr::from_bytes_until_nul   -> {:?}, {} bytes",
            c.to_str().unwrap(),
            c.to_bytes().len()
        ),
        Err(e) => println!("   CStr::from_bytes_until_nul   -> Err {:?}", e),
    }
    println!("   The padding is still in the buffer. The NUL is where the value ends.");
    println!();

    println!("5. NUL AS THE SEPARATOR");
    let stream = b"holiday\nphotos.txt\0notes.txt\0";
    let names: Vec<String> = stream
        .split(|&b| b == 0)
        .filter(|part| !part.is_empty())
        .map(|part| String::from_utf8_lossy(part).into_owned())
        .collect();
    println!("   split on b'\\0'               -> {:?}", names);
    println!("   Two names, and the first one contains a newline. That is what");
    println!("   `find -print0` produces and what any -0 reader has to expect.");
}
