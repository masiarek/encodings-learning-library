// Only one of these is a dot -- and in UTF-8 no other character can contain
// its byte.
//
// The Python half of this lesson asks three readers whether a character is a
// dot, and gets three answers. This half asks the question underneath all of
// them: can a scan for the byte 0x2E ever land inside some other character?
// It answers by encoding every Unicode scalar value there is. That is
// arithmetic on the number line, not a lookup in the Unicode table, so the
// count cannot move when rustc's copy of the table does.

fn bar() {
    println!("{}", "-".repeat(72));
}

fn main() {
    // U+002E FULL STOP, then four characters drawn like it:
    // ONE DOT LEADER, HORIZONTAL ELLIPSIS, IDEOGRAPHIC FULL STOP,
    // FULLWIDTH FULL STOP.
    let chars = ['.', '\u{2024}', '\u{2026}', '\u{3002}', '\u{FF0E}'];

    // ------------------------------------------------------------------ 1
    println!("1. A u8 AND A char, AND SPLITTING ON EACH");
    bar();
    println!("   b'.'            {:#04x}  (a u8)", b'.');
    println!("   '.' as u32      U+{:04X}  (a char)", '.' as u32);
    println!();
    println!("   char     len_utf8  UTF-8        is_ascii_punctuation  \"a?b\".split('.')");
    for c in chars {
        let word = format!("a{c}b");
        let hex: Vec<String> = c
            .to_string()
            .bytes()
            .map(|b| format!("{b:02x}"))
            .collect();
        let pieces = word.split('.').count();
        println!(
            "   U+{:04X}   {:<8}  {:<11}  {:<20}  {} {}",
            c as u32,
            c.len_utf8(),
            hex.join(" "),
            c.is_ascii_punctuation(),
            pieces,
            if pieces == 1 { "piece" } else { "pieces" }
        );
    }
    println!();
    println!("   All five in one string, split two ways:");
    let all: String = chars.iter().flat_map(|&c| ['x', c]).chain(['x']).collect();
    let by_char = all.split('.').count();
    let by_byte = all.as_bytes().split(|&b| b == b'.').count();
    println!("   str::split('.')                        {by_char} pieces");
    println!("   as_bytes().split(|&b| b == b'.')       {by_byte} pieces");
    println!();
    println!("   The same answer from the char and from the byte. Section 2 is why");
    println!("   that is not luck for these five, but true of every string.");

    // ------------------------------------------------------------------ 2
    println!();
    println!("2. EVERY SCALAR VALUE, ENCODED, AND SEARCHED FOR 0x2E");
    bar();
    let mut scalars = 0u32;
    let mut multibyte = 0u32;
    let mut ascii_byte_in_multibyte = 0u32;
    let mut holding_2e: Vec<u32> = Vec::new();
    let mut buf = [0u8; 4];
    for n in 0..=0x10FFFFu32 {
        let Some(c) = char::from_u32(n) else { continue };
        scalars += 1;
        let bytes = c.encode_utf8(&mut buf).as_bytes();
        if bytes.len() > 1 {
            multibyte += 1;
            if bytes.iter().any(|&b| b < 0x80) {
                ascii_byte_in_multibyte += 1;
            }
        }
        if bytes.contains(&b'.') {
            holding_2e.push(n);
        }
    }
    let found: Vec<String> = holding_2e.iter().map(|n| format!("U+{n:04X}")).collect();
    println!("   scalar values encoded                      {scalars}");
    println!("   of those, encoded in more than one byte    {multibyte}");
    println!("   ...with any byte below 0x80 among them     {ascii_byte_in_multibyte}");
    println!("   scalar values whose UTF-8 holds a 0x2E     {}  ({})", holding_2e.len(), found.join(", "));
    println!();
    println!("   Every byte of a multi-byte UTF-8 sequence is 0x80 or above, so the");
    println!("   byte 0x2E appears in exactly one character's encoding: the full stop");
    println!("   itself. A byte scan for '.' can never cut a look-alike in half --");
    println!("   and, by the same rule, can never find one. Nothing on char says");
    println!("   U+2024 resembles U+002E, and std has no normalization to say it");
    println!("   either.");
}
