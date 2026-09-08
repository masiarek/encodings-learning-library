// `OsStr` and `Path` are the types for text the operating system never promised
// was text. This program is about them as an API — the three doors out, what a
// `Cow` is actually deciding, and the one comparison that surprises everybody.
//
// Nothing here touches the filesystem: every value is built in memory, so the
// answers are the types' and not this machine's.
//
// It is a UNIX program: std::os::unix::ffi is how you build an OsStr out of
// arbitrary bytes, and there is no such constructor on Windows — which is
// itself section 7's point. CI runs Ubuntu and macOS, so both runners compile
// it; a Windows reader gets a compile error, not a wrong answer.
//
// Build & run:  rustc --edition 2024 osstr_path_and_wtf8_rs.rs && ./osstr_path_and_wtf8_rs

use std::borrow::Cow;
use std::ffi::{OsStr, OsString};
use std::os::unix::ffi::{OsStrExt, OsStringExt};
use std::path::{Path, PathBuf};

/// A filename a Unix kernel will accept and a `String` will not: `café.txt`
/// with the `é` written as Latin-1 rather than UTF-8.
const RAW: &[u8] = b"caf\xe9.txt";

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    println!("1. FOUR PAIRS, ONE SHAPE — OWNED, AND BORROWED");
    println!("   {:<10} {:<10} {:>7} {:>8}   what has been promised about the bytes", "owned", "borrowed", "owned", "borrow");
    println!("   {:<10} {:<10} {:>7} {:>8}   {}", "Vec<u8>", "&[u8]", size_of::<Vec<u8>>(), size_of::<&[u8]>(), "nothing at all");
    println!("   {:<10} {:<10} {:>7} {:>8}   {}", "OsString", "&OsStr", size_of::<OsString>(), size_of::<&OsStr>(), "whatever the OS accepts as a name");
    println!("   {:<10} {:<10} {:>7} {:>8}   {}", "PathBuf", "&Path", size_of::<PathBuf>(), size_of::<&Path>(), "the same, plus separators mean something");
    println!("   {:<10} {:<10} {:>7} {:>8}   {}", "String", "&str", size_of::<String>(), size_of::<&str>(), "valid UTF-8");
    println!("   The same two-type pattern four times over, and the same two sizes: an owned");
    println!("   one is a pointer, length and capacity; a borrowed one is a pointer and a");
    println!("   length. Only the last row has made a promise, and only it can be printed");
    println!("   without a decision. Take &Path in a signature the way you take &str.");
    println!();

    let name = OsStr::from_bytes(RAW);
    println!("2. THREE DOORS OUT OF AN OsStr, AND ONLY ONE HANDS IT BACK");
    println!("   the name: {}   ({} bytes)", hex(RAW), name.len());
    println!("   to_str()          {:?}", name.to_str());
    println!("      -> Option<&str>. None means 'not UTF-8'. You have LOST the name unless");
    println!("         you still hold the OsStr — the None carries nothing.");
    let lossy = name.to_string_lossy();
    println!("   to_string_lossy() {lossy:?}");
    println!("      -> Cow<str>. Always succeeds. The e9 has become ef bf bd:");
    println!("         {}", hex(lossy.as_bytes()));
    println!("         You have CORRUPTED the name. Open that and you get ENOENT.");
    match OsString::from_vec(RAW.to_vec()).into_string() {
        Ok(s) => println!("   into_string()     Ok({s:?})"),
        Err(back) => println!(
            "   into_string()     Err(OsString) — {} bytes, identical to the input? {}",
            back.len(),
            back.as_bytes() == RAW
        ),
    }
    println!("      -> Result<String, OsString>. The failure case RETURNS THE VALUE. That is");
    println!("         the door to use when you need a String and might not get one, because");
    println!("         it is the only one that leaves you able to carry on with the name.");
    println!("   Same three contracts as from_utf8 / from_utf8_lossy / the unsafe one, one");
    println!("   type along — check, replace, or (here) check and hand it back.");
    println!();

    println!("3. THE Cow IS A DECISION, AND IT TELLS YOU WHICH ONE IT MADE");
    println!("   {:<27} {:<10}   {}", "name", "Cow", "what that means for you");
    for raw in [&b"plain.txt"[..], "café.txt".as_bytes(), RAW, &b"\xff\xfe"[..]] {
        let o = OsStr::from_bytes(raw);
        let (which, meaning) = match o.to_string_lossy() {
            Cow::Borrowed(_) => ("Borrowed", "already UTF-8; the &str points at the same bytes"),
            Cow::Owned(_) => ("Owned", "a new String was built, and it is NOT this name"),
        };
        println!("   {:<27} {which:<10}   {meaning}", hex(raw));
    }
    println!("   So `matches!(c, Cow::Owned(_))` is 'this name cannot be represented', asked");
    println!("   without a second pass. Calling .to_string() or .into_owned() on the result");
    println!("   throws that answer away — which is why to_string_lossy() is a decision and");
    println!("   not a convenience: the convenient spelling is the one that loses the flag.");
    println!();

    println!("4. Path IS THOSE BYTES WITH PATH METHODS ON THEM");
    let p = Path::new(OsStr::from_bytes(b"/var/log/caf\xe9.txt"));
    println!("   path              {}", hex(p.as_os_str().as_bytes()));
    println!("   .parent()         {:?}", p.parent().map(|x| x.to_string_lossy().into_owned()));
    println!("   .file_name()      {} bytes", p.file_name().map(|x| x.as_bytes().len()).unwrap_or(0));
    println!("   .file_stem()      {}", p.file_stem().map(|x| hex(x.as_bytes())).unwrap_or_default());
    println!("   .extension()      {:?}   <- a &OsStr that happens to be ASCII", p.extension());
    println!("   .is_absolute()    {}", p.is_absolute());
    let mut owned = PathBuf::from("/var/log");
    owned.push(OsStr::from_bytes(b"caf\xe9"));
    owned.set_extension("gz");
    println!("   PathBuf::push + set_extension -> {}", hex(owned.as_os_str().as_bytes()));
    println!("   Every one of those worked on a name no String can hold. Splitting, joining");
    println!("   and opening never look inside a component at all; only DISPLAYING needs");
    println!("   the name to be text, which is why display() is the method with the");
    println!("   disclaimer attached. Comparing is the one with a wrinkle — next section.");
    println!();

    println!("5. AND EQUALITY TIDIES THE SEPARATORS AND NOTHING ELSE");
    println!("   Path::eq compares components(), not raw bytes, so a little SYNTAX is");
    println!("   normalized on the way — and only syntax:");
    for (l, r) in [("a/b", "a//b"), ("a/b", "a/b/"), ("a/b", "a/./b"), ("a/b", "./a/b"), ("a/c", "a/b/../c"), ("a.txt", "A.TXT")] {
        println!("     {:<9} == {:<11} {}", format!("{l:?}"), format!("{r:?}"), Path::new(l) == Path::new(r));
    }
    println!("   Repeated separators, a trailing one and an inner '.' all collapse; a");
    println!("   LEADING './' does not, and neither does '..' — because the thing before it");
    println!("   might be a symlink, so std refuses to guess. Case is untouched too, even");
    println!("   though the volume this ran on may not care.");
    println!();
    println!("   And then each component is compared as BYTES, which is where it bites:");
    let nfc = Path::new("\u{17c}\u{f3}\u{142}w.txt"); // żółw.txt, composed
    let nfd = Path::new("z\u{307}o\u{301}\u{142}w.txt"); // the same word, decomposed
    println!("     composed    {} bytes   {}", nfc.as_os_str().len(), hex(nfc.as_os_str().as_bytes()));
    println!("     decomposed  {} bytes   {}", nfd.as_os_str().len(), hex(nfd.as_os_str().as_bytes()));
    println!("     identical on screen, and nfc == nfd is {}", nfc == nfd);
    println!("   Nothing in std will tell you those are the same word. On macOS APFS they");
    println!("   are the SAME FILE — the filesystem is normalization-insensitive — while on");
    println!("   Linux they are two files. So a program that compares paths itself and a");
    println!("   program that opens them can reach opposite conclusions on one machine.");
    println!("   The rule that survives all of it: a Path comparison answers a question");
    println!("   about NAMES. If you meant to ask about files, ask the OS — canonicalize.");
    println!();

    println!("6. as_encoded_bytes(), AND WHY IT IS NOT CALLED as_bytes()");
    println!("   as_encoded_bytes()  {}", hex(name.as_encoded_bytes()));
    println!("   Portable — it exists on every platform, where as_bytes() is Unix-only. But");
    println!("   read its contract before you use the result for anything: the standard");
    println!("   library calls the encoding 'an unspecified, platform-specific,");
    println!("   self-synchronizing superset of UTF-8', and says any sub-slice that is not");
    println!("   valid UTF-8 should be treated as OPAQUE and 'only comparable within the same");
    println!("   Rust version built for the same target platform'.");
    println!("   So: fine for searching, splitting on ASCII, hashing in memory. Not a value");
    println!("   to write to a file, put in a database or send over a network — and that is");
    println!("   why from_encoded_bytes_unchecked is unsafe, and why the method's name says");
    println!("   'encoded' rather than pretending these are simply the bytes.");
    println!();

    println!("7. WHAT THAT SUPERSET IS, ON THE PLATFORM THIS PROGRAM CANNOT RUN ON");
    println!("   A Windows filename is a sequence of UTF-16 code units, and NTFS does not");
    println!("   check that surrogates are paired — so a name may contain a LONE surrogate,");
    println!("   which no valid UTF-8 can represent. Rust stores those names as WTF-8.");
    println!();
    println!("   WTF-8 is UTF-8's arithmetic with the surrogate ban lifted. Encoding U+D800");
    println!("   through the ordinary three-byte template, by hand:");
    let cp: u32 = 0xD800;
    let wtf8 = [
        0xE0 | (cp >> 12) as u8,
        0x80 | ((cp >> 6) & 0x3F) as u8,
        0x80 | (cp & 0x3F) as u8,
    ];
    println!("     U+{cp:04X}  ->  {}", hex(&wtf8));
    println!("     and UTF-8 refuses those same three bytes: from_utf8 is Ok? {}", std::str::from_utf8(&wtf8).is_ok());
    println!("   That is the whole of it — a real encoding with a real spelling, which every");
    println!("   UTF-8 decoder is required to reject. Python spells the same three bytes");
    println!("   errors='surrogatepass'. Rust never lets them into a String at all, and");
    println!("   keeps them in OsString instead, which is the reason the type exists.");
    println!();
    println!("   The Windows-only API is a different shape for the same reason: there is no");
    println!("   as_bytes()/from_bytes() there, only encode_wide() and from_wide(), which");
    println!("   work in u16 code units — because on that platform the bytes were never the");
    println!("   thing the OS handed you. See the lesson for the facts that cannot be run");
    println!("   on the two machines CI has.");
}
