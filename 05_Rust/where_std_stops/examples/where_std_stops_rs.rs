// Nine text jobs, and how far std gets on each one with bare rustc and no crate.
//
// This is the BASELINE for the lesson page. The crates the page is about are
// measured on the page in dated fences, because the runner has no Cargo and the
// examples here never will (CONTRIBUTING.md).
//
// Nothing here reads a Unicode property a newer table could change: the two
// char methods called on non-ASCII input are is_alphabetic on ż and is_numeric
// on an Arabic-Indic digit, both letters and digits since Unicode 1.1.
//
// Build & run:  rustc --edition 2024 where_std_stops_rs.rs && ./where_std_stops_rs

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    println!("1. LEGACY ENCODINGS -- std decodes UTF-8 and UTF-16, plus one table by accident");
    let latin1: &[u8] = b"caf\xe9";
    let s: String = latin1.iter().map(|&b| b as char).collect();
    println!("   b as char over {}         -> {s:?}    Latin-1 IS the first 256 code points", hex(latin1));
    let cp1252: &[u8] = b"Preis\x85 100\x80";
    let s: String = cp1252.iter().map(|&b| b as char).collect();
    println!("   the same cast over cp1252 bytes  -> {s:?}");
    println!("   0x80 became U+0080, a C1 control, not the euro sign. windows-1252 needs a");
    println!("   32-entry table for 80..9f, windows-1250 a 128-entry one, Shift_JIS a state");
    println!("   machine. std ships none of them: from_utf8, from_utf16, and that is all.");
    let cp1250_owned: Vec<u8> = b"Za\xbf\xf3\xb3\xe6".to_vec(); // owned, so the invalid_from_utf8 lint has no literal to see
    let cp1250: &[u8] = &cp1250_owned;
    let verdict = std::str::from_utf8(cp1250).map(|_| "Ok").map_err(|e| (e.valid_up_to(), e.error_len()));
    println!("   from_utf8({})      -> {verdict:?}", hex(cp1250));
    println!();

    println!("2. DETECTION -- validation is the only test std has, and it only names UTF-8");
    for (name, b) in [("utf8", "café".as_bytes()), ("latin1", latin1), ("cp1250", cp1250), ("ascii", &b"plain"[..])] {
        println!("   {name:7} {:20} valid UTF-8: {}", hex(b), std::str::from_utf8(b).is_ok());
    }
    println!("   'Not UTF-8' is where std stops. Which 8-bit table the bytes are in instead");
    println!("   is a guess from letter statistics, and the page measures Firefox's guesser.");
    println!();

    println!("3. NORMALIZATION -- two spellings of one word, and == has one opinion");
    let a = "café";
    let b = "cafe\u{301}";
    println!("   {a:?} == {b:?} -> {}", a == b);
    println!("   bytes {} vs {}, chars {} vs {}", a.len(), b.len(), a.chars().count(), b.chars().count());
    println!("   std has no nfc(). Python's unicodedata.normalize is a standard-library");
    println!("   call; in Rust it is a crate, and the page measures it.");
    println!();

    println!("4. WHAT A PERSON CALLS ONE CHARACTER -- three rulers in std, and none is that one");
    let zwj = "\u{200d}";
    let family = format!("👨{zwj}👩{zwj}👧{zwj}👦");
    for (label, s) in [("e + acute", "e\u{301}"), ("flag PL", "🇵🇱"), ("family", family.as_str()), ("Devanagari kshi", "क्षि"), ("thumbs up + tone", "👍🏽")] {
        println!("   {label:18} bytes {:2}  chars {:2}  utf16 {:2}   a person sees 1", s.len(), s.chars().count(), s.encode_utf16().count());
    }
    let sent = "can't stop, won't stop; 3.14 isn't 3,14. 東京都";
    println!("   split_whitespace: {:?}", sent.split_whitespace().collect::<Vec<_>>());
    println!("   Whitespace is the only word boundary std knows. UAX #29's boundaries, which");
    println!("   keep can't and 3.14 whole and drop the punctuation, are a crate.");
    println!();

    println!("5. COLUMNS -- {{:<8}} pads by chars().count(), which is the wrong ruler");
    for s in ["café", "日本語", family.as_str(), "🇵🇱"] {
        println!("   |{s:<8}|  chars {}", s.chars().count());
    }
    println!("   The bars are meant to line up. A terminal draws 日本語 six columns wide and");
    println!("   the family two. std has no width function and no East_Asian_Width property;");
    println!("   both are a crate.");
    println!();

    println!("6. BYTES THAT ARE MOSTLY TEXT -- std has the pieces, and each one is a line");
    let raw: &[u8] = b"caf\xe9 au lait\nZa\xbf\xf3\xb3\xe6 g\xea\x9cl\xb9\r\nplain";
    println!("   lines:           {}", raw.split(|&b| b == b'\n').count());
    println!("   find \"au\":       {:?}", raw.windows(2).position(|w| w == b"au"));
    let chunks: Vec<(&str, String)> = raw.utf8_chunks().map(|c| (c.valid(), hex(c.invalid()))).collect();
    println!("   utf8_chunks():   {chunks:?}");
    println!("   from_utf8_lossy: {:?}", String::from_utf8_lossy(raw));
    println!("   No lines(), no find(), no chars() on a [u8] -- but since Rust 1.79");
    println!("   utf8_chunks() is std, and it is the loop that bstr and from_utf8_lossy share.");
    println!();

    println!("7. VALIDATION -- std checks every byte, and what that costs is not in this key");
    let unit = "Zażółć gęślą jaźń. ";
    let big = unit.repeat(1 << 20);
    println!("   from_utf8 over {} MB of Polish text -> {}", big.len() / (1024 * 1024), if std::str::from_utf8(big.as_bytes()).is_ok() { "Ok" } else { "Err" });
    println!("   How long it took, and how long simdutf8 takes over the same bytes, is on");
    println!("   the page in a dated fence: a speed is a fact about one machine.");
    println!();

    println!("8. REGEX -- there is none in std; char predicates cover the small cases");
    let s = "Zażółć gęślą jaźń — can't stop";
    let letters: Vec<&str> = s.split(|c: char| !c.is_alphabetic()).filter(|w| !w.is_empty()).collect();
    println!("   split on !is_alphabetic: {letters:?}");
    println!("   is_alphabetic('ż') = {}   is_numeric('٣') = {}", 'ż'.is_alphabetic(), '٣'.is_numeric());
    println!("   That is \\p{{L}}+ and \\p{{N}} by hand. Anything with structure -- alternation,");
    println!("   repetition, a class named by script -- is the regex crate, measured on the page.");
    println!();

    println!("9. SORTING -- sort() is code point order, and std has no locale to ask");
    let mut words = vec!["zebra", "Zebra", "łódź", "lód", "Łukasiewicz", "Zawadzki", "żaba", "ćma", "cmentarz"];
    words.sort();
    println!("   sort():                  {}", words.join(" "));
    words.sort_by_key(|w| w.to_lowercase());
    println!("   sort_by_key(lowercase):  {}", words.join(" "));
    println!("   ł, ć and ż land after z in both. A Polish dictionary puts ć after c and ł");
    println!("   after l, and the rules that know that are locale data -- which is why std");
    println!("   does not carry them and ICU4X does. Measured on the page.");
}
