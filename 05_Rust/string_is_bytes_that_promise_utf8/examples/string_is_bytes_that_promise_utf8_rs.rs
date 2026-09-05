// `String` is a Vec<u8> with one promise attached: the bytes are valid UTF-8.
//
// Build & run:  rustc --edition 2024 string_is_bytes_that_promise_utf8_rs.rs && ./string_is_bytes_that_promise_utf8_rs

fn main() {
    let noodles = "noodles".to_string();
    let oodles = &noodles[1..];
    let poodles = "ಠ_ಠ";

    println!("1. THREE STRINGS, AND THE TWO COUNTS THAT DISAGREE");
    for (name, s) in [("noodles", noodles.as_str()), ("oodles", oodles), ("poodles", poodles)] {
        println!(
            "   {name:<8} {s:<10} len() = {:<2} bytes    chars().count() = {} chars",
            s.len(),
            s.chars().count()
        );
    }
    println!("   noodles and poodles report the SAME len(). One is 7 characters, the other is 3.");
    println!();

    println!("2. len() IS A BYTE COUNT, AND HERE ARE THE BYTES");
    for (name, s) in [("noodles", noodles.as_str()), ("poodles", poodles)] {
        let hex: Vec<String> = s.as_bytes().iter().map(|b| format!("{b:02X}")).collect();
        println!("   {name:<8} {}", hex.join(" "));
    }
    println!("   'ಠ' is U+0CA0, and UTF-8 spends three bytes on it. 3 + 1 + 3 = 7.");
    println!();

    println!("3. THE PROMISE, MADE VISIBLE AS THREE CONVERSIONS");
    let owned: Vec<u8> = String::from(poodles).into_bytes();
    println!("   as_bytes()   -> &[u8]     borrow them:  {} bytes, still promised", poodles.as_bytes().len());
    println!("   into_bytes() -> Vec<u8>   own them:     {} bytes, promise dropped with the String", owned.len());
    println!("   from_utf8()  -> Result    make the promise again — the only direction that can FAIL,");
    println!("                             because it is the only one that has to CHECK.");
    println!();

    println!("4. SO from_utf8 IS WHERE THE PROMISE IS KEPT");
    let good = poodles.as_bytes().to_vec();
    match String::from_utf8(good.clone()) {
        Ok(s) => println!("   from_utf8({} bytes) -> Ok({s:?})", good.len()),
        Err(e) => println!("   unexpected: {e}"),
    }
    let truncated = good[..good.len() - 1].to_vec(); // drop the last byte of the last 'ಠ'
    match String::from_utf8(truncated.clone()) {
        Ok(s) => println!("   unexpected: {s:?}"),
        Err(e) => {
            let ue = e.utf8_error();
            println!("   from_utf8({} bytes) -> Err: {ue}", truncated.len());
            println!("   valid_up_to() = {}  — the first 4 bytes are fine; the cut character is not", ue.valid_up_to());
        }
    }
    println!();

    println!("5. &str IS TO String WHAT &[u8] IS TO Vec<u8>");
    println!("   String  owns its bytes and can grow      &str    borrows a run of them");
    println!("   Vec<u8> owns its bytes and can grow      &[u8]   borrows a run of them");
    println!("   The difference between the two rows is the promise, and nothing else.");
    println!("   oodles borrows bytes 1..7 of noodles: {oodles:?}  (no copy was made)");
    println!();

    println!("6. b\"...\" IS BYTES WITH NO PROMISE, SO IT HAS NO CHARACTERS");
    let raw: &[u8; 7] = b"noodles";
    println!("   b\"noodles\" is &[u8; {}]  first byte = {}", raw.len(), raw[0]);
    println!("   It has .len() and .iter(), but no .chars() — nothing has promised these bytes are text.");
    println!();

    println!("7. TWO THINGS THE COMPILER REFUSES, AND WHY");
    println!("   s[0]        `String` cannot be indexed by a number: byte 0 of 'ಠ_ಠ' is E0, which is not a character.");
    println!("   &s[0..2]    compiles, then PANICS at run time: byte 2 is inside 'ಠ'. Slicing is by byte, and the");
    println!("               promise is checked at the cut — see the `Slicing by byte` lesson.");
}
