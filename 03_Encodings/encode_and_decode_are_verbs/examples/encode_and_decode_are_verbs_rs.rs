// The same two verbs, with the table written into the type.
//
// Rust makes the two directions deliberately unequal. Encoding is free and
// takes no argument, because a `String` has exactly one encoding and the type
// says so. Decoding is a `Result` you are made to look at. And the one table
// Rust does NOT ship -- Latin-1 -- is one line to write, never fails, and is
// the mojibake mechanism spelled out.
//
// Build:  rustc --edition 2024 encode_and_decode_are_verbs_rs.rs -o /tmp/verbs && /tmp/verbs

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{}", "-".repeat(72));
}

/// Latin-1, in one line: every byte IS its code point. This is the whole table.
fn decode_latin1(bytes: &[u8]) -> String {
    bytes.iter().map(|&b| b as char).collect()
}

fn main() {
    let text: &str = "café";

    // -------------------------------------------------------------- 1
    head(1, "TWO NOUNS, AND THE TABLE IS PART OF THE TYPE");
    println!("   let text: &str = {text:?};");
    println!("     text.len()            = {}  <- BYTES, always", text.len());
    println!("     text.chars().count()  = {}  <- characters", text.chars().count());
    println!("     text.as_bytes()       = {:02x?}", text.as_bytes());
    println!();
    println!("   `&str` does not mean 'text'. It means 'bytes that are valid");
    println!("   UTF-8', and that promise is the type. There is no second kind");
    println!("   of String holding Latin-1, so no String ever has to say which");
    println!("   table it is -- which is why .len() can be bytes without lying.");

    // -------------------------------------------------------------- 2
    head(2, "ENCODING TAKES NO ARGUMENT");
    println!("   text.as_bytes()  -> {:02x?}", text.as_bytes());
    println!("   text.to_string().into_bytes()  -> same bytes, no copy of the data");
    println!();
    println!("   Python's .encode() needs a table and defaults to UTF-8. Rust");
    println!("   has nothing to pass: the bytes under a String ALREADY are the");
    println!("   UTF-8 ones. Encoding here is not a conversion, it is a cast of");
    println!("   the reader's attention from characters to the bytes beneath.");

    // -------------------------------------------------------------- 3
    head(3, "DECODING IS A Result, AND YOU ARE MADE TO LOOK AT IT");
    for raw in [
        vec![0x63, 0x61, 0x66, 0xc3, 0xa9], // café in UTF-8
        vec![0x63, 0x61, 0x66, 0xe9],       // café in Latin-1
    ] {
        print!("   String::from_utf8({:02x?})", raw);
        match String::from_utf8(raw.clone()) {
            Ok(s) => println!("\n     Ok({s:?})"),
            Err(e) => {
                let u = e.utf8_error();
                println!("\n     Err: valid up to byte {}, error_len {:?}", u.valid_up_to(), u.error_len());
                println!("     from_utf8_lossy -> {:?}", String::from_utf8_lossy(&raw));
            }
        }
    }
    println!();
    println!("   valid_up_to() is the offset to put in the bug report: everything");
    println!("   before it decoded, and the byte at it is the one to look at in a");
    println!("   hex dump. from_utf8_lossy never fails -- it substitutes U+FFFD,");
    println!("   which means the damage is now IN the string and the original");
    println!("   byte is gone.");

    // -------------------------------------------------------------- 4
    head(4, "THE TABLE RUST DOES NOT SHIP");
    let utf8_bytes = text.as_bytes();
    println!("   the same bytes {:02x?}, read under the other table:", utf8_bytes);
    println!("     as UTF-8   {:?}", std::str::from_utf8(utf8_bytes).unwrap());
    println!("     as Latin-1 {:?}   <- one line, and it cannot fail", decode_latin1(utf8_bytes));
    println!();
    println!("   fn decode_latin1(b: &[u8]) -> String {{ b.iter().map(|&b| b as char).collect() }}");
    println!();
    println!("   That is the entire Latin-1 decoder: every byte IS its code point.");
    println!("   It has no error case, so it accepts every file ever written and");
    println!("   returns something. Std does not ship it, and the reason is not");
    println!("   that it is hard -- it is that a decoder which cannot fail is a");
    println!("   decoder that cannot warn you.");

    // -------------------------------------------------------------- 5
    head(5, "WHERE THE TWO VERBS LIVE IN A RUST PROGRAM");
    println!("   fs::read_to_string(p) -> io::Result<String>   decodes; fails on bad UTF-8");
    println!("   fs::read(p)           -> io::Result<Vec<u8>>  does not decode");
    println!("   String::from_utf8     -> Result<String, _>    the decode, made explicit");
    println!("   str::as_bytes         -> &[u8]                the encode, free");
    println!();
    println!("   The sandwich is not advice here, it is the signatures: to get a");
    println!("   String out of bytes you pass through a Result, and the compiler");
    println!("   will not let you forget which side of the boundary you are on.");
}
