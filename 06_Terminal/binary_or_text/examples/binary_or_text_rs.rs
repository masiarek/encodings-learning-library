// Binary or text: Rust has no text mode, so it asks the question in one place.
//
// A File moves bytes. Whether those bytes are text is decided only when you
// ask for a String, and the question is then always the same one: are they
// well-formed UTF-8? The filename is never an input.
//
// Build & run:  rustc --edition 2024 binary_or_text_rs.rs && ./binary_or_text_rs

use std::fs;
use std::io::Write;

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    let dir = std::env::temp_dir().join(format!("binary_or_text_rs_{}", std::process::id()));
    fs::create_dir_all(&dir).expect("temp dir");
    let path = dir.join("output.txt");

    println!("1. File::create WRITES BYTES, WHATEVER THE NAME SAYS");
    let mut f = fs::File::create(&path).expect("create");
    f.write_all(&[0xc0, 0xff, 0xee]).expect("write");
    drop(f);
    let back = fs::read(&path).expect("read");
    println!("   wrote c0 ff ee to output.txt; fs::read returns {}", hex(&back));
    println!("   No mode was asked for, and there is none to ask for: a File is");
    println!("   bytes in and bytes out, whatever its name.");
    println!();

    println!("2. ASKING FOR A String IS ASKING 'IS THIS UTF-8?'");
    match fs::read_to_string(&path) {
        Ok(s) => println!("   fs::read_to_string -> Ok({s:?})"),
        Err(e) => println!("   fs::read_to_string -> Err, kind {:?}", e.kind()),
    }
    match std::str::from_utf8(&back) {
        Ok(s) => println!("   str::from_utf8     -> Ok({s:?})"),
        Err(e) => println!(
            "   str::from_utf8     -> Err, valid_up_to {}, error_len {:?}",
            e.valid_up_to(),
            e.error_len()
        ),
    }
    println!("   valid_up_to 0: not one byte of it is UTF-8. error_len Some(1): the");
    println!("   first bad sequence is one byte long - the c0 on its own.");
    println!();

    println!("3. from_utf8_lossy SAYS YES BY REPLACING");
    let lossy = String::from_utf8_lossy(&back);
    let marks = lossy.chars().filter(|&c| c == char::REPLACEMENT_CHARACTER).count();
    println!(
        "   {} chars, {} of them U+FFFD, {} bytes: {}",
        lossy.chars().count(),
        marks,
        lossy.len(),
        hex(lossy.as_bytes())
    );
    println!("   Three bytes in, nine out, and nothing of the original left in them.");
    println!();

    println!("4. LATIN-1 IS THE TABLE WHERE `b as char` IS THE WHOLE DECODER");
    let latin1: String = back.iter().map(|&b| b as char).collect();
    let points: Vec<String> = latin1.chars().map(|c| format!("U+{:04X}", c as u32)).collect();
    println!("   {:?}   {}", latin1, points.join(" "));
    fs::write(&path, &latin1).expect("write");
    println!("   fs::write of that String -> {}", hex(&fs::read(&path).expect("read")));
    println!("   Every u8 is a char under Latin-1, so this step cannot fail. Written");
    println!("   back, the three letters are six bytes, because a String is UTF-8.");

    fs::remove_dir_all(&dir).expect("cleanup");
}
